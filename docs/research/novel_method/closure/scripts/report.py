"""Closure-phase tables, figures and summary from the stored replicates (synthetic outcomes only).

    python report.py            # writes evidence/tables/*.csv, evidence/tables/report_tables.md, evidence/summary.json,
                                # evidence/figures/*.png

Every decision is recomputed with ``cairn.closure_analysis`` (rules R-F, R-G, R-H, R-I), so the report shows how each
decision follows from its pre-declared rule.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from cairn import closure_analysis as CA

EV = Path(__file__).resolve().parents[1] / "evidence"
TAB = EV / "tables"
FIG = EV / "figures"


def fmt(x, d=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    return f"{x:.{d}f}" if isinstance(x, (float, np.floating)) else str(x)


def md(df: pd.DataFrame, digits: int = 3) -> str:
    if df is None or df.empty:
        return "_(no data)_\n"
    cols = list(df.columns)
    out = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(fmt(r[c], digits) for c in cols) + " |")
    return "\n".join(out) + "\n"


def stage1_reference() -> pd.DataFrame:
    """Stage-1 designs 1, 5, 7 power curves at rho = .4 (composite truth) for the comparison figure."""
    p = Path(__file__).resolve().parents[2] / "stage1/evidence/tables/power_curves.csv"
    if not p.exists():
        return pd.DataFrame()
    c = pd.read_csv(p)
    keep = []
    for s, v, t, lab in (("locked_primary", "CAIRN-linear-dt", "NH1", "Stage-1 design 1 (E4, CV)"),
                         ("locked_pooled", "CAIRN-linear-dt", "NH1", "Stage-1 design 5 (pooled, CV)"),
                         ("locked_pooled", "CAIRN-linear-dt", "NH1lr", "Stage-1 design 7 (pooled, LR)")):
        g = c[(c.set == s) & (c.variant == v) & (c.test == t) & (c.rho == 0.4)]
        if len(g):
            keep.append(g.assign(label=lab).rename(columns={"power": "rate"})[["label", "odds_ratio", "rate"]])
    return pd.concat(keep) if keep else pd.DataFrame()


def fig_power(curves: pd.DataFrame, ref: pd.DataFrame, label: str, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    styles = ["#9aa0a6", "#5f6368", "#202124"]
    for (lab, g), col in zip(ref.groupby("label", sort=False), styles):
        g = g.sort_values("odds_ratio")
        ax.plot(g.odds_ratio, g.rate, color=col, lw=1.2, ls="--", marker="o", ms=3, label=lab)
    for truth, col in (("composite", "#1a73e8"), ("random", "#d93025")):
        g = curves[(curves.truth == truth) & (curves.rho == 0.4) & (curves.sensitivity == "base")].sort_values("odds_ratio")
        if len(g):
            ax.plot(g.odds_ratio, g.NH1lr, color=col, lw=2, marker="o", ms=4, label=f"{label}, {truth} truth")
            if "locked_primary_closed" in g:
                ax.plot(g.odds_ratio, g.locked_primary_closed, color=col, lw=1, ls=":", label=f"E4 claim (closed testing), {truth}")
    ax.axhline(0.8, color="#bdc1c6", lw=0.8)
    ax.axvline(1.35, color="#bdc1c6", lw=0.8)
    ax.set_xscale("log")
    ax.set_xticks([1.15, 1.25, 1.35, 1.5, 1.75, 2, 2.5, 3])
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.FormatStrFormatter("%g"))
    ax.set_xlabel("Odds ratio per SD of the latent moment state (ρ = .4)")
    ax.set_ylabel("Power (one-sided α = .05)")
    ax.set_ylim(0, 1.02)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=7, frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


# categorical slots 1-5 of the dataviz reference palette (validated: CVD and normal-vision floors pass; contrast relief
# by legend, marker shape and the tables in report_tables.md)
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
MARKERS = ["o", "s", "D", "^", "v"]


def _style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#9aa0a6")
    ax.tick_params(colors="#52514e", labelsize=8)
    ax.grid(axis="y", color="#e8eaed", lw=0.6)
    ax.set_axisbelow(True)


def fig_rf(per_null: pd.DataFrame, path: Path):
    """Maximum decisive false-detection rate by detrend degree, one line per null (rule R-F)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    for (null, g), col, mk in zip(per_null.groupby("scenario", sort=False), SERIES, MARKERS):
        g = g.sort_values("degree")
        ax.plot(g.degree, g.rate, color=col, lw=2, marker=mk, ms=6, label=null)
    ax.axhline(0.07, color="#5f6368", lw=1, ls="--")
    ax.text(3.05, 0.071, "bound .07", fontsize=7, color="#52514e", va="bottom")
    ax.axhline(0.05, color="#bdc1c6", lw=0.8)
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(["linear (Stage 1)", "quadratic", "cubic (d* = 3)"])
    ax.set_ylabel("Max false detection (T1lr, T2lr, NH1lr;\npooled + E4; P6 and P0)", fontsize=8)
    ax.set_xlabel("Within-recording detrend degree", fontsize=8)
    _style(ax)
    ax.legend(fontsize=7, frameon=False, title="Null", title_fontsize=7, loc="upper right")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def fig_rg(power: pd.DataFrame, path: Path):
    """NH1lr power by truth direction for the five parametrizations, OR 1.35 and 1.5 (rule R-G)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    truths = list(dict.fromkeys(power.truth))
    labels = {"composite": "equal-weight", "random": "random\n(shared)", "logdens": "logdens\nonly", "gaze": "gaze\nonly",
              "validity": "validity\nonly", "random/random_indep": "random\n(dev ≠ lock)"}
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.6), sharey=True)
    for ax, o in zip(axes, (1.35, 1.5)):
        for j, (param, col, mk) in enumerate(zip(CA.ORDER, SERIES, MARKERS)):
            g = power[(power.param == param) & (power.odds_ratio == o)].set_index("truth").reindex(truths)
            x = np.arange(len(truths)) + (j - 2) * 0.12
            ax.plot(x, g.rate, ls="none", marker=mk, ms=6, color=col, label=param, markeredgecolor="#fcfcfb", markeredgewidth=0.8)
        ax.axhline(0.8, color="#bdc1c6", lw=0.8)
        ax.set_xticks(np.arange(len(truths)))
        ax.set_xticklabels([labels.get(t, t) for t in truths], fontsize=7)
        ax.set_title(f"OR {o:g} (ρ = .4)", fontsize=9, color="#202124")
        ax.set_ylim(0, 1.02)
        _style(ax)
    axes[0].set_ylabel("NH1lr power, pooled lock", fontsize=8)
    axes[1].legend(fontsize=7, frameon=False, title="Parametrization", title_fontsize=7, loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    summary, parts = {}, ["# Closure-phase tables (generated by scripts/report.py; synthetic outcomes only)\n"]
    # ---------------- R-F
    if (EV / "sim_rf").exists():
        d = CA.load(EV / "sim_rf")
        r = CA.rule_rf(d)
        r["table"].to_csv(TAB / "rf_null_rates.csv", index=False)
        r["power"].to_csv(TAB / "rf_power.csv", index=False)
        wide = r["table"].pivot_table(index=["set", "scenario", "param", "test"], columns="degree", values="rate").reset_index()
        wide.columns = [f"d={c}" if isinstance(c, (int, np.integer)) else c for c in wide.columns]
        parts += ["## 1. R-F — temporal control\n", "Maximum decisive rate (pooled lock and E4; T1lr, T2lr, NH1lr; nulls N0, N1, N1q, N1c, N1e; both P6 and P0) per degree:\n",
                  md(r["per_degree"]), f"\n**Decision: d\\* = {r['chosen']}** (passing degrees: {r['passing']}; resolved: {r['resolved']}).\n",
                  "\nFalse-detection rates by degree:\n", md(wide), "\nPower cost at OR 1.5 (ρ = .4), NH1lr:\n",
                  md(r["power"].pivot_table(index=["set", "truth", "param"], columns="degree", values="rate").reset_index())]
        summary["rf"] = dict(chosen=r["chosen"], passing=r["passing"], per_degree=r["per_degree"].to_dict(orient="records"))
        dec = r["table"][r["table"].set.isin(["locked_pooled", "locked_primary"]) & r["table"].test.isin(["T1lr", "T2lr", "NH1lr"])]
        fig_rf(dec.groupby(["scenario", "degree"]).rate.max().reset_index(), FIG / "rf_max_rate_by_degree.png")
    # ---------------- R-G
    k = summary.get("rf", {}).get("chosen")
    if (EV / "sim_rg").exists() and k:
        d = CA.load(EV / "sim_rg")
        g = CA.rule_rg(d, k)
        g["admissibility"].to_csv(TAB / "rg_null_rates.csv", index=False)
        g["power"].to_csv(TAB / "rg_power.csv", index=False)
        g["summary"].to_csv(TAB / "rg_summary.csv", index=False)
        adm = g["admissibility"].pivot_table(index=["scenario", "test"], columns="param", values="rate").reset_index()
        pw = g["power"].pivot_table(index=["truth", "odds_ratio"], columns="param", values="rate").reset_index()
        cos = d[d.name == "ALT"].groupby(["truth", "dev_truth", "odds_ratio"])["dev_dir_cosine"].mean().reset_index() \
            if "dev_dir_cosine" in d else pd.DataFrame()
        parts += ["## 2. R-G — parametrization\n", "Summary (admissible: every T1lr, T2lr, NH1lr ≤ .07 in seven nulls; score: mean NH1lr power over 12 truth × OR cells; robust: min ≥ P6 min − .05):\n",
                  md(g["summary"]), f"\n**Decision: {g['chosen']}.**\n", "\nFalse-detection rates (pooled lock):\n", md(adm),
                  "\nNH1lr power by truth (pooled lock, ρ = .4):\n", md(pw), "\nMean cosine of the frozen development direction with the truth:\n", md(cos)]
        summary["rg"] = dict(chosen=g["chosen"], summary=g["summary"].to_dict(orient="records"))
        fig_rg(g["power"], FIG / "rg_power_by_truth.png")
    # ---------------- conf
    chosen = summary.get("rg", {}).get("chosen")
    if (EV / "sim_conf").exists() and chosen:
        d = CA.load(EV / "sim_conf")
        c = CA.conf_checks(d, chosen, k)
        for nm in ("pooled", "elementary", "false_go"):
            c[nm].to_csv(TAB / f"conf_{nm}.csv", index=False)
        curves = CA.power_table(d, chosen, k, sets=("locked_pooled", "development"))
        curves.to_csv(TAB / "conf_power.csv", index=False)
        if curves.empty:
            curves = pd.DataFrame(columns=["set", "rho", "truth", "odds_ratio", "sensitivity", "NH1lr", "NH1"])
        pooled = curves[curves.set == "locked_pooled"]
        mdes = []
        for (rho, truth), gg in pooled[pooled.sensitivity == "base"].groupby(["rho", "truth"]):
            mdes.append(dict(rho=rho, truth=truth, mde_pooled_nh1lr=CA.mde(gg, "NH1lr"), mde_pooled_cv_nh1=CA.mde(gg, "NH1"),
                             mde_e4_closed=CA.mde(gg, "locked_primary_closed"), mde_e5_closed=CA.mde(gg, "locked_secondary_closed")))
        mdes = pd.DataFrame(mdes)
        mdes.to_csv(TAB / "conf_mde.csv", index=False)
        v = CA.vname(chosen, k)
        lam = []
        for (o, truth), gg in d[(d.set == "locked_pooled") & (d.name == "ALT") & (d.rho == 0.4) & ~d.two_pl & ~d.guessing
                                & ~d.hetero & (d.e5_factor == 1.0)].groupby(["odds_ratio", "truth"]):
            row = dict(odds_ratio=o, truth=truth)
            for pre in ("locked_primary::", "locked_secondary::"):
                col = f"{pre}{v}|lam"
                if col in gg:
                    row[f"{pre[:-2]}_lambda_mean"] = float(gg[col].mean())
                    row[f"{pre[:-2]}_lambda_sd"] = float(gg[col].std())
            lam.append(row)
        lam = pd.DataFrame(lam)
        parts += ["## 3. R-H — confirmation of the selected design\n", f"Criteria: {json.dumps(c['criteria'])}; **passed: {c['passed']}**\n",
                  "\nPooled lock, false detection (LR and CV fallback):\n",
                  md(c["pooled"].pivot_table(index="scenario", columns="test", values="rate").reset_index()),
                  "\nE4 / E5 elementary tests on the same outcomes (closed testing):\n",
                  md(c["elementary"].pivot_table(index=["scenario"], columns=["set", "test"], values="rate").reset_index()),
                  "\nDevelopment stop rule, false go:\n", md(c["false_go"]), "\nMinimum detectable effects (OR at 80% power):\n", md(mdes),
                  "\nPower and usefulness (pooled lock and development):\n", md(curves), "\nPer-cohort λ̂ (1-df forms):\n", md(lam)]
        if len(pooled):
            fig_power(pooled, stage1_reference(), f"{chosen} (d = {k}), pooled LR", FIG / "power_closure_vs_stage1.png")
        summary["conf"] = dict(passed=c["passed"], criteria=c["criteria"], mde=mdes.to_dict(orient="records"))
    # ---------------- NH4
    if (EV / "sim_nh4").exists() and k:
        d = CA.load(EV / "sim_nh4")
        rows = []
        for v in (f"CAIRN-gaze|val-dt{k}", f"CAIRN-validity-dt{k}", f"CAIRN-gaze-dt{k}"):
            t = CA.null_rows(d, ("locked_pooled", "locked_primary", "development"), ("N4", "N0", "N3"), v, ("T1lr", "T2lr", "NH1lr"))
            rows.append(t)
            for s in ("locked_pooled", "locked_primary", "development"):
                gg = d[(d.set == s) & (d.name == "ALT")]
                r = CA.rate(gg, "", v, "NH1lr")
                if r["n"]:
                    rows.append(pd.DataFrame([dict(set=s, scenario="ALT gaze OR 1.5", variant=v, test="NH1lr", **r)]))
        nh = pd.concat(rows, ignore_index=True)
        nh.to_csv(TAB / "nh4.csv", index=False)
        cond = nh[(nh.variant == f"CAIRN-gaze|val-dt{k}") & nh.scenario.isin(["N4", "N0", "N3"])]
        ok = bool((cond.rate <= CA.BOUND).all())
        parts += ["## 4. R-I — NH4 attribution (gaze conditional on validity)\n",
                  md(nh.pivot_table(index=["set", "scenario"], columns=["variant", "test"], values="rate").reset_index()),
                  f"\n**Conditional test calibrated in N4 / N0 / N3: {ok}**\n"]
        summary["nh4"] = dict(calibrated=ok)
    (TAB / "report_tables.md").write_text("\n".join(parts))
    (EV / "summary.json").write_text(json.dumps(summary, indent=2, default=float))
    print(json.dumps(summary, indent=2, default=float)[:3000])


if __name__ == "__main__":
    sys.exit(main())
