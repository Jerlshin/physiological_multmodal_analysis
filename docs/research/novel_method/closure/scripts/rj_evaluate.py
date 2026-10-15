"""Rule R-J: evaluate the re-simulation on the frozen human anchors and write ``rj_record.json`` (closure C-D09).

    python rj_evaluate.py <rj_run_dir> <design_config.json> <anchors_frozen.csv> <out rj_record.json>

The record states whether every R-H pass criterion holds on the human anchor structure and the pooled power at
OR 1.5 (random truth). It binds the anchor-table and design-configuration hashes, which ``cairn.freezing`` checks
before it writes a development freeze record. Outcome-free: the run uses synthetic outcomes only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from cairn import closure_analysis as CA

if __name__ == "__main__":
    run_dir, cfg_path, anchors, out = map(Path, sys.argv[1:5])
    cfg = json.loads(cfg_path.read_text())
    man = json.loads((run_dir / "MANIFEST.json").read_text())
    if man["inputs"]["anchor_table"]["sha256"] != __import__("cairn.paths", fromlist=["x"]).sha256_file(anchors):
        raise SystemExit("the R-J run did not use this anchor table")
    d = CA.load(run_dir)
    rec = CA.rj_record(d, cfg["parametrization"], int(cfg["detrend_degree"]), anchors, cfg_path, man["manifest_sha256"])
    out.write_text(json.dumps(rec, indent=2, default=float))
    print(json.dumps(rec, indent=2, default=float))
    sys.exit(0 if rec["passed"] else 1)
