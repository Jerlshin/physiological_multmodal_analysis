"""Quality variables Q (protocol §6), entered in every baseline model."""
from __future__ import annotations

import numpy as np

from bbbd_audit.qc import Stats


def eeg_zeroed_fraction(zeroed: np.ndarray) -> float:
    """Median over channels of the fraction of video samples whose released value encodes 0 uV."""
    return float(np.median(zeroed.mean(axis=0)))


def eeg_16hz_excess_audit(data: np.ndarray, chunks, labels, fs: float) -> float:
    """Median over channels of the audit's 16 Hz excess (dB).

    Reuses the audit's own streaming estimator (bbbd_audit.qc.Stats) on the identical
    BDF read chunks, so the value equals the audited definition exactly (validated
    against files_exp*.parquet: eeg_16hz_median_db).
    """
    stats = Stats(data.shape[1], fs)
    for start, stop in chunks:
        stats.update(data[start:stop])
    rows = stats.result(labels)
    return float(np.median([r.get("excess_16hz_db", 0) for r in rows]))
