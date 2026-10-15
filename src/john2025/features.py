"""Outcome-free ocular features of the time-stamped plan (external_analysis_plan_john2025.md).

Per person, on the instructional-video window [start_video_mine, stop_video_mine) of the EDF clock:

* valid sample: outside every EyeLink-parsed blink widened by +/-100 ms, gaze finite, and on the
  display (0 <= x < width, 0 <= y < height, from the EDF ``DISPLAY_COORDS`` message);
* Q-ext: invalid-sample fraction = 1 - valid / expected samples of the window (IJ-003);
* RF: gaze dispersion sqrt(var x + var y) of valid samples / display diagonal; saccade rate =
  EyeLink-parsed saccades whose onset sample is valid, per valid minute;
* 128 Hz video-locked series for synchrony: the mean of the valid 500 Hz samples in each
  1/128-s bin from video onset, NaN where a bin has none (IJ-004); pupil series is the
  within-recording z-scored pupil over valid samples (secondary block only).

The frozen protocol's missing rule applies: a feature with < 60 s of valid data is missing.
"""
from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

from .paths import DERIVED, EVIDENCE, PARSED, SERIES

BLINK_BUFFER_MS = 100.0
LONG_BLINK_MS = 500.0                   # amendment A2: longer parsed "blinks" are data loss
GRID_HZ = 128
MIN_VALID_S = 60.0


def blink_mask(t_ms: np.ndarray, blinks: np.ndarray, buffer_ms: float = BLINK_BUFFER_MS) -> np.ndarray:
    """True for samples inside any blink interval widened by ``buffer_ms`` on both sides."""
    m = np.zeros(len(t_ms), bool)
    for s, e in blinks:
        lo = np.searchsorted(t_ms, s - buffer_ms, side="left")
        hi = np.searchsorted(t_ms, e + buffer_ms, side="right")
        m[lo:hi] = True
    return m


def nearest_sample(t_ms: np.ndarray, times: np.ndarray, tol_ms: float) -> np.ndarray:
    """Index of the sample nearest to each time, or -1 when none lies within ``tol_ms``."""
    i = np.clip(np.searchsorted(t_ms, times), 1, len(t_ms) - 1)
    i = np.where(np.abs(t_ms[i - 1] - times) <= np.abs(t_ms[i] - times), i - 1, i)
    return np.where(np.abs(t_ms[i] - times) <= tol_ms, i, -1)


def bin_average(values: np.ndarray, valid: np.ndarray, bins: np.ndarray, n_bins: int) -> np.ndarray:
    """Mean of valid values per bin index (NaN for bins without a valid sample)."""
    s = np.bincount(bins[valid], values[valid], minlength=n_bins)[:n_bins]
    c = np.bincount(bins[valid], minlength=n_bins)[:n_bins]
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(c > 0, s / c, np.nan)


def person_features(pid: str) -> dict:
    z = np.load(PARSED / f"{pid}.npz")
    t, x, y, ps = z["time_ms"], z["xpos"], z["ypos"], z["ps"]
    d = z["display"]
    width, height = d[2] - d[0] + 1, d[3] - d[1] + 1
    diag = float(np.hypot(width, height))
    onset, offset = z["video"]
    if not (np.isfinite(onset) and np.isfinite(offset) and offset > onset):
        return dict(participant=pid, video_window_ok=False)
    dt = float(np.median(np.diff(t)))
    fs = 1000.0 / dt
    win = (t >= onset) & (t < offset)
    expected = int(round((offset - onset) / dt))
    blink = blink_mask(t, z["blinks"])
    finite = np.isfinite(x) & np.isfinite(y)
    with np.errstate(invalid="ignore"):
        on_display = finite & (x >= 0) & (x < width) & (y >= 0) & (y < height)
    valid = win & ~blink & on_display
    n_valid = int(valid.sum())
    valid_s = n_valid / fs
    row = dict(participant=pid, video_window_ok=True, fs=fs, display_width=width, display_height=height,
               display_diagonal=diag, video_window_s=(offset - onset) / 1000.0, expected_samples=expected,
               recorded_samples=int(win.sum()), valid_samples=n_valid, valid_seconds=valid_s)
    # Q-ext and its outcome-free decomposition (amendment A2): shares of the expected window samples.
    # EyeLink parses every pupil loss as a "blink"; intervals longer than LONG_BLINK_MS are read as
    # data loss (track loss / looking away), shorter ones as physiological blinks (IJ-010).
    dur = z["blinks"][:, 1] - z["blinks"][:, 0] if len(z["blinks"]) else np.zeros(0)
    long_loss = blink_mask(t, z["blinks"][dur > LONG_BLINK_MS])
    row["Q_invalid"] = 1.0 - n_valid / expected
    row["Qd_blink"] = float((win & blink & ~long_loss).sum()) / expected
    row["Qd_long_loss"] = float((win & long_loss).sum()) / expected
    row["Qd_offscreen"] = float((win & ~blink & finite & ~on_display).sum()) / expected
    row["Qd_lost"] = (float((win & ~blink & ~finite).sum()) + max(expected - int(win.sum()), 0)) / expected
    row["n_blinks_window"] = int(((z["blinks"][:, 0] >= onset) & (z["blinks"][:, 0] < offset)).sum()) if len(dur) else 0
    row["n_long_loss_window"] = int(((z["blinks"][:, 0] >= onset) & (z["blinks"][:, 0] < offset) & (dur > LONG_BLINK_MS)).sum()) if len(dur) else 0
    # RF5 gaze dispersion and RF6 saccade rate.
    if valid_s >= MIN_VALID_S:
        row["RF5_gaze_dispersion"] = float(np.sqrt(x[valid].var() + y[valid].var()) / diag)
        on = z["saccades"][:, 0]
        on = on[(on >= onset) & (on < offset)]
        idx = nearest_sample(t, on, dt / 2)
        hit = (idx >= 0) & valid[np.maximum(idx, 0)]
        row["RF6_saccade_rate"] = float(hit.sum() / (valid_s / 60.0))
        row["n_saccades_valid_onset"] = int(hit.sum())
        row["n_saccades_window"] = int(len(on))
    else:
        row["RF5_gaze_dispersion"] = row["RF6_saccade_rate"] = np.nan
    # 128 Hz video-locked series.
    n_bins = int(np.floor((offset - onset) / 1000.0 * GRID_HZ))
    bins = np.floor((t - onset) / 1000.0 * GRID_HZ).astype(np.int64)
    inb = valid & (bins >= 0) & (bins < n_bins)
    gaze = np.column_stack([bin_average(x, inb, np.where(inb, bins, 0), n_bins),
                            bin_average(y, inb, np.where(inb, bins, 0), n_bins)]).astype(np.float32)
    with np.errstate(invalid="ignore"):
        pv = inb & np.isfinite(ps) & (ps > 0)
    if pv.sum() >= 2:
        pz = (ps - ps[pv].mean()) / ps[pv].std()
        pupil = bin_average(pz, pv, np.where(pv, bins, 0), n_bins).astype(np.float32)[:, None]
    else:
        pupil = np.full((n_bins, 1), np.nan, np.float32)
    row["pupil_valid_seconds"] = float(pv.sum() / fs)
    row["grid_bins"] = n_bins
    row["grid_valid_bins_gaze"] = int(np.isfinite(gaze[:, 0]).sum())
    SERIES.mkdir(parents=True, exist_ok=True)
    np.save(SERIES / f"{pid}_gaze.npy", gaze)
    np.save(SERIES / f"{pid}_pupil.npy", pupil)
    return row


def extract_all(workers: int = 4) -> pd.DataFrame:
    pids = sorted(p.stem for p in PARSED.glob("*.npz"))
    with ProcessPoolExecutor(workers) as ex:
        rows = list(ex.map(person_features, pids))
    table = pd.DataFrame(rows).sort_values("participant").reset_index(drop=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    table.to_parquet(DERIVED / "person_features.parquet", index=False)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    table.to_csv(EVIDENCE / "person_features.csv", index=False, float_format="%.8g")
    (EVIDENCE / "feature_definitions.json").write_text(json.dumps(dict(
        blink_buffer_ms=BLINK_BUFFER_MS, long_blink_ms=LONG_BLINK_MS, grid_hz=GRID_HZ, min_valid_seconds=MIN_VALID_S,
        window="[start_video_mine, stop_video_mine) on the EDF clock", eye="as recorded (right)"), indent=1) + "\n")
    return table
