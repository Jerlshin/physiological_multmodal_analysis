"""Experiment manifests and run records (Stage-1 spec §6-§7).

A manifest is written **before** fitting. It binds the code (SHA-256 of every ``src/cairn`` module),
the environment lock, every input file, the analysis set, regime, models, grid, CV and inference
budgets, seeds and the outcome-access mode. The manifest hash identifies the run; the same manifest
must reproduce bit-identical outputs (spec §3 test 10).

Stage-2+ manifests must also carry ``anchor_freeze_sha256``; :func:`verify_inputs` refuses a run whose
anchor table is not the frozen one unless the stage is the outcome-free Stage-1 simulation.
"""
from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from .paths import DERIVED, ITEM_BANK, ROOT, STAGE0_EVIDENCE, sha256_bytes, sha256_file
from .paths_stage1 import PROVISIONAL_ANCHORS

CODE_DIR = Path(__file__).resolve().parent        # the package actually imported (a run snapshot or src/cairn)
ENV_LOCK = ROOT / "requirements-cairn.lock"
STAGES = ("1-simulation", "2-development", "4-locked")


def code_hashes() -> dict:
    return {p.name: sha256_file(p) for p in sorted(CODE_DIR.glob("*.py"))}


def code_sha256() -> str:
    return sha256_bytes(json.dumps(code_hashes(), sort_keys=True).encode())


def default_inputs(anchor_table: Path = PROVISIONAL_ANCHORS) -> dict:
    files = {
        "item_bank": ITEM_BANK,
        "anchor_table": Path(anchor_table),
        "timeline_table": STAGE0_EVIDENCE / "timeline_table.csv",
        "timeline_seconds": STAGE0_EVIDENCE / "timeline_seconds.csv",
        "series10_manifest": DERIVED / "series10_manifest.parquet",
        "exposure_tensor": ROOT / "docs/research/dataset_exploration/evidence/exposure_tensor.parquet",
        "behavioral_eligibility_flags": ROOT / "docs/research/dataset_exploration/evidence/gate_closure_behavioral_eligibility.parquet",
    }
    return {k: dict(path=str(Path(v).relative_to(ROOT)), sha256=sha256_file(v)) for k, v in files.items()}


def build(run_id: str, stage: str, sets: list, regime: str, models: list, grid: dict, cv: dict, inference: dict,
          seeds: dict, outcome_access: str = "none", anchor_table: Path = PROVISIONAL_ANCHORS,
          anchor_freeze_sha256: str | None = None, extra: dict | None = None) -> dict:
    if stage not in STAGES:
        raise ValueError(stage)
    if stage != "1-simulation" and outcome_access == "none":
        raise ValueError("Stage-2+ runs read outcomes only through cairn.gate; declare the gate scope")
    m = dict(run_id=run_id, stage=stage, created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
             code_sha256=code_sha256(), code_files=code_hashes(),
             environment=dict(python=sys.version.split()[0], platform=platform.platform(),
                              environment_lock=sha256_file(ENV_LOCK) if ENV_LOCK.exists() else None,
                              interpreter=sys.executable),
             inputs=default_inputs(anchor_table), anchor_provisional=Path(anchor_table) == PROVISIONAL_ANCHORS,
             anchor_freeze_sha256=anchor_freeze_sha256, sets=sets, regime=regime, models=models, grid=grid, cv=cv,
             inference=inference, seeds=seeds, outcome_access=outcome_access)
    if extra:
        m["extra"] = extra
    return m


def manifest_sha256(m: dict) -> str:
    core = {k: v for k, v in m.items() if k not in ("created_utc",)}
    return sha256_bytes(json.dumps(core, sort_keys=True, default=str).encode())


def write(m: dict, path: Path) -> str:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    h = manifest_sha256(m)
    path.write_text(json.dumps(dict(m, manifest_sha256=h), indent=2, default=str))
    return h


def verify_inputs(m: dict) -> list:
    """Return the inputs whose files changed since the manifest was written (empty = verified)."""
    bad = [k for k, v in m["inputs"].items() if not (ROOT / v["path"]).exists() or sha256_file(ROOT / v["path"]) != v["sha256"]]
    if m["stage"] != "1-simulation":
        if not m.get("anchor_freeze_sha256"):
            bad.append("anchor_freeze_sha256 missing (Stage 2+ needs the frozen human anchor set)")
        if m.get("anchor_provisional"):
            bad.append("provisional machine anchors cannot be used after Stage 1")
    return bad


def verify_code(m: dict) -> list:
    now = code_hashes()
    return sorted(k for k in set(now) | set(m["code_files"]) if now.get(k) != m["code_files"].get(k))
