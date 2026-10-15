"""Repository paths and the plan's fixed constants for the John 2025 replication."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "docs/research/experimental_design/external_analysis_plan_john2025.md"
PLAN_COMMIT = "ef1df1b3014ccc85f5ac956bd192b6b0d39c3e34"
OSF_MANIFEST = ROOT / "docs/research/experimental_design/evidence/external/john2025_osf_4rn5q_file_manifest.json"

DATA = ROOT / "data/john2025/osf_4rn5q"
EDF_DIR = DATA / "Mine/Mine_Eye/edf"
WORKBOOK = DATA / "Scripts Analysis/ScriptVariables.xlsx"
DERIVED = ROOT / "data/derived/john2025"
PARSED = DERIVED / "parsed"             # one .npz per EDF (outcome-free)
SERIES = DERIVED / "series"             # 128 Hz video-locked gaze / pupil series per person

DOCS = ROOT / "docs/research/external_john2025"
EVIDENCE = DOCS / "evidence"
FREEZE_RECORD = EVIDENCE / "feature_freeze.json"
ACCESS_LOG = EVIDENCE / "outcome_access_log.jsonl"
CLARIFICATIONS = DOCS / "implementation_clarifications.md"

OSF_NODE = "4rn5q"
VIDEO = "mine"                          # "Programming in Minecraft"
SET_NAME = "JOHN2025_mine"
