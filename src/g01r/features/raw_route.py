"""Prespecified raw-export EEG route (measurement_provenance.md, frozen feature route item 2).

Strictly per exposure: zero-phase 0.5 Hz fifth-order high-pass and 59-61 Hz fifth-order
band-stop; common-average reference; least-squares regression of the (identically
filtered) released raw EOG channels; samples beyond 4 x IQR set missing with a +/-40 ms
extension. Returns the cleaned data and the per-channel missing mask.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import butter, sosfiltfilt


def raw_route_eeg(x: np.ndarray, eog: np.ndarray | None, fs: float, rr_cfg: dict):
    hp = butter(rr_cfg["highpass_order"], rr_cfg["highpass_hz"], btype="highpass", fs=fs, output="sos")
    w = rr_cfg["notch_halfwidth_hz"]
    notch = butter(rr_cfg["notch_order"], [rr_cfg["notch_hz"] - w, rr_cfg["notch_hz"] + w], btype="bandstop", fs=fs, output="sos")

    def filt(a):
        a = np.asarray(a, float)
        a = np.where(np.isfinite(a), a, 0.0)
        return sosfiltfilt(notch, sosfiltfilt(hp, a, axis=0), axis=0)

    y = filt(x)
    y = y - y.mean(axis=1, keepdims=True)                      # common-average reference
    regressed = False
    if eog is not None and len(eog):
        n = min(len(y), len(eog))
        e = filt(eog[:n])
        e = e[:, e.std(axis=0) > 0]
        if e.shape[1]:
            beta, *_ = np.linalg.lstsq(e, y[:n], rcond=None)
            y = y.copy()
            y[:n] = y[:n] - e @ beta
            regressed = True
    med = np.median(y, axis=0)
    q75, q25 = np.percentile(y, [75, 25], axis=0)
    bad = np.abs(y - med) > rr_cfg["artifact_iqr_multiple"] * (q75 - q25)
    ext = int(round(rr_cfg["artifact_extension_s"] * fs))
    if ext > 0 and bad.any():
        k = np.ones(2 * ext + 1)
        grown = np.zeros_like(bad)
        for c in np.flatnonzero(bad.any(axis=0)):
            grown[:, c] = np.convolve(bad[:, c].astype(float), k, mode="same") > 0
        bad = grown
    return y, bad, regressed
