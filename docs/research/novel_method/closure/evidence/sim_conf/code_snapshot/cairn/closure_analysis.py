"""Mechanical application of the closure-phase rules (``closure/evidence/predeclared_rules.md``) to stored replicates.

Everything here reads simulation output (synthetic outcomes) only. Each ``rule_*`` function returns the full table it
used together with the decision, so the report shows exactly how a decision followed from the rule.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .analysis import wilson

ALPHA = 0.05
BOUND = 0.07
NULLS_F = ("N0", "N1", "N1q", "N1c", "N1e")
NULLS_ALL = ("N0", "N1", "N2", "N3", "N1q", "N1c", "N1e")
TRUTHS = (("composite", ""), ("random", ""), ("logdens", ""), ("gaze", ""), ("validity", ""), ("random", "random_indep"))
ORDER = ("P6", "PT", "P0", "PD", "PA")


def vname(param: str, d: int) -> str:
    if param == "P6":
        return "CAIRN-linear-dt" if d == 1 else f"CAIRN-linear-dt{d}"
    return {"P0": "CAIRN-u-dt", "PT": "CAIRN-t-dt", "PD": "CAIRN-d-dt", "PA": "CAIRN-a-dt"}[param] + str(d)


def load(out_dir: Path) -> pd.DataFrame:
    rows = []
    for p in sorted(Path(out_dir).glob("*/*.jsonl")):
        rows += [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
    d = pd.DataFrame(rows)
    if not d.empty:
        d["dev_truth"] = d.get("dev_truth", pd.Series("", index=d.index)).fillna("")
    return d


def _p(d: pd.DataFrame, col: str) -> pd.Series:
    return d[col] if col in d else pd.Series(np.nan, index=d.index)


def pvals(d: pd.DataFrame, prefix: str, var: str, test: str) -> pd.Series:
    """p-values of one test; NH1 / NH1lr / NH1c... are intersection-union (max of the two)."""
    pre = f"{prefix}::" if prefix else ""
    if test in ("NH1", "NH1lr", "NH1clr"):
        a, b = {"NH1": ("T1", "T2"), "NH1lr": ("T1lr", "T2lr"), "NH1clr": ("T1lr", "T2clr")}[test]
        return np.maximum(_p(d, f"{pre}{var}|p_{a}"), _p(d, f"{pre}{var}|p_{b}"))
    return _p(d, f"{pre}{var}|p_{test}")


def rate(d: pd.DataFrame, prefix: str, var: str, test: str) -> dict:
    p = pvals(d, prefix, var, test).dropna()
    k = int((p <= ALPHA).sum())
    lo, hi = wilson(k, len(p)) if len(p) else (np.nan, np.nan)
    return dict(n=len(p), rate=k / len(p) if len(p) else np.nan, ci_lo=lo, ci_hi=hi)


def null_rows(d: pd.DataFrame, sets, nulls, var: str, tests, prefix: str = "") -> pd.DataFrame:
    out = []
    for s in sets:
        for n in nulls:
            g = d[(d.set == s) & (d.name == n) & (d.odds_ratio == 1.0) & ~d.two_pl & ~d.guessing]
            if g.empty:
                continue
            for t in tests:
                r = rate(g, prefix, var, t)
                if r["n"]:
                    out.append(dict(set=s if not prefix else f"{s}::{prefix}", scenario=n, variant=var, test=t, **r))
    return pd.DataFrame(out)


# ----------------------------------------------------------------------------- R-F
def rule_rf(d: pd.DataFrame) -> dict:
    tab = []
    for k in (1, 2, 3):
        for param in ("P6", "P0"):
            t = null_rows(d, ("locked_pooled", "locked_primary", "development"), NULLS_F, vname(param, k),
                          ("T1lr", "T2lr", "NH1lr", "T2clr"))
            t["degree"], t["param"] = k, param
            tab.append(t)
    tab = pd.concat(tab, ignore_index=True)
    decisive = tab[tab.set.isin(["locked_pooled", "locked_primary"]) & tab.test.isin(["T1lr", "T2lr", "NH1lr"])]
    per_d = decisive.groupby("degree").agg(max_rate=("rate", "max"), n_cells=("rate", "size"),
                                           n_over=("rate", lambda r: int((r > BOUND).sum()))).reset_index()
    passing = per_d[per_d.max_rate <= BOUND].degree.tolist()
    chosen = int(min(passing)) if passing else int(per_d.sort_values("max_rate").degree.iloc[0])
    power = []
    for k in (1, 2, 3):
        for param in ("P6", "P0"):
            for s in ("locked_pooled", "locked_primary", "development"):
                for truth in ("composite", "random"):
                    g = d[(d.set == s) & (d.name == "ALT") & (d.odds_ratio == 1.5) & (d.truth == truth)]
                    r = rate(g, "", vname(param, k), "NH1lr")
                    if r["n"]:
                        power.append(dict(degree=k, param=param, set=s, truth=truth, **r))
    return dict(table=tab, per_degree=per_d, passing=passing, chosen=chosen, resolved=bool(passing), power=pd.DataFrame(power))


# ----------------------------------------------------------------------------- R-G
def rule_rg(d: pd.DataFrame, k: int) -> dict:
    adm, pw = [], []
    for param in ORDER:
        v = vname(param, k)
        t = null_rows(d, ("locked_pooled",), NULLS_ALL, v, ("T1lr", "T2lr", "NH1lr", "T2clr"))
        t["param"] = param
        adm.append(t)
        for o in (1.35, 1.5):
            for truth, dt in TRUTHS:
                g = d[(d.set == "locked_pooled") & (d.name == "ALT") & (d.odds_ratio == o) & (d.truth == truth)
                      & (d.dev_truth == dt)]
                r = rate(g, "", v, "NH1lr")
                pw.append(dict(param=param, odds_ratio=o, truth=truth + (f"/{dt}" if dt else ""), **r))
    adm = pd.concat(adm, ignore_index=True)
    pw = pd.DataFrame(pw)
    dec = adm[adm.test.isin(["T1lr", "T2lr", "NH1lr"])]
    summ = []
    for param in ORDER:
        a = dec[dec.param == param]
        p = pw[pw.param == param]
        summ.append(dict(param=param, max_null=float(a.rate.max()), admissible=bool(len(a) and a.rate.max() <= BOUND),
                         score=float(p.rate.mean()), min_power=float(p.rate.min()), n_cells=int(p.rate.notna().sum())))
    summ = pd.DataFrame(summ)
    p6_min = float(summ.loc[summ.param == "P6", "min_power"].iloc[0])
    summ["robust"] = summ.min_power >= p6_min - 0.05
    ok = summ[summ.admissible & summ.robust]
    if ok.empty:
        chosen = "P6"
    else:
        best = ok.score.max()
        near = ok[ok.score >= best - 0.02]
        chosen = min(near.param, key=ORDER.index)
    return dict(admissibility=adm, power=pw, summary=summ, chosen=chosen)


# ----------------------------------------------------------------------------- R-H / R-J
def conf_checks(d: pd.DataFrame, param: str, k: int) -> dict:
    v = vname(param, k)
    pooled = null_rows(d, ("locked_pooled",), NULLS_ALL, v, ("T1lr", "T2lr", "NH1lr", "T2clr", "T1", "T2", "NH1"))
    subs = pd.concat([null_rows(d, ("locked_pooled",), NULLS_ALL, v, ("T1lr", "T2lr", "NH1lr"), prefix=s)
                      for s in ("locked_primary", "locked_secondary")], ignore_index=True)
    dev = d[(d.set == "development") & (d.odds_ratio == 1.0)]
    go = []
    for n in NULLS_ALL:
        g = dev[dev.name == n]
        if len(g) and "dev_go" in g:
            k_ = int(g.dev_go.astype(bool).sum())
            go.append(dict(scenario=n, n=len(g), false_go=k_ / len(g)))
    go = pd.DataFrame(go)
    crit = dict(
        pooled_lr=bool((pooled[pooled.test.isin(["T1lr", "T2lr", "NH1lr"])].rate <= BOUND).all()),
        elementary_nh1lr=bool((subs[subs.test == "NH1lr"].rate <= BOUND).all()),
        cv_fallback=bool((pooled[pooled.test.isin(["T1", "T2", "NH1"])].rate <= BOUND).all()),
        false_go=bool(go.empty or (go.false_go <= 0.10).all()))
    return dict(pooled=pooled, elementary=subs, false_go=go, criteria=crit, passed=all(crit.values()))


def power_table(d: pd.DataFrame, param: str, k: int, sets=("locked_pooled",)) -> pd.DataFrame:
    v = vname(param, k)
    out = []
    alt = d[d.name == "ALT"]
    for keys, g in alt.groupby(["set", "rho", "truth", "odds_ratio", "two_pl", "guessing", "hetero", "sigma_q", "e5_factor"]):
        s, rho, truth, o, tp, gu, he, sq, e5 = keys
        if s not in sets:
            continue
        rec = dict(set=s, rho=rho, truth=truth, odds_ratio=o, sensitivity=",".join(
            n for n, on in (("2pl", tp), ("guess", gu), ("het", he), ("noLD", sq == 0), (f"e5x{e5:g}", e5 != 1.0)) if on) or "base")
        for t in ("NH1lr", "T1lr", "T2lr", "NH1"):
            rec[t] = rate(g, "", v, t)["rate"]
        for sub in ("locked_primary", "locked_secondary"):
            rec[f"{sub}_closed"] = float(np.mean((pvals(g, "", v, "NH1lr") <= ALPHA) & (pvals(g, sub, v, "NH1lr") <= ALPHA))) \
                if f"{sub}::{v}|p_T1lr" in g else np.nan
        if "dev_go" in g:
            rec["go"] = float(g.dev_go.astype(bool).mean())
        for m in ("s_item", "d_auc_wp"):
            c = f"{v}|{m}"
            rec[m] = float(g[c].mean()) if c in g else np.nan
        rec["n"] = len(g)
        out.append(rec)
    return pd.DataFrame(out)


def mde(curve: pd.DataFrame, col: str = "NH1lr", target: float = 0.8) -> float:
    c = curve.sort_values("odds_ratio")
    x, y = np.log(c.odds_ratio.to_numpy(float)), c[col].to_numpy(float)
    for i in range(1, len(x)):
        if y[i - 1] < target <= y[i]:
            return float(np.exp(x[i - 1] + (target - y[i - 1]) * (x[i] - x[i - 1]) / (y[i] - y[i - 1])))
    return float("nan")


def rj_record(d: pd.DataFrame, param: str, k: int, anchor_table: Path, design_config: Path, manifest_sha256: str) -> dict:
    from .paths import sha256_file
    c = conf_checks(d, param, k)
    pw = power_table(d, param, k)
    p15 = pw[(pw.odds_ratio == 1.5) & (pw.truth == "random") & (pw.sensitivity == "base")]
    power15 = float(p15.NH1lr.iloc[0]) if len(p15) else float("nan")
    return dict(rule="R-J", passed=c["passed"], criteria=c["criteria"], power_or15_random=power15,
                power_floor_breached=bool(power15 < 0.5), anchor_table=str(anchor_table),
                anchor_table_sha256=sha256_file(anchor_table), design_config_sha256=sha256_file(design_config),
                manifest_sha256=manifest_sha256, max_null_rate=float(c["pooled"].rate.max()))
