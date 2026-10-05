"""Tabulate one finished H1_H2 run into the phase evidence tables (outcome-free post-processing).

Reads only the run's tracked artifacts (result.json, run.json, predictions.parquet, cells.parquet,
log10_lambda_absolute.json, outer_folds.npy, permutation nulls). It never calls the outcome loader,
so it adds no outcome access and computes no new physiology-outcome quantity: every scientific number
it writes is copied from result.json. The only values it derives are numerical run diagnostics
(non-finite predictions, penalty at the grid edges, fold-assignment checks, null-distribution shape).

Usage:
    PYTHONPATH=src .venv/bin/python docs/research/confirmatory_h1h2/evidence/summarize_h1h2.py <run_dir> <out_dir>
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))
from g01r.config import load_config  # noqa: E402


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(run_dir: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    art = run_dir / "artifacts"
    res = json.loads((art / "result.json").read_text())
    meta = json.loads((run_dir / "run.json").read_text())
    cfg = load_config()
    delta, thr = cfg.inference["delta"], cfg.inference["futility_threshold"]

    # ------------------------------------------------------------------ H1
    c = res["comparisons"]["M5_vs_M2"]
    rep, fut, iv = c["report"], c["futility"], c["intervals"]
    h1 = res["tests"]["H1"]
    h1_row = dict(
        people=res["n_people"], cells=res["n_cells"], videos=res["n_videos"],
        skill_person_balanced=rep["skill_person_balanced"],
        ncv90_lo=iv["person"]["lo_skill"], ncv90_hi=iv["person"]["hi_skill"],
        ncv_centre_skill=iv["person"]["centre_skill"], ncv_reps=iv["person"]["reps"],
        ncv_root_over_se=iv["person"]["root_over_se"],
        p_perm=h1["p"], B=h1["B"], perm_reps=h1["reps"], observed_skill_R10=h1["observed_skill_R10"],
        futility_U3=fut["upper_skill"], futility_J=fut["J"], futility_rules_out_0_10=fut["rules_out_threshold"],
        skill_ge_delta=rep["skill_person_balanced"] >= delta, U3_lt_2delta=fut["upper_skill"] < thr,
        decision=res["h1_decision"]["category"], detection_procedure=res["detection_procedure"],
        base_mse_pb=rep["base_mse_person_balanced"], full_mse_pb=rep["full_mse_person_balanced"],
        delta_mse_pb=rep["delta_mse_person_balanced"], delta_rmse_items=rep["delta_rmse_items"],
        delta_mae_items=rep["delta_mae_items"])
    pd.DataFrame([h1_row]).to_csv(out / "h1.csv", index=False)

    # ------------------------------------------------------------------ H2 (Holm)
    rows = []
    for t in cfg.inference["holm_family"]:
        v = res["tests"][t]
        comp = {"H2a": "M5_vs_M3", "H2b": "M_EEG_vs_M2", "H2c": "M_ECG_vs_M2", "H2d": "M_GAZE_vs_M2"}[t]
        rows.append(dict(test=t, base=v["base"], full=v["full"], tested_blocks="+".join(v["tested_blocks"]),
                         skill_person_balanced_R50=res["comparisons"][comp]["report"]["skill_person_balanced"],
                         observed_skill_R10=v["observed_skill_R10"], p=v["p"], p_holm=v["p_holm"],
                         reject_holm=v["reject_holm"], null_mean=v["null_mean"], null_q95=v["null_q95"], B=v["B"]))
    pd.DataFrame(rows).to_csv(out / "h2_holm.csv", index=False)

    # ------------------------------------------------------------------ every prespecified comparison
    rows = []
    for k, v in res["comparisons"].items():
        r = v["report"]
        rows.append(dict(comparison=k, skill_person_balanced=r["skill_person_balanced"],
                         skill_cell_weighted=r["skill_cell_weighted"], base_mse_pb=r["base_mse_person_balanced"],
                         full_mse_pb=r["full_mse_person_balanced"], delta_rmse_items=r["delta_rmse_items"],
                         delta_mae_items=r["delta_mae_items"], state_skill_point=r["state_skill"],
                         calib_base_slope=r["calibration_base"]["slope"], calib_base_intercept=r["calibration_base"]["intercept"],
                         calib_full_slope=r["calibration_full"]["slope"], calib_full_intercept=r["calibration_full"]["intercept"],
                         skill_E3=r["per_experiment"]["3"]["skill"], skill_E4=r["per_experiment"]["4"]["skill"]))
    pd.DataFrame(rows).to_csv(out / "comparisons.csv", index=False)

    # ------------------------------------------------------------------ heterogeneity (per experiment, per video)
    rows = []
    for k, v in res["comparisons"].items():
        for e, d in v["report"]["per_experiment"].items():
            rows.append(dict(comparison=k, experiment=int(e), **d))
    pd.DataFrame(rows).to_csv(out / "per_experiment.csv", index=False)
    rows = []
    for k, v in res["comparisons"].items():
        for unit, d in v["report"]["per_video"].items():
            rows.append(dict(comparison=k, unit=unit, skill_cell_weighted=d["skill"], cells_people=d["people"]))
    pd.DataFrame(rows).to_csv(out / "per_video.csv", index=False)

    # ------------------------------------------------------------------ intervals from the H1 fits (H3.7, state)
    rows = []
    labels = {"person": "H1 person-balanced (primary interval)", "cell": "H3.7 cell-weighted (robustness)",
              "state": "state skill (exploratory)"}
    for loss, d in iv.items():
        rows.append(dict(estimate=labels[loss], point_skill=d["point_skill"], ncv_centre_skill=d["centre_skill"],
                         ncv90_lo=d["lo_skill"], ncv90_hi=d["hi_skill"], reps=d["reps"], root_over_se=d["root_over_se"],
                         base_loss=d["base_loss"]))
    pd.DataFrame(rows).to_csv(out / "intervals_from_h1_fits.csv", index=False)

    # ------------------------------------------------------------------ numerical run diagnostics
    preds = pd.read_parquet(art / "predictions.parquet")
    cells = pd.read_parquet(art / "cells.parquet")
    assert not ({"normalized_exact_score", "normalized_partial_score"} & set(cells.columns)), "cells must be outcome-free"
    lam = json.loads((art / "log10_lambda_absolute.json").read_text())
    folds = np.load(art / "outer_folds.npy")
    R, K = cfg.resampling["reps_A"], cfg.resampling["outer_folds_A"]
    rel_lo, rel_hi = cfg.raw["model"]["lambda_log10_min"], cfg.raw["model"]["lambda_log10_max"]
    # n_train per (rep, fold) in cells, in the order the runner extended the lambda lists (rep-major, fold-minor)
    person = cells.person.to_numpy()
    ntrain = [int((folds[r][person] != k).sum()) for r in range(R) for k in range(K)]
    diag = []
    for m, g in preds.groupby("model"):
        arr = np.array(lam[m], float)
        row = dict(model=m, predictions=len(g), nonfinite_predictions=int((~np.isfinite(g.pred)).sum()),
                   pred_min=float(g.pred.min()), pred_max=float(g.pred.max()),
                   clipped_at_0=int((g.pred <= 0).sum()), clipped_at_1=int((g.pred >= 1).sum()), n_lambda=len(arr))
        if m == "M0" or len(arr) != len(ntrain):
            row.update(lambda_note="no penalised inputs" if m == "M0" else f"{len(arr)} penalties vs {len(ntrain)} splits")
        else:
            rel = arr - np.log10(ntrain)
            row.update(log10_lambda_rel_median=float(np.median(rel)),
                       share_at_grid_min=float(np.mean(np.isclose(rel, rel_lo, atol=1e-6))),
                       share_at_grid_max=float(np.mean(np.isclose(rel, rel_hi, atol=1e-6))))
        diag.append(row)
    pd.DataFrame(diag).to_csv(out / "run_diagnostics_models.csv", index=False)

    fold_check = dict(reps=int(folds.shape[0]), people=int(folds.shape[1]),
                      folds_per_rep=sorted({len(np.unique(f)) for f in folds}),
                      every_person_tested_once_per_rep=bool(all(np.isfinite(preds[(preds.model == "M2") & (preds.rep == r)].pred).all()
                                                                for r in range(R))))
    nulls = {}
    for t in res["tests"]:
        n = np.load(art / f"permutation_null_{t}.npy")
        nulls[t] = dict(B=len(n), nonfinite=int((~np.isfinite(n)).sum()), mean=float(n.mean()), sd=float(n.std(ddof=1)),
                        q05=float(np.quantile(n, 0.05)), q50=float(np.median(n)), q95=float(np.quantile(n, 0.95)),
                        observed=res["tests"][t]["observed_loss_difference"],
                        n_null_ge_observed=int((n >= res["tests"][t]["observed_loss_difference"]).sum()))

    digest = dict(
        run_id=meta["run_id"], run_dir=str(run_dir.relative_to(ROOT)), status=meta["status"],
        start_utc=meta["start_utc"], end_utc=meta["end_utc"], elapsed_s=res.get("elapsed_s"),
        config=meta["config"], protocol=meta["protocol"], git=meta["git"], code_sha256=meta["code"],
        environment=meta["environment"], data_download_manifest_sha256=meta["data"]["download_manifest_sha256"],
        mlflow=meta.get("mlflow"), mlflow_errors=meta.get("mlflow_errors", []), identity=meta.get("identity"),
        split_identity=res["split_identity"], set_identity=res["set_identity"],
        detection_procedure=res["detection_procedure"], h1_decision=res["h1_decision"],
        person_bootstrap_NON_DECISIONAL=res.get("person_bootstrap_detection_NON_DECISIONAL"),
        fold_check=fold_check, permutation_nulls=nulls,
        artifacts={p.name: sha256(p) for p in sorted(art.iterdir()) if p.is_file()},
        run_files={p.name: sha256(p) for p in sorted(run_dir.iterdir()) if p.is_file()},
    )
    (out / "run_digest.json").write_text(json.dumps(digest, indent=2, default=float) + "\n")
    print(json.dumps(dict(h1=h1_row, h2=rows and pd.read_csv(out / "h2_holm.csv").to_dict("records")), indent=1, default=str))


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
