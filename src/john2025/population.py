"""Case flow and analysis sets of the replication (outcome-free).

People = EDF files that join a workbook ``Quest`` row (the plan's 117). The frozen QC rule
excludes invalid-sample fraction > 0.50 (the BBBD threshold). Only the identifier, the plan's
covariates (age, sex, condition) and the pretest items are ever read here; ``usecols`` keeps
every ``knowPost_*`` column out of memory.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from g01r.population import AnalysisSet

from .paths import DERIVED, EVIDENCE, SET_NAME, VIDEO, WORKBOOK

PRETEST_ITEMS = ["knowPre_1", "knowPre_2", "knowPre_3", "knowPre_4", "knowPre_6", "knowPre_7", "knowPre_8"]
COVARIATE_SOURCE = ["participants", "age", "sex_n", "condition"] + PRETEST_ITEMS + ["knowPre_sum"]
QC_MAX_INVALID = 0.50
SENSITIVITY_THRESHOLDS = {"eye30": 0.30, "eye70": 0.70}     # amendment A1 (BBBD H3.2 thresholds)
EXPERIMENT_CODE = 0                                          # one cohort, one protocol


def quest_covariates() -> pd.DataFrame:
    q = pd.read_excel(WORKBOOK, sheet_name="Quest", usecols=COVARIATE_SOURCE)
    if any(c.startswith("knowPost") for c in q.columns):
        raise AssertionError("Posttest columns must never be read before the feature freeze")
    q = q.rename(columns={"participants": "participant"})
    q["pretest_sum"] = q[PRETEST_ITEMS].sum(axis=1)
    return q


def case_flow(features: pd.DataFrame, parse: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (person table with flags, case-flow table)."""
    q = quest_covariates()
    edf_ids = set(parse.participant)
    quest_ids = set(q.participant)
    people = features.merge(q, on="participant", how="left", indicator=True)
    people["has_quest"] = people.pop("_merge").eq("both")
    people["qc_pass"] = people.video_window_ok.fillna(False).astype(bool) & (people.Q_invalid <= QC_MAX_INVALID)
    for name, thr in SENSITIVITY_THRESHOLDS.items():
        people[f"qc_{name}"] = people.video_window_ok.fillna(False).astype(bool) & (people.Q_invalid <= thr)
    joined = people[people.has_quest]
    flow = pd.DataFrame([
        ("Workbook Quest rows", len(quest_ids)),
        ("Instructional-video EDF files", len(edf_ids)),
        ("EDF without a Quest row (excluded)", len(edf_ids - quest_ids)),
        ("Quest row without an EDF (no eye data)", len(quest_ids - edf_ids)),
        ("People with EDF + Quest (plan population)", int(len(joined))),
        ("Excluded: no usable video window", int((~joined.video_window_ok.fillna(False).astype(bool)).sum())),
        (f"Excluded: invalid-sample fraction > {QC_MAX_INVALID}", int((joined.video_window_ok.fillna(False).astype(bool)
                                                                       & (joined.Q_invalid > QC_MAX_INVALID)).sum())),
        ("Primary analysis set (QC <= 0.50)", int(joined.qc_pass.sum())),
        ("Sensitivity set A1, QC <= 0.30", int(joined.qc_eye30.sum())),
        ("Sensitivity set A1, QC <= 0.70", int(joined.qc_eye70.sum())),
    ], columns=["step", "people"])
    return people, flow


def analysis_set(people: pd.DataFrame, flag: str = "qc_pass", name: str = SET_NAME) -> AnalysisSet:
    sel = people[people.has_quest & people[flag]].sort_values("participant").reset_index(drop=True)
    cells = pd.DataFrame(dict(experiment=EXPERIMENT_CODE, participant_id=sel.participant,
                              qualified_participant_id="J:" + sel.participant, session=1,
                              local_stimulus_id=VIDEO, canonical_video_id=VIDEO))
    return AnalysisSet(name, cells)


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    features = pd.read_parquet(DERIVED / "person_features.parquet")
    parse = pd.read_csv(EVIDENCE / "edf_parse_summary.csv")
    people, flow = case_flow(features, parse)
    people.to_parquet(DERIVED / "people.parquet", index=False)
    flow.to_csv(EVIDENCE / "case_flow.csv", index=False)
    return people, flow
