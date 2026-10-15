"""Outcome-free calibration of the detection test on this cohort's real features (BBBD V2 analogue).

Synthetic posttest scores on the 13-item scale, generated without reading any outcome:

* pure null: independent of every feature;
* nuisance null: 40 % of the latent variance is a random linear combination of the baseline
  columns (C, P, Q), which M2p contains, so the gaze block still carries no information.

For each dataset the primary contrast (M5p vs M2p) is fitted on the first 10 repetitions of the
real folds and tested with the frozen Freedman-Lane permutation test (199 permutations). The
pre-declared criterion is the BBBD validation bound: false detection <= 0.07.
"""
from __future__ import annotations

import json

import numpy as np

from g01r import inference as inf
from g01r import metrics as met
from g01r.config import load_config
from g01r.rng import rng_for

from .analysis import COMPARISONS, Executor, _context, fit_set
from .paths import EVIDENCE

N_DATASETS = 200
B_VALIDATION = 199
MAX_FALSE_DETECTION = 0.07


def synthetic_scores(scenario: str, s: int) -> np.ndarray:
    cfg, aset, prov = _context("primary", ())
    rng = rng_for(cfg.resampling["base_seed"], "john2025_null", scenario, s)
    z = rng.normal(size=aset.n)
    if scenario == "nuisance":
        X, _ = prov.design(("C", "P", "Q"), None)
        X = (X - X.mean(0)) / np.where(X.std(0) > 0, X.std(0), 1.0)
        comb = X @ rng.normal(size=X.shape[1])
        z = np.sqrt(0.6) * z + np.sqrt(0.4) * (comb - comb.mean()) / comb.std()
    return np.clip(np.round((0.45 + 0.2 * z) * 13) / 13, 0, 1)


def _task_null(args):
    scenario, s = args
    cfg, aset, prov = _context("primary", ())
    comp = COMPARISONS[0]
    y = synthetic_scores(scenario, s)
    R_perm = cfg.inference["reps_permutation"]
    ex = Executor(1)
    fit = fit_set(ex, "primary", [comp.base, comp.full], y, R_perm, keep_reps=R_perm, keep_models=[comp.full])
    lb = met.cell_losses(fit.preds[comp.base], y)
    lf = met.cell_losses(fit.preds[comp.full], y)
    obs = inf.permutation_statistic(lb, lf, aset.person)
    perms = inf.draw_permutations(aset, B_VALIDATION, cfg.resampling["base_seed"], aset.name, "validation", scenario, s)
    tested = [c for b in comp.test[0] for c in prov.block_columns(b)]
    nuisance = [c for b in comp.test[1] for c in prov.block_columns(b)]
    prepared = inf.prepare_permutation(aset, inf.PermutationSetup(fit.designs, comp.full, tested, nuisance))
    null = inf.permutation_null(aset, prepared, y, lb, perms, cfg.lambda_grid_rel, cfg.raw["model"]["standardize_min_sd"])
    return scenario, s, float(obs / met.person_means(lb, aset.person).mean()), inf.permutation_p(obs, null)


def run(workers: int = 5, n: int = N_DATASETS) -> dict:
    ex = Executor(workers)
    try:
        rows = ex.map(_task_null, [(sc, s) for sc in ("pure", "nuisance") for s in range(n)])
    finally:
        ex.close()
    out = dict(description=__doc__.strip().splitlines()[0], datasets_per_scenario=n, permutations=B_VALIDATION,
               criterion_max_false_detection=MAX_FALSE_DETECTION, scenarios={})
    for sc in ("pure", "nuisance"):
        p = np.array([r[3] for r in rows if r[0] == sc])
        sk = np.array([r[2] for r in rows if r[0] == sc])
        rate = float(np.mean(p <= 0.05))
        out["scenarios"][sc] = dict(false_detection=rate, mc_se=float(np.sqrt(rate * (1 - rate) / len(p))),
                                    mean_skill=float(sk.mean()), sd_skill=float(sk.std(ddof=1)),
                                    p_quantiles=np.quantile(p, [0.05, 0.25, 0.5, 0.75]).round(4).tolist())
    out["passes"] = all(v["false_detection"] <= MAX_FALSE_DETECTION for v in out["scenarios"].values())
    path = EVIDENCE / "validation" / "null_calibration_summary.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1) + "\n")
    return out
