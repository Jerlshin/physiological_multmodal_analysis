"""Feature provider for the frozen ``g01r`` pipeline on the John cohort (same interface as
``g01r.design.FeatureProvider``).

Blocks:
  C        age, sex, study condition                        (the plan's M2-ext covariates)
  P        pretest sum over the 7 knowPre items             (M2p only)
  Q        invalid-sample fraction                          (Q-ext, "gaze-data loss")
  QD       short-blink / long-loss / off-display shares     (amendment A2 only; replaces Q)
  RF_GAZE  gaze dispersion, saccade rate (+ block missing indicator)
  SYN_GAZE gaze ISC (+ indicator);  SYN_PUPIL pupil ISC (+ indicator, secondary block)

Synchrony uses :func:`reference_correlations_chunked`, a memory-bounded evaluation of the frozen
``g01r.features.synchrony.reference_correlations`` (same reference means, masks, two-pass Pearson
via the frozen ``_pearson_rows`` and the same 60 s missing rule); equality is asserted in the tests.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from g01r.design import plan_key
from g01r.features.synchrony import _pad, _pearson_rows
from g01r.population import AnalysisSet
from g01r.references import ReferencePlan

from .features import GRID_HZ, MIN_VALID_S
from .paths import SERIES

BLOCKS = {
    "C": ["age", "sex_n", "condition"],
    "P": ["pretest_sum"],
    "Q": ["Q_invalid"],
    "QD": ["Qd_blink", "Qd_long_loss", "Qd_offscreen"],
    "RF_GAZE": ["RF5_gaze_dispersion", "RF6_saccade_rate", "RF_GAZE_missing"],
    "SYN_GAZE": ["SYN3_gaze_isc", "SYN_GAZE_missing"],
    "SYN_PUPIL": ["SYNP_pupil_isc", "SYN_PUPIL_missing"],
}
SYN_BLOCKS = ("SYN_GAZE", "SYN_PUPIL")


def reference_correlations_chunked(Y: np.ndarray, V: np.ndarray, Yz: np.ndarray, refs: dict, min_valid: int,
                                   chunk: int = 16):
    """As ``g01r.features.synchrony.reference_correlations`` (Y: N x k x T, NaN invalid), with V and the
    zero-filled Yz precomputed once and the per-target reference means formed ``chunk`` targets at a time."""
    if not refs:
        return {}, {}
    union = np.unique(np.concatenate([np.asarray(r, int) for r in refs.values()]))
    S_u = Yz[union].sum(axis=0)
    C_u = V[union].sum(axis=0).astype(float)
    targets = np.fromiter(refs.keys(), int)
    r_out, n_out = {}, {}
    for start in range(0, len(targets), chunk):
        tg = targets[start:start + chunk]
        REF = np.empty((len(tg),) + Y.shape[1:])
        CNT = np.empty((len(tg),) + Y.shape[1:])
        for t, i in enumerate(tg):
            excl = np.setdiff1d(union, refs[i])
            if len(excl) == 0:
                REF[t], CNT[t] = S_u, C_u
            elif len(excl) == 1:
                np.subtract(S_u, Yz[excl[0]], out=REF[t])
                np.subtract(C_u, V[excl[0]], out=CNT[t])
            else:
                REF[t], CNT[t] = S_u - Yz[excl].sum(axis=0), C_u - V[excl].sum(axis=0)
        M = V[tg] & (CNT >= 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            REF /= CNT
        r, n = _pearson_rows(Y[tg], REF, M)
        n_joint = n.min(axis=1)
        r[n_joint < min_valid] = np.nan
        for t, i in enumerate(tg):
            r_out[int(i)], n_out[int(i)] = r[t], int(n_joint[t])
    return r_out, n_out


class JohnProvider:
    def __init__(self, aset: AnalysisSet, people: pd.DataFrame, syn_blocks=("SYN_GAZE",)):
        self.aset = aset
        self.syn_blocks = tuple(syn_blocks)
        p = people.set_index("participant").loc[aset.cells.participant_id]
        static = pd.DataFrame(index=np.arange(aset.n))
        for block in ("C", "P", "Q", "QD"):
            for c in BLOCKS[block]:
                static[c] = p[c].to_numpy(float)
        rf = BLOCKS["RF_GAZE"][:-1]
        for c in rf:
            static[c] = p[c].to_numpy(float)
        static["RF_GAZE_missing"] = static[rf].isna().any(axis=1).astype(float)
        self.static = static
        self.min_valid = int(round(MIN_VALID_S * GRID_HZ))
        self._series = {}
        self._cache = {}

    def series(self, kind: str):
        if kind not in self._series:
            Y = _pad([np.load(SERIES / f"{pid}_{kind}.npy") for pid in self.aset.cells.participant_id])
            V = np.isfinite(Y)
            self._series[kind] = (Y, V, np.where(V, Y, 0.0))
        return self._series[kind]

    def block_columns(self, block: str) -> list:
        return list(BLOCKS[block])

    @staticmethod
    def needs_syn(blocks) -> bool:
        return any(b in SYN_BLOCKS for b in blocks)

    def syn(self, plan: ReferencePlan) -> pd.DataFrame:
        key = plan_key(plan, "edf", self.aset.name) + "|" + ",".join(self.syn_blocks)
        if key in self._cache:
            return self._cache[key]
        frame = pd.DataFrame(index=np.arange(self.aset.n))
        refs = {int(c): np.asarray(r, int) for c, r in plan.refs.items()}
        for block, kind, col in (("SYN_GAZE", "gaze", "SYN3_gaze_isc"), ("SYN_PUPIL", "pupil", "SYNP_pupil_isc")):
            values = np.full(self.aset.n, np.nan)
            if block in self.syn_blocks:
                Y, V, Yz = self.series(kind)
                rr, _ = reference_correlations_chunked(Y, V, Yz, refs, self.min_valid)
                for c, r in rr.items():
                    values[c] = r.mean() if np.isfinite(r).all() else np.nan
            frame[col] = values
            frame[f"{block}_missing"] = np.isnan(values).astype(float)
        if len(self._cache) > 512:
            self._cache.clear()
        self._cache[key] = frame
        return frame

    def syn_many(self, plans: list) -> list:
        return [self.syn(p) for p in plans]

    def design(self, blocks, syn: pd.DataFrame | None):
        cols, parts = [], []
        for b in blocks:
            names = self.block_columns(b)
            src = syn if b in SYN_BLOCKS else self.static
            if src is None:
                raise ValueError(f"Block {b} needs synchrony features for this split")
            parts.append(src[names].to_numpy(float))
            cols.extend(names)
        X = np.column_stack(parts) if parts else np.zeros((self.aset.n, 0))
        return X, cols
