"""Recheck formulation denominators from existing audit artifacts; no model fitting.

Run from repository root:
    .venv/bin/python docs/research/research_gap/evidence/review_snapshot.py

Writes only phase-level aggregate snapshots and a source fingerprint manifest.
Never changes audit tables, participant eligibility, masks, or source archives.
"""
from pathlib import Path
import hashlib
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
AUDIT = ROOT / "docs/research/dataset_exploration/evidence"
outcomes = pd.read_parquet(AUDIT / "gate_closure_behavioral_eligibility.parquet")
tensor = pd.read_parquet(AUDIT / "exposure_tensor.parquet")
items = pd.read_parquet(AUDIT / "quiz_items.parquet")
memory = outcomes[(outcomes.question_type == "memory") & outcomes.gate_behavior_eligible]
direct = tensor[tensor.valid_quiz_outcome & (tensor.experiment != 2)]

def counts(frame):
    return {
        "qualified_people": int(frame.qualified_participant_id.nunique()),
        "observations": int(len(frame)),
        "canonical_videos": int(frame.canonical_video_id.nunique()),
    }

def groups(frame):
    return {str(e): counts(f) for e, f in frame.groupby("experiment")}

modalities = {}
for label, cols in {
    "eeg_ecg_eye": ["eeg_basic_qc", "ecg_basic_qc", "eye_basic_qc"],
    "ecg_eye": ["ecg_basic_qc", "eye_basic_qc"],
    "eeg": ["eeg_basic_qc"],
    "eye": ["eye_basic_qc"],
}.items():
    subset = direct[direct[cols].fillna(False).all(axis=1)]
    modalities[label] = {
        "overall": counts(subset),
        "by_experiment": groups(subset),
        "experiments_3_4": counts(subset[subset.experiment.isin([3, 4])]),
        "experiments_4_5": counts(subset[subset.experiment.isin([4, 5])]),
    }

snapshot = {
    "phase_date": "2026-10-03",
    "scope": "read-only aggregate verification, not a new signal or outcome audit",
    "person_unit": "experiment-qualified records; cross-experiment human uniqueness unresolved",
    "outcome_eligible_all": counts(memory),
    "outcome_eligible_by_experiment": groups(memory),
    "outcome_eligible_experiments_3_5": counts(memory[memory.experiment.isin([3, 4, 5])]),
    "outcome_eligible_experiments_3_4": counts(memory[memory.experiment.isin([3, 4])]),
    "outcome_eligible_experiments_4_5": counts(memory[memory.experiment.isin([4, 5])]),
    "direct_provisional_qc": modalities,
    "full_partial_credit_with_wrong_choices_release_item_rows": int(
        ((items.recomputed_score == 1) & (items.selected_wrong_option_count > 0)).sum()
    ),
    "model_fitted": False,
    "waveform_audit_repeated": False,
}
assert snapshot["outcome_eligible_all"] == {
    "qualified_people": 147, "observations": 581, "canonical_videos": 11
}
assert modalities["eeg_ecg_eye"]["overall"] == {
    "qualified_people": 94, "observations": 324, "canonical_videos": 8
}
assert modalities["eeg_ecg_eye"]["experiments_3_4"] == {
    "qualified_people": 57, "observations": 216, "canonical_videos": 8
}
assert modalities["ecg_eye"]["overall"]["observations"] == 327
assert modalities["eeg"]["overall"]["observations"] == 429

# Fingerprint narrative record and decisive aggregate inputs; do not hash 27GB again.
paths = sorted(
    p for p in (ROOT / "docs/research").rglob("*.md")
    if "research_gap" not in p.parts
)
paths += [
    AUDIT / name for name in [
        "gate_closure_behavioral_eligibility.parquet",
        "exposure_tensor.parquet",
        "quiz_items.parquet",
        "participant_traits.parquet",
        "gate_closure_feasibility_counts.csv",
        "gate_closure_validation.json",
        "gate_closure_historical_quiz_comparison.json",
        "gate_closure_sources.json",
        "research_feasibility.csv",
        "exploratory_group_structure.csv",
        "exploratory_quality_correlations.csv",
        "independence_graph.json",
        "leakage_risk_register.json",
    ]
]
manifest = []
for path in paths:
    blob = path.read_bytes()
    manifest.append({
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(blob),
        "sha256": hashlib.sha256(blob).hexdigest(),
        "role": "narrative research record" if path.suffix == ".md" else "decisive aggregate evidence",
    })
(OUT / "repository_snapshot.json").write_text(json.dumps(snapshot, indent=2) + "\n")
(OUT / "repository_source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({
    "manifest_files": len(manifest),
    "eligible_outcomes": snapshot["outcome_eligible_all"],
    "tri_modal": modalities["eeg_ecg_eye"],
    "full_partial_credit_with_wrong_choices": snapshot["full_partial_credit_with_wrong_choices_release_item_rows"],
}, indent=2))

