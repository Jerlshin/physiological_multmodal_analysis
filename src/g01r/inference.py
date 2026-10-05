"""Inference procedures fixed by role (protocol §11; evaluation contract §6; EDD-009, EDD-014).

* Detection (H1, H2): person-block Freedman-Lane permutation test on paired outer folds.
* Reported interval: nested CV (Bates, Hastie & Tibshirani 2024, Alg. 1, eq. 15 bias
  correction, MSE clipping), 90 %, divided by the CV baseline MSE.
* Futility: corrected resampled-t upper bound with z = 3.0 compared with 2 delta = 0.10.
* B/C: two-way (person x video) bootstrap, conditional on the sampled videos; no p-values.
* Declared fallback detection test: stratified person bootstrap (used only if the
  production re-validation shows permutation false detection > 0.07).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

from .metrics import person_means, state_losses
from .models import fit_predict
from .population import AnalysisSet
from .rng import rng_for


# ---------------------------------------------------------------------------- permutation
def pattern_groups(aset: AnalysisSet) -> dict:
    """(experiment, tested experiment x video pattern) -> member persons."""
    groups = {}
    exp_of_person = aset.exp_of_person
    for p, pat in aset.patterns().items():
        groups.setdefault((int(exp_of_person[p]), pat), []).append(p)
    return groups


def person_block_permutation(aset: AnalysisSet, rng: np.random.Generator) -> np.ndarray:
    """Cell index map: cell i receives the tested-block values of cell perm[i]. Whole learners are
    exchanged among learners of the same experiment with the identical tested-video pattern;
    learners with a unique pattern stay fixed."""
    cell_of = {(int(p), int(e)): i for i, (p, e) in enumerate(zip(aset.person, aset.ev))}
    perm = np.arange(aset.n)
    for (_, pat), members in sorted(pattern_groups(aset).items()):
        if len(members) < 2:
            continue
        shuffled = rng.permutation(members)
        for src, dst in zip(members, shuffled):
            for e in pat:
                perm[cell_of[(src, e)]] = cell_of[(int(dst), e)]
    return perm


@dataclass
class PermutationSetup:
    """Per paired split: imputed full design (all cells), tested/nuisance columns, targets and inner folds."""

    splits: list          # list of SplitResult (with designs) from the first R repetitions
    full_model: str
    tested_cols: list
    nuisance_cols: list


def _residualize(aset: AnalysisSet, X: np.ndarray, tested: np.ndarray, nuisance: np.ndarray):
    """Full-data OLS of the tested block on content dummies + nuisance columns (no outcomes)."""
    D = np.eye(aset.n_ev)[aset.ev]
    Z = np.column_stack([D, X[:, nuisance]])
    T = X[:, tested]
    coef, *_ = np.linalg.lstsq(Z, T, rcond=None)
    fitted = Z @ coef
    return fitted, T - fitted


def prepare_permutation(aset: AnalysisSet, setup: PermutationSetup):
    prepared = []
    for res in setup.splits:
        X, cols = res.designs[setup.full_model]
        tested = np.array([cols.index(c) for c in setup.tested_cols])
        nuisance = np.array([cols.index(c) for c in setup.nuisance_cols], int)
        fitted, resid = _residualize(aset, X, tested, nuisance)
        prepared.append((res, X, tested, fitted, resid))
    return prepared


def full_model_losses(aset, prepared, y, perm, lam_rel, min_sd, clip=(0.0, 1.0)) -> np.ndarray:
    """Per-cell squared error of the full model averaged over the paired repetitions, with the
    tested block replaced by fitted + residual[perm] (perm = identity gives the observed fit)."""
    total = np.zeros(aset.n)
    count = np.zeros(aset.n)
    for res, X, tested, fitted, resid in prepared:
        Xp = X.copy()
        Xp[:, tested] = fitted + resid[perm]
        tr, te = res.train, res.test
        pred, _ = fit_predict(Xp[tr], res.resid_train, Xp[te], res.inner_fold, lam_rel, min_sd)
        pred = np.clip(res.offsets_test + pred, *clip)
        total[te] += (pred - y[te]) ** 2
        count[te] += 1
    return total / np.maximum(count, 1)


def permutation_statistic(lb_cells, lf_cells, person) -> float:
    """Person-balanced loss difference (base minus full)."""
    return float((person_means(lb_cells, person) - person_means(lf_cells, person)).mean())


def permutation_p(observed: float, null: np.ndarray) -> float:
    return float((1 + np.sum(np.asarray(null) >= observed)) / (1 + len(null)))


def permutation_null(aset, prepared, y, lb_cells, perms, lam_rel, min_sd, clip=(0.0, 1.0)) -> np.ndarray:
    out = np.empty(len(perms))
    for b, perm in enumerate(perms):
        lf = full_model_losses(aset, prepared, y, perm, lam_rel, min_sd, clip)
        out[b] = permutation_statistic(lb_cells, lf, aset.person)
    return out


def draw_permutations(aset: AnalysisSet, B: int, base_seed: int, *labels) -> np.ndarray:
    return np.stack([person_block_permutation(aset, rng_for(base_seed, *labels, "perm", b)) for b in range(B)])


# ---------------------------------------------------------------------------- corrected resampled t
def fold_differences(preds_b: np.ndarray, preds_f: np.ndarray, y: np.ndarray, folds: np.ndarray, aset: AnalysisSet):
    """Person-mean loss difference (base - full) inside every outer test fold (R*K values)."""
    out = []
    for r in range(preds_b.shape[0]):
        if not np.isfinite(preds_b[r]).any():
            continue
        f = folds[r][aset.person]
        for k in np.unique(folds[r]):
            m = f == k
            d = (preds_b[r, m] - y[m]) ** 2 - (preds_f[r, m] - y[m]) ** 2
            out.append(person_means(d, aset.person[m]).mean())
    return np.array(out)


def corrected_t_upper(fold_diffs: np.ndarray, K: int, z: float, base_mse: float) -> dict:
    J = len(fold_diffs)
    centre = float(fold_diffs.mean())
    se = float(np.sqrt(fold_diffs.var(ddof=1) * (1 / J + 1 / (K - 1))))
    return dict(centre=centre, se=se, z=z, upper=centre + z * se, upper_skill=(centre + z * se) / base_mse, J=J)


# ---------------------------------------------------------------------------- nested CV (Bates et al. 2024)
def nested_cv_pieces(aset: AnalysisSet, fit_pair, loss_fns: dict, K: int, base_seed: int, labels, rep: int) -> dict:
    """One nested-CV repetition. ``fit_pair(train, test, labels)`` returns (pred_base, pred_full) on
    test cells; ``loss_fns[name](cells, pb, pf)`` returns per-person loss differences (base - full)."""
    from .splits import person_folds

    folds = person_folds(aset.exp_of_person, K, rng_for(base_seed, *labels, "ncv", rep))[aset.person]
    out = {name: dict(a=[], b=[], e_in=[]) for name in loss_fns}
    for k in range(K):
        trn = folds != k
        pb_in = np.full(aset.n, np.nan)
        pf_in = np.full(aset.n, np.nan)
        for j in range(K):
            if j == k:
                continue
            te = folds == j
            pb, pf = fit_pair(trn & ~te, te, (*labels, "ncv", rep, k, j))
            pb_in[te], pf_in[te] = pb, pf
        te = folds == k
        pb_out, pf_out = fit_pair(trn, te, (*labels, "ncv", rep, k, "out"))
        cells_in, cells_out = np.flatnonzero(trn), np.flatnonzero(te)
        for name, fn in loss_fns.items():
            e_in = fn(cells_in, pb_in[cells_in], pf_in[cells_in])
            e_out = fn(cells_out, pb_out, pf_out)
            if len(e_in) == 0 or len(e_out) < 2:
                continue
            out[name]["a"].append((e_in.mean() - e_out.mean()) ** 2)
            out[name]["b"].append(e_out.var(ddof=1) / len(e_out))
            out[name]["e_in"].append(e_in)
    return out


def nested_cv_interval(pieces: list, delta_cv: float, person_diffs: np.ndarray, base_loss: float, K: int,
                       level: float = 0.90) -> dict:
    """Combine repetitions: bias-corrected centre and clipped root-MSE (Bates et al. 2024, eq. 15)."""
    a = np.concatenate([p["a"] for p in pieces])
    b = np.concatenate([p["b"] for p in pieces])
    e_in = np.concatenate([e for p in pieces for e in p["e_in"]])
    err_ncv = float(e_in.mean())
    mse_hat = (K - 1) / K * (a.mean() - b.mean())
    se = float(np.std(person_diffs, ddof=1) / np.sqrt(len(person_diffs)))
    root = float(np.clip(np.sqrt(max(mse_hat, 0.0)), se, np.sqrt(K) * se))
    bias = (1 + (K - 2) / K) * (err_ncv - delta_cv)
    centre = err_ncv - bias
    zq = norm.ppf(0.5 + level / 2)
    lo, hi = centre - zq * root, centre + zq * root
    return dict(level=level, centre=centre, lo=lo, hi=hi, centre_skill=centre / base_loss, lo_skill=lo / base_loss,
                hi_skill=hi / base_loss, err_ncv=err_ncv, mse_hat=float(mse_hat), se_naive=se,
                root_over_se=root / se if se > 0 else np.nan, reps=len(pieces), base_loss=base_loss)


def person_loss_diff(y, aset: AnalysisSet):
    def fn(cells, pb, pf):
        d = (pb - y[cells]) ** 2 - (pf - y[cells]) ** 2
        return person_means(d, aset.person[cells])
    return fn


def state_loss_diff(y, aset: AnalysisSet):
    def fn(cells, pb, pf):
        lb, keep = state_losses(y[cells], pb, aset.person[cells], aset.ev[cells])
        lf, _ = state_losses(y[cells], pf, aset.person[cells], aset.ev[cells])
        if keep.sum() == 0:
            return np.array([])
        return person_means((lb - lf)[keep], aset.person[cells][keep])
    return fn


# ---------------------------------------------------------------------------- multiplicity and decisions
def holm(pvalues: dict) -> dict:
    items = sorted(pvalues.items(), key=lambda kv: kv[1])
    m = len(items)
    adjusted, running = {}, 0.0
    for i, (name, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        adjusted[name] = running
    return adjusted


def h1_decision(p: float, skill: float, upper3_skill: float, delta: float, threshold: float, alpha: float) -> dict:
    """Pre-declared interpretation of H1 (estimand_and_hypotheses.md §6)."""
    if p <= alpha and skill >= delta:
        cat, text = "detected_useful", "Incremental individual information detected, with a point estimate of practically useful size"
    elif p <= alpha:
        cat, text = "detected_small", "Information detected, but the estimate is below the useful threshold (non-zero yet practically small)"
    elif upper3_skill < threshold:
        cat, text = ("bounded_negative", "Increments >= 0.10 are ruled out at this sample size and for this procedure; "
                     "increments in 0.05-0.10 remain possible (not 'no information')")
    else:
        cat, text = "inconclusive", "Inconclusive; never reported as absence"
    return dict(category=cat, conclusion=text, p=p, skill=skill, upper3_skill=upper3_skill)


# ---------------------------------------------------------------------------- bootstraps
def stratified_person_weights(exp_of_person: np.ndarray, rng: np.random.Generator, B: int) -> np.ndarray:
    n = len(exp_of_person)
    W = np.zeros((B, n))
    for e in np.unique(exp_of_person):
        idx = np.flatnonzero(exp_of_person == e)
        draws = rng.integers(0, len(idx), (B, len(idx)))
        for j in range(len(idx)):
            np.add.at(W, (np.arange(B), idx[draws[:, j]]), 1.0)
    return W


def two_way_bootstrap(lb: np.ndarray, lf: np.ndarray, aset: AnalysisSet, rng: np.random.Generator, B: int,
                      level: float = 0.90) -> dict:
    """Person x video bootstrap of the person-balanced (within-content) skill. Conditional on the
    sampled videos; approximate; undercovers the content population in simulation (IS-015)."""
    Wp = stratified_person_weights(aset.exp_of_person, rng, B)
    Wv = rng.multinomial(aset.n_video, np.full(aset.n_video, 1 / aset.n_video), B).astype(float)
    per = np.bincount(aset.person)[aset.person]
    w = Wp[:, aset.person] * Wv[:, aset.video] / per[None, :]
    with np.errstate(invalid="ignore", divide="ignore"):
        bs = 1 - (w @ lf) / (w @ lb)
    bs = bs[np.isfinite(bs)]
    q = np.quantile(bs, [(1 - level) / 2, 1 - (1 - level) / 2])
    return dict(lo=float(q[0]), hi=float(q[1]), level=level, B=int(len(bs)),
                label="conditional on the sampled videos; approximate; undercovers the content population in simulation")


def person_bootstrap_detection(person_diffs: np.ndarray, exp_of_person: np.ndarray, rng, B: int, level=0.90) -> dict:
    """Declared fallback (EDD-009): detect if the lower bound of the stratified person bootstrap of the
    person-level loss differences exceeds 0."""
    W = stratified_person_weights(exp_of_person, rng, B)
    bs = W @ person_diffs / W.sum(axis=1)
    lo, hi = np.quantile(bs, [(1 - level) / 2, 1 - (1 - level) / 2])
    return dict(lo=float(lo), hi=float(hi), detect=bool(lo > 0))
