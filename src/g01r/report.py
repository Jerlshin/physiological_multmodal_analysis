"""Collate tracked registry runs into the prespecified results tables (protocol §12, §15).

Reads the latest FINISHED run of every registry analysis in one tracking experiment
(``results/runs/<experiment>/``) and writes a markdown report plus machine-readable CSVs.
Every number carries its unit of independence (people, cells, videos).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .config import RESULTS


def collect(experiment: str, root: Path | None = None) -> dict:
    base = (root or RESULTS / "runs") / experiment
    latest = {}
    for run in sorted(base.glob("*__*")):
        meta = json.loads((run / "run.json").read_text())
        res_path = run / "artifacts" / "result.json"
        if meta.get("status") != "FINISHED" or not res_path.exists():
            continue
        aid = meta["tags"].get("analysis", meta["run_name"])
        latest[aid] = dict(meta=meta, result=json.loads(res_path.read_text()), dir=str(run))
    return latest


def _fmt(x, d=4):
    if x is None or (isinstance(x, float) and x != x):
        return "—"
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, (int,)):
        return str(x)
    if isinstance(x, float):
        return f"{x:.{d}f}"
    return str(x)


def markdown_table(frame: pd.DataFrame) -> str:
    cols = list(frame.columns)
    rows = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    for rec in frame.to_dict("records"):
        rows.append("| " + " | ".join(_fmt(rec[c]) for c in cols) + " |")
    return "\n".join(rows)


def tables(runs: dict) -> dict:
    out = {}
    if "H1_H2" in runs:
        r = runs["H1_H2"]["result"]
        c = r["comparisons"]["M5_vs_M2"]
        iv = c.get("intervals", {}) if isinstance(c.get("intervals"), dict) else {}
        iv = iv.get("person", {})
        out["H1"] = pd.DataFrame([dict(
            people=r["n_people"], cells=r["n_cells"], videos=r["n_videos"],
            skill=c["report"]["skill_person_balanced"], p_perm=r["tests"]["H1"]["p"], B=r["tests"]["H1"]["B"],
            ncv90_lo=iv.get("lo_skill"), ncv90_hi=iv.get("hi_skill"), futility_U3=c["futility"]["upper_skill"],
            decision=r.get("h1_decision", {}).get("category"))])
        out["H2"] = pd.DataFrame([dict(test=t, base=v["base"], full=v["full"], p=v["p"], p_holm=v.get("p_holm"),
                                       reject_holm=v.get("reject_holm"), observed_skill_R10=v["observed_skill_R10"])
                                  for t, v in r["tests"].items() if t != "H1"])
        out["models"] = pd.DataFrame([dict(comparison=k, skill_person_balanced=v["report"]["skill_person_balanced"],
                                           skill_cell_weighted=v["report"]["skill_cell_weighted"],
                                           delta_rmse_items=v["report"]["delta_rmse_items"],
                                           state_skill=v["report"]["state_skill"])
                                      for k, v in r["comparisons"].items()])
        out["per_video"] = pd.DataFrame([dict(unit=u, **d) for u, d in c["report"]["per_video"].items()])
        out["per_experiment"] = pd.DataFrame([dict(experiment=e, **d) for e, d in c["report"]["per_experiment"].items()])
        extra = []
        for loss in ("cell", "state"):
            if isinstance(c.get("intervals"), dict) and loss in c["intervals"]:
                i = c["intervals"][loss]
                extra.append(dict(estimate={"cell": "H3.7 cell-weighted", "state": "state skill (exploratory)"}[loss],
                                  point=i["point_skill"], ncv90_lo=i["lo_skill"], ncv90_hi=i["hi_skill"]))
        out["derived"] = pd.DataFrame(extra)
    rows = []
    for aid, run in runs.items():
        res = run["result"]
        if aid.startswith(("H3_", "D_E5", "D_E1")) and "comparisons" in res:
            for k, v in res["comparisons"].items():
                iv = v.get("intervals") if isinstance(v.get("intervals"), dict) else {}
                iv = iv.get("person", {})
                rows.append(dict(analysis=aid, comparison=k, people=res["n_people"], cells=res["n_cells"], videos=res["n_videos"],
                                 skill=v["report"]["skill_person_balanced"], ncv90_lo=iv.get("lo_skill"), ncv90_hi=iv.get("hi_skill")))
    out["robustness_and_descriptive_A"] = pd.DataFrame(rows)
    if "D_BC" in runs:
        r = runs["D_BC"]["result"]
        out["BC"] = pd.DataFrame([dict(regime=g, within_content_skill=v["within_content_skill"], absolute_skill=v["absolute_skill"],
                                       boot90_lo=v["interval"]["lo"], boot90_hi=v["interval"]["hi"]) for g, v in r["regimes"].items()])
        out["BC_per_video"] = pd.DataFrame([dict(video=vid, B=r["regimes"]["B"]["per_video"][vid]["skill"],
                                                 C=r["regimes"]["C"]["per_video"][vid]["skill"], B_minus_C=r["B_minus_C_per_video"][vid])
                                            for vid in r["B_minus_C_per_video"]])
    if "D_CAS" in runs:
        out["CAS"] = pd.DataFrame([{k: v for k, v in runs["D_CAS"]["result"].items() if not isinstance(v, (dict, list))}])
    if "D_transport" in runs:
        rows = []
        for d, variants in runs["D_transport"]["result"]["directions"].items():
            for variant, v in variants.items():
                ci = v["loss_difference_interval_conditional_on_fitted_source_model"]
                rows.append(dict(direction=d, variant=variant, skill=v["skill"], loss_diff_lo=ci["lo"], loss_diff_hi=ci["hi"]))
        out["transport"] = pd.DataFrame(rows)
    if "X_explanatory" in runs:
        out["explanatory"] = pd.DataFrame(runs["X_explanatory"]["result"]["fixed_effects"])
    if "S_identity_probe" in runs:
        out["identity_probe"] = pd.DataFrame([{k: v for k, v in runs["S_identity_probe"]["result"].items()}])
    return out


def write(experiment: str, out_dir: Path, title: str, root: Path | None = None) -> Path:
    runs = collect(experiment, root)
    t = tables(runs)
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", "", f"Tracking experiment `{experiment}`; {len(runs)} registry analyses collated.", ""]
    srcs = {r['meta']['tags'].get('outcome_source', '?') for r in runs.values()}
    lines += [f"Outcome source(s): {', '.join(sorted(srcs))}", ""]
    for name, frame in t.items():
        if frame is None or frame.empty:
            continue
        frame.to_csv(out_dir / f"{name}.csv", index=False)
        lines += [f"## {name}", "", markdown_table(frame), ""]
    lines += ["## Runs", ""] + [f"- `{aid}`: run `{r['meta']['run_id']}`, config `{r['meta']['config']['sha256'][:12]}`, "
                                f"frozen={r['meta']['config']['frozen']}, git `{str(r['meta']['git']['commit'])[:10]}`"
                                for aid, r in sorted(runs.items())]
    path = out_dir / "report.md"
    path.write_text("\n".join(lines) + "\n")
    return path
