"""Baseline ladder B0-B9 behind one interface (plan §16; Stage-1 spec §5).

    class ItemModel(Protocol):
        name: str
        def fit(self, train: ItemData, config: dict, rng) -> ItemModel
        def predict_proba(self, test: ItemData) -> np.ndarray      # P(correct) per (learner, item) row
        def n_params(self) -> int

``ItemData`` carries one split of a set: incidence, features (through the split) and **training
outcomes only** - its constructor refuses a split whose test rows carry outcomes. Video-level models
(B0 video mean, B1/B2 frozen G01-R ridge) predict a cell score that every item of the cell receives,
so item- and video-level metrics stay comparable.

Implemented in Stage 1 (numpy/scipy only): B0, B1/B2 (frozen ``g01r.models`` ridge on caller-supplied
video-level features), B5 (IRT-M2, IRT-whole), B6 (CAIRN-linear, raw or detrended), the frozen-direction
CAIRN-linear, B9 (Lalle-style pooled window classifier).
Not implementable without new packages (Stage-2 work after a user-authorized install into .venv-cairn):
B3 (elastic net / random forest / LightGBM / CatBoost / GPBoost / TabPFN v2), B4a (foundation-model
embeddings), B4b (attention-MIL), B7/B8 (TCN encoder variants). They raise :class:`MissingDependency`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import numpy as np
from scipy.special import expit

from . import features as F
from . import inference as I
from .model import Params, penalized_logistic, predict_marginal


class MissingDependency(RuntimeError):
    pass


@dataclass
class ItemData:
    S: I.SetStructure
    split: I.Split
    y: np.ndarray                  # outcomes on training rows; NaN on test rows
    video_features: np.ndarray | None = None   # cells x p (B1/B2 only)
    rows: np.ndarray = field(init=False)

    def __post_init__(self):
        if np.isfinite(self.y[self.split.test]).any():
            raise ValueError("ItemData must not carry outcomes of test rows")
        if not np.isfinite(self.y[self.split.train]).all():
            raise ValueError("training rows need outcomes")
        self.rows = np.flatnonzero(self.split.train)


class ItemModel(Protocol):
    name: str

    def fit(self, train: ItemData, config: dict, rng: np.random.Generator) -> "ItemModel": ...

    def predict_proba(self, test: ItemData) -> np.ndarray: ...

    def n_params(self) -> int: ...


# ----------------------------------------------------------------------------- B0
class VideoMean:
    name = "B0-video-mean"

    def fit(self, train, config=None, rng=None):
        S, sp = train.S, train.split
        g = S.group[sp.train]
        self.mean = np.bincount(g, train.y[sp.train], S.G.shape[1]) / np.maximum(np.bincount(g, minlength=S.G.shape[1]), 1)
        return self

    def predict_proba(self, test):
        return np.clip(self.mean[test.S.group[test.split.test]], 1e-6, 1 - 1e-6)

    def n_params(self):
        return len(self.mean)


class GLMM:
    """B0 IRT-0, B5 IRT-M2 / IRT-whole, B6 CAIRN-linear and its variants: one penalized Rasch GLMM."""

    def __init__(self, variant: I.Variant):
        self.variant = variant
        self.name = variant.name

    def fit(self, train, config=None, rng=None):
        S, sp, y = train.S, train.split, np.nan_to_num(train.y)
        D0, pen0 = I.design(S, sp, I.BASE)
        self.base = sp.fitter.fit_em(D0[sp.train], y[sp.train], pen0)
        if self.variant.name == I.BASE.name:
            self.prm, self.D = self.base, D0
        else:
            self.D, pen = I.design(S, sp, self.variant)
            self.prm = sp.fitter.newton(self.D[sp.train], y[sp.train], pen, self.base.tau2, self.base.sb2, init=self.base)
        return self

    def predict_proba(self, test):
        sp = test.split
        return predict_marginal(self.prm, test.S.item[sp.test], self.D[sp.test])

    def n_params(self):
        return int(self.D.shape[1] + len(self.prm.a) + 2)          # dense + item deviations + (tau2, sigma_beta2)


class IRT0(GLMM):
    """B0 IRT-0: video intercepts + item easiness + learner random effect; no person path."""

    def __init__(self):
        self.variant = None
        self.name = "B0-IRT-0"

    def fit(self, train, config=None, rng=None):
        S, sp, y = train.S, train.split, np.nan_to_num(train.y)
        self.D = S.G
        self.prm = sp.fitter.fit_em(self.D[sp.train], y[sp.train], np.full(S.G.shape[1], I.G_PEN))
        return self


class FrozenRidge:
    """B1 / B2: frozen G01-R ridge (``g01r.models.fit_predict``, inner person-grouped CV over the frozen grid)
    on video-level features supplied by the caller (``ItemData.video_features``)."""

    def __init__(self, name: str, lam_rel: np.ndarray | None = None):
        self.name = name
        self.lam_rel = lam_rel

    def fit(self, train, config=None, rng=None):
        from g01r import models as G
        S, sp = train.S, train.split
        if train.video_features is None:
            raise ValueError("B1/B2 need cell-level video features")
        cells_tr = np.unique(S.cell[sp.train])
        score = np.bincount(S.cell[sp.train], train.y[sp.train], len(S.inc.cells)) / np.maximum(
            np.bincount(S.cell[sp.train], minlength=len(S.inc.cells)), 1)
        self.cells_tr = cells_tr
        Xtr = train.video_features[cells_tr]
        cell_person = S.inc.cells.person.to_numpy()[cells_tr]
        _, inner = np.unique(cell_person, return_inverse=True)
        inner = inner % 5
        lam_rel = self.lam_rel if self.lam_rel is not None else np.logspace(-3, 3, 9)
        self._fit = (G, Xtr, score[cells_tr], inner, lam_rel)
        return self

    def predict_proba(self, test):
        G, Xtr, ytr, inner, lam_rel = self._fit
        S, sp = test.S, test.split
        cells_te = np.unique(S.cell[sp.test])
        pred, _ = G.fit_predict(Xtr, ytr, test.video_features[cells_te], inner, lam_rel)
        lut = dict(zip(cells_te, np.clip(pred, 1e-6, 1 - 1e-6)))
        return np.array([lut[c] for c in S.cell[sp.test]])

    def n_params(self):
        return int(self._fit[1].shape[1] + 1)


class LalleB9:
    """B9: reference-free gaze features in each item's window (whole video for non-anchorable items), item
    identity dropped, learner-grouped CV (N15), penalized logistic."""
    name = "B9-Lalle-pooled-window"

    def _X(self, data, rows):
        S, sp = data.S, data.split
        rf = [F.PRIMARY.index(c) for c in F.REF_FREE_USED]
        Xw = sp.mb.ebar[S.cell][:, rf].copy()
        Xw[S.anch_index] = np.where(np.isfinite(sp.mb.z[:, rf]), sp.mb.z[:, rf], Xw[S.anch_index])
        X = np.hstack([np.ones((S.n, 1)), np.nan_to_num(Xw), S.anch[:, None].astype(float)])
        return X[rows]

    def fit(self, train, config=None, rng=None):
        sp = train.split
        X = self._X(train, sp.train)
        self.w, _ = penalized_logistic(X, train.y[sp.train], np.r_[0.0, np.full(X.shape[1] - 1, 1.0)])
        return self

    def predict_proba(self, test):
        return np.clip(expit(self._X(test, test.split.test) @ self.w), 1e-6, 1 - 1e-6)

    def n_params(self):
        return len(self.w)


class _Unavailable:
    def __init__(self, name: str, needs: str):
        self.name, self.needs = name, needs

    def fit(self, *a, **k):
        raise MissingDependency(f"{self.name} needs {self.needs}; install into .venv-cairn (user-authorized download, Stage 2)")

    predict_proba = n_params = fit


def ladder(primary_form: str = "dt") -> dict:
    cl = I.CL6_DT if primary_form == "dt" else I.CL6
    return {
        "B0-video-mean": VideoMean(),
        "B0-IRT-0": IRT0(),
        "B1-M2 (frozen G01-R ridge)": FrozenRidge("B1-M2"),
        "B2-M-gaze/M3/M4 (frozen G01-R ridge)": FrozenRidge("B2"),
        "B3 (EN/RF/GBM/GPBoost/TabPFN)": _Unavailable("B3", "scikit-learn, lightgbm, catboost, gpboost, tabpfn"),
        "B4a (FM embeddings)": _Unavailable("B4a", "torch + model checkpoints"),
        "B4b (attention-MIL)": _Unavailable("B4b", "torch"),
        "B5-IRT-M2": GLMM(I.BASE),
        "B5-IRT-whole": GLMM(I.WHOLE),
        "B6-CAIRN-linear": GLMM(cl),
        "B7/B8 (TCN encoder variants)": _Unavailable("B7/B8", "torch"),
        "B9-Lalle": LalleB9(),
    }
