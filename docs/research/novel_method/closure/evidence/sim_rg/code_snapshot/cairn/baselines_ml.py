"""Strong modern baselines B3, B4a, B4b and B7 behind the ``ItemModel`` interface (plan §16; closure rule R-K).

Imported only in ``.venv-cairn-ml`` (torch, scikit-learn, LightGBM, CatBoost, GPBoost, TabPFN v2, Mantis,
sentence-transformers; ``requirements-cairn-ml.lock``). The CAIRN primary and every confirmatory computation stay
in ``.venv-cairn`` (frozen numerical stack); these baselines never enter NH1.

Every model fits on the **training rows of one split** (``ItemData`` refuses test-row outcomes) and uses only
fold-safe inputs:

* per-second channels from :func:`cairn.features.compute_split` (regime-A references and standardization from the
  split's training learners);
* whole-video summary features computed per recording from those channels (no cross-recording fitting);
* foundation-model embeddings computed per recording / per window by frozen pretrained networks; their PCA,
  scaling and every downstream fit use training rows only;
* item-text <-> transcript relevance from item texts and public transcripts only (no learner data);
* label-free encoder pretraining on the training learners' channels only.

Item-level use of video-level learners (B3, B4a-video, B4b-video) is by **cross-fitted stacking into IRT-M2**:
the learner's cross-fitted cell-score prediction enters the IRT-M2 person path as one more column, so item
easiness is kept and item-level metrics are comparable with CAIRN. The plain video-level prediction (every item of
a cell receives the predicted score, as B1/B2) is also available (``mode="video"``).
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
from scipy.special import expit, logit

from . import features as F
from . import inference as I
from .baselines import ItemData
from .model import predict_marginal

SEED = 20261014
INNER_K = 5
_SC_CACHE: dict = {}


# ----------------------------------------------------------------------------- determinism
def torch_deterministic(seed: int = SEED):
    import torch
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(int(os.environ.get("CAIRN_TORCH_THREADS", "1")))


# ----------------------------------------------------------------------------- fold-safe inputs
def split_channels(S: I.SetStructure, sp: I.Split) -> F.SplitChannels:
    """The split's standardized per-second channels (cached on disk by split identity; memoized here)."""
    key = (S.inc.set_name, sp.train_persons)
    if key not in _SC_CACHE:
        if len(_SC_CACHE) > 40:
            _SC_CACHE.clear()
        _SC_CACHE[key] = F.compute_split(S.inc, sp.train_persons)
    return _SC_CACHE[key]


def cell_series(S: I.SetStructure, sp: I.Split) -> list:
    """Per cell (order of ``S.inc.cells``): (n_s x D) standardized channels, NaN kept."""
    sc = split_channels(S, sp)
    out = [None] * len(S.inc.cells)
    for v, A in sc.arrays.items():
        for i, ci in enumerate(sc.cell_index[v]):
            out[ci] = A[i]
    return out


FEATURE_STATS = ("mean", "sd", "q10", "q50", "q90", "ac1", "slope", "sd10")


def whole_video_features(S: I.SetStructure, sp: I.Split) -> tuple[np.ndarray, list]:
    """Whole-recording summaries per cell: for each of the six primary channels mean, SD, 10/50/90% quantiles,
    lag-1 autocorrelation, linear slope and SD of 10-s block means (48 features), plus the recording invalid
    fraction. Per-recording computations only; NaN -> training-cell median at fit time."""
    series = cell_series(S, sp)
    X = np.full((len(series), len(F.PRIMARY) * len(FEATURE_STATS) + 1), np.nan)
    for c, A in enumerate(series):
        n_s = A.shape[0]
        t = np.linspace(-1, 1, n_s)
        row = []
        for d in range(A.shape[1]):
            a = A[:, d]
            ok = np.isfinite(a)
            if ok.sum() < 10:
                row += [np.nan] * len(FEATURE_STATS)
                continue
            av = a[ok]
            q10, q50, q90 = np.quantile(av, [.1, .5, .9])
            a0 = np.where(ok, a - av.mean(), 0.0)
            ac = (a0[1:] * a0[:-1]).sum() / max((a0 ** 2).sum(), 1e-12)
            slope = np.polyfit(t[ok], av, 1)[0]
            nb = n_s // 10
            blocks = [np.nanmean(a[i * 10:(i + 1) * 10]) for i in range(nb) if np.isfinite(a[i * 10:(i + 1) * 10]).any()]
            row += [av.mean(), av.std(), q10, q50, q90, ac, slope, np.std(blocks) if len(blocks) > 1 else np.nan]
        X[c, :-1] = row
    X[:, -1] = S.q_raw
    names = [f"{ch}_{st}" for ch in F.PRIMARY for st in FEATURE_STATS] + ["invalid_fraction"]
    return X, names


def impute_scale(X: np.ndarray, train_rows: np.ndarray) -> np.ndarray:
    """Median imputation and standardization with training-row statistics only."""
    med = np.nanmedian(X[train_rows], 0)
    med = np.where(np.isfinite(med), med, 0.0)
    Z = np.where(np.isfinite(X), X, med)
    mu, sd = Z[train_rows].mean(0), Z[train_rows].std(0)
    return (Z - mu) / np.where(sd > 0, sd, 1.0)


def cell_targets(S: I.SetStructure, y: np.ndarray, rows: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per cell: mean correctness and number of items over ``rows`` (training rows)."""
    k = np.bincount(S.cell[rows], y[rows], len(S.inc.cells))
    n = np.bincount(S.cell[rows], minlength=len(S.inc.cells)).astype(float)
    return k / np.maximum(n, 1), n


def inner_folds(persons: np.ndarray, k: int = INNER_K, seed: int = SEED) -> np.ndarray:
    """Deterministic learner-grouped fold id per element of ``persons``."""
    ups = np.array(sorted(set(persons)))
    rng = np.random.default_rng(seed)
    rng.shuffle(ups)
    f = {p: i % k for i, p in enumerate(ups)}
    return np.array([f[p] for p in persons])


# ----------------------------------------------------------------------------- cell-level learners (B3, B4)
class CellModel:
    """A regressor of the cell score (proportion correct) from cell features; ``fit(X, y, w, groups)``."""
    name = "cell"
    n_configs = 1

    def fit(self, X, y, w, groups):
        raise NotImplementedError

    def predict(self, X):
        raise NotImplementedError

    def n_params(self) -> int:
        return 0


def _inner_select(make, configs, X, y, w, groups):
    """Pick the configuration with the lowest inner learner-grouped weighted squared error."""
    if len(configs) == 1:
        return configs[0]
    fid = inner_folds(groups)
    best, best_err = None, np.inf
    for cfg in configs:
        err = 0.0
        for k in range(INNER_K):
            tr, te = fid != k, fid == k
            if te.sum() == 0 or tr.sum() < 5:
                continue
            m = make(cfg).fit(X[tr], y[tr], w[tr], groups[tr])
            err += float(np.sum(w[te] * (m.predict(X[te]) - y[te]) ** 2))
        if err < best_err:
            best, best_err = cfg, err
    return best


class ElasticNetCell(CellModel):
    name = "B3-elastic-net"
    CONFIGS = [dict(alpha=a, l1_ratio=r) for a in (0.003, 0.03, 0.3) for r in (0.1, 0.5, 0.9)]
    n_configs = len(CONFIGS)

    def __init__(self, cfg=None):
        self.cfg = cfg

    def fit(self, X, y, w, groups):
        from sklearn.linear_model import ElasticNet
        cfg = self.cfg or _inner_select(lambda c: ElasticNetCell(c), self.CONFIGS, X, y, w, groups)
        self.cfg = cfg
        self.m = ElasticNet(alpha=cfg["alpha"], l1_ratio=cfg["l1_ratio"], max_iter=20000).fit(X, y, sample_weight=w)
        return self

    def predict(self, X):
        return self.m.predict(X)

    def n_params(self):
        return int(np.sum(self.m.coef_ != 0) + 1)


class RandomForestCell(CellModel):
    name = "B3-random-forest"

    def __init__(self, cfg=None):
        self.cfg = cfg or dict(n_estimators=500, min_samples_leaf=5, max_features="sqrt")

    def fit(self, X, y, w, groups):
        from sklearn.ensemble import RandomForestRegressor
        self.m = RandomForestRegressor(random_state=SEED, n_jobs=1, **self.cfg).fit(X, y, sample_weight=w)
        return self

    def predict(self, X):
        return self.m.predict(X)

    def n_params(self):
        return int(sum(t.tree_.node_count for t in self.m.estimators_))


class LightGBMCell(CellModel):
    name = "B3-lightgbm"
    CONFIGS = [dict(num_leaves=nl, learning_rate=lr, n_estimators=ne) for nl in (4, 8) for lr in (0.03, 0.1)
               for ne in (100, 300)]
    n_configs = len(CONFIGS)

    def __init__(self, cfg=None):
        self.cfg = cfg

    def fit(self, X, y, w, groups):
        import lightgbm as lgb
        cfg = self.cfg or _inner_select(lambda c: LightGBMCell(c), self.CONFIGS, X, y, w, groups)
        self.cfg = cfg
        self.m = lgb.LGBMRegressor(min_child_samples=10, subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
                                   reg_lambda=1.0, random_state=SEED, n_jobs=1, verbose=-1, deterministic=True,
                                   force_row_wise=True, **cfg).fit(X, y, sample_weight=w)
        return self

    def predict(self, X):
        return self.m.predict(X)

    def n_params(self):
        return int(self.m.booster_.num_trees() * (2 * self.cfg["num_leaves"] - 1))


class CatBoostCell(CellModel):
    name = "B3-catboost"
    CONFIGS = [dict(depth=d, learning_rate=lr) for d in (2, 4) for lr in (0.03, 0.1)]
    n_configs = len(CONFIGS)

    def __init__(self, cfg=None):
        self.cfg = cfg

    def fit(self, X, y, w, groups):
        from catboost import CatBoostRegressor
        cfg = self.cfg or _inner_select(lambda c: CatBoostCell(c), self.CONFIGS, X, y, w, groups)
        self.cfg = cfg
        self.m = CatBoostRegressor(iterations=300, l2_leaf_reg=3.0, random_seed=SEED, verbose=False, thread_count=1,
                                   allow_writing_files=False, **cfg).fit(X, y, sample_weight=w)
        return self

    def predict(self, X):
        return self.m.predict(X)

    def n_params(self):
        return int(self.m.tree_count_ * 2 ** self.cfg["depth"])


class GPBoostCell(CellModel):
    """Tree boosting with a learner random effect (Sigrist 2022): cell scores are repeated measures of learners."""
    name = "B3-gpboost"
    CONFIGS = [dict(num_leaves=nl, learning_rate=lr) for nl in (4, 8) for lr in (0.03, 0.1)]
    n_configs = len(CONFIGS)

    def __init__(self, cfg=None):
        self.cfg = cfg

    def fit(self, X, y, w, groups):
        import gpboost as gpb
        cfg = self.cfg or _inner_select(lambda c: GPBoostCell(c), self.CONFIGS, X, y, w, groups)
        self.cfg = cfg
        gp = gpb.GPModel(group_data=np.asarray(groups).astype(str), likelihood="gaussian", seed=SEED,
                         weights=np.asarray(w, float))
        ds = gpb.Dataset(X, y)
        params = dict(objective="regression_l2", min_data_in_leaf=10, verbose=-1, num_threads=1, seed=SEED,
                      deterministic=True, **cfg)
        self.m = gpb.train(params=params, train_set=ds, gp_model=gp, num_boost_round=150, verbose_eval=False)
        self.gp = gp
        return self

    def predict(self, X):
        # new learners: random effect at its prior mean (0); fixed-effect (tree) part only
        p = self.m.predict(data=X, group_data_pred=np.array(["__new__"] * len(X)), predict_var=False, pred_latent=True)
        return np.asarray(p["fixed_effect"]) + np.asarray(p["random_effect_mean"])

    def n_params(self):
        return int(self.m.num_trees() * (2 * self.cfg["num_leaves"] - 1) + 2)


class TabPFNCell(CellModel):
    """TabPFN v2 regressor (Hollmann et al., Nature 2025; Apache-2.0 weights with attribution). In-context
    learning, no tuning. Later TabPFN versions are gated behind a non-commercial licence only the user can accept."""
    name = "B3-tabpfn-v2"

    def fit(self, X, y, w, groups):
        from tabpfn import TabPFNRegressor
        from tabpfn.constants import ModelVersion
        self.m = TabPFNRegressor.create_default_for_version(ModelVersion.V2, device="cpu", random_state=SEED,
                                                            n_estimators=8)
        self.m.fit(X, y)
        return self

    def predict(self, X):
        return self.m.predict(X)

    def n_params(self):
        return 0                                   # in-context; pretrained weights fixed (~7M, not fitted here)


class RidgeCell(CellModel):
    """Ridge on cell features (used on foundation-model embedding components); inner-CV ridge from 9 values."""
    name = "ridge"
    CONFIGS = [dict(alpha=a) for a in np.logspace(-2, 4, 9)]
    n_configs = len(CONFIGS)

    def __init__(self, cfg=None):
        self.cfg = cfg

    def fit(self, X, y, w, groups):
        from sklearn.linear_model import Ridge
        cfg = self.cfg or _inner_select(lambda c: RidgeCell(c), self.CONFIGS, X, y, w, groups)
        self.cfg = cfg
        self.m = Ridge(alpha=cfg["alpha"]).fit(X, y, sample_weight=w)
        return self

    def predict(self, X):
        return self.m.predict(X)

    def n_params(self):
        return int(len(self.m.coef_) + 1)


# ----------------------------------------------------------------------------- stacking into IRT-M2
def _irt_fit_with_columns(S, sp, y, extra: np.ndarray | None, ridge: float = I.R_F):
    """IRT-M2 (variance components by Laplace-EM on the base) plus extra row-level columns (ridge ``ridge``)."""
    D0, pen0 = I.design(S, sp, I.BASE)
    base = sp.fitter.fit_em(D0[sp.train], y[sp.train], pen0)
    if extra is None:
        return base, D0
    D = np.hstack([D0, extra])
    pen = np.r_[pen0, np.full(extra.shape[1], ridge)]
    prm = sp.fitter.newton(D[sp.train], y[sp.train], pen, base.tau2, base.sb2, init=base)
    return prm, D


class VideoLevelBaseline:
    """A cell-score learner used (a) at video level (``mode="video"``: every item of a cell gets the predicted cell
    score) or (b) stacked into IRT-M2 (``mode="stacked"``: the cross-fitted logit of the predicted cell score is
    one more person-path column)."""

    def __init__(self, cell_model_factory, features, name: str, mode: str = "stacked", scale: bool = True):
        self.factory, self.features, self.mode, self.scale = cell_model_factory, features, mode, scale
        self.name = f"{name}{'' if mode == 'stacked' else ' (video level)'}"

    def _cell_pred(self, S, sp, y):
        X, _ = self.features(S, sp)
        tr_cells = np.flatnonzero(sp.cell_train)
        Xs = impute_scale(X, tr_cells) if self.scale else X
        score, n = cell_targets(S, y, np.flatnonzero(sp.train))
        persons = S.inc.cells.person.to_numpy()
        # cross-fitted predictions for training cells; full-training fit for the other cells
        oof = np.full(len(X), np.nan)
        fid = inner_folds(persons[tr_cells])
        for k in range(INNER_K):
            a, b = tr_cells[fid != k], tr_cells[fid == k]
            m = self.factory().fit(Xs[a], score[a], n[a], persons[a])
            oof[b] = m.predict(Xs[b])
        full = self.factory().fit(Xs[tr_cells], score[tr_cells], n[tr_cells], persons[tr_cells])
        self.cell_model = full
        pred = full.predict(Xs)
        pred[tr_cells] = oof[tr_cells]
        return np.clip(pred, 0.02, 0.98)

    def fit(self, train: ItemData, config=None, rng=None):
        S, sp = train.S, train.split
        y = np.nan_to_num(train.y)
        self.cell_pred = self._cell_pred(S, sp, y)
        if self.mode == "stacked":
            col = logit(self.cell_pred)[S.cell][:, None]
            mu, sd = col[sp.train].mean(), col[sp.train].std()
            self.prm, self.D = _irt_fit_with_columns(S, sp, y, (col - mu) / (sd if sd > 0 else 1.0))
        return self

    def predict_proba(self, test: ItemData):
        S, sp = test.S, test.split
        if self.mode == "video":
            return np.clip(self.cell_pred[S.cell[sp.test]], 1e-6, 1 - 1e-6)
        return predict_marginal(self.prm, S.item[sp.test], self.D[sp.test])

    def n_params(self):
        return int(self.cell_model.n_params() + (self.D.shape[1] + len(self.prm.a) + 2 if self.mode == "stacked" else 0))


# ----------------------------------------------------------------------------- B3-item: boosting on item rows
def item_features(S: I.SetStructure, sp: I.Split) -> np.ndarray:
    """Row features: whole-video summaries of the cell (49), the anchored window means minus the cell's whole-video
    means for the six channels (NaN for non-anchorable items), the anchorable flag, quiz and anchor position."""
    Xc, _ = whole_video_features(S, sp)
    mb = sp.mb if sp.mb is not None else sp.any_block
    m = np.full((S.n, len(F.PRIMARY)), np.nan)
    m[S.anch_index] = mb.m
    rows = S.inc.rows
    return np.column_stack([Xc[S.cell], m, S.anch.astype(float), rows.quiz_pos.to_numpy(float),
                            np.nan_to_num(rows.anchor_pos.to_numpy(float), nan=-1.0)])


class IRTBoostResidual:
    """B3-item: LightGBM on item rows boosted from the IRT-M2 marginal logit (``init_score``), with the cell's
    whole-video features and the item's anchored-window features. A flexible, non-linear competitor that sees the
    same anchored information as CAIRN-linear but no Rasch moment structure."""
    name = "B3-item-lightgbm-residual"
    CONFIGS = [dict(num_leaves=nl, learning_rate=lr, n_estimators=ne) for nl in (4, 8) for lr in (0.02, 0.05)
               for ne in (100, 300)]

    def fit(self, train: ItemData, config=None, rng=None):
        import lightgbm as lgb
        S, sp = train.S, train.split
        y = np.nan_to_num(train.y)
        self.base, D0 = _irt_fit_with_columns(S, sp, y, None)
        off = logit(predict_marginal(self.base, S.item, D0))
        X = item_features(S, sp)
        tr = np.flatnonzero(sp.train)
        persons = S.person[tr]
        fid = inner_folds(persons)

        def make(cfg):
            return lgb.LGBMClassifier(min_child_samples=20, subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
                                      reg_lambda=5.0, random_state=SEED, n_jobs=1, verbose=-1, deterministic=True,
                                      force_row_wise=True, **cfg)

        best, best_ll = None, np.inf
        for cfg in self.CONFIGS:
            ll = 0.0
            for k in range(INNER_K):
                a, b = tr[fid != k], tr[fid == k]
                m = make(cfg).fit(X[a], y[a], init_score=off[a])
                p = np.clip(expit(m.predict(X[b], raw_score=True) + off[b]), 1e-6, 1 - 1e-6)
                ll -= float(np.sum(y[b] * np.log(p) + (1 - y[b]) * np.log1p(-p)))
            if ll < best_ll:
                best, best_ll = cfg, ll
        self.cfg = best
        self.m = make(best).fit(X[tr], y[tr], init_score=off[tr])
        self._X, self._off = X, off
        return self

    def predict_proba(self, test: ItemData):
        te = np.flatnonzero(test.split.test)
        return np.clip(expit(self.m.predict(self._X[te], raw_score=True) + self._off[te]), 1e-6, 1 - 1e-6)

    def n_params(self):
        return int(self.m.booster_.num_trees() * (2 * self.cfg["num_leaves"] - 1))


class GPBoostItem:
    """B3-item-RE: tree boosting with crossed learner and item random effects on item rows (binary, Laplace),
    same row features as :class:`IRTBoostResidual`. New learners get the learner effect's prior mean."""
    name = "B3-item-gpboost-crossed-RE"

    def fit(self, train: ItemData, config=None, rng=None):
        import gpboost as gpb
        S, sp = train.S, train.split
        y = np.nan_to_num(train.y)
        X = np.nan_to_num(item_features(S, sp), nan=-9.0)
        tr = np.flatnonzero(sp.train)
        grp = np.column_stack([S.person.astype(str), S.item.astype(str)])
        gp = gpb.GPModel(group_data=grp[tr], likelihood="bernoulli_logit", seed=SEED)
        params = dict(objective="binary", num_leaves=4, learning_rate=0.05, min_data_in_leaf=20, verbose=-1,
                      num_threads=1, seed=SEED, deterministic=True)
        self.m = gpb.train(params=params, train_set=gpb.Dataset(X[tr], y[tr]), gp_model=gp, num_boost_round=100,
                           verbose_eval=False)
        self._X, self._grp = X, grp
        return self

    def predict_proba(self, test: ItemData):
        te = np.flatnonzero(test.split.test)
        grp = self._grp[te].copy()
        grp[:, 0] = "__new__"                       # held-out learners are new
        p = self.m.predict(data=self._X[te], group_data_pred=grp, predict_var=True, pred_latent=False)
        return np.clip(np.asarray(p["response_mean"]), 1e-6, 1 - 1e-6)

    def n_params(self):
        return int(self.m.num_trees() * 7 + 2)


# ----------------------------------------------------------------------------- GLMM with a custom moment block
class GLMMCustomMoment:
    """CAIRN's Rasch head with a moment block computed by ``moment_fn(S, sp) -> (m_anch (n_anch x k), e_anch
    (cells x k))``: within-cell and within-item centring and training-row scaling exactly as CAIRN-linear
    (:func:`cairn.features.moment_regressors`), isotropic ridge 100, anchored summary in the person path. Used for
    the foundation-model front end (B4a-anchored, ablation A4-FM) and the TCN encoder (B7)."""

    def __init__(self, name: str, moment_fn):
        self.name, self.moment_fn = name, moment_fn

    def fit(self, train: ItemData, config=None, rng=None):
        S, sp = train.S, train.split
        y = np.nan_to_num(train.y)
        m, e = self.moment_fn(S, sp)
        x = F.moment_regressors(m, S.anch_cell, S.anch_item, sp.anch_train)
        mc = np.zeros((S.n, x.shape[1]))
        mc[S.anch_index] = x
        pc = I._std_cells(e, sp.cell_train)[S.cell]
        D0, pen0 = I.design(S, sp, I.BASE)
        base = sp.fitter.fit_em(D0[sp.train], y[sp.train], pen0)
        self.D = np.hstack([D0, pc, mc])
        pen = np.r_[pen0, np.full(pc.shape[1], I.R_F), np.full(mc.shape[1], I.R_M_MULTI)]
        self.prm = sp.fitter.newton(self.D[sp.train], y[sp.train], pen, base.tau2, base.sb2, init=base)
        return self

    def predict_proba(self, test: ItemData):
        sp = test.split
        return predict_marginal(self.prm, test.S.item[sp.test], self.D[sp.test])

    def n_params(self):
        return int(self.D.shape[1] + len(self.prm.a) + 2)


def _window_bounds(S: I.SetStructure):
    rows = S.inc.rows
    anch = rows[rows.anchorable]
    n_s = np.array([S.inc.n_s[v] for v in anch.video])
    return F.window_bounds(anch.start.to_numpy(float), anch.end.to_numpy(float), n_s)


# ----------------------------------------------------------------------------- B4a: Mantis embeddings
FM_LEN = 512
FM_PCS = 8


def _resample(a: np.ndarray, n: int = FM_LEN) -> np.ndarray:
    """Linear interpolation of a (possibly NaN-containing) series to n points; NaN -> series mean (0 if none)."""
    ok = np.isfinite(a)
    fill = a[ok].mean() if ok.any() else 0.0
    a = np.where(ok, a, fill)
    if len(a) == 1:
        return np.full(n, a[0])
    return np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a)


class MantisEmbedder:
    """Frozen Mantis-8M (Feofanov et al., ICML 2026) or MantisV2 (2026) embeddings: each channel of a recording or
    of an anchored window is resampled to 512 points and embedded separately (256 dims), channels concatenated."""

    def __init__(self, version: str = "v2"):
        self.version = version
        self._net = None
        self._cache: dict = {}

    def net(self):
        if self._net is None:
            import torch
            from mantis.architecture import Mantis8M, MantisV2
            torch_deterministic()
            cls, rid = (MantisV2, "paris-noah/MantisV2") if self.version == "v2" else (Mantis8M, "paris-noah/Mantis-8M")
            self._net = cls(device="cpu").from_pretrained(rid)
            self._net.eval()
        return self._net

    def embed(self, segs: list) -> np.ndarray:
        """segs: list of (L_i x D) arrays -> (n x D*256)."""
        import torch
        X = np.stack([np.stack([_resample(s[:, d]) for d in range(s.shape[1])]) for s in segs]).astype(np.float32)
        n, D, L = X.shape
        out = []
        with torch.no_grad():
            flat = torch.from_numpy(X.reshape(n * D, 1, L))
            for i in range(0, len(flat), 512):
                out.append(self.net()(flat[i:i + 512]).numpy())
        return np.concatenate(out).reshape(n, D * 256)

    def split_embeddings(self, S: I.SetStructure, sp: I.Split) -> tuple[np.ndarray, np.ndarray]:
        """(whole-recording embeddings per cell, anchored-window embeddings per anchorable row) for one split."""
        key = (S.inc.set_name, sp.train_persons, self.version)
        if key not in self._cache:
            if len(self._cache) > 20:
                self._cache.clear()
            series = cell_series(S, sp)
            whole = self.embed(series)
            lo, hi = _window_bounds(S)
            wins = [series[c][a:b] for c, a, b in zip(S.anch_cell, lo, hi)]
            self._cache[key] = (whole, self.embed(wins))
        return self._cache[key]


class MomentEmbedder(MantisEmbedder):
    """Frozen MOMENT-1-small (Goswami et al., ICML 2024; AutonLab/MOMENT-1-small, 35M parameters) embeddings, 512 dims
    per channel (``momentfm`` installed without its dependency pins; verified on the frozen stack)."""

    def __init__(self):
        super().__init__(version="moment-small")

    def net(self):
        if self._net is None:
            from momentfm import MOMENTPipeline
            torch_deterministic()
            self._net = MOMENTPipeline.from_pretrained("AutonLab/MOMENT-1-small", model_kwargs={"task_name": "embedding"})
            self._net.init()
            self._net.eval()
        return self._net

    def embed(self, segs: list) -> np.ndarray:
        import torch
        X = np.stack([np.stack([_resample(s[:, d]) for d in range(s.shape[1])]) for s in segs]).astype(np.float32)
        n, D, L = X.shape
        out = []
        with torch.no_grad():
            flat = torch.from_numpy(X.reshape(n * D, 1, L))
            for i in range(0, len(flat), 256):
                out.append(self.net()(x_enc=flat[i:i + 256]).embeddings.numpy())
        return np.concatenate(out).reshape(n, -1)


def _pca_fit(Z: np.ndarray, rows: np.ndarray, k: int = FM_PCS):
    mu = Z[rows].mean(0)
    sd = Z[rows].std(0)
    sd = np.where(sd > 0, sd, 1.0)
    Zs = (Z[rows] - mu) / sd
    _, _, vt = np.linalg.svd(Zs, full_matrices=False)
    return mu, sd, vt[:k].T


def mantis_video_features(embedder: MantisEmbedder):
    def f(S, sp):
        whole, _ = embedder.split_embeddings(S, sp)
        mu, sd, V = _pca_fit(whole, np.flatnonzero(sp.cell_train))
        return ((whole - mu) / sd) @ V, [f"pc{i}" for i in range(V.shape[1])]
    return f


def mantis_moment_fn(embedder: MantisEmbedder):
    """FM front end for the anchored moment block: training-fitted PCA of the window embeddings; the moment term
    is the window's components minus the cell's whole-recording components (projected on the same PCA)."""
    def f(S, sp):
        whole, win = embedder.split_embeddings(S, sp)
        mu, sd, V = _pca_fit(win, np.flatnonzero(sp.anch_train))
        zw = ((win - mu) / sd) @ V
        zc = ((whole - mu) / sd) @ V
        m = zw - zc[S.anch_cell]
        e = np.zeros((len(S.inc.cells), V.shape[1]))
        cnt = np.bincount(S.anch_cell, minlength=len(S.inc.cells))[:, None]
        np.add.at(e, S.anch_cell, zw)
        return m, np.where(cnt > 0, e / np.maximum(cnt, 1), np.nan)
    return f


# ----------------------------------------------------------------------------- sequence tensors
def padded(series: list) -> tuple[np.ndarray, np.ndarray]:
    """(cells x Tmax x 2D) inputs [values with NaN -> 0 | availability] and a (cells x Tmax) length mask."""
    T = max(a.shape[0] for a in series)
    D = series[0].shape[1]
    X = np.zeros((len(series), T, 2 * D), np.float32)
    L = np.zeros((len(series), T), bool)
    for i, a in enumerate(series):
        ok = np.isfinite(a)
        X[i, : a.shape[0], :D] = np.where(ok, a, 0.0)
        X[i, : a.shape[0], D:] = ok
        L[i, : a.shape[0]] = True
    return X, L


# ----------------------------------------------------------------------------- B4b: gated-attention MIL (video level)
class AttentionMILCell(CellModel):
    """Gated-attention MIL (Ilse, Tomczak & Welling 2018) over the per-second channels of a recording: unconstrained
    learned temporal pooling with the cell score as the bag label (binomial likelihood). Fixed configuration
    (hidden 16, attention 8, weight decay 1e-2, 150 full-batch Adam epochs), 3-seed ensemble."""
    name = "B4b-attention-MIL"

    def __init__(self, X3: np.ndarray, L: np.ndarray, hidden: int = 16, att: int = 8, epochs: int = 150,
                 wd: float = 1e-2, seeds=(0, 1, 2)):
        self.X3, self.L, self.hidden, self.att, self.epochs, self.wd, self.seeds = X3, L, hidden, att, epochs, wd, seeds

    def _net(self):
        import torch.nn as nn
        D = self.X3.shape[2]

        class Net(nn.Module):
            def __init__(s):
                super().__init__()
                s.enc = nn.Sequential(nn.Linear(D, self.hidden), nn.ReLU(), nn.Linear(self.hidden, self.hidden), nn.ReLU())
                s.V = nn.Linear(self.hidden, self.att)
                s.U = nn.Linear(self.hidden, self.att)
                s.w = nn.Linear(self.att, 1)
                s.head = nn.Linear(self.hidden, 1)

            def forward(s, x, mask):
                import torch
                h = s.enc(x)
                a = s.w(torch.tanh(s.V(h)) * torch.sigmoid(s.U(h))).squeeze(-1)
                a = a.masked_fill(~mask, -1e9).softmax(-1)
                return s.head((a.unsqueeze(-1) * h).sum(1)).squeeze(-1)
        return Net()

    def fit(self, X, y, w, groups):
        import torch
        idx = X[:, 0].astype(int)
        x, m = torch.from_numpy(self.X3[idx]), torch.from_numpy(self.L[idx])
        k = torch.tensor(y * w, dtype=torch.float32)
        n = torch.tensor(w, dtype=torch.float32)
        self.nets = []
        for sd in self.seeds:
            torch_deterministic(SEED + sd)
            net = self._net()
            opt = torch.optim.Adam(net.parameters(), lr=3e-3, weight_decay=self.wd)
            for _ in range(self.epochs):
                opt.zero_grad()
                z = net(x, m)
                loss = -(k * torch.nn.functional.logsigmoid(z) + (n - k) * torch.nn.functional.logsigmoid(-z)).sum() / n.sum()
                loss.backward()
                opt.step()
            net.eval()
            self.nets.append(net)
        return self

    def predict(self, X):
        import torch
        idx = X[:, 0].astype(int)
        x, m = torch.from_numpy(self.X3[idx]), torch.from_numpy(self.L[idx])
        with torch.no_grad():
            return np.mean([torch.sigmoid(net(x, m)).numpy() for net in self.nets], 0)

    def n_params(self):
        return int(sum(p.numel() for p in self.nets[0].parameters()) * len(self.nets))


def mil_video_baseline(mode: str = "stacked") -> "VideoLevelBaseline":
    """B4b video-level MIL; the split's sequences are bound at fit time."""
    holder = {}

    def features(S, sp):
        X3, L = padded(cell_series(S, sp))
        holder["X3"], holder["L"] = X3, L
        return np.arange(len(S.inc.cells), dtype=float)[:, None], ["cell"]

    return VideoLevelBaseline(lambda: AttentionMILCell(holder["X3"], holder["L"]), features, "B4b-attention-MIL",
                              mode=mode, scale=False)


# ----------------------------------------------------------------------------- B4b: text-conditioned item attention
_REL_CACHE: dict = {}


def item_text(it) -> str:
    keyed = list(it.options)[: int(it.k_keyed)]
    return f"{it.question} {' '.join(map(str, keyed))}"


def text_relevance(S: I.SetStructure, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> np.ndarray:
    """(items x Tmax) relevance of each second's transcript cue to each item text (cosine similarity of
    sentence embeddings, z-scored per item over the seconds that carry speech; NaN where no cue lies within 3 s).
    Uses item texts (question + keyed options, as the outcome-blind anchoring raters did) and public transcripts
    on the recording clock; no learner data. Computed once per set (it is fold-independent)."""
    key = S.inc.set_name
    if key in _REL_CACHE:
        return _REL_CACHE[key]
    import pandas as pd
    from sentence_transformers import SentenceTransformer

    from .anchors import item_bank
    from .paths import STIMULI

    enc = SentenceTransformer(model_name, device="cpu")
    bank = item_bank().set_index(["canonical_video_id", "item"])
    rows = S.inc.rows.drop_duplicates("item_key")
    kidx = {k: i for i, k in enumerate(sorted(S.inc.rows.item_key.unique()))}
    Tmax = max(S.inc.n_s.values())
    R = np.full((len(kidx), Tmax), np.nan, np.float32)
    for v, g in rows.groupby("video"):
        n_s = S.inc.n_s[v]
        tr = pd.read_csv(STIMULI / "transcripts" / f"{v}.csv")
        tr = tr[tr.shown & tr.rec_start_s.notna()].reset_index(drop=True)
        ce = enc.encode(list(tr.text), normalize_embeddings=True, show_progress_bar=False)
        cue_at = np.full(n_s, -1)
        mid = ((tr.rec_start_s + tr.rec_end_s) / 2).to_numpy()
        for t in range(n_s):
            inside = np.flatnonzero((tr.rec_start_s.to_numpy() <= t + 0.5) & (t + 0.5 < tr.rec_end_s.to_numpy()))
            if len(inside):
                cue_at[t] = inside[0]
            else:
                d = np.abs(mid - (t + 0.5))
                if d.min() <= 3.0:
                    cue_at[t] = int(np.argmin(d))
        texts = [item_text(bank.loc[(v, int(j))]) for j in g.item]
        ie = enc.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        sim = ie @ ce.T                                  # items x cues
        for r_i, k in enumerate(g.item_key):
            r = np.where(cue_at >= 0, sim[r_i, np.maximum(cue_at, 0)], np.nan)
            ok = np.isfinite(r)
            r[ok] = (r[ok] - r[ok].mean()) / (r[ok].std() + 1e-6)
            R[kidx[k], :n_s] = r
    _REL_CACHE[key] = R
    return R


class TextAttentionMIL:
    """B4b-item: **learned, text-conditioned anchoring** (the deep competitor to outcome-blind human anchors).

    For row (cell c, item j): attention over the recording's seconds alpha_j(t) = softmax_t(beta * r_j(t)) with
    r_j the item-text <-> transcript relevance and beta >= 0 learned (initialized at 3, no weight decay);
    engagement h_c(t) = MLP(channels) in R^4; pooled z_cj = sum_t alpha_j(t) h_c(t). As in CAIRN's identification,
    the pooled term is centred within the cell (minus mean_t h_c) and within the item (minus its training-row mean).
    logit P = IRT-M2 offset_j + w'(centred z_cj) + v' mean_t h_c, where the fold's IRT-M2 marginal logit supplies
    item easiness and the person path. The number of epochs (25..400) is chosen on an inner learner-grouped 20%
    validation split; then the model is refit on all training rows. Adam lr 3e-2; 3-seed ensemble. Two declared
    configurations: MLP engagement map (hidden 8 -> 4 features, weight decay 1e-3) and a linear map (2 features,
    weight decay 1e-2; ``linear=True``), which isolates learned text-conditioned anchoring from the engagement map.
    Configurations were fixed on synthetic outcomes (closure smoke tests); real-data tuning is the inner epoch choice."""
    name = "B4b-item-text-attention-MIL"
    EPOCH_GRID = tuple(range(25, 401, 25))

    def __init__(self, hidden: int = 8, k: int = 4, wd: float = 1e-3, seeds=(0, 1, 2), epochs: int | None = None,
                 linear: bool = False, lr: float = 3e-2):
        self.hidden, self.k, self.wd, self.seeds, self.epochs, self.linear, self.lr = hidden, k, wd, seeds, epochs, linear, lr
        if linear:
            self.name = "B4b-item-text-attention-linear"

    def _net(self, D):
        import torch
        import torch.nn as nn
        hidden, k, linear = self.hidden, self.k, self.linear

        class Net(nn.Module):
            def __init__(s):
                super().__init__()
                s.enc = nn.Linear(D, k) if linear else nn.Sequential(nn.Linear(D, hidden), nn.ReLU(), nn.Linear(hidden, k))
                s.beta_raw = nn.Parameter(torch.tensor(2.9489))      # softplus -> 3.0: attend to text-matched seconds
                s.w = nn.Linear(k, 1, bias=False)
                s.v = nn.Linear(k, 1, bias=False)

            def pooled(s, t, rows):
                h = s.enc(t["X3"])                                  # cells x T x k
                Lf = t["L"].unsqueeze(-1).float()
                hm = (h * Lf).sum(1) / Lf.sum(1)
                cell, item = t["cell"][rows], t["item"][rows]
                beta = torch.nn.functional.softplus(s.beta_raw)
                rel = t["R"][item]
                ok = torch.isfinite(rel) & t["L"][cell]
                a = (beta * torch.nan_to_num(rel, nan=0.0)).masked_fill(~ok, -1e9)
                none = ok.sum(1) == 0                               # no speech: uniform over the recording
                a = torch.where(none.unsqueeze(1), torch.zeros_like(a).masked_fill(~t["L"][cell], -1e9), a)
                z = torch.einsum("rt,rtk->rk", a.softmax(-1), h[cell]) - hm[cell]
                return z, hm[cell], item

            def forward(s, t, rows, ref_rows):
                z, hm, item = s.pooled(t, rows)
                zr, _, item_r = s.pooled(t, ref_rows)               # item means from the reference (training) rows
                K = int(t["n_items"])
                sums = torch.zeros(K, zr.shape[1]).index_add(0, item_r, zr)
                cnt = torch.zeros(K).index_add(0, item_r, torch.ones(len(item_r))).clamp(min=1).unsqueeze(1)
                zc = z - (sums / cnt)[item]
                return t["off"][rows] + s.w(zc).squeeze(-1) + s.v(hm).squeeze(-1)
        return Net()

    def _train(self, D, rows, ref_rows, yt, epochs, seed, eval_rows=None):
        import torch
        torch_deterministic(SEED + seed)
        net = self._net(D)
        decay = [p for n, p in net.named_parameters() if n != "beta_raw"]
        opt = torch.optim.Adam([dict(params=decay, weight_decay=self.wd), dict(params=[net.beta_raw], weight_decay=0.0)],
                               lr=self.lr)
        curve = []
        for e in range(1, epochs + 1):
            opt.zero_grad()
            loss = torch.nn.functional.binary_cross_entropy_with_logits(net(self.t, rows, ref_rows), yt[rows])
            loss.backward()
            opt.step()
            if eval_rows is not None and e in self.EPOCH_GRID:
                with torch.no_grad():
                    curve.append(float(torch.nn.functional.binary_cross_entropy_with_logits(
                        net(self.t, eval_rows, rows), yt[eval_rows])))
        net.eval()
        return net, curve

    def fit(self, train: ItemData, config=None, rng=None):
        import torch
        S, sp = train.S, train.split
        y = np.nan_to_num(train.y)
        self.base, D0 = _irt_fit_with_columns(S, sp, y, None)
        off = logit(predict_marginal(self.base, S.item, D0)).astype(np.float32)
        X3, L = padded(cell_series(S, sp))
        R = text_relevance(S)[:, : X3.shape[1]]
        self.t = dict(X3=torch.from_numpy(X3), L=torch.from_numpy(L), R=torch.from_numpy(R), n_items=int(S.item.max()) + 1,
                      cell=torch.from_numpy(S.cell), item=torch.from_numpy(S.item), off=torch.from_numpy(off))
        tr = np.flatnonzero(sp.train)
        yt = torch.tensor(y, dtype=torch.float32)
        if self.epochs is None:                              # inner learner-grouped validation for the epoch count
            fid = inner_folds(S.person[tr])
            a, b = torch.from_numpy(tr[fid != 0]), torch.from_numpy(tr[fid == 0])
            _, curve = self._train(X3.shape[2], a, a, yt, max(self.EPOCH_GRID), self.seeds[0], eval_rows=b)
            self.epochs_ = self.EPOCH_GRID[int(np.argmin(curve))]
        else:
            self.epochs_ = self.epochs
        trt = torch.from_numpy(tr)
        self.tr = trt
        self.nets = [self._train(X3.shape[2], trt, trt, yt, self.epochs_, sd)[0] for sd in self.seeds]
        return self

    def predict_proba(self, test: ItemData):
        import torch
        te = torch.from_numpy(np.flatnonzero(test.split.test))
        with torch.no_grad():
            p = np.mean([torch.sigmoid(net(self.t, te, self.tr)).numpy() for net in self.nets], 0)
        return np.clip(p, 1e-6, 1 - 1e-6)

    def beta(self) -> float:
        import torch
        return float(np.mean([torch.nn.functional.softplus(n.beta_raw).item() for n in self.nets]))

    def n_params(self):
        return int(sum(p.numel() for p in self.nets[0].parameters()) * len(self.nets) + len(self.base.a) + 2)


# ----------------------------------------------------------------------------- B7: TCN encoder (label-free)
class TCNEncoder:
    """Label-free temporal convolutional encoder (plan §9/§12.1; ablation A4): two dilated 1-D convolutions (kernel 5,
    receptive field 9 s) to K = 3 features, pretrained by masked-span reconstruction (20% of seconds in spans of
    3-8 s) on the split's **training learners'** recordings only. ~2.4k parameters."""

    def __init__(self, K: int = 3, epochs: int = 150, seed: int = 0):
        self.K, self.epochs, self.seed = K, epochs, seed

    def fit(self, X3: np.ndarray, L: np.ndarray, train_cells: np.ndarray):
        import torch
        import torch.nn as nn
        torch_deterministic(SEED + self.seed)
        D2 = X3.shape[2]
        D = D2 // 2
        self.enc = nn.Sequential(nn.Conv1d(D2, 16, 5, padding=2), nn.ReLU(), nn.Conv1d(16, 16, 5, padding=2), nn.ReLU(),
                                 nn.Conv1d(16, self.K, 1))
        self.dec = nn.Conv1d(self.K, D, 1)
        x = torch.from_numpy(X3[train_cells]).transpose(1, 2)        # n x 2D x T
        lm = torch.from_numpy(L[train_cells])
        g = np.random.default_rng(SEED + self.seed)
        opt = torch.optim.Adam(list(self.enc.parameters()) + list(self.dec.parameters()), lr=3e-3, weight_decay=1e-4)
        for _ in range(self.epochs):
            mask = np.zeros(lm.shape, bool)
            for i in range(lm.shape[0]):
                T = int(lm[i].sum())
                while mask[i, :T].mean() < 0.2:
                    a = g.integers(0, max(T - 3, 1))
                    mask[i, a: a + g.integers(3, 9)] = True
            mt = torch.from_numpy(mask & L[train_cells])
            xin = x.clone()
            xin[:, :, :][mt.unsqueeze(1).expand(-1, D2, -1)] = 0.0
            rec = self.dec(self.enc(xin))                                 # n x D x T
            obs = x[:, D:, :] > 0
            sel = obs & mt.unsqueeze(1)
            loss = ((rec - x[:, :D, :]) ** 2)[sel].mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
        self.fitted_on = frozenset(int(c) for c in train_cells)
        return self

    def transform(self, X3: np.ndarray) -> np.ndarray:
        import torch
        with torch.no_grad():
            return self.enc(torch.from_numpy(X3).transpose(1, 2)).transpose(1, 2).numpy()

    def n_params(self) -> int:
        return int(sum(p.numel() for p in self.enc.parameters()) + sum(p.numel() for p in self.dec.parameters()))


def tcn_moment_fn(store: dict | None = None):
    """B7: TCN features e(t) pooled in the hard anchor windows; moment term = window mean - recording mean."""
    def f(S, sp):
        X3, L = padded(cell_series(S, sp))
        enc = TCNEncoder().fit(X3, L, np.flatnonzero(sp.cell_train))
        if store is not None:
            store["encoder"] = enc
        E = enc.transform(X3)
        lo, hi = _window_bounds(S)
        n_s = np.array([S.inc.n_s[v] for v in S.inc.cells.video])
        whole = np.stack([E[c, : n_s[c]].mean(0) for c in range(len(n_s))])
        z = np.stack([E[c, a:b].mean(0) for c, a, b in zip(S.anch_cell, lo, hi)])
        e = np.zeros_like(whole)
        cnt = np.bincount(S.anch_cell, minlength=len(n_s))[:, None]
        np.add.at(e, S.anch_cell, z)
        return z - whole[S.anch_cell], np.where(cnt > 0, e / np.maximum(cnt, 1), np.nan)
    return f


# ----------------------------------------------------------------------------- ladder
def ml_ladder(include_slow: bool = True) -> dict:
    """The closure baselines (name -> ItemModel). Video-level learners appear stacked into IRT-M2 (item level)."""
    wv = whole_video_features
    lad = {
        "B3-elastic-net": VideoLevelBaseline(ElasticNetCell, wv, "B3-elastic-net"),
        "B3-random-forest": VideoLevelBaseline(RandomForestCell, wv, "B3-random-forest"),
        "B3-lightgbm": VideoLevelBaseline(LightGBMCell, wv, "B3-lightgbm"),
        "B3-catboost": VideoLevelBaseline(CatBoostCell, wv, "B3-catboost"),
        "B3-gpboost": VideoLevelBaseline(GPBoostCell, wv, "B3-gpboost"),
        "B3-tabpfn-v2": VideoLevelBaseline(TabPFNCell, wv, "B3-tabpfn-v2"),
        "B3-item-lightgbm-residual": IRTBoostResidual(),
        "B3-item-gpboost-crossed-RE": GPBoostItem(),
    }
    if include_slow:
        emb = MantisEmbedder("v2")
        emb8 = MantisEmbedder("8m")
        embm = MomentEmbedder()
        lad.update({
            "B4a-mantisv2-video": VideoLevelBaseline(RidgeCell, mantis_video_features(emb), "B4a-mantisv2-video"),
            "B4a-mantisv2-anchored (A4-FM)": GLMMCustomMoment("B4a-mantisv2-anchored", mantis_moment_fn(emb)),
            "B4a-mantis8m-anchored (A4-FM)": GLMMCustomMoment("B4a-mantis8m-anchored", mantis_moment_fn(emb8)),
            "B4a-moment-video": VideoLevelBaseline(RidgeCell, mantis_video_features(embm), "B4a-moment-video"),
            "B4a-moment-anchored (A4-FM)": GLMMCustomMoment("B4a-moment-anchored", mantis_moment_fn(embm)),
            "B4b-attention-MIL": mil_video_baseline(),
            "B4b-item-text-attention-MIL": TextAttentionMIL(),
            "B4b-item-text-attention-linear": TextAttentionMIL(linear=True, k=2, wd=1e-2),
            "B7-TCN-encoder (A4)": GLMMCustomMoment("B7-TCN-encoder", tcn_moment_fn()),
        })
    return lad
