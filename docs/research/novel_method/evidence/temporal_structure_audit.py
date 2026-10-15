"""Outcome-free audit: how much ocular engagement structure do whole-video features discard?

Reads only (a) the frozen analysis-set manifest (keys and set flags, no scores) and
(b) the G01-R 128 Hz signal cache (gaze in pixels with NaN outside the frozen valid
mask; pupil z-scored within recording). No quiz outcome, item response or score file
is opened. Nothing here is a predictive analysis.

For each experiment x canonical-video unit of a set, every learner's tested exposure is
cut into non-overlapping windows (default 10 s). Per window it computes:

* ``valid``  - fraction of valid gaze samples (on-screen, outside correction intervals);
* ``isc``    - gaze ISC: mean over x and y of Pearson r with the leave-one-out mean of
               the unit's other viewers (pairwise-valid samples; >= 30% valid required);
* ``isc_x`` / ``isc_y`` - the two axes separately (two semi-independent readings);
* ``disp``   - gaze dispersion / screen diagonal;
* ``pupil_isc`` - the same ISC for the within-recording z-scored pupil.

Each person x window matrix is decomposed additively (fitted on observed cells) into a
person level a_p (what a whole-video feature keeps), a window level b_w (shared,
stimulus-locked: what every viewer does at that moment) and a person x window residual
e_pw (idiosyncratic, time-localized deviations: what whole-video averaging discards).

The script reports variance shares, the agreement of the x- and y-axis residuals
(a split-measure reliability of the idiosyncratic component), residual autocorrelation
across windows (persistence of engagement episodes) and the coupling between the
validity and ISC residuals (looking-away episodes).

Usage: python temporal_structure_audit.py [--window 10] [--out DIR]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
MANIFEST = ROOT / "docs/research/experimental_design/evidence/analysis_set_manifest.csv"
CACHE = ROOT / "data/derived/g01r/cache/processed"
FS = 128
DIAG = 2203.0
SETS = ("PAS_E34_core", "E1_gaze", "E5_core")


def uid(r) -> str:
    return f"e{int(r.experiment)}_{r.participant_id}_s{int(r.session)}_t{int(r.local_stimulus_id)}"


def loo_reference(stack: np.ndarray) -> np.ndarray:
    """Leave-one-out mean over people (axis 0), NaN-aware."""
    filled = np.nan_to_num(stack)
    count = (~np.isnan(stack)).sum(axis=0)
    total = filled.sum(axis=0)
    own = ~np.isnan(stack)
    with np.errstate(invalid="ignore", divide="ignore"):
        ref = (total[None] - filled) / (count[None] - own)
    ref[(count[None] - own) < 2] = np.nan
    return ref


def wcorr(a: np.ndarray, b: np.ndarray, min_valid: int) -> float:
    ok = ~(np.isnan(a) | np.isnan(b))
    if ok.sum() < min_valid:
        return np.nan
    a, b = a[ok], b[ok]
    sa, sb = a.std(), b.std()
    if sa == 0 or sb == 0:
        return np.nan
    return float(((a - a.mean()) * (b - b.mean())).mean() / (sa * sb))


def two_way(F: np.ndarray, iters: int = 50):
    """Additive fit F[p,w] = mu + a_p + b_w + e_pw on observed cells."""
    obs = ~np.isnan(F)
    mu = np.nanmean(F)
    a = np.zeros(F.shape[0])
    b = np.zeros(F.shape[1])
    for _ in range(iters):
        r = F - mu - b[None]
        a = np.array([np.nanmean(r[i]) if obs[i].any() else 0.0 for i in range(F.shape[0])])
        r = F - mu - a[:, None]
        b = np.array([np.nanmean(r[:, j]) if obs[:, j].any() else 0.0 for j in range(F.shape[1])])
    e = F - mu - a[:, None] - b[None]
    A = np.broadcast_to(a[:, None], F.shape)[obs]
    B = np.broadcast_to(b[None], F.shape)[obs]
    E = e[obs]
    return dict(var_person=float(A.var()), var_window=float(B.var()), var_resid=float(E.var()),
                n_cells=int(obs.sum())), e


def lag_autocorr(e: np.ndarray, lag: int) -> float:
    x, y = e[:, :-lag].ravel(), e[:, lag:].ravel()
    ok = ~(np.isnan(x) | np.isnan(y))
    if ok.sum() < 30:
        return np.nan
    return float(np.corrcoef(x[ok], y[ok])[0, 1])


def pair_corr(e1: np.ndarray, e2: np.ndarray) -> float:
    x, y = e1.ravel(), e2.ravel()
    ok = ~(np.isnan(x) | np.isnan(y))
    if ok.sum() < 30:
        return np.nan
    return float(np.corrcoef(x[ok], y[ok])[0, 1])


def unit_features(cells: pd.DataFrame, win_s: float):
    L = int(win_s * FS)
    gaze = {}
    pupil = {}
    for r in cells.itertuples(index=False):
        u = uid(r)
        gp, pp = CACHE / "gaze" / f"{u}.npy", CACHE / "pupil" / f"{u}.npy"
        if gp.exists():
            gaze[r.qualified_participant_id] = np.load(gp)
        if pp.exists():
            pupil[r.qualified_participant_id] = np.load(pp).astype(np.float64)
    people = sorted(gaze)
    if len(people) < 5:
        return None
    T = min(len(gaze[p]) for p in people)
    nw = T // L
    G = np.stack([gaze[p][: nw * L] for p in people]).astype(np.float64)  # P x T x 2
    refx, refy = loo_reference(G[..., 0]), loo_reference(G[..., 1])
    P = len(people)
    out = {k: np.full((P, nw), np.nan) for k in ("valid", "isc", "isc_x", "isc_y", "disp", "pupil_isc")}
    minv = int(0.3 * L)
    pp_people = [p for p in people if p in pupil and len(pupil[p]) >= nw * L]
    if len(pp_people) >= 5:
        Pz = np.full((P, nw * L), np.nan)
        for i, p in enumerate(people):
            if p in pupil and len(pupil[p]) >= nw * L:
                Pz[i] = pupil[p][: nw * L]
        refp = loo_reference(Pz)
    else:
        Pz = refp = None
    for i in range(P):
        for w in range(nw):
            s = slice(w * L, (w + 1) * L)
            gx, gy = G[i, s, 0], G[i, s, 1]
            v = ~np.isnan(gx)
            out["valid"][i, w] = v.mean()
            if v.sum() >= minv:
                cx, cy = wcorr(gx, refx[i, s], minv), wcorr(gy, refy[i, s], minv)
                out["isc_x"][i, w], out["isc_y"][i, w] = cx, cy
                out["isc"][i, w] = np.nanmean([cx, cy]) if not (np.isnan(cx) and np.isnan(cy)) else np.nan
                out["disp"][i, w] = np.sqrt(np.nanvar(gx) + np.nanvar(gy)) / DIAG
            if Pz is not None and not np.isnan(Pz[i]).all():
                out["pupil_isc"][i, w] = wcorr(Pz[i, s], refp[i, s], minv)
    return dict(people=P, windows=nw, seconds=T / FS, feats=out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=float, default=10.0)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    args = ap.parse_args()
    m = pd.read_csv(MANIFEST)
    rows, units = [], []
    for s in SETS:
        d = m[m[s]]
        for (exp, vid), cells in d.groupby(["experiment", "canonical_video_id"]):
            res = unit_features(cells, args.window)
            if res is None:
                continue
            units.append(dict(set=s, experiment=int(exp), video=vid, people=res["people"],
                              windows=res["windows"], seconds=round(res["seconds"], 1)))
            F = res["feats"]
            resid = {}
            for k, M in F.items():
                if np.isnan(M).all():
                    continue
                shares, e = two_way(M)
                resid[k] = e
                rows.append(dict(set=s, experiment=int(exp), video=vid, feature=k, **shares,
                                 lag1=lag_autocorr(e, 1), lag3=lag_autocorr(e, 3), lag6=lag_autocorr(e, 6)))
            extra = dict(set=s, experiment=int(exp), video=vid, feature="_pairs",
                         xy_resid_corr=pair_corr(resid["isc_x"], resid["isc_y"]),
                         valid_isc_resid_corr=pair_corr(resid["valid"], resid["isc"]),
                         disp_isc_resid_corr=pair_corr(resid["disp"], resid["isc"]),
                         pupil_gaze_isc_resid_corr=pair_corr(resid.get("pupil_isc", np.full(1, np.nan)), resid["isc"])
                         if "pupil_isc" in resid else np.nan)
            rows.append(extra)
    df = pd.DataFrame(rows)
    pd.DataFrame(units).to_csv(args.out / f"temporal_units_w{int(args.window)}.csv", index=False)
    df.to_csv(args.out / f"temporal_structure_w{int(args.window)}.csv", index=False)
    feats = df[df.feature != "_pairs"].copy()
    tot = feats.var_person + feats.var_window + feats.var_resid
    for k in ("person", "window", "resid"):
        feats[f"share_{k}"] = feats[f"var_{k}"] / tot
    summary = {}
    for (s, f), g in feats.groupby(["set", "feature"]):
        w = g.n_cells / g.n_cells.sum()
        summary.setdefault(s, {})[f] = {
            "units": int(len(g)),
            "cells": int(g.n_cells.sum()),
            "share_person": round(float((g.share_person * w).sum()), 3),
            "share_window": round(float((g.share_window * w).sum()), 3),
            "share_resid": round(float((g.share_resid * w).sum()), 3),
            "resid_lag1_autocorr_median": round(float(g.lag1.median()), 3),
            "resid_lag3_autocorr_median": round(float(g.lag3.median()), 3),
            "resid_lag6_autocorr_median": round(float(g.lag6.median()), 3),
        }
    pairs = df[df.feature == "_pairs"]
    for s, g in pairs.groupby("set"):
        summary[s]["_pairs_median_over_units"] = {
            c: round(float(g[c].median()), 3) for c in
            ("xy_resid_corr", "valid_isc_resid_corr", "disp_isc_resid_corr", "pupil_gaze_isc_resid_corr")}
    meta = dict(window_s=args.window, outcome_access=False,
                inputs=[str(MANIFEST.relative_to(ROOT)), str(CACHE.relative_to(ROOT))],
                note="Variance shares of person x window matrices; residual = time-localized idiosyncratic component")
    (args.out / f"temporal_structure_w{int(args.window)}_summary.json").write_text(
        json.dumps(dict(meta=meta, summary=summary), indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
