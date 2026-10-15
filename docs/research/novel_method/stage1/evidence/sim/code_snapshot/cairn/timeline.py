"""Stage 0a: recover the stimulus timeline (recording clock -> public video clock), outcome-free.

Two independent alignment signals per video, both at 10 Hz:

* **temporal** - frame-to-frame visual change magnitude of the public video versus the
  peer-mean saccade-onset rate (z-scored per recording): viewers re-orient after cuts and
  transitions;
* **spatial**  - the screen location of visual change (intensity-weighted centroid of the
  frame difference, i.e. where new ink/motion appears) versus the peer-median gaze position.

For a recording-clock window [t0, t0 + W) and a candidate offset o (video time = recording
time + o), the score is the mean of the Pearson correlations of the available signals.
Sliding windows give a piecewise offset profile, so internal edits appear as steps.

Inputs: the public videos (data/stimuli, git-ignored) and the 10 Hz series from
:mod:`cairn.extract`. No quiz outcome is read.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .extract import CHANNELS
from .paths import BIN_HZ, DERIVED, SERIES, YOUTUBE

VIDEO_CACHE = DERIVED / "video10"
W_PIX, H_PIX = 96, 54


# ----------------------------------------------------------------------------- video side
def decode_gray(path: Path, w: int = W_PIX, h: int = H_PIX) -> tuple[np.ndarray, float]:
    """All frames of a video as uint8 grayscale (frames x h x w) and the frame rate."""
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                            "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout.strip()
    num, den = probe.split("/")
    fps = float(num) / float(den)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"scale={w}:{h},format=gray",
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, h, w)
    return frames, fps


def video_features(video_id: str) -> pd.DataFrame:
    """10 Hz visual-change features on the public video's own clock (cached)."""
    VIDEO_CACHE.mkdir(parents=True, exist_ok=True)
    cache = VIDEO_CACHE / f"{video_id}.parquet"
    if cache.exists():
        return pd.read_parquet(cache)
    frames, fps = decode_gray(YOUTUBE / video_id / f"{video_id}.mp4")
    f = frames.astype(np.float32)
    d = np.abs(np.diff(f, axis=0))                              # frame i+1 minus frame i
    mag = d.mean(axis=(1, 2))
    t = (np.arange(1, len(frames)) / fps)                        # time of the later frame
    # change-location centroid in normalized screen coordinates [0, 1]
    thr = d > 12.0                                               # ignore compression noise
    wsum = (d * thr).sum(axis=(1, 2))
    xs = (np.arange(W_PIX) + 0.5) / W_PIX
    ys = (np.arange(H_PIX) + 0.5) / H_PIX
    with np.errstate(invalid="ignore", divide="ignore"):
        cx = np.where(wsum > 0, (d * thr).sum(axis=1) @ xs / wsum, np.nan)
        cy = np.where(wsum > 0, (d * thr).sum(axis=2) @ ys / wsum, np.nan)
    # hard cuts: change far above the local median
    med = pd.Series(mag).rolling(int(round(fps)), center=True, min_periods=1).median().to_numpy()
    cut = (mag > np.maximum(4 * med, 20.0))
    lum = f[1:].mean(axis=(1, 2))                                # mean luminance (pupillary light response)
    k = np.floor(t * BIN_HZ).astype(int)
    n = int(np.floor(len(frames) / fps * BIN_HZ))
    keep = k < n
    df = pd.DataFrame(dict(k=k[keep], mag=mag[keep], cx=cx[keep], cy=cy[keep], w=wsum[keep], cut=cut[keep], lum=lum[keep]))
    g = df.groupby("k")
    out = pd.DataFrame(index=pd.RangeIndex(n, name="k"))
    out["mag"] = g.mag.max()
    out["cut"] = g.cut.max().astype(float)
    out["lum"] = g.lum.mean()
    wcx = (df.cx * df.w).groupby(df.k).sum()
    wcy = (df.cy * df.w).groupby(df.k).sum()
    ww = df.w.groupby(df.k).sum()
    out["cx"] = (wcx / ww).where(ww > 0)
    out["cy"] = (wcy / ww).where(ww > 0)
    out["t"] = out.index / BIN_HZ
    out.attrs["fps"] = fps
    out.reset_index().to_parquet(cache, index=False)
    return out.reset_index()


# ----------------------------------------------------------------------------- gaze side
def peer_courses(manifest: pd.DataFrame, uids: list[str]) -> pd.DataFrame:
    """Peer summary courses at 10 Hz on the recording clock for one set of viewings."""
    arrs = [np.load(SERIES / f"{u}.npy") for u in uids]
    n = int(np.median([a.shape[1] for a in arrs]))
    ix = {c: i for i, c in enumerate(CHANNELS)}

    def stack(c):
        s = np.full((len(arrs), n), np.nan)
        for j, a in enumerate(arrs):
            m = min(n, a.shape[1])
            s[j, :m] = a[ix[c], :m]
        return s

    gx, gy, sacc, valid, pupil = stack("gx"), stack("gy"), stack("sacc"), stack("valid"), stack("pupil")
    with np.errstate(invalid="ignore"):
        sz = (sacc - np.nanmean(sacc, 1, keepdims=True)) / np.nanstd(sacc, 1, keepdims=True)
        pz = (pupil - np.nanmean(pupil, 1, keepdims=True)) / np.nanstd(pupil, 1, keepdims=True)
    out = pd.DataFrame(dict(
        gx=np.nanmedian(gx, 0) / 1920.0, gy=np.nanmedian(gy, 0) / 1080.0,
        sacc=np.nanmean(sz, 0), pupil=np.nanmean(pz, 0), n_valid=np.sum(np.isfinite(gx), 0), valid=np.nanmean(valid, 0)))
    out.loc[out.n_valid < max(3, 0.3 * len(arrs)), ["gx", "gy"]] = np.nan
    out["t"] = np.arange(n) / BIN_HZ
    return out


# ----------------------------------------------------------------------------- alignment
def _corr_all_lags(a: np.ndarray, b: np.ndarray, lags: np.ndarray) -> np.ndarray:
    """Pearson r between a (window, fixed) and b shifted by each lag (b index = a index + lag)."""
    r = np.full(len(lags), np.nan)
    n = len(a)
    ok = (lags >= 0) & (lags + n <= len(b))
    if not ok.any() or len(b) < n:
        return r
    B = np.lib.stride_tricks.sliding_window_view(b, n)[lags[ok]]          # lags x n
    m = np.isfinite(B) & np.isfinite(a)[None, :]
    cnt = m.sum(1)
    A = np.where(m, a[None, :], 0.0)
    Bz = np.where(m, B, 0.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        ma, mb = A.sum(1) / cnt, Bz.sum(1) / cnt
        cov = (A * Bz).sum(1) / cnt - ma * mb
        va = (A * A).sum(1) / cnt - ma ** 2
        vb = (Bz * Bz).sum(1) / cnt - mb ** 2
        rr = cov / np.sqrt(va * vb)
    rr[(cnt < max(20, 0.3 * n)) | ~(va > 1e-12) | ~(vb > 1e-12)] = np.nan
    r[ok] = rr
    return r


@dataclass
class WindowFit:
    t0: float
    best_offset: float
    score: float
    peak_z: float
    second_gap_s: float
    r_temporal: float
    r_spatial: float


def score_curve(peer: pd.DataFrame, vid: pd.DataFrame, k0: int, k1: int, lags: np.ndarray,
                latency_bins: int = 0, use=("sacc", "spatial")) -> tuple[np.ndarray, dict]:
    """Mean alignment score over offsets for recording bins [k0, k1)."""
    parts = {}
    if "sacc" in use:
        # hard cuts smoothed over the typical 0-0.6 s re-orienting response
        cut = np.convolve(vid.cut.fillna(0).to_numpy(), np.ones(6) / 6, mode="full")[: len(vid)]
        parts["temporal"] = _corr_all_lags(peer.sacc.to_numpy()[k0:k1], cut, lags + k0 - latency_bins)
    if "spatial" in use:
        rx = _corr_all_lags(peer.gx.to_numpy()[k0:k1], vid.cx.ffill().to_numpy(), lags + k0 - latency_bins)
        ry = _corr_all_lags(peer.gy.to_numpy()[k0:k1], vid.cy.ffill().to_numpy(), lags + k0 - latency_bins)
        parts["spatial"] = np.nanmean(np.vstack([rx, ry]), 0)
    stack = np.vstack(list(parts.values()))
    with np.errstate(invalid="ignore"):
        score = np.nanmean(stack, 0)
    return score, parts


def score_matrix(peer: pd.DataFrame, vids: dict, win_s: float = 30.0, step_s: float = 5.0):
    """Windowed alignment scores for every (source, offset): returns window starts, the state
    list [(source, offset_bins)] and scores (windows x states).

    Offsets span [-recording length, source length], so any excerpt of any source can be
    placed anywhere on the recording clock.
    """
    n = len(peer)
    starts = np.arange(0, max(1, n - int(win_s * BIN_HZ)) + 1, int(step_s * BIN_HZ))
    states, blocks = [], []
    for src, vid in vids.items():
        lags = np.arange(-n, len(vid) + 1)
        S = np.vstack([score_curve(peer, vid, k0, k0 + int(win_s * BIN_HZ), lags)[0] for k0 in starts])
        states += [(src, int(L)) for L in lags]
        blocks.append(S)
    return starts, states, np.hstack(blocks)


def viterbi_offsets(S: np.ndarray, states: list, jump_cost: float = 0.25, drift_bins: int = 2) -> np.ndarray:
    """Piecewise-constant alignment path through a (windows x states) score matrix.

    Staying on the same source and offset (+/- ``drift_bins``) is free; any other change
    (an edit point) costs ``jump_cost`` in correlation units. NaN scores count as 0.
    Returns the state index per window.
    """
    W, K = S.shape
    s = np.nan_to_num(S, nan=0.0)
    src = np.array([st[0] for st in states])
    acc = s[0].copy()
    back = np.zeros((W, K), dtype=np.int64)
    for w in range(1, W):
        # best "stay" predecessor within the drift tolerance on the same source
        stay = acc.copy()
        stay_idx = np.arange(K)
        for d in range(1, drift_bins + 1):
            for sh in (d, -d):
                cand = np.roll(acc, sh)
                idx = np.roll(np.arange(K), sh)
                same = src[idx] == src
                better = same & (cand > stay)
                stay = np.where(better, cand, stay)
                stay_idx = np.where(better, idx, stay_idx)
        j = int(np.argmax(acc))
        jump = acc[j] - jump_cost
        use_jump = jump > stay
        back[w] = np.where(use_jump, j, stay_idx)
        acc = np.where(use_jump, jump, stay) + s[w]
    path = np.zeros(W, dtype=np.int64)
    path[-1] = int(np.argmax(acc))
    for w in range(W - 1, 0, -1):
        path[w - 1] = back[w, path[w]]
    return path


def monotone_viterbi(S: np.ndarray, states: list, source_order: list, jump_cost: float = 0.25,
                     drift_bins: int = 2) -> tuple[np.ndarray, float]:
    """Alignment path under the physical editing constraint: a stimulus made by cutting sources
    only removes material, so within a source the offset never decreases (beyond ``drift_bins``)
    and sources appear in ``source_order`` without returning. Each removal or source switch
    costs ``jump_cost``. Returns (state index per window, total path score)."""
    W, K = S.shape
    s = np.nan_to_num(S, nan=0.0)
    blocks = []
    for src in source_order:
        idx = np.array([i for i, st in enumerate(states) if st[0] == src])
        idx = idx[np.argsort([states[i][1] for i in idx])]
        blocks.append(idx)
    acc = np.full(K, -np.inf)
    acc[blocks[0]] = s[0, blocks[0]]
    if len(blocks) > 1:                       # a stimulus may start inside a later source only if earlier ones are absent
        for b in blocks[1:]:
            acc[b] = s[0, b] - jump_cost
    back = np.zeros((W, K), dtype=np.int64)
    for w in range(1, W):
        new = np.full(K, -np.inf)
        prev_best_val, prev_best_idx = -np.inf, -1
        for bi, idx in enumerate(blocks):
            a = acc[idx]
            n = len(idx)
            # stay within +/- drift
            stay_val = a.copy()
            stay_arg = np.arange(n)
            for d in range(1, drift_bins + 1):
                for sh in (d, -d):
                    cand = np.full(n, -np.inf)
                    if sh > 0:
                        cand[sh:] = a[:-sh]
                    else:
                        cand[:sh] = a[-sh:]
                    better = cand > stay_val
                    stay_val = np.where(better, cand, stay_val)
                    stay_arg = np.where(better, np.arange(n) - sh, stay_arg)
            # forward jump (removal): best predecessor with offset < current - drift
            cm = np.maximum.accumulate(a)
            cm_arg = np.zeros(n, dtype=np.int64)
            run = 0
            for i in range(n):
                if a[i] >= a[run]:
                    run = i
                cm_arg[i] = run
            jump_val = np.full(n, -np.inf)
            jump_arg = np.zeros(n, dtype=np.int64)
            sh = drift_bins + 1
            jump_val[sh:] = cm[:-sh] - jump_cost
            jump_arg[sh:] = cm_arg[:-sh]
            best_val = np.where(jump_val > stay_val, jump_val, stay_val)
            best_arg = idx[np.where(jump_val > stay_val, jump_arg, stay_arg)]
            # source switch from any earlier source
            if bi > 0 and prev_best_val - jump_cost > -np.inf:
                sw = prev_best_val - jump_cost
                use = sw > best_val
                best_val = np.where(use, sw, best_val)
                best_arg = np.where(use, prev_best_idx, best_arg)
            new[idx] = best_val + s[w, idx]
            back[w, idx] = best_arg
            j = int(np.argmax(a))
            if a[j] > prev_best_val:
                prev_best_val, prev_best_idx = a[j], idx[j]
        acc = new
    path = np.zeros(W, dtype=np.int64)
    path[-1] = int(np.argmax(acc))
    total = float(acc[path[-1]])
    for w in range(W - 1, 0, -1):
        path[w - 1] = back[w, path[w]]
    return path, total


def constant_path(S: np.ndarray, states: list) -> tuple[np.ndarray, float]:
    """Best single (source, offset) for the whole recording (no edit)."""
    tot = np.nan_to_num(S, nan=0.0).sum(0)
    k = int(np.argmax(tot))
    return np.full(S.shape[0], k), float(tot[k])


def fit_window(peer, vid, t0, win_s, lags, latency_bins=0) -> WindowFit:
    k0, k1 = int(t0 * BIN_HZ), int((t0 + win_s) * BIN_HZ)
    score, parts = score_curve(peer, vid, k0, k1, lags, latency_bins)
    if np.all(np.isnan(score)):
        return WindowFit(t0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan)
    i = int(np.nanargmax(score))
    s = score[np.isfinite(score)]
    z = (score[i] - np.median(s)) / (1.4826 * np.median(np.abs(s - np.median(s))) + 1e-9)
    far = np.abs(lags - lags[i]) > 2 * BIN_HZ                     # best competing peak > 2 s away
    second = np.nanmax(np.where(far, score, np.nan)) if far.any() else np.nan
    return WindowFit(t0, lags[i] / BIN_HZ, float(score[i]), float(z), float(score[i] - second),
                     float(parts.get("temporal", [np.nan] * len(lags))[i]), float(parts.get("spatial", [np.nan] * len(lags))[i]))
