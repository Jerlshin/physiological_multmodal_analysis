"""The only CAIRN module allowed to touch item-level quiz outcomes - and it refuses by default.

Item correctness becomes readable only when **all** of the following hold, re-checked at every
access (research plan §15.3, "outcome-access leakage"):

1. a CAIRN freeze record exists (``analysis_freeze_cairn/FREEZE_RECORD.json``) and every file it
   binds (code, configuration, frozen anchor set, timeline, manifests) still has its recorded hash;
2. an authorization record (``analysis_freeze_cairn/AUTHORIZATION.json``) written by the user
   names the requested cohort scope (``development`` first; ``locked_primary`` / ``locked_secondary``
   / ``reserved_descriptive`` only after the CAIRN preregistration) and binds the freeze hash;
3. the access is appended to ``analysis_freeze_cairn/outcome_access_log.jsonl``.

No path in this module opens an outcome file before checks 1-2 pass. Neither the freeze record
nor the authorization exists at the end of Stage 0, so every call raises.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .paths import AUDIT_EVIDENCE, ROOT, sha256_file

FREEZE_DIR = ROOT / "analysis_freeze_cairn"
FREEZE_RECORD = FREEZE_DIR / "FREEZE_RECORD.json"
AUTHORIZATION = FREEZE_DIR / "AUTHORIZATION.json"
ACCESS_LOG = FREEZE_DIR / "outcome_access_log.jsonl"
ITEM_TABLE = AUDIT_EVIDENCE / "quiz_items.parquet"        # forensic-audit item rows (locked for CAIRN)

# Cohort scopes (plan §15.2). Tested exposure per cohort; videos restrict E1.
SCOPES = {
    "development": [dict(experiment=3), dict(experiment=1, videos=("oCEKMEeZXug", "21eFwbb48sE", "3IaYhG11ckA"))],
    "locked_primary": [dict(experiment=4)],
    "locked_secondary": [dict(experiment=5)],
    "reserved_descriptive": [dict(experiment=1, videos=("VVAKFJ8VVp4", "zQGOcOUBi6s"))],
}


class OutcomeAccessDenied(PermissionError):
    pass


def verify_freeze() -> dict:
    """Return the freeze record if every bound file still matches; raise otherwise."""
    if not FREEZE_RECORD.exists():
        raise OutcomeAccessDenied("No CAIRN freeze record (analysis_freeze_cairn/FREEZE_RECORD.json); "
                                  "Stage 3 (freeze + preregistration) has not happened")
    rec = json.loads(FREEZE_RECORD.read_text())
    bad = [p for p, h in rec.get("bound_files", {}).items() if not (ROOT / p).exists() or sha256_file(ROOT / p) != h]
    if bad:
        raise OutcomeAccessDenied(f"CAIRN freeze does not verify; changed files: {bad[:5]}")
    if not rec.get("anchor_freeze_sha256"):
        raise OutcomeAccessDenied("Freeze record lacks a frozen, G-AN-satisfying anchor set")
    return rec


def load_authorization(scope: str) -> dict:
    if scope not in SCOPES:
        raise ValueError(f"Unknown scope {scope}")
    rec = verify_freeze()
    if not AUTHORIZATION.exists():
        raise OutcomeAccessDenied("No CAIRN authorization record (analysis_freeze_cairn/AUTHORIZATION.json)")
    auth = json.loads(AUTHORIZATION.read_text())
    if auth.get("freeze_record_sha256") != sha256_file(FREEZE_RECORD):
        raise OutcomeAccessDenied("Authorization does not bind the current freeze record")
    if scope not in auth.get("scopes", []):
        raise OutcomeAccessDenied(f"Scope '{scope}' not authorized (authorized: {auth.get('scopes')})")
    if scope != "development" and not auth.get("preregistration_url"):
        raise OutcomeAccessDenied("Locked/reserved scopes need a CAIRN preregistration URL in the authorization")
    return dict(freeze=rec, authorization=auth, authorization_sha256=sha256_file(AUTHORIZATION))


def load_item_outcomes(scope: str, purpose: str):
    """Exact-set item correctness for the tested exposures of ``scope`` (raises unless authorized)."""
    ok = load_authorization(scope)                      # raises before any outcome file is opened
    import pandas as pd

    # schema read (names only) at Stage 0; exact-set correctness = recomputed_exact_correct (quiz_integrity.md)
    cols = ["experiment", "participant_id", "qualified_participant_id", "local_stimulus_id", "canonical_video_id",
            "question_type", "question_no", "duplicate_item_key", "recomputed_exact_correct"]
    t = pd.read_parquet(ITEM_TABLE, columns=cols)
    t = t[~t.duplicate_item_key]                         # E3 sub-01/stim03 duplicate is quarantined (D029)
    keep = pd.Series(False, index=t.index)
    for spec in SCOPES[scope]:
        m = t.experiment == spec["experiment"]
        if "videos" in spec:
            m &= t.canonical_video_id.isin(spec["videos"])
        keep |= m
    t = t[keep & (t.question_type == "memory")]
    FREEZE_DIR.mkdir(exist_ok=True)
    with ACCESS_LOG.open("a") as f:
        f.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(), scope=scope, purpose=purpose, rows=len(t),
                                freeze_record_sha256=sha256_file(FREEZE_RECORD),
                                authorization_sha256=ok["authorization_sha256"])) + "\n")
    return t
