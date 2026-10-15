"""The only module that reads the John posttest.

:func:`load_posttest` refuses unless the feature freeze verifies (re-checked at every access)
and appends every access to ``evidence/outcome_access_log.jsonl`` with the freeze record's
SHA-256. Outcome (plan): posttest proportion correct over the 13 ``knowPost_*`` items, using the
scoring supplied in the workbook; the item sum is cross-checked against ``knowPost_sum``.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from . import freeze
from .paths import ACCESS_LOG, WORKBOOK

POSTTEST_ITEMS = ["knowPost_1", "knowPost_2", "knowPost_3", "knowPost_4", "knowPost_6", "knowPost_7", "knowPost_8",
                  "knowPost_9", "knowPost_10", "knowPost_11", "knowPost_12", "knowPost_13", "knowPost_14"]


class OutcomeAccessDenied(PermissionError):
    pass


def load_posttest(participants, purpose: str) -> tuple[np.ndarray, dict]:
    problems = freeze.verify()
    if problems:
        raise OutcomeAccessDenied("John posttest locked: " + "; ".join(problems))
    q = pd.read_excel(WORKBOOK, sheet_name="Quest", usecols=["participants"] + POSTTEST_ITEMS + ["knowPost_sum"])
    q = q.set_index("participants")
    items = q[POSTTEST_ITEMS].astype(float)
    values = sorted(set(np.unique(items.to_numpy()).tolist()))
    semantics = dict(items=len(POSTTEST_ITEMS), item_values=values, binary_items=set(values) <= {0.0, 1.0},
                     sum_matches_knowPost_sum=bool((items.sum(axis=1) == q.knowPost_sum).all()))
    y = items.mean(axis=1).reindex(list(participants)).to_numpy(float)
    if not np.isfinite(y).all():
        raise ValueError("A participant without a complete posttest")
    entry = dict(utc=datetime.now(timezone.utc).isoformat(), freeze_record_sha256=freeze.record_sha256(),
                 purpose=purpose, n=int(len(y)), semantics=semantics)
    with ACCESS_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return y, semantics
