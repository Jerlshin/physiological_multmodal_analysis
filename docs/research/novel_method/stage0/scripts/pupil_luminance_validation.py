"""Stage 0a validation - pupillary light response under each candidate timeline (outcome-free).

Independent of both alignment signals (gaze position, cut-locked saccades): the peer-mean
pupil size (z-scored per recording) follows the negative of the screen's mean luminance with a
sub-second to ~1.5 s lag. For each video, candidate mapping (final G-TL mapping and every signal
configuration's pooled path) and region (whole recording; each final segment; disputed regions),
the luminance of the public source is mapped onto the recording clock and correlated with the
pupil course after removing slow drifts (10 s moving-average high-pass). The lag is chosen in
[0.2, 1.5] s. The null distribution re-places the mapped luminance at random circular shifts
of >= 20 s (1,000 draws, lag also maximized) - an honest null for the lag search.

Usage (repo root): PYTHONPATH=src python docs/research/novel_method/stage0/scripts/pupil_luminance_validation.py
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import cairn.timeline as tl
from cairn.paths import BIN_HZ, DERIVED, SOURCES, STAGE0_EVIDENCE, VIDEOS

SEED = 11
N_NULL = 1000
LAGS = np.arange(2, 16)          # 0.2-1.5 s


def highpass(x: np.ndarray, win_s: float = 10.0) -> np.ndarray:
    s = pd.Series(x).interpolate(limit_direction="both")
    return (s - s.rolling(int(win_s * BIN_HZ), center=True, min_periods=1).mean()).to_numpy()


def mapped_luminance(lum: dict, mapping: pd.DataFrame, n_bins: int) -> np.ndarray:
    k = np.arange(n_bins)
    sec = np.minimum(k // BIN_HZ, len(mapping) - 1)
    src = mapping.source.to_numpy()[sec]
    off = mapping.offset_s.to_numpy()[sec]
    out = np.full(n_bins, np.nan)
    for s, L in lum.items():
        m = src == s
        vk = np.round(k[m] + off[m] * BIN_HZ).astype(int)
        ok = (vk >= 0) & (vk < len(L))
        idx = np.flatnonzero(m)[ok]
        out[idx] = L[vk[ok]]
    return out


def best_r(p: np.ndarray, L: np.ndarray, lo: int, hi: int) -> tuple[float, float]:
    best, lag_s = -np.inf, np.nan
    for lag in LAGS:
        a = p[lo + lag: hi]
        b = -L[lo: hi - lag]
        m = np.isfinite(a) & np.isfinite(b)
        if m.sum() < 50 or a[m].std() == 0 or b[m].std() == 0:
            continue
        r = np.corrcoef(a[m], b[m])[0, 1]
        if r > best:
            best, lag_s = r, lag / BIN_HZ
    return (best if np.isfinite(best) else np.nan), lag_s


def main():
    rng = np.random.default_rng(SEED)
    m = pd.read_parquet(DERIVED / "series10_manifest.parquet")
    m = m[m.status == "ok"]
    mp = pd.read_csv(STAGE0_EVIDENCE / "timeline_map_1hz.csv")
    rows = []
    for vid, name in VIDEOS.items():
        mv = m[m.canonical_video_id == vid]
        n_bins = int(mv.n_bins.min())
        p = highpass(tl.peer_courses(mv, list(mv.uid)).pupil.to_numpy()[:n_bins])
        lum = {s: tl.video_features(s).lum.to_numpy() for s in SOURCES[vid]}
        d = mp[mp.video == name].reset_index(drop=True)
        cands = {"final": d[["rec_s", "source", "offset_s"]]}
        for c in ("combined", "spatial", "temporal"):
            cands[c] = d[["rec_s", f"source_{c}", f"offset_{c}"]].rename(columns={f"source_{c}": "source", f"offset_{c}": "offset_s"})
        # regions: whole recording plus 60 s blocks (to localize disagreements)
        regions = [("all", 0, n_bins)] + [(f"{a}-{min(a + 60, n_bins // BIN_HZ)}s", a * BIN_HZ, min((a + 60) * BIN_HZ, n_bins))
                                          for a in range(0, n_bins // BIN_HZ, 60) if min((a + 60) * BIN_HZ, n_bins) - a * BIN_HZ >= 30 * BIN_HZ]
        for cname, mapping in cands.items():
            Lr = highpass(mapped_luminance(lum, mapping, n_bins))
            for rname, lo, hi in regions:
                r, lag = best_r(p, Lr, lo, hi)
                null = []
                for _ in range(N_NULL if rname == "all" else 200):
                    sh = rng.integers(20 * BIN_HZ, n_bins - 20 * BIN_HZ)
                    null.append(best_r(p, np.roll(Lr, sh), lo, hi)[0])
                null = np.array(null)
                pval = float((np.sum(null >= r) + 1) / (np.sum(np.isfinite(null)) + 1)) if np.isfinite(r) else np.nan
                rows.append(dict(video=name, mapping=cname, region=rname, r=r, lag_s=lag, null_q95=float(np.nanquantile(null, 0.95)), p_null=pval))
        print(name, [(x["mapping"], round(x["r"], 3), x["lag_s"], round(x["p_null"], 4)) for x in rows if x["video"] == name and x["region"] == "all"], flush=True)
    pd.DataFrame(rows).to_csv(STAGE0_EVIDENCE / "timeline_pupil_luminance_validation.csv", index=False, float_format="%.4f")


if __name__ == "__main__":
    sys.exit(main())
