"""Frozen analysis-set ledger for the G01 protocol (WP3 / gate M03).

Builds the case flow and an analysis-set manifest from existing audited tables.
Pre-existing provisional QC flags (audit_config.json) are used unchanged.
Fits nothing and computes no association between physiology and outcomes.
The manifest contains keys and membership flags only, without outcome values.

Run from the repository root:
    .venv/bin/python docs/research/experimental_design/evidence/design_ledger.py
"""
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
AUDIT = ROOT / "docs/research/dataset_exploration/evidence"
OUT = Path(__file__).resolve().parent

# Tested exposure defined by protocol chronology (forecast after this viewing, before the quiz).
TESTED = {
    1: dict(session=1, condition=None, role="E1 ocular-only secondary cohort, first attentive viewing"),
    3: dict(session=1, condition="intentional_attend", role="primary first-view, intentional"),
    4: dict(session=2, condition="attend_tested_content", role="primary first-view, second block"),
    5: dict(session=2, condition="incentive_preview_repeat", role="repeat-exposure stress test"),
}
CORE = ["eeg", "ecg", "gaze"]          # primary sensor policy (see measurement_provenance.md)
FOUR = ["eeg", "ecg", "gaze", "pupil"]  # prior 'tri-modal' definition: eye = gaze AND pupil
KEYS = ["experiment", "participant_id", "canonical_video_id"]


def tested_cells():
    tensor = pd.read_parquet(AUDIT / "exposure_tensor.parquet")
    elig = pd.read_parquet(AUDIT / "gate_closure_behavioral_eligibility.parquet")
    elig = elig[elig.question_type == "memory"][KEYS + ["gate_behavior_eligible", "gate_behavior_reason"]]
    frames = []
    for exp, spec in TESTED.items():
        x = tensor[(tensor.experiment == exp) & (tensor.session == spec["session"])]
        if spec["condition"]:
            x = x[x.condition == spec["condition"]]
        frames.append(x)
    cells = pd.concat(frames, ignore_index=True)
    cells = cells.merge(elig, on=KEYS, how="left")
    cells["eligible_outcome"] = cells.gate_behavior_eligible.fillna(False).astype(bool)
    return cells


def flag(cells, mods, kind):
    return np.all([cells[f"{m}_{kind}"].fillna(False).astype(bool) for m in mods], axis=0)


def count(frame):
    return dict(people=int(frame.qualified_participant_id.nunique()), cells=int(len(frame)),
                videos=int(frame.canonical_video_id.nunique()))


def main():
    cells = tested_cells()
    cells["core_present"] = flag(cells, CORE, "present")
    cells["core_qc"] = flag(cells, CORE, "basic_qc")
    cells["pupil_qc"] = flag(cells, ["pupil"], "basic_qc")
    cells["four_qc"] = flag(cells, FOUR, "basic_qc")
    cells["gaze_qc"] = flag(cells, ["gaze"], "basic_qc")

    e34 = cells.experiment.isin([3, 4])
    ok = cells.eligible_outcome
    sets = {
        "CAS_E34": e34 & ok,                          # coverage set: all eligible first-view outcomes
        "PAS_E34_core": e34 & ok & cells.core_qc,     # primary analysis set
        "PAS_E34_four": e34 & ok & cells.four_qc,     # pupil secondary / prior-definition sensitivity
        "E5_core": (cells.experiment == 5) & ok & cells.core_qc,
        "E5_four": (cells.experiment == 5) & ok & cells.four_qc,
        "E5_CAS": (cells.experiment == 5) & ok,
        "E1_gaze": (cells.experiment == 1) & ok & cells.gaze_qc,
        "E1_gaze_pupil": (cells.experiment == 1) & ok & cells.gaze_qc & cells.pupil_qc,
    }
    for name, mask in sets.items():
        cells[name] = mask

    # Stage-wise case flow per experiment, with the reason each cell leaves.
    flow = []
    for exp in [3, 4, 5, 1]:
        x = cells[cells.experiment == exp]
        stages = [("design tested cells", np.ones(len(x), bool)),
                  ("eligible outcome", x.eligible_outcome.to_numpy())]
        if exp != 1:
            m = x.eligible_outcome.to_numpy()
            for mod in CORE:
                m = m & x[f"{mod}_basic_qc"].fillna(False).astype(bool).to_numpy()
                stages.append((f"+ {mod} QC (cumulative)", m.copy()))
            stages.append(("+ pupil QC (cumulative, four-sensor)", m & x.pupil_qc.to_numpy()))
        else:
            m = x.eligible_outcome.to_numpy() & x.gaze_qc.to_numpy()
            stages.append(("+ gaze QC", m))
            stages.append(("+ pupil QC", m & x.pupil_qc.to_numpy()))
        for label, mask in stages:
            flow.append(dict(experiment=exp, stage=label, **count(x[mask])))
    flow = pd.DataFrame(flow)
    flow.to_csv(OUT / "case_flow.csv", index=False)

    # Exclusion reasons inside eligible E3-E5 cells (first failing core modality, then pupil).
    reasons = []
    for _, r in cells[cells.experiment.isin([3, 4, 5]) & cells.eligible_outcome].iterrows():
        why = "included_core"
        for mod in CORE:
            if not bool(r[f"{mod}_basic_qc"]):
                why = f"{mod}: " + ("absent" if not bool(r[f"{mod}_present"]) else str(r[f"{mod}_qc_reasons"]))
                break
        reasons.append(dict(experiment=r.experiment, reason=why,
                            pupil_qc=bool(r.pupil_qc)))
    reasons = pd.DataFrame(reasons)
    reasons.groupby(["experiment", "reason"]).size().rename("cells").reset_index().to_csv(
        OUT / "core_exclusion_reasons.csv", index=False)

    # Incidence: people x videos per experiment in each analysis set.
    inc = []
    for name in sets:
        x = cells[cells[name]]
        for (exp, vid), f in x.groupby(["experiment", "canonical_video_id"]):
            inc.append(dict(set=name, experiment=exp, canonical_video_id=vid, people=f.qualified_participant_id.nunique()))
        per_person = x.groupby("qualified_participant_id").size()
        inc.append(dict(set=name, experiment=-1, canonical_video_id="cells_per_person_histogram",
                        people=json.dumps({int(k): int(v) for k, v in per_person.value_counts().sort_index().items()})))
    pd.DataFrame(inc).to_csv(OUT / "analysis_set_incidence.csv", index=False)

    # Covariate availability inside each analysis set (person level).
    traits = pd.read_parquet(AUDIT / "participant_traits.parquet")
    traits = traits.assign(
        sex_known=traits.Sex.isin(["Male", "Female"]),
        age_known=traits.Age.notna(),
        asrs_known=traits.asrs_recomputed_inattention_0_4.notna() & traits.asrs_recomputed_hyperactivity_0_4.notna(),
        digit_span_valid=traits.digit_span.between(3, 7),
        gpa_valid=traits.GPA_numeric.astype(float).between(0.01, 4.0),
    )
    cov = []
    for name in sets:
        people = cells[cells[name]].qualified_participant_id.unique()
        t = traits[traits.qualified_participant_id.isin(people)]
        row = dict(set=name, people=len(people))
        for c in ["sex_known", "age_known", "asrs_known", "digit_span_valid", "gpa_valid"]:
            row[c] = int(t[c].sum())
        cov.append(row)
    pd.DataFrame(cov).to_csv(OUT / "covariate_availability.csv", index=False)

    # Descriptive selection diagnostic required by the protocol's flow report:
    # outcome distribution inside versus outside the primary set among eligible E3+E4 cells.
    outcomes = pd.read_parquet(AUDIT / "gate_closure_behavioral_eligibility.parquet")
    outcomes = outcomes[outcomes.question_type == "memory"][KEYS + ["normalized_exact_score", "normalized_partial_score"]]
    cas = cells[cells.CAS_E34].merge(outcomes, on=KEYS, how="left")
    sel = (cas.groupby(["experiment", "PAS_E34_core"])
              .agg(people=("qualified_participant_id", "nunique"), cells=("participant_id", "size"),
                   mean_exact=("normalized_exact_score", "mean"), mean_partial=("normalized_partial_score", "mean"))
              .reset_index())
    sel.to_csv(OUT / "selection_diagnostic.csv", index=False)

    # Prespecified eye-correction threshold sensitivity (0.30 / 0.70 instead of 0.50); all other rules fixed.
    summ_x = pd.read_parquet(AUDIT / "exploratory_exposure_summaries.parquet")[
        KEYS + ["session", "gaze_correction_fraction", "pupil_correction_fraction"]]
    cells = cells.merge(summ_x, on=KEYS + ["session"], how="left")
    for thr in (0.30, 0.70):
        tag = f"{int(thr * 100):02d}"
        gaze_alt = (cells.gaze_qc_reasons.isin(["[]", '["correction_gt_50pct"]'])
                    & (cells.gaze_correction_fraction <= thr))
        cells[f"PAS_E34_core_eye{tag}"] = (e34 & ok & flag(cells, ["eeg", "ecg"], "basic_qc") & gaze_alt).to_numpy()
        sets[f"PAS_E34_core_eye{tag}"] = cells[f"PAS_E34_core_eye{tag}"]

    manifest_cols = KEYS + ["qualified_participant_id", "session", "local_stimulus_id", "condition",
                            "exposure_number"] + list(sets)
    manifest = cells[manifest_cols].copy()
    manifest = manifest[manifest[list(sets)].any(axis=1)]
    manifest.to_csv(OUT / "analysis_set_manifest.csv", index=False)

    summary = {name: count(cells[cells[name]]) for name in sets}
    summary["by_experiment"] = {name: {str(e): count(f) for e, f in cells[cells[name]].groupby("experiment")}
                                for name in sets}
    summary["qc_rules"] = "audit_config.json basic_qc unchanged (max_eye_correction_fraction 0.5, etc.)"
    summary["outcome_values_in_manifest"] = False
    (OUT / "design_ledger.json").write_text(json.dumps(summary, indent=2) + "\n")
    # Consistency with the inherited, previously verified ceilings.
    assert summary["PAS_E34_four"] == {"people": 57, "cells": 216, "videos": 8}
    assert summary["CAS_E34"] == {"people": 72, "cells": 302, "videos": 8}
    print(flow.to_string(index=False))
    print(json.dumps({k: v for k, v in summary.items() if k != "by_experiment"}, indent=2))


if __name__ == "__main__":
    main()
