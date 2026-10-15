"""Registry and runner of the John 2025 replication (plan + declared clarifications IJ-001...).

Everything statistical is the frozen ``g01r`` machinery with the frozen configuration
(``configs/g01r_protocol_v1.toml``): person-grouped 10-fold CV x 50 repetitions, ridge with the
13-value penalty grid chosen by inner 5-fold CV, content offset (here: training mean, one video)
plus ridge output clipped to [0, 1]; person-block Freedman-Lane permutation test on the first 10
paired repetitions with 999 permutations; 90 % nested-CV interval with 200 repetitions; corrected
resampled-t futility bound (z = 3) against 2 delta = 0.10.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, replace
from multiprocessing import get_context

import numpy as np
import pandas as pd

from g01r import inference as inf
from g01r import metrics as met
from g01r import references as refs_mod
from g01r.config import load_config
from g01r.models import ModelSpec
from g01r.pipeline import Pipeline, run_regime_A
from g01r.rng import rng_for
from g01r.splits import split_identity

from .paths import DERIVED, SET_NAME
from .population import analysis_set
from .provider import SYN_BLOCKS, JohnProvider

ITEMS = 13
SETS = {"primary": ("qc_pass", SET_NAME), "eye30": ("qc_eye30", SET_NAME + "_eye30"),
        "eye70": ("qc_eye70", SET_NAME + "_eye70")}

MODELS = {m.name: m for m in [
    ModelSpec("M0", (), "content effect only (training mean)"),
    ModelSpec("M1", ("C",), "+ age, sex, condition"),
    ModelSpec("M1p", ("C", "P"), "+ pretest"),
    ModelSpec("M2_ext", ("C", "Q"), "plan baseline M2-ext"),
    ModelSpec("M2p", ("C", "P", "Q"), "plan pretest-adjusted baseline M2p"),
    ModelSpec("M3p", ("C", "P", "Q", "RF_GAZE"), "+ reference-free gaze only"),
    ModelSpec("M4p", ("C", "P", "Q", "SYN_GAZE"), "+ gaze ISC only"),
    ModelSpec("M5_ext", ("C", "Q", "RF_GAZE", "SYN_GAZE"), "gaze block on M2-ext (secondary contrast)"),
    ModelSpec("M5p", ("C", "P", "Q", "RF_GAZE", "SYN_GAZE"), "gaze block on M2p (primary contrast)"),
    ModelSpec("M5p_pupil", ("C", "P", "Q", "RF_GAZE", "SYN_GAZE", "SYN_PUPIL"), "+ pupil ISC (secondary block)"),
    ModelSpec("M2p_QD", ("C", "P", "QD"), "A2: M2p with decomposed quality"),
    ModelSpec("M5p_QD", ("C", "P", "QD", "RF_GAZE", "SYN_GAZE"), "A2: M5p with decomposed quality"),
]}


@dataclass(frozen=True)
class Comparison:
    id: str
    base: str
    full: str
    role: str
    set: str = "primary"
    test: tuple | None = None          # (tested blocks, nuisance blocks)
    interval: bool = False
    futility: bool = False


COMPARISONS = [
    Comparison("PRIMARY_M5p_vs_M2p", "M2p", "M5p", "PRIMARY (plan): gaze block beyond the pretest-adjusted baseline; "
               "one-sided alpha 0.05", test=(("RF_GAZE", "SYN_GAZE"), ("C", "P", "Q")), interval=True, futility=True),
    Comparison("SECONDARY_M5_vs_M2ext", "M2_ext", "M5_ext", "SECONDARY (plan): gaze block beyond M2-ext (no pretest)",
               test=(("RF_GAZE", "SYN_GAZE"), ("C", "Q")), interval=True),
    Comparison("PUPIL_M5p_pupil_vs_M2p", "M2p", "M5p_pupil", "secondary block (plan): + pupil ISC; estimate only"),
    Comparison("PUPIL_M5p_pupil_vs_M5p", "M5p", "M5p_pupil", "secondary block (plan): pupil ISC increment; estimate only"),
    Comparison("LADDER_M1_vs_M0", "M0", "M1", "ladder: covariates; estimate only"),
    Comparison("LADDER_M1p_vs_M1", "M1", "M1p", "ladder: pretest beyond covariates; estimate only"),
    Comparison("LADDER_M2p_vs_M1p", "M1p", "M2p", "ladder: quality beyond covariates + pretest; estimate only"),
    Comparison("LADDER_M2p_vs_M2ext", "M2_ext", "M2p", "ladder: pretest beyond M2-ext; estimate only"),
    Comparison("LADDER_M3p_vs_M2p", "M2p", "M3p", "ladder: reference-free gaze only; estimate only"),
    Comparison("LADDER_M4p_vs_M2p", "M2p", "M4p", "ladder: gaze ISC only; estimate only"),
    Comparison("LADDER_M5p_vs_M3p", "M3p", "M5p", "ladder: ISC beyond reference-free gaze (H2a analogue); estimate only"),
    Comparison("A1_eye30_M5p_vs_M2p", "M2p", "M5p", "A1 (results-informed): primary contrast at QC <= 0.30; estimate only",
               set="eye30"),
    Comparison("A1_eye70_M5p_vs_M2p", "M2p", "M5p", "A1 (results-informed): primary contrast at QC <= 0.70; estimate only",
               set="eye70"),
    Comparison("A2_M5p_QD_vs_M2p_QD", "M2p_QD", "M5p_QD", "A2 (results-informed): gaze block beyond decomposed "
               "quality (short blinks, long loss, off-display); estimate only"),
    Comparison("A2_M2p_QD_vs_M2p", "M2p", "M2p_QD", "A2 (results-informed): decomposed vs single quality; estimate only"),
]


# ============================================================================ worker context
_CTX: dict = {}


def syn_blocks_for(model_names) -> tuple:
    return tuple(b for b in SYN_BLOCKS if any(b in MODELS[m].blocks for m in model_names))


def _context(set_key: str, syn_blocks: tuple):
    key = (set_key, syn_blocks)
    if key not in _CTX:
        cfg = load_config()
        people = pd.read_parquet(DERIVED / "people.parquet")
        flag, name = SETS[set_key]
        aset = analysis_set(people, flag, name)
        _CTX[key] = (cfg, aset, JohnProvider(aset, people, syn_blocks))
    return _CTX[key]


def set_participants(set_key: str) -> list:
    people = pd.read_parquet(DERIVED / "people.parquet")
    flag, name = SETS[set_key]
    return analysis_set(people, flag, name).cells.participant_id.tolist()


def _task_A(args):
    set_key, model_names, y, rep, keep_reps, keep_models = args
    cfg, aset, prov = _context(set_key, syn_blocks_for(model_names))
    pipe = Pipeline(cfg, aset, prov, [MODELS[m] for m in model_names])
    cv = run_regime_A(pipe, y, keep_design_reps=keep_reps, reps=[rep])
    for res in cv.designs:
        res.designs = {m: v for m, v in res.designs.items() if m in keep_models}
    lam = {m: v for m, v in cv.lambdas.items()}
    return rep, {m: cv.preds[m][rep] for m in model_names}, lam, cv.designs, cv.folds


def _task_perm(args):
    set_key, splits, full, y, lb, perms, tested_cols, nuisance_cols = args
    cfg, aset, _ = _context(set_key, ())
    prepared = inf.prepare_permutation(aset, inf.PermutationSetup(splits, full, tested_cols, nuisance_cols))
    return inf.permutation_null(aset, prepared, y, lb, perms, cfg.lambda_grid_rel, cfg.raw["model"]["standardize_min_sd"])


def _task_ncv(args):
    set_key, base, full, y, rep = args
    cfg, aset, prov = _context(set_key, syn_blocks_for([base, full]))
    pipe = Pipeline(cfg, aset, prov, [MODELS[base], MODELS[full]])

    def fit_pair(train, test, labels):
        plan = refs_mod.regime_A(aset, train, train | test) if pipe.needs_syn else None
        res = pipe.fit_split(y[train], train, test, plan, "A", labels=labels)
        return res.preds[base], res.preds[full]

    return inf.nested_cv_pieces(aset, fit_pair, {"person": inf.person_loss_diff(y, aset)},
                                cfg.resampling["outer_folds_A"], cfg.resampling["base_seed"], (aset.name, base, full), rep)


class Executor:
    def __init__(self, workers: int):
        self.pool = get_context("spawn").Pool(workers) if workers > 1 else None
        self.workers = workers

    def map(self, fn, items):
        return self.pool.map(fn, items, chunksize=1) if self.pool else [fn(x) for x in items]

    def close(self):
        if self.pool:
            self.pool.close()
            self.pool.join()


# ============================================================================ regime A on one set
@dataclass
class SetFit:
    set_key: str
    preds: dict
    folds: np.ndarray
    lambdas: dict
    designs: list = field(default_factory=list)


def fit_set(ex: Executor, set_key: str, model_names: list, y: np.ndarray, R: int, keep_reps: int = 0,
            keep_models=()) -> SetFit:
    parts = ex.map(_task_A, [(set_key, model_names, y, r, keep_reps, tuple(keep_models)) for r in range(R)])
    n = len(y)
    preds = {m: np.full((R, n), np.nan) for m in model_names}
    lambdas = {m: [] for m in model_names}
    designs, folds = [], None
    for rep, p, lam, des, f in sorted(parts, key=lambda q: q[0]):
        for m in model_names:
            preds[m][rep] = p[m]
            lambdas[m].extend(lam[m])
        designs.extend(des)
        folds = f
    designs.sort(key=lambda d: (d.rep, d.fold))
    return SetFit(set_key, preds, folds, lambdas, designs)


def comparison_report(pb: np.ndarray, pf: np.ndarray, y: np.ndarray, person: np.ndarray) -> dict:
    lb, lf = met.cell_losses(pb, y), met.cell_losses(pf, y)
    ab, af = met.cell_losses(pb, y, "ae"), met.cell_losses(pf, y, "ae")
    Lb, Lf = met.person_means(lb, person), met.person_means(lf, person)
    per_rep = [1 - np.mean((pf[r] - y) ** 2) / np.mean((pb[r] - y) ** 2) for r in range(pb.shape[0])]
    return dict(skill=float(1 - Lf.mean() / Lb.mean()), base_mse=float(Lb.mean()), full_mse=float(Lf.mean()),
                delta_rmse_items=float((np.sqrt(Lb.mean()) - np.sqrt(Lf.mean())) * ITEMS),
                delta_mae_items=float((ab.mean() - af.mean()) * ITEMS),
                calibration_base=met.calibration(np.nanmean(pb, 0), y), calibration_full=met.calibration(np.nanmean(pf, 0), y),
                skill_per_repetition=dict(min=float(np.min(per_rep)), median=float(np.median(per_rep)), max=float(np.max(per_rep))),
                n_people=int(len(Lb)))


def permutation_test(ex, fit: SetFit, comp: Comparison, y, aset, prov, cfg, B: int, R_perm: int) -> dict:
    lb = met.cell_losses(fit.preds[comp.base][:R_perm], y)
    lf = met.cell_losses(fit.preds[comp.full][:R_perm], y)
    obs = inf.permutation_statistic(lb, lf, aset.person)
    tested_cols = [c for b in comp.test[0] for c in prov.block_columns(b)]
    nuisance_cols = [c for b in comp.test[1] for c in prov.block_columns(b)]
    perms = inf.draw_permutations(aset, B, cfg.resampling["base_seed"], aset.name)
    light = [replace(d, designs={comp.full: d.designs[comp.full]}) for d in fit.designs if d.rep < R_perm]
    chunks = [c for c in np.array_split(np.arange(B), max(1, ex.workers * 2)) if len(c)]
    null = np.concatenate(ex.map(_task_perm, [(fit.set_key, light, comp.full, y, lb, perms[c], tested_cols, nuisance_cols)
                                               for c in chunks]))
    return dict(observed_loss_difference=float(obs), observed_skill_R10=float(obs / met.person_means(lb, aset.person).mean()),
                p=inf.permutation_p(obs, null), B=int(B), reps=int(R_perm), null_mean=float(null.mean()),
                null_q95=float(np.quantile(null, 0.95)), tested_blocks=list(comp.test[0]), nuisance_blocks=list(comp.test[1]))


def nested_interval(ex, comp: Comparison, fit: SetFit, y, aset, cfg, reps: int) -> dict:
    K = cfg.resampling["outer_folds_A"]
    pieces = ex.map(_task_ncv, [(comp.set, comp.base, comp.full, y, r) for r in range(reps)])
    Lb = met.person_means(met.cell_losses(fit.preds[comp.base], y), aset.person)
    Lf = met.person_means(met.cell_losses(fit.preds[comp.full], y), aset.person)
    diffs = Lb - Lf
    out = inf.nested_cv_interval([p["person"] for p in pieces if p["person"]["a"]], float(diffs.mean()), diffs,
                                 float(Lb.mean()), K, cfg.inference["ncv_level"])
    out["point_skill"] = float(diffs.mean() / Lb.mean())
    return out


# ============================================================================ full replication run
def run(y_by_set: dict, workers: int = 5, ncv_reps: int | None = None, n_perm: int | None = None, log=print) -> dict:
    """``y_by_set`` maps set key -> outcome array aligned with that set's analysis cells."""
    cfg = load_config()
    R, K = cfg.resampling["reps_A"], cfg.resampling["outer_folds_A"]
    R_perm = cfg.inference["reps_permutation"]
    B = cfg.inference["n_permutations"] if n_perm is None else n_perm
    ncv = cfg.inference["ncv_reps"] if ncv_reps is None else ncv_reps
    ex = Executor(workers)
    out = dict(config_sha256=cfg.sha256, R=R, K=K, comparisons={}, sets={})
    t0 = time.time()
    try:
        for set_key in SETS:
            comps = [c for c in COMPARISONS if c.set == set_key]
            models = sorted({m for c in comps for m in (c.base, c.full)})
            keep = sorted({c.full for c in comps if c.test})
            y = y_by_set[set_key]
            fit = fit_set(ex, set_key, models, y, R, keep_reps=R_perm if keep else 0, keep_models=keep)
            cfg_w, aset, prov = _context(set_key, ())
            out["sets"][set_key] = dict(name=aset.name, n_people=aset.n_person, split_identity=split_identity(fit.folds, aset.person),
                                        set_identity=aset.identity(), outcome_mean=float(y.mean()), outcome_sd=float(y.std(ddof=1)),
                                        log10_lambda_median={m: float(np.median(np.log10(np.maximum(v, 1e-300))))
                                                             for m, v in fit.lambdas.items()},
                                        # penalty = grid value x n_train; the lowest value is 1e-3 n_train < 10^-2.75 n,
                                        # the next is 10^-2.5 n_train > 10^-2.75 n for n_train >= 0.57 n
                                        lambda_at_grid_min_share={m: float(np.mean((np.array(v) > 0) & (np.array(v) < 10 ** -2.75 * aset.n)))
                                                                  for m, v in fit.lambdas.items()})
            log(f"[{time.time() - t0:7.0f}s] {set_key}: {len(models)} models x {R} repetitions fitted")
            for comp in comps:
                res = dict(role=comp.role, base=comp.base, full=comp.full, set=set_key,
                           report=comparison_report(fit.preds[comp.base], fit.preds[comp.full], y, aset.person))
                if comp.futility:
                    fd = inf.fold_differences(fit.preds[comp.base], fit.preds[comp.full], y, fit.folds, aset)
                    fut = inf.corrected_t_upper(fd, K, cfg.inference["futility_z"], res["report"]["base_mse"])
                    fut["threshold"] = cfg.inference["futility_threshold"]
                    fut["rules_out_threshold"] = bool(fut["upper_skill"] < cfg.inference["futility_threshold"])
                    res["futility"] = fut
                if comp.test:
                    res["test"] = permutation_test(ex, fit, comp, y, aset, prov, cfg, B, R_perm)
                    log(f"[{time.time() - t0:7.0f}s] {comp.id}: permutation p = {res['test']['p']:.4f}")
                if comp.interval and ncv > 0:
                    res["interval"] = nested_interval(ex, comp, fit, y, aset, cfg, ncv)
                    log(f"[{time.time() - t0:7.0f}s] {comp.id}: nested-CV interval done")
                if comp.id.startswith("PRIMARY"):
                    res["decision"] = inf.h1_decision(res["test"]["p"], res["report"]["skill"], res["futility"]["upper_skill"],
                                                      cfg.inference["delta"], cfg.inference["futility_threshold"],
                                                      cfg.inference["alpha"])
                out["comparisons"][comp.id] = res
            if set_key == "primary":
                out["predictions"] = {m: np.nanmean(v, 0).tolist() for m, v in fit.preds.items()}
                out["outer_folds"] = fit.folds.tolist()
    finally:
        ex.close()
    out["elapsed_s"] = time.time() - t0
    return out


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=float) + "\n")
