"""Every released exposure (all experiments and sessions), read through outcome-free whitelists.

The exposure tensor also holds availability flags for quiz outcomes; they are never read here.
"""
from __future__ import annotations

import pandas as pd

from .paths import AUDIT_EVIDENCE

COLUMNS = (
    ["experiment", "participant_id", "qualified_participant_id", "session", "local_stimulus_id",
     "canonical_video_id", "exposure_number", "condition"]
    + [f"{m}_{k}" for m in ("eeg", "ecg", "gaze", "pupil", "head") for k in ("present", "basic_qc", "processed_present")]
    + ["gaze_qc_reasons"]
)

# Which exposure of each cohort is followed by that video's quiz (G01-R protocol §5; plan §15.2).
TESTED = {
    1: dict(session=1, condition="intentional_attend"),
    2: dict(session=1, condition="incidental_attend"),       # E2 behaviour quarantined (D038): label-free only
    3: dict(session=1, condition="intentional_attend"),
    4: dict(session=2, condition="attend_tested_content"),
    5: dict(session=2, condition="incentive_preview_repeat"),
}
DISTRACTED = {"arithmetic_repeat"}


def uid(r) -> str:
    return f"e{int(r.experiment)}_{r.participant_id}_s{int(r.session)}_t{int(r.local_stimulus_id)}"


def all_exposures() -> pd.DataFrame:
    t = pd.read_parquet(AUDIT_EVIDENCE / "exposure_tensor.parquet", columns=COLUMNS)
    t = t.copy()
    t["uid"] = [uid(r) for r in t.itertuples(index=False)]
    tested = pd.Series(False, index=t.index)
    for exp, spec in TESTED.items():
        tested |= (t.experiment == exp) & (t.session == spec["session"]) & (t.condition == spec["condition"])
    t["tested_exposure"] = tested
    t["distracted"] = t.condition.isin(DISTRACTED)
    return t.sort_values(["experiment", "participant_id", "session", "local_stimulus_id"]).reset_index(drop=True)
