"""Small, dependency-free statistics used by Stage 0/1 (numpy/scipy only; the frozen
environment has no scikit-learn): additive two-way decomposition, Spearman-Brown, AUC,
L2 logistic and multinomial regression, grouped K-fold splits."""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, log_softmax


def two_way(M: np.ndarray, iters: int = 20):
    """Additive fit M[p, t] ~ mu + a_p + b_t on observed cells (NaN = missing).
    Returns (mu, a, b, residual) with residual NaN where M is NaN."""
    obs = np.isfinite(M)
    mu = np.nanmean(M)
    a = np.zeros(M.shape[0])
    b = np.zeros(M.shape[1])
    for _ in range(iters):
        with np.errstate(invalid="ignore"):
            a = np.nanmean(np.where(obs, M - mu - b[None, :], np.nan), axis=1)
            a = np.nan_to_num(a - np.nanmean(a))
            b = np.nanmean(np.where(obs, M - mu - a[:, None], np.nan), axis=0)
            b = np.nan_to_num(b - np.nanmean(b))
    res = np.where(obs, M - mu - a[:, None] - b[None, :], np.nan)
    return mu, a, b, res


def variance_shares(M: np.ndarray) -> dict:
    """Shares of person, moment and person x moment variance (fitted values on observed cells)."""
    mu, a, b, res = two_way(M)
    obs = np.isfinite(M)
    pa = np.broadcast_to(a[:, None], M.shape)[obs]
    pb = np.broadcast_to(b[None, :], M.shape)[obs]
    r = res[obs]
    tot = pa.var() + pb.var() + r.var()
    lag1 = np.nan
    if M.shape[1] > 2:
        x, y = res[:, :-1].ravel(), res[:, 1:].ravel()
        ok = np.isfinite(x) & np.isfinite(y)
        if ok.sum() > 10:
            lag1 = float(np.corrcoef(x[ok], y[ok])[0, 1])
    return dict(person=pa.var() / tot, moment=pb.var() / tot, residual=r.var() / tot, resid_lag1=lag1, n_cells=int(obs.sum()))


def spearman_brown(r: float, k: float = 2.0) -> float:
    return k * r / (1 + (k - 1) * r) if np.isfinite(r) and r > -1 / (k - 1) else np.nan


def auc(y: np.ndarray, s: np.ndarray) -> float:
    y = np.asarray(y).astype(bool)
    s = np.asarray(s, float)
    pos, neg = s[y], s[~y]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    from scipy.stats import rankdata
    r = rankdata(np.concatenate([pos, neg]))
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def group_kfold(groups: np.ndarray, k: int, seed: int = 0):
    """Deterministic grouped K-fold: every member of a group falls in one fold."""
    ug = np.unique(groups)
    rng = np.random.default_rng(seed)
    rng.shuffle(ug)
    fold_of = {g: i % k for i, g in enumerate(ug)}
    f = np.array([fold_of[g] for g in groups])
    for i in range(k):
        yield np.flatnonzero(f != i), np.flatnonzero(f == i)


def standardize(train: np.ndarray, *others):
    mu = np.nanmean(train, 0)
    sd = np.nanstd(train, 0)
    sd[~(sd > 0)] = 1.0
    out = [np.nan_to_num((train - mu) / sd)]
    out += [np.nan_to_num((o - mu) / sd) for o in others]
    return out


def logistic_fit(X: np.ndarray, y: np.ndarray, l2: float = 1.0) -> np.ndarray:
    X1 = np.hstack([np.ones((len(X), 1)), X])

    def f(w):
        z = X1 @ w
        nll = np.sum(np.logaddexp(0, z) - y * z)
        g = X1.T @ (expit(z) - y)
        pen = 0.5 * l2 * np.sum(w[1:] ** 2)
        gp = np.r_[0.0, l2 * w[1:]]
        return nll + pen, g + gp

    return minimize(f, np.zeros(X1.shape[1]), jac=True, method="L-BFGS-B").x


def logistic_predict(w: np.ndarray, X: np.ndarray) -> np.ndarray:
    return expit(np.hstack([np.ones((len(X), 1)), X]) @ w)


def softmax_fit(X: np.ndarray, y: np.ndarray, n_class: int, l2: float = 1.0) -> np.ndarray:
    X1 = np.hstack([np.ones((len(X), 1)), X])
    Y = np.eye(n_class)[y]
    d = X1.shape[1]

    def f(wf):
        W = wf.reshape(d, n_class)
        L = log_softmax(X1 @ W, axis=1)
        nll = -np.sum(Y * L)
        P = np.exp(L)
        G = X1.T @ (P - Y)
        G[1:] += l2 * W[1:]
        return nll + 0.5 * l2 * np.sum(W[1:] ** 2), G.ravel()

    return minimize(f, np.zeros(d * n_class), jac=True, method="L-BFGS-B").x.reshape(d, n_class)


def softmax_predict(W: np.ndarray, X: np.ndarray) -> np.ndarray:
    return np.argmax(np.hstack([np.ones((len(X), 1)), X]) @ W, axis=1)


def balanced_accuracy(y: np.ndarray, yhat: np.ndarray) -> float:
    cls = np.unique(y)
    return float(np.mean([(yhat[y == c] == c).mean() for c in cls]))
