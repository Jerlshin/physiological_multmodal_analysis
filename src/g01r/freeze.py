"""Analysis freeze manifest and the outcome-access authorization gate (protocol §16).

``analysis_freeze/freeze_manifest.json`` binds, by SHA-256, the protocol, frozen configuration,
implementation specification, every production source file (including the analysis registry),
the population ledger, both feature tables and their signal caches, the derived synchrony caches
(append-only), the feature QC report, the production re-validation summaries, the data release
identity and the environment.

Real outcomes become readable only when ``analysis_freeze/AUTHORIZATION.json`` exists, names the
deposited preregistration, references the manifest's SHA-256, and the manifest still verifies
against the working tree. Writing that record (``g01r authorize``) is a USER action taken after
the preregistration deposit; it is never performed automatically.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import DERIVED, FREEZE_DIR, IMPL_EVIDENCE, ROOT, ProtocolConfig, sha256_file
from .provenance import code_hash, data_identity, environment, git_state

MANIFEST = FREEZE_DIR / "freeze_manifest.json"
CACHE_INDEX = FREEZE_DIR / "derived_cache_index.json"
AUTHORIZATION = FREEZE_DIR / "AUTHORIZATION.json"
ACCESS_LOG = FREEZE_DIR / "outcome_access_log.jsonl"

FROZEN_DOCUMENTS = [
    "docs/research/experimental_design/protocol.md",
    "docs/research/experimental_design/estimand_and_hypotheses.md",
    "docs/research/experimental_design/evaluation_contract.md",
    "docs/research/experimental_design/evidence/analysis_set_manifest.csv",
    "docs/research/baseline_implementation/implementation_spec.md",
    "configs/g01r_protocol_v1.toml",
    "requirements-baseline.lock",
]
# Outcome-free caches derived from the bound signal caches by the frozen code. The confirmatory run
# reuses their entries and adds new ones, so they are bound append-only: every entry present at the
# freeze must keep its SHA-256; entries written later are allowed.
DERIVED_CACHES = {"syn_cache": "*.parquet", "corrca_stats": "*.npy"}
EVIDENCE_FILES = [
    "population/analysis_sets.csv",
    "population/case_flow.csv",
    "population/population_summary.json",
    "feature_qc/feature_qc.json",
    "validation/v1_summary.csv",
    "validation/v2_summary.csv",
    "validation/validation_verdict.json",
    "validation/cache_consistency.json",
]


def _tree_hash(root: Path) -> dict:
    h = hashlib.sha256()
    n = 0
    total = 0
    if root.exists():
        for p in sorted(root.rglob("*.npy")):
            rel = str(p.relative_to(root))
            h.update(rel.encode())
            h.update(sha256_file(p).encode())
            n += 1
            total += p.stat().st_size
    return dict(sha256=h.hexdigest(), files=n, bytes=total)


def _derived_cache_index() -> dict:
    index = {}
    for name, pattern in DERIVED_CACHES.items():
        root = DERIVED / name
        index[name] = {str(p.relative_to(root)): sha256_file(p) for p in sorted(root.rglob(pattern))
                       if ".tmp" not in p.name} if root.exists() else {}
    return index


def write_derived_cache_index() -> dict:
    index = _derived_cache_index()
    CACHE_INDEX.write_text(json.dumps(index, indent=0, sort_keys=True) + "\n")
    return dict(index=CACHE_INDEX.name, index_sha256=sha256_file(CACHE_INDEX),
                entries={k: len(v) for k, v in index.items()})


def verify_derived_caches(frozen: dict) -> list:
    """Append-only check: every cache entry indexed at the freeze is present and unchanged."""
    record = frozen.get("derived_caches")
    if record is None:
        return ["derived_caches not bound"]
    if not CACHE_INDEX.exists() or sha256_file(CACHE_INDEX) != record["index_sha256"]:
        return ["derived cache index changed or absent"]
    problems = []
    for name, entries in json.loads(CACHE_INDEX.read_text()).items():
        root = DERIVED / name
        bad = [rel for rel, digest in entries.items() if not (root / rel).exists() or sha256_file(root / rel) != digest]
        if bad:
            problems.append(f"{name}: {len(bad)} frozen entries changed or deleted (e.g. {bad[:3]})")
    return problems


def build_manifest(cfg: ProtocolConfig, include_caches: bool = True) -> dict:
    if not cfg.is_frozen:
        raise ValueError("The freeze manifest is built only from the unmodified frozen configuration")
    from .registry import REGISTRY

    m = dict(
        schema=2,                # 2: adds requirements-baseline.lock and the append-only derived caches
        created_utc=datetime.now(timezone.utc).isoformat(),
        question=cfg.raw["meta"]["question"],
        protocol_commit=cfg.raw["meta"]["protocol_commit"],
        documents={d: sha256_file(ROOT / d) for d in FROZEN_DOCUMENTS},
        code=code_hash(),
        registry=[s.id for s in REGISTRY],
        evidence={e: sha256_file(IMPL_EVIDENCE / e) for e in EVIDENCE_FILES if (IMPL_EVIDENCE / e).exists()},
        features={route: sha256_file(DERIVED / "features" / route / "exposure_features.parquet")
                  for route in ("processed", "raw") if (DERIVED / "features" / route / "exposure_features.parquet").exists()},
        data=data_identity(),
        environment=environment(),
        git_at_freeze=git_state(),
        seeds=dict(base_seed=cfg.resampling["base_seed"]),
    )
    if include_caches:
        m["signal_caches"] = {route: _tree_hash(DERIVED / "cache" / route) for route in ("processed", "raw")}
    missing = [e for e in EVIDENCE_FILES if not (IMPL_EVIDENCE / e).exists()]
    if missing:
        raise FileNotFoundError(f"Freeze evidence missing: {missing}")
    return m


def write_manifest(cfg: ProtocolConfig) -> Path:
    FREEZE_DIR.mkdir(parents=True, exist_ok=True)
    m = build_manifest(cfg)
    m["derived_caches"] = write_derived_cache_index()
    MANIFEST.write_text(json.dumps(m, indent=2) + "\n")
    return MANIFEST


def verify_manifest(cfg: ProtocolConfig, include_caches: bool = True) -> list:
    """Recompute every bound hash; returns a list of mismatches (empty = verified)."""
    if not MANIFEST.exists():
        return ["freeze manifest absent"]
    frozen = json.loads(MANIFEST.read_text())
    now = build_manifest(cfg, include_caches=include_caches)
    problems = []
    for section in ("documents", "evidence", "features", "registry", "protocol_commit"):
        if frozen.get(section) != now.get(section):
            problems.append(section)
    if frozen["code"]["sha256"] != now["code"]["sha256"]:
        changed = sorted(k for k in set(frozen["code"]["files"]) | set(now["code"]["files"])
                         if frozen["code"]["files"].get(k) != now["code"]["files"].get(k))
        problems.append(f"code changed: {changed}")
    if include_caches and frozen.get("signal_caches") != now.get("signal_caches"):
        problems.append("signal_caches")
    if frozen["data"]["archives"] != now["data"]["archives"]:
        problems.append("data archives")
    if include_caches:
        problems.extend(verify_derived_caches(frozen))
    return problems


def environment_differences() -> list:
    """Differences between the frozen and the current software environment (reported, not enforced)."""
    if not MANIFEST.exists():
        return []
    frozen, now = json.loads(MANIFEST.read_text()).get("environment", {}), environment()
    diffs = [f"python {frozen.get('python')} -> {now['python']}"] if frozen.get("python") != now["python"] else []
    for pkg, version in frozen.get("packages", {}).items():
        if now["packages"].get(pkg) != version:
            diffs.append(f"{pkg} {version} -> {now['packages'].get(pkg)}")
    return diffs


def bound_repository_paths() -> list:
    """Repository files bound by the freeze, which the freeze commit must contain unmodified."""
    rel = lambda p: str(p.relative_to(ROOT))
    return sorted(set(FROZEN_DOCUMENTS) | set(code_hash()["files"]) | {rel(IMPL_EVIDENCE / e) for e in EVIDENCE_FILES}
                  | {rel(MANIFEST), rel(CACHE_INDEX)})


def uncommitted_bound_files() -> list:
    """Bound files that are untracked or differ from git HEAD (empty = the freeze is committed)."""
    paths = bound_repository_paths()
    try:
        tracked = set(subprocess.run(["git", "ls-files", "--", *paths], cwd=ROOT, capture_output=True, text=True,
                                     check=True).stdout.splitlines())
        changed = subprocess.run(["git", "status", "--porcelain", "--", *paths], cwd=ROOT, capture_output=True,
                                 text=True, check=True).stdout.splitlines()
    except Exception as exc:                                   # no git: the freeze cannot be shown committed
        return [f"git unavailable: {exc}"]
    return sorted({p for p in paths if p not in tracked} | {line[3:] for line in changed if line.strip()})


@dataclass
class Authorization:
    record: dict
    record_sha256: str
    verified: bool

    def log_access(self, set_name: str, kind: str, n: int):
        with ACCESS_LOG.open("a") as f:
            f.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(), set=set_name, outcome=kind, cells=n,
                                    authorization_sha256=self.record_sha256)) + "\n")


REQUIRED_FIELDS = ("authorized_by", "authorized_utc", "preregistration", "freeze_manifest_sha256", "statement",
                   "git_commit")


def load_authorization(cfg: ProtocolConfig) -> Authorization:
    from .outcomes import OutcomeAccessDenied

    if not AUTHORIZATION.exists():
        raise OutcomeAccessDenied("No analysis-freeze authorization record (analysis_freeze/AUTHORIZATION.json)")
    record = json.loads(AUTHORIZATION.read_text())
    missing = [f for f in REQUIRED_FIELDS if not record.get(f)]
    if missing:
        raise OutcomeAccessDenied(f"Authorization record incomplete: {missing}")
    if record["freeze_manifest_sha256"] != sha256_file(MANIFEST):
        raise OutcomeAccessDenied("Authorization refers to a different freeze manifest")
    problems = verify_manifest(cfg)
    if problems:
        raise OutcomeAccessDenied(f"Freeze manifest no longer verifies: {problems}")
    return Authorization(record, sha256_file(AUTHORIZATION), True)


def authorize(cfg: ProtocolConfig, preregistration: str, authorized_by: str, statement: str) -> Path:
    """USER ACTION after depositing the preregistration: writes the authorization record.

    Refuses unless the manifest verifies and every bound repository file is committed unmodified,
    so the recorded ``git_commit`` contains exactly the frozen state."""
    problems = verify_manifest(cfg)
    if problems:
        raise RuntimeError(f"Refusing to authorize: freeze manifest does not verify: {problems}")
    if AUTHORIZATION.exists():
        raise RuntimeError("An authorization record already exists; it is append-only history")
    uncommitted = uncommitted_bound_files()
    if uncommitted:
        raise RuntimeError(f"Refusing to authorize: commit the freeze first; uncommitted bound files: {uncommitted[:10]}")
    record = dict(authorized_by=authorized_by, authorized_utc=datetime.now(timezone.utc).isoformat(),
                  preregistration=preregistration, freeze_manifest_sha256=sha256_file(MANIFEST), statement=statement,
                  protocol_commit=cfg.raw["meta"]["protocol_commit"], git_commit=git_state()["commit"])
    AUTHORIZATION.write_text(json.dumps(record, indent=2) + "\n")
    return AUTHORIZATION
