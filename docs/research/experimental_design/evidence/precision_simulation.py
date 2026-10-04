"""Pre-model design simulation for gate M04 (attainable precision).

Simulates complete synthetic datasets on the ACTUAL learner x content incidence of
each frozen analysis set and runs the FROZEN evaluation pipeline on them:
ridge with inner grouped-CV penalty selection, an outer person-grouped CV
(setting A), or a leave-one-video-out x person-fold crossed holdout (setting B).
It then measures, against simulated truth:

  * the bias and spread of the held-out incremental skill estimate;
  * coverage and type-I error of the candidate inference methods;
  * power to exclude zero, and the probability of ruling out the minimum useful
    effect delta when the truth is null.

Outcome-generating parameters come ONLY from outcome psychometrics (no
physiology). Nuisance structure of the synthetic physiological features follows
the audit's physiology-only group-structure summaries (between-person fraction
about 0.6-0.95, between-video fraction < 0.06). Physiological signal strength is a
scenario parameter: no real physiology-outcome association is used or computed.

Run from the repository root (roughly 30-60 minutes on 10 cores):
    .venv/bin/python docs/research/experimental_design/evidence/precision_simulation.py [--quick]
"""
from __future__ import annotations

import json
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
EV = Path(__file__).resolve().parent

LAMS_REL = 10.0 ** np.linspace(-3, 3, 13)   # ridge penalty grid, multiplied by n_train
N_T, N_Q = 5, 3                               # traits (age, sex, ASRS-I, ASRS-H, digit span); quality covariates
TRAIT_SHARE = 0.10                            # share of person variance explained by permissible traits
QUALITY_LOAD = 0.25                           # quality covariate 1 loads (negatively) on ability
PI_PERSON, PI_VIDEO = 0.60, 0.05              # nuisance variance fractions of each physiological feature
K_INF = 3                                     # features carrying the latent information
DELTA = 0.05                                  # minimum useful effect (outcome_psychometrics.json)
B_BOOT = 2000


# ----------------------------------------------------------------------------- parameters
def outcome_params():
    s = json.loads((EV / "outcome_psychometrics.json").read_text())
    rel = pd.read_csv(EV / "outcome_reliability_by_video.csv")
    out = {}
    for exp, lab in [(1, "E1_ocular"), (3, "E3"), (4, "E4"), (5, "E5_repeat")]:
        rv = rel[rel.set == lab]
        within = float((rv.sd_exact ** 2).mean())
        err = float(((1 - rv.alpha_exact) * rv.sd_exact ** 2).mean())
        vc = s["sets"][lab]["variance_components_normalized_exact_score"]
        out[exp] = dict(mean=s["sets"][lab]["normalized_exact_score"]["mean"], video=vc["video"],
                        person=vc["person"], pv=max(within - err - vc["person"], 1e-4), meas=err)
    return out


def incidence(set_name):
    m = pd.read_csv(EV / "analysis_set_manifest.csv")
    m = m[m[set_name]]
    persons, pidx = np.unique(m.qualified_participant_id, return_inverse=True)
    vids, vidx = np.unique(m.canonical_video_id, return_inverse=True)
    evkey = m.experiment.astype(str) + ":" + m.canonical_video_id
    evs, evidx = np.unique(evkey, return_inverse=True)
    exp_of_person = m.groupby(pidx).experiment.first().to_numpy()
    patterns = [np.sort(evidx[pidx == p]) for p in range(len(persons))]
    ev_exp = np.array([int(k.split(":")[0]) for k in evs])
    ev_vid = np.array([np.searchsorted(vids, k.split(":")[1]) for k in evs])
    return dict(person=pidx, ev=evidx, exp=m.experiment.to_numpy(), vid=vidx, exp_of_person=exp_of_person,
                patterns=patterns, ev_exp=ev_exp, ev_vid=ev_vid, n_vid=len(vids))


# ----------------------------------------------------------------------------- generator
def draw_content(inc, par, rng, n_feat, n_new_vid=0):
    """Video difficulty per experiment-video and video-level feature shifts per canonical video."""
    beta = np.array([rng.normal(0, np.sqrt(par[e]["video"])) for e in inc["ev_exp"]])
    wx = rng.normal(0, 1, (inc["n_vid"] + n_new_vid, n_feat))
    wq = rng.normal(0, 1, (inc["n_vid"] + n_new_vid, N_Q))
    return beta, wx, wq


def generate(cells_person, cells_ev, cells_vid, cells_exp, person_exp, par, beta, wx, wq, amp, phi, n_feat, rng):
    n_p, n = len(person_exp), len(cells_person)
    z1, z2 = rng.normal(size=n_p), rng.normal(size=n_p)
    zab = np.sqrt(TRAIT_SHARE) * z1 + np.sqrt(1 - TRAIT_SHARE) * z2
    sd_p = np.array([np.sqrt(par[e]["person"]) for e in person_exp])
    T = np.column_stack([z1, rng.normal(size=(n_p, N_T - 1))])[cells_person]
    zpv = rng.normal(size=n)
    pe = cells_exp
    mean = np.array([par[e]["mean"] for e in pe])
    sd_pv = np.sqrt(np.array([par[e]["pv"] for e in pe]))
    sd_m = np.sqrt(np.array([par[e]["meas"] for e in pe]))
    ystar = mean + beta[cells_ev] + sd_p[cells_person] * zab[cells_person] + sd_pv * zpv
    y = np.clip(np.round((ystar + sd_m * rng.normal(size=n)) * 12) / 12, 0, 1)
    uq = rng.normal(size=(n_p, N_Q))[cells_person]
    Q = np.sqrt(0.5) * uq + np.sqrt(PI_VIDEO) * wq[cells_vid] + np.sqrt(0.45) * rng.normal(size=(n, N_Q))
    Q[:, 0] += -QUALITY_LOAD * zab[cells_person]
    g = np.cos(phi) * z2[cells_person] + np.sin(phi) * zpv
    ux = rng.normal(size=(n_p, n_feat))[cells_person]
    X = (np.sqrt(PI_PERSON) * ux + np.sqrt(PI_VIDEO) * wx[cells_vid]
         + np.sqrt(1 - PI_PERSON - PI_VIDEO) * rng.normal(size=(n, n_feat)))
    X[:, :K_INF] += amp * g[:, None]
    return y, T, Q, X


def sample_people(inc, n_new, rng):
    """Fresh people re-using observed experiment/content patterns (new-person population)."""
    pick = rng.integers(0, len(inc["patterns"]), n_new)
    cp, ce = [], []
    for i, p in enumerate(pick):
        for ev in inc["patterns"][p]:
            cp.append(i); ce.append(ev)
    cp, ce = np.array(cp), np.array(ce)
    return cp, ce, inc["ev_vid"][ce], inc["ev_exp"][ce], inc["exp_of_person"][pick]


# ----------------------------------------------------------------------------- estimator
def ridge_path(Xtr, ytr, Xte, lams):
    mx, sx = Xtr.mean(0), Xtr.std(0)
    sx[sx < 1e-12] = 1.0
    Z = (Xtr - mx) / sx
    my = ytr.mean()
    U, s, Vt = np.linalg.svd(Z, full_matrices=False)
    F = s[:, None] / (s[:, None] ** 2 + lams[None, :])
    B = Vt.T @ (F * (U.T @ (ytr - my))[:, None])
    return my + ((Xte - mx) / sx) @ B


def fit_predict(Xtr, ytr, gtr, Xte, rng, k_inner=5):
    """Ridge with penalty chosen by inner person-grouped CV (frozen pipeline)."""
    n = len(ytr)
    _, inv = np.unique(gtr, return_inverse=True)
    f = rng.permutation(inv.max() + 1)[inv] % k_inner
    sse = np.zeros(len(LAMS_REL))
    for k in range(k_inner):
        tr = f != k
        pred = ridge_path(Xtr[tr], ytr[tr], Xtr[~tr], LAMS_REL * tr.sum())
        sse += ((pred - ytr[~tr][:, None]) ** 2).sum(0)
    lam = LAMS_REL[np.argmin(sse)] * n
    return ridge_path(Xtr, ytr, Xte, np.array([lam]))[:, 0]


def person_folds(person, exp_of_person, K, rng):
    fold_p = np.empty(len(exp_of_person), int)
    offset = 0
    for e in np.unique(exp_of_person):
        idx = np.flatnonzero(exp_of_person == e)
        fold_p[rng.permutation(idx)] = (np.arange(len(idx)) + offset) % K
        offset += len(idx)
    return fold_p[person]


def ev_means(y, ev, n_ev):
    s = np.bincount(ev, y, minlength=n_ev)
    c = np.bincount(ev, minlength=n_ev)
    return s / np.maximum(c, 1), c


def cv_setting_A(d, inc, rng, R, K=10):
    n = len(d["y"])
    W = np.column_stack([d["T"], d["Q"]])
    WX = np.column_stack([W, d["X"]])
    loss_b, loss_f = np.zeros(n), np.zeros(n)
    pred_b, pred_f = np.zeros(n), np.zeros(n)
    n_ev = len(inc["ev_exp"])
    n_p = len(inc["exp_of_person"])
    fold_diffs = []
    for _ in range(R):
        f = person_folds(inc["person"], inc["exp_of_person"], K, rng)
        for k in range(K):
            te, tr = f == k, f != k
            fe, cnt = ev_means(d["y"][tr], inc["ev"][tr], n_ev)
            r = d["y"][tr] - fe[inc["ev"][tr]]
            g = inc["person"][tr]
            pb = np.clip(fe[inc["ev"][te]] + fit_predict(W[tr], r, g, W[te], rng), 0, 1)
            pf = np.clip(fe[inc["ev"][te]] + fit_predict(WX[tr], r, g, WX[te], rng), 0, 1)
            loss_b[te] += (pb - d["y"][te]) ** 2 / R
            loss_f[te] += (pf - d["y"][te]) ** 2 / R
            pred_b[te] += pb / R
            pred_f[te] += pf / R
            fold_diffs.append(person_mean((pb - d["y"][te]) ** 2 - (pf - d["y"][te]) ** 2,
                                          inc["person"][te], n_p).mean())
    return loss_b, loss_f, pred_b, pred_f, np.array(fold_diffs)


def cv_setting_B(d, inc, rng, R, K=5):
    """New person AND new canonical video; reference-free features; no target-video labels."""
    n = len(d["y"])
    W = np.column_stack([d["T"], d["Q"]])
    WX = np.column_stack([W, d["X"]])
    pred_b, pred_f = np.zeros(n), np.zeros(n)
    n_ev = len(inc["ev_exp"])
    for _ in range(R):
        f = person_folds(inc["person"], inc["exp_of_person"], K, rng)
        for v in range(inc["n_vid"]):
            for k in range(K):
                te = (inc["vid"] == v) & (f == k)
                if not te.any():
                    continue
                tr = (inc["vid"] != v) & (f != k)
                fe, _ = ev_means(d["y"][tr], inc["ev"][tr], n_ev)
                r = d["y"][tr] - fe[inc["ev"][tr]]
                emean = {e: d["y"][tr][inc["exp"][tr] == e].mean() for e in np.unique(inc["exp"][te])}
                base0 = np.array([emean[e] for e in inc["exp"][te]])
                g = inc["person"][tr]
                pred_b[te] += np.clip(base0 + fit_predict(W[tr], r, g, W[te], rng), 0, 1) / R
                pred_f[te] += np.clip(base0 + fit_predict(WX[tr], r, g, WX[te], rng), 0, 1) / R
    return pred_b, pred_f


def within_content(y, pred, ev):
    """Centre outcome and prediction within each experiment-video (evaluation only)."""
    n_ev = ev.max() + 1
    yc = y - (np.bincount(ev, y, n_ev) / np.bincount(ev, minlength=n_ev))[ev]
    pc = pred - (np.bincount(ev, pred, n_ev) / np.bincount(ev, minlength=n_ev))[ev]
    return (yc - pc) ** 2


def within_person(y, pred, person, ev):
    """Double-centred (person and content) residual: tracks video-specific 'state' deviations."""
    def dc(a):
        out = a.copy()
        for _ in range(10):  # alternating projections converge quickly on this incidence
            out = out - (np.bincount(person, out) / np.bincount(person))[person]
            out = out - (np.bincount(ev, out) / np.bincount(ev))[ev]
        return out
    keep = np.bincount(person)[person] >= 2
    return (dc(y) - dc(pred)) ** 2, keep


# ----------------------------------------------------------------------------- inference
def stratified_weights(groups_exp, rng, B):
    n = len(groups_exp)
    W = np.zeros((B, n))
    for e in np.unique(groups_exp):
        idx = np.flatnonzero(groups_exp == e)
        draws = rng.integers(0, len(idx), (B, len(idx)))
        for j in range(len(idx)):
            np.add.at(W, (np.arange(B), idx[draws[:, j]]), 1.0)
    return W


def person_balanced(loss, person, n_p):
    c = np.bincount(person, minlength=n_p)
    return np.bincount(person, loss, minlength=n_p) / np.maximum(c, 1), c > 0


def boot_skill(Lb, Lf, W):
    return 1 - (W @ Lf) / (W @ Lb)


def fit_pair_losses(d, inc, tr, te, rng):
    """Frozen setting-A pipeline on a train/test cell split; returns per-cell base and full losses."""
    W = np.column_stack([d["T"], d["Q"]])
    WX = np.column_stack([W, d["X"]])
    fe, _ = ev_means(d["y"][tr], inc["ev"][tr], len(inc["ev_exp"]))
    r = d["y"][tr] - fe[inc["ev"][tr]]
    g = inc["person"][tr]
    pb = np.clip(fe[inc["ev"][te]] + fit_predict(W[tr], r, g, W[te], rng), 0, 1)
    pf = np.clip(fe[inc["ev"][te]] + fit_predict(WX[tr], r, g, WX[te], rng), 0, 1)
    return (pb - d["y"][te]) ** 2, (pf - d["y"][te]) ** 2


def person_mean(values, person_idx, n_p):
    c = np.bincount(person_idx, minlength=n_p)
    s = np.bincount(person_idx, values, minlength=n_p)
    ok = c > 0
    return s[ok] / c[ok]


def ncv_A(d, inc, rng, R_ncv, K=10):
    """Nested CV of Bates, Hastie & Tibshirani (JASA 2024, Alg. 1 and eq. 15), applied to the
    person-balanced loss DIFFERENCE (base minus full) with person-grouped, experiment-stratified folds."""
    n_p = len(inc["exp_of_person"])
    a_list, b_list, es = [], [], []
    for _ in range(R_ncv):
        f = person_folds(inc["person"], inc["exp_of_person"], K, rng)
        for k in range(K):
            out = f == k
            trn = ~out
            diff_in = np.full(len(f), np.nan)
            for j in range(K):
                if j == k:
                    continue
                te_j = f == j
                lb, lf = fit_pair_losses(d, inc, trn & ~te_j, te_j, rng)
                diff_in[te_j] = lb - lf
            e_in = person_mean(diff_in[trn], inc["person"][trn], n_p)
            lb, lf = fit_pair_losses(d, inc, trn, out, rng)
            e_out = person_mean(lb - lf, inc["person"][out], n_p)
            a_list.append((e_in.mean() - e_out.mean()) ** 2)
            b_list.append(e_out.var(ddof=1) / len(e_out))
            es.append(e_in)
    mse_hat = (K - 1) / K * (np.mean(a_list) - np.mean(b_list))
    return float(np.mean(np.concatenate(es))), float(mse_hat)


# ----------------------------------------------------------------------------- one replicate
def replicate_A(args):
    seed, set_name, amp, phi, n_feat, R, truth_n, R_ncv = args
    rng = np.random.default_rng(seed)
    inc, par = INC[set_name], PAR
    n_p = len(inc["exp_of_person"])
    K = 10
    beta, wx, wq = draw_content(inc, par, rng, n_feat)
    y, T, Q, X = generate(inc["person"], inc["ev"], inc["vid"], inc["exp"], inc["exp_of_person"], par,
                          beta, wx, wq, amp, phi, n_feat, rng)
    d = dict(y=y, T=T, Q=Q, X=X)
    lb, lf, pb, pf, fold_d = cv_setting_A(d, inc, rng, R, K)
    Lb, okp = person_balanced(lb, inc["person"], n_p)
    Lf, _ = person_balanced(lf, inc["person"], n_p)
    Lb, Lf = Lb[okp], Lf[okp]
    base_mse = Lb.mean()
    dp = Lb - Lf
    delta_cv = dp.mean()
    out = dict(seed=seed, est=1 - Lf.mean() / base_mse, est_cw=1 - lf.mean() / lb.mean(), base_mse=base_mse,
               delta_cv=delta_cv)
    # (i) person-cluster bootstrap of out-of-fold person losses (fitted models held fixed)
    W = stratified_weights(inc["exp_of_person"][okp], rng, B_BOOT)
    bs = W @ dp / W.sum(1)
    out["boot_lo"], out["boot_hi"] = np.quantile(bs, [0.05, 0.95])
    # (ii) corrected resampled t (Nadeau & Bengio 2003) on fold-level differences, R x K folds
    J = len(fold_d)
    v = fold_d.var(ddof=1) * (1 / J + 1 / (K - 1))
    from scipy.stats import t as tdist
    tq = tdist.ppf(0.95, J - 1)
    out["nb_lo"], out["nb_hi"] = fold_d.mean() - tq * np.sqrt(v), fold_d.mean() + tq * np.sqrt(v)
    # (iii) nested CV (Bates et al.) with bias correction and MSE clipping between se and sqrt(K) se
    if R_ncv > 0:
        err_ncv, mse_hat = ncv_A(d, inc, rng, R_ncv, K)
        se = dp.std(ddof=1) / np.sqrt(len(dp))
        root = np.clip(np.sqrt(max(mse_hat, 0.0)), se, np.sqrt(K) * se)
        bias = (1 + (K - 2) / K) * (err_ncv - delta_cv)
        centre = err_ncv - bias
        out.update(ncv_centre=centre, ncv_lo=centre - 1.645 * root, ncv_hi=centre + 1.645 * root,
                   ncv_root_over_se=root / se)
    # state (within-person, within-content) metric
    sb, keep = within_person(y, pb, inc["person"], inc["ev"])
    sf, _ = within_person(y, pf, inc["person"], inc["ev"])
    out["state"] = 1 - sf[keep].sum() / sb[keep].sum()
    # truth: the same pipeline trained on all n people (and on 90%), evaluated on fresh people, same content
    cp, ce, cv, cx, pe = sample_people(inc, truth_n, rng)
    yN, TN, QN, XN = generate(cp, ce, cv, cx, pe, par, beta, wx, wq, amp, phi, n_feat, rng)
    dN = dict(y=np.concatenate([y, yN]), T=np.vstack([T, TN]), Q=np.vstack([Q, QN]), X=np.vstack([X, XN]))
    incN = dict(inc)
    incN["ev"] = np.concatenate([inc["ev"], ce])
    incN["person"] = np.concatenate([inc["person"], cp + n_p])
    test = np.r_[np.zeros(len(y), bool), np.ones(len(yN), bool)]
    for label, frac in [("truth", 1.0), ("truth90", 0.9)]:
        trp = rng.random(n_p) < frac if frac < 1 else np.ones(n_p, bool)
        tr = np.r_[trp[inc["person"]], np.zeros(len(yN), bool)]
        lbN, lfN = fit_pair_losses(dN, incN, tr, test, rng)
        LbN = person_mean(lbN, cp, truth_n)
        LfN = person_mean(lfN, cp, truth_n)
        out[label] = 1 - LfN.mean() / LbN.mean()
        out[label + "_delta"] = LbN.mean() - LfN.mean()
    return out


def replicate_B(args):
    seed, set_name, amp, phi, n_feat, R, truth_vid = args
    rng = np.random.default_rng(seed)
    inc, par = INC[set_name], PAR
    n_p = len(inc["exp_of_person"])
    beta, wx, wq = draw_content(inc, par, rng, n_feat, n_new_vid=truth_vid)
    y, T, Q, X = generate(inc["person"], inc["ev"], inc["vid"], inc["exp"], inc["exp_of_person"], par,
                          beta, wx, wq, amp, phi, n_feat, rng)
    d = dict(y=y, T=T, Q=Q, X=X)
    pb, pf = cv_setting_B(d, inc, rng, R)
    lb, lf = within_content(y, pb, inc["ev"]), within_content(y, pf, inc["ev"])
    Lb, okp = person_balanced(lb, inc["person"], n_p)
    Lf, _ = person_balanced(lf, inc["person"], n_p)
    est = 1 - Lf[okp].mean() / Lb[okp].mean()
    abs_b, abs_f = (pb - y) ** 2, (pf - y) ** 2
    est_abs = 1 - abs_f.mean() / abs_b.mean()
    # per-video estimates
    per_vid = [1 - lf[inc["vid"] == v].sum() / lb[inc["vid"] == v].sum() for v in range(inc["n_vid"])]
    # inference 1: person bootstrap conditional on the sampled videos
    W = stratified_weights(inc["exp_of_person"][okp], rng, B_BOOT)
    bs = boot_skill(Lb[okp], Lf[okp], W)
    q = np.quantile(bs, [0.05, 0.95])
    # inference 2: two-way (person x video) pigeonhole bootstrap on cell losses
    Wp = stratified_weights(inc["exp_of_person"], rng, B_BOOT)
    Wv = rng.multinomial(inc["n_vid"], np.full(inc["n_vid"], 1 / inc["n_vid"]), B_BOOT).astype(float)
    wcell = Wp[:, inc["person"]] * Wv[:, inc["vid"]]
    bs2 = 1 - (wcell @ lf) / (wcell @ lb)
    q2 = np.quantile(bs2, [0.05, 0.95])
    # truth: model trained on all observed data, evaluated on NEW videos with fresh people
    tr = np.ones(len(y), bool)
    fe, _ = ev_means(y, inc["ev"], len(inc["ev_exp"]))
    r = y - fe[inc["ev"]]
    W0, WX0 = np.column_stack([T, Q]), np.column_stack([T, Q, X])
    lbN, lfN = [], []
    for j in range(truth_vid):
        e = 3 if j % 2 == 0 else 4
        npv = 30
        cp = np.arange(npv); cvid = np.full(npv, inc["n_vid"] + j)
        cev = np.zeros(npv, int)  # single new experiment-video
        bnew = np.array([rng.normal(0, np.sqrt(par[e]["video"]))])
        yN, TN, QN, XN = generate(cp, cev, cvid, np.full(npv, e), np.full(npv, e), par, bnew, wx, wq,
                                  amp, phi, n_feat, rng)
        base0 = y[inc["exp"] == e].mean()
        pbN = np.clip(base0 + fit_predict(W0, r, inc["person"], np.column_stack([TN, QN]), rng), 0, 1)
        pfN = np.clip(base0 + fit_predict(WX0, r, inc["person"], np.column_stack([TN, QN, XN]), rng), 0, 1)
        lbN.append(within_content(yN, pbN, cev).sum()); lfN.append(within_content(yN, pfN, cev).sum())
    truth = 1 - np.sum(lfN) / np.sum(lbN)
    return dict(seed=seed, est=est, est_abs=est_abs, lo90_person=q[0], hi90_person=q[1],
                lo90_twoway=q2[0], hi90_twoway=q2[1], per_video_sd=float(np.std(per_vid, ddof=1)),
                per_video_min=float(np.min(per_vid)), truth=truth)


# ----------------------------------------------------------------------------- oracle calibration
def oracle_skill(set_name, amp, phi, n_feat, rng, n_people=20000):
    inc, par = INC[set_name], PAR
    beta, wx, wq = draw_content(inc, par, rng, n_feat)
    cp, ce, cv, cx, pe = sample_people(inc, n_people, rng)
    y, T, Q, X = generate(cp, ce, cv, cx, pe, par, beta, wx, wq, amp, phi, n_feat, rng)
    fe, _ = ev_means(y, ce, len(inc["ev_exp"]))
    r = y - fe[ce]
    def mse(M):
        A = np.column_stack([np.ones(len(r)), M])
        coef, *_ = np.linalg.lstsq(A, r, rcond=None)
        return np.mean((r - A @ coef) ** 2)
    return 1 - mse(np.column_stack([T, Q, X])) / mse(np.column_stack([T, Q]))


def calibrate_amp(set_name, target, phi, n_feat, seed=7):
    if target <= 0:
        return 0.0
    lo, hi = 0.0, 4.0
    for _ in range(30):
        mid = (lo + hi) / 2
        s = oracle_skill(set_name, mid, phi, n_feat, np.random.default_rng(seed))
        lo, hi = (mid, hi) if s < target else (lo, mid)
    return (lo + hi) / 2


def mix_angle(set_name, kind):
    """phi = 0: stable-person information; pi/2: video-specific state; 'proportional': tracks true score."""
    if kind == "person":
        return 0.0
    if kind == "state":
        return np.pi / 2
    inc = INC[set_name]
    exps = inc["exp"]
    vp = np.mean([PAR[e]["person"] * (1 - TRAIT_SHARE) for e in exps])
    vs = np.mean([PAR[e]["pv"] for e in exps])
    return float(np.arctan(np.sqrt(vs / vp)))


INC: dict = {}
PAR: dict = {}


def init_worker(inc, par):
    INC.update(inc); PAR.update(par)


def summarize_A(df, delta=DELTA):
    """Coverage is judged on the loss-difference scale against the expected full-n truth;
    decisions are taken on the skill scale (interval divided by the estimated baseline MSE)."""
    td = df.truth_delta.mean()
    t = df.truth.mean()
    res = dict(expected_truth=t, expected_truth90=df.truth90.mean(), mean_est=df.est.mean(),
               bias=df.est.mean() - t, sd_est=df.est.std(ddof=1), n=len(df),
               state_mean=df.state.mean(), state_sd=df.state.std(ddof=1))
    methods = ["boot", "nb"] + (["ncv"] if "ncv_lo" in df else [])
    for m in methods:
        lo, hi = df[m + "_lo"], df[m + "_hi"]
        res[f"cover90_{m}"] = ((lo <= td) & (td <= hi)).mean()
        res[f"cover90_cond_{m}"] = ((lo <= df.truth_delta) & (df.truth_delta <= hi)).mean()
        res[f"hw90_skill_{m}"] = ((hi - lo) / 2 / df.base_mse).median()
        res[f"reject0_{m}"] = (lo > 0).mean()
        res[f"rule_out_delta_{m}"] = (hi / df.base_mse < delta).mean()
    if "ncv_root_over_se" in df:
        res["ncv_inflation_median"] = df.ncv_root_over_se.median()
    return res


def summarize_B(df, delta=DELTA):
    t = df.truth.mean()
    return dict(
        expected_truth=t, mean_est=df.est.mean(), bias=df.est.mean() - t, sd_est=df.est.std(ddof=1),
        mean_est_abs=df.est_abs.mean(),
        cover90_person=((df.lo90_person <= t) & (t <= df.hi90_person)).mean(),
        cover90_twoway=((df.lo90_twoway <= t) & (t <= df.hi90_twoway)).mean(),
        median_hw90_person=((df.hi90_person - df.lo90_person) / 2).median(),
        median_hw90_twoway=((df.hi90_twoway - df.lo90_twoway) / 2).median(),
        reject0_person=(df.lo90_person > 0).mean(), reject0_twoway=(df.lo90_twoway > 0).mean(),
        rule_out_delta_person=(df.hi90_person < delta).mean(), rule_out_delta_twoway=(df.hi90_twoway < delta).mean(),
        per_video_sd=df.per_video_sd.mean(), n=len(df))


def main(quick=False):
    sets = {"PAS_E34_core": 9, "PAS_E34_four": 11, "E5_core": 9, "E1_gaze": 3}
    inc = {s: incidence(s) for s in sets}
    par = outcome_params()
    init_worker(inc, par)
    nsim = 40 if quick else 400
    R_A, R_B, R_NCV = (2, 1, 2) if quick else (5, 2, 20)
    targets = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30]
    plan = []
    for s, p in sets.items():
        for tgt in (targets if s.startswith("PAS") else [0.0, 0.10, 0.20, 0.30]):
            plan.append(("A", s, "proportional", tgt, p))
    for kind in ["person", "state"]:
        for tgt in [0.10]:
            plan.append(("A", "PAS_E34_core", kind, tgt, 9))
    for tgt in targets:
        plan.append(("B", "PAS_E34_core", "proportional", tgt, 6))
    calib = []
    for regime, s, kind, tgt, p in plan:
        phi = mix_angle(s, kind)
        amp = calibrate_amp(s, tgt, phi, p)
        calib.append(dict(regime=regime, set=s, mix=kind, oracle_target=tgt, phi=phi, amp=amp, n_feat=p,
                          oracle_check=oracle_skill(s, amp, phi, p, np.random.default_rng(11))))
    calib = pd.DataFrame(calib)
    print(calib.to_string())
    ctx = get_context("spawn")
    results = []
    t0 = time.time()
    with ctx.Pool(10, initializer=init_worker, initargs=(inc, par)) as pool:
        for i, row in calib.iterrows():
            base_seed = 1_000_000 * (i + 1)
            if row.regime == "A":
                args = [(base_seed + j, row.set, row.amp, row.phi, row.n_feat, R_A, 1500, R_NCV) for j in range(nsim)]
                df = pd.DataFrame(pool.map(replicate_A, args, chunksize=2))
                summ = summarize_A(df)
            else:
                args = [(base_seed + j, row.set, row.amp, row.phi, row.n_feat, R_B, 60) for j in range(nsim)]
                df = pd.DataFrame(pool.map(replicate_B, args, chunksize=4))
                summ = summarize_B(df)
            df.assign(**{k: row[k] for k in ["regime", "set", "mix", "oracle_target"]}).to_csv(
                EV / "simulation_replicates" / f"{row.regime}_{row.set}_{row.mix}_{row.oracle_target:.3f}.csv", index=False)
            summ.update({k: row[k] for k in ["regime", "set", "mix", "oracle_target", "oracle_check", "n_feat"]})
            results.append(summ)
            print(f"[{time.time()-t0:7.1f}s] {row.regime} {row.set} {row.mix} S*={row.oracle_target:.3f} "
                  + " ".join(f"{k}={v:.3f}" for k, v in summ.items() if isinstance(v, float)), flush=True)
    out = pd.DataFrame(results)
    out.to_csv(EV / ("precision_simulation_quick.csv" if quick else "precision_simulation_summary.csv"), index=False)
    meta = dict(phase_date="2026-10-04", nsim=nsim, R_A=R_A, R_B=R_B, R_NCV=R_NCV, B_boot=B_BOOT, delta=DELTA,
                trait_share=TRAIT_SHARE, quality_load=QUALITY_LOAD, pi_person=PI_PERSON, pi_video=PI_VIDEO,
                k_inf=K_INF, outcome_params={str(k): v for k, v in par.items()}, quick=quick,
                physiology_outcome_association_used=False)
    (EV / ("precision_simulation_meta_quick.json" if quick else "precision_simulation_meta.json")).write_text(
        json.dumps(meta, indent=2) + "\n")


if __name__ == "__main__":
    (EV / "simulation_replicates").mkdir(exist_ok=True)
    main(quick="--quick" in sys.argv)
