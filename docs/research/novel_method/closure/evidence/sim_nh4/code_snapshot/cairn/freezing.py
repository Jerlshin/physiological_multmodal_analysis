"""CAIRN freeze records (plan §15.3, §23; spec §4; closure C-D11).

``cairn.gate`` (Stage 0, hash-bound) opens item outcomes only when ``analysis_freeze_cairn/FREEZE_RECORD.json``
exists, every file it binds still hashes as recorded, it names a frozen G-AN anchor set (``anchor_freeze_sha256``)
and a user-written ``AUTHORIZATION.json`` binds that record. This module builds the record; it never writes the
authorization (a user act) and never touches outcomes.

A freeze for **development** (Stage 2) is refused unless:

1. the human anchor freeze (``ANCHOR_FREEZE.json`` from :func:`cairn.gan.freeze_human_set`) exists and every file it
   binds verifies, and its companion binds the recording-clock table that will be used;
2. the post-G-AN re-simulation record (closure rule R-J) exists, passed, and was run on that same anchor table and the
   same design configuration;
3. the design configuration names a recorded lock-design decision ID.

A freeze for the **lock** (Stage 4) additionally binds the development selections (kernel, strongest competing
baseline) and needs a preregistration URL in the authorization (enforced by the gate). An existing record is
archived under ``FREEZE_RECORD_<stage>_<utc>.json`` before a new one is written; nothing is overwritten.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from . import gate
from .paths import ITEM_BANK, ROOT, STAGE0_EVIDENCE, sha256_bytes, sha256_file

STAGES = ("development", "lock")
ENV_LOCKS = ("requirements-cairn.lock", "requirements-cairn-ml.lock")
RULE_FILES = ("docs/research/novel_method/stage1/evidence/predeclared_rules.md",
              "docs/research/novel_method/closure/evidence/predeclared_rules.md")


class FreezeRefused(RuntimeError):
    pass


def _rel(p: Path) -> str:
    return str(Path(p).resolve().relative_to(ROOT))


def verify_anchor_freeze(anchor_dir: Path) -> dict:
    """Re-hash every file bound by the anchor freeze and its companion; return the companion."""
    anchor_dir = Path(anchor_dir)
    rec_p, comp_p = anchor_dir / "ANCHOR_FREEZE.json", anchor_dir / "ANCHOR_FREEZE_COMPANION.json"
    for p in (rec_p, comp_p):
        if not p.exists():
            raise FreezeRefused(f"anchor freeze incomplete: {p} missing")
    rec = json.loads(rec_p.read_text())
    if not rec.get("gate", {}).get("passed"):
        raise FreezeRefused("anchor freeze record does not show a passed G-AN")
    for group in ("files", "timeline"):
        for p, h in rec.get(group, {}).items():
            if not Path(p).exists() or sha256_file(Path(p)) != h:
                raise FreezeRefused(f"anchor freeze file changed: {p}")
    comp = json.loads(comp_p.read_text())
    if comp.get("anchor_freeze_sha256") != sha256_file(rec_p):
        raise FreezeRefused("companion does not bind this ANCHOR_FREEZE.json")
    if sha256_file(Path(comp["anchor_table"])) != comp["anchor_table_sha256"]:
        raise FreezeRefused("recording-clock anchor table changed since the anchor freeze")
    return comp


def build_record(stage: str, anchor_dir: Path, rj_record: Path, design_config: Path, extra_files: tuple = (),
                 note: str = "") -> dict:
    if stage not in STAGES:
        raise ValueError(stage)
    comp = verify_anchor_freeze(anchor_dir)
    cfg = json.loads(Path(design_config).read_text())
    if not cfg.get("decision_id"):
        raise FreezeRefused("design configuration names no lock-design decision ID")
    rj = json.loads(Path(rj_record).read_text()) if Path(rj_record).exists() else None
    if not rj or not rj.get("passed"):
        raise FreezeRefused("post-G-AN re-simulation (rule R-J) missing or not passed")
    if rj.get("anchor_table_sha256") != comp["anchor_table_sha256"]:
        raise FreezeRefused("R-J re-simulation was not run on the frozen anchor table")
    if rj.get("design_config_sha256") != sha256_file(design_config):
        raise FreezeRefused("R-J re-simulation was not run with this design configuration")
    if stage == "lock" and not cfg.get("development_selections"):
        raise FreezeRefused("a lock freeze needs the development selections (kernel, strongest baseline)")
    files = [*sorted((ROOT / "src/cairn").glob("*.py")), ITEM_BANK, STAGE0_EVIDENCE / "timeline_table.csv",
             STAGE0_EVIDENCE / "timeline_seconds.csv", Path(anchor_dir) / "ANCHOR_FREEZE.json",
             Path(anchor_dir) / "ANCHOR_FREEZE_COMPANION.json", Path(comp["anchor_table"]), Path(design_config),
             Path(rj_record), *[ROOT / p for p in ENV_LOCKS if (ROOT / p).exists()], *[ROOT / p for p in RULE_FILES],
             *map(Path, extra_files)]
    bound = {_rel(p): sha256_file(p) for p in files}
    rec = dict(stage=stage, created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
               anchor_freeze_sha256=comp["anchor_freeze_sha256"], anchor_table=_rel(Path(comp["anchor_table"])),
               anchor_table_sha256=comp["anchor_table_sha256"], design_config_sha256=sha256_file(design_config),
               decision_id=cfg["decision_id"], bound_files=bound, note=note)
    rec["record_sha256"] = sha256_bytes(json.dumps(rec, sort_keys=True).encode())
    return rec


def write_record(rec: dict, freeze_dir: Path = gate.FREEZE_DIR) -> Path:
    freeze_dir = Path(freeze_dir)
    freeze_dir.mkdir(parents=True, exist_ok=True)
    path = freeze_dir / "FREEZE_RECORD.json"
    if path.exists():
        old = json.loads(path.read_text())
        stamp = old.get("created_utc", "unknown").replace(":", "")
        arch = freeze_dir / f"FREEZE_RECORD_{old.get('stage', 'unknown')}_{stamp}.json"
        if arch.exists():
            raise FreezeRefused(f"archive {arch} exists")
        path.rename(arch)
    path.write_text(json.dumps(rec, indent=2))
    return path


def authorization_template(scope: str, purpose: str, freeze_dir: Path = gate.FREEZE_DIR) -> dict:
    """The JSON the **user** writes to ``analysis_freeze_cairn/AUTHORIZATION.json`` to open one scope (printed,
    never written by code). Locked scopes also need the preregistration URL."""
    rec_p = Path(freeze_dir) / "FREEZE_RECORD.json"
    if scope not in gate.SCOPES:
        raise ValueError(scope)
    return dict(scopes=[scope], purpose=purpose, freeze_record_sha256=sha256_file(rec_p) if rec_p.exists() else "<run after freeze>",
                authorized_by="<user name>", utc="<UTC time of authorization>",
                preregistration_url=None if scope == "development" else "<OSF URL of the CAIRN preregistration>")
