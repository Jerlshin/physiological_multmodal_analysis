"""Explanatory companion model and shortcut diagnostic (ii) (evaluation contract §5).

* :func:`crossed_reml` fits y = X b + person intercept + content intercept + e by REML
  (profiled residual variance, two variance ratios). Labelled explanatory; fit once on the
  full analysis set; never presented as predictive evidence.
* :func:`identity_probe` measures held-out accuracy of predicting the experiment x video unit
  from the physiological features (person-grouped outer folds, ridge one-vs-rest, penalty by
  inner person-grouped CV), against the majority-class rate.
"""
from __future__ import annotations

import numpy as np
from scipy import optimize
from scipy.stats import norm

from .models import ridge_path


def crossed_reml(y: np.ndarray, X: np.ndarray, groups_a: np.ndarray, groups_b: np.ndarray, names=None) -> dict:
    n, p = X.shape
    Za = np.eye(int(groups_a.max()) + 1)[groups_a]
    Zb = np.eye(int(groups_b.max()) + 1)[groups_b]
    Ka, Kb = Za @ Za.T, Zb @ Zb.T
    I = np.eye(n)

    def parts(log_theta):
        ta, tb = np.exp(log_theta)
        V = I + ta * Ka + tb * Kb
        L = np.linalg.cholesky(V)
        Vi_X = np.linalg.solve(L.T, np.linalg.solve(L, X))
        Vi_y = np.linalg.solve(L.T, np.linalg.solve(L, y))
        XtViX = X.T @ Vi_X
        beta = np.linalg.solve(XtViX, X.T @ Vi_y)
        r = y - X @ beta
        Vi_r = np.linalg.solve(L.T, np.linalg.solve(L, r))
        sigma2 = float(r @ Vi_r) / (n - p)
        logdetV = 2 * np.log(np.diag(L)).sum()
        sign, logdetX = np.linalg.slogdet(XtViX)
        nll = 0.5 * ((n - p) * np.log(sigma2) + logdetV + logdetX)
        return nll, beta, sigma2, XtViX

    best = None
    for start in ([0.0, -1.0], [-2.0, -3.0], [1.0, 0.0]):
        res = optimize.minimize(lambda t: parts(t)[0], np.array(start), method="L-BFGS-B", bounds=[(-12, 6), (-12, 6)])
        if best is None or res.fun < best.fun:
            best = res
    nll, beta, sigma2, XtViX = parts(best.x)
    cov = sigma2 * np.linalg.inv(XtViX)
    se = np.sqrt(np.diag(cov))
    ta, tb = np.exp(best.x)
    names = names or [f"x{j}" for j in range(p)]
    z = beta / se
    return dict(
        converged=bool(best.success), reml_neg_loglik=float(nll),
        variance=dict(group_a=float(ta * sigma2), group_b=float(tb * sigma2), residual=float(sigma2)),
        fixed_effects=[dict(name=nm, estimate=float(b), se=float(s), wald_z=float(zz),
                            ci95=[float(b - 1.96 * s), float(b + 1.96 * s)], p_wald=float(2 * norm.sf(abs(zz))))
                       for nm, b, s, zz in zip(names, beta, se, z)],
        label="EXPLANATORY: in-sample crossed REML; not predictive evidence; Wald inference conditional on the model",
    )


def identity_probe(splits, label: np.ndarray, lam_rel: np.ndarray) -> dict:
    """``splits``: iterable of (train_idx, test_idx, X_all, inner_fold_of_train) with X_all the split's
    physiological design (cells x p, training-mean imputed). Ridge one-vs-rest on standardized X."""
    n_cls = int(label.max()) + 1
    Y = np.eye(n_cls)[label]
    correct = np.zeros(len(label))
    tested = np.zeros(len(label))
    n_splits = 0
    for tr, te, X, inner_fold in splits:
        Xtr, Xte, Ytr = X[tr], X[te], Y[tr]
        sse = np.zeros(len(lam_rel))
        for j in np.unique(inner_fold):
            a, b = inner_fold != j, inner_fold == j
            P = np.stack([ridge_path(Xtr[a], Ytr[a, c], Xtr[b], lam_rel * a.sum()) for c in range(n_cls)], axis=2)
            sse += ((P - Ytr[b][:, None, :]) ** 2).sum(axis=(0, 2))
        lam = lam_rel[int(np.argmin(sse))] * len(tr)
        P = np.stack([ridge_path(Xtr, Ytr[:, c], Xte, np.array([lam]))[:, 0] for c in range(n_cls)], axis=1)
        correct[te] += P.argmax(axis=1) == label[te]
        tested[te] += 1
        n_splits += 1
    m = tested > 0
    acc = float((correct[m] / tested[m]).mean())
    freq = np.bincount(label, minlength=n_cls) / len(label)
    return dict(accuracy=acc, majority_rate=float(freq.max()), chance_by_frequency=float((freq ** 2).sum()),
                n_classes=n_cls, splits=n_splits,
                label="DIAGNOSTIC: accuracy well above the majority rate means features carry content identity")
