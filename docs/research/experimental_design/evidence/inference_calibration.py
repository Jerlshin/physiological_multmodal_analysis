"""Targeted calibration of the H1 decision procedures (gate M04/M06).

The main precision simulation showed that interval methods for the cross-validated
skill undercover on the LOW side when signal is present: ridge shrinkage makes the
spread of the estimate smaller when the realized estimate is small. This script
calibrates the decision procedures themselves, on PAS-core, at the points that
matter for the pre-declared rules:

* the null (true skill 0): type-I error of the detection test, and the probability
  of ruling out delta;
* true procedure skill about delta (0.05): the futility test's error rate;
* true procedure skill about 2 delta (0.10): detection power.

Tests compared:

* person bootstrap;
* corrected resampled t (Nadeau & Bengio);
* a Freedman-Lane-style permutation test. The physiological block is residualized
  on content, covariates and quality using full-data OLS that never uses outcomes;
  residuals are then permuted within experiment x video, with the outer folds
  paired across permutations.

The futility bound is the corrected-t upper bound with a multiplier chosen so that
P(rule out | truth = delta) <= 0.05.

Uses only simulated data. Run from the repository root after precision_simulation.py:
    .venv/bin/python docs/research/experimental_design/evidence/inference_calibration.py           # cell-wise permutation
    .venv/bin/python docs/research/experimental_design/evidence/inference_calibration.py --person  # person-block permutation
"""
from __future__ import annotations

import json
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm, t as tdist

EV = Path(__file__).resolve().parent
sys.path.insert(0, str(EV))
import precision_simulation as psim  # noqa: E402  (importable by spawned workers)

SET = "PAS_E34_core"
N_FEAT = 9
K = 10
R = 4          # paired outer-CV repetitions for observed and permuted statistics
B_PERM = 99
DELTA = psim.DELTA
# "cell": residuals permuted cell-wise within experiment x video (shown invalid: breaks person coherence)
# "person": whole-person residual blocks exchanged among people of the same experiment with the
#           identical tested-video pattern (people with a unique pattern stay fixed; conservative)
PERM_MODE = "person" if "--person" in sys.argv else "cell"


def cv_losses(d, inc, folds, rng, X=None):
    """Person-balanced base/full losses for fixed fold assignments (list of arrays)."""
    n = len(d["y"])
    W = np.column_stack([d["T"], d["Q"]])
    WX = np.column_stack([W, d["X"] if X is None else X])
    n_ev, n_p = len(inc["ev_exp"]), len(inc["exp_of_person"])
    lb, lf, fold_d = np.zeros(n), np.zeros(n), []
    for f in folds:
        for k in range(K):
            te, tr = f == k, f != k
            fe, _ = psim.ev_means(d["y"][tr], inc["ev"][tr], n_ev)
            r = d["y"][tr] - fe[inc["ev"][tr]]
            g = inc["person"][tr]
            pb = np.clip(fe[inc["ev"][te]] + psim.fit_predict(W[tr], r, g, W[te], rng), 0, 1)
            pf = np.clip(fe[inc["ev"][te]] + psim.fit_predict(WX[tr], r, g, WX[te], rng), 0, 1)
            eb, ef = (pb - d["y"][te]) ** 2, (pf - d["y"][te]) ** 2
            lb[te] += eb / len(folds)
            lf[te] += ef / len(folds)
            fold_d.append(psim.person_mean(eb - ef, inc["person"][te], n_p).mean())
    Lb, ok = psim.person_balanced(lb, inc["person"], n_p)
    Lf, _ = psim.person_balanced(lf, inc["person"], n_p)
    return Lb[ok], Lf[ok], np.array(fold_d), ok


def replicate(args):
    seed, amp, phi = args
    rng = np.random.default_rng(seed)
    inc, par = psim.INC[SET], psim.PAR
    n_p = len(inc["exp_of_person"])
    beta, wx, wq = psim.draw_content(inc, par, rng, N_FEAT)
    y, T, Q, X = psim.generate(inc["person"], inc["ev"], inc["vid"], inc["exp"], inc["exp_of_person"], par,
                               beta, wx, wq, amp, phi, N_FEAT, rng)
    d = dict(y=y, T=T, Q=Q, X=X)
    folds = [psim.person_folds(inc["person"], inc["exp_of_person"], K, rng) for _ in range(R)]
    Lb, Lf, fold_d, ok = cv_losses(d, inc, folds, rng)
    base = Lb.mean()
    dp = Lb - Lf
    obs = dp.mean()
    out = dict(seed=seed, est=obs / base, base_mse=base, delta_cv=obs)
    # corrected resampled t
    J = len(fold_d)
    se_nb = np.sqrt(fold_d.var(ddof=1) * (1 / J + 1 / (K - 1)))
    out["nb_centre"], out["nb_se"], out["nb_df"] = fold_d.mean(), se_nb, J - 1
    # person bootstrap
    Wb = psim.stratified_weights(inc["exp_of_person"][ok], rng, psim.B_BOOT)
    bs = Wb @ dp / Wb.sum(1)
    out["boot_lo"], out["boot_hi"] = np.quantile(bs, [0.05, 0.95])
    # Freedman-Lane-style permutation of residualized X within experiment x video
    Z = np.column_stack([np.eye(len(inc["ev_exp"]))[inc["ev"]], T, Q])
    coef, *_ = np.linalg.lstsq(Z, X, rcond=None)
    Xhat = Z @ coef
    Xres = X - Xhat
    groups = [np.flatnonzero(inc["ev"] == e) for e in range(len(inc["ev_exp"]))]
    cell_of = {(p, e): i for i, (p, e) in enumerate(zip(inc["person"], inc["ev"]))}
    pattern_groups = {}
    for p, pat in enumerate(inc["patterns"]):
        pattern_groups.setdefault((inc["exp_of_person"][p], tuple(pat)), []).append(p)
    null = []
    for _ in range(B_PERM):
        perm = np.arange(len(y))
        if PERM_MODE == "cell":
            for g in groups:
                perm[g] = rng.permutation(g)
        else:
            for (_, pat), members in pattern_groups.items():
                if len(members) < 2:
                    continue
                for src, dst in zip(members, rng.permutation(members)):
                    for e in pat:
                        perm[cell_of[(src, e)]] = cell_of[(dst, e)]
        _, Lf_p, _, _ = cv_losses(d, inc, folds, rng, X=Xhat + Xres[perm])
        null.append((Lb - Lf_p).mean())
    out["perm_p"] = (1 + np.sum(np.array(null) >= obs)) / (1 + B_PERM)
    # truth: train on all n people, evaluate on fresh people with the same content
    cp, ce, cv, cx, pe = psim.sample_people(inc, 1500, rng)
    yN, TN, QN, XN = psim.generate(cp, ce, cv, cx, pe, par, beta, wx, wq, amp, phi, N_FEAT, rng)
    dN = dict(y=np.concatenate([y, yN]), T=np.vstack([T, TN]), Q=np.vstack([Q, QN]), X=np.vstack([X, XN]))
    incN = dict(inc)
    incN["ev"] = np.concatenate([inc["ev"], ce])
    incN["person"] = np.concatenate([inc["person"], cp + n_p])
    tr = np.r_[np.ones(len(y), bool), np.zeros(len(yN), bool)]
    lbN, lfN = psim.fit_pair_losses(dN, incN, tr, ~tr, rng)
    LbN, LfN = psim.person_mean(lbN, cp, 1500), psim.person_mean(lfN, cp, 1500)
    out["truth"] = 1 - LfN.mean() / LbN.mean()
    return out


def operating(df, delta=DELTA):
    res = {"n": len(df), "expected_truth": df.truth.mean(), "mean_est": df.est.mean()}
    tq = tdist.ppf(0.95, df.nb_df.iloc[0])
    res["detect_perm"] = (df.perm_p <= 0.05).mean()
    res["detect_nb"] = ((df.nb_centre - tq * df.nb_se) > 0).mean()
    res["detect_boot"] = (df.boot_lo > 0).mean()
    for m in [1.645, 1.96, 2.33, 2.58, 3.0]:
        res[f"futility_nb_z{m}"] = (((df.nb_centre + m * df.nb_se) / df.base_mse) < delta).mean()
    return res


def main():
    inc = {SET: psim.incidence(SET)}
    par = psim.outcome_params()
    psim.init_worker(inc, par)
    phi = psim.mix_angle(SET, "proportional")
    # oracle targets chosen from the main simulation's mapping so that the expected
    # procedure skill is about 0, delta (0.05) and 2 delta (0.10)
    targets = {"null": 0.0, "truth_at_delta": 0.085, "truth_at_2delta": 0.14}
    if PERM_MODE == "person":
        targets = {"null": 0.0, "truth_at_2delta": 0.14}
    nsim = 300
    rows, t0 = [], time.time()
    ctx = get_context("spawn")
    with ctx.Pool(10, initializer=psim.init_worker, initargs=(inc, par)) as pool:
        for i, (label, tgt) in enumerate(targets.items()):
            amp = psim.calibrate_amp(SET, tgt, phi, N_FEAT)
            df = pd.DataFrame(pool.map(replicate, [(7_000_000 * (i + 1) + j, amp, phi) for j in range(nsim)],
                                       chunksize=2))
            df.to_csv(EV / "simulation_replicates" / f"calibration_{PERM_MODE}perm_{label}.csv", index=False)
            res = operating(df)
            res.update(scenario=label, oracle_target=tgt, perm_mode=PERM_MODE)
            rows.append(res)
            print(f"[{time.time()-t0:7.1f}s] {label} " + " ".join(
                f"{k}={v:.3f}" for k, v in res.items() if isinstance(v, float)), flush=True)
    pd.DataFrame(rows).to_csv(EV / f"inference_calibration_summary_{PERM_MODE}perm.csv", index=False)
    (EV / f"inference_calibration_meta_{PERM_MODE}perm.json").write_text(json.dumps(
        dict(phase_date="2026-10-04", set=SET, nsim=nsim, R=R, B_perm=B_PERM, K=K, delta=DELTA,
             targets=targets, perm_mode=PERM_MODE, physiology_outcome_association_used=False), indent=2) + "\n")


if __name__ == "__main__":
    main()
