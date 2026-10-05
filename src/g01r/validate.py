"""Production re-validation of the inference operating characteristics (protocol §17.3).

V1: the design-phase simulation (docs/research/experimental_design/evidence/precision_simulation.py
    generator, PAS-core incidence, "proportional" information) re-run through the PRODUCTION
    pipeline: production splits, ridge, inner CV, content offsets, person-block Freedman-Lane
    permutation (R = 10 paired repetitions, B = 999), corrected-t futility on R = 50, and
    nested CV. Targets: false detection <= 0.07; power >= 0.80 at 2 delta; futility error <= 0.05.
V2: null calibration on the REAL feature matrices (real C, Q, RF and split-specific SYN) with
    synthetic outcomes that carry no physiological information (pure null, and a nuisance null
    where outcomes depend on C and Q). Addresses the design simulation's stated limitation
    (Gaussian, uncorrelated synthetic features).

No real quiz outcome is used anywhere in this module.
"""
from __future__ import annotations

import importlib.util
import sys
import time
from multiprocessing import get_context

import numpy as np
import pandas as pd

from . import inference as inf
from . import metrics as met
from .config import DESIGN_EVIDENCE, load_config
from .design import FixedFeatureProvider
from .models import ModelSpec
from .pipeline import Pipeline, run_regime_A
from .population import AnalysisSet, Population
from .rng import rng_for

BASE = ModelSpec("BASE", ("C", "Q"))
FULL = ModelSpec("FULL", ("C", "Q", "PHYS"))
_STATE: dict = {}


def _psim():
    if "psim" not in _STATE:
        spec = importlib.util.spec_from_file_location("precision_simulation", DESIGN_EVIDENCE / "precision_simulation.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["precision_simulation"] = mod
        spec.loader.exec_module(mod)
        inc = {"PAS_E34_core": mod.incidence("PAS_E34_core")}
        mod.init_worker(inc, mod.outcome_params())
        _STATE["psim"] = mod
    return _STATE["psim"]


def _setup(cfg_path):
    if "aset" not in _STATE:
        cfg = load_config(cfg_path)
        pop = Population(cfg)
        _STATE.update(cfg=cfg, aset=pop.analysis_set("PAS_E34_core"))
    return _STATE["cfg"], _STATE["aset"]


def _inc_from_aset(aset: AnalysisSet) -> dict:
    return dict(person=aset.person, ev=aset.ev, exp=aset.experiment, vid=aset.video, exp_of_person=aset.exp_of_person,
                ev_exp=aset.ev_experiment, ev_vid=aset.ev_video, n_vid=aset.n_video,
                patterns=[np.array(p) for _, p in sorted(aset.patterns().items())])


def _fresh_set(aset: AnalysisSet, inc: dict, rng, n_new: int):
    """Original cells plus n_new fresh synthetic learners re-using observed experiment/content patterns."""
    pick = rng.integers(0, aset.n_person, n_new)
    ev_video_id = aset.cells.groupby("ev").canonical_video_id.first().sort_index().to_numpy()
    rows, cp, ce = [], [], []
    for i, p in enumerate(pick):
        e = int(inc["exp_of_person"][p])
        for ev in inc["patterns"][p]:
            rows.append(dict(experiment=e, participant_id=f"syn-{i:05d}", qualified_participant_id=f"exp-{e}:syn-{i:05d}",
                             session=0, local_stimulus_id=0, canonical_video_id=ev_video_id[ev], condition="synthetic",
                             exposure_number=1))
            cp.append(i)
            ce.append(ev)
    cols = ["experiment", "participant_id", "qualified_participant_id", "session", "local_stimulus_id",
            "canonical_video_id", "condition", "exposure_number"]
    combined = pd.concat([aset.cells[cols], pd.DataFrame(rows)], ignore_index=True)
    big = AnalysisSet("PAS_E34_core+fresh", combined)
    cp, ce = np.array(cp), np.array(ce)
    return big, cp, ce, inc["ev_vid"][ce], inc["ev_exp"][ce], inc["exp_of_person"][pick]


def v1_replicate(args):
    cfg_path, seed, amp, phi, n_perm, ncv_reps, R_point = args
    cfg, aset = _setup(cfg_path)
    psim = _psim()
    inc = _inc_from_aset(aset)
    rng = np.random.default_rng(seed)
    n_feat = 9
    beta, wx, wq = psim.draw_content(inc, psim.PAR, rng, n_feat)
    y, T, Q, X = psim.generate(inc["person"], inc["ev"], inc["vid"], inc["exp"], inc["exp_of_person"], psim.PAR,
                               beta, wx, wq, amp, phi, n_feat, rng)
    prov = FixedFeatureProvider({"C": T, "Q": Q, "PHYS": X}, aset.n)
    label = f"v1-{seed}"
    pipe = Pipeline(cfg, aset, prov, [BASE, FULL], seed_label=label)
    R_perm = cfg.inference["reps_permutation"]
    cv = run_regime_A(pipe, y, R=R_point, keep_design_reps=R_perm)
    K = cfg.resampling["outer_folds_A"]
    lb, lf = met.cell_losses(cv.preds["BASE"], y), met.cell_losses(cv.preds["FULL"], y)
    Lb, Lf = met.person_means(lb, aset.person), met.person_means(lf, aset.person)
    out = dict(seed=seed, est=1 - Lf.mean() / Lb.mean(), base_mse=Lb.mean(), delta_cv=(Lb - Lf).mean())
    fd = inf.fold_differences(cv.preds["BASE"], cv.preds["FULL"], y, cv.folds, aset)
    fut = inf.corrected_t_upper(fd, K, cfg.inference["futility_z"], Lb.mean())
    out.update(futility_upper_skill=fut["upper_skill"], nb_centre=fut["centre"], nb_se=fut["se"])
    # Permutation test on the first R_perm paired repetitions (production configuration).
    lb10 = met.cell_losses(cv.preds["BASE"][:R_perm], y)
    lf10 = met.cell_losses(cv.preds["FULL"][:R_perm], y)
    obs = inf.permutation_statistic(lb10, lf10, aset.person)
    cols = prov.block_columns("PHYS")
    nuis = prov.block_columns("C") + prov.block_columns("Q")
    prepared = inf.prepare_permutation(aset, inf.PermutationSetup(cv.designs, "FULL", cols, nuis))
    perms = inf.draw_permutations(aset, n_perm, cfg.resampling["base_seed"], label)
    null = inf.permutation_null(aset, prepared, y, lb10, perms, cfg.lambda_grid_rel, cfg.raw["model"]["standardize_min_sd"])
    out["perm_p"] = inf.permutation_p(obs, null)
    # Declared fallback (person bootstrap) evaluated on the same data.
    fb = inf.person_bootstrap_detection(Lb - Lf, aset.exp_of_person, rng_for(seed, "fallback"), cfg.inference["bootstrap_B"])
    out["fallback_detect"] = fb["detect"]
    # Nested CV interval (production procedure; fewer repetitions than the confirmatory 200).
    if ncv_reps:
        def fit_pair(train, test, labels):
            res = pipe.fit_split(y[train], train, test, None, "A", labels=labels)
            return res.preds["BASE"], res.preds["FULL"]
        pieces = [inf.nested_cv_pieces(aset, fit_pair, {"person": inf.person_loss_diff(y, aset)}, K,
                                       cfg.resampling["base_seed"], (label, "ncv"), r)["person"] for r in range(ncv_reps)]
        ci = inf.nested_cv_interval(pieces, (Lb - Lf).mean(), Lb - Lf, Lb.mean(), K, cfg.inference["ncv_level"])
        out.update(ncv_lo=ci["lo"], ncv_hi=ci["hi"], ncv_lo_skill=ci["lo_skill"], ncv_hi_skill=ci["hi_skill"])
    # Procedure truth: the production pipeline trained on all n learners, evaluated on 1500 fresh learners.
    big, cp, ce, cv_, cx, pe = _fresh_set(aset, inc, rng, 1500)
    yN, TN, QN, XN = psim.generate(cp, ce, cv_, cx, pe, psim.PAR, beta, wx, wq, amp, phi, n_feat, rng)
    provN = FixedFeatureProvider({"C": np.vstack([T, TN]), "Q": np.vstack([Q, QN]), "PHYS": np.vstack([X, XN])}, big.n)
    pipeN = Pipeline(cfg, big, provN, [BASE, FULL], seed_label=label + "-truth")
    train = np.r_[np.ones(aset.n, bool), np.zeros(len(yN), bool)]
    yy = np.r_[y, yN]
    res = pipeN.fit_split(y, train, ~train, None, "A", labels=("truth",))
    eb, ef = (res.preds["BASE"] - yN) ** 2, (res.preds["FULL"] - yN) ** 2
    pidx = big.person[~train]
    TbN, TfN = met.person_means(eb, pidx), met.person_means(ef, pidx)
    out["truth"] = 1 - TfN.mean() / TbN.mean()
    out["truth_delta"] = TbN.mean() - TfN.mean()
    return out


def v1_operating(df: pd.DataFrame, cfg) -> dict:
    alpha, thr = cfg.inference["alpha"], cfg.inference["futility_threshold"]
    res = dict(n=len(df), expected_truth=float(df.truth.mean()), mean_est=float(df.est.mean()),
               detect_perm=float((df.perm_p <= alpha).mean()),
               detect_fallback_bootstrap=float(df.fallback_detect.mean()),
               futility_rules_out_threshold=float((df.futility_upper_skill < thr).mean()))
    delta = cfg.inference["delta"]
    res["est_ge_delta"] = float((df.est >= delta).mean())
    res["decision_detected_useful"] = float(((df.perm_p <= alpha) & (df.est >= delta)).mean())
    if "ncv_lo" in df:
        res["ncv_cover90_conditional"] = float(((df.ncv_lo <= df.truth_delta) & (df.truth_delta <= df.ncv_hi)).mean())
    p = res["detect_perm"]
    res["detect_perm_mc_se"] = float(np.sqrt(p * (1 - p) / len(df)))
    return res


def run_v1(cfg_path: str, nsim: int = 300, workers: int = 9, n_perm: int | None = None, ncv_reps: int = 20,
           R_point: int | None = None, out_dir=None, tracker=None):
    cfg = load_config(cfg_path)
    psim = _psim()
    phi = psim.mix_angle("PAS_E34_core", "proportional")
    n_perm = n_perm or cfg.inference["n_permutations"]
    R_point = R_point or cfg.resampling["reps_A"]
    scenarios = {"null": 0.0, "truth_at_2delta": 0.14}     # oracle targets of inference_calibration.py --person
    rows, t0 = [], time.time()
    with get_context("spawn").Pool(workers) as pool:
        for i, (label, target) in enumerate(scenarios.items()):
            amp = psim.calibrate_amp("PAS_E34_core", target, phi, 9)
            args = [(cfg_path, 91_000_000 * (i + 1) + j, amp, phi, n_perm, ncv_reps, R_point) for j in range(nsim)]
            df = pd.DataFrame(pool.map(v1_replicate, args, chunksize=1))
            df["scenario"] = label
            if out_dir is not None:
                df.to_csv(out_dir / f"v1_replicates_{label}.csv", index=False)
            if tracker is not None:
                tracker.log_frame(f"v1_replicates_{label}.csv", df)
            op = v1_operating(df, cfg)
            op.update(scenario=label, oracle_target=target, amp=amp, phi=phi, n_perm=n_perm, R_point=R_point,
                      R_perm=cfg.inference["reps_permutation"], ncv_reps=ncv_reps, elapsed_s=time.time() - t0)
            rows.append(op)
            print(f"[V1 {time.time() - t0:7.0f}s] {label}: " + ", ".join(f"{k}={v:.3f}" for k, v in op.items()
                                                                           if isinstance(v, float)), flush=True)
    return pd.DataFrame(rows)


# ============================================================================ V2: real features, synthetic null outcomes
def v2_replicate(args):
    """One synthetic null outcome on the real PAS-core features, H1 test with the production runner."""
    from .analysis import OutcomeSource, _context

    cfg_path, seed_label, scenario, n_perm, R_point = args
    cfg = load_config(cfg_path)
    key = (str(cfg.path), (), "PAS_E34_core", "processed", False)
    cfg_w, aset, prov = _context(*key)
    from .models import FAMILY

    src = OutcomeSource("synthetic", scenario=scenario, seed_label=seed_label)
    y = src.outcomes(cfg, aset, "exact", prov)
    pipe = Pipeline(cfg, aset, prov, [FAMILY["M2"], FAMILY["M5"]])     # production folds of PAS-core (paired)
    R_perm = cfg.inference["reps_permutation"]
    cv = run_regime_A(pipe, y, R=R_point, keep_design_reps=R_perm)
    lb, lf = met.cell_losses(cv.preds["M2"], y), met.cell_losses(cv.preds["M5"], y)
    Lb, Lf = met.person_means(lb, aset.person), met.person_means(lf, aset.person)
    fd = inf.fold_differences(cv.preds["M2"], cv.preds["M5"], y, cv.folds, aset)
    fut = inf.corrected_t_upper(fd, cfg.resampling["outer_folds_A"], cfg.inference["futility_z"], Lb.mean())
    lb10, lf10 = met.cell_losses(cv.preds["M2"][:R_perm], y), met.cell_losses(cv.preds["M5"][:R_perm], y)
    obs = inf.permutation_statistic(lb10, lf10, aset.person)
    tested = [c for b in ("RF_EEG", "RF_ECG", "RF_GAZE", "SYN_EEG", "SYN_ECG", "SYN_GAZE") for c in prov.block_columns(b)]
    nuis = prov.block_columns("C") + prov.block_columns("Q")
    prepared = inf.prepare_permutation(aset, inf.PermutationSetup(cv.designs, "M5", tested, nuis))
    perms = inf.draw_permutations(aset, n_perm, cfg.resampling["base_seed"], "v2", seed_label)
    null = inf.permutation_null(aset, prepared, y, lb10, perms, cfg.lambda_grid_rel, cfg.raw["model"]["standardize_min_sd"])
    return dict(seed_label=seed_label, est=1 - Lf.mean() / Lb.mean(), perm_p=inf.permutation_p(obs, null),
                futility_upper_skill=fut["upper_skill"])


def run_v2(cfg_path: str, nsim: int = 200, workers: int = 9, n_perm: int = 199, R_point: int | None = None,
           scenarios=None, tracker=None, out_dir=None):
    cfg = load_config(cfg_path)
    R_point = R_point or cfg.resampling["reps_A"]
    scenarios = scenarios or {
        "pure_null": dict(nsim=nsim),
        "nuisance_null": dict(nsim=nsim, nuisance_share=0.3),
        # Sanity check of power on the real feature space (not a calibration target).
        "planted_rf_signal": dict(nsim=max(1, nsim // 2), signal_amp=0.12,
                                  signal_features=["RF1_eeg_posterior_alpha", "RF3_heart_rate", "RF5_gaze_dispersion"]),
    }
    rows, t0 = [], time.time()
    with get_context("spawn").Pool(workers) as pool:
        for label, sc in scenarios.items():
            sc = dict(sc)
            n_this = sc.pop("nsim", nsim)
            args = [(cfg_path, f"v2-{label}-{j}", sc, n_perm, R_point) for j in range(n_this)]
            df = pd.DataFrame(pool.map(v2_replicate, args, chunksize=1))
            df["scenario"] = label
            if out_dir is not None:
                df.to_csv(out_dir / f"v2_replicates_{label}.csv", index=False)
            if tracker is not None:
                tracker.log_frame(f"v2_replicates_{label}.csv", df)
            p = float((df.perm_p <= cfg.inference["alpha"]).mean())
            delta = cfg.inference["delta"]
            op = dict(scenario=label, n=len(df), detect_perm=p, detect_perm_mc_se=float(np.sqrt(p * (1 - p) / len(df))),
                      mean_est=float(df.est.mean()), sd_est=float(df.est.std()),
                      est_ge_delta=float((df.est >= delta).mean()),
                      decision_detected_useful=float(((df.perm_p <= cfg.inference["alpha"]) & (df.est >= delta)).mean()),
                      futility_rules_out_threshold=float((df.futility_upper_skill < cfg.inference["futility_threshold"]).mean()),
                      n_perm=n_perm, R_point=R_point, elapsed_s=time.time() - t0,
                      **{f"scenario_{k}": (v if not isinstance(v, list) else "+".join(v)) for k, v in sc.items()})
            rows.append(op)
            print(f"[V2 {time.time() - t0:7.0f}s] {label}: detect={p:.3f} est={op['mean_est']:.4f} "
                  f"futility={op['futility_rules_out_threshold']:.3f}", flush=True)
    return pd.DataFrame(rows)
