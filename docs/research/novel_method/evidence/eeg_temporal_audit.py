"""Outcome-free audit of time-localized EEG structure and its coupling with ocular structure.

Companion to temporal_structure_audit.py, same inputs and rules: the frozen analysis-set
manifest (keys and set flags only), the outcome-free exposure feature table (EEG channel
labels only) and the G01-R 128 Hz cache. No quiz outcome is opened.

Per window (default 10 s) and learner it computes:

* ``alpha``   - log10 relative posterior alpha (8-12 Hz over 1-40 Hz, 14.5-17.5 Hz excluded),
                median over the frozen RF1 channels, from 2-s Hann segments without invalid samples;
* ``eeg_isc`` - mean over the 64 channels of Pearson r with the leave-one-out mean of the
                unit's other viewers (a descriptive, filter-free proxy for EEG ISC);
* ``gaze_valid`` and ``gaze_isc`` - as in temporal_structure_audit.py, for coupling.

It reports the same person / window / residual variance shares, and correlations between
EEG and gaze residuals (is time-localized EEG structure ocular?).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from temporal_structure_audit import CACHE, FS, MANIFEST, ROOT, loo_reference, pair_corr, two_way, uid, wcorr

FEATURES = ROOT / "data/derived/g01r/features/processed/exposure_features.parquet"
ALPHA_CH = ["P3", "Pz", "P4", "PO3", "POz", "PO4", "O1", "Oz", "O2"]


def rel_alpha(seg: np.ndarray, valid: np.ndarray, idx: list) -> float:
    L = 2 * FS
    freqs = np.fft.rfftfreq(L, 1 / FS)
    win = np.hanning(L)
    num = (freqs >= 8) & (freqs <= 12)
    den = (freqs >= 1) & (freqs <= 40) & ~((freqs >= 14.5) & (freqs <= 17.5))
    ps = []
    for s in range(0, len(seg) - L + 1, L // 2):
        if not valid[s:s + L].all():
            continue
        X = seg[s:s + L][:, idx] * win[:, None]
        ps.append(np.abs(np.fft.rfft(X, axis=0)) ** 2)
    if len(ps) < 2:
        return np.nan
    P = np.mean(ps, axis=0)
    return float(np.median(np.log10(P[num].sum(0) / P[den].sum(0))))


def unit(cells: pd.DataFrame, labels: dict, win_s: float):
    L = int(win_s * FS)
    eeg, ev, gz = {}, {}, {}
    for r in cells.itertuples(index=False):
        u = uid(r)
        p_e, p_v, p_g = CACHE / "eeg" / f"{u}.npy", CACHE / "eeg" / f"{u}_valid.npy", CACHE / "gaze" / f"{u}.npy"
        if p_e.exists() and p_v.exists() and p_g.exists() and u in labels:
            eeg[u], ev[u], gz[u] = np.load(p_e, mmap_mode="r"), np.load(p_v), np.load(p_g)
    us = sorted(eeg)
    if len(us) < 5:
        return None
    T = min(min(len(eeg[u]), len(gz[u])) for u in us)
    nw = T // L
    lab = labels[us[0]]
    idx = [lab.index(c) for c in ALPHA_CH if c in lab]
    E = np.stack([np.where(ev[u][: nw * L, None], eeg[u][: nw * L], np.nan) for u in us]).astype(np.float32)
    G = np.stack([gz[u][: nw * L] for u in us]).astype(np.float64)
    refE = loo_reference(E)
    refx, refy = loo_reference(G[..., 0]), loo_reference(G[..., 1])
    P = len(us)
    out = {k: np.full((P, nw), np.nan) for k in ("alpha", "eeg_isc", "gaze_valid", "gaze_isc")}
    minv = int(0.3 * L)
    for i, u in enumerate(us):
        for w in range(nw):
            s = slice(w * L, (w + 1) * L)
            vmask = ev[u][s]
            out["alpha"][i, w] = rel_alpha(np.asarray(eeg[u][s]), vmask, idx)
            if vmask.sum() >= minv:
                rs = [wcorr(E[i, s, c], refE[i, s, c], minv) for c in range(E.shape[2])]
                out["eeg_isc"][i, w] = np.nanmean(rs)
            gx, gy = G[i, s, 0], G[i, s, 1]
            out["gaze_valid"][i, w] = (~np.isnan(gx)).mean()
            if (~np.isnan(gx)).sum() >= minv:
                out["gaze_isc"][i, w] = np.nanmean([wcorr(gx, refx[i, s], minv), wcorr(gy, refy[i, s], minv)])
    return P, nw, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=float, default=10.0)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    args = ap.parse_args()
    m = pd.read_csv(MANIFEST)
    f = pd.read_parquet(FEATURES)
    f["uid"] = [uid(r) for r in f.itertuples(index=False)]
    labels = {r.uid: json.loads(r.eeg_labels) for r in f.itertuples(index=False)
              if isinstance(r.eeg_labels, str)}
    rows = []
    for s in ("PAS_E34_core", "E5_core"):
        for (exp, vid), cells in m[m[s]].groupby(["experiment", "canonical_video_id"]):
            res = unit(cells, labels, args.window)
            if res is None:
                continue
            P, nw, F = res
            resid = {}
            for k, M in F.items():
                shares, e = two_way(M)
                resid[k] = e
                rows.append(dict(set=s, experiment=int(exp), video=vid, feature=k, people=P, windows=nw, **shares))
            rows.append(dict(set=s, experiment=int(exp), video=vid, feature="_pairs", people=P, windows=nw,
                             eegisc_gazeisc=pair_corr(resid["eeg_isc"], resid["gaze_isc"]),
                             eegisc_gazevalid=pair_corr(resid["eeg_isc"], resid["gaze_valid"]),
                             alpha_gazevalid=pair_corr(resid["alpha"], resid["gaze_valid"]),
                             alpha_gazeisc=pair_corr(resid["alpha"], resid["gaze_isc"])))
            print(s, exp, vid, P, nw, flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(args.out / f"eeg_temporal_w{int(args.window)}.csv", index=False)
    feats = df[df.feature != "_pairs"].copy()
    tot = feats.var_person + feats.var_window + feats.var_resid
    summary = {}
    for (s, k), g in feats.groupby(["set", "feature"]):
        w = g.n_cells / g.n_cells.sum()
        summary.setdefault(s, {})[k] = {c: round(float(((g[f"var_{c}"] / tot[g.index]) * w).sum()), 3)
                                       for c in ("person", "window", "resid")}
    for s, g in df[df.feature == "_pairs"].groupby("set"):
        summary[s]["_pairs_median_over_units"] = {c: round(float(g[c].median()), 3) for c in
                                                 ("eegisc_gazeisc", "eegisc_gazevalid", "alpha_gazevalid", "alpha_gazeisc")}
    (args.out / f"eeg_temporal_w{int(args.window)}_summary.json").write_text(
        json.dumps(dict(meta=dict(window_s=args.window, outcome_access=False), summary=summary), indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
