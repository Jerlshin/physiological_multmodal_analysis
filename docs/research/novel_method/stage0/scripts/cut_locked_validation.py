"""Stage 0a validation - cut-locked peer saccade response under each candidate timeline (outcome-free).

Independent of the windowed alignment scores: if a timeline is right, the peer saccade-onset
rate (z-scored per recording, averaged over every released viewing) rises sharply 0.1-0.6 s
after each hard cut of the public video, mapped onto the recording clock by that timeline.
A wrong timeline smears the response. For each video and candidate mapping (the final
G-TL mapping and every signal configuration's pooled path), the script reports the
post-cut response (mean z over [0.1, 0.6] s minus mean over [-1.5, -0.2] s) and its
permutation p-value against cuts placed at random recording times (2,000 draws).

Usage (repo root): PYTHONPATH=src python docs/research/novel_method/stage0/scripts/cut_locked_validation.py
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

import cairn.timeline as tl
from cairn.paths import BIN_HZ, DERIVED, SOURCES, STAGE0_EVIDENCE, VIDEOS

SEED = 7
N_PERM = 2000
POST = (1, 6)        # bins 0.1-0.6 s after the cut
PRE = (-15, -2)      # bins -1.5 to -0.2 s


def frame_cuts(src: str) -> np.ndarray:
    """Hard-cut times (s) on the source clock at frame resolution."""
    frames, fps = tl.decode_gray(tl.YOUTUBE / src / f"{src}.mp4")
    mag = np.abs(np.diff(frames.astype(np.float32), axis=0)).mean(axis=(1, 2))
    med = pd.Series(mag).rolling(int(round(fps)), center=True, min_periods=1).median().to_numpy()
    cut = np.flatnonzero(mag > np.maximum(4 * med, 20.0))
    # merge consecutive frames of one transition
    keep = cut[np.r_[True, np.diff(cut) > 2]]
    return (keep + 1) / fps


def map_to_recording(cuts: dict, mapping: pd.DataFrame) -> np.ndarray:
    """Recording times of source cuts under a per-second mapping (rec_s, source, offset_s)."""
    out = []
    for r in mapping.itertuples():
        for t in cuts.get(r.source, []):
            v0 = r.rec_s + r.offset_s
            if v0 <= t < v0 + 1:
                out.append(t - r.offset_s)
    return np.array(sorted(out))


def response(sacc: np.ndarray, times: np.ndarray) -> float:
    k = np.round(times * BIN_HZ).astype(int)
    k = k[(k + PRE[0] >= 0) & (k + POST[1] < len(sacc))]
    if len(k) < 3:
        return np.nan
    post = np.nanmean([sacc[i + POST[0]: i + POST[1]].mean() for i in k])
    pre = np.nanmean([sacc[i + PRE[0]: i + PRE[1]].mean() for i in k])
    return float(post - pre)


def main():
    rng = np.random.default_rng(SEED)
    m = pd.read_parquet(DERIVED / "series10_manifest.parquet")
    m = m[m.status == "ok"]
    mp = pd.read_csv(STAGE0_EVIDENCE / "timeline_map_1hz.csv")
    rows = []
    for vid, name in VIDEOS.items():
        mv = m[m.canonical_video_id == vid]
        n_bins = int(mv.n_bins.min())
        sacc = tl.peer_courses(mv, list(mv.uid)).sacc.to_numpy()[:n_bins]
        cuts = {s: frame_cuts(s) for s in SOURCES[vid]}
        d = mp[mp.video == name]
        cands = {"final": d[["rec_s", "source", "offset_s"]]}
        for c in ("combined", "spatial", "temporal"):
            cands[c] = d[["rec_s", f"source_{c}", f"offset_{c}"]].rename(columns={f"source_{c}": "source", f"offset_{c}": "offset_s"})
        for cname, mapping in cands.items():
            t = map_to_recording(cuts, mapping)
            obs = response(sacc, t)
            null = np.array([response(sacc, np.sort(rng.uniform(2, n_bins / BIN_HZ - 2, len(t)))) for _ in range(N_PERM)]) if len(t) >= 3 else np.array([np.nan])
            p = float((np.sum(null >= obs) + 1) / (np.sum(np.isfinite(null)) + 1)) if np.isfinite(obs) else np.nan
            rows.append(dict(video=name, mapping=cname, n_cuts=len(t), response_z=obs,
                             null_mean=float(np.nanmean(null)), null_sd=float(np.nanstd(null)), p_perm=p))
        print(name, [(r["mapping"], r["n_cuts"], round(r["response_z"], 3) if np.isfinite(r["response_z"]) else None, r["p_perm"]) for r in rows if r["video"] == name], flush=True)
    pd.DataFrame(rows).to_csv(STAGE0_EVIDENCE / "timeline_cut_locked_validation.csv", index=False, float_format="%.4f")


if __name__ == "__main__":
    sys.exit(main())
