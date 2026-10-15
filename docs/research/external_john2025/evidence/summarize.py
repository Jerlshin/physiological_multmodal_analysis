"""Tabulate the aggregate replication result (evidence/results/results.json) into CSV tables.

Reads only the committed aggregate file; it never calls the outcome loader and writes no
participant-level value.

    python docs/research/external_john2025/evidence/summarize.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent


def main():
    res = json.loads((HERE / "results" / "results.json").read_text())
    rows = []
    for cid, c in res["comparisons"].items():
        r = c["report"]
        row = dict(comparison=cid, set=c["set"], base=c["base"], full=c["full"], n=r["n_people"], skill=r["skill"],
                   base_mse=r["base_mse"], full_mse=r["full_mse"], delta_rmse_items=r["delta_rmse_items"],
                   delta_mae_items=r["delta_mae_items"], skill_rep_min=r["skill_per_repetition"]["min"],
                   skill_rep_max=r["skill_per_repetition"]["max"], calib_slope_full=r["calibration_full"]["slope"],
                   role=c["role"])
        if "test" in c:
            row.update(p=c["test"]["p"], observed_skill_R10=c["test"]["observed_skill_R10"], B=c["test"]["B"])
        if "interval" in c:
            row.update(ncv90_lo=c["interval"]["lo_skill"], ncv90_hi=c["interval"]["hi_skill"],
                       ncv_centre=c["interval"]["centre_skill"], ncv_root_over_se=c["interval"]["root_over_se"])
        if "futility" in c:
            row.update(futility_upper_skill=c["futility"]["upper_skill"],
                       rules_out_2delta=c["futility"]["rules_out_threshold"])
        if "decision" in c:
            row.update(decision=c["decision"]["category"])
        rows.append(row)
    table = pd.DataFrame(rows)
    out = HERE / "tables"
    out.mkdir(exist_ok=True)
    table.to_csv(out / "comparisons.csv", index=False, float_format="%.5f")
    sets = pd.DataFrame([dict(set=k, **{x: v[x] for x in ("name", "n_people", "outcome_mean", "outcome_sd",
                                                           "split_identity", "set_identity")})
                         for k, v in res["sets"].items()])
    sets.to_csv(out / "sets.csv", index=False, float_format="%.5f")
    lam = pd.DataFrame({k: v["lambda_at_grid_min_share"] for k, v in res["sets"].items()})
    lam.to_csv(out / "penalty_at_grid_minimum_share.csv", float_format="%.4f")
    print(table[["comparison", "n", "skill", "p", "ncv90_lo", "ncv90_hi", "decision"]].to_string(index=False))


if __name__ == "__main__":
    main()
