"""Tabulate the finished run-book steps 2-4 runs into the phase evidence tables (outcome-free post-processing).

Reads only the tracked artifacts of the latest FINISHED run of each registry analysis in one tracking
experiment (result.json, run.json and, where logged, predictions.parquet, cells.parquet,
log10_lambda_absolute.json, outer_folds.npy) plus the frozen, outcome-free population ledger and
feature tables. It never calls the outcome loader, so it adds no outcome access and computes no new
physiology-outcome quantity: every scientific number it writes is copied from a result.json.

The only values it derives are:
  * case flow per analysis set (from the frozen ledger);
  * outcome-free quality and missingness summaries of the features of each set;
  * numerical run diagnostics (non-finite predictions, clipping, penalty at the grid edges, folds);
  * descriptive position flags of each reported estimate and interval relative to 0, delta and 2 delta,
    and the IS-028 robustness reading for H3 (same sign as the primary estimate and same side of delta).
    These flags are descriptions of reported numbers, not tests.

Usage:
    PYTHONPATH=src .venv/bin/python docs/research/preregistered_completion/evidence/summarize_steps2_4.py \
        results/runs/g01r-confirmatory docs/research/preregistered_completion/evidence/tables
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
from g01r.config import IMPL_EVIDENCE, load_config  # noqa: E402

STEP = {"H3_1_partial": 2, "H3_6_gpa": 2, "H3_2_eye30": 3, "H3_2_eye70": 3, "H3_3_four": 3, "H3_4_raw": 3,
        "H3_5_alpha": 3, "D_BC": 4, "D_CAS": 4, "D_E5": 4, "D_transport": 4, "D_E1": 4, "X_explanatory": 4,
        "S_identity_probe": 4}
ROLE = {"H3": "robustness (H3; estimate + interval only; IS-028)", "D_E5": "descriptive", "D_E1": "descriptive",
        "D_BC": "descriptive", "D_CAS": "descriptive", "D_transport": "descriptive",
        "X_explanatory": "explanatory (never predictive evidence)", "S_identity_probe": "diagnostic (shortcut ii)"}
CORE_FEATURES = ["RF1_eeg_posterior_alpha", "RF2_eeg_frontal_theta", "RF3_heart_rate", "RF4_ln_rmssd",
                 "RF5_gaze_dispersion", "RF6_saccade_rate"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def latest_runs(base: Path) -> dict:
    out = {}
    for run in sorted(base.glob("*__*")):
        meta = json.loads((run / "run.json").read_text())
        res = run / "artifacts" / "result.json"
        if meta.get("status") != "FINISHED" or not res.exists():
            continue
        out[meta["tags"].get("analysis", meta["run_name"])] = run
    return out


def flags(point, lo, hi, delta, thr):
    d = dict(point_below_delta=point < delta, point_below_0=point < 0)
    if lo is not None and hi is not None:
        d.update(interval_contains_0=lo <= 0 <= hi, interval_contains_delta=lo <= delta <= hi,
                 interval_upper_below_2delta=hi < thr, interval_lower_above_0=lo > 0)
    return d


def role(aid):
    return ROLE["H3"] if aid.startswith("H3") else ROLE.get(aid, "")


def main(base: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    cfg = load_config()
    delta, thr = cfg.inference["delta"], cfg.inference["futility_threshold"]
    runs = latest_runs(base)
    primary = json.loads((runs["H1_H2"] / "artifacts" / "result.json").read_text())
    p_rep = primary["comparisons"]["M5_vs_M2"]["report"]
    S0 = p_rep["skill_person_balanced"]

    # ------------------------------------------------------------------ case flow per set (frozen ledger)
    sets = pd.read_csv(IMPL_EVIDENCE / "population" / "analysis_sets.csv")
    rows = []
    for s in ["PAS_E34_core", "PAS_E34_core_eye30", "PAS_E34_core_eye70", "PAS_E34_four", "PAS_E34_core_alpha30",
              "CAS_E34", "E5_core", "E4_core", "E1_gaze"]:
        sub = sets[sets[s]]
        for e, g in [("all", sub)] + list(sub.groupby("experiment")):
            rows.append(dict(set=s, experiment=e, people=g.qualified_participant_id.nunique(), cells=len(g),
                             videos=g.canonical_video_id.nunique(),
                             vs_PAS_core_cells_added=int((g.PAS_E34_core == False).sum()),   # noqa: E712
                             vs_PAS_core_cells_removed=None if e != "all" else int((sets.PAS_E34_core & ~sets[s]).sum())))
    pd.DataFrame(rows).to_csv(out / "case_flow_by_set.csv", index=False)

    # ------------------------------------------------------------------ quality / missingness per set (outcome-free)
    from g01r.design import FeatureProvider
    from g01r.population import Population
    pop = Population(cfg)
    qrows = []
    for s, route in [("PAS_E34_core", "processed"), ("PAS_E34_core", "raw"), ("PAS_E34_core_eye30", "processed"),
                     ("PAS_E34_core_eye70", "processed"), ("PAS_E34_four", "processed"),
                     ("PAS_E34_core_alpha30", "processed"), ("CAS_E34", "processed"), ("E5_core", "processed"),
                     ("E1_gaze", "processed")]:
        aset = pop.analysis_set(s)
        st = FeatureProvider(cfg, aset, route).static
        row = dict(set=s, route=route, people=aset.n_person, cells=aset.n)
        for c in ["Q_gaze_correction", "Q_pupil_correction", "Q_eeg_zeroed", "Q_eeg_16hz_excess"]:
            v = st[c].to_numpy(float)
            row[f"{c}_median"] = float(np.nanmedian(v)) if np.isfinite(v).any() else None
            row[f"{c}_max"] = float(np.nanmax(v)) if np.isfinite(v).any() else None
        for c in ["Q_gaze_missing", "Q_pupil_absent", "Q_eeg_missing"]:
            row[f"{c}_cells"] = int(np.nansum(st[c].to_numpy(float)))
        for b in ["RF_EEG", "RF_ECG", "RF_GAZE", "RF_PUPIL"]:
            row[f"{b}_missing_cells"] = int(st[f"{b}_missing"].sum())
        qrows.append(row)
    pd.DataFrame(qrows).to_csv(out / "quality_missingness_by_set.csv", index=False)

    # ------------------------------------------------------------------ regime-A analyses (H3, D_E5, D_E1)
    rob, pe, pv, diag, digest = [], [], [], [], {}
    for aid, run in sorted(runs.items()):
        res = json.loads((run / "artifacts" / "result.json").read_text())
        meta = json.loads((run / "run.json").read_text())
        art = run / "artifacts"
        digest[aid] = dict(run_id=meta["run_id"], run_dir=str(run.relative_to(ROOT)), status=meta["status"],
                           start_utc=meta["start_utc"], end_utc=meta["end_utc"], elapsed_s=res.get("elapsed_s"),
                           config=meta["config"], git=meta["git"], code_sha256=meta["code"],
                           environment=meta["environment"], mlflow=meta.get("mlflow"),
                           mlflow_errors=meta.get("mlflow_errors", []), identity=meta.get("identity"),
                           outcome_source=meta["tags"].get("outcome_source"),
                           artifacts={p.name: sha256(p) for p in sorted(art.iterdir()) if p.is_file()})
        if aid == "H1_H2" or "comparisons" not in res:
            continue
        for k, v in res["comparisons"].items():
            r = v["report"]
            iv = v["intervals"]["person"] if isinstance(v.get("intervals"), dict) else {}
            point = r["skill_person_balanced"]
            row = dict(analysis=aid, role=role(aid), step=STEP.get(aid), comparison=k, set=res["set"],
                       outcome=res["outcome"], route=res["route"], people=res["n_people"], cells=res["n_cells"],
                       videos=res["n_videos"], skill_person_balanced=point,
                       ncv90_lo=iv.get("lo_skill"), ncv90_hi=iv.get("hi_skill"), ncv_centre=iv.get("centre_skill"),
                       ncv_reps=iv.get("reps"), ncv_root_over_se=iv.get("root_over_se"),
                       skill_cell_weighted=r["skill_cell_weighted"], base_mse_pb=r["base_mse_person_balanced"],
                       full_mse_pb=r["full_mse_person_balanced"], delta_rmse_items=r["delta_rmse_items"],
                       delta_mae_items=r["delta_mae_items"], state_skill_point=r["state_skill"],
                       calib_base_slope=r["calibration_base"]["slope"], calib_full_slope=r["calibration_full"]["slope"],
                       calib_base_intercept=r["calibration_base"]["intercept"],
                       calib_full_intercept=r["calibration_full"]["intercept"],
                       set_identity=res["set_identity"], split_identity=res["split_identity"])
            row.update(flags(point, iv.get("lo_skill"), iv.get("hi_skill"), delta, thr))
            if aid.startswith("H3"):
                same_sign = np.sign(point) == np.sign(S0)
                same_side = (point < delta) == (S0 < delta)
                row.update(primary_skill=S0, same_sign_as_primary=bool(same_sign),
                           same_side_of_delta_as_primary=bool(same_side),
                           IS028_reading="robust" if same_sign and same_side else "sensitive")
            rob.append(row)
            for e, d in r["per_experiment"].items():
                pe.append(dict(analysis=aid, comparison=k, experiment=int(e), **d))
            for unit, d in r["per_video"].items():
                pv.append(dict(analysis=aid, comparison=k, unit=unit, skill_cell_weighted=d["skill"],
                               cells_people=d["people"]))
        # numerical diagnostics of the predictions
        if (art / "predictions.parquet").exists():
            preds = pd.read_parquet(art / "predictions.parquet")
            cells = pd.read_parquet(art / "cells.parquet")
            assert not ({"normalized_exact_score", "normalized_partial_score"} & set(cells.columns)), "cells must be outcome-free"
            lam = json.loads((art / "log10_lambda_absolute.json").read_text())
            folds = np.load(art / "outer_folds.npy")
            R, K = folds.shape[0], cfg.resampling["outer_folds_A"]
            person = cells.person.to_numpy()
            ntrain = [int((folds[r][person] != k).sum()) for r in range(R) for k in range(K)]
            lo_, hi_ = cfg.raw["model"]["lambda_log10_min"], cfg.raw["model"]["lambda_log10_max"]
            for m, g in preds.groupby("model"):
                arr = np.array(lam[m], float)
                d = dict(analysis=aid, model=m, predictions=len(g), nonfinite_predictions=int((~np.isfinite(g.pred)).sum()),
                         pred_min=float(g.pred.min()), pred_max=float(g.pred.max()),
                         clipped_at_0=int((g.pred <= 0).sum()), clipped_at_1=int((g.pred >= 1).sum()),
                         cells_with_any_clip_at_0=int(g[g.pred <= 0].cell.nunique()),
                         every_cell_tested_every_rep=bool(np.isfinite(g.pred).all()),
                         folds_per_rep=",".join(map(str, sorted({len(np.unique(f)) for f in folds}))))
                if len(arr) == len(ntrain):
                    rel = arr - np.log10(ntrain)
                    d.update(log10_lambda_rel_median=float(np.median(rel)),
                             share_at_grid_min=float(np.mean(np.isclose(rel, lo_, atol=1e-6))),
                             share_at_grid_max=float(np.mean(np.isclose(rel, hi_, atol=1e-6))))
                diag.append(d)
            # which cells were clipped at 0 (cell index -> outcome-free identifiers and the 16 Hz quality value)
            clip = preds[preds.pred <= 0].groupby(["model", "cell"]).size().rename("n_clipped").reset_index()
            if len(clip):
                aset = pop.analysis_set(res["set"])
                st = FeatureProvider(cfg, aset, res["route"]).static
                clip["experiment"] = cells.experiment.to_numpy()[clip.cell] if "experiment" in cells else None
                clip["person_index"] = person[clip.cell]
                clip["Q_eeg_16hz_excess"] = st.Q_eeg_16hz_excess.to_numpy()[clip.cell]
                rank = st.Q_eeg_16hz_excess.rank(ascending=False, method="min").to_numpy()
                clip["Q_eeg_16hz_excess_rank_in_set"] = rank[clip.cell]
                clip.insert(0, "analysis", aid)
                clip.to_csv(out / f"clipped_at_zero_{aid}.csv", index=False)

    pd.DataFrame(rob).to_csv(out / "regime_A_steps2_4.csv", index=False)
    pd.DataFrame(pe).to_csv(out / "per_experiment_steps2_4.csv", index=False)
    pd.DataFrame(pv).to_csv(out / "per_video_steps2_4.csv", index=False)
    pd.DataFrame(diag).to_csv(out / "run_diagnostics_steps2_4.csv", index=False)

    # H3 summary including H3.7 (derived from the H1 fits; IS-016)
    h3 = [r for r in rob if r["analysis"].startswith("H3")]
    cw = primary["comparisons"]["M5_vs_M2"]["intervals"]["cell"]
    h37 = dict(analysis="H3_7_cell", role=ROLE["H3"], step=1, comparison="M5_vs_M2 (cell-weighted)", set="PAS_E34_core",
               outcome="exact", route="processed", people=primary["n_people"], cells=primary["n_cells"],
               videos=primary["n_videos"], skill_person_balanced=cw["point_skill"], ncv90_lo=cw["lo_skill"],
               ncv90_hi=cw["hi_skill"], primary_skill=S0, same_sign_as_primary=bool(np.sign(cw["point_skill"]) == np.sign(S0)),
               same_side_of_delta_as_primary=bool((cw["point_skill"] < delta) == (S0 < delta)))
    h37["IS028_reading"] = "robust" if h37["same_sign_as_primary"] and h37["same_side_of_delta_as_primary"] else "sensitive"
    h37.update(flags(cw["point_skill"], cw["lo_skill"], cw["hi_skill"], delta, thr))
    cols = ["analysis", "comparison", "set", "outcome", "route", "people", "cells", "videos", "skill_person_balanced",
            "ncv90_lo", "ncv90_hi", "primary_skill", "same_sign_as_primary", "same_side_of_delta_as_primary",
            "IS028_reading", "point_below_delta", "interval_contains_0", "interval_contains_delta",
            "interval_upper_below_2delta"]
    pd.DataFrame(h3 + [h37]).reindex(columns=cols).to_csv(out / "h3_summary.csv", index=False)

    # ------------------------------------------------------------------ regimes B / C
    if "D_BC" in runs:
        r = json.loads((runs["D_BC"] / "artifacts" / "result.json").read_text())
        rows = []
        for g, v in r["regimes"].items():
            d = dict(regime=g, full_model={"B": "M5_B = M2 + RF", "C": "M5 = M2 + RF + SYN_C"}[g], base_model="M2",
                     people=r["n_people"], cells=r["n_cells"], videos=r["n_videos"],
                     within_content_skill=v["within_content_skill"], absolute_skill=v["absolute_skill"],
                     boot90_lo=v["interval"]["lo"], boot90_hi=v["interval"]["hi"], boot_B=v["interval"]["B"],
                     interval_label=v["interval"]["label"])
            d.update(flags(v["within_content_skill"], v["interval"]["lo"], v["interval"]["hi"], delta, thr))
            rows.append(d)
        pd.DataFrame(rows).to_csv(out / "bc_pooled.csv", index=False)
        pd.DataFrame([dict(video=vid, cells=r["regimes"]["B"]["per_video"][vid]["cells"],
                           B=r["regimes"]["B"]["per_video"][vid]["skill"], C=r["regimes"]["C"]["per_video"][vid]["skill"],
                           B_minus_C=r["B_minus_C_per_video"][vid]) for vid in r["B_minus_C_per_video"]]
                     ).to_csv(out / "bc_per_video.csv", index=False)
    if "D_CAS" in runs:
        r = json.loads((runs["D_CAS"] / "artifacts" / "result.json").read_text())
        pd.DataFrame([{k: v for k, v in r.items() if not isinstance(v, (dict, list))}]).to_csv(out / "cas.csv", index=False)
    if "D_transport" in runs:
        r = json.loads((runs["D_transport"] / "artifacts" / "result.json").read_text())
        rows = []
        for d, variants in r["directions"].items():
            for variant, v in variants.items():
                ci = v["loss_difference_interval_conditional_on_fitted_source_model"]
                rows.append(dict(direction=d, variant=variant, skill_person_balanced=v["skill"],
                                 loss_diff_boot90_lo=ci["lo"], loss_diff_boot90_hi=ci["hi"],
                                 loss_diff_interval_excludes_0=bool(ci["lo"] > 0 or ci["hi"] < 0)))
        pd.DataFrame(rows).to_csv(out / "transport.csv", index=False)
    if "X_explanatory" in runs:
        r = json.loads((runs["X_explanatory"] / "artifacts" / "result.json").read_text())
        pd.DataFrame(r["fixed_effects"]).to_csv(out / "explanatory_fixed_effects.csv", index=False)
        pd.DataFrame([dict(converged=r["converged"], reml_neg_loglik=r["reml_neg_loglik"],
                           var_person=r["variance"]["group_a"], var_content=r["variance"]["group_b"],
                           var_residual=r["variance"]["residual"], label=r["label"])]
                     ).to_csv(out / "explanatory_variance.csv", index=False)
    if "S_identity_probe" in runs:
        r = json.loads((runs["S_identity_probe"] / "artifacts" / "result.json").read_text())
        pd.DataFrame([{k: v for k, v in r.items() if not isinstance(v, (dict, list))}]
                     ).to_csv(out / "identity_probe.csv", index=False)

    (out / "run_digest_steps2_4.json").write_text(json.dumps(digest, indent=2, default=float) + "\n")
    print(pd.DataFrame(h3 + [h37]).reindex(columns=cols).to_string())


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
