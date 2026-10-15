"""Stage-1 locations. Kept apart from ``cairn.paths``, whose bytes are fixed by the Stage-0 hash list
(``stage0/SHA256SUMS``), so Stage-0 provenance stays verifiable."""
from __future__ import annotations

from .paths import AUDIT_EVIDENCE, DERIVED, DOCS, STAGE0_EVIDENCE

STAGE1 = DOCS / "stage1"
STAGE1_EVIDENCE = STAGE1 / "evidence"
PROVISIONAL_ANCHORS = STAGE0_EVIDENCE / "anchors_provisional.csv"   # machine anchors: Stage-1 (outcome-free) use only
RELEASE_METADATA = AUDIT_EVIDENCE / "release_metadata"
STAGE1_CACHE = DERIVED / "stage1"               # fold-safe per-second channels, keyed by split identity
