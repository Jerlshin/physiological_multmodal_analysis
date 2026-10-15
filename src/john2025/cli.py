"""Command line for the John 2025 replication (run with ``.venv-ext``; ``PYTHONPATH=src``).

  python -m john2025 fetch        acquire and verify the plan's files (OSF 4rn5q)
  python -m john2025 parse        EDF -> per-person archives (outcome-free)
  python -m john2025 features     features, 128 Hz series, case flow (outcome-free)
  python -m john2025 validate     synthetic-null calibration of the test (outcome-free)
  python -m john2025 freeze       write the feature-freeze record
  python -m john2025 verify       verify the freeze (prints VERIFIED or the problems)
  python -m john2025 run          gated outcome access, then every registered comparison
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from .paths import DERIVED, EVIDENCE, ROOT


def _git() -> dict:
    def run(*a):
        return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout
    status = run("status", "--porcelain")
    return dict(commit=run("rev-parse", "HEAD").strip(), dirty_files=[l[3:] for l in status.splitlines() if l.strip()][:300])


def cmd_run(args):
    from . import analysis, freeze
    from .outcomes import load_posttest
    from .population import QC_MAX_INVALID

    problems = freeze.verify()
    if problems:
        print("NOT VERIFIED:", *problems, sep="\n  ")
        return 2
    started = datetime.now(timezone.utc)
    run_id = started.strftime("%Y%m%dT%H%M%SZ")
    people = pd.read_parquet(DERIVED / "people.parquet")
    plan_pop = people[people.has_quest].sort_values("participant")
    y_all, semantics = load_posttest(plan_pop.participant.tolist(),
                                     purpose=f"run {run_id}: all {len(plan_pop)} plan-population participants "
                                             f"(analysis sets + QC-exclusion report)")
    y_map = dict(zip(plan_pop.participant, y_all))
    y_by_set = {k: np.array([y_map[p] for p in analysis.set_participants(k)]) for k in analysis.SETS}
    excluded = plan_pop[~plan_pop.qc_pass]
    included = plan_pop[plan_pop.qc_pass]
    exclusion = dict(rule=f"invalid-sample fraction > {QC_MAX_INVALID}", n_excluded=int(len(excluded)),
                     excluded_posttest=dict(mean=float(np.mean([y_map[p] for p in excluded.participant])),
                                            min=float(min(y_map[p] for p in excluded.participant)),
                                            max=float(max(y_map[p] for p in excluded.participant))),
                     included_posttest=dict(mean=float(np.mean([y_map[p] for p in included.participant])),
                                            sd=float(np.std([y_map[p] for p in included.participant], ddof=1))))
    result = analysis.run(y_by_set, workers=args.workers, ncv_reps=args.ncv_reps, n_perm=args.n_perm,
                          log=lambda m: print(m, flush=True))
    result.update(run_id=run_id, outcome_semantics=semantics, qc_exclusion=exclusion)
    store = ROOT / "results/runs/john2025" / run_id
    analysis.write_json(store / "result_full.json", result)
    aggregate = {k: v for k, v in result.items() if k not in ("predictions", "outer_folds")}
    analysis.write_json(EVIDENCE / "results" / "results.json", aggregate)
    analysis.write_json(store / "run.json", dict(run_id=run_id, started_utc=started.isoformat(),
                                                 finished_utc=datetime.now(timezone.utc).isoformat(),
                                                 argv=sys.argv, git=_git(), freeze_record_sha256=freeze.record_sha256(),
                                                 overrides=dict(ncv_reps=args.ncv_reps, n_perm=args.n_perm),
                                                 workers=args.workers, environment=freeze.environment()))
    analysis.write_json(EVIDENCE / "results" / "run.json", json.loads((store / "run.json").read_text()))
    print(json.dumps({k: v for k, v in aggregate["comparisons"]["PRIMARY_M5p_vs_M2p"].items()}, indent=1, default=float))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="john2025")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("fetch", "parse", "features", "freeze", "verify"):
        sub.add_parser(name)
    v = sub.add_parser("validate")
    v.add_argument("--workers", type=int, default=5)
    v.add_argument("--n", type=int, default=200)
    r = sub.add_parser("run")
    r.add_argument("--workers", type=int, default=5)
    r.add_argument("--ncv-reps", type=int, default=None, help="override only for smoke tests")
    r.add_argument("--n-perm", type=int, default=None, help="override only for smoke tests")
    args = ap.parse_args(argv)
    if args.cmd == "fetch":
        from .fetch import fetch
        out = fetch(workers=1)
        print(f"{out['files']} files, {out['bytes']} bytes, failed: {out['failed']}")
        return 1 if out["failed"] else 0
    if args.cmd == "parse":
        from .edf import parse_all
        print(f"{len(parse_all())} EDF files parsed")
    elif args.cmd == "features":
        from .features import extract_all
        from .population import build
        extract_all()
        print(build()[1].to_string(index=False))
    elif args.cmd == "validate":
        from .validate import run
        print(json.dumps(run(args.workers, args.n), indent=1))
    elif args.cmd == "freeze":
        from .freeze import record_sha256, write_record
        write_record()
        print("feature freeze written:", record_sha256())
    elif args.cmd == "verify":
        from .freeze import verify
        problems = verify()
        print("VERIFIED" if not problems else "NOT VERIFIED:\n  " + "\n  ".join(problems))
        return 1 if problems else 0
    elif args.cmd == "run":
        return cmd_run(args)
    return 0
