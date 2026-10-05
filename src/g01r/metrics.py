"""Prespecified metrics (protocol §10; evaluation contract §6).

All losses are first averaged over outer repetitions per cell, then per person
(person-balanced) or over cells (cell-weighted). Skill = 1 - loss(full) / loss(base).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import DESIGN_EVIDENCE


def cell_losses(preds: np.ndarray, y: np.ndarray, kind: str = "se") -> np.ndarray:
    """Mean over repetitions (rows of ``preds``) of the per-cell loss; NaN-safe across untested reps."""
    err = preds - y[None, :]
    loss = err ** 2 if kind == "se" else np.abs(err)
    return np.nanmean(loss, axis=0)


def person_means(values: np.ndarray, person: np.ndarray, n_person: int | None = None, keep=None) -> np.ndarray:
    n_person = n_person or int(person.max() + 1)
    m = np.ones(len(values), bool) if keep is None else np.asarray(keep, bool)
    s = np.bincount(person[m], values[m], minlength=n_person)
    c = np.bincount(person[m], minlength=n_person)
    return s[c > 0] / c[c > 0]


def skill_person_balanced(lb, lf, person) -> float:
    Lb, Lf = person_means(lb, person), person_means(lf, person)
    return float(1 - Lf.mean() / Lb.mean())


def skill_cell_weighted(lb, lf) -> float:
    return float(1 - lf.sum() / lb.sum())


def calibration(pred_mean: np.ndarray, y: np.ndarray) -> dict:
    """Out-of-fold calibration: OLS of y on the (repetition-averaged) prediction."""
    A = np.column_stack([np.ones(len(y)), pred_mean])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return dict(intercept=float(coef[0]), slope=float(coef[1]))


def within_content_losses(y, pred, ev) -> np.ndarray:
    """Squared error after centring outcome and prediction within each experiment x video unit."""
    n_ev = int(ev.max() + 1)
    cnt = np.bincount(ev, minlength=n_ev)
    yc = y - (np.bincount(ev, y, n_ev) / np.maximum(cnt, 1))[ev]
    pc = pred - (np.bincount(ev, pred, n_ev) / np.maximum(cnt, 1))[ev]
    return (yc - pc) ** 2


def double_centre(a: np.ndarray, person: np.ndarray, ev: np.ndarray, iters: int = 50) -> np.ndarray:
    out = np.asarray(a, float).copy()
    cp = np.maximum(np.bincount(person), 1)
    ce = np.maximum(np.bincount(ev), 1)
    for _ in range(iters):
        out = out - (np.bincount(person, out, len(cp)) / cp)[person]
        out = out - (np.bincount(ev, out, len(ce)) / ce)[ev]
    return out


def state_losses(y, pred, person, ev):
    """Double-centred (person and content) squared error among people with >= 2 cells (exploratory state metric)."""
    keep = np.bincount(person)[person] >= 2
    loss = np.full(len(y), np.nan)
    if keep.sum() == 0:
        return loss, keep
    p_idx = np.unique(person[keep], return_inverse=True)[1]
    e_idx = np.unique(ev[keep], return_inverse=True)[1]
    d = double_centre(y[keep], p_idx, e_idx) - double_centre(pred[keep], p_idx, e_idx)
    loss[keep] = d ** 2
    return loss, keep


def state_skill(y, pb, pf, person, ev) -> float:
    lb, keep = state_losses(y, pb, person, ev)
    lf, _ = state_losses(y, pf, person, ev)
    return float(1 - np.nansum(lf[keep]) / np.nansum(lb[keep]))


def reliable_share() -> dict:
    """Reliable share of within-video variance per experiment = 1 - mean((1-alpha) var) / mean(var),
    from the design-phase outcome psychometrics (already computed; no new outcome access)."""
    rel = pd.read_csv(DESIGN_EVIDENCE / "outcome_reliability_by_video.csv")
    out = {}
    for exp, lab in [(1, "E1_ocular"), (3, "E3"), (4, "E4"), (5, "E5_repeat")]:
        rv = rel[rel.set == lab]
        within = float((rv.sd_exact ** 2).mean())
        err = float(((1 - rv.alpha_exact) * rv.sd_exact ** 2).mean())
        out[exp] = 1 - err / within
    return out


def regime_A_report(preds_b: np.ndarray, preds_f: np.ndarray, y: np.ndarray, aset, items: int = 12) -> dict:
    """Primary and companion metrics for one base/full comparison on identical cells and folds."""
    person, ev, exp = aset.person, aset.ev, aset.experiment
    lb, lf = cell_losses(preds_b, y), cell_losses(preds_f, y)
    ab, af = cell_losses(preds_b, y, "ae"), cell_losses(preds_f, y, "ae")
    Lb, Lf = person_means(lb, person), person_means(lf, person)
    pb_mean, pf_mean = np.nanmean(preds_b, axis=0), np.nanmean(preds_f, axis=0)
    out = dict(
        skill_person_balanced=float(1 - Lf.mean() / Lb.mean()),
        skill_cell_weighted=skill_cell_weighted(lb, lf),
        base_mse_person_balanced=float(Lb.mean()),
        full_mse_person_balanced=float(Lf.mean()),
        delta_mse_person_balanced=float(Lb.mean() - Lf.mean()),
        delta_rmse_items=float((np.sqrt(Lb.mean()) - np.sqrt(Lf.mean())) * items),
        delta_mae_items=float((person_means(ab, person).mean() - person_means(af, person).mean()) * items),
        calibration_base=calibration(pb_mean, y),
        calibration_full=calibration(pf_mean, y),
        state_skill=state_skill(y, pb_mean, pf_mean, person, ev),
        n_people=int(len(Lb)), n_cells=int(len(y)), n_videos=int(aset.n_video),
    )
    shares = reliable_share()
    out["per_experiment"] = {}
    for e in np.unique(exp):
        m = exp == e
        s = skill_person_balanced(lb[m], lf[m], person[m])
        out["per_experiment"][int(e)] = dict(skill=s, skill_over_reliable_share=s / shares[int(e)],
                                             reliable_share=shares[int(e)], people=int(len(np.unique(person[m]))),
                                             cells=int(m.sum()))
    out["per_video"] = {}
    for key, m in aset.cells.groupby("ev_key").groups.items():
        m = np.asarray(list(m))
        out["per_video"][key] = dict(skill=skill_cell_weighted(lb[m], lf[m]), people=int(len(m)))
    return out
