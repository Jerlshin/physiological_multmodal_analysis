"""Anchored pooling (research plan §10): z_pvj = sum_t kappa_vj(t) e_pv(t), moment term z - e_bar.

``kernel`` is ``"hard"`` (uniform over the anchor's recording span) or ``"gauss"`` (centre mu,
variance h^2 + omega^2 with an optional lag delta, as in the plan). Diffuse items get the
uniform whole-video kernel, so their moment term is zero by construction.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def kernel(n_s: int, start: float, end: float, kind: str = "hard", lag: float = 0.0, omega: float = 0.0) -> np.ndarray:
    t = np.arange(n_s) + 0.5
    if kind == "hard":
        k = ((t >= start + lag) & (t < end + lag)).astype(float)
    elif kind == "gauss":
        mu, h = (start + end) / 2 + lag, (end - start) / 2
        k = np.exp(-((t - mu) ** 2) / (2 * (h ** 2 + omega ** 2 + 1e-9)))
    else:
        raise ValueError(kind)
    s = k.sum()
    return k / s if s > 0 else np.full(n_s, 1.0 / n_s)


def pooled(E: np.ndarray, K: np.ndarray) -> np.ndarray:
    """E: seconds x channels (NaN allowed); K: items x seconds (rows sum to 1).
    NaN-aware: kernel weights are renormalized over observed seconds per channel."""
    obs = np.isfinite(E)
    Ez = np.where(obs, E, 0.0)
    num = K @ Ez
    den = K @ obs.astype(float)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0.25, num / den, np.nan)


def anchored_moment_terms(E: np.ndarray, anchors: pd.DataFrame, kind: str = "hard", lag: float = 0.0) -> np.ndarray:
    """z_pvj - e_bar_pv for every anchor row (columns rec_start_s, rec_end_s, localized)."""
    n_s = E.shape[0]
    K = np.vstack([kernel(n_s, r.rec_start_s, r.rec_end_s, kind, lag) if r.localized else np.full(n_s, 1.0 / n_s)
                   for r in anchors.itertuples()])
    z = pooled(E, K)
    ebar = np.nanmean(E, axis=0)
    return z - ebar[None, :]
