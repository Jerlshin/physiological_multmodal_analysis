"""Fold-safe per-second channels and anchored moment terms for CAIRN-linear (plan §10-§11; spec §2.2).

Channels (Stage-0 decision S0-D09; plan [S0-3])
-----------------------------------------------
Six primary channels at 1 Hz on the recording clock:

* reference-free: ``loss_long`` (fraction of the second inside invalid episodes >= 1 s, the NH4
  channel, S0-D12), ``onscreen``, ``sacc`` (saccade onsets), ``disp5`` (5 s gaze dispersion);
* reference-relative: ``logdens`` (peer-KDE log-density) and ``rho5`` (5 s correlation with the
  peer mean course).

Fold safety (plan §11.1, §15.3; spec §3 tests 2-3)
--------------------------------------------------
Everything that crosses recordings is fitted on the **training learners of the split**:

* regime A references: for a training learner, the other training learners who viewed the same
  video in the same experiment; for a test learner, all of them. The target learner is never in
  its own reference (:func:`cairn.channels.reference_stats` raises);
* regime C references: the other, unlabelled half of the cohort, assigned by a hash of the learner
  id only (never by outcome, condition or quality);
* channel standardization: mean and SD over training cells' seconds;
* item centring and scaling of the moment regressor: training rows only (:func:`moment_regressors`).

Every split is identified by a hash of (set, regime, training learners, channel version); caches are
keyed by it (as G01-R caches synchrony features by split identity).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .channels import load as load_series
from .channels import reference_free, reference_relative, reference_stats
from .design import Incidence
from .extract import CHANNELS
from .paths import BIN_HZ, STAGE1_CACHE

CHANNEL_VERSION = "s1-v1"
PRIMARY = ("loss_long", "onscreen", "logdens", "rho5", "sacc", "disp5")
REF_FREE_USED = ("loss_long", "onscreen", "sacc", "disp5")
REF_REL_USED = ("logdens", "rho5")
VALIDITY = ("loss_long",)
GAZE = ("logdens", "rho5", "sacc", "disp5")
# Sign that makes "more engaged" positive, from the Stage-0 construct check (distracted - attentive dz):
# rho5 -1.28, sacc -.99, logdens -.75, disp5 -.69, onscreen -.50; long invalid episodes 7x under distraction.
ENGAGED_SIGN = {"loss_long": -1.0, "onscreen": 1.0, "logdens": 1.0, "rho5": 1.0, "sacc": 1.0, "disp5": 1.0}
LONG_EPISODE_BINS = BIN_HZ           # >= 1 s
MIN_COVERAGE = 0.25                  # as cairn.pooling.pooled
_IX = {c: i for i, c in enumerate(CHANNELS)}


# ----------------------------------------------------------------------------- channels
def long_loss(valid10: np.ndarray, n_s: int, min_bins: int = LONG_EPISODE_BINS) -> np.ndarray:
    """Per-second fraction of 100 ms bins inside invalid runs of at least ``min_bins`` bins.
    A bin is invalid when fewer than half its samples pass the frozen validity rule (or it is NaN)."""
    v = np.asarray(valid10[: n_s * BIN_HZ], float)
    inv = ~(v >= 0.5)
    out = np.zeros(len(v))
    i = 0
    while i < len(v):
        if inv[i]:
            j = i
            while j < len(v) and inv[j]:
                j += 1
            if j - i >= min_bins:
                out[i:j] = 1.0
            i = j
        else:
            i += 1
    if len(out) < n_s * BIN_HZ:
        out = np.r_[out, np.ones(n_s * BIN_HZ - len(out))]
    return out.reshape(n_s, BIN_HZ).mean(1)


def ref_free_cell(a: np.ndarray, n_s: int) -> np.ndarray:
    rf = reference_free(a, n_s)
    return np.column_stack([long_loss(a[_IX["valid"]], n_s), rf["onscreen"], rf["sacc"], rf["disp5"]])


def ref_rel_cell(a: np.ndarray, ref, n_s: int) -> np.ndarray:
    rf = pd.DataFrame(dict(pupil=np.full(n_s, np.nan), valid=np.full(n_s, np.nan)))
    rr = reference_relative(a, rf, ref, n_s)
    return np.column_stack([rr["logdens"], rr["rho5"]])


def regime_a_references(cells: pd.DataFrame, train_persons: set) -> dict:
    """uid -> reference uids: training learners on the same (experiment, video), never the target."""
    out = {}
    tr = cells[cells.person.isin(train_persons)]
    for r in cells.itertuples():
        g = tr[(tr.experiment == r.experiment) & (tr.video == r.video) & (tr.person != r.person)]
        out[r.uid] = list(g.uid)
    return out


def regime_c_halves(persons, seed: int = 0) -> dict:
    """Deterministic half assignment from the learner id alone (no outcome, condition or quality)."""
    return {p: int(hashlib.sha256(f"{seed}:{p}".encode()).hexdigest(), 16) % 2 for p in sorted(set(persons))}


def regime_c_references(cells: pd.DataFrame, seed: int = 0) -> dict:
    half = regime_c_halves(cells.person, seed)
    out = {}
    for r in cells.itertuples():
        g = cells[(cells.experiment == r.experiment) & (cells.video == r.video) & (cells.person.map(half) != half[r.person])]
        out[r.uid] = list(g.uid)
    return out


def split_key(set_name: str, regime: str, train_persons, extra: str = "") -> str:
    blob = json.dumps(dict(set=set_name, regime=regime, train=sorted(train_persons), version=CHANNEL_VERSION,
                           extra=extra), sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()


# ----------------------------------------------------------------------------- split channels
@dataclass
class SplitChannels:
    """Standardized per-second channels of every cell of a set under one split (fold)."""

    key: str
    set_name: str
    regime: str
    train_persons: frozenset
    cell_uids: list
    videos: list                       # video per cell
    arrays: dict                       # video -> (n_cells_v, n_s_v, D) standardized (NaN kept)
    cell_index: dict                   # video -> list of global cell indices (order of arrays)
    mu: np.ndarray                     # standardization (training cells)
    sd: np.ndarray
    references: dict = field(repr=False, default_factory=dict)   # uid -> reference uids (audit)

    def detrended(self) -> dict:
        """Arrays with each cell's linear trend over the recording removed per channel (mean kept).
        Uses only the cell's own seconds, so it is fold-safe by construction (S1-D06)."""
        return {v: detrend(A) for v, A in self.arrays.items()}

    def cumsums(self, detrend_: bool = False):
        out = {}
        arrays = self.detrended() if detrend_ else self.arrays
        for v, A in arrays.items():
            ok = np.isfinite(A)
            c = np.concatenate([np.zeros((A.shape[0], 1, A.shape[2])), np.cumsum(np.where(ok, A, 0.0), axis=1)], axis=1)
            n = np.concatenate([np.zeros((A.shape[0], 1, A.shape[2])), np.cumsum(ok, axis=1)], axis=1)
            out[v] = (c, n)
        return out


def compute_split(inc: Incidence, train_persons, regime: str = "A", load=load_series, seed: int = 0,
                  cache: bool = True) -> SplitChannels:
    """Fold-safe channels for every cell of ``inc`` given the training learners of the split."""
    train_persons = frozenset(train_persons)
    key = split_key(inc.set_name, regime, train_persons, extra=str(seed) if regime == "C" else "")
    path = STAGE1_CACHE / f"{inc.set_name}_{regime}_{key[:20]}.npz"
    cells = inc.cells
    people = dict(zip(cells.uid, cells.person))
    refs = regime_a_references(cells, train_persons) if regime == "A" else regime_c_references(cells, seed)
    if cache and path.exists():
        z = np.load(path, allow_pickle=False)
        raw = {v: z[f"raw_{v}"] for v in inc.n_s}
    else:
        raw = {}
        for v, n_s in inc.n_s.items():
            cv = cells[cells.video == v]
            out = np.full((len(cv), n_s, len(PRIMARY)), np.nan)
            for i, r in enumerate(cv.itertuples()):
                a = load(r.uid)
                rf = ref_free_cell(a, n_s)
                ref_uids = refs[r.uid]
                if len(ref_uids) < 2:
                    raise ValueError(f"{r.uid}: fewer than 2 reference viewings")
                ref = reference_stats(ref_uids, people, n_s, exclude_person=r.person)
                rr = ref_rel_cell(a, ref, n_s)
                out[i] = np.column_stack([rf[:, 0], rf[:, 1], rr[:, 0], rr[:, 1], rf[:, 2], rf[:, 3]])
            raw[v] = out
        if cache:
            STAGE1_CACHE.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(path, **{f"raw_{v}": raw[v] for v in raw})
    # standardization from training cells only
    train_rows = []
    for v in inc.n_s:
        cv = cells[cells.video == v]
        m = cv.person.isin(train_persons).to_numpy()
        train_rows.append(raw[v][m].reshape(-1, len(PRIMARY)))
    T = np.vstack(train_rows)
    mu = np.nanmean(T, 0)
    sd = np.nanstd(T, 0)
    sd[~(sd > 0)] = 1.0
    arrays = {v: (raw[v] - mu) / sd for v in raw}
    cell_index = {v: list(np.flatnonzero((cells.video == v).to_numpy())) for v in inc.n_s}
    return SplitChannels(key, inc.set_name, regime, train_persons, list(cells.uid), list(cells.video), arrays,
                         cell_index, mu, sd, references=refs)


def detrend(A: np.ndarray) -> np.ndarray:
    """Remove the least-squares linear time trend of every (cell, channel) series in A (cells x s x D),
    over its finite seconds; the series mean is unchanged."""
    n_s = A.shape[1]
    t = (np.arange(n_s) - (n_s - 1) / 2.0)[None, :, None]
    ok = np.isfinite(A)
    Az = np.where(ok, A, 0.0)
    n = np.maximum(ok.sum(1, keepdims=True), 1)
    tb = (ok * t).sum(1, keepdims=True) / n
    xb = Az.sum(1, keepdims=True) / n
    tc = (t - tb) * ok
    den = (tc ** 2).sum(1, keepdims=True)
    b = np.where(den > 0, (tc * (Az - xb)).sum(1, keepdims=True) / np.where(den > 0, den, 1.0), 0.0)
    return A - b * (t - tb)


# ----------------------------------------------------------------------------- pooling
def window_bounds(start: np.ndarray, end: np.ndarray, n_s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Second indices [lo, hi) of a hard kernel: second t is inside iff t + 0.5 in [start, end)."""
    lo = np.clip(np.ceil(start - 0.5), 0, n_s - 1).astype(int)
    hi = np.clip(np.ceil(end - 0.5), 1, n_s).astype(int)
    hi = np.maximum(hi, lo + 1)
    return lo, hi


class Pooler:
    """Window means of standardized channels for the anchorable rows of an incidence, from cumulative
    sums (NaN-aware; NaN when observed coverage <= MIN_COVERAGE). Supports relocated and circularly
    shifted windows for the randomization nulls."""

    def __init__(self, inc: Incidence, sc: SplitChannels, detrend: bool = False):
        self.inc = inc
        self.detrend = detrend
        rows = inc.rows
        anch = rows[rows.anchorable]
        self.anch_index = np.flatnonzero(rows.anchorable.to_numpy())
        cell_pos = {u: i for i, u in enumerate(inc.cells.uid)}
        self.cell = anch.uid.map(cell_pos).to_numpy()
        self.video = anch.video.to_numpy()
        self.n_s = np.array([inc.n_s[v] for v in self.video])
        self.start = anch.start.to_numpy(float)
        self.end = anch.end.to_numpy(float)
        self.D = len(PRIMARY)
        cs = sc.cumsums(detrend_=detrend)
        # flatten per-video arrays into one padded array for vectorized gathers
        nmax = max(inc.n_s.values())
        n_cells = len(inc.cells)
        self.C = np.zeros((n_cells, nmax + 1, self.D))
        self.N = np.zeros((n_cells, nmax + 1, self.D))
        for v, (c, n) in cs.items():
            idx = sc.cell_index[v]
            self.C[idx, : c.shape[1]] = c
            self.N[idx, : n.shape[1]] = n
            self.C[idx, c.shape[1]:] = c[:, -1:]
            self.N[idx, n.shape[1]:] = n[:, -1:]
        self.cell_ns = inc.cells.video.map(inc.n_s).to_numpy()

    def _gather(self, lo, hi):
        if not hasattr(self, "_Cf"):
            self._stride = self.C.shape[1]
            self._Cf = self.C.reshape(-1, self.D)
            self._Nf = self.N.reshape(-1, self.D)
        base = self.cell * self._stride
        s = self._Cf[base + hi] - self._Cf[base + lo]
        n = self._Nf[base + hi] - self._Nf[base + lo]
        return s, n, (hi - lo)[:, None]

    def means(self, start=None, end=None, shift=None) -> np.ndarray:
        """Window means (n_anchorable x D). ``shift`` (per anchorable row, seconds) moves each window
        circularly on its recording (wrap-around)."""
        start = self.start if start is None else start
        end = self.end if end is None else end
        lo, hi = window_bounds(start, end, self.n_s)
        if shift is None:
            s, n, L = self._gather(lo, hi)
        else:
            L1 = hi - lo
            lo2 = (lo + shift.astype(int)) % self.n_s
            hi2 = lo2 + L1
            wrap = hi2 > self.n_s
            a_hi = np.where(wrap, self.n_s, hi2)
            s, n, _ = self._gather(lo2, a_hi)
            s2, n2, _ = self._gather(np.zeros_like(lo2), np.where(wrap, hi2 - self.n_s, 0))
            s, n = s + s2, n + n2
            L = L1[:, None]
        with np.errstate(invalid="ignore", divide="ignore"):
            out = np.where(n / L > MIN_COVERAGE, s / np.maximum(n, 1), np.nan)
        return out

    def whole_video(self) -> np.ndarray:
        """Whole-recording channel means per cell (n_cells x D)."""
        idx = np.arange(len(self.cell_ns))
        s = self.C[idx, self.cell_ns]
        n = self.N[idx, self.cell_ns]
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(n > 0, s / np.maximum(n, 1), np.nan)



def moment_centres(inc: Incidence) -> dict:
    rows = inc.rows[inc.rows.anchorable]
    return {k: float(((g.start + g.end) / 2).mean()) for k, g in rows.groupby(["video", "moment"])}



# ----------------------------------------------------------------------------- regressors
@dataclass
class MomentBlock:
    """Moment terms and person-path summaries of one split."""

    m: np.ndarray        # anchorable rows x D: z - e_bar (NaN where window coverage is low)
    z: np.ndarray        # anchorable rows x D
    ebar: np.ndarray     # cells x D whole-recording means
    eanch: np.ndarray    # cells x D mean of z over the cell's anchorable items


def moment_block(inc: Incidence, pooler: Pooler, start=None, end=None, shift=None) -> MomentBlock:
    z = pooler.means(start, end, shift)
    ebar = pooler.whole_video()
    m = z - ebar[pooler.cell]
    n_cells = len(inc.cells)
    s = np.zeros((n_cells, z.shape[1]))
    n = np.zeros((n_cells, z.shape[1]))
    ok = np.isfinite(z)
    np.add.at(s, pooler.cell, np.where(ok, z, 0.0))
    np.add.at(n, pooler.cell, ok)
    with np.errstate(invalid="ignore", divide="ignore"):
        eanch = np.where(n > 0, s / np.maximum(n, 1), np.nan)
    return MomentBlock(m, z, ebar, eanch)


def within_cell_centre(m: np.ndarray, cell: np.ndarray) -> np.ndarray:
    """Centre each channel within learner x video over the cell's anchorable items (NaN -> 0 after)."""
    ok = np.isfinite(m)
    n_cells = int(cell.max()) + 1 if len(cell) else 0
    out = np.zeros_like(m, dtype=float)
    for c in range(m.shape[1]):
        o = ok[:, c]
        s = np.bincount(cell, np.where(o, m[:, c], 0.0), n_cells)
        n = np.bincount(cell, o.astype(float), n_cells)
        out[:, c] = np.where(o, m[:, c] - (s / np.maximum(n, 1))[cell], 0.0)
    return out


def moment_regressors(m: np.ndarray, cell: np.ndarray, item: np.ndarray, train: np.ndarray,
                      return_stats: bool = False):
    """The moment regressor of plan §10, centred within learner x video and within item.

    Within-cell centring makes lambda a within-learner x video contrast (identification, plan §10);
    item means and the scale are fitted on training rows only (fold safety)."""
    x = within_cell_centre(m, cell)
    n_item = int(item.max()) + 1
    n = np.bincount(item[train], minlength=n_item).astype(float)
    mu = np.stack([np.bincount(item[train], x[train, c], n_item) for c in range(x.shape[1])], 1) / np.maximum(n, 1)[:, None]
    x = x - mu[item]
    sd = x[train].std(0)
    sd[~(sd > 0)] = 1.0
    x = x / sd
    return (x, dict(item_mean=mu, sd=sd)) if return_stats else x


def identity_probe(x: np.ndarray, label: np.ndarray, groups: np.ndarray, k: int = 5, n_perm: int = 99,
                   seed: int = 0) -> dict:
    """Held-out balanced accuracy of predicting ``label`` (video) from item-centred moment terms,
    learner-grouped, with a label-permutation 95% band (spec §3 test 8)."""
    from .stats import balanced_accuracy, group_kfold, softmax_fit, softmax_predict

    classes, y = np.unique(label, return_inverse=True)

    def score(yy):
        pred = np.zeros_like(yy)
        for tr, te in group_kfold(groups, k, seed):
            W = softmax_fit(x[tr], yy[tr], len(classes), l2=1.0)
            pred[te] = softmax_predict(W, x[te])
        return balanced_accuracy(yy, pred)

    obs = score(y)
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(n_perm):
        # permute labels between learners (whole learners keep their label vector)
        ug = np.unique(groups)
        pg = rng.permutation(ug)
        mp = dict(zip(ug, pg))
        idx = {g: np.flatnonzero(groups == g) for g in ug}
        yy = y.copy()
        for g in ug:
            src, dst = idx[mp[g]], idx[g]
            if len(src) == len(dst):
                yy[dst] = y[src]
        null.append(score(yy))
    hi = float(np.quantile(null, 0.95))
    return dict(balanced_accuracy=obs, chance=1 / len(classes), null_q95=hi, at_chance=bool(obs <= hi))


def fit_fold_encoder(sc: SplitChannels, cells: pd.DataFrame, K: int = 3):
    """Ablation A4: the label-free encoder, fitted on the split's **training** cells only (spec §3 test 4).
    The returned encoder records the learners it was fitted on."""
    from .encoder import LinearMaskedEncoder

    mats = [np.nan_to_num(A[i]) for v, A in sc.arrays.items() for i, ci in enumerate(sc.cell_index[v])
            if cells.person.iloc[ci] in sc.train_persons]
    enc = LinearMaskedEncoder(K=K).fit(mats)
    enc.fitted_on = frozenset(sc.train_persons)
    return enc
