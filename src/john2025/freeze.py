"""Outcome-blind feature freeze for the replication (plan: "Freeze the feature table, with its hash
recorded. Only then join the posttest").

The record binds, by SHA-256: the plan (and that it is byte-identical to its time-stamping commit
ef1df1b), the implementation clarifications, this package's code, the frozen ``g01r`` code and
configuration it reuses (which must equal the BBBD freeze), the acquisition manifest, the parse
summary, the feature/person tables, every 128 Hz series file, the synthetic-null validation
summary and the environment. :func:`verify` recomputes all of it; the outcome loader refuses
unless it returns no problem.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata

from g01r.config import CONFIG_PATH, ROOT, sha256_file
from g01r.provenance import code_hash as g01r_code_hash

from .paths import CLARIFICATIONS, DERIVED, EVIDENCE, FREEZE_RECORD, PLAN, PLAN_COMMIT, SERIES

BOUND_EVIDENCE = ["download_manifest.json", "edf_parse_summary.csv", "person_features.csv", "case_flow.csv",
                  "validation/null_calibration_summary.json"]
BOUND_DERIVED = ["person_features.parquet", "people.parquet"]


def _tree(root) -> dict:
    h = hashlib.sha256()
    files = sorted(root.glob("*.npy"))
    for p in files:
        h.update(p.name.encode())
        h.update(sha256_file(p).encode())
    return dict(sha256=h.hexdigest(), files=len(files))


def plan_identity() -> dict:
    rel = str(PLAN.relative_to(ROOT))
    committed = subprocess.run(["git", "show", f"{PLAN_COMMIT}:{rel}"], cwd=ROOT, capture_output=True, check=True).stdout
    current = PLAN.read_bytes()
    return dict(path=rel, commit=PLAN_COMMIT, sha256=hashlib.sha256(current).hexdigest(),
                identical_to_commit=committed == current)


def code_files() -> list:
    return sorted((ROOT / "src/john2025").glob("*.py"))


def environment() -> dict:
    pkgs = {d.metadata["Name"].lower(): d.version for d in metadata.distributions()}
    return dict(python=sys.version.split()[0], packages=dict(sorted(pkgs.items())))


def current_state() -> dict:
    bbbd = json.loads((ROOT / "analysis_freeze/freeze_manifest.json").read_text())
    g = g01r_code_hash()
    return dict(
        plan=plan_identity(),
        clarifications=dict(path=str(CLARIFICATIONS.relative_to(ROOT)), sha256=sha256_file(CLARIFICATIONS)),
        code={str(p.relative_to(ROOT)): sha256_file(p) for p in code_files()},
        g01r=dict(code_sha256=g["sha256"], equals_bbbd_freeze=g["sha256"] == bbbd["code"]["sha256"],
                  config_sha256=sha256_file(CONFIG_PATH)),
        evidence={e: sha256_file(EVIDENCE / e) for e in BOUND_EVIDENCE},
        derived={d: sha256_file(DERIVED / d) for d in BOUND_DERIVED},
        series=_tree(SERIES),
        environment=environment(),
    )


def write_record() -> dict:
    state = current_state()
    if not state["plan"]["identical_to_commit"]:
        raise RuntimeError("The plan differs from its time-stamping commit; record a deviation first")
    if not state["g01r"]["equals_bbbd_freeze"]:
        raise RuntimeError("The reused g01r code differs from the BBBD freeze")
    record = dict(created_utc=datetime.now(timezone.utc).isoformat(), purpose="John 2025 feature freeze before outcome access",
                  **state)
    FREEZE_RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    return record


def verify() -> list:
    """Problems that block outcome access (empty list = verified)."""
    if not FREEZE_RECORD.exists():
        return ["no feature-freeze record"]
    frozen = json.loads(FREEZE_RECORD.read_text())
    now = current_state()
    problems = []
    for key in ("plan", "clarifications", "code", "g01r", "evidence", "derived", "series"):
        if frozen.get(key) != now[key]:
            problems.append(f"{key} changed since the freeze")
    if not now["plan"]["identical_to_commit"]:
        problems.append("plan differs from its time-stamping commit")
    if not now["g01r"]["equals_bbbd_freeze"]:
        problems.append("reused g01r code differs from the BBBD freeze")
    for pkg in ("numpy", "scipy", "pandas", "pyarrow"):
        if frozen["environment"]["packages"].get(pkg) != now["environment"]["packages"].get(pkg):
            problems.append(f"environment: {pkg} version changed")
    return problems


def record_sha256() -> str:
    return sha256_file(FREEZE_RECORD)
