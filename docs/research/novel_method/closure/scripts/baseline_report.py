"""Summarize the outcome-free baseline validation (rule R-K): negative control (N0), positive controls (N2 person-level
engagement; ALT3 anchored effect at OR 3, rho .7), compute and size, plus the determinism / fold-safety checks.

    python baseline_report.py      # writes evidence/baselines/summary.csv, summary.md and verdicts.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

EV = Path(__file__).resolve().parents[1] / "evidence" / "baselines"
WHOLE_VIDEO = ("B3-", "B4a-mantisv2-video", "B4b-attention-MIL", "IRT-whole")
ANCHORED = ("anchored", "B7-", "text-attention", "CAIRN", "item-lightgbm", "item-gpboost", "B9")


def _md(df: pd.DataFrame) -> str:
    df = df.reset_index()
    head = "| " + " | ".join(map(str, df.columns)) + " |\n|" + "---|" * len(df.columns) + "\n"
    return head + "\n".join("| " + " | ".join(f"{v:.4f}" if isinstance(v, float) else str(v) for v in r) + " |"
                             for r in df.itertuples(index=False))


def main():
    rows = []
    for p in sorted(EV.glob("*_*.jsonl")):
        rows += [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
    d = pd.DataFrame(rows)
    models = sorted({c.split("|")[0] for c in d.columns if c.endswith("|s_item")})
    out = []
    for (s, sc), g in d.groupby(["set", "scenario"]):
        for m in models:
            x = g[f"{m}|s_item"].astype(float).dropna()
            if x.empty:
                continue
            gm = g.loc[x.index]
            out.append(dict(set=s, scenario=sc, model=m, reps=len(x), s_item_mean=x.mean(),
                            s_item_mcse=x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else np.nan,
                            d_auc_wp_mean=gm[f"{m}|d_auc_wp"].astype(float).mean(), seconds_per_rep=gm[f"{m}|seconds"].mean(),
                            n_params=int(gm[f"{m}|n_params"].iloc[0])))
    t = pd.DataFrame(out)
    t.to_csv(EV / "summary.csv", index=False)
    verdict = {}
    for m in models:
        r = t[t.model == m].set_index(["set", "scenario"])
        neg = r.xs("N0", level="scenario") if "N0" in r.index.get_level_values(1) else None
        neg_ok = bool(neg is not None and (neg.s_item_mean <= 2 * neg.s_item_mcse).all())
        kind = "anchored/item-level" if any(a in m for a in ANCHORED) else "whole-video"
        pos_sc = "N2" if kind == "whole-video" else "ALT3"
        pos = r.xs(pos_sc, level="scenario") if pos_sc in r.index.get_level_values(1) else None
        pos_ok = bool(pos is not None and (pos.s_item_mean > 2 * pos.s_item_mcse).any())
        verdict[m] = dict(kind=kind, negative_control=neg_ok, positive_control_scenario=pos_sc, positive_control=pos_ok)
    checks = {}
    for f in sorted(EV.glob("checks*.json")):
        checks.update(json.loads(f.read_text())["results"])
    for m, c in checks.items():
        verdict.setdefault(m, {}).update(deterministic=c["deterministic"], fold_safe=c["fold_safe"])
    (EV / "verdicts.json").write_text(json.dumps(verdict, indent=2))
    piv = t.pivot_table(index="model", columns=["set", "scenario"], values="s_item_mean")
    piv.columns = [f"{a}/{b}" for a, b in piv.columns]
    lines = ["# Baseline validation summary (synthetic outcomes; rule R-K)\n", "Mean held-out S_item over IRT-M2:\n",
             _md(piv), "\n\nVerdicts:\n", _md(pd.DataFrame(verdict).T)]
    (EV / "summary.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
