"""Label-free engagement encoders f_phi (research plan §12.1) - Stage-0 linear version.

``LinearMaskedEncoder``: masked-centre reconstruction with a reduced-rank ridge map. For each
second t, the context u(t-k..t+k) with the centre second removed predicts u(t); the fitted map
is truncated to rank K and the K-dimensional bottleneck is the engagement state e(t). It is the
linear special case of the plan's masked-span TCN objective and needs no outcome.

``ReferenceDistiller``: predicts reference-relative channels from reference-free channels
(peer-free regime B), also label-free.

``RandomEncoder``: a random projection of the same context with the same output size - the
matched-noise control (ablation A4).

Every fitted statistic (standardization, ridge maps) comes from the matrices passed to ``fit``;
callers pass training-fold learners only.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


def context(U: np.ndarray, k: int, drop_centre: bool = True) -> np.ndarray:
    """Stack u(t-k..t+k) for every t (zero-padded at the edges); U is seconds x D (no NaN)."""
    T, D = U.shape
    P = np.vstack([np.zeros((k, D)), U, np.zeros((k, D))])
    cols = [P[k + o: k + o + T] for o in range(-k, k + 1) if not (drop_centre and o == 0)]
    return np.hstack(cols)


@dataclass
class Standardizer:
    mu: np.ndarray = None
    sd: np.ndarray = None

    def fit(self, mats: list[np.ndarray]):
        X = np.vstack(mats)
        self.mu = np.nanmean(X, 0)
        self.sd = np.nanstd(X, 0)
        self.sd[~(self.sd > 0)] = 1.0
        return self

    def transform(self, U: np.ndarray) -> np.ndarray:
        return np.nan_to_num((U - self.mu) / self.sd)


@dataclass
class LinearMaskedEncoder:
    K: int = 3
    k: int = 4
    alpha: float = 10.0
    std: Standardizer = field(default_factory=Standardizer)
    B: np.ndarray = None
    V: np.ndarray = None

    def fit(self, mats: list[np.ndarray]):
        self.std.fit(mats)
        Xs, Ys = [], []
        for U in mats:
            Z = self.std.transform(U)
            Xs.append(context(Z, self.k))
            Ys.append(Z)
        X, Y = np.vstack(Xs), np.vstack(Ys)
        self.B = np.linalg.solve(X.T @ X + self.alpha * np.eye(X.shape[1]), X.T @ Y)
        F = X @ self.B
        _, _, Vt = np.linalg.svd(F - F.mean(0), full_matrices=False)
        self.V = Vt[: self.K].T                              # D x K output directions
        return self

    def transform(self, U: np.ndarray) -> np.ndarray:
        return context(self.std.transform(U), self.k) @ self.B @ self.V

    def reconstruct(self, U: np.ndarray) -> np.ndarray:
        return self.transform(U) @ self.V.T

    def r2(self, U: np.ndarray) -> float:
        Z = self.std.transform(U)
        R = Z - self.reconstruct(U)
        return float(1 - (R ** 2).sum() / ((Z - Z.mean(0)) ** 2).sum())

    @property
    def n_params(self) -> int:
        return int(self.B.size + self.V.size)


@dataclass
class ReferenceDistiller:
    k: int = 4
    alpha: float = 10.0
    sx: Standardizer = field(default_factory=Standardizer)
    sy: Standardizer = field(default_factory=Standardizer)
    B: np.ndarray = None

    def fit(self, X_free: list[np.ndarray], Y_rel: list[np.ndarray]):
        self.sx.fit(X_free)
        self.sy.fit(Y_rel)
        X = np.vstack([context(self.sx.transform(x), self.k, drop_centre=False) for x in X_free])
        Y = np.vstack([self.sy.transform(y) for y in Y_rel])
        self.B = np.linalg.solve(X.T @ X + self.alpha * np.eye(X.shape[1]), X.T @ Y)
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        return context(self.sx.transform(x), self.k, drop_centre=False) @ self.B

    def r2(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        Y = self.sy.transform(y)
        R = Y - self.predict(x)
        return 1 - (R ** 2).sum(0) / ((Y - Y.mean(0)) ** 2).sum(0)


@dataclass
class RandomEncoder:
    D: int
    K: int = 3
    k: int = 4
    seed: int = 0
    std: Standardizer = field(default_factory=Standardizer)
    W: np.ndarray = None

    def fit(self, mats: list[np.ndarray]):
        self.std.fit(mats)
        rng = np.random.default_rng(self.seed)
        self.W = rng.standard_normal((2 * self.k * self.D, self.K)) / np.sqrt(2 * self.k * self.D)
        return self

    def transform(self, U: np.ndarray) -> np.ndarray:
        return context(self.std.transform(U), self.k) @ self.W
