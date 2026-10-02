#!/usr/bin/env python3
"""Audit BBBD repository reference TSV metadata only; no model or waveform work.
Usage: python3 audit_repository_metadata.py /path/to/pinned/bbbd-dataset output.json
Pin commit 5109afa0fd70c407b869108106f5808c6b0cc33c before running.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

def audit(checkout):
    records = []
    for path in sorted((checkout / "data-reformatting/config").glob("*.tsv")):
        with path.open() as stream:
            rows = list(csv.DictReader(stream, delimiter="\t"))
        if not rows:
            continue
        records.append({
            "file": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "rows": len(rows),
            "unique_participant_ids": len({r["participant_id"] for r in rows}),
            "columns": list(rows[0]),
            "nonmissing_by_column": {
                key: sum(r[key].strip().lower() not in ("", "nan", "n/a", "na") for r in rows)
                for key in rows[0]
            },
            "contains_sub09": any(r["participant_id"] == "sub-09" for r in rows),
        })
    if not records:
        raise SystemExit("No reference TSVs found; pass the extracted repository root.")
    return records

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    result = {
        "scope": "Repository reference TSVs only; NOT verified Zenodo archive or usable waveform cohort",
        "commit": "5109afa0fd70c407b869108106f5808c6b0cc33c",
        "files": audit(Path(sys.argv[1])),
    }
    Path(sys.argv[2]).write_text(json.dumps(result, indent=2) + "\n")
