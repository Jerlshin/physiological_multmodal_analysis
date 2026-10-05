"""Split-dependent synchrony features SYN1-SYN3 and SYN-P (protocol §6), computed under a
:class:`g01r.references.ReferencePlan`.

* SYN1 EEG ISC: CorrCA filters fitted on the plan's CorrCA cells (pooled over their
  experiment x video units; within-subject covariance shrunk toward its mean eigenvalue,
  gamma = 0.5); sum over components 1-3 of Pearson r between the target's component time
  course and the mean of its reference people's component time courses, on samples valid
  in both (IS-007/IS-008).
* SYN2 heart-rate ISC on the 2 Hz instantaneous-HR series.
* SYN3 gaze ISC: mean of the horizontal and vertical Pearson r.
* SYN-P pupil ISC on the within-recording z-scored pupil.

Missing rule: fewer than 60 s of samples valid for both target and reference -> NaN.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd
from scipy.linalg import eigh

from ..config import ProtocolConfig
from ..population import AnalysisSet
from ..references import ReferencePlan
from .extract import cache_dir, cell_uid

SYN_COLUMNS = ["SYN1_eeg_isc", "SYN2_hr_isc", "SYN3_gaze_isc", "SYNP_pupil_isc"]


class SignalStore:
    """Memory-mapped access to the per-exposure signal cache of one feature route."""

    def __init__(self, route: str):
        self.route = route
        self.root = cache_dir(route)
        self.processed_root = cache_dir("processed")   # heart-rate series are route-independent

    def _path(self, kind, uid, suffix=""):
        root = self.processed_root if kind == "hr" else self.root
        return root / kind / f"{uid}{suffix}.npy"

    def has(self, kind, uid) -> bool:
        return self._path(kind, uid).exists()

    @lru_cache(maxsize=None)
    def eeg(self, uid):
        return np.load(self._path("eeg", uid), mmap_mode="r"), np.load(self._path("eeg", uid, "_valid"))

    @lru_cache(maxsize=1024)            # bounded: ~0.4 GB per worker at most
    def series(self, kind, uid):
        return np.load(self._path(kind, uid)).astype(np.float32)


def _pad(arrays, width=None):
    """Stack variable-length (T x k) arrays into a time-last (N x k x Tmax) float64 array, NaN padded."""
    T = max(len(a) for a in arrays)
    k = arrays[0].shape[1] if arrays[0].ndim == 2 else 1
    out = np.full((len(arrays), k, T), np.nan)
    for i, a in enumerate(arrays):
        out[i, :, : len(a)] = np.asarray(a, float).reshape(len(a), k).T
    return out


def _pearson_rows(A: np.ndarray, B: np.ndarray, M: np.ndarray):
    """Row-wise Pearson r of A and B (n x k x T, time last) over samples where M is True (two-pass, centred)."""
    n = M.sum(axis=-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        Az = np.where(M, A, 0.0)
        Bz = np.where(M, B, 0.0)
        ma = Az.sum(axis=-1) / n
        mb = Bz.sum(axis=-1) / n
        Az -= ma[..., None]
        Bz -= mb[..., None]
        Az *= M
        Bz *= M
        r = (Az * Bz).sum(axis=-1) / np.sqrt((Az * Az).sum(axis=-1) * (Bz * Bz).sum(axis=-1))
    r[n < 3] = np.nan
    return r, n.astype(int)


def masked_pearson(a: np.ndarray, b: np.ndarray, valid: np.ndarray):
    """Pearson r between columns of a and b (T x k) over rows where ``valid`` (T x k) is True."""
    r, n = _pearson_rows(a.T[None], b.T[None], valid.T[None])
    return r[0], n[0]


def reference_correlations(Y: np.ndarray, members: np.ndarray, refs: dict, min_valid: int):
    """Y: N x k x T (time last, NaN invalid) for the N member cells; ``refs`` maps member position ->
    member positions. Returns dicts r[i] (k,) and n[i] (jointly valid samples). The reference mean at
    each sample averages the reference people valid at that sample; a target never enters its own
    reference."""
    if not refs:
        return {}, {}
    V = np.isfinite(Y)
    Yz = np.where(V, Y, 0.0)
    union = np.unique(np.concatenate([np.asarray(r, int) for r in refs.values()]))
    S_u = Yz[union].sum(axis=0)
    C_u = V[union].sum(axis=0).astype(float)
    targets = np.fromiter(refs.keys(), int)
    REF = np.empty((len(targets),) + Y.shape[1:])
    CNT = np.empty((len(targets),) + Y.shape[1:])
    shared = {}
    for t, i in enumerate(targets):
        excl = np.setdiff1d(union, refs[i])
        if len(excl) == 0:
            REF[t], CNT[t] = S_u, C_u
        elif len(excl) == 1:
            np.subtract(S_u, Yz[excl[0]], out=REF[t])
            np.subtract(C_u, V[excl[0]], out=CNT[t])
        else:
            key = excl.tobytes()
            if key not in shared:
                shared[key] = (S_u - Yz[excl].sum(axis=0), C_u - V[excl].sum(axis=0))
            REF[t], CNT[t] = shared[key]
    M = V[targets] & (CNT >= 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        REF /= CNT
    r, n = _pearson_rows(Y[targets], REF, M)
    n_joint = n.min(axis=1)
    r[n_joint < min_valid] = np.nan
    return {i: r[t] for t, i in enumerate(targets)}, {i: int(n_joint[t]) for t, i in enumerate(targets)}


class CorrCAStats:
    """Pairwise cross-products C_ij = X_i' X_j of the zero-filled, centred EEG of all viewers
    of each experiment x video unit in an analysis set (exact sufficient statistics for
    pooled CorrCA on any subset of those viewers). Computed once per (set, route), stored
    on disk and memory-mapped by every worker."""

    def __init__(self, store: SignalStore, aset: AnalysisSet, uids: list, eeg_ok: np.ndarray, block: int = 4096):
        import hashlib
        import os

        from ..config import DERIVED

        self.units = {}
        ev = aset.ev
        root = DERIVED / "corrca_stats" / aset.name / store.route
        root.mkdir(parents=True, exist_ok=True)
        D = None
        for e in range(aset.n_ev):
            cells = np.flatnonzero((ev == e) & eeg_ok)
            if len(cells) == 0:
                continue
            tag = hashlib.sha256("|".join(uids[c] for c in cells).encode()).hexdigest()[:16]
            path = root / f"ev{e}_{tag}.npy"
            if not path.exists():
                Xs = [store.eeg(uids[c])[0] for c in cells]
                T = max(len(x) for x in Xs)
                D = Xs[0].shape[1]
                N = len(cells)
                G = np.zeros((N * D, N * D))
                for s in range(0, T, block):
                    B = np.zeros((min(block, T - s), N * D))
                    for i, x in enumerate(Xs):
                        seg = np.asarray(x[s:s + block], dtype=float)
                        B[: len(seg), i * D:(i + 1) * D] = seg
                    G += B.T @ B
                    del B
                C = G.reshape(N, D, N, D).transpose(0, 2, 1, 3)
                tmp = path.with_suffix(f".{os.getpid()}.tmp.npy")
                np.save(tmp, np.ascontiguousarray(C))
                os.replace(tmp, path)
                del G, C
            C = np.load(path, mmap_mode="r")
            D = C.shape[-1]
            self.units[e] = (cells, C)
        self.D = D

    def fit(self, fit_mask: np.ndarray, n_comp: int, gamma: float):
        D = self.D
        Rw = np.zeros((D, D))
        Rb = np.zeros((D, D))
        used = 0
        for e, (cells, C) in self.units.items():
            sel = np.flatnonzero(fit_mask[cells])
            if len(sel) == 0:
                continue
            diag = np.asarray(C[sel, sel]).sum(axis=0)
            Rw += diag
            used += len(sel)
            if len(sel) >= 2:
                total = np.asarray(C[np.ix_(sel, sel)]).sum(axis=(0, 1))
                Rb += (total - diag) / (len(sel) - 1)
        if used == 0:
            raise ValueError("CorrCA: no fitting cells")
        Rb = (Rb + Rb.T) / 2
        Rw = (Rw + Rw.T) / 2
        Rw_s = (1 - gamma) * Rw + gamma * np.trace(Rw) / D * np.eye(D)
        evals, evecs = eigh(Rb, Rw_s)
        order = np.argsort(evals)[::-1][:n_comp]
        return evecs[:, order], evals[order]


class SynchronyEngine:
    """Computes SYN features for a reference plan on one analysis set and route."""

    def __init__(self, cfg: ProtocolConfig, aset: AnalysisSet, features: pd.DataFrame, route: str):
        self.cfg, self.aset, self.route = cfg, aset, route
        self.store = SignalStore(route)
        self.uids = [cell_uid(r) for r in aset.cells.itertuples(index=False)]
        f = features.set_index("uid").reindex(self.uids)
        self.eeg_ok = (f.eeg_present.fillna(False).astype(bool).to_numpy()
                       & np.array([self.store.has("eeg", u) for u in self.uids]))
        self.has = {kind: np.array([self.store.has(kind, u) for u in self.uids]) for kind in ("hr", "gaze", "pupil")}
        self._corrca = None
        self.min_valid = {"eeg": cfg.min_valid_samples, "gaze": cfg.min_valid_samples,
                          "pupil": cfg.min_valid_samples,
                          "hr": int(round(cfg.data["min_valid_seconds"] * cfg.ecg["hr_grid_hz"]))}

    @property
    def corrca(self) -> CorrCAStats:
        if self._corrca is None:
            self._corrca = CorrCAStats(self.store, self.aset, self.uids, self.eeg_ok)
        return self._corrca

    def _by_video(self, plan: ReferencePlan, ok: np.ndarray):
        """Group targets by canonical video; members = targets and references with the signal."""
        video = self.aset.video
        groups = {}
        for c, r in plan.refs.items():
            if not ok[c]:
                continue
            groups.setdefault(video[c], {})[c] = r[ok[r]]
        return groups

    def _static(self, kind, plan, ok, transform):
        out = {}
        for v, tr in self._by_video(plan, ok).items():
            members = np.unique(np.concatenate([np.fromiter(tr.keys(), int)] + list(tr.values())))
            pos = {c: i for i, c in enumerate(members)}
            Y = _pad([transform(self.store.series(kind, self.uids[c])) for c in members])
            refs = {pos[c]: np.array([pos[x] for x in r], int) for c, r in tr.items()}
            rr, nn = reference_correlations(Y, members, refs, self.min_valid[kind])
            for c in tr:
                out[c] = (rr[pos[c]], nn[pos[c]])
        return out

    def compute(self, plan: ReferencePlan, blocks=("eeg", "hr", "gaze", "pupil")) -> pd.DataFrame:
        return self.compute_many([plan], blocks)[0]

    def compute_many(self, plans: list, blocks=("eeg", "hr", "gaze", "pupil"), batch: int = 10) -> list:
        """SYN features for several plans. EEG is read once per video per batch of plans: every
        plan's CorrCA filters are applied in one projection (identical results to one-by-one)."""
        out = []
        for i in range(0, len(plans), batch):
            out.extend(self._compute_batch(plans[i:i + batch], blocks))
        return out

    def _compute_batch(self, plans: list, blocks) -> list:
        n = self.aset.n
        res = [np.full((n, len(SYN_COLUMNS)), np.nan) for _ in plans]
        col = {c: j for j, c in enumerate(SYN_COLUMNS)}
        k = self.cfg.syn["corrca_components"]
        if "eeg" in blocks:
            jobs = [j for j, plan in enumerate(plans) if self.eeg_ok[plan.targets()].any()]
            Ws = {j: self.corrca.fit(plans[j].corrca_fit & self.eeg_ok, k, self.cfg.syn["corrca_shrinkage"])[0]
                  for j in jobs}
            groups = {j: self._by_video(plans[j], self.eeg_ok) for j in jobs}
            if jobs:
                videos = sorted({v for j in jobs for v in groups[j]})
                for v in videos:
                    members_v = np.unique(np.concatenate(
                        [np.concatenate([np.fromiter(tr.keys(), int)] + list(tr.values()))
                         for j in jobs if v in groups[j] for tr in [groups[j][v]]]))
                    proj = {}
                    for c in members_v:
                        x, valid = self.store.eeg(self.uids[c])
                        x64 = np.asarray(x, dtype=np.float64)
                        # One float64 projection per plan with a fixed shape: results are bit-identical
                        # however plans are batched (IS-009).
                        P = {}
                        for j in jobs:
                            if v in groups[j]:
                                y = x64 @ Ws[j]
                                y[~valid] = np.nan
                                P[j] = y
                        proj[c] = P
                    for j in jobs:
                        if v not in groups[j]:
                            continue
                        tr = groups[j][v]
                        members = np.unique(np.concatenate([np.fromiter(tr.keys(), int)] + list(tr.values())))
                        pos = {c: i for i, c in enumerate(members)}
                        Y = _pad([proj[c][j] for c in members])
                        refs = {pos[c]: np.array([pos[x] for x in r], int) for c, r in tr.items()}
                        rr, _ = reference_correlations(Y, members, refs, self.min_valid["eeg"])
                        for c in tr:
                            r = rr[pos[c]]
                            res[j][c, col["SYN1_eeg_isc"]] = r.sum() if np.isfinite(r).all() else np.nan
                    del proj
        for j, plan in enumerate(plans):
            if "hr" in blocks and self.has["hr"].any():
                for c, (r, _) in self._static("hr", plan, self.has["hr"], lambda a: a).items():
                    res[j][c, col["SYN2_hr_isc"]] = r[0]
            if "gaze" in blocks and self.has["gaze"].any():
                for c, (r, _) in self._static("gaze", plan, self.has["gaze"], lambda a: a).items():
                    res[j][c, col["SYN3_gaze_isc"]] = r.mean() if np.isfinite(r).all() else np.nan
            if "pupil" in blocks and self.has["pupil"].any():
                for c, (r, _) in self._static("pupil", plan, self.has["pupil"], lambda a: a).items():
                    res[j][c, col["SYNP_pupil_isc"]] = r[0]
            not_target = np.setdiff1d(np.arange(n), plan.targets())
            res[j][not_target] = np.nan
        return [pd.DataFrame(a, columns=SYN_COLUMNS) for a in res]
