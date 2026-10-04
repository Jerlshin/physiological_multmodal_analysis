"""Outcome-only psychometrics for the experimental-design phase (WP2/WP4).

Reads audited quiz items and gate eligibility. It uses NO physiological variable
and fits no predictor of outcomes from signals. Results feed three pre-declared
decisions (phase_plan.md rules 1-2) and the precision simulation:

* floor/ceiling and internal consistency of exact-set versus partial-credit scores;
* crossed person/video variance components (REML) of the video score;
* the "one-item-equivalent" held-out skill that anchors the minimum useful effect.

Run from the repository root:
    .venv/bin/python docs/research/experimental_design/evidence/outcome_psychometrics.py
"""
from pathlib import Path
import json

import numpy as np
import pandas as pd
from scipy import optimize

ROOT = Path(__file__).resolve().parents[4]
AUDIT = ROOT / "docs/research/dataset_exploration/evidence"
OUT = Path(__file__).resolve().parent

# First tested exposure cells (primary), repeated exposure (E5), ocular cohort (E1).
SETS = {
    "E3+E4_first_view": [3, 4],
    "E3": [3],
    "E4": [4],
    "E5_repeat": [5],
    "E1_ocular": [1],
}


def load():
    items = pd.read_parquet(AUDIT / "quiz_items.parquet")
    elig = pd.read_parquet(AUDIT / "gate_closure_behavioral_eligibility.parquet")
    elig = elig[(elig.question_type == "memory") & elig.gate_behavior_eligible]
    items = items[items.question_type == "memory"]
    keys = ["experiment", "participant_id", "canonical_video_id"]
    items = items.merge(elig[keys], on=keys, how="inner")
    items = items[~items.duplicate_item_key]
    return items, elig


def kr20(matrix):
    """Cronbach alpha (KR-20 for binary items) for a persons x items matrix."""
    m = matrix[~np.isnan(matrix).any(axis=1)]
    k = m.shape[1]
    if m.shape[0] < 3 or k < 2:
        return np.nan
    item_var = m.var(axis=0, ddof=1).sum()
    total_var = m.sum(axis=1).var(ddof=1)
    return float(k / (k - 1) * (1 - item_var / total_var)) if total_var > 0 else np.nan


def reml_crossed(y, person, video, fixed):
    """REML for y = X b + a_person + b_video + e, all random effects Gaussian.

    Dense implementation; adequate for a few hundred cells.
    Returns variance components (person, video, residual).
    """
    n = len(y)
    pu, pi = np.unique(person, return_inverse=True)
    vu, vi = np.unique(video, return_inverse=True)
    Zp = np.zeros((n, len(pu))); Zp[np.arange(n), pi] = 1
    Zv = np.zeros((n, len(vu))); Zv[np.arange(n), vi] = 1
    Kp, Kv = Zp @ Zp.T, Zv @ Zv.T
    X = fixed

    def negloglik(theta):
        sp, sv, se = np.exp(theta)
        V = sp * Kp + sv * Kv + se * np.eye(n)
        L = np.linalg.cholesky(V)
        Vi_X = np.linalg.solve(L.T, np.linalg.solve(L, X))
        Vi_y = np.linalg.solve(L.T, np.linalg.solve(L, y))
        XtViX = X.T @ Vi_X
        beta = np.linalg.solve(XtViX, X.T @ Vi_y)
        r = y - X @ beta
        Vi_r = np.linalg.solve(L.T, np.linalg.solve(L, r))
        logdetV = 2 * np.log(np.diag(L)).sum()
        _, logdetXVX = np.linalg.slogdet(XtViX)
        return 0.5 * (logdetV + logdetXVX + r @ Vi_r)

    v0 = np.var(y)
    best = None
    for start in ([0.3, 0.2, 0.5], [0.1, 0.05, 0.8], [0.5, 0.4, 0.3]):
        res = optimize.minimize(negloglik, np.log(np.array(start) * v0), method="Nelder-Mead",
                                options={"xatol": 1e-6, "fatol": 1e-9, "maxiter": 4000})
        if best is None or res.fun < best.fun:
            best = res
    sp, sv, se = np.exp(best.x)
    return {"person": float(sp), "video": float(sv), "residual": float(se), "converged": bool(best.success)}


def one_item_equivalent(items_exact):
    """Held-out relative MSE reduction from observing ONE item when predicting the
    mean of the remaining items of the same video (leave-one-person-out, per video).

    Baseline: training-person mean of the remaining-item score (the video mean).
    Augmented: training-person OLS of remaining-item score on the single item.
    """
    rows = []
    for (exp, vid), frame in items_exact.groupby(["experiment", "canonical_video_id"]):
        wide = frame.pivot_table(index="participant_id", columns="question_no",
                                 values="recomputed_exact_correct", aggfunc="first")
        wide = wide.dropna(axis=0, how="any")
        m = wide.to_numpy(float)
        n, k = m.shape
        if n < 8:
            continue
        for j in range(k):
            x = m[:, j]
            rest = np.delete(m, j, axis=1).mean(axis=1)
            se_base, se_aug = [], []
            for i in range(n):
                tr = np.arange(n) != i
                base = rest[tr].mean()
                xt = x[tr]
                if xt.std() == 0:
                    pred = base
                else:
                    slope = np.cov(xt, rest[tr], ddof=1)[0, 1] / xt.var(ddof=1)
                    pred = rest[tr].mean() + slope * (x[i] - xt.mean())
                se_base.append((rest[i] - base) ** 2)
                se_aug.append((rest[i] - pred) ** 2)
            rows.append({"experiment": exp, "canonical_video_id": vid, "item": int(wide.columns[j]),
                         "n": n, "mse_base": float(np.mean(se_base)), "mse_aug": float(np.mean(se_aug))})
    out = pd.DataFrame(rows)
    out["skill"] = 1 - out.mse_aug / out.mse_base
    return out


def main():
    items, elig = load()
    summary = {"phase_date": "2026-10-04", "physiology_used": False, "sets": {}}
    per_video_rows = []
    oie_tables = []
    for label, exps in SETS.items():
        cells = elig[elig.experiment.isin(exps)].copy()
        it = items[items.experiment.isin(exps)]
        res = {
            "people": int(cells.qualified_participant_id.nunique()),
            "cells": int(len(cells)),
            "videos": int(cells.canonical_video_id.nunique()),
        }
        for score in ["normalized_exact_score", "normalized_partial_score"]:
            s = cells[score]
            res[score] = {
                "mean": float(s.mean()), "sd": float(s.std(ddof=1)),
                "floor_fraction": float((s <= 1e-9).mean()), "ceiling_fraction": float((s >= 1 - 1e-9).mean()),
                "distinct_values": int(s.round(6).nunique()),
            }
        # internal consistency per experiment-video, exact versus partial item scores
        alphas = []
        for (exp, vid), frame in it.groupby(["experiment", "canonical_video_id"]):
            row = {"experiment": int(exp), "canonical_video_id": vid}
            for col, name in [("recomputed_exact_correct", "alpha_exact"), ("recomputed_score", "alpha_partial")]:
                wide = frame.pivot_table(index="participant_id", columns="question_no", values=col, aggfunc="first")
                row[name] = kr20(wide.to_numpy(float))
                row["n_people"] = int(wide.dropna().shape[0])
            ve = cells[(cells.experiment == exp) & (cells.canonical_video_id == vid)]
            row["mean_exact"] = float(ve.normalized_exact_score.mean())
            row["sd_exact"] = float(ve.normalized_exact_score.std(ddof=1))
            alphas.append(row)
        alphas = pd.DataFrame(alphas)
        alphas["set"] = label
        per_video_rows.append(alphas)
        res["alpha_exact_median"] = float(alphas.alpha_exact.median())
        res["alpha_partial_median"] = float(alphas.alpha_partial.median())
        # crossed variance components; fixed effect per experiment
        if res["videos"] > 1:
            for score in ["normalized_exact_score", "normalized_partial_score"]:
                fixed = pd.get_dummies(cells.experiment.astype(str), drop_first=False).to_numpy(float)
                vc = reml_crossed(cells[score].to_numpy(float), cells.qualified_participant_id.to_numpy(),
                                  cells.canonical_video_id.to_numpy(), fixed)
                tot = vc["person"] + vc["video"] + vc["residual"]
                vc["person_fraction"] = vc["person"] / tot
                vc["video_fraction"] = vc["video"] / tot
                res["variance_components_" + score] = vc
        oie = one_item_equivalent(it)
        oie["set"] = label
        oie_tables.append(oie)
        res["one_item_equivalent_skill"] = {
            "mean": float(oie.skill.mean()), "median": float(oie.skill.median()),
            "video_mean_of_means": float(oie.groupby("canonical_video_id").skill.mean().mean()),
            "items": int(len(oie)),
        }
        summary["sets"][label] = res

    primary = summary["sets"]["E3+E4_first_view"]
    oie_value = primary["one_item_equivalent_skill"]["mean"]
    summary["minimum_useful_effect_rule"] = "delta = max(0.05, one-item-equivalent skill) on E3+E4 first view, exact score"
    summary["delta"] = float(np.round(max(0.05, oie_value), 2))
    summary["outcome_rule_check"] = {
        "exact_floor_or_ceiling_gt_15pct": bool(
            primary["normalized_exact_score"]["floor_fraction"] > 0.15
            or primary["normalized_exact_score"]["ceiling_fraction"] > 0.15),
        "exact_alpha_lower_by_gt_0.10": bool(
            primary["alpha_partial_median"] - primary["alpha_exact_median"] > 0.10),
    }
    pd.concat(per_video_rows).to_csv(OUT / "outcome_reliability_by_video.csv", index=False)
    pd.concat(oie_tables).to_csv(OUT / "one_item_equivalent_items.csv", index=False)
    (OUT / "outcome_psychometrics.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
