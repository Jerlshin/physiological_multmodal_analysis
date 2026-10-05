"""Prespecified baseline families and the ridge learner (protocol §8-§9; evaluation contract §5).

No other learner and no model search exist in this module. A model is a list of feature
blocks; the learner is ridge regression on standardized inputs, fitted to the residual of
the outcome from its training content effect, with the penalty chosen by person-grouped
inner 5-fold CV over the frozen 13-value grid.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ModelSpec:
    name: str
    blocks: tuple
    role: str = ""


PHYS_RF = ("RF_EEG", "RF_ECG", "RF_GAZE")
PHYS_SYN = ("SYN_EEG", "SYN_ECG", "SYN_GAZE")

FAMILY = {
    "M0": ModelSpec("M0", (), "content effect only (reference floor)"),
    "M1": ModelSpec("M1", ("C",), "+ admissible covariates"),
    "M2": ModelSpec("M2", ("C", "Q"), "primary baseline: nonsignal information + quality"),
    "M3": ModelSpec("M3", ("C", "Q") + PHYS_RF, "+ reference-free physiology"),
    "M4": ModelSpec("M4", ("C", "Q") + PHYS_SYN, "+ synchrony only"),
    "M5": ModelSpec("M5", ("C", "Q") + PHYS_RF + PHYS_SYN, "primary full model"),
    "M_EEG": ModelSpec("M_EEG", ("C", "Q", "RF_EEG", "SYN_EEG"), "H2b"),
    "M_ECG": ModelSpec("M_ECG", ("C", "Q", "RF_ECG", "SYN_ECG"), "H2c"),
    "M_GAZE": ModelSpec("M_GAZE", ("C", "Q", "RF_GAZE", "SYN_GAZE"), "H2d"),
    "M5_PUPIL": ModelSpec("M5_PUPIL", ("C", "Q") + PHYS_RF + PHYS_SYN + ("RF_PUPIL", "SYN_PUPIL"), "secondary pupil block"),
    # Regime B: reference-free only (no statistic from any other recording of the held-out video).
    "M5_B": ModelSpec("M5_B", ("C", "Q") + PHYS_RF, "regime B full model"),
    # Shortcut diagnostics (descriptive).
    "M0_Q": ModelSpec("M0_Q", ("Q",), "quality-only shortcut diagnostic"),
    "M2_NOISE": ModelSpec("M2_NOISE", ("C", "Q", "NOISE"), "matched random-feature control"),
    # E1 ocular-only regime A.
    "M5_E1": ModelSpec("M5_E1", ("C", "Q", "RF_GAZE", "SYN_GAZE"), "E1 ocular full model"),
}


def standardize(Xtr: np.ndarray, Xte: np.ndarray, min_sd: float = 1e-12):
    mx = Xtr.mean(axis=0)
    sx = Xtr.std(axis=0)
    sx = np.where(sx < min_sd, 1.0, sx)
    return (Xtr - mx) / sx, (Xte - mx) / sx


def ridge_path(Xtr: np.ndarray, ytr: np.ndarray, Xte: np.ndarray, lams: np.ndarray, min_sd: float = 1e-12) -> np.ndarray:
    """Predictions for every penalty in ``lams`` (n_te x n_lam). Inputs standardized with training
    mean/SD, unpenalized intercept = training mean of y. Solved via SVD of the standardized design."""
    my = ytr.mean()
    if Xtr.shape[1] == 0:
        return np.full((len(Xte), len(lams)), my)
    Ztr, Zte = standardize(Xtr, Xte, min_sd)
    U, s, Vt = np.linalg.svd(Ztr, full_matrices=False)
    F = s[:, None] / (s[:, None] ** 2 + lams[None, :])
    B = Vt.T @ (F * (U.T @ (ytr - my))[:, None])
    return my + Zte @ B


def choose_lambda(Xtr, ytr, inner_fold: np.ndarray, lam_rel: np.ndarray, min_sd: float = 1e-12) -> float:
    """Inner person-grouped CV: penalty minimizing summed squared error over the frozen grid."""
    n = len(ytr)
    if Xtr.shape[1] == 0:
        return 0.0
    sse = np.zeros(len(lam_rel))
    for k in np.unique(inner_fold):
        tr = inner_fold != k
        pred = ridge_path(Xtr[tr], ytr[tr], Xtr[~tr], lam_rel * tr.sum(), min_sd)
        sse += ((pred - ytr[~tr][:, None]) ** 2).sum(axis=0)
    return float(lam_rel[int(np.argmin(sse))] * n)


def fit_predict(Xtr, ytr, Xte, inner_fold, lam_rel, min_sd=1e-12):
    lam = choose_lambda(Xtr, ytr, inner_fold, lam_rel, min_sd)
    pred = ridge_path(Xtr, ytr, Xte, np.array([lam]), min_sd)[:, 0]
    return pred, lam


def impute_train_mean(Xtr: np.ndarray, Xte: np.ndarray):
    """Training-mean imputation (protocol §6); all-missing training columns are set to 0."""
    with np.errstate(invalid="ignore"):
        mu = np.nanmean(np.where(np.isfinite(Xtr), Xtr, np.nan), axis=0) if len(Xtr) else np.zeros(Xtr.shape[1])
    mu = np.where(np.isfinite(mu), mu, 0.0)
    Xtr = np.where(np.isfinite(Xtr), Xtr, mu)
    Xte = np.where(np.isfinite(Xte), Xte, mu)
    return Xtr, Xte, mu
