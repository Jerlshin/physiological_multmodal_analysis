"""Feature blocks and design matrices for an analysis set (protocol §6, §8 step 4-5).

Static blocks (C, Q, RF) are exposure- or person-level and split-independent. Synchrony
blocks are recomputed for every split from its :class:`~g01r.references.ReferencePlan`.
Every physiological block carries a block missing-indicator; C and Q carry their explicit
indicators. Imputation and standardization happen later, inside the training split.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import numpy as np
import pandas as pd

from .config import DERIVED, ProtocolConfig
from .features import C_COLUMNS, C_COLUMNS_E1, GPA_COLUMNS, RF_BLOCKS, SYN_BLOCKS
from .features.covariates import covariate_table
from .features.extract import cell_uid, features_path
from .features.synchrony import SynchronyEngine
from .population import AnalysisSet
from .references import ReferencePlan
from .rng import rng_for

Q_BLOCK = ["Q_gaze_correction", "Q_gaze_missing", "Q_pupil_correction", "Q_pupil_absent",
           "Q_eeg_zeroed", "Q_eeg_16hz_excess", "Q_eeg_missing"]
Q_BLOCK_E1 = ["Q_gaze_correction", "Q_gaze_missing", "Q_pupil_correction", "Q_pupil_absent"]
NOISE_DIM = 9   # matched to the core RF + SYN feature count (6 + 3)


def plan_key(plan: ReferencePlan, route: str, set_name: str) -> str:
    h = hashlib.sha256(f"{set_name}|{route}|{plan.regime}".encode())
    for c in sorted(plan.refs):
        h.update(np.int64(c).tobytes())
        h.update(np.asarray(plan.refs[c], np.int64).tobytes())
    h.update(np.packbits(plan.corrca_fit).tobytes())
    return h.hexdigest()


class FeatureProvider:
    def __init__(self, cfg: ProtocolConfig, aset: AnalysisSet, route: str = "processed", include_gpa: bool = False,
                 ocular_only: bool | None = None, syn_disk_cache: bool = True):
        self.cfg, self.aset, self.route = cfg, aset, route
        self.ocular_only = bool((aset.experiment == 1).all()) if ocular_only is None else ocular_only
        self.include_gpa = include_gpa
        uids = [cell_uid(r) for r in aset.cells.itertuples(index=False)]
        processed = pd.read_parquet(features_path("processed")).set_index("uid").reindex(uids)
        if processed.index.isna().any() or processed.experiment.isna().any():
            raise KeyError("Feature table lacks cells of this analysis set; rerun extraction")
        routed = processed if route == "processed" else pd.read_parquet(features_path(route)).set_index("uid").reindex(uids)
        self.features_frame = (processed if route == "processed" else routed).reset_index()
        static = pd.DataFrame(index=np.arange(aset.n))
        # Reference-free blocks: EEG, gaze and pupil from the route; ECG timing is route-independent.
        for block, cols in RF_BLOCKS.items():
            src = processed if block == "RF_ECG" else routed
            for c in cols:
                static[c] = src[c].to_numpy(float) if c in src else np.nan
            static[f"{block}_missing"] = static[cols].isna().any(axis=1).astype(float)
        # Quality (always the processed-release definitions; identical across routes).
        for c in ["Q_gaze_correction", "Q_pupil_correction", "Q_pupil_absent", "Q_eeg_zeroed", "Q_eeg_16hz_excess"]:
            static[c] = processed[c].to_numpy(float)
        static["Q_gaze_missing"] = static.Q_gaze_correction.isna().astype(float)
        static["Q_eeg_missing"] = (static.Q_eeg_zeroed.isna() | static.Q_eeg_16hz_excess.isna()).astype(float)
        static["Q_pupil_absent"] = static.Q_pupil_absent.fillna(1.0)
        # Covariates (person level).
        cov = covariate_table().set_index("qualified_participant_id")
        cov = cov.reindex(aset.cells.qualified_participant_id)
        for c in C_COLUMNS + GPA_COLUMNS:
            static[c] = cov[c].to_numpy(float)
        # Matched random-feature control (shortcut diagnostic iii): fixed seed, independent of everything.
        noise = rng_for(cfg.resampling["base_seed"], "noise_block", aset.name).normal(size=(aset.n, NOISE_DIM))
        for j in range(NOISE_DIM):
            static[f"NOISE_{j + 1}"] = noise[:, j]
        self.static = static
        self._engine = None
        self._syn_cache = {}
        self.syn_disk_cache = syn_disk_cache

    # ------------------------------------------------------------------ blocks
    def block_columns(self, block: str) -> list:
        if block == "C":
            cols = list(C_COLUMNS_E1 if self.ocular_only else C_COLUMNS)
            return cols + (list(GPA_COLUMNS) if self.include_gpa else [])
        if block == "Q":
            return list(Q_BLOCK_E1 if self.ocular_only else Q_BLOCK)
        if block in RF_BLOCKS:
            return RF_BLOCKS[block] + [f"{block}_missing"]
        if block in SYN_BLOCKS:
            return SYN_BLOCKS[block] + [f"{block}_missing"]
        if block == "NOISE":
            return [f"NOISE_{j + 1}" for j in range(NOISE_DIM)]
        raise KeyError(block)

    @property
    def engine(self) -> SynchronyEngine:
        if self._engine is None:
            self._engine = SynchronyEngine(self.cfg, self.aset, self.features_frame, self.route)
        return self._engine

    def syn(self, plan: ReferencePlan, blocks=("eeg", "hr", "gaze", "pupil")) -> pd.DataFrame:
        key = plan_key(plan, self.route, self.aset.name) + "|" + ",".join(blocks)
        if key in self._syn_cache:
            return self._syn_cache[key]
        path = self._cache_path(key)
        if self.syn_disk_cache and path.exists():
            frame = pd.read_parquet(path)
            if len(self._syn_cache) > 256:
                self._syn_cache.clear()
            self._syn_cache[key] = frame
            return frame
        frame = self.engine.compute(plan, blocks)
        for block, cols in SYN_BLOCKS.items():
            frame[f"{block}_missing"] = frame[cols].isna().any(axis=1).astype(float)
        self._store(key, frame)
        return frame

    def _cache_path(self, key: str) -> Path:
        return DERIVED / "syn_cache" / self.aset.name / self.route / (hashlib.sha256(key.encode()).hexdigest() + ".parquet")

    def syn_many(self, plans: list, blocks=("eeg", "hr", "gaze", "pupil")) -> list:
        """Batch version of :meth:`syn`: computes only plans absent from the memory/disk caches,
        sharing one pass over the EEG cache per batch."""
        keys = [plan_key(p, self.route, self.aset.name) + "|" + ",".join(blocks) for p in plans]
        todo = [i for i, k in enumerate(keys) if k not in self._syn_cache
                and not (self.syn_disk_cache and self._cache_path(k).exists())]
        if todo:
            frames = self.engine.compute_many([plans[i] for i in todo], blocks)
            for i, frame in zip(todo, frames):
                for block, cols in SYN_BLOCKS.items():
                    frame[f"{block}_missing"] = frame[cols].isna().any(axis=1).astype(float)
                self._store(keys[i], frame)
        return [self.syn(p, blocks) for p in plans]

    def _store(self, key: str, frame: pd.DataFrame):
        if self.syn_disk_cache:
            path = self._cache_path(key)
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(f".{os.getpid()}.tmp")
            frame.to_parquet(tmp)
            os.replace(tmp, path)     # atomic: concurrent workers never see a partial file
        if len(self._syn_cache) > 256:
            self._syn_cache.clear()
        self._syn_cache[key] = frame

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

    @staticmethod
    def needs_syn(blocks) -> bool:
        return any(b in SYN_BLOCKS for b in blocks)


class FixedFeatureProvider:
    """Provider over fixed matrices (simulation and tests): same interface, no reference plans."""

    def __init__(self, blocks: dict, n: int):
        self.blocks = blocks          # block name -> (n x p) array
        self.n = n

    def block_columns(self, block):
        return [f"{block}_{j}" for j in range(self.blocks[block].shape[1])]

    def syn(self, plan, blocks=None):
        return None

    def syn_many(self, plans, blocks=None):
        return [None for _ in plans]

    def design(self, blocks, syn=None):
        parts = [self.blocks[b] for b in blocks]
        cols = [c for b in blocks for c in self.block_columns(b)]
        X = np.column_stack(parts) if parts else np.zeros((self.n, 0))
        return X, cols

    @staticmethod
    def needs_syn(blocks) -> bool:
        return False
