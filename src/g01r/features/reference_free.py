"""Reference-free whole-video features RF1-RF6 and RF-P (protocol §6), as pure array functions.

Every function returns ``(value, valid_seconds)``. The caller applies the frozen
missing-data rule (value set missing when ``valid_seconds`` < 60 s).
"""
from __future__ import annotations

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.signal import get_window


# ----------------------------------------------------------------------------- EEG
def masked_welch(x: np.ndarray, invalid: np.ndarray, fs: float, window_s: float, overlap: float):
    """Welch PSD per channel over fixed-grid Hann windows that contain no invalid sample (IS-004).

    x, invalid: samples x channels. Returns (freqs, psd [freq x channel], covered_samples [channel]).
    Windows start at 0 and advance by window*(1-overlap); a window is used for a channel only if
    none of its samples is invalid in that channel. Scaling matches scipy.signal.welch(density).
    """
    nper = int(round(window_s * fs))
    step = int(round(nper * (1 - overlap)))
    T, C = x.shape
    freqs = np.fft.rfftfreq(nper, 1 / fs)
    if T < nper:
        return freqs, np.full((len(freqs), C), np.nan), np.zeros(C, int)
    starts = np.arange(0, T - nper + 1, step)
    win = get_window("hann", nper)
    scale = 1.0 / (fs * (win ** 2).sum())
    seg = sliding_window_view(x, nper, axis=0)[starts]            # nwin x C x nper
    bad = sliding_window_view(invalid, nper, axis=0)[starts].any(axis=2)   # nwin x C
    seg = seg - seg.mean(axis=2, keepdims=True)
    spec = np.abs(np.fft.rfft(seg * win, axis=2)) ** 2 * scale     # nwin x C x nfreq
    if nper % 2 == 0:
        spec[..., 1:-1] *= 2
    else:
        spec[..., 1:] *= 2
    use = ~bad
    n_used = use.sum(axis=0)                                       # C
    psd = np.einsum("wcf,wc->fc", spec, use.astype(float))
    with np.errstate(invalid="ignore", divide="ignore"):
        psd = psd / n_used[None, :]
    covered = np.zeros(C, int)
    for c in range(C):
        m = np.zeros(T, bool)
        for s in starts[use[:, c]]:
            m[s:s + nper] = True
        covered[c] = int(m.sum())
    psd[:, n_used == 0] = np.nan
    return freqs, psd, covered


def band_power(freqs, psd, lo, hi, exclude=None):
    """Sum of PSD bins with lo <= f <= hi (closed band), optionally excluding [a, b], times the bin width."""
    sel = (freqs >= lo) & (freqs <= hi)
    if exclude is not None:
        sel &= ~((freqs >= exclude[0]) & (freqs <= exclude[1]))
    df = freqs[1] - freqs[0]
    return psd[sel].sum(axis=0) * df


def eeg_relative_band(x, invalid, labels, channels, band, eeg_cfg, fs, min_valid_samples):
    """RF1 / RF2: median over the named channels of log10[P(band) / P(1-40 Hz excluding 14.5-17.5 Hz)]."""
    idx = [labels.index(c) for c in channels]
    freqs, psd, covered = masked_welch(x[:, idx], invalid[:, idx], fs, eeg_cfg["welch_window_s"], eeg_cfg["welch_overlap"])
    num = band_power(freqs, psd, *band)
    den = band_power(freqs, psd, *eeg_cfg["total_band_hz"], exclude=eeg_cfg["excluded_band_hz"])
    ok = (covered >= min_valid_samples) & np.isfinite(num) & np.isfinite(den) & (num > 0) & (den > 0)
    if not ok.any():
        return np.nan, float(np.median(covered) / fs)
    return float(np.median(np.log10(num[ok] / den[ok]))), float(np.median(covered[ok]) / fs)


# ----------------------------------------------------------------------------- ECG
def rr_series(peaks: np.ndarray, end_s: float, rr_valid=(0.3, 2.0)):
    """RR intervals between consecutive R-peaks inside [0, end]; returns (beat_times, rr, valid)."""
    p = np.sort(np.asarray(peaks, float))
    p = p[np.isfinite(p) & (p >= 0) & (p <= end_s)]
    rr = np.diff(p)
    valid = (rr >= rr_valid[0]) & (rr <= rr_valid[1])
    return p[1:], rr, valid


def heart_rate(peaks, end_s, rr_valid=(0.3, 2.0)):
    """RF3: median of 60/RR over valid RR."""
    _, rr, valid = rr_series(peaks, end_s, rr_valid)
    dur = float(rr[valid].sum())
    if not valid.any():
        return np.nan, 0.0
    return float(np.median(60.0 / rr[valid])), dur


def ln_rmssd(peaks, end_s, rr_valid=(0.3, 2.0), max_rel_change=0.2):
    """RF4: ln RMSSD (ms) over successive pairs with both RR valid and |dRR| < 0.2 * RR_prev."""
    _, rr, valid = rr_series(peaks, end_s, rr_valid)
    dur = float(rr[valid].sum())
    if len(rr) < 2:
        return np.nan, dur
    d = np.diff(rr)
    pair = valid[:-1] & valid[1:] & (np.abs(d) < max_rel_change * rr[:-1])
    if not pair.any():
        return np.nan, dur
    rmssd = np.sqrt(np.mean((d[pair] * 1000.0) ** 2))
    return (float(np.log(rmssd)) if rmssd > 0 else np.nan), dur


# ----------------------------------------------------------------------------- eye
def gaze_valid_mask(xy: np.ndarray, corrected: np.ndarray, width: float, height: float) -> np.ndarray:
    """Valid gaze: outside released correction intervals, finite, 0 <= x < width, 0 <= y < height."""
    x, y = xy[:, 0], xy[:, 1]
    finite = np.isfinite(x) & np.isfinite(y)
    with np.errstate(invalid="ignore"):
        inside = (x >= 0) & (x < width) & (y >= 0) & (y < height)
    return ~corrected & finite & inside


def gaze_on_screen(xy: np.ndarray, width: float, height: float) -> np.ndarray:
    x, y = xy[:, 0], xy[:, 1]
    with np.errstate(invalid="ignore"):
        return np.isfinite(x) & np.isfinite(y) & (x >= 0) & (x < width) & (y >= 0) & (y < height)


def pupil_valid_mask(pupil: np.ndarray, corrected: np.ndarray, gaze_screen: np.ndarray | None) -> np.ndarray:
    """Valid pupil (IS-006): outside pupil correction intervals, finite and > 0, gaze on screen when gaze exists."""
    p = pupil.reshape(-1)
    with np.errstate(invalid="ignore"):
        ok = ~corrected & np.isfinite(p) & (p > 0)
    if gaze_screen is not None:
        n = min(len(ok), len(gaze_screen))
        ok = ok[:n] & gaze_screen[:n]
    return ok


def gaze_dispersion(xy, valid, diagonal_px, fs):
    """RF5: sqrt(var x + var y) of valid gaze, divided by the screen diagonal."""
    if valid.sum() < 2:
        return np.nan, float(valid.sum() / fs)
    v = xy[valid, :2]
    return float(np.sqrt(v[:, 0].var() + v[:, 1].var()) / diagonal_px), float(valid.sum() / fs)


def inside_intervals(t: np.ndarray, intervals: np.ndarray) -> np.ndarray:
    """True where start <= t < end for any released correction interval."""
    t = np.asarray(t, float)
    if len(intervals) == 0:
        return np.zeros(len(t), bool)
    s, e = intervals[:, 0], intervals[:, 1]
    return ((t[:, None] >= s[None, :]) & (t[:, None] < e[None, :])).any(axis=1)


def saccade_rate(onsets, gaze_intervals, valid_gaze_samples, end_s, fs):
    """RF6: saccade onsets inside the video and outside correction intervals, per valid gaze minute."""
    t = np.asarray(onsets, float)
    t = t[np.isfinite(t) & (t >= 0) & (t < end_s)]
    n = int((~inside_intervals(t, gaze_intervals)).sum())
    minutes = valid_gaze_samples / fs / 60.0
    if minutes <= 0:
        return np.nan, 0.0
    return float(n / minutes), float(valid_gaze_samples / fs)


def pupil_variability(pupil, valid, fs):
    """RF-P: SD / mean of valid processed pupil."""
    p = pupil.reshape(-1)[: len(valid)][valid]
    if len(p) < 2 or p.mean() <= 0:
        return np.nan, float(valid.sum() / fs)
    return float(p.std() / p.mean()), float(valid.sum() / fs)


# ----------------------------------------------------------------------------- 2 Hz heart-rate series for SYN2
def hr_series(peaks, end_s, grid_hz=2.0, rr_valid=(0.3, 2.0)) -> np.ndarray:
    """Instantaneous HR (60/RR at the closing beat of each valid RR), linearly interpolated on a
    grid starting at 0 s; NaN outside the span of valid beats (no extrapolation)."""
    grid = np.arange(0.0, end_s, 1.0 / grid_hz)
    t, rr, valid = rr_series(peaks, end_s, rr_valid)
    out = np.full(len(grid), np.nan)
    if valid.sum() < 2:
        return out
    tb, hr = t[valid], 60.0 / rr[valid]
    inside = (grid >= tb[0]) & (grid <= tb[-1])
    out[inside] = np.interp(grid[inside], tb, hr)
    return out
