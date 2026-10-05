"""Execution of registry analyses (protocol §11-§15) with parallel workers and run tracking.

Outcomes enter only through an :class:`OutcomeSource`: either synthetic (validation and dry
runs) or real, which requires a verified analysis-freeze authorization (:mod:`g01r.outcomes`).
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, replace
from multiprocessing import get_context

import numpy as np
import pandas as pd

from . import inference as inf
from . import metrics as met
from . import references as refs_mod
from .config import ProtocolConfig, load_config
from .design import FeatureProvider
from .models import FAMILY
from .outcomes import load_real_outcomes, synthetic_outcomes
from .pipeline import Pipeline, run_cas_policy, run_regime_A, run_regimes_BC, run_transport
from .population import Population
from .registry import AnalysisSpec, PermTest
from .rng import rng_for
from .splits import outer_folds, split_identity

# ============================================================================ outcome sources
@dataclass
class OutcomeSource:
    """``kind='synthetic'`` draws from the psychometric generator with ``scenario`` options;
    ``kind='real'`` needs a verified :class:`g01r.freeze.Authorization`."""

    kind: str
    scenario: dict | None = None
    authorization: object = None
    seed_label: str = "synthetic"

    def describe(self) -> str:
        if self.kind == "real":
            return f"real:authorized:{getattr(self.authorization, 'record_sha256', '?')}"
        return f"synthetic:{self.seed_label}:{self.scenario}"

    def outcomes(self, cfg: ProtocolConfig, aset, outcome: str, provider=None) -> np.ndarray:
        if self.kind == "real":
            return load_real_outcomes(aset, outcome, self.authorization)
        sc = dict(self.scenario or {})
        rng = rng_for(cfg.resampling["base_seed"], "synthetic_outcome", self.seed_label, aset.name, outcome)
        nuisance = None
        if sc.get("nuisance_share", 0) > 0 and provider is not None:
            cols = provider.block_columns("C") + provider.block_columns("Q")
            Xn, _ = provider.design(("C", "Q"), None)
            Xn = np.where(np.isfinite(Xn), Xn, np.nanmean(Xn, axis=0))
            nuisance = Xn[:, np.nanstd(Xn, axis=0) > 0]
        signal = None
        if sc.get("signal_amp") and provider is not None:
            # Planted information in named real features (validation only): mean of their z-scores.
            Xs = provider.static[list(sc["signal_features"])].to_numpy(float)
            Xs = (Xs - np.nanmean(Xs, 0)) / np.nanstd(Xs, 0)
            signal = np.nanmean(Xs, axis=1)
        return synthetic_outcomes(aset, rng, nuisance=nuisance, nuisance_share=sc.get("nuisance_share", 0.0),
                                  signal=signal, signal_amp=sc.get("signal_amp", 0.0))


# ============================================================================ worker context
_CTX: dict = {}
_POP: dict = {}


def _context(cfg_path: str, overrides: tuple, set_name: str, route: str, include_gpa: bool):
    key = (cfg_path, overrides, set_name, route, include_gpa)
    if key not in _CTX:
        cfg = load_config(cfg_path)
        if overrides:
            cfg = cfg.with_overrides(**dict(overrides))
        if cfg_path not in _POP:
            _POP[cfg_path] = Population(cfg)
        aset = _POP[cfg_path].analysis_set(set_name)
        _CTX[key] = (cfg, aset, FeatureProvider(cfg, aset, route, include_gpa))
    return _CTX[key]


def _ctx_key(cfg: ProtocolConfig, spec: AnalysisSpec, set_name: str | None = None, route: str | None = None):
    return (str(cfg.path), tuple(sorted(cfg.overrides.items())), set_name or spec.set_name, route or spec.route,
            spec.include_gpa)


def _task_A(args):
    key, model_names, y, reps, keep_reps, keep_models = args
    cfg, aset, prov = _context(*key)
    pipe = Pipeline(cfg, aset, prov, [FAMILY[m] for m in model_names])
    cv = run_regime_A(pipe, y, keep_design_reps=keep_reps, reps=reps)
    for res in cv.designs:
        res.designs = {m: v for m, v in res.designs.items() if m in keep_models}
    return list(reps), {m: cv.preds[m][list(reps)] for m in model_names}, cv.lambdas, cv.designs, cv.folds


def _task_perm(args):
    key, splits, test, y, lb, perms, tested_cols, nuisance_cols = args
    cfg, aset, _ = _context(*key)
    prepared = inf.prepare_permutation(aset, inf.PermutationSetup(splits, test.full, tested_cols, nuisance_cols))
    return inf.permutation_null(aset, prepared, y, lb, perms, cfg.lambda_grid_rel, cfg.raw["model"]["standardize_min_sd"])


def _cell_loss_diff(y, aset):
    c = aset.n_person / aset.n

    def fn(cells, pb, pf):
        d = (pb - y[cells]) ** 2 - (pf - y[cells]) ** 2
        p = aset.person[cells]
        s = np.bincount(p, d, minlength=aset.n_person)
        return c * s[np.bincount(p, minlength=aset.n_person) > 0]
    return fn


def _state_cell_loss_diff(y, aset):
    keep_all = np.bincount(aset.person)[aset.person] >= 2
    c = len(np.unique(aset.person[keep_all])) / keep_all.sum()

    def fn(cells, pb, pf):
        lb, keep = met.state_losses(y[cells], pb, aset.person[cells], aset.ev[cells])
        lf, _ = met.state_losses(y[cells], pf, aset.person[cells], aset.ev[cells])
        if keep.sum() == 0:
            return np.array([])
        p = aset.person[cells][keep]
        s = np.bincount(p, (lb - lf)[keep], minlength=aset.n_person)
        return c * s[np.bincount(p, minlength=aset.n_person) > 0]
    return fn


def _task_ncv(args):
    key, base, full, y, rep, loss_names = args
    cfg, aset, prov = _context(*key)
    pipe = Pipeline(cfg, aset, prov, [FAMILY[base], FAMILY[full]])

    def fit_pair(train, test, labels):
        plan = refs_mod.regime_A(aset, train, train | test) if pipe.needs_syn else None
        res = pipe.fit_split(y[train], train, test, plan, "A", labels=labels)
        return res.preds[base], res.preds[full]

    if pipe.needs_syn:
        # Prefetch every plan of this nested repetition (same fold draw as nested_cv_pieces).
        from .splits import person_folds
        K = cfg.resampling["outer_folds_A"]
        folds = person_folds(aset.exp_of_person, K, rng_for(cfg.resampling["base_seed"], aset.name, base, full, "ncv", rep))[aset.person]
        plans = []
        for k in range(K):
            trn = folds != k
            for j in range(K):
                if j != k:
                    te = folds == j
                    plans.append(refs_mod.regime_A(aset, trn & ~te, trn))
            plans.append(refs_mod.regime_A(aset, trn, np.ones(aset.n, bool)))
        prov.syn_many(plans)
    fns = {"person": inf.person_loss_diff(y, aset), "state": _state_cell_loss_diff(y, aset), "cell": _cell_loss_diff(y, aset)}
    return inf.nested_cv_pieces(aset, fit_pair, {k: fns[k] for k in loss_names}, cfg.resampling["outer_folds_A"],
                                cfg.resampling["base_seed"], (aset.name, base, full), rep)


def _task_BC(args):
    key, y, r = args
    cfg, aset, prov = _context(*key)
    pB = Pipeline(cfg, aset, prov, [FAMILY["M2"], FAMILY["M5_B"]])
    pC = Pipeline(cfg, aset, prov, [FAMILY["M2"], FAMILY["M5"]])
    res = run_regimes_BC(pB, pC, y, reps=[r])
    return r, {m: v[r] for m, v in res.preds_B.items()}, {m: v[r] for m, v in res.preds_C.items()}, res.split_id


def _task_CAS(args):
    key, core_mask, y, r = args
    cfg, aset, prov = _context(*key)
    p2 = Pipeline(cfg, aset, prov, [FAMILY["M2"]])
    p5 = Pipeline(cfg, aset, prov, [FAMILY["M5"]])
    preds, folds = run_cas_policy(p2, p5, y, core_mask, reps=[r])
    return r, {m: v[r] for m, v in preds.items()}, folds


class Executor:
    def __init__(self, workers: int):
        self.workers = workers
        self.pool = get_context("spawn").Pool(workers) if workers > 1 else None

    def map(self, fn, items):
        if self.pool is None:
            return [fn(x) for x in items]
        return self.pool.map(fn, items, chunksize=1)

    def close(self):
        if self.pool is not None:
            self.pool.close()
            self.pool.join()


# ============================================================================ regime A
def detection_procedure(cfg: ProtocolConfig) -> str:
    """Detection procedure fixed by the production validation verdict (IS-027); permutation if absent."""
    from .config import IMPL_EVIDENCE

    path = IMPL_EVIDENCE / "validation" / "validation_verdict.json"
    if path.exists():
        return json.loads(path.read_text()).get("detection_procedure", "permutation")
    return "permutation"


def run_A(spec: AnalysisSpec, cfg: ProtocolConfig, source: OutcomeSource, tracker, ex: Executor,
          ncv_reps: int | None = None, n_perm: int | None = None) -> dict:
    t0 = time.time()
    key = _ctx_key(cfg, spec)
    cfg_w, aset, prov = _context(*key)
    y = source.outcomes(cfg, aset, spec.outcome, prov)
    R, K = cfg.resampling["reps_A"], cfg.resampling["outer_folds_A"]
    R_perm = min(cfg.inference["reps_permutation"], R) if spec.tests else 0
    keep_models = sorted({t.full for t in spec.tests})
    parts = ex.map(_task_A, [(key, spec.models, y, [r], R_perm, keep_models) for r in range(R)])
    preds = {m: np.full((R, aset.n), np.nan) for m in spec.models}
    designs, lambdas, folds = [], {m: [] for m in spec.models}, None
    for reps, p, lam, des, f in parts:
        for m in spec.models:
            preds[m][reps] = p[m]
            lambdas[m].extend(lam[m])
        designs.extend(des)
        folds = f
    designs.sort(key=lambda d: (d.rep, d.fold))
    out = dict(analysis=spec.id, set=spec.set_name, outcome=spec.outcome, route=spec.route, n_people=aset.n_person,
               n_cells=aset.n, n_videos=aset.n_video, split_identity=split_identity(folds, aset.person),
               set_identity=aset.identity(), comparisons={}, tests={})
    tracker.set_identity(set=spec.set_name, set_identity=aset.identity(), split_identity=out["split_identity"],
                         outcome_source=source.describe())
    # Point estimates and companions for every prespecified comparison (identical cells and folds).
    for comp in spec.comparisons:
        rep = met.regime_A_report(preds[comp.base], preds[comp.full], y, aset, cfg.data["items_per_quiz"])
        res = dict(report=rep)
        lb = met.cell_losses(preds[comp.base], y)
        lf = met.cell_losses(preds[comp.full], y)
        Lb, Lf = met.person_means(lb, aset.person), met.person_means(lf, aset.person)
        if comp.futility:
            fd = inf.fold_differences(preds[comp.base], preds[comp.full], y, folds, aset)
            res["futility"] = inf.corrected_t_upper(fd, K, cfg.inference["futility_z"], Lb.mean())
            res["futility"]["threshold"] = cfg.inference["futility_threshold"]
            res["futility"]["rules_out_threshold"] = bool(res["futility"]["upper_skill"] < cfg.inference["futility_threshold"])
        nrep = ncv_reps if ncv_reps is not None else cfg.inference["ncv_reps"]
        if comp.interval and nrep == 0:
            res["intervals"] = "not computed (smoke-test override ncv_reps=0)"
        elif comp.interval:
            losses = ("person",) + tuple(comp.extra_losses)
            pieces = ex.map(_task_ncv, [(key, comp.base, comp.full, y, r, losses) for r in range(nrep)])
            res["intervals"] = {}
            pb_mean, pf_mean = np.nanmean(preds[comp.base], 0), np.nanmean(preds[comp.full], 0)
            for loss in losses:
                pcs = [p[loss] for p in pieces if p[loss]["a"]]
                if loss == "person":
                    diffs, base = Lb - Lf, Lb.mean()
                elif loss == "cell":
                    c = aset.n_person / aset.n
                    diffs = c * np.bincount(aset.person, lb - lf)
                    base = lb.mean()
                else:
                    sb, keep = met.state_losses(y, pb_mean, aset.person, aset.ev)
                    sf, _ = met.state_losses(y, pf_mean, aset.person, aset.ev)
                    c = len(np.unique(aset.person[keep])) / keep.sum()
                    s = np.bincount(aset.person[keep], (sb - sf)[keep], minlength=aset.n_person)
                    diffs = c * s[np.bincount(aset.person[keep], minlength=aset.n_person) > 0]
                    base = np.nanmean(sb[keep])
                res["intervals"][loss] = inf.nested_cv_interval(pcs, float(diffs.mean()), diffs, float(base), K,
                                                                cfg.inference["ncv_level"])
                res["intervals"][loss]["point_skill"] = float(diffs.mean() / base)
        out["comparisons"][comp.id] = res
    # Detection tests (person-block Freedman-Lane, paired first R_perm repetitions).
    if spec.tests:
        B = n_perm if n_perm is not None else cfg.inference["n_permutations"]
        perms = inf.draw_permutations(aset, B, cfg.resampling["base_seed"], aset.name)
        chunks = np.array_split(np.arange(B), max(1, ex.workers * 2))
        for test in spec.tests:
            lb10 = met.cell_losses(preds[test.base][:R_perm], y)
            lf10 = met.cell_losses(preds[test.full][:R_perm], y)
            obs = inf.permutation_statistic(lb10, lf10, aset.person)
            tested_cols = [c for b in test.tested_blocks for c in prov.block_columns(b)]
            nuisance_cols = [c for b in test.nuisance_blocks for c in prov.block_columns(b)]
            light = [replace(d, designs={test.full: d.designs[test.full]}) for d in designs]
            nulls = ex.map(_task_perm, [(key, light, test, y, lb10, perms[ch], tested_cols, nuisance_cols)
                                        for ch in chunks if len(ch)])
            null = np.concatenate(nulls)
            p = inf.permutation_p(obs, null)
            out["tests"][test.id] = dict(observed_loss_difference=obs, observed_skill_R10=obs / met.person_means(lb10, aset.person).mean(),
                                         p=p, B=int(B), reps=int(R_perm), null_mean=float(null.mean()),
                                         null_q95=float(np.quantile(null, 0.95)), tested_blocks=list(test.tested_blocks),
                                         nuisance_blocks=list(test.nuisance_blocks), base=test.base, full=test.full)
            tracker.log_array(f"permutation_null_{test.id}.npy", null)
        h2 = {t: out["tests"][t]["p"] for t in cfg.inference["holm_family"] if t in out["tests"]}
        if h2:
            adj = inf.holm(h2)
            for t, a in adj.items():
                out["tests"][t]["p_holm"] = a
                out["tests"][t]["reject_holm"] = bool(a <= cfg.inference["alpha"])
        if "H1" in out["tests"] and "M5_vs_M2" in out["comparisons"]:
            c = out["comparisons"]["M5_vs_M2"]
            Lb, Lf = met.person_means(met.cell_losses(preds["M2"], y), aset.person), met.person_means(met.cell_losses(preds["M5"], y), aset.person)
            boot = inf.person_bootstrap_detection(Lb - Lf, aset.exp_of_person,
                                                  rng_for(cfg.resampling["base_seed"], aset.name, "fallback_boot"),
                                                  cfg.inference["bootstrap_B"])
            procedure = detection_procedure(cfg)
            if procedure == "permutation":
                p_decision = out["tests"]["H1"]["p"]
            else:   # declared fallback (EDD-009, IS-027): decide by the bootstrap lower bound
                p_decision = 0.0 if boot["detect"] else 1.0
            out["detection_procedure"] = procedure
            out["h1_decision"] = inf.h1_decision(p_decision, c["report"]["skill_person_balanced"],
                                                 c["futility"]["upper_skill"], cfg.inference["delta"],
                                                 cfg.inference["futility_threshold"], cfg.inference["alpha"])
            out["person_bootstrap_detection" + ("" if procedure != "permutation" else "_NON_DECISIONAL")] = boot
    # Artifacts for later tables and figures.
    rows = []
    for m in spec.models:
        for r in range(R):
            rows.append(pd.DataFrame(dict(model=m, rep=r, cell=np.arange(aset.n), pred=preds[m][r])))
    tracker.log_frame("predictions.parquet", pd.concat(rows, ignore_index=True))
    tracker.log_frame("cells.parquet", aset.cells.drop(columns=[], errors="ignore"))
    tracker.log_array("outer_folds.npy", folds)
    tracker.log_json("log10_lambda_absolute.json", {m: np.log10(np.maximum(np.array(v, float), 1e-300)).tolist()
                                                    for m, v in lambdas.items()})
    out["elapsed_s"] = time.time() - t0
    return out


# ============================================================================ regimes B and C
def run_BC(spec, cfg, source, tracker, ex):
    key = _ctx_key(cfg, spec)
    _, aset, prov = _context(*key)
    y = source.outcomes(cfg, aset, spec.outcome, prov)
    R = cfg.resampling["reps_BC"]
    parts = ex.map(_task_BC, [(key, y, r) for r in range(R)])
    pB = {m: np.stack([p[1][m] for p in sorted(parts, key=lambda q: q[0])]) for m in ("M2", "M5_B")}
    pC = {m: np.stack([p[2][m] for p in sorted(parts, key=lambda q: q[0])]) for m in ("M2", "M5")}
    out = dict(analysis=spec.id, n_people=aset.n_person, n_cells=aset.n, n_videos=aset.n_video, regimes={})
    rng = rng_for(cfg.resampling["base_seed"], aset.name, "BC_bootstrap")
    per_video = {}
    for regime, preds, full in (("B", pB, "M5_B"), ("C", pC, "M5")):
        mb, mf = np.nanmean(preds["M2"], 0), np.nanmean(preds[full], 0)
        lb, lf = met.within_content_losses(y, mb, aset.ev), met.within_content_losses(y, mf, aset.ev)
        res = dict(within_content_skill=met.skill_person_balanced(lb, lf, aset.person),
                   absolute_skill=met.skill_person_balanced((mb - y) ** 2, (mf - y) ** 2, aset.person),
                   interval=inf.two_way_bootstrap(lb, lf, aset, rng, cfg.inference["bootstrap_B"], cfg.inference["bc_interval_level"]),
                   per_video={})
        for v in range(aset.n_video):
            m = aset.video == v
            vid = aset.cells.canonical_video_id[m].iloc[0]
            res["per_video"][vid] = dict(skill=met.skill_cell_weighted(lb[m], lf[m]), cells=int(m.sum()))
            per_video.setdefault(vid, {})[regime] = res["per_video"][vid]["skill"]
        out["regimes"][regime] = res
    out["B_minus_C_per_video"] = {v: d["B"] - d["C"] for v, d in per_video.items()}
    out["label"] = "DESCRIPTIVE; conditional on the 8 sampled videos; no p-values"
    tracker.log_frame("predictions_B.parquet", pd.DataFrame({m: np.nanmean(v, 0) for m, v in pB.items()}))
    tracker.log_frame("predictions_C.parquet", pd.DataFrame({m: np.nanmean(v, 0) for m, v in pC.items()}))
    return out


# ============================================================================ CAS policy
def run_CAS(spec, cfg, source, tracker, ex):
    key = _ctx_key(cfg, spec)
    _, aset, prov = _context(*key)
    pop = _POP[str(cfg.path)]
    core_keys = set(map(tuple, pop.analysis_set(spec.options["core_set"]).cells[["experiment", "participant_id", "local_stimulus_id"]].to_numpy().tolist()))
    in_core = np.array([tuple(r) in core_keys for r in aset.cells[["experiment", "participant_id", "local_stimulus_id"]].to_numpy().tolist()])
    y = source.outcomes(cfg, aset, spec.outcome, prov)
    R = cfg.resampling["reps_A"]
    parts = ex.map(_task_CAS, [(key, in_core, y, r) for r in range(R)])
    preds = {m: np.stack([p[1][m] for p in sorted(parts, key=lambda q: q[0])]) for m in ("M2", "POLICY")}
    lb, lf = met.cell_losses(preds["M2"], y), met.cell_losses(preds["POLICY"], y)
    out = dict(analysis=spec.id, n_people=aset.n_person, n_cells=aset.n, n_core_cells=int(in_core.sum()),
               policy_vs_M2_skill_all_cells=met.skill_person_balanced(lb, lf, aset.person),
               policy_vs_M2_cell_weighted=met.skill_cell_weighted(lb, lf),
               skill_on_core_cells=met.skill_cell_weighted(lb[in_core], lf[in_core]),
               skill_on_noncore_cells=met.skill_cell_weighted(lb[~in_core], lf[~in_core]) if (~in_core).any() else None,
               label="DESCRIPTIVE coverage-policy risk; selection report in analysis_population.md")
    return out


# ============================================================================ transport
def run_transport_analysis(spec, cfg, source, tracker, ex):
    src_name, tgt_name = spec.options["pair"]
    pop_cfg = load_config(cfg.path)
    pop = _POP.setdefault(str(cfg.path), Population(pop_cfg))
    union = pop.cells[pop.cells[src_name] | pop.cells[tgt_name]]
    from .population import AnalysisSet
    cols = ["experiment", "participant_id", "qualified_participant_id", "session", "local_stimulus_id",
            "canonical_video_id", "condition", "exposure_number"]
    aset = AnalysisSet(f"{src_name}+{tgt_name}", union[cols].reset_index(drop=True))
    prov = FeatureProvider(cfg, aset, spec.route, spec.include_gpa)
    in_src = union[src_name].to_numpy()
    y = np.empty(aset.n)
    for name, mask in ((src_name, in_src), (tgt_name, ~in_src)):
        sub = pop.analysis_set(name)
        ys = source.outcomes(cfg, sub, spec.outcome, None)
        k = dict(zip(map(tuple, sub.cells[["experiment", "participant_id", "local_stimulus_id"]].to_numpy().tolist()), ys))
        y[mask] = [k[tuple(r)] for r in aset.cells.loc[mask, ["experiment", "participant_id", "local_stimulus_id"]].to_numpy().tolist()]
    out = dict(analysis=spec.id, directions={})
    for direction, source_mask in ((f"{src_name}->{tgt_name}", in_src), (f"{tgt_name}->{src_name}", ~in_src)):
        pipe = Pipeline(cfg, aset, prov, [FAMILY["M2"], FAMILY["M5"]], seed_label=aset.name + direction)
        target = ~source_mask
        preds, res = run_transport(pipe, y[source_mask], source_mask, target, y_target_for_recalibration=y)
        te = np.flatnonzero(target)
        d = {}
        for variant, pr in preds.items():
            lb, lf = (pr["M2"] - y[te]) ** 2, (pr["M5"] - y[te]) ** 2
            boot = inf.person_bootstrap_detection(
                met.person_means(lb, aset.person[te]) - met.person_means(lf, aset.person[te]),
                aset.exp_of_person[np.unique(aset.person[te])], rng_for(cfg.resampling["base_seed"], direction, variant),
                cfg.inference["bootstrap_B"])
            d[variant] = dict(skill=met.skill_person_balanced(lb, lf, aset.person[te]),
                              loss_difference_interval_conditional_on_fitted_source_model=boot)
        out["directions"][direction] = d
    out["label"] = "DESCRIPTIVE transport on 3 shared videos; within-protocol regime A estimates are in H1_H2 (E4) and D_E5"
    return out


# ============================================================================ explanatory and diagnostics
def run_explanatory(spec, cfg, source, tracker, ex):
    from .diagnostics import crossed_reml

    key = _ctx_key(cfg, spec)
    _, aset, prov = _context(*key)
    y = source.outcomes(cfg, aset, spec.outcome, prov)
    plan = refs_mod.full_leave_self_out(aset)
    syn = prov.syn(plan)
    X, cols = prov.design(FAMILY["M5"].blocks, syn)
    X = np.where(np.isfinite(X), X, np.nanmean(X, axis=0))
    keep = X.std(axis=0) > 1e-12
    X, cols = X[:, keep], [c for c, k in zip(cols, keep) if k]
    X = (X - X.mean(0)) / X.std(0)
    exp4 = (aset.experiment == 4).astype(float)
    D = np.column_stack([np.ones(aset.n), exp4, X])
    names = ["intercept", "experiment_E4"] + cols
    fit = crossed_reml(y, D, aset.person, aset.ev, names)
    fit["groups"] = dict(a="person", b="experiment x video")
    return fit


def run_identity_probe(spec, cfg, source, tracker, ex, reps: int = 10):
    from .diagnostics import identity_probe
    from .models import impute_train_mean
    from .splits import inner_folds

    key = _ctx_key(cfg, spec)
    cfg_w, aset, prov = _context(*key)
    K = cfg.resampling["outer_folds_A"]
    folds = outer_folds(aset, K, cfg.resampling["reps_A"], cfg.resampling["base_seed"], aset.name, "A")
    blocks = ("RF_EEG", "RF_ECG", "RF_GAZE", "SYN_EEG", "SYN_ECG", "SYN_GAZE")
    reps = min(reps, cfg.resampling["reps_A"])

    def splits():
        for r in range(reps):
            for k in range(K):
                test = folds[r][aset.person] == k
                train = ~test
                syn = prov.syn(refs_mod.regime_A(aset, train, np.ones(aset.n, bool)))
                X, _ = prov.design(blocks, syn)
                tr, te = np.flatnonzero(train), np.flatnonzero(test)
                Xtr, Xte, _ = impute_train_mean(X[tr], X[te])
                Xall = np.empty_like(X)
                Xall[tr], Xall[te] = Xtr, Xte
                fmap = inner_folds(aset.person[tr], cfg.raw["model"]["inner_folds"], cfg.resampling["base_seed"],
                                   aset.name, "probe", r, k)
                yield tr, te, Xall, np.array([fmap[p] for p in aset.person[tr]])

    return identity_probe(splits(), aset.ev, cfg.lambda_grid_rel)


RUNNERS = {"A": run_A, "BC": run_BC, "CAS": run_CAS, "transport": run_transport_analysis,
           "explanatory": run_explanatory, "identity_probe": run_identity_probe}
