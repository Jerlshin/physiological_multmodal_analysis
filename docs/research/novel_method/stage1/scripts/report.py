"""Stage-1 simulation report: tables, figures and a summary JSON from the stored replicates.

Reads only simulation output (synthetic outcomes). Usage:
    PYTHONPATH=src .venv-cairn/bin/python docs/research/novel_method/stage1/scripts/report.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from cairn import analysis as A
from cairn import design
from cairn import inference as I
from cairn import simulate as SIM
from cairn.paths_stage1 import STAGE1_EVIDENCE

OUT = STAGE1_EVIDENCE
TAB = OUT / "tables"
FIG = OUT / "figures"
SETS = ("locked_primary", "locked_pooled", "development")
SET_LABEL = {"locked_primary": "E4 (locked primary)", "locked_pooled": "E4 + E5 pooled", "development": "Development",
             "locked_secondary": "E5 (locked secondary)"}
NULLS = ("N0", "N1", "N2", "N3")
# reference palette (dataviz skill, light mode; validated: CVD worst adjacent dE 9.1, normal 22.9; contrast relief = labels + tables)
C = dict(s1="#2a78d6", s2="#eb6834", s3="#1baf7a", s4="#eda100", ink="#0b0b0b", ink2="#52514e", muted="#898781",
         grid="#e1e0d9", surface="#fcfcfb")


def fmt(x, d=3):
    return "—" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{d}f}"


def primary_name(d: pd.DataFrame) -> str:
    form = d.primary_form.dropna().iloc[0] if "primary_form" in d else "dt"
    return SIM.FORMS[form][0].name


# ----------------------------------------------------------------------------- figures
def _ax_style(ax):
    ax.set_facecolor(C["surface"])
    ax.grid(True, color=C["grid"], linewidth=0.8, linestyle="-")
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(C["muted"])
    ax.tick_params(colors=C["ink2"], labelsize=9)


def _log_or_axis(ax, matplotlib):
    ax.set_xscale("log")
    ax.set_xlim(0.97, 3.15)
    ax.set_xticks([1.0, 1.25, 1.5, 2.0, 2.5, 3.0])
    ax.xaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%g"))
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())


def fig_power(curves: pd.DataFrame, prim: str, analytic: dict, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sets = [s for s in SETS if s in set(curves.set)]
    fig, axes = plt.subplots(1, len(sets), figsize=(4.6 * len(sets), 4.2), sharey=True, facecolor=C["surface"])
    axes = np.atleast_1d(axes)
    series = [(prim, "NH1", "CV statistic (plan)", C["s1"], "o"), (prim, "NH1lr", "LR statistic", C["s2"], "s"),
              (f"{prim}-dir", "NH1", "CV, frozen dev direction", C["s3"], "^"),
              (f"{prim}-dir", "NH1lr", "LR, frozen dev direction", C["s4"], "D")]
    for ax, s in zip(axes, sets):
        _ax_style(ax)
        for v, t, lab, col, mk in series:
            g = curves[(curves.set == s) & (curves.variant == v) & (curves.test == t) & (curves.rho == 0.4)].sort_values("odds_ratio")
            if g.empty:
                continue
            ax.plot(g.odds_ratio, g.power, color=col, lw=2, marker=mk, ms=6, mec=C["surface"], mew=1.5, label=lab)
        if s in analytic:
            o = np.array(sorted(set(curves.odds_ratio)))
            ax.plot(o, analytic[s](o), color=C["muted"], lw=1.5, label="plan §20.3 analytic (independent responses)")
        ax.axhline(0.8, color=C["ink2"], lw=0.8)
        ax.axvline(1.35, color=C["muted"], lw=0.8)
        ax.text(1.36, 0.02, "OR 1.35", color=C["ink2"], fontsize=8)
        _log_or_axis(ax, matplotlib)
        ax.set_ylim(0, 1.02)
        ax.set_title(SET_LABEL[s], color=C["ink"], fontsize=11, loc="left")
        ax.set_xlabel("odds ratio per SD of latent moment state (ρ = .4)", color=C["ink2"], fontsize=9)
    axes[0].set_ylabel("P(NH1 supported: T1 and T2 at α = .05)", color=C["ink2"], fontsize=9)
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=3, frameon=False, fontsize=9, labelcolor=C["ink"])
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    fig.savefig(path, dpi=150, facecolor=C["surface"])
    plt.close(fig)


def fig_type1(cal: pd.DataFrame, prim: str, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    tests = [(prim, "T1"), (prim, "T2"), (prim, "T2c"), (prim, "NH1"), (prim, "T1lr"), (prim, "T2lr"), (prim, "NH1lr"),
             (f"{prim}-dir", "NH1"), (f"{prim}-dir", "NH1lr"), ("stop-rule", "go")]
    sets = [s for s in SETS if s in set(cal.set)]
    fig, axes = plt.subplots(1, len(sets), figsize=(4.4 * len(sets), 4.8), sharey=True, facecolor=C["surface"])
    axes = np.atleast_1d(axes)
    cols = dict(zip(NULLS, (C["s1"], C["s2"], C["s3"], C["s4"])))
    marks = dict(zip(NULLS, ("o", "s", "^", "D")))
    for ax, s in zip(axes, sets):
        _ax_style(ax)
        for k, n in enumerate(NULLS):
            for i, (v, t) in enumerate(tests):
                g = cal[(cal.set == s) & (cal.name == n) & (cal.variant == v) & (cal.test == t) & (cal.realism == "base")]
                if g.empty:
                    continue
                r = g.iloc[0]
                yy = i + (k - 1.5) * 0.17
                ax.plot([r.ci_lo, r.ci_hi], [yy, yy], color=cols[n], lw=1.2)
                ax.plot(r.rate, yy, marker=marks[n], color=cols[n], ms=6, mec=C["surface"], mew=1.2,
                        label=n if i == 0 else None, ls="none")
        ax.axvline(0.05, color=C["ink2"], lw=0.8)
        ax.axvline(0.07, color=C["s2"], lw=0.8)
        ax.text(0.071, -0.9, ".07 bound", color=C["ink2"], fontsize=8)
        ax.set_yticks(range(len(tests)))
        ax.set_yticklabels([f"{'dir ' if v.endswith('-dir') else ''}{t}" for v, t in tests], fontsize=9, color=C["ink2"])
        ax.set_xlim(0, 0.16)
        ax.invert_yaxis()
        ax.set_title(SET_LABEL[s], color=C["ink"], fontsize=11, loc="left")
        ax.set_xlabel("false-detection rate (95% Wilson interval)", color=C["ink2"], fontsize=9)
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=4, frameon=False, fontsize=9, labelcolor=C["ink"], title_fontsize=9)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(path, dpi=150, facecolor=C["surface"])
    plt.close(fig)


def fig_metrics(pop: pd.DataFrame, means: pd.DataFrame, prim: str, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.0), facecolor=C["surface"])
    for ax, col, thr, lab in ((axes[0], "s_item", 0.01, "S_item"), (axes[1], "d_auc_wp", 0.02, "ΔAUC_wp")):
        _ax_style(ax)
        for s, c, mk in (("locked_primary", C["s1"], "o"), ("development", C["s2"], "s")):
            g = pop[(pop.set == s) & (pop.rho == 0.4)].sort_values("odds_ratio")
            ax.plot(g.odds_ratio, g[f"{col}_pop"], color=c, lw=2, marker=mk, ms=6, mec=C["surface"], mew=1.5,
                    label=f"{SET_LABEL[s]}: infinite-data")
            h = means[(means.set == s) & (means.variant == prim) & (means.rho == 0.4)].sort_values("odds_ratio")
            if not h.empty:
                ax.plot(h.odds_ratio, h[col], color=c, lw=1.2, marker=mk, ms=5, mfc=C["surface"], mew=1.2,
                        label=f"{SET_LABEL[s]}: mean CV estimate")
        ax.axhline(thr, color=C["ink2"], lw=0.8)
        ax.text(1.02, thr * 1.04, f"useful threshold {thr}", color=C["ink2"], fontsize=8)
        _log_or_axis(ax, matplotlib)
        ax.set_title(f"{lab} over IRT-M2 (ρ = .4)", color=C["ink"], fontsize=11, loc="left")
        ax.set_xlabel("odds ratio per SD of latent moment state", color=C["ink2"], fontsize=9)
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=2, frameon=False, fontsize=9, labelcolor=C["ink"])
    fig.tight_layout(rect=(0, 0.14, 1, 1))
    fig.savefig(path, dpi=150, facecolor=C["surface"])
    plt.close(fig)


def fig_collapse(curves: pd.DataFrame, prim: str, path: Path):
    """Power against the observed-scale effect log(OR) sqrt(rho): does rho act only through attenuation?"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sets = [s for s in SETS if s in set(curves.set)]
    fig, axes = plt.subplots(1, len(sets), figsize=(4.4 * len(sets), 3.8), sharey=True, facecolor=C["surface"])
    axes = np.atleast_1d(axes)
    for ax, s in zip(axes, sets):
        _ax_style(ax)
        for rho, c, mk in ((0.2, C["s1"], "o"), (0.4, C["s2"], "s"), (0.7, C["s3"], "^")):
            g = curves[(curves.set == s) & (curves.variant == prim) & (curves.test == "NH1lr") & (curves.rho == rho)
                       & (curves.odds_ratio > 1)].sort_values("odds_ratio")
            if g.empty:
                continue
            ax.plot(np.log(g.odds_ratio) * np.sqrt(rho), g.power, color=c, lw=2, marker=mk, ms=6, mec=C["surface"],
                    mew=1.5, label=f"ρ = {rho}")
        ax.axhline(0.8, color=C["ink2"], lw=0.8)
        ax.set_title(SET_LABEL[s], color=C["ink"], fontsize=11, loc="left")
        ax.set_xlabel("observed-scale effect log(OR)·√ρ", color=C["ink2"], fontsize=9)
    axes[0].set_ylabel("P(NH1, LR statistic)", color=C["ink2"], fontsize=9)
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=3, frameon=False, fontsize=9, labelcolor=C["ink"])
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    fig.savefig(path, dpi=150, facecolor=C["surface"])
    plt.close(fig)


def rule_ra(n1: pd.DataFrame) -> dict:
    """Pre-declared rule R-A (S1-D06) on the N1 decision experiment."""
    def ok(v, names):
        g = n1[(n1.variant == v) & n1.name.isin(names) & n1.test.isin(["T1", "T2", "NH1"])
               & n1.set.isin(["locked_primary", "development"])]
        return bool(len(g) == 3 * 2 * len(names) and (g.rate <= 0.07).all()), float(g.rate.max())
    raw_ok, raw_max = ok("CAIRN-linear", ["N1"])
    dt_ok, dt_max = ok("CAIRN-linear-dt", ["N1", "N0"])
    form = "raw" if raw_ok else ("dt" if dt_ok else "unresolved")
    return dict(raw_passes_N1=raw_ok, raw_max_rate=raw_max, dt_passes_N1_N0=dt_ok, dt_max_rate=dt_max, primary_form=form)



# ----------------------------------------------------------------------------- markdown tables
def md_table(df: pd.DataFrame, digits: int = 3) -> str:
    def cell(x):
        if isinstance(x, (float, np.floating)):
            if not np.isfinite(x):
                return "—" if np.isnan(x) else "> grid"
            return f"{x:.{digits}f}"
        return str(x)
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(cell(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(out)


def write_markdown(path: Path, prim: str, cal: pd.DataFrame, nul: pd.DataFrame, curves: pd.DataFrame, mde: pd.DataFrame,
                   des: pd.DataFrame, useful: pd.DataFrame, pop: pd.DataFrame, means: pd.DataFrame, jt: pd.DataFrame,
                   n1: pd.DataFrame | None, summary: dict):
    L = ["# Stage-1 simulation tables (generated)", "",
         "Written by `stage1/scripts/report.py` from the stored replicates (synthetic outcomes only). Do not edit by hand.", ""]
    lab = {prim: "CAIRN-linear-dt", f"{prim}-dir": "dir"}
    # 1 calibration
    L += ["## 1. False-detection rate at α = .05 (base nulls; N0–N3 500 replicates, N1q 500 E4/pooled after R-E, 200 development, E5 200)", ""]
    tests = ["T1", "T2", "T2c", "NH1", "T1lr", "T2lr", "T2clr", "NH1lr"]
    base_nulls = cal[(cal.odds_ratio == 1.0) & (cal.realism == "base") & cal.name.isin(list(NULLS) + ["N1q"])]
    for s in ("locked_primary", "development", "locked_pooled", "locked_secondary"):
        g = base_nulls[base_nulls.set == s]
        if g.empty:
            continue
        rows = []
        for v in (prim, f"{prim}-dir", "CAIRN-validity-dt", "stop-rule", "full-data glmm Wald", "full-data naive Wald",
                  "full-data robust Wald", "full-data literal Wald"):
            for t in tests + ["go", "one-sided z"]:
                h = g[(g.variant == v) & (g.test == t)]
                if h.empty:
                    continue
                r = {"model": lab.get(v, v), "test": t}
                for n in list(NULLS) + ["N1q"]:
                    k = h[h.name == n]
                    r[n] = float(k.rate.iloc[0]) if len(k) else np.nan
                mx = h[h.name.isin(NULLS)].rate
                r["max N0–N3"] = float(mx.max()) if len(mx) else np.nan
                rows.append(r)
        L += [f"### {SET_LABEL[s]}", "", md_table(pd.DataFrame(rows)), ""]
    # 2 power
    L += ["## 2. Power (rejection rate) on the alternative grid, ρ = .4", ""]
    rows = []
    for s in SETS:
        for v, t, name in ((prim, "NH1", "NH1, CV (plan)"), (prim, "NH1lr", "NH1, LR"), (f"{prim}-dir", "NH1", "NH1, CV, frozen direction"),
                           (f"{prim}-dir", "NH1lr", "NH1, LR, frozen direction"), (prim, "T1", "T1 alone, CV"), (prim, "T2", "T2 alone, CV"),
                           ("full-data glmm Wald", "z", "oracle GLMM Wald (true composite)"), ("full-data naive Wald", "z", "oracle naive Wald (independent responses)")):
            g = curves[(curves.set == s) & (curves.variant == v) & (curves.test == t) & (curves.rho == 0.4)]
            if g.empty:
                continue
            r = {"set": SET_LABEL[s], "statistic": name}
            r.update({f"OR {o:g}": float(p) for o, p in zip(g.odds_ratio, g.power)})
            rows.append(r)
    L += [md_table(pd.DataFrame(rows), 2), ""]
    for rho in (0.2, 0.7):
        rows = []
        for s in SETS:
            for v, t, name in ((prim, "NH1", "NH1, CV"), (prim, "NH1lr", "NH1, LR"), (f"{prim}-dir", "NH1lr", "NH1, LR, frozen direction")):
                g = curves[(curves.set == s) & (curves.variant == v) & (curves.test == t) & (curves.rho == rho)]
                if g.empty:
                    continue
                r = {"set": SET_LABEL[s], "statistic": name}
                r.update({f"OR {o:g}": float(p) for o, p in zip(g.odds_ratio, g.power)})
                rows.append(r)
        L += [f"ρ = {rho} (OR 1 = pure null N0):", "", md_table(pd.DataFrame(rows), 2), ""]
    # 3 MDE
    L += ["## 3. Minimum detectable effect: OR per SD of the latent state at 80% power", ""]
    m = mde[mde.test.isin(["NH1", "NH1lr", "z"]) & ~mde.variant.str.contains("validity|gaze|robust")].copy()
    m["statistic"] = m.variant.map(lambda v: lab.get(v, v)) + " " + m.test
    piv = m.pivot_table(index=["set", "statistic"], columns="rho", values="mde_or").reset_index()
    piv.columns = ["set", "statistic"] + [f"ρ = {c}" for c in piv.columns[2:]]
    piv["set"] = piv.set.map(SET_LABEL)
    L += [md_table(piv), ""]
    g = mde[mde.test.isin(["NH1", "NH1lr", "z"]) & ~mde.variant.str.contains("validity|gaze|robust") & (mde.rho == 0.4)].copy()
    g["statistic"] = g.variant.map(lambda v: lab.get(v, v)) + " " + g.test
    g["set"] = g.set.map(SET_LABEL)
    L += ["At ρ = .4, in usefulness units (population metrics of the oracle predictor at the MDE; λ_obs = log OR · √ρ):", "",
          md_table(g[["set", "statistic", "mde_or", "lambda_obs", "s_item_pop_at_mde", "d_auc_wp_pop_at_mde"]], 4), ""]
    # 4 designs
    L += ["## 4. Candidate confirmatory designs (rule R-B2)", "", md_table(des.drop(columns=["nulls_checked"])), "",
          f"Recommended by the pre-declared choice rule: design {summary['recommended_design']['design'] if summary['recommended_design'] else '—'}.", ""]
    # 5 usefulness
    L += ["## 5. Usefulness mapping: smallest OR whose mean metric meets S_item ≥ .01 and ΔAUC_wp ≥ .02", "",
          md_table(useful[useful.set.isin(SETS)].assign(set=lambda x: x.set.map(SET_LABEL))), "",
          "Population (infinite-data) S_item and ΔAUC_wp of the oracle predictor, ρ = .4:", ""]
    pp = pop[pop.rho == 0.4].pivot_table(index="set", columns="odds_ratio", values=["s_item_pop", "d_auc_wp_pop"])
    rows = []
    for s in pp.index:
        for metric in ("s_item_pop", "d_auc_wp_pop"):
            r = {"set": SET_LABEL[s], "metric": metric}
            r.update({f"OR {o:g}": float(pp.loc[s, (metric, o)]) for o in sorted({c[1] for c in pp.columns})})
            rows.append(r)
    L += [md_table(pd.DataFrame(rows), 4), "", "Mean cross-validated estimate (planned procedure), ρ = .4:", ""]
    rows = []
    mm = means[(means.rho == 0.4) & means.variant.str.startswith("CAIRN-linear") & means.set.isin(SETS)]
    for (s, v), g in mm.groupby(["set", "variant"]):
        for metric in ("s_item", "d_auc_wp"):
            r = {"set": SET_LABEL[s], "model": lab.get(v, v), "metric": metric}
            r.update({f"OR {o:g}": float(x) for o, x in zip(g.odds_ratio, g[metric])})
            rows.append(r)
    L += [md_table(pd.DataFrame(rows), 4), ""]
    # 6 clustering
    L += ["## 6. Clustering versus the plan §20.3 analytic estimate (ρ = .4)", ""]
    rows = []
    for s, c in summary["clustering"].items():
        rows.append({"set": SET_LABEL[s], "anchorable responses": c["anchorable_responses"], "learners": c["learners"],
                     "moments": c["distinct_moments"], "analytic SE (independent)": c["analytic_se_independent"],
                     "oracle GLMM SE (model)": c["glmm_model_se"], "oracle GLMM SD (empirical)": c["glmm_emp_sd"],
                     "variance ratio": c["glmm_variance_ratio"], "analytic MDE": c["analytic_mde80_or_rho04"],
                     "oracle GLMM MDE": c.get("mde80_or_full-data glmm Wald|z"), "NH1 CV MDE": c.get(f"mde80_or_{prim}|NH1"),
                     "NH1 LR MDE": c.get(f"mde80_or_{prim}|NH1lr")})
    L += [md_table(pd.DataFrame(rows)), ""]
    # 7 joint
    L += ["## 7. Joint behaviour of T1 and T2", ""]
    j = jt[jt.scenario.str.match(r"^(N0|N1|N2|N3|N1q)_or1_rho0.4_q0.5$") | jt.scenario.isin(
        ["ALT_or1.35_rho0.4_q0.5", "ALT_or1.5_rho0.4_q0.5", "ALT_or2_rho0.4_q0.5"])].copy()
    j["set"] = j.set.map(SET_LABEL)
    L += [md_table(j[["set", "scenario", "statistic", "n", "T1", "T2", "both", "T1_only", "T2_only", "p_spearman", "P_T2_given_T1"]]), ""]
    # 8 N1 decision
    if n1 is not None:
        L += ["## 8. N1 decision experiment (rule R-A)", ""]
        g = n1[n1.test.isin(["T1", "T2", "T2c", "NH1"])].copy()
        g["form"] = g.variant.map({"CAIRN-linear": "raw (plan-literal)", "CAIRN-linear-dt": "detrended"})
        piv = g.pivot_table(index=["set", "name", "form"], columns="test", values="rate").reset_index()
        piv["set"] = piv.set.map(SET_LABEL)
        L += [md_table(piv), ""]
    path.write_text("\n".join(L) + "\n")

# ----------------------------------------------------------------------------- main
def load_all(dirs) -> pd.DataFrame:
    """Main grid plus extension runs (rule R-E); a replicate may be stored once only."""
    d = pd.concat([A.load(x) for x in dirs if Path(x).exists()], ignore_index=True)
    if d.duplicated(["set", "scenario", "rep"]).any():
        raise SystemExit("a replicate is stored twice")
    return d


def rule_re(nul_all: pd.DataFrame, prim: str) -> dict:
    """Pre-declared rule R-E: N1q on the pooled lock, designs 7 (LR) and 5 (CV), 500 replicates."""
    g = nul_all[(nul_all.set == "locked_pooled") & (nul_all.name == "N1q") & (nul_all.variant == prim)]
    tests = ("T1", "T2", "NH1", "T1lr", "T2lr", "NH1lr")
    rates = {t: float(g[g.test == t].rate.iloc[0]) for t in tests if (g.test == t).any()}
    n = int(g.n.max()) if len(g) else 0
    ok = len(rates) == len(tests) and n >= 500 and max(rates.values()) <= 0.07
    return dict(replicates=n, rates=rates, design7_stands=ok if n >= 500 else None)


def main(sim_dirs=(OUT / "sim", OUT / "sim_addendum")):
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    d = load_all(sim_dirs)
    prim = primary_name(d)
    summary = dict(primary=prim, replicates=int(len(d)), by_set=d.groupby("set").size().to_dict())

    # 0 N1 decision experiment (rule R-A, S1-D06): raw vs within-recording-detrended form, same outcomes
    n1_dir = OUT / "sim_n1decision"
    if n1_dir.exists():
        n1 = A.rejection_table(A.load(n1_dir))
        n1.to_csv(TAB / "n1_decision.csv", index=False, float_format="%.4f")
        summary["n1_decision"] = dict(rule_ra=rule_ra(n1), replicates=int(len(A.load(n1_dir))))
        if summary["n1_decision"]["rule_ra"]["primary_form"] != (d.primary_form.dropna().iloc[0] if "primary_form" in d else None):
            raise SystemExit("main-grid primary form disagrees with rule R-A")

    # 1 calibration
    cal = A.rejection_table(d)
    cal.to_csv(TAB / "calibration_all.csv", index=False, float_format="%.4f")
    nul = cal[cal.name.isin(NULLS) & (cal.realism == "base") & (cal.odds_ratio == 1.0)]   # "N2 with an effect" is not a null
    nul.to_csv(TAB / "calibration_nulls.csv", index=False, float_format="%.4f")
    summary["max_false_detection"] = {
        f"{s}|{v}|{t}": float(g.rate.max()) for (s, v, t), g in nul.groupby(["set", "variant", "test"])}
    unif = {s: A.uniformity(d, s, "N0_or1_rho0.4_q0.5") for s in SETS + ("locked_secondary",) if s in set(d.set)}
    summary["uniformity_N0"] = unif
    summary["rule_re_n1q_pooled"] = rule_re(cal[cal.odds_ratio == 1.0], prim)
    e4q = cal[(cal.set == "locked_primary") & (cal.name == "N1q") & (cal.variant == prim)]
    d200 = A.rejection_table(d[(d.set == "locked_primary") & (d.name == "N1q") & (d.rep < 200)])
    summary["n1q_e4"] = dict(replicates=int(e4q.n.max()) if len(e4q) else 0,
                             rates_all={t: float(r) for t, r in zip(e4q.test, e4q.rate)},
                             rates_declared_200={t: float(r) for t, r in zip(d200[d200.variant == prim].test, d200[d200.variant == prim].rate)})

    # 2 power and MDE
    curves = A.power_curves(d)
    curves.to_csv(TAB / "power_curves.csv", index=False, float_format="%.4f")
    mde = A.mde_table(curves)
    mde.to_csv(TAB / "mde.csv", index=False, float_format="%.4f")

    # 3 metric mapping
    means = A.metric_means(d)
    means.to_csv(TAB / "metric_means_cv.csv", index=False, float_format="%.5f")
    pops = []
    for s in ("locked_primary", "development", "locked_pooled"):
        S = I.build_structure(design.build(s), with_splits=False)
        T = SIM.build_truth(S)
        for rho, ors in ((0.2, (1.5, 2.0, 2.5, 3.0, 4.0, 5.0)), (0.4, (1.15, 1.25, 1.35, 1.5, 1.75, 2.0, 2.5, 3.0)),
                         (0.7, (1.15, 1.25, 1.35, 1.5, 1.75, 2.0, 2.5))):
            for o in ors:
                pops.append(dict(set=s, **A.population_metrics(S, T, o, rho, n_draw=32)))
    pop = pd.DataFrame(pops)
    pop.to_csv(TAB / "metric_population.csv", index=False, float_format="%.5f")
    u_pop = A.useful_or(pop.assign(variant="infinite-data"), cols=("s_item_pop", "d_auc_wp_pop"))
    u_cv = A.useful_or(means[means.variant.str.startswith("CAIRN-linear") & means.set.isin(SETS)])
    useful = pd.concat([u_pop, u_cv], ignore_index=True)

    # MDEs in usefulness units: population S_item / dAUC_wp at the MDE (log-OR interpolation) and observed-scale lambda
    def at_or(s, rho, o, col):
        g = pop[(pop.set == s) & (pop.rho == rho)].sort_values("odds_ratio")
        if g.empty or not np.isfinite(o) or o < g.odds_ratio.min() or o > g.odds_ratio.max():
            return np.nan
        return float(np.interp(np.log(o), np.log(g.odds_ratio), g[col]))
    mde["lambda_obs"] = np.log(mde.mde_or) * np.sqrt(mde.rho)
    mde["s_item_pop_at_mde"] = [at_or(s, r, o, "s_item_pop") for s, r, o in zip(mde.set, mde.rho, mde.mde_or)]
    mde["d_auc_wp_pop_at_mde"] = [at_or(s, r, o, "d_auc_wp_pop") for s, r, o in zip(mde.set, mde.rho, mde.mde_or)]
    mde.to_csv(TAB / "mde.csv", index=False, float_format="%.4f")
    useful.to_csv(TAB / "useful_or.csv", index=False, float_format="%.4f")

    # 4 adequacy of candidate designs (R-B / R-B2)
    designs = []
    order = [("locked_primary", "NH1", prim), ("locked_primary", "NH1", f"{prim}-dir"),
             ("locked_primary", "NH1lr", prim), ("locked_primary", "NH1lr", f"{prim}-dir"),
             ("locked_pooled", "NH1", prim), ("locked_pooled", "NH1", f"{prim}-dir"),
             ("locked_pooled", "NH1lr", prim), ("locked_pooled", "NH1lr", f"{prim}-dir")]
    tests_of = {"NH1": ("T1", "T2", "NH1"), "NH1lr": ("T1lr", "T2lr", "NH1lr")}
    for k, (s, t, v) in enumerate(order, 1):
        cs = nul[(nul.set == s) & (nul.variant == v) & nul.test.isin(tests_of[t])]
        max_fd = float(cs.rate.max()) if len(cs) else np.nan
        n_nulls = int(cs.name.nunique())
        u = u_cv[(u_cv.set == s) & (u_cv.variant == v) & (u_cv.rho == 0.4)]   # usefulness as the design itself would estimate it
        or_useful = float(u.or_useful.iloc[0]) if len(u) else np.nan
        upop = u_pop[(u_pop.set == s) & (u_pop.rho == 0.4)]
        or_useful_pop = float(upop.or_useful.iloc[0]) if len(upop) else np.nan
        m = mde[(mde.set == s) & (mde.variant == v) & (mde.test == t) & (mde.rho == 0.4)]
        designs.append(dict(design=k, set=s, statistic="CV log-loss" if t == "NH1" else "likelihood ratio",
                            moment="refitted" if not v.endswith("-dir") else "frozen development direction",
                            nulls_checked=n_nulls, max_false_detection=max_fd, admissible=bool(n_nulls == 4 and max_fd <= 0.07),
                            power_or_1_35=A.power_at(curves, s, v, t, 0.4, 1.35),
                            power_or_1_50=A.power_at(curves, s, v, t, 0.4, 1.5),
                            mde80_or=float(m.mde_or.iloc[0]) if len(m) else np.nan,
                            or_useful_cv=or_useful, power_at_useful_cv=A.power_at(curves, s, v, t, 0.4, or_useful),
                            or_useful_pop=or_useful_pop, power_at_useful_pop=A.power_at(curves, s, v, t, 0.4, or_useful_pop)))
    des = pd.DataFrame(designs)
    des.to_csv(TAB / "candidate_designs.csv", index=False, float_format="%.4f")
    summary["candidate_designs"] = des.to_dict(orient="records")
    adm = des[des.admissible]
    hit = adm[adm.power_or_1_35 >= 0.8]
    if len(hit):
        rec = hit.iloc[0]
    elif len(adm):
        rec = adm.sort_values("mde80_or").iloc[0]
    else:
        rec = None
    summary["recommended_design"] = None if rec is None else rec.to_dict()

    # 5 clustering vs plan §20.3 analytic estimate
    clus = {}
    analytic_fn = {}
    for s in SETS:
        S_inc = design.build(s).summary()
        de = A.design_effect(d, s)
        if not de:
            continue
        p = de["mean_accuracy"]
        n_anch = S_inc["anchorable_responses"]
        f = (lambda o, n=n_anch, p=p: A.analytic_power(n, p, o, 0.4))
        analytic_fn[s] = f
        grid_o = np.exp(np.linspace(0, np.log(4), 400))
        clus[s] = dict(anchorable_responses=n_anch, item_responses=S_inc["item_responses"], learners=S_inc["learners"],
                       distinct_moments=S_inc["distinct_moments"],
                       analytic_se_independent=float(1 / np.sqrt(n_anch * p * (1 - p))),
                       analytic_mde80_or_rho04=float(grid_o[np.argmax(f(grid_o) >= 0.8)]), **de)
        for v, t in ((prim, "NH1"), (prim, "NH1lr"), ("full-data glmm Wald", "z"), ("full-data naive Wald", "z")):
            m = mde[(mde.set == s) & (mde.variant == v) & (mde.test == t) & (mde.rho == 0.4)]
            clus[s][f"mde80_or_{v}|{t}"] = float(m.mde_or.iloc[0]) if len(m) else None
    summary["clustering"] = clus

    # 6 joint T1 / T2
    jt = pd.concat([A.joint_table(d, prim).assign(statistic="CV"),
                    A.joint_table(d.rename(columns={f"{prim}|p_T1lr": "LRX|p_T1", f"{prim}|p_T2lr": "LRX|p_T2"}), "LRX").assign(statistic="LR")])
    jt.to_csv(TAB / "joint_T1_T2.csv", index=False, float_format="%.4f")

    # 7 N2 bias, NH4, stop rule, sensitivity
    bias = d[d.name == "N2"].groupby(["set", "scenario"])[["oracle|glmm_lambda", "oracle|literal_lambda", "oracle|naive_lambda"]].mean()
    ref = d[(d.name.isin(["N0", "ALT"])) & (d.realism == "base")].groupby(["set", "scenario"])[["oracle|glmm_lambda", "oracle|literal_lambda"]].mean()
    bias.to_csv(TAB / "n2_lambda_bias.csv", float_format="%.4f")
    ref.to_csv(TAB / "lambda_reference_N0_ALT.csv", float_format="%.4f")
    sens = cal[(cal.set == "locked_primary") & ((cal.realism == "sensitivity") | (cal.name.isin(["N0"]) & (cal.realism == "base"))
                                                 | ((cal.name == "ALT") & (cal.odds_ratio == 1.5) & (cal.rho == 0.4)))]
    sens.to_csv(TAB / "sensitivity_E4.csv", index=False, float_format="%.4f")
    nh4 = cal[cal.name.isin(["N0", "N3", "N4"]) & cal.variant.str.contains("validity|gaze")]
    nh4.to_csv(TAB / "nh4.csv", index=False, float_format="%.4f")

    # 8 delta_item per spec §1.7(3): OR (rho .4) where development NH1 power reaches .80
    di = {}
    for t in ("NH1", "NH1lr"):
        m = mde[(mde.set == "development") & (mde.variant == prim) & (mde.test == t) & (mde.rho == 0.4)]
        o = float(m.mde_or.iloc[0]) if len(m) else np.nan
        pm = pop[(pop.set == "development") & (pop.rho == 0.4)].sort_values("odds_ratio")
        di[t] = dict(or_dev80=o, s_item_pop=float(np.interp(np.log(o), np.log(pm.odds_ratio), pm.s_item_pop)) if np.isfinite(o) else None,
                     d_auc_wp_pop=float(np.interp(np.log(o), np.log(pm.odds_ratio), pm.d_auc_wp_pop)) if np.isfinite(o) else None)
    g = cal[(cal.set == "development") & (cal.variant == "stop-rule") & (cal.name == "ALT") & (cal.rho == 0.4)].sort_values("odds_ratio")
    di["stop_rule_go_or80"] = A.interpolate_or(np.r_[1.0, g.odds_ratio], np.r_[0.0, g.rate], 0.8) if len(g) else None
    summary["delta_item_spec"] = di

    # figures
    fig_power(curves, prim, analytic_fn, FIG / "power_nh1_rho04.png")
    fig_type1(nul, prim, FIG / "false_detection_nulls.png")
    fig_metrics(pop, means, prim, FIG / "metric_mapping_rho04.png")
    fig_collapse(curves, prim, FIG / "power_vs_observed_effect.png")
    write_markdown(TAB / "report_tables.md", prim, cal, nul, curves, mde, des, useful, pop, means, jt,
                   n1 if n1_dir.exists() else None, summary)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=lambda o: None if o is None else float(o)))
    print(json.dumps(dict(primary=prim, replicates=len(d), recommended=summary["recommended_design"]), indent=2, default=str))


if __name__ == "__main__":
    main([Path(x) for x in sys.argv[1:]] or (OUT / "sim", OUT / "sim_addendum"))
