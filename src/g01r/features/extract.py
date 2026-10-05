"""Outcome-blind feature extraction for every analysis-set cell (protocol §17.4).

Writes, per feature route:

* ``exposure_features.parquet``: RF features, Q, valid durations and availability flags;
* a signal cache used by the split-dependent synchrony features:
  EEG (centred over valid samples, invalid channel-samples set to 0, float32) with its
  all-channel validity vector, the 2 Hz heart-rate series, gaze x/y and z-scored pupil
  (NaN where invalid).

No quiz outcome is read anywhere in this module.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import pandas as pd

from .. import signals as sig
from ..config import DERIVED, ProtocolConfig, load_config, sha256_file
from . import quality, raw_route, reference_free as rf

ROUTES = ("processed", "raw")


def cell_uid(row) -> str:
    return f"e{int(row.experiment)}_{row.participant_id}_s{int(row.session)}_t{int(row.local_stimulus_id)}"


def cache_dir(route: str) -> Path:
    return DERIVED / "cache" / route


def features_path(route: str) -> Path:
    return DERIVED / "features" / route / "exposure_features.parquet"


@dataclass
class _Job:
    route: str
    rows: list
    config_path: str


def _save(path: Path, array: np.ndarray):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.npy")
    np.save(tmp, array)
    tmp.replace(path)


def _eeg_features(cfg, key, route, out, uid, cache):
    fs = cfg.fs
    rec = sig.read_eeg(key, route, fs)
    if route == "processed":
        data, invalid = rec.data, rec.zeroed
        out["Q_eeg_zeroed"] = quality.eeg_zeroed_fraction(rec.zeroed)
        out["Q_eeg_16hz_excess"] = quality.eeg_16hz_excess_audit(rec.data, rec.chunks, rec.labels, fs)
    else:
        eog = sig.read_eog_raw(key, fs) if key.has("eog_raw") else None
        data, invalid, regressed = raw_route.raw_route_eeg(rec.data, eog, fs, cfg.raw_route)
        out["raw_eog_regressed"] = bool(regressed)
    a, a_dur = rf.eeg_relative_band(data, invalid, rec.labels, cfg.eeg["alpha_channels"], cfg.eeg["alpha_band_hz"],
                                    cfg.eeg, fs, cfg.min_valid_samples)
    t, t_dur = rf.eeg_relative_band(data, invalid, rec.labels, cfg.eeg["theta_channels"], cfg.eeg["theta_band_hz"],
                                    cfg.eeg, fs, cfg.min_valid_samples)
    out.update(RF1_eeg_posterior_alpha=a, RF1_valid_s=a_dur, RF2_eeg_frontal_theta=t, RF2_valid_s=t_dur)
    # Synchrony cache: centre each channel over its valid samples, zero-fill invalid samples.
    valid = ~invalid
    cnt = valid.sum(axis=0)
    mean = np.divide((data * valid).sum(axis=0), cnt, out=np.zeros(data.shape[1]), where=cnt > 0)
    xt = np.where(valid, data - mean, 0.0).astype(np.float32)
    all_valid = valid.all(axis=1)
    _save(cache / "eeg" / f"{uid}.npy", xt)
    _save(cache / "eeg" / f"{uid}_valid.npy", all_valid)
    out["eeg_samples"] = int(len(xt))
    out["eeg_all_channel_valid_s"] = float(all_valid.sum() / fs)
    out["eeg_labels"] = json.dumps(rec.labels)


def _ecg_features(cfg, key, out, uid, cache):
    peaks = sig.read_rpeaks(key)
    end = key.end_seconds
    lo_hi = tuple(cfg.ecg["rr_valid_s"])
    hr, hr_dur = rf.heart_rate(peaks, end, lo_hi)
    lr, lr_dur = rf.ln_rmssd(peaks, end, lo_hi, cfg.ecg["rmssd_max_relative_change"])
    out.update(RF3_heart_rate=hr, RF3_valid_s=hr_dur, RF4_ln_rmssd=lr, RF4_valid_s=lr_dur)
    series = rf.hr_series(peaks, end, cfg.ecg["hr_grid_hz"], lo_hi)
    _save(cache / "hr" / f"{uid}.npy", series)
    out["hr_series_valid_s"] = float(np.isfinite(series).sum() / cfg.ecg["hr_grid_hz"])


def _eye_features(cfg, key, route, out, uid, cache):
    fs, d = cfg.fs, cfg.data
    gaze_screen = None
    if key.has(f"gaze_{route}"):
        g = sig.read_eye(key, "gaze", route, fs)
        xy = g.values[:, :2]
        valid = rf.gaze_valid_mask(xy, g.corrected, d["screen_width_px"], d["screen_height_px"])
        gaze_screen = rf.gaze_on_screen(xy, d["screen_width_px"], d["screen_height_px"])
        disp, disp_dur = rf.gaze_dispersion(xy, valid, d["screen_diagonal_px"], fs)
        try:
            onsets = sig.read_saccade_onsets(key)
            srate, s_dur = rf.saccade_rate(onsets, sig.read_intervals(key, "gaze"), int(valid.sum()), key.end_seconds, fs)
        except sig.SignalUnavailable:
            srate, s_dur = np.nan, 0.0
        out.update(RF5_gaze_dispersion=disp, RF5_valid_s=disp_dur, RF6_saccade_rate=srate, RF6_valid_s=s_dur, gaze_present=True)
        _save(cache / "gaze" / f"{uid}.npy", np.where(valid[:, None], xy, np.nan).astype(np.float32))
    if key.has(f"pupil_{route}"):
        p = sig.read_eye(key, "pupil", route, fs)
        pupil = p.values[:, 0]
        valid = rf.pupil_valid_mask(pupil, p.corrected, gaze_screen)
        pupil = pupil[: len(valid)]
        var, var_dur = rf.pupil_variability(pupil, valid, fs)
        out.update(RFP_pupil_variability=var, RFP_valid_s=var_dur, pupil_present=True)
        z = np.full(len(pupil), np.nan)
        if valid.sum() >= 2 and pupil[valid].std() > 0:
            z[valid] = (pupil[valid] - pupil[valid].mean()) / pupil[valid].std()
        _save(cache / "pupil" / f"{uid}.npy", z.astype(np.float32))


def extract_cell(cfg: ProtocolConfig, row, route: str) -> dict:
    key = sig.ExposureKey(int(row.experiment), row.participant_id, int(row.session), int(row.local_stimulus_id))
    uid = cell_uid(row)
    cache = cache_dir(route)
    out = dict(uid=uid, experiment=key.experiment, participant_id=key.participant_id, session=key.session,
               local_stimulus_id=key.local_stimulus_id, qualified_participant_id=row.qualified_participant_id,
               canonical_video_id=row.canonical_video_id, route=route, end_seconds=np.nan,
               eeg_present=False, ecg_present=False, gaze_present=False, pupil_present=False)
    try:
        out["end_seconds"] = key.end_seconds
    except sig.SignalUnavailable:
        # No released stream at all for this exposure (coverage-set cells only): every feature and Q missing.
        if route == "processed":
            out.update(Q_gaze_correction=np.nan, Q_pupil_correction=np.nan, Q_pupil_absent=1.0,
                       Q_eeg_zeroed=np.nan, Q_eeg_16hz_excess=np.nan)
        return out
    if route == "processed" or key.experiment != 1:
        if key.has("eeg_processed" if route == "processed" else "eeg_raw"):
            _eeg_features(cfg, key, route, out, uid, cache)
            out["eeg_present"] = True
    if route == "processed" and key.has("rpeaks"):
        _ecg_features(cfg, key, out, uid, cache)
        out["ecg_present"] = True
    _eye_features(cfg, key, route, out, uid, cache)
    if route == "processed":
        out["Q_gaze_correction"] = sig.correction_fraction(key, "gaze", cfg.fs)
        out["Q_pupil_correction"] = sig.correction_fraction(key, "pupil", cfg.fs)
        out["Q_pupil_absent"] = float(not key.has("pupil_processed"))
    return out


def _work(job: _Job):
    from types import SimpleNamespace

    cfg = load_config(Path(job.config_path))
    return [extract_cell(cfg, SimpleNamespace(**r), job.route) for r in job.rows]


def apply_missing_rule(frame: pd.DataFrame, cfg: ProtocolConfig) -> pd.DataFrame:
    """Protocol §6: a feature with fewer than 60 s of valid data is set missing."""
    f = frame.copy()
    pairs = [("RF1_eeg_posterior_alpha", "RF1_valid_s"), ("RF2_eeg_frontal_theta", "RF2_valid_s"),
             ("RF3_heart_rate", "RF3_valid_s"), ("RF4_ln_rmssd", "RF4_valid_s"),
             ("RF5_gaze_dispersion", "RF5_valid_s"), ("RF6_saccade_rate", "RF6_valid_s"),
             ("RFP_pupil_variability", "RFP_valid_s")]
    for value, dur in pairs:
        if value not in f:
            f[value] = np.nan
            f[dur] = 0.0
        short = ~(f[dur].fillna(0) >= cfg.data["min_valid_seconds"])
        f.loc[short, value] = np.nan
    return f


def extract(cfg: ProtocolConfig, cells: pd.DataFrame, route: str, workers: int = 6, chunk: int = 8) -> pd.DataFrame:
    if route not in ROUTES:
        raise ValueError(route)
    cols = ["experiment", "participant_id", "session", "local_stimulus_id", "qualified_participant_id", "canonical_video_id"]
    rows = cells[cols].to_dict("records")
    jobs = [_Job(route, rows[i:i + chunk], str(cfg.path)) for i in range(0, len(rows), chunk)]
    t0, results = time.time(), []
    with get_context("spawn").Pool(workers) as pool:
        for i, part in enumerate(pool.imap(_work, jobs)):
            results.extend(part)
            if (i + 1) % 10 == 0:
                print(f"[{route}] {len(results)}/{len(rows)} cells, {time.time() - t0:.0f}s", flush=True)
    frame = apply_missing_rule(pd.DataFrame(results), cfg)
    path = features_path(route)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)
    return frame


def cache_index(route: str) -> pd.DataFrame:
    rows = []
    root = cache_dir(route)
    for p in sorted(root.rglob("*.npy")):
        rows.append(dict(route=route, kind=p.parent.name, file=str(p.relative_to(root)), bytes=p.stat().st_size,
                         sha256=sha256_file(p)))
    return pd.DataFrame(rows)
