"""Repository paths and fixed constants for the CAIRN phase."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT_EVIDENCE = ROOT / "docs/research/dataset_exploration/evidence"
ITEM_BANK = AUDIT_EVIDENCE / "gate_closure_Education_questions.json"

DOCS = ROOT / "docs/research/novel_method"
STAGE0 = DOCS / "stage0"
STAGE0_EVIDENCE = STAGE0 / "evidence"

STIMULI = ROOT / "data/stimuli"                 # git-ignored: videos and captions, never redistributed
YOUTUBE = STIMULI / "youtube"
DERIVED = ROOT / "data/derived/cairn"           # git-ignored: per-exposure series, caches
SERIES = DERIVED / "series10"                   # 10 Hz per-exposure series (outcome-free)

FS = 128                                        # released signal rate (Hz)
BIN_HZ = 10                                     # series resolution used for timeline and channels
SCREEN_W, SCREEN_H, SCREEN_DIAG = 1920, 1080, 2203.0

# canonical video id -> short name used in the item bank and the documentation
VIDEOS = {
    "VVAKFJ8VVp4": "Stars",
    "oCEKMEeZXug": "Lightbulbs",
    "zQGOcOUBi6s": "Immune",
    "21eFwbb48sE": "Internet",
    "3IaYhG11ckA": "Birth rate",
    "e0NT9i4Qnak": "Mosquitoes",
    "mnYSMhR3jCI": "Related",
    "30o4omX5qfo": "Work-energy",
    "rkntp3_cZl4": "Capacitors",
    "bYgV9nvgJ3E": "Planets",
    "lkRZKqDdwzU": "Enzymes",
}
# public sources per stimulus; the item bank lists a second URL for Enzymes (Stage-0a audit)
SOURCES = {v: [v] for v in VIDEOS}
SOURCES["lkRZKqDdwzU"] = ["lkRZKqDdwzU", "AAZ03aScPr8"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()
