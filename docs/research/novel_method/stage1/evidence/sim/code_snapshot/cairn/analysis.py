"""Summaries of the Stage-1 simulation (spec §1.7): calibration, power curves, minimum detectable effects,
joint T1/T2 behaviour, the clustering question, and the mapping of odds ratios to S_item / dAUC_wp.

Everything here reads simulation output (synthetic outcomes) only.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kstest, norm, spearmanr

ALPHA = 0.05


# ----------------------------------------------------------------------------- loading
def load(out_dir: Path) -> pd.DataFrame:
    rows = []
    for p in sorted(Path(out_dir).glob("*/*.jsonl")):
        rows += [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
    d = pd.DataFrame(rows)
    if d.empty:
        return d
    d["realism"] = np.where((d.sigma_q == 0.5) & ~d.two_pl & ~d.guessing & ~d.hetero & (d.truth == "composite")
                            & (d.e5_factor == 1.0), "base", "sensitivity")
    return d


def variants(d: pd.DataFrame) -> list:
    return sorted({c.split("|")[0] for c in d.columns if c.endswith("|p_T1")})


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


# (learner-block test, moment test, intersection) for the CV and LR statistics
IUT_PAIRS = (("T1", "T2", "NH1"), ("T1", "T2c", "NH1c"), ("T1lr", "T2lr", "NH1lr"), ("T1lr", "T2clr", "NH1clr"))


def add_iut(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    for v in variants(d):
        for a, b, nh in IUT_PAIRS:
            t1, t2 = d.get(f"{v}|p_{a}"), d.get(f"{v}|p_{b}")
            if t1 is not None and t2 is not None:
                d[f"{v}|p_{nh}"] = np.where(t1.notna() & t2.notna(), np.maximum(t1, t2), np.nan)   # IUT p-value
    return d


def test_columns(d: pd.DataFrame) -> list:
    return [c for c in d.columns if "|p_" in c]


# ----------------------------------------------------------------------------- calibration
def rejection_table(d: pd.DataFrame, alpha: float = ALPHA) -> pd.DataFrame:
    d = add_iut(d)
    out = []
    for (s, scen), g in d.groupby(["set", "scenario"]):
        for c in test_columns(g):
            p = g[c].dropna()
            if p.empty:
                continue
            k = int((p <= alpha).sum())
            lo, hi = wilson(k, len(p))
            v, t = c.split("|p_")
            out.append(dict(set=s, scenario=scen, name=g.name.iloc[0], odds_ratio=g.odds_ratio.iloc[0], rho=g.rho.iloc[0],
                            realism=g.realism.iloc[0], variant=v, test=t, n=len(p), rate=k / len(p), ci_lo=lo, ci_hi=hi,
                            mean_p=float(p.mean()), B=int(g.B.iloc[0])))
        if "dev_go" in g:
            k = int(g.dev_go.sum())
            lo, hi = wilson(k, len(g))
            out.append(dict(set=s, scenario=scen, name=g.name.iloc[0], odds_ratio=g.odds_ratio.iloc[0], rho=g.rho.iloc[0],
                            realism=g.realism.iloc[0], variant="stop-rule", test="go", n=len(g), rate=k / len(g),
                            ci_lo=lo, ci_hi=hi, mean_p=np.nan, B=int(g.B.iloc[0])))
        for tag in ("naive", "robust", "glmm", "literal"):
            z = g.get(f"oracle|{tag}_z")
            if z is not None:
                k = int((z > norm.ppf(1 - alpha)).sum())
                lo, hi = wilson(k, len(z))
                out.append(dict(set=s, scenario=scen, name=g.name.iloc[0], odds_ratio=g.odds_ratio.iloc[0], rho=g.rho.iloc[0],
                                realism=g.realism.iloc[0], variant=f"full-data {tag} Wald", test="one-sided z", n=len(z),
                                rate=k / len(z), ci_lo=lo, ci_hi=hi, mean_p=np.nan, B=0))
    return pd.DataFrame(out)


def uniformity(d: pd.DataFrame, set_name: str, scenario: str) -> dict:
    g = d[(d.set == set_name) & (d.scenario == scenario)]
    out = {}
    rng = np.random.default_rng(0)
    for c in [c for c in test_columns(g) if g[c].notna().any()]:
        p = g[c].dropna().to_numpy()
        pr = p - rng.random(len(p)) / (1 + g.B.iloc[0])          # randomized p-values (continuous under H0)
        out[c] = dict(n=len(p), ks_p=float(kstest(pr, "uniform").pvalue), mean=float(p.mean()))
    return out


# ----------------------------------------------------------------------------- joint T1/T2
def joint_table(d: pd.DataFrame, variant: str, alpha: float = ALPHA) -> pd.DataFrame:
    out = []
    for (s, scen), g in d.groupby(["set", "scenario"]):
        a, b = g.get(f"{variant}|p_T1"), g.get(f"{variant}|p_T2")
        if a is None or b is None or a.isna().all():
            continue
        r1, r2 = a <= alpha, b <= alpha
        rho = spearmanr(a, b).statistic if a.nunique() > 1 and b.nunique() > 1 else np.nan
        out.append(dict(set=s, scenario=scen, n=len(g), T1=r1.mean(), T2=r2.mean(), both=(r1 & r2).mean(),
                        T1_only=(r1 & ~r2).mean(), T2_only=(~r1 & r2).mean(), neither=(~r1 & ~r2).mean(),
                        p_spearman=rho, P_T2_given_T1=(r1 & r2).sum() / max(r1.sum(), 1)))
    return pd.DataFrame(out)


# ----------------------------------------------------------------------------- power and MDE
def power_curves(d: pd.DataFrame, alpha: float = ALPHA) -> pd.DataFrame:
    """Rejection rates on the alternative grid (base realism) with the pure null N0 as OR = 1."""
    d = add_iut(d)
    base = d[(d.realism == "base") & d.name.isin(["ALT", "N0"])]
    out = []
    for (s, scen), g in base.groupby(["set", "scenario"]):
        rhos = [g.rho.iloc[0]] if g.name.iloc[0] == "ALT" else [0.2, 0.4, 0.7]
        for c in test_columns(g):
            p = g[c].dropna()
            if p.empty:
                continue
            k = int((p <= alpha).sum())
            lo, hi = wilson(k, len(p))
            v, t = c.split("|p_")
            for rho in rhos:
                out.append(dict(set=s, variant=v, test=t, odds_ratio=float(g.odds_ratio.iloc[0]), rho=rho, n=len(p),
                                power=k / len(p), ci_lo=lo, ci_hi=hi))
        for tag in ("naive", "robust", "glmm"):
            z = g.get(f"oracle|{tag}_z")
            if z is None:
                continue
            k = int((z > norm.ppf(1 - alpha)).sum())
            lo, hi = wilson(k, len(z))
            for rho in rhos:
                out.append(dict(set=s, variant=f"full-data {tag} Wald", test="z", odds_ratio=float(g.odds_ratio.iloc[0]),
                                rho=rho, n=len(z), power=k / len(z), ci_lo=lo, ci_hi=hi))
    return pd.DataFrame(out).sort_values(["set", "variant", "test", "rho", "odds_ratio"]).reset_index(drop=True)


def interpolate_or(x_or: np.ndarray, y: np.ndarray, target: float) -> float:
    """Smallest OR at which y (monotone-smoothed) reaches target, linear in log OR; inf if never; 1 if at OR 1."""
    o = np.asarray(x_or, float)
    v = np.maximum.accumulate(np.asarray(y, float))          # monotone envelope (MC noise)
    order = np.argsort(o)
    o, v = o[order], v[order]
    if v[0] >= target:
        return float(o[0])
    for i in range(1, len(o)):
        if v[i] >= target:
            lo, hi = np.log(o[i - 1]), np.log(o[i])
            f = (target - v[i - 1]) / (v[i] - v[i - 1]) if v[i] > v[i - 1] else 1.0
            return float(np.exp(lo + f * (hi - lo)))
    return float("inf")


def mde_table(curves: pd.DataFrame, target: float = 0.8) -> pd.DataFrame:
    out = []
    for (s, v, t, rho), g in curves.groupby(["set", "variant", "test", "rho"]):
        if (g.odds_ratio > 1).sum() < 2:
            continue
        out.append(dict(set=s, variant=v, test=t, rho=rho, mde_or=interpolate_or(g.odds_ratio, g.power, target),
                        max_or=g.odds_ratio.max(), power_at_max=float(g.power[g.odds_ratio.idxmax()])))
    return pd.DataFrame(out)


def metric_means(d: pd.DataFrame) -> pd.DataFrame:
    base = d[(d.realism == "base") & d.name.isin(["ALT", "N0"])]
    out = []
    for (s, scen), g in base.groupby(["set", "scenario"]):
        for v in sorted({c.split("|")[0] for c in g.columns if c.endswith("|s_item")}):
            si, da = g.get(f"{v}|s_item"), g.get(f"{v}|d_auc_wp")
            if si is None or si.isna().all():
                continue
            rhos = [g.rho.iloc[0]] if g.name.iloc[0] == "ALT" else [0.2, 0.4, 0.7]
            for rho in rhos:
                out.append(dict(set=s, variant=v, odds_ratio=float(g.odds_ratio.iloc[0]), rho=rho, n=int(si.notna().sum()),
                                s_item=float(si.mean()), s_item_sd=float(si.std()), d_auc_wp=float(da.mean()) if da is not None else np.nan,
                                d_auc_wp_sd=float(da.std()) if da is not None else np.nan,
                                futility_z1645=float((g.get(f"{v}|s_item_upper_z1645", pd.Series(np.nan)) < 0.01).mean()),
                                futility_z3=float((g.get(f"{v}|s_item_upper_z3", pd.Series(np.nan)) < 0.01).mean())))
    return pd.DataFrame(out)


# ----------------------------------------------------------------------------- analytic comparison (plan §20.3)
def analytic_power(n_resp: int, p_correct: float, odds_ratio: np.ndarray, rho: float, two_sided: bool = True,
                   alpha: float = ALPHA) -> np.ndarray:
    """Plan §20.3: Wald test of lambda with independent responses, SE = 1/sqrt(N p (1 - p)) per SD of the
    observed within-learner signal; observed effect = log(OR) sqrt(rho)."""
    se = 1 / np.sqrt(n_resp * p_correct * (1 - p_correct))
    lam = np.log(np.asarray(odds_ratio, float)) * np.sqrt(rho)
    z = norm.ppf(1 - alpha / 2) if two_sided else norm.ppf(1 - alpha)
    return norm.cdf(lam / se - z)


def design_effect(d: pd.DataFrame, set_name: str) -> dict:
    """Empirical variance of the full-data GLMM / naive lambda-hat under N0 versus their model-based variances."""
    g = d[(d.set == set_name) & (d.scenario.str.startswith("N0_")) & (d.realism == "base")]
    if g.empty:
        return {}
    out = dict(n=len(g))
    for tag in ("glmm", "naive"):
        lam, z = g[f"oracle|{tag}_lambda"], g[f"oracle|{tag}_z"]
        se = (lam / z).abs()
        out[f"{tag}_emp_sd"] = float(lam.std())
        out[f"{tag}_model_se"] = float(np.sqrt((se ** 2).mean()))
        out[f"{tag}_variance_ratio"] = float(lam.var() / (se ** 2).mean())
    out["mean_accuracy"] = float(g.accuracy.mean())
    return out


# ----------------------------------------------------------------------------- population metrics
def population_metrics(S, T, odds_ratio: float, rho: float, n_draw: int = 32, seed: int = 0) -> dict:
    """Infinite-training-data S_item and dAUC_wp of the oracle CAIRN predictor (true lambda, true item easiness,
    latent terms integrated out) over the oracle IRT predictor, by Monte Carlo over the generator."""
    from . import inference as I
    from .model import C2
    from .simulate import NUISANCE, W_SD, Scenario, generate
    from scipy.special import expit

    sc = Scenario("ALT", odds_ratio, rho)
    lam = np.log(odds_ratio)
    s_items, daucs = [], []
    cell_person = S.inc.cells.person.map({p: i for i, p in enumerate(S.persons)}).to_numpy()
    rng = np.random.default_rng(seed)
    for r in range(n_draw):
        y, info, parts = generate(S, T, sc, r, rng, return_parts=True)
        tau = NUISANCE[r % len(NUISANCE)][2]
        base_v = tau ** 2 + W_SD ** 2 + sc.sigma_q ** 2
        beta = parts["beta"][S.item]
        xo = np.zeros(S.n)
        xo[S.anch_index] = parts["x_obs"]
        anch = S.anch
        p_full = np.where(anch, expit((beta + lam * np.sqrt(rho) * xo) / np.sqrt(1 + C2 * (base_v + lam ** 2 * (1 - rho)))),
                          expit(beta / np.sqrt(1 + C2 * base_v)))
        p_irt = np.where(anch, expit(beta / np.sqrt(1 + C2 * (base_v + lam ** 2))), expit(beta / np.sqrt(1 + C2 * base_v)))
        pt = parts["p_true"]
        ll_f = -(pt * np.log(p_full) + (1 - pt) * np.log1p(-p_full))
        ll_b = -(pt * np.log(p_irt) + (1 - pt) * np.log1p(-p_irt))
        lf, lb = I.person_balanced(ll_f, S.person), I.person_balanced(ll_b, S.person)
        s_items.append(1 - lf / lb)
        daucs.append(I.delta_auc_wp(y, p_full, p_irt, S.cell, cell_person))
    return dict(odds_ratio=odds_ratio, rho=rho, s_item_pop=float(np.mean(s_items)), d_auc_wp_pop=float(np.nanmean(daucs)))


def useful_or(means: pd.DataFrame, s_thr: float = 0.01, auc_thr: float = 0.02, cols=("s_item", "d_auc_wp")) -> pd.DataFrame:
    """Smallest OR whose mean metric meets both thresholds (R-B), per set, variant, rho."""
    out = []
    for (s, v, rho), g in means.groupby(["set", "variant", "rho"]):
        g = g.sort_values("odds_ratio")
        o1 = interpolate_or(g.odds_ratio, g[cols[0]], s_thr)
        o2 = interpolate_or(g.odds_ratio, g[cols[1]], auc_thr)
        out.append(dict(set=s, variant=v, rho=rho, or_s_item=o1, or_d_auc=o2, or_useful=max(o1, o2)))
    return pd.DataFrame(out)


def power_at(curves: pd.DataFrame, set_name: str, variant: str, test: str, rho: float, odds_ratio: float) -> float:
    g = curves[(curves.set == set_name) & (curves.variant == variant) & (curves.test == test) & (curves.rho == rho)]
    g = g.sort_values("odds_ratio")
    if g.empty or not np.isfinite(odds_ratio):
        return np.nan
    lo = np.log(g.odds_ratio.to_numpy())
    v = np.maximum.accumulate(g.power.to_numpy())
    x = np.log(odds_ratio)
    if x > lo[-1]:
        return float(v[-1]) if x - lo[-1] < 1e-9 else np.nan
    return float(np.interp(x, lo, v))
