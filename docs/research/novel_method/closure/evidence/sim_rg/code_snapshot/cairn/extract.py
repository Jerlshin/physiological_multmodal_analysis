"""10 Hz per-exposure ocular series from the verified BBBD archives (outcome-free).

Each exposure's released 128 Hz streams are read in place through the frozen ``g01r.signals``
readers, trimmed to the video interval exactly as in G01-R, and summarized in 100 ms bins on
the recording clock (bin b covers [b/10, (b+1)/10) s):

* ``gx``, ``gy``   mean valid gaze (px); NaN when fewer than half of the bin's samples are valid;
* ``valid``        fraction of samples valid under the frozen G01-R rule
                   (outside correction intervals, finite, on screen);
* ``onscreen``     fraction finite and on screen, ignoring correction intervals;
* ``corrected``    fraction inside released gaze correction (interpolation) intervals;
* ``blink``        fraction inside released blink intervals;
* ``sacc``         number of released saccade onsets;
* ``pupil``        mean released pupil size over valid pupil samples (frozen rule); NaN otherwise;
* ``head_x/y/z``   mean released head position (E2-E5 only; NaN elsewhere).

No quiz outcome, item response or score is read.

Usage: PYTHONPATH=src python -m cairn.extract [--workers 5]
"""
from __future__ import annotations

import argparse
import json
import time
from multiprocessing import get_context

import numpy as np
import pandas as pd

from g01r import signals as sig
from g01r.features import reference_free as rf

from .exposures import all_exposures
from .paths import BIN_HZ, FS, SCREEN_H, SCREEN_W, SERIES, sha256_bytes

CHANNELS = ("gx", "gy", "valid", "onscreen", "corrected", "blink", "sacc", "pupil", "head_x", "head_y", "head_z")


def bin_index(n_samples: int, n_bins: int) -> np.ndarray:
    """Bin of each 128 Hz sample on the recording clock; -1 beyond the last whole bin."""
    b = np.floor(np.arange(n_samples) * BIN_HZ / FS).astype(int)
    b[b >= n_bins] = -1
    return b


def bin_mean(values: np.ndarray, ok: np.ndarray, b: np.ndarray, n_bins: int) -> tuple[np.ndarray, np.ndarray]:
    """Mean of ``values`` over ``ok`` samples per bin, and the per-bin fraction of ok samples."""
    keep = b >= 0
    cnt = np.bincount(b[keep], minlength=n_bins).astype(float)
    okk = ok[keep]
    n_ok = np.bincount(b[keep][okk], minlength=n_bins).astype(float)
    s = np.bincount(b[keep][okk], weights=values[keep][okk], minlength=n_bins)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = np.where(n_ok > 0, s / n_ok, np.nan)
        frac = np.where(cnt > 0, n_ok / cnt, np.nan)
    return mean, frac


def interval_fraction(intervals: np.ndarray, n_samples: int, b: np.ndarray, n_bins: int) -> np.ndarray:
    mask, _ = sig.intervals_to_mask(intervals, n_samples, FS) if len(intervals) else (np.zeros(n_samples, bool), 0)
    return bin_mean(np.zeros(n_samples), mask, b, n_bins)[1]


def _blinks(key: sig.ExposureKey) -> np.ndarray:
    member = f"derivatives/{key.subdir}/eyetrack/{key.stem}_desc-blinks.tsv.gz"
    if member not in sig.members(key.experiment):
        return np.zeros((0, 2))
    t = sig.read_table(key.experiment, member, header=0)
    return t[["start_time", "end_time"]].to_numpy(float)


def _head(key: sig.ExposureKey, n: int) -> np.ndarray | None:
    member = f"derivatives/{key.subdir}/eyetrack/{key.stem}_desc-head_eyetrack.tsv.gz"
    if member not in sig.members(key.experiment):
        return None
    h = sig.read_table(key.experiment, member, header=None).to_numpy(float)[:, :3]
    return h[:n]


def extract_one(row: dict) -> dict:
    key = sig.ExposureKey(int(row["experiment"]), row["participant_id"], int(row["session"]), int(row["local_stimulus_id"]))
    out = dict(uid=row["uid"], status="ok")
    try:
        end = key.end_seconds
        n_bins = int(np.floor(end * BIN_HZ))
        g = sig.read_eye(key, "gaze", "processed", FS)
        xy = g.values[:, :2]
        n = len(xy)
        b = bin_index(n, n_bins)
        valid = rf.gaze_valid_mask(xy, g.corrected, SCREEN_W, SCREEN_H)
        onscreen = rf.gaze_on_screen(xy, SCREEN_W, SCREEN_H)
        series = {}
        gx, vfrac = bin_mean(np.nan_to_num(xy[:, 0]), valid, b, n_bins)
        gy, _ = bin_mean(np.nan_to_num(xy[:, 1]), valid, b, n_bins)
        half = vfrac >= 0.5
        series["gx"] = np.where(half, gx, np.nan)
        series["gy"] = np.where(half, gy, np.nan)
        series["valid"] = vfrac
        series["onscreen"] = bin_mean(np.zeros(n), onscreen, b, n_bins)[1]
        series["corrected"] = bin_mean(np.zeros(n), g.corrected[:n], b, n_bins)[1]
        series["blink"] = interval_fraction(_blinks(key), n, b, n_bins)
        try:
            on = sig.read_saccade_onsets(key)
            ob = np.floor(on[np.isfinite(on)] * BIN_HZ).astype(int)
            ob = ob[(ob >= 0) & (ob < n_bins)]
            series["sacc"] = np.bincount(ob, minlength=n_bins).astype(float)
        except sig.SignalUnavailable:
            series["sacc"] = np.full(n_bins, np.nan)
        if key.has("pupil_processed"):
            p = sig.read_eye(key, "pupil", "processed", FS)
            pv = rf.pupil_valid_mask(p.values[:, 0], p.corrected, onscreen)
            m = min(len(pv), n)
            series["pupil"] = bin_mean(np.nan_to_num(p.values[:m, 0]), pv[:m], b[:m], n_bins)[0]
        else:
            series["pupil"] = np.full(n_bins, np.nan)
        h = _head(key, n)
        for j, c in enumerate(("head_x", "head_y", "head_z")):
            if h is None:
                series[c] = np.full(n_bins, np.nan)
            else:
                m = len(h)
                series[c] = bin_mean(np.nan_to_num(h[:, j]), np.isfinite(h[:, j]), b[:m], n_bins)[0]
        arr = np.vstack([series[c] for c in CHANNELS]).astype(np.float32)
        SERIES.mkdir(parents=True, exist_ok=True)
        path = SERIES / f"{row['uid']}.npy"
        tmp = path.with_suffix(".tmp.npy")
        np.save(tmp, arr)
        tmp.replace(path)
        out.update(end_seconds=end, n_bins=n_bins, n_samples=n, valid_fraction=float(valid[: n_bins * FS // BIN_HZ].mean()),
                   has_head=h is not None, sha256=sha256_bytes(arr.tobytes()))
    except sig.SignalUnavailable as e:
        out.update(status=f"unavailable: {e}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=5)
    a = ap.parse_args(argv)
    ex = all_exposures()
    ex = ex[ex.gaze_processed_present.fillna(False).astype(bool)]
    rows = ex.to_dict("records")
    t0 = time.time()
    with get_context("spawn").Pool(a.workers) as pool:
        res = pool.map(extract_one, rows, chunksize=4)
    man = ex.merge(pd.DataFrame(res), on="uid", how="left")
    SERIES.mkdir(parents=True, exist_ok=True)
    man.to_parquet(SERIES.parent / "series10_manifest.parquet", index=False)
    meta = dict(channels=CHANNELS, bin_hz=BIN_HZ, fs=FS, n=len(man), ok=int((man.status == "ok").sum()),
                seconds=round(time.time() - t0, 1))
    (SERIES.parent / "series10_meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
