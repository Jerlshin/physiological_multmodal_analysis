"""Per-exposure signal access from the checksum-verified BBBD v1.1 archives.

Archives are read in place (stored ZIP members, no extraction). Every reader trims
continuous streams to the video interval [0, end) given by the exposure's
``events.tsv`` end marker, so "within the video" is identical across modalities.
Nothing here reads or derives quiz outcomes.
"""
from __future__ import annotations

import gzip
import io
import zipfile
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
import pandas as pd

from bbbd_audit.io import open_archive
from bbbd_audit.qc import bdf_chunks, bdf_header, intervals_to_mask

from .config import AUDIT_EVIDENCE


class SignalUnavailable(Exception):
    """A required member is absent from the release for this exposure."""


@lru_cache(maxsize=None)
def archive(exp: int) -> zipfile.ZipFile:
    # bbbd_audit.io.open_archive refuses any archive whose MD5/size does not match the
    # verified download manifest of the pinned release.
    return open_archive(exp)


@lru_cache(maxsize=None)
def members(exp: int) -> frozenset:
    return frozenset(archive(exp).namelist())


@lru_cache(maxsize=None)
def event_end_table() -> dict:
    out = {}
    for exp in (3, 4, 5):   # E1 has no event files in the release
        t = pd.read_parquet(AUDIT_EVIDENCE / f"events_exp{exp}.parquet",
                            columns=["experiment", "participant_id", "session", "local_stimulus_id", "end_seconds"])
        for r in t.itertuples(index=False):
            out[(int(r.experiment), r.participant_id, int(r.session), int(r.local_stimulus_id))] = r.end_seconds
    return out


@dataclass(frozen=True)
class ExposureKey:
    experiment: int
    participant_id: str
    session: int
    local_stimulus_id: int

    @property
    def stem(self) -> str:
        return f"{self.participant_id}_ses-{self.session:02d}_task-stim{self.local_stimulus_id:02d}"

    @property
    def subdir(self) -> str:
        return f"{self.participant_id}/ses-{self.session:02d}"

    def path(self, kind: str) -> str:
        s, d = self.stem, self.subdir
        paths = {
            "eeg_processed": f"derivatives/{d}/eeg/{s}_desc-eeg.bdf",
            "eeg_raw": f"{d}/eeg/{s}_eeg.bdf",
            "eog_raw": f"{d}/beh/{s}_recording-eog_physio.tsv.gz",
            "ecg_raw": f"{d}/beh/{s}_recording-ecg_physio.tsv.gz",
            "gaze_processed": f"derivatives/{d}/eyetrack/{s}_desc-gaze_visualangle_eyetrack.tsv.gz",
            "gaze_raw": f"{d}/eyetrack/{s}_gaze_visualangle_eyetrack.tsv.gz",
            "pupil_processed": f"derivatives/{d}/eyetrack/{s}_desc-pupil_eyetrack.tsv.gz",
            "pupil_raw": f"{d}/eyetrack/{s}_pupil_eyetrack.tsv.gz",
            "gaze_intervals": f"derivatives/{d}/eyetrack/{s}_desc-gaze_interpolation_timestamps.tsv.gz",
            "pupil_intervals": f"derivatives/{d}/eyetrack/{s}_desc-pupil_interpolation_timestamps.tsv.gz",
            "saccades": f"derivatives/{d}/eyetrack/{s}_desc-saccades.tsv.gz",
            "rpeaks": f"derivatives/{d}/beh/{s}_desc-rpeak_timestamps.tsv.gz",
        }
        return paths[kind]

    def has(self, kind: str) -> bool:
        return self.path(kind) in members(self.experiment)

    @property
    def end_seconds(self) -> float:
        """Video end relative to stimulus onset.

        From the exposure's ``events.tsv`` end marker (released with the EEG). Exposures
        without an event file (all of E1; E3-E5 exposures whose EEG is absent) use the
        length of the first available stimulus-aligned export, in the order processed
        gaze, raw ECG, processed pupil (rows / 128 Hz; IS-002).
        """
        key = (self.experiment, self.participant_id, self.session, self.local_stimulus_id)
        end = event_end_table().get(key)
        if end is None:
            return _export_seconds(self)
        if not np.isfinite(end):
            raise SignalUnavailable(f"Non-finite end event for {key}")
        return float(end)

    def n_video_samples(self, fs: int) -> int:
        return int(round(self.end_seconds * fs))


@lru_cache(maxsize=4096)
def _export_seconds(key: ExposureKey, fs: int = 128) -> float:
    for kind in ("gaze_processed", "ecg_raw", "pupil_processed"):
        member = key.path(kind)
        if member in members(key.experiment):
            return len(read_table(key.experiment, member, header=None)) / fs
    raise SignalUnavailable(f"No stimulus-aligned export to define the video interval of {key}")


def _read(exp: int, member: str) -> bytes:
    if member not in members(exp):
        raise SignalUnavailable(member)
    raw = archive(exp).read(member)
    return gzip.decompress(raw) if member.endswith(".gz") else raw


def read_table(exp: int, member: str, header) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(_read(exp, member)), sep="\t", header=header)


@dataclass
class EEGRecording:
    data: np.ndarray            # samples x channels, physical units (uV), video-trimmed
    zeroed: np.ndarray          # samples x channels, True where the released value encodes exactly 0 uV
    labels: list
    fs: float
    gain: np.ndarray
    chunks: list = field(default_factory=list)   # (start, stop) of the audit's BDF read chunks


def zero_digital_codes(pmin, pmax, dmin, dmax):
    """Per channel, the two digital codes bracketing 0 physical units (floor and ceil of the exact
    zero crossing); they coincide when 0 is exactly representable."""
    pmin, pmax, dmin, dmax = (np.asarray(a, float) for a in (pmin, pmax, dmin, dmax))
    gain = (pmax - pmin) / (dmax - dmin)
    crossing = -(pmin - gain * dmin) / gain
    return np.floor(crossing), np.ceil(crossing)


def read_eeg(key: ExposureKey, route: str, fs_expected: int) -> EEGRecording:
    """Processed (``route='processed'``) or raw-export (``'raw'``) EEG, trimmed to the video.

    Zero coding (IS-003): the released BDF stores 16-bit codes with a symmetric
    physical range, so 0 uV is not representable exactly; it is written as the
    digital code nearest to 0 uV (0 or -1, both +/- half an LSB). A sample is
    "exactly zero" in the release when its digital code is one of those two codes.
    """
    member = key.path("eeg_processed" if route == "processed" else "eeg_raw")
    if member not in members(key.experiment):
        raise SignalUnavailable(member)
    bound = key.n_video_samples(fs_expected)
    xs, zs, chunks, seen = [], [], [], 0
    with archive(key.experiment).open(member) as f:
        h = bdf_header(f)
        fs = float(h["samples_per_record"][0] / h["record_seconds"])
        if fs != fs_expected:
            raise ValueError(f"Unexpected EEG rate {fs} in {member}")
        gain = (h["physical_max"] - h["physical_min"]) / (h["digital_max"] - h["digital_min"])
        lo, hi = zero_digital_codes(h["physical_min"], h["physical_max"], h["digital_min"], h["digital_max"])
        for x, d in bdf_chunks(f, h):
            take = max(0, min(len(x), bound - seen))
            if take:
                xs.append(x[:take])
                zs.append((d[:take] == lo[None, :]) | (d[:take] == hi[None, :]))
                chunks.append((seen, seen + take))
            seen += len(x)
    if not xs:
        raise SignalUnavailable(f"Empty EEG {member}")
    labels = list(h["labels"])
    return EEGRecording(np.vstack(xs), np.vstack(zs), labels, fs, gain, chunks)


def read_eog_raw(key: ExposureKey, fs: int) -> np.ndarray:
    x = read_table(key.experiment, key.path("eog_raw"), header=None).to_numpy(float)
    return x[: key.n_video_samples(fs)]


@dataclass
class EyeRecording:
    values: np.ndarray          # samples x columns (gaze: x, y [, vdx, vdy]; pupil: size)
    corrected: np.ndarray       # released correction-interval mask on the file's own grid
    n_file_samples: int


def read_intervals(key: ExposureKey, which: str) -> np.ndarray:
    kind = f"{which}_intervals"
    if not key.has(kind):
        return np.zeros((0, 2))
    t = read_table(key.experiment, key.path(kind), header=0)
    return t.iloc[:, :2].to_numpy(float)


def read_eye(key: ExposureKey, which: str, route: str, fs: int) -> EyeRecording:
    """Gaze or pupil stream (processed or raw export) plus the released correction mask."""
    member = key.path(f"{which}_{route}")
    if member not in members(key.experiment):
        raise SignalUnavailable(member)
    values = read_table(key.experiment, member, header=None).to_numpy(float)
    n_file = len(values)
    mask, _ = intervals_to_mask(read_intervals(key, which), n_file, fs)
    n = min(n_file, key.n_video_samples(fs))
    return EyeRecording(values[:n], mask[:n], n_file)


def correction_fraction(key: ExposureKey, which: str, fs: int) -> float:
    """Audit definition: released intervals on the processed file's full sample grid."""
    member = key.path(f"{which}_processed")
    if member not in members(key.experiment):
        return np.nan
    n_file = len(read_table(key.experiment, member, header=None))
    mask, _ = intervals_to_mask(read_intervals(key, which), n_file, fs)
    return float(mask.mean())


def read_saccade_onsets(key: ExposureKey) -> np.ndarray:
    if not key.has("saccades"):
        raise SignalUnavailable(key.path("saccades"))
    t = read_table(key.experiment, key.path("saccades"), header=0)
    return t["start_time"].to_numpy(float)


def read_rpeaks(key: ExposureKey) -> np.ndarray:
    if not key.has("rpeaks"):
        raise SignalUnavailable(key.path("rpeaks"))
    t = read_table(key.experiment, key.path("rpeaks"), header=0)
    return np.sort(t.iloc[:, 0].to_numpy(float))
