"""Eligibility, case flow and frozen analysis sets (protocol §3; M03).

This is an independent production re-implementation of the design-phase ledger
(docs/research/experimental_design/evidence/design_ledger.py). It reads audited
bookkeeping tables through explicit column whitelists, so outcome values are
never loaded, and it must reproduce the frozen manifest exactly
(:func:`verify_against_frozen_manifest`).
"""
from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import AUDIT_EVIDENCE, DESIGN_EVIDENCE, ProtocolConfig

KEYS = ["experiment", "participant_id", "canonical_video_id"]
CELL_KEYS = ["experiment", "participant_id", "session", "local_stimulus_id"]

# Tested exposure per cohort (protocol §5 chronology; analysis_population.md).
TESTED = {
    1: dict(session=1, condition=None),
    3: dict(session=1, condition="intentional_attend"),
    4: dict(session=2, condition="attend_tested_content"),
    5: dict(session=2, condition="incentive_preview_repeat"),
}
CORE = ("eeg", "ecg", "gaze")
FOUR = ("eeg", "ecg", "gaze", "pupil")

# Column whitelists: nothing outcome-valued is ever read by this module.
TENSOR_COLUMNS = (
    ["experiment", "participant_id", "qualified_participant_id", "session", "local_stimulus_id",
     "canonical_video_id", "exposure_number", "condition"]
    + [f"{m}_{k}" for m in ("eeg", "ecg", "gaze", "pupil") for k in ("present", "basic_qc", "processed_present", "raw_present")]
    + ["gaze_qc_reasons"]
)
ELIGIBILITY_COLUMNS = KEYS + ["question_type", "gate_behavior_eligible", "gate_behavior_reason"]
FILES_COLUMNS = CELL_KEYS + ["modality", "status", "correction_fraction"]

BASE_SETS = ["CAS_E34", "PAS_E34_core", "PAS_E34_four", "E5_core", "E5_four", "E5_CAS", "E1_gaze", "E1_gaze_pupil"]
EYE_SETS = ["PAS_E34_core_eye30", "PAS_E34_core_eye70"]
DERIVED_SETS = ["PAS_E34_core_alpha30", "E3_core", "E4_core"]


def _flag(cells: pd.DataFrame, mods, kind: str) -> np.ndarray:
    return np.all([cells[f"{m}_{kind}"].fillna(False).astype(bool).to_numpy() for m in mods], axis=0)


def tested_cells() -> pd.DataFrame:
    tensor = pd.read_parquet(AUDIT_EVIDENCE / "exposure_tensor.parquet", columns=TENSOR_COLUMNS)
    elig = pd.read_parquet(AUDIT_EVIDENCE / "gate_closure_behavioral_eligibility.parquet", columns=ELIGIBILITY_COLUMNS)
    elig = elig[elig.question_type == "memory"][KEYS + ["gate_behavior_eligible", "gate_behavior_reason"]]
    frames = []
    for exp, spec in TESTED.items():
        x = tensor[(tensor.experiment == exp) & (tensor.session == spec["session"])]
        if spec["condition"]:
            x = x[x.condition == spec["condition"]]
        frames.append(x)
    cells = pd.concat(frames, ignore_index=True).merge(elig, on=KEYS, how="left", validate="one_to_one")
    cells["eligible_outcome"] = cells.gate_behavior_eligible.fillna(False).astype(bool)
    return cells


def gaze_correction_fraction() -> pd.DataFrame:
    frames = []
    for exp in TESTED:
        f = pd.read_parquet(AUDIT_EVIDENCE / f"files_exp{exp}.parquet", columns=FILES_COLUMNS)
        f = f[(f.modality == "gaze") & (f.status == "author_processed")]
        frames.append(f[CELL_KEYS + ["correction_fraction"]].rename(columns={"correction_fraction": "gaze_correction_fraction"}))
    return pd.concat(frames, ignore_index=True)


def build_sets(cfg: ProtocolConfig) -> pd.DataFrame:
    """Cell table with every frozen analysis-set membership flag."""
    cells = tested_cells()
    core_qc = _flag(cells, CORE, "basic_qc")
    four_qc = _flag(cells, FOUR, "basic_qc")
    gaze_qc = _flag(cells, ["gaze"], "basic_qc")
    pupil_qc = _flag(cells, ["pupil"], "basic_qc")
    e34 = cells.experiment.isin([3, 4]).to_numpy()
    ok = cells.eligible_outcome.to_numpy()
    e5 = (cells.experiment == 5).to_numpy()
    e1 = (cells.experiment == 1).to_numpy()
    sets = {
        "CAS_E34": e34 & ok,
        "PAS_E34_core": e34 & ok & core_qc,
        "PAS_E34_four": e34 & ok & four_qc,
        "E5_core": e5 & ok & core_qc,
        "E5_four": e5 & ok & four_qc,
        "E5_CAS": e5 & ok,
        "E1_gaze": e1 & ok & gaze_qc,
        "E1_gaze_pupil": e1 & ok & gaze_qc & pupil_qc,
    }
    cells = cells.merge(gaze_correction_fraction(), on=CELL_KEYS, how="left", validate="one_to_one")
    eeg_ecg = _flag(cells, ["eeg", "ecg"], "basic_qc")
    for thr in cfg.population["eye_qc_sensitivity_thresholds"]:
        gaze_alt = (cells.gaze_qc_reasons.isin(["[]", '["correction_gt_50pct"]'])
                    & (cells.gaze_correction_fraction <= thr)).to_numpy()
        sets[f"PAS_E34_core_eye{int(round(thr * 100)):02d}"] = e34 & ok & eeg_ecg & gaze_alt
    low = cells.canonical_video_id.isin(cfg.population["low_reliability_content"]).to_numpy()
    sets["PAS_E34_core_alpha30"] = sets["PAS_E34_core"] & ~low
    sets["E3_core"] = sets["PAS_E34_core"] & (cells.experiment == 3).to_numpy()
    sets["E4_core"] = sets["PAS_E34_core"] & (cells.experiment == 4).to_numpy()
    for name, mask in sets.items():
        cells[name] = mask
    keep = cells[list(sets)].any(axis=1)
    return cells[keep].sort_values(["experiment", "participant_id", "local_stimulus_id"]).reset_index(drop=True)


def count(frame: pd.DataFrame) -> dict:
    return dict(people=int(frame.qualified_participant_id.nunique()), cells=int(len(frame)),
                videos=int(frame.canonical_video_id.nunique()))


def verify_against_frozen_manifest(cells: pd.DataFrame, cfg: ProtocolConfig) -> dict:
    """Assert identical keys and set flags versus the design-phase frozen manifest."""
    frozen = pd.read_csv(DESIGN_EVIDENCE / "analysis_set_manifest.csv")
    key = ["experiment", "participant_id", "canonical_video_id", "session", "local_stimulus_id"]
    report = {}
    for name in BASE_SETS + EYE_SETS:
        a = set(map(tuple, cells.loc[cells[name], key].to_numpy().tolist()))
        b = set(map(tuple, frozen.loc[frozen[name], key].to_numpy().tolist()))
        if a != b:
            raise AssertionError(f"{name}: production set differs from frozen manifest "
                                 f"(+{len(a - b)} / -{len(b - a)} cells)")
        got = count(cells[cells[name]])
        expected = dict(zip(["people", "cells", "videos"], cfg.population["expected_counts"][name]))
        if got != expected:
            raise AssertionError(f"{name}: counts {got} != frozen {expected}")
        report[name] = got
    return report


def case_flow(cells_all: pd.DataFrame) -> pd.DataFrame:
    """Stage-wise case flow per cohort (reproduces case_flow.csv of the design phase)."""
    rows = []
    for exp in [3, 4, 5, 1]:
        x = cells_all[cells_all.experiment == exp]
        stages = [("design tested cells", np.ones(len(x), bool)), ("eligible outcome", x.eligible_outcome.to_numpy())]
        if exp != 1:
            m = x.eligible_outcome.to_numpy()
            for mod in CORE:
                m = m & x[f"{mod}_basic_qc"].fillna(False).astype(bool).to_numpy()
                stages.append((f"+ {mod} QC (cumulative)", m.copy()))
            stages.append(("+ pupil QC (cumulative, four-sensor)", m & x.pupil_basic_qc.fillna(False).astype(bool).to_numpy()))
        else:
            m = x.eligible_outcome.to_numpy() & x.gaze_basic_qc.fillna(False).astype(bool).to_numpy()
            stages.append(("+ gaze QC", m))
            stages.append(("+ pupil QC", m & x.pupil_basic_qc.fillna(False).astype(bool).to_numpy()))
        for label, mask in stages:
            rows.append(dict(experiment=exp, stage=label, **count(x[mask])))
    return pd.DataFrame(rows)


@dataclass
class AnalysisSet:
    """Cells of one analysis set with integer indices used by the modelling layer."""

    name: str
    cells: pd.DataFrame

    def __post_init__(self):
        c = self.cells.reset_index(drop=True).copy()
        c["person"] = pd.factorize(c.qualified_participant_id, sort=True)[0]
        c["video"] = pd.factorize(c.canonical_video_id, sort=True)[0]
        c["ev_key"] = c.experiment.astype(str) + ":" + c.canonical_video_id
        c["ev"] = pd.factorize(c.ev_key, sort=True)[0]
        self.cells = c

    @property
    def n(self) -> int:
        return len(self.cells)

    @property
    def person(self) -> np.ndarray:
        return self.cells.person.to_numpy()

    @property
    def ev(self) -> np.ndarray:
        return self.cells.ev.to_numpy()

    @property
    def video(self) -> np.ndarray:
        return self.cells.video.to_numpy()

    @property
    def experiment(self) -> np.ndarray:
        return self.cells.experiment.to_numpy()

    @property
    def n_person(self) -> int:
        return int(self.person.max() + 1)

    @property
    def n_ev(self) -> int:
        return int(self.ev.max() + 1)

    @property
    def n_video(self) -> int:
        return int(self.video.max() + 1)

    @property
    def exp_of_person(self) -> np.ndarray:
        return self.cells.groupby("person").experiment.first().sort_index().to_numpy()

    @property
    def ev_experiment(self) -> np.ndarray:
        return self.cells.groupby("ev").experiment.first().sort_index().to_numpy()

    @property
    def ev_video(self) -> np.ndarray:
        return self.cells.groupby("ev").video.first().sort_index().to_numpy()

    def patterns(self) -> dict:
        """Person -> sorted tuple of tested experiment x video units (for person-block permutation)."""
        return {p: tuple(sorted(g.ev.tolist())) for p, g in self.cells.groupby("person")}

    def identity(self) -> str:
        """Content hash of the set membership (keys only)."""
        import hashlib

        payload = self.cells[["experiment", "participant_id", "session", "local_stimulus_id", "canonical_video_id"]]
        return hashlib.sha256(payload.to_csv(index=False).encode()).hexdigest()

    def subset(self, mask: np.ndarray, name: str) -> "AnalysisSet":
        return AnalysisSet(name, self.cells.loc[np.asarray(mask, bool), self.cells.columns.difference(
            ["person", "video", "ev", "ev_key"])].reset_index(drop=True))


class Population:
    def __init__(self, cfg: ProtocolConfig):
        self.cfg = cfg
        self.cells = build_sets(cfg)

    def analysis_set(self, name: str) -> AnalysisSet:
        if name not in self.cells.columns:
            raise KeyError(f"Unknown analysis set {name}")
        cols = ["experiment", "participant_id", "qualified_participant_id", "session", "local_stimulus_id",
                "canonical_video_id", "condition", "exposure_number"]
        return AnalysisSet(name, self.cells.loc[self.cells[name], cols].reset_index(drop=True))

    def summary(self) -> dict:
        names = BASE_SETS + EYE_SETS + DERIVED_SETS
        out = {n: count(self.cells[self.cells[n]]) for n in names}
        out["by_experiment"] = {n: {str(e): count(f) for e, f in self.cells[self.cells[n]].groupby("experiment")} for n in names}
        return out

    def write_ledger(self, out_dir) -> dict:
        out_dir.mkdir(parents=True, exist_ok=True)
        verified = verify_against_frozen_manifest(self.cells, self.cfg)
        flow = case_flow(tested_cells())
        flow.to_csv(out_dir / "case_flow.csv", index=False)
        names = BASE_SETS + EYE_SETS + DERIVED_SETS
        manifest = self.cells[["experiment", "participant_id", "qualified_participant_id", "canonical_video_id", "session",
                               "local_stimulus_id", "condition", "exposure_number"] + names]
        manifest.to_csv(out_dir / "analysis_sets.csv", index=False)
        summary = self.summary()
        summary["verified_against_frozen_manifest"] = verified
        summary["outcome_values_read"] = False
        (out_dir / "population_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        return summary
