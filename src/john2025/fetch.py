"""Acquisition of the files the plan needs from OSF 4rn5q, verified against OSF's SHA-256.

Only ``/Mine/Mine_Eye/edf`` (118 EDF files, about 1.48 GB) and the small workbook/scripts are
fetched; the EEG and the non-educational "Bang" clip are not. Every file is downloaded to a
temporary name, hashed, compared with the SHA-256 the OSF API reports, and only then renamed.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from .paths import DATA, EVIDENCE, OSF_MANIFEST

SMALL = ("/README.txt", "/Scripts Analysis/ScriptVariables.xlsx", "/Scripts Analysis/codebook.Rmd",
         "/Scripts Analysis/analysis.qmd")


def wanted() -> list:
    rows = json.loads(OSF_MANIFEST.read_text())
    return [r for r in rows if r[0] == "F" and (r[1].startswith("/Mine/Mine_Eye/edf/")
                                                or r[1].startswith("/Scripts PreProcessing/") or r[1] in SMALL)]


def _api(file_id: str, retries: int = 6) -> dict:
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(f"https://api.osf.io/v2/files/{file_id}/", timeout=120) as r:
                a = json.load(r)["data"]["attributes"]
            return dict(name=a["name"], size=a["size"], md5=a["extra"]["hashes"]["md5"],
                        sha256=a["extra"]["hashes"]["sha256"], date_modified=a["date_modified"])
        except urllib.error.HTTPError as exc:      # OSF answers 429 when rate-limited
            if exc.code != 429 or attempt == retries - 1:
                raise
            time.sleep(30 * (attempt + 1))


def _sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def fetch_one(row, retries: int = 4) -> dict:
    _, rel, size, url = row
    dst = DATA / rel.lstrip("/")
    dst.parent.mkdir(parents=True, exist_ok=True)
    meta = _api(url.rstrip("/").split("/")[-1])
    rec = dict(path=rel, url=url, listing_bytes=size, osf=meta)
    if dst.exists() and dst.stat().st_size == meta["size"] and _sha256(dst) == meta["sha256"]:
        return dict(rec, local_bytes=dst.stat().st_size, sha256=meta["sha256"], status="present_verified")
    tmp = dst.with_name(dst.name + f".{os.getpid()}.part")
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=300) as r, open(tmp, "wb") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
            digest = _sha256(tmp)
            if digest != meta["sha256"]:
                raise IOError(f"SHA-256 mismatch for {rel}")
            os.replace(tmp, dst)
            return dict(rec, local_bytes=dst.stat().st_size, sha256=digest, status="downloaded_verified")
        except Exception as exc:            # network errors, rate limits and hash mismatches are retried
            last = repr(exc)
            time.sleep((30 if "429" in last else 5) * (attempt + 1))
    if tmp.exists():
        tmp.unlink()
    return dict(rec, status="failed", error=last)


def fetch(workers: int = 4) -> dict:
    rows = wanted()
    started = datetime.now(timezone.utc).isoformat()
    with ThreadPoolExecutor(workers) as ex:
        records = list(ex.map(fetch_one, rows))
    out = dict(source="OSF 4rn5q (John et al. 2025, CC-BY 4.0)", started_utc=started,
               finished_utc=datetime.now(timezone.utc).isoformat(), files=len(records),
               bytes=sum(r.get("local_bytes", 0) for r in records),
               failed=[r["path"] for r in records if r["status"] == "failed"], records=records)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "download_manifest.json").write_text(json.dumps(out, indent=1) + "\n")
    return out
