"""Stage-1 design simulation (spec §1): real incidence, real anchor structure, real moment terms,
synthetic outcomes. No quiz outcome is read anywhere in this module.

Generating model (spec §1.3, extended for realistic dependence; S1-D05)
----------------------------------------------------------------------
    logit P(y_pvj = 1) = beta_j + a_j (u_p + w_pv) + q_p,m(j) + lambda_p,v x*_pvj [+ confound]

* beta_j ~ N(m_beta, s_beta^2) per item (crossed: shared by all learners); per experiment in the pooled lock;
* u_p ~ N(0, tau^2) learner effect shared across videos; w_pv ~ N(0, 0.3^2) learner x video;
* q ~ N(0, sigma_q^2) **local dependence**: one draw per learner x anchor moment, shared by the items
  that sit in that moment (item-specific prior knowledge of the same content), one per learner x item
  otherwise. Independent of engagement. sigma_q = 0.5 by default;
* x*_pvj = sqrt(rho) x_pvj + sqrt(1 - rho) eps_p,v,m(j): the latent moment state. x_pvj is the **real**
  anchored moment composite of the learner (engagement-signed equal-weight composite of the six primary
  channels; centred within learner x video and item; unit SD), eps is shared by items of one moment;
  corr(x, x*) = sqrt(rho) on anchorable rows; x* = 0 for non-anchorable items;
* a_j = 1 (Rasch) or log-normal(0, 0.3) (2PL misspecification); optional guessing floor
  c_j = 0.25 (one keyed option) / 0.10 (several); optional heterogeneity lambda_p,v = lambda (1 + 0.5 z_p)(1 + 0.3 z_v).

Nuisance values (m_beta, s_beta, tau) cycle through the 2 x 2 x 2 grid of spec §1.3 with the
replicate index, so every scenario averages over the declared grid and can be stratified by it.

Confound scenarios (spec §1.4), all with lambda = 0 unless stated:

* N0 pure null;
* N1 fatigue/position: beta_j += -0.5 (pos_j - .5); theta += 0.3 s_pv; and the interaction
  0.4 s_pv * 2 (anchor_pos_j - .5), with s_pv the learner's **real** engagement slope over the recording;
* N1q non-linear fatigue (added in Stage 1): as N1 with the learner's real engagement *curvature* c_pv and
  the interaction 0.6 c_pv ((2 (anchor_pos_j - .5))^2 - 1/3): linear detrending cannot remove it;
* N2 person confound: u_p correlated .5 with the learner's real whole-video engagement;
* N3 data loss not content-timed: theta += -0.5 Q_pv (real recording invalid fraction, standardized);
* N4 content-timed data loss (NH4 true): eta += -log(1.5) x^loss_pvj (real in-window long-loss term).

Closure-phase additions (docs/research/novel_method/closure; declared in its predeclared_rules.md before the runs):

* N1c cubic fatigue: as N1q with the learner's real **cubic** Legendre coefficient c3_pv and the shape P3(2a - 1),
  strength matched to N1q by RMS over the anchor-position range (0.6 * RMS(x^2 - 1/3) / RMS(P3));
* N1e exponential ("vigilance decrement") fatigue: the learner's real coefficient on exp(-2 (x + 1)) and that shape,
  strength matched the same way;
* truth directions other than the equal-weight composite: ``gaze`` (equal weights on the four gaze channels),
  ``validity`` (in-window long loss only), ``random`` (sign-coherent random direction w = s * |g|, g ~ N(0, I),
  drawn per replicate from its own stream); ``dev_truth`` sets the development cohort's truth separately
  (``random_indep``: an independent random direction, i.e. the lock and development directions differ).
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass

import numpy as np
from scipy.special import expit

from . import features as F
from . import inference as I
from .model import Fitter, penalized_logistic, predict_marginal

NUISANCE = [(mb, sb, tau) for mb in (0.4, 0.8) for sb in (0.8, 1.2) for tau in (0.5, 1.0)]
W_SD = 0.3
N1_GAMMA_POS, N1_KAPPA0, N1_KAPPA = -0.5, 0.3, 0.4
N1Q_KAPPA = 0.6
# closure nulls: RMS over x = 2a - 1 ~ U(-1, 1) matched to the N1q shape x^2 - 1/3 (RMS sqrt(4/45))
_RMS_Q = float(np.sqrt(4 / 45))
_RMS_P3 = float(np.sqrt(1 / 7))
_E_MEAN = (1 - np.exp(-4.0)) / 4
_RMS_E = float(np.sqrt((1 - np.exp(-8.0)) / 8 - _E_MEAN ** 2))
N1C_KAPPA = N1Q_KAPPA * _RMS_Q / _RMS_P3            # ~0.473
N1E_KAPPA = N1Q_KAPPA * _RMS_Q / _RMS_E             # ~0.703
TRUTHS = ("composite", "logdens", "gaze", "validity", "random")
N2_R = 0.5
N3_GAMMA_Q = -0.5
N4_OR = 1.5
DEV_STOP_P = 0.10
DEV_STOP_DAUC = 0.01


@dataclass(frozen=True)
class Scenario:
    name: str                    # N0..N4 or ALT
    odds_ratio: float = 1.0      # per SD of the latent moment state x*
    rho: float = 0.4             # squared correlation of observed and latent moment state
    sigma_q: float = 0.5
    two_pl: bool = False
    guessing: bool = False
    hetero: bool = False
    truth: str = "composite"     # composite | logdens | gaze | validity | random
    e5_factor: float = 1.0       # lambda multiplier in E5 rows (pooled lock)
    dev_truth: str = ""          # development cohort's truth if different ("" = same; "random_indep")

    @property
    def key(self) -> str:
        parts = [self.name, f"or{self.odds_ratio:g}", f"rho{self.rho:g}", f"q{self.sigma_q:g}"]
        parts += [t for t, on in (("2pl", self.two_pl), ("guess", self.guessing), ("het", self.hetero)) if on]
        if self.truth != "composite":
            parts.append(self.truth)
        if self.e5_factor != 1.0:
            parts.append(f"e5x{self.e5_factor:g}")
        if self.dev_truth:
            parts.append(f"dev-{self.dev_truth}")
        return "_".join(parts)


# ----------------------------------------------------------------------------- truth from real signals
@dataclass
class Truth:
    x_comp: np.ndarray           # anchorable rows: real engagement composite (double-centred, unit SD)
    x6: np.ndarray               # anchorable rows x 6 canonical regressors (unit SD each)
    x_literal: np.ndarray        # anchorable rows: (z - e_bar) composite, NOT within-cell centred (plan literal)
    x_loss: np.ndarray           # anchorable rows: in-window long-loss regressor (unit SD)
    x_logdens: np.ndarray
    slope: np.ndarray            # cells: standardized engagement slope over the recording
    curv: np.ndarray             # cells: standardized curvature (orthogonal quadratic) of the engagement course
    e_person: np.ndarray         # persons: standardized whole-video engagement
    q_cell: np.ndarray           # cells: standardized invalid fraction
    eanch_comp: np.ndarray       # cells: anchored engagement composite (standardized)
    grp: np.ndarray              # rows: local-dependence group (learner x moment, or learner x item)
    eps_grp: np.ndarray          # anchorable rows: latent-state group (learner x video x moment)
    sign: np.ndarray
    cub: np.ndarray | None = None    # cells: standardized cubic Legendre coefficient of the engagement course (N1c)
    cexp: np.ndarray | None = None   # cells: standardized coefficient on exp(-2 (x + 1)) (N1e)


def build_truth(S: I.SetStructure) -> Truth:
    can = S.canonical
    allrows = np.ones(len(S.anch_index), bool)
    x6 = F.moment_regressors(can.mb.m, S.anch_cell, S.anch_item, allrows)
    sign = np.array([F.ENGAGED_SIGN[c] for c in F.PRIMARY])
    xc = x6 @ sign
    xc = F.moment_regressors(xc[:, None], S.anch_cell, S.anch_item, allrows)[:, 0]
    lit = np.nan_to_num(can.mb.m) @ sign
    lit = (lit - lit.mean()) / lit.std()
    # engagement slope per cell from the canonical per-second channels
    slope = np.zeros(len(S.inc.cells))
    curv = np.zeros(len(S.inc.cells))
    cub = np.zeros(len(S.inc.cells))
    cexp = np.zeros(len(S.inc.cells))
    for v, A in can.sc.arrays.items():
        comp = np.nansum(A * sign, axis=2) / np.maximum(np.isfinite(A).sum(2), 1) * len(sign)
        t = np.arange(A.shape[1], dtype=float)
        t = (t - t.mean()) / t.std()
        t2 = t ** 2 - np.mean(t ** 2)
        xs = np.linspace(-1.0, 1.0, A.shape[1])
        L3 = F.legendre_basis(A.shape[1], 3)
        ex = np.exp(-2.0 * (xs + 1.0))
        ok = np.isfinite(comp)
        for i, ci in enumerate(can.sc.cell_index[v]):
            if ok[i].sum() > 10:
                X = np.column_stack([np.ones(ok[i].sum()), t[ok[i]], t2[ok[i]]])
                coef = np.linalg.lstsq(X, comp[i, ok[i]], rcond=None)[0]
                slope[ci], curv[ci] = coef[1], coef[2]
                cub[ci] = np.linalg.lstsq(L3[ok[i]], comp[i, ok[i]], rcond=None)[0][3]
                cexp[ci] = np.linalg.lstsq(np.column_stack([np.ones(ok[i].sum()), ex[ok[i]]]), comp[i, ok[i]],
                                           rcond=None)[0][1]
    slope = (slope - slope.mean()) / slope.std()
    curv = (curv - curv.mean()) / curv.std()
    cub = (cub - cub.mean()) / cub.std()
    cexp = (cexp - cexp.mean()) / cexp.std()
    ebar = np.nan_to_num(can.mb.ebar) @ sign
    cells = S.inc.cells
    pidx = {p: i for i, p in enumerate(S.persons)}
    cp = cells.person.map(pidx).to_numpy()
    e_person = np.bincount(cp, ebar) / np.bincount(cp)
    e_person = (e_person - e_person.mean()) / e_person.std()
    q = (S.q_raw - S.q_raw.mean()) / S.q_raw.std()
    ea = np.nan_to_num(can.mb.eanch) @ sign
    ea = (ea - ea.mean()) / ea.std()
    rows = S.inc.rows
    key = np.where(rows.anchorable, (rows.uid + "|m" + rows.moment.astype(str)).to_numpy(),
                   (rows.uid + "|i" + rows.item.astype(str)).to_numpy())
    _, grp = np.unique(key, return_inverse=True)
    _, eps_grp = np.unique(key[S.anch_index], return_inverse=True)
    li = F.PRIMARY.index("loss_long")
    ld = F.PRIMARY.index("logdens")
    return Truth(xc, x6, lit, x6[:, li], x6[:, ld], slope, curv, e_person, q, ea, grp, eps_grp, sign, cub, cexp)


def random_direction(rng: np.random.Generator, sign: np.ndarray) -> np.ndarray:
    """Sign-coherent random truth direction: every channel contributes in its engaged direction, with a random
    magnitude (w = s * |g|, g ~ N(0, I), unit norm)."""
    w = sign * np.abs(rng.standard_normal(len(sign)))
    return w / np.linalg.norm(w)


def truth_regressor(T: Truth, truth: str, w: np.ndarray | None = None) -> np.ndarray:
    """The observed-scale engagement regressor whose latent version carries the effect (unit SD)."""
    if truth == "composite":
        return T.x_comp
    if truth == "logdens":
        return T.x_logdens / T.x_logdens.std()
    if truth == "gaze":
        idx = [F.PRIMARY.index(c) for c in F.GAZE]
        x = T.x6[:, idx] @ T.sign[idx]
    elif truth == "validity":
        li = F.PRIMARY.index("loss_long")
        x = T.x6[:, li] * T.sign[li]
    elif truth == "random":
        if w is None:
            raise ValueError("truth 'random' needs a direction")
        x = T.x6 @ w
    else:
        raise ValueError(truth)
    return x / x.std()


# ----------------------------------------------------------------------------- generator
def generate(S: I.SetStructure, T: Truth, sc: Scenario, rep_idx: int, rng: np.random.Generator,
             return_parts: bool = False, w_truth: np.ndarray | None = None):
    m_beta, s_beta, tau = NUISANCE[rep_idx % len(NUISANCE)]
    rows = S.inc.rows
    n_items = int(S.item.max()) + 1
    beta = m_beta + s_beta * rng.standard_normal(n_items)
    z_p = rng.standard_normal(len(S.persons))
    if sc.name == "N2":
        u = tau * (N2_R * T.e_person + np.sqrt(1 - N2_R ** 2) * z_p)
    else:
        u = tau * z_p
    w = W_SD * rng.standard_normal(len(S.inc.cells))
    q = sc.sigma_q * rng.standard_normal(int(T.grp.max()) + 1)
    eps = rng.standard_normal(int(T.eps_grp.max()) + 1)
    a_item = np.exp(0.3 * rng.standard_normal(n_items)) if sc.two_pl else np.ones(n_items)
    lam = np.log(sc.odds_ratio)
    x_obs = truth_regressor(T, sc.truth, w_truth)
    xstar = np.zeros(S.n)
    xstar[S.anch_index] = np.sqrt(sc.rho) * x_obs + np.sqrt(1 - sc.rho) * eps[T.eps_grp]
    lam_row = np.full(S.n, lam)
    if sc.hetero:
        zl = rng.standard_normal(len(S.persons))
        vids = sorted(S.inc.n_s)
        zv = dict(zip(vids, rng.standard_normal(len(vids))))
        lam_row = lam * (1 + 0.5 * zl[S.person]) * (1 + 0.3 * rows.video.map(zv).to_numpy())
    if sc.e5_factor != 1.0:
        lam_row = np.where(rows.experiment.to_numpy() == 5, lam_row * sc.e5_factor, lam_row)
    eta = beta[S.item] + a_item[S.item] * (u[S.person] + w[S.cell]) + q[T.grp] + lam_row * xstar
    if sc.name == "N1":
        pos = rows.quiz_pos.to_numpy()
        apos = np.nan_to_num(rows.anchor_pos.to_numpy(), nan=0.5)
        eta += N1_GAMMA_POS * (pos - 0.5) + N1_KAPPA0 * T.slope[S.cell] + N1_KAPPA * T.slope[S.cell] * 2 * (apos - 0.5)
    elif sc.name == "N1q":
        # non-linear fatigue: learner-specific curvature of engagement x quadratic anchor position
        apos = np.nan_to_num(rows.anchor_pos.to_numpy(), nan=0.5)
        eta += N1_GAMMA_POS * (rows.quiz_pos.to_numpy() - 0.5) + N1_KAPPA0 * T.curv[S.cell] \
            + N1Q_KAPPA * T.curv[S.cell] * ((2 * (apos - 0.5)) ** 2 - 1 / 3)
    elif sc.name in ("N1c", "N1e"):
        # closure out-of-family fatigue shapes (cubic; exponential decrement), learner-specific real coefficients
        x_a = 2 * (np.nan_to_num(rows.anchor_pos.to_numpy(), nan=0.5) - 0.5)
        if sc.name == "N1c":
            coef, shape, kap = T.cub, (5 * x_a ** 3 - 3 * x_a) / 2, N1C_KAPPA
        else:
            coef, shape, kap = T.cexp, np.exp(-2.0 * (x_a + 1.0)) - _E_MEAN, N1E_KAPPA
        eta += N1_GAMMA_POS * (rows.quiz_pos.to_numpy() - 0.5) + N1_KAPPA0 * coef[S.cell] + kap * coef[S.cell] * shape
    elif sc.name == "N3":
        eta += N3_GAMMA_Q * T.q_cell[S.cell]
    elif sc.name == "N4":
        add = np.zeros(S.n)
        add[S.anch_index] = -np.log(N4_OR) * T.x_loss
        eta += add
    p = expit(eta)
    if sc.guessing:
        c = np.where(rows.k_keyed.to_numpy() == 1, 0.25, 0.10)
        p = c + (1 - c) * p
    y = (rng.random(S.n) < p).astype(float)
    info = dict(m_beta=m_beta, s_beta=s_beta, tau=tau, accuracy=float(y.mean()))
    if return_parts:
        return y, info, dict(beta=beta, p_true=p, lam=lam, x_obs=x_obs)
    return y, info


# ----------------------------------------------------------------------------- full-data references
def oracle_tests(S: I.SetStructure, T: Truth, y: np.ndarray) -> dict:
    """Full-data (no CV) references for the clustering question: (a) GLMM Wald on the true composite;
    (b) naive logistic Wald treating responses as independent; (c) the same with a learner-cluster
    sandwich SE; (d) the plan-literal regressor (z - e_bar, not within-cell centred) in the GLMM."""
    can = S.canonical
    out = {}
    D0, pen0 = I.design(S, can, I.BASE)
    base = can.fitter.fit_em(D0, y, pen0)
    for tag, x in (("glmm", T.x_comp), ("literal", T.x_literal)):
        col = np.zeros((S.n, 1))
        col[S.anch_index, 0] = x
        extra = [col]
        if tag == "literal":
            extra.insert(0, T.eanch_comp[S.cell][:, None])
        D = np.hstack([D0] + extra)
        pen = np.r_[pen0, np.full(len(extra), 1e-6)]
        prm, cov = can.fitter.newton(D, y, pen, base.tau2, base.sb2, init=base, want_cov=True)
        se = float(np.sqrt(cov[-1, -1]))
        out[f"{tag}_lambda"] = float(prm.b[-1])
        out[f"{tag}_z"] = float(prm.b[-1] / se)
    out["tau2_hat"], out["sb2_hat"] = base.tau2, base.sb2
    # naive logistic: item fixed effects + Q + x, responses independent
    K = int(S.item.max()) + 1
    X = np.hstack([np.ones((S.n, 1)), np.eye(K)[S.item][:, 1:], can.q[S.cell][:, None], np.zeros((S.n, 1))])
    X[S.anch_index, -1] = T.x_comp
    wv, cov = penalized_logistic(X, y, np.r_[0.0, np.full(X.shape[1] - 1, 1e-6)])
    out["naive_lambda"] = float(wv[-1])
    out["naive_z"] = float(wv[-1] / np.sqrt(cov[-1, -1]))
    r = y - expit(X @ wv)
    U = np.zeros((len(S.persons), X.shape[1]))
    np.add.at(U, S.person, X * r[:, None])
    sand = cov @ (U.T @ U) @ cov
    out["robust_z"] = float(wv[-1] / np.sqrt(sand[-1, -1]))
    return out


# ----------------------------------------------------------------------------- B9 (Lalle-style)
def b9_cv(S: I.SetStructure, y: np.ndarray) -> np.ndarray:
    """Pooled window classifier: reference-free gaze features in each item's window (whole video for
    non-anchorable items), item identity dropped, learner-grouped CV (same splits). Per-row mean loss."""
    rf = [F.PRIMARY.index(c) for c in F.REF_FREE_USED]
    ll = np.zeros(S.n)
    cnt = np.zeros(S.n)
    for sp in S.splits:
        Xw = sp.mb.ebar[S.cell][:, rf].copy()
        Xw[S.anch_index] = np.where(np.isfinite(sp.mb.z[:, rf]), sp.mb.z[:, rf], Xw[S.anch_index])
        Xw = np.nan_to_num(Xw)
        X = np.hstack([np.ones((S.n, 1)), Xw, S.anch[:, None].astype(float)])
        w, _ = penalized_logistic(X[sp.train], y[sp.train], np.r_[0.0, np.full(X.shape[1] - 1, 1.0)])
        p = np.clip(expit(X[sp.test] @ w), 1e-6, 1 - 1e-6)
        ll[sp.test] += -(y[sp.test] * np.log(p) + (1 - y[sp.test]) * np.log1p(-p))
        cnt[sp.test] += 1
    return ll / np.maximum(cnt, 1)


# ----------------------------------------------------------------------------- variants per mode
# Primary CAIRN-linear form for the main grid; fixed by decision S1-D06 from the N1 decision experiment.
PRIMARY_FORM = "dt"
FORMS = {"raw": (I.CL6, I.CLV, I.CLG), "dt": (I.CL6_DT, I.CLV_DT, I.CLG_DT)}


def development_direction(Sd: I.SetStructure, Td: Truth, sc: Scenario, rep_idx: int, rng,
                          primary: I.Variant, w_truth: np.ndarray | None = None) -> tuple[np.ndarray, float]:
    """Simulate the development cohort under the same scenario, fit the primary CAIRN-linear on all of it and
    return its moment-coefficient direction (what Stage 3 would freeze) and its cosine with the true direction."""
    y, _ = generate(Sd, Td, sc, rep_idx, rng, w_truth=w_truth)
    can = Sd.canonical
    D0, pen0 = I.design(Sd, can, I.BASE)
    base = can.fitter.fit_em(D0, y, pen0)
    D, pen = I.design(Sd, can, primary)
    prm = can.fitter.newton(D, y, pen, base.tau2, base.sb2, init=base)
    lam = prm.b[-len(F.PRIMARY):]
    w = lam / (np.linalg.norm(lam) or 1.0)
    return w, float(w @ Td.sign / np.linalg.norm(Td.sign))


def plan_for(set_name: str, sc: Scenario, t2c: bool, mode: str = "main") -> tuple[dict, I.Variant | None]:
    """{variant: tests} and the primary whose development direction is frozen for the lock (or None)."""
    if mode == "n1decision":
        return {I.CL6: ("T1", "T2", "T2c"), I.CL6_DT: ("T1", "T2", "T2c")}, None
    prim, val, gaze = FORMS[PRIMARY_FORM]
    main = ("T1", "T2", "T2c", "T1lr", "T2lr", "T2clr") if t2c else ("T1", "T2", "T1lr", "T2lr")
    plan = {prim: main}
    if sc.name in ("N0", "N3", "N4"):
        plan[val] = ("T2", "T2lr")
    if sc.name == "N1q":
        plan[prim] = ("T1", "T2", "T2c", "T1lr", "T2lr", "T2clr")
    if sc.name == "N4":
        plan[gaze] = ("T2", "T2lr")
    return plan, (prim if set_name != "development" else None)


# ----------------------------------------------------------------------------- one replicate
def run_replicate(S: I.SetStructure, T: Truth, sc: Scenario, rep_idx: int, seed: int, B: int,
                  Sd: I.SetStructure | None = None, Td: Truth | None = None, t2c: bool = True,
                  mode: str = "main") -> dict:
    t0 = time.time()
    ss = np.random.SeedSequence([seed, rep_idx])
    g_out, g_dev, g_perm = (np.random.default_rng(s) for s in ss.spawn(3))
    y, info = generate(S, T, sc, rep_idx, g_out)
    rec = dict(set=S.inc.set_name, scenario=sc.key, rep=rep_idx, seed=seed, B=B, mode=mode, **asdict(sc), **info)
    plan, dir_of = plan_for(S.inc.set_name, sc, t2c, mode)
    variants = list(plan) + [I.WHOLE]
    if dir_of is not None:
        w, cos = development_direction(Sd, Td, sc, rep_idx, g_dev, dir_of)
        dv = I.direction_variant(w, name=f"{dir_of.name}-dir", detrend=dir_of.detrend)
        plan[dv] = ("T1", "T2", "T1lr", "T2lr")
        variants.append(dv)
        rec.update(dev_dir_cosine=cos, dev_dir=json.dumps(np.round(w, 4).tolist()))
    cv = I.cv_evaluate(S, y, variants)
    for v in variants:
        sm = I.summarize(S, y, cv, v.name)
        rec.update({f"{v.name}|{k}": val for k, val in sm.items()})
    for var, tests in plan.items():
        for t, p in I.run_tests(S, y, cv, var, B, g_perm, tests).items():
            rec[f"{var.name}|{t}" if t == "lr_stat" else f"{var.name}|p_{t}"] = p
    llb9 = b9_cv(S, y)
    lb = I.person_balanced(cv.ll_base, S.person)
    rec["B9|s_item"] = 1 - I.person_balanced(llb9, S.person) / lb
    rec.update({f"oracle|{k}": v for k, v in oracle_tests(S, T, y).items()})
    if S.inc.set_name == "development" and mode == "main":
        prim = FORMS[PRIMARY_FORM][0].name
        rec["dev_go"] = bool(rec[f"{prim}|p_T2"] < DEV_STOP_P and rec[f"{prim}|d_auc_wp"] >= DEV_STOP_DAUC)
    rec["primary_form"] = PRIMARY_FORM
    rec["seconds"] = time.time() - t0
    return rec


# ----------------------------------------------------------------------------- closure phase (pre-Stage-2)
# Modes are declared in docs/research/novel_method/closure/evidence/predeclared_rules.md before their runs.
#   rf    rule R-F: temporal control, polynomial within-recording detrend of degree d in {1, 2, 3}, for the six-channel
#         block (P6) and the unit-weighted composite (P0); LR statistics under T1 / T2 / T2c.
#   rg    rule R-G: parametrization at the chosen degree: P6, P0, PT (anisotropic ridge), PD (frozen development
#         direction) and PA = min-p(P0, P6), all under one set of permutation draws per null.
#   conf  rule R-H: the selected design, its CV fallback, closed testing of E4 and E5 inside pooled replicates,
#         per-cohort lambda estimates, usefulness metrics and the development stop rule.
#   nh4   rule R-I: NH4 attribution, the gaze block conditional on the in-window validity term.
CLOSURE_DEGREES = (1, 2, 3)
_SUB = {}


def closure_variants(mode: str, d: int, chosen: str = "") -> dict:
    """{'lr': [...], 'combos': {...}, 'cv': [...], 'dev_dir': bool} for a closure mode at detrend degree d."""
    if mode == "rf":
        lr = [v for k in CLOSURE_DEGREES for v in (I.six_variant(k), I.unit_variant(k))]
        return dict(lr=lr, combos={}, cv=list(lr), dev_dir=False)
    if mode == "rg":
        lr = [I.six_variant(d), I.unit_variant(d), I.aniso_variant(d)]
        return dict(lr=lr, combos={f"CAIRN-a-dt{d}": [lr[1].name, lr[0].name]}, cv=list(lr), dev_dir=True)
    if mode == "nh4":
        val = I.Variant(f"CAIRN-validity-dt{d}", channels=(F.PRIMARY.index("loss_long"),), person_anch=True, detrend=True,
                        trend=d)
        gaze = I.Variant(f"CAIRN-gaze-dt{d}", channels=tuple(F.PRIMARY.index(c) for c in F.GAZE), person_anch=True,
                         detrend=True, trend=d)
        return dict(lr=[I.gaze_given_validity_variant(d), val, gaze], combos={}, cv=[], dev_dir=False)
    if mode == "conf":
        if chosen == "PA":                                   # adaptive: P0 and P6 jointly, min-p combination
            p0, p6 = I.unit_variant(d), I.six_variant(d)
            return dict(lr=[p0, p6], combos={f"CAIRN-a-dt{d}": [p0.name, p6.name]}, cv=[p0, p6], dev_dir=False,
                        chosen=None, chosen_name=f"CAIRN-a-dt{d}")
        if chosen == "PD":                                   # direction frozen from the (simulated) development fit
            return dict(lr=[], combos={}, cv=[], dev_dir=True, chosen=None, chosen_name=f"CAIRN-d-dt{d}")
        v = closure_chosen(chosen, d)
        return dict(lr=[v], combos={}, cv=[v], dev_dir=False, chosen=v, chosen_name=v.name)
    raise ValueError(mode)


def closure_chosen(chosen: str, d: int) -> I.Variant:
    return {"P6": I.six_variant, "P0": I.unit_variant, "PT": I.aniso_variant}[chosen](d)


def _sub_rows(S: I.SetStructure, Ssub: I.SetStructure) -> np.ndarray:
    """Row index into S for every row of Ssub (same (uid, item) keys)."""
    k = (id(S), id(Ssub))
    if k not in _SUB:
        pos = {(u, j): i for i, (u, j) in enumerate(zip(S.inc.rows.uid, S.inc.rows.item))}
        _SUB[k] = np.array([pos[(u, j)] for u, j in zip(Ssub.inc.rows.uid, Ssub.inc.rows.item)])
    return _SUB[k]


def run_replicate_closure(S: I.SetStructure, T: Truth, sc: Scenario, rep_idx: int, seed: int, B: int, mode: str,
                          degree: int = 1, Sd: I.SetStructure | None = None, Td: Truth | None = None,
                          subs: dict | None = None, chosen: str = "", cv_tests: tuple = (), dev_stop: bool = False,
                          tests: tuple = ("T1lr", "T2lr", "T2clr")) -> dict:
    """One closure replicate. ``subs``: {set_name: (Ssub, Tsub)} elementary cohorts analysed on the same outcomes
    (closed testing of E4 and E5 inside the pooled lock). ``cv_tests``: CV permutation tests of the chosen variant
    (the CV fallback). ``dev_stop``: development stop rule (CV T2 p < .10 and CV dAUC_wp >= .01)."""
    t0 = time.time()
    ss = np.random.SeedSequence([seed, rep_idx])
    g_out, g_dev, g_perm, g_dir, g_sub, g_cvt = (np.random.default_rng(s) for s in ss.spawn(6))
    w_lock = w_dev = None
    if sc.truth == "random":
        w_lock = random_direction(g_dir, T.sign)
        w_dev = random_direction(g_dir, T.sign) if sc.dev_truth == "random_indep" else w_lock
    y, info = generate(S, T, sc, rep_idx, g_out, w_truth=w_lock)
    rec = dict(set=S.inc.set_name, scenario=sc.key, rep=rep_idx, seed=seed, B=B, mode=f"closure-{mode}", degree=degree,
               **asdict(sc), **info)
    if w_lock is not None:
        rec["w_truth"] = json.dumps(np.round(w_lock, 4).tolist())
    plan = closure_variants(mode, degree, chosen)
    if mode == "conf" and chosen == "PD" and S.inc.set_name == "development":
        # in development the PD design's primary is P6 itself (it produces the direction frozen for the lock)
        plan = closure_variants("conf", degree, "P6")
    lr = list(plan["lr"])
    combos = dict(plan["combos"])
    if plan["dev_dir"] and Sd is not None:
        prim = I.six_variant(degree)
        sc_dev = sc if sc.dev_truth in ("", "random_indep") else Scenario(**{**asdict(sc), "truth": sc.dev_truth,
                                                                              "dev_truth": ""})
        w, _ = development_direction(Sd, Td, sc_dev, rep_idx, g_dev, prim, w_truth=w_dev)
        w_true = (w_lock if w_lock is not None else _truth_weights(sc.truth, T.sign))
        rec["dev_dir_cosine"] = float(w @ w_true / np.linalg.norm(w_true))
        rec["dev_dir"] = json.dumps(np.round(w, 4).tolist())
        lr.append(I.direction_variant(w, name=f"CAIRN-d-dt{degree}", detrend=True, trend=degree))
        if mode == "conf":
            plan["cv"] = [lr[-1]]
            plan["chosen"] = lr[-1]
    rec.update(I.lr_tests_joint(S, y, lr, B, g_perm, tests, combos))
    if plan["cv"]:
        cvv = list(plan["cv"]) + ([lr[-1]] if plan["dev_dir"] and Sd is not None and mode != "conf" else [])
        cv = I.cv_evaluate(S, y, cvv)
        for v in cvv:
            rec.update({f"{v.name}|{k}": val for k, val in I.summarize(S, y, cv, v.name).items()})
        if cv_tests or dev_stop:
            ts = tuple(cv_tests) + (("T2",) if dev_stop and "T2" not in cv_tests else ())
            if mode == "conf" and plan.get("chosen") is None:     # PA: joint CV permutations, min-p
                rec.update(I.cv_tests_joint(S, y, cv, cvv, B, g_cvt, ts, combos))
                v0n = plan["chosen_name"]
                rec[f"{v0n}|d_auc_wp"] = rec.get(f"{cvv[0].name}|d_auc_wp")    # usefulness of PA = its P0 model
            else:
                v0 = plan.get("chosen") or cvv[0]
                v0n = v0.name
                for t, p in I.run_tests(S, y, cv, v0, B, g_cvt, ts).items():
                    rec[f"{v0n}|p_{t}"] = p
            if dev_stop:
                rec["dev_go"] = bool(rec[f"{v0n}|p_T2"] < DEV_STOP_P and rec[f"{v0n}|d_auc_wp"] >= DEV_STOP_DAUC)
    if mode == "conf" and plan.get("chosen") is not None:
        v0 = plan["chosen"]
        if v0.direction is not None:
            rec.update({f"{v0.name}|{k}": val for k, val in I.lambda_hat(S, y, v0).items()})
    for name, (Ssub, Tsub) in (subs or {}).items():
        ysub = y[_sub_rows(S, Ssub)]
        r = I.lr_tests_joint(Ssub, ysub, lr, B, g_sub, tests, combos)
        rec.update({f"{name}::{k}": val for k, val in r.items()})
        if mode == "conf" and lr and lr[0].direction is not None:
            rec.update({f"{name}::{lr[0].name}|{k}": val for k, val in I.lambda_hat(Ssub, ysub, lr[0]).items()})
    rec["seconds"] = time.time() - t0
    return rec


def _truth_weights(truth: str, sign: np.ndarray) -> np.ndarray:
    """Channel weights of a named truth (for the development-direction cosine)."""
    w = np.zeros(len(sign))
    if truth == "composite":
        w = sign.copy()
    elif truth == "logdens":
        w[F.PRIMARY.index("logdens")] = 1.0
    elif truth == "gaze":
        for c in F.GAZE:
            w[F.PRIMARY.index(c)] = sign[F.PRIMARY.index(c)]
    elif truth == "validity":
        w[F.PRIMARY.index("loss_long")] = sign[F.PRIMARY.index("loss_long")]
    else:
        w = sign.copy()
    return w / np.linalg.norm(w)
