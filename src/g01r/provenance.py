"""Code, data and environment provenance recorded with every run and in the freeze manifest."""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from importlib import metadata
from pathlib import Path

from .config import AUDIT_EVIDENCE, ROOT, sha256_file

CODE_PATHS = [
    "src/g01r",
    "src/bbbd_audit/io.py",
    "src/bbbd_audit/qc.py",
    "configs/g01r_protocol_v1.toml",
    "docs/research/experimental_design/evidence/precision_simulation.py",
]
PACKAGES = ["numpy", "scipy", "pandas", "pyarrow", "mlflow-skinny", "sqlalchemy"]


def git_state() -> dict:
    def run(*args, strip=True):
        try:
            out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout
            return out.strip() if strip else out
        except Exception:
            return None

    status = run("status", "--porcelain", strip=False) or ""      # keep the leading status column of line 1
    dirty = [line[3:] for line in status.splitlines() if line.strip()]
    return dict(commit=run("rev-parse", "HEAD"), branch=run("rev-parse", "--abbrev-ref", "HEAD"),
                dirty=bool(dirty), dirty_files=dirty[:200])


def code_files() -> list[Path]:
    files = []
    for rel in CODE_PATHS:
        p = ROOT / rel
        if p.is_dir():
            files.extend(sorted(q for q in p.rglob("*.py") if "__pycache__" not in q.parts))
        elif p.exists():
            files.append(p)
    return files


def code_hash() -> dict:
    h = hashlib.sha256()
    per_file = {}
    for p in code_files():
        digest = sha256_file(p)
        rel = str(p.relative_to(ROOT))
        per_file[rel] = digest
        h.update(rel.encode())
        h.update(digest.encode())
    return dict(sha256=h.hexdigest(), files=per_file)


def environment() -> dict:
    versions = {}
    for pkg in PACKAGES:
        try:
            versions[pkg] = metadata.version(pkg)
        except metadata.PackageNotFoundError:
            versions[pkg] = None
    return dict(python=sys.version.split()[0], implementation=platform.python_implementation(),
                platform=platform.platform(), machine=platform.machine(), packages=versions)


def data_identity() -> dict:
    manifest = json.loads((AUDIT_EVIDENCE / "download_manifest.json").read_text())
    archives = {r["filename"]: dict(sha256=r.get("sha256"), md5=r.get("computed_md5"), bytes=r.get("local_bytes"),
                                    status=r.get("status")) for r in manifest}
    return dict(release_record=22968459, version="1.1", archives=archives,
                download_manifest_sha256=sha256_file(AUDIT_EVIDENCE / "download_manifest.json"))


def file_identity(paths) -> dict:
    return {str(Path(p).relative_to(ROOT)) if Path(p).is_absolute() else str(p): sha256_file(p) for p in paths if Path(p).exists()}
