"""Penalized Rasch-type GLMM shared by IRT-0, IRT-M2, IRT-whole and the CAIRN variants (plan §10, §12.2).

    logit P(y_pvj = 1) = alpha_g(v) + delta_j + u_p + F_pv' b + M_pvj' lambda

* ``alpha_g`` - video (x experiment) intercepts, essentially unpenalized;
* ``delta_j`` - item easiness deviation from its video mean, ridge 1 / sigma_beta^2 (the plan's
  shrinkage of beta_vj toward the video mean);
* ``u_p``     - learner random intercept, N(0, tau^2), mode found jointly (Laplace);
* ``F``       - person path (cell-level: recording quality Q; anchored engagement e_anch for CAIRN;
  whole-video engagement e_bar for IRT-whole), ridge ``r_f``;
* ``M``       - moment regressors (within learner x video and within item; :mod:`cairn.features`),
  ridge ``r_m``.

Variance components (tau^2, sigma_beta^2) are estimated by Laplace-EM on the **base** model (IRT-M2)
of each training fold and then held fixed for every model compared in that fold, including all
permutation refits. Observed and permuted fits are therefore computed by the identical,
deterministic procedure (Stage-1 decision S1-D04).

Prediction for a new learner integrates u_p out with the logistic-normal approximation
``expit(eta / sqrt(1 + c^2 tau^2))``, c = 16 sqrt(3) / (15 pi) (Zeger, Liang & Albert 1988). The plan's
§10 formula wrote Phi(eta / sqrt(1 + pi tau^2 / 8)); that mixes the probit and logit scales and is
corrected here (S1-D04).

The solver is a damped Newton method on the joint penalized log-likelihood with block-structured
Hessian assembly (items and learners are one-hot blocks), so a fit on ~3,000 responses takes
milliseconds. It is deterministic: same inputs, same floating-point result.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import cho_factor, cho_solve
from scipy.special import expit, log_expit
from scipy.sparse import csr_matrix

C2 = (16 * np.sqrt(3) / (15 * np.pi)) ** 2       # ~0.346
P_CLIP = 1e-6


@dataclass
class Params:
    a: np.ndarray        # item deviations (K)
    u: np.ndarray        # learner effects (P_train)
    b: np.ndarray        # dense coefficients (d)
    tau2: float
    sb2: float
    n_iter: int = 0
    converged: bool = True


class Fitter:
    """Training-fold structure (rows, item and learner indices) reused across many fits."""

    def __init__(self, item: np.ndarray, person: np.ndarray, K: int, P: int):
        self.k = np.asarray(item, np.int64)
        self.p = np.asarray(person, np.int64)
        self.K, self.P = K, P
        n = len(self.k)
        self.kp = self.k * P + self.p
        ones = np.ones(n)
        self.Ik_T = csr_matrix((ones, (self.k, np.arange(n))), shape=(K, n))
        self.Ip_T = csr_matrix((ones, (self.p, np.arange(n))), shape=(P, n))

    # ------------------------------------------------------------------ core Newton
    def _eta(self, D, a, u, b, offset):
        e = a[self.k] + u[self.p] + D @ b
        return e if offset is None else e + offset

    def newton(self, D: np.ndarray, y: np.ndarray, pen_d: np.ndarray, tau2: float, sb2: float, init: Params | None = None,
               offset: np.ndarray | None = None, tol: float = 1e-6, max_iter: int = 50, want_cov: bool = False):
        K, P, d = self.K, self.P, D.shape[1]
        a = np.zeros(K) if init is None else init.a.copy()
        u = np.zeros(P) if init is None else init.u.copy()
        b = np.zeros(d) if init is None else _fit_len(init.b, d)
        pk, pp = 1.0 / sb2, 1.0 / tau2

        def objective(a, u, b):
            eta = self._eta(D, a, u, b, offset)
            ll = np.sum(y * log_expit(eta) + (1 - y) * log_expit(-eta))
            return ll - 0.5 * (pk * a @ a + pp * u @ u + np.sum(pen_d * b * b))

        obj = None
        it, conv = 0, False
        for it in range(1, max_iter + 1):
            eta = self._eta(D, a, u, b, offset)
            mu = expit(eta)
            w = mu * (1 - mu)
            r = y - mu
            g = np.concatenate([np.bincount(self.k, r, K) - pk * a, np.bincount(self.p, r, P) - pp * u,
                                D.T @ r - pen_d * b])
            H = self._hessian(D, w, pk, pp, pen_d)
            step = cho_solve(cho_factor(H, lower=False, check_finite=False), g, check_finite=False)
            t = 1.0
            if np.max(np.abs(step)) > 1.0:            # far from the optimum: damped step (monotone ascent)
                obj = objective(a, u, b) if obj is None else obj
                while True:
                    o1 = objective(a + t * step[:K], u + t * step[K:K + P], b + t * step[K + P:])
                    if o1 >= obj - 1e-12 or t < 1e-4:
                        break
                    t *= 0.5
                obj = o1
            else:                                     # pure Newton step (concave objective, local quadratic convergence)
                obj = None
            a, u, b = a + t * step[:K], u + t * step[K:K + P], b + t * step[K + P:]
            if np.max(np.abs(t * step)) < tol:
                conv = True
                break
        out = Params(a, u, b, tau2, sb2, it, conv)
        if want_cov:
            eta = self._eta(D, a, u, b, offset)
            mu = expit(eta)
            H = self._hessian(D, mu * (1 - mu), pk, pp, pen_d)
            cov = cho_solve(cho_factor(H, check_finite=False), np.eye(H.shape[0]), check_finite=False)
            return out, cov
        return out

    def _hessian(self, D, w, pk, pp, pen_d):
        K, P, d = self.K, self.P, D.shape[1]
        WD = D * w[:, None]
        H = np.empty((K + P + d, K + P + d))
        H[:K, :K] = 0.0
        H[np.arange(K), np.arange(K)] = np.bincount(self.k, w, K) + pk
        H[K:K + P, K:K + P] = 0.0
        H[K + np.arange(P), K + np.arange(P)] = np.bincount(self.p, w, P) + pp
        Hkp = np.bincount(self.kp, w, K * P).reshape(K, P)
        H[:K, K:K + P] = Hkp
        H[K:K + P, :K] = Hkp.T
        Hkd = self.Ik_T @ WD
        Hpd = self.Ip_T @ WD
        H[:K, K + P:] = Hkd
        H[K + P:, :K] = Hkd.T
        H[K:K + P, K + P:] = Hpd
        H[K + P:, K:K + P] = Hpd.T
        H[K + P:, K + P:] = D.T @ WD
        H[K + P + np.arange(d), K + P + np.arange(d)] += pen_d
        return H

    # ------------------------------------------------------------------ variance components
    def fit_em(self, D, y, pen_d, tau2=1.0, sb2=1.0, n_em: int = 30, rtol: float = 1e-4, init: Params | None = None):
        """Laplace-EM for (tau^2, sigma_beta^2) on the given design; returns Params with the estimates."""
        prm = init
        K, P = self.K, self.P
        for _ in range(n_em):
            prm, cov = self.newton(D, y, pen_d, tau2, sb2, init=prm, want_cov=True)
            dv = np.diag(cov)
            sb2_new = float(np.mean(prm.a ** 2 + dv[:K]))
            tau2_new = float(np.mean(prm.u ** 2 + dv[K:K + P]))
            sb2_new, tau2_new = max(sb2_new, 1e-3), max(tau2_new, 1e-3)
            done = abs(sb2_new - sb2) / sb2 < rtol and abs(tau2_new - tau2) / tau2 < rtol
            sb2, tau2 = sb2_new, tau2_new
            if done:
                break
        prm = self.newton(D, y, pen_d, tau2, sb2, init=prm)
        return prm


def _fit_len(b: np.ndarray, d: int) -> np.ndarray:
    out = np.zeros(d)
    out[: min(d, len(b))] = b[: min(d, len(b))]
    return out


def predict_marginal(prm: Params, item: np.ndarray, D: np.ndarray, offset: np.ndarray | None = None) -> np.ndarray:
    """P(correct) for new learners (u_p integrated out)."""
    eta = prm.a[item] + D @ prm.b
    if offset is not None:
        eta = eta + offset
    p = expit(eta / np.sqrt(1.0 + C2 * prm.tau2))
    return np.clip(p, P_CLIP, 1 - P_CLIP)


def log_loss(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    p = np.clip(p, P_CLIP, 1 - P_CLIP)
    return -(y * np.log(p) + (1 - y) * np.log1p(-p))


def penalized_logistic(X: np.ndarray, y: np.ndarray, l2: np.ndarray, tol: float = 1e-9, max_iter: int = 50):
    """Plain penalized logistic regression with intercept in column 0 of X (used by B9 and the naive
    Wald reference). Returns (coef, covariance from the penalized Hessian)."""
    w = np.zeros(X.shape[1])
    for _ in range(max_iter):
        mu = expit(X @ w)
        g = X.T @ (y - mu) - l2 * w
        H = X.T @ (X * (mu * (1 - mu))[:, None]) + np.diag(l2)
        step = np.linalg.solve(H, g)
        w = w + step
        if np.max(np.abs(step)) < tol:
            break
    mu = expit(X @ w)
    H = X.T @ (X * (mu * (1 - mu))[:, None]) + np.diag(l2)
    return w, np.linalg.inv(H)
