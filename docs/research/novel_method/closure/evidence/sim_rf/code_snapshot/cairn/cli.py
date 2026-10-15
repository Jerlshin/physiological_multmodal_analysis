"""``python -m cairn {verify, simulate, run}`` (Stage-1 spec §2.2).

* ``verify``   outcome-free self-checks: gate closed, set incidence, item-key map, anchor-table hash,
               timeline round trip, fold safety and reference rule on a real split, identity probe;
* ``simulate`` the Stage-1 design simulation (writes its manifest before any fitting);
* ``run``      any outcome-linked analysis. It calls the gate first and therefore refuses until a
               CAIRN freeze (with a G-AN-frozen human anchor set) and a scoped user authorization exist.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .paths_stage1 import STAGE1_EVIDENCE


def cmd_verify(args) -> int:
    from . import checks
    rep = checks.run_all(quick=args.quick)
    print(json.dumps(rep, indent=2, default=str))
    if args.out:
        Path(args.out).write_text(json.dumps(rep, indent=2, default=str))
    return 0 if rep["passed"] else 1


def cmd_simulate(args) -> int:
    from . import design, manifest, simrun
    from . import inference as I
    from . import simulate as SIM

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    g = simrun.grid(args.grid)
    m = manifest.build(
        run_id=f"stage1-sim-{args.grid}", stage="1-simulation",
        sets=sorted({s for s, *_ in g}), regime="A", extra=dict(primary_form=SIM.PRIMARY_FORM, mode=simrun.mode_of(args.grid),
                                                         also_done=list(args.also_done)),
        models=["IRT-M2", "IRT-whole", "CAIRN-linear", "CAIRN-linear-dir (frozen development direction)",
                "CAIRN-validity", "CAIRN-gaze", "B9 Lalle-style pooled classifier"],
        grid=[dict(set=s, scenario=sc.key, replicates=n, circular_shift=c, B=args.B or b) for s, sc, n, c, b in g],
        cv=dict(outer=f"learner-grouped, experiment-stratified {I.K_FOLDS}-fold", repetitions=I.R_REPS, inner="none (fixed hyperparameters, S1-D04)",
                cv_seeds=list(range(I.R_REPS))),
        inference=dict(B_null=simrun.B_NULL, B_alternative=simrun.B_ALT, B_override=args.B, circular_shift_min_s=I.CIRC_MIN_S, alpha=0.05,
                       ridge=dict(intercepts=I.G_PEN, person_path=I.R_F, moment_multi=I.R_M_MULTI, moment_one=I.R_M_ONE)),
        seeds=dict(base=simrun.BASE_SEED, per_task="sha256(base|set|scenario)[:8]", cv=list(range(I.R_REPS))),
        outcome_access="none (synthetic outcomes only)")
    h = manifest.write(m, out / "MANIFEST.json")
    print(f"manifest {h}", flush=True)
    # build every structure once so fold caches exist before workers start (no write races)
    for s in sorted({s for s, *_ in g} | {"development"}):
        I.build_structure(design.build(s))
    log_path = out / "run.log"

    def log(msg):
        line = f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} {msg}"
        print(line, flush=True)
        with log_path.open("a") as f:
            f.write(line + "\n")

    log(f"start grid={args.grid} manifest={h}")
    res = simrun.run(out, args.grid, workers=args.workers, B=args.B, log=log, also_done=tuple(args.also_done))
    log(f"finished {res}")
    return 0


def cmd_closure(args) -> int:
    """Closure-phase simulations (docs/research/novel_method/closure): manifest first, then the grid, set by set."""
    from . import manifest, simrun
    from . import inference as I
    from . import simulate as SIM

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    g = simrun.closure_grid(args.grid, args.degree, args.chosen)
    m = manifest.build(
        run_id=f"closure-sim-{args.grid}", stage="1-simulation", sets=sorted({e[0] for e in g}), regime="A",
        extra=dict(phase="closure", mode=args.grid, degree=args.degree, chosen=args.chosen,
                   degrees=list(simrun.closure_degrees(args.grid, args.degree)), rules=args.rules_sha256),
        models=sorted({v.name for v in SIM.closure_variants(args.grid if args.grid != "conf" else "conf", args.degree,
                                                            args.chosen or "P6")["lr"]}),
        grid=[dict(set=s, scenario=sc.key, replicates=n, B=b, mode=mo, kwargs=kw) for s, sc, n, b, mo, kw in g],
        cv=dict(outer=f"learner-grouped, experiment-stratified {I.K_FOLDS}-fold", repetitions=I.R_REPS,
                inner="none (fixed hyperparameters, S1-D04)", cv_seeds=list(range(I.R_REPS))),
        inference=dict(B_null=simrun.B_NULL, B_alternative=simrun.B_ALT, circular_shift_min_s=I.CIRC_MIN_S, alpha=0.05,
                       ridge=dict(intercepts=I.G_PEN, person_path=I.R_F, moment_multi=I.R_M_MULTI, moment_one=I.R_M_ONE)),
        seeds=dict(base=simrun.BASE_SEED, per_task="sha256(base|set|mode|scenario)[:8]", cv=list(range(I.R_REPS))),
        outcome_access="none (synthetic outcomes only)")
    h = manifest.write(m, out / "MANIFEST.json")
    log_path = out / "run.log"

    def log(msg):
        line = f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} {msg}"
        print(line, flush=True)
        with log_path.open("a") as f:
            f.write(line + "\n")

    log(f"start closure grid={args.grid} degree={args.degree} chosen={args.chosen} manifest={h}")
    res = simrun.run_closure(out, args.grid, args.degree, args.chosen, workers=args.workers, log=log)
    log(f"finished {res}")
    return 0


def cmd_run(args) -> int:
    from . import gate
    try:
        gate.load_authorization(args.scope)          # raises unless frozen and authorized
    except gate.OutcomeAccessDenied as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    print("Authorization verified; the Stage-2 analysis entry point is not part of Stage 1.", file=sys.stderr)
    return 3


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="cairn")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--quick", action="store_true")
    v.add_argument("--out", default=None)
    s = sub.add_parser("simulate")
    s.add_argument("--grid", default="main")
    s.add_argument("--workers", type=int, default=9)
    s.add_argument("--B", type=int, default=None, help="override every entry's permutation budget (pilots only)")
    s.add_argument("--out", default=str(STAGE1_EVIDENCE / "sim"))
    s.add_argument("--also-done", action="append", default=[], help="earlier output directory whose replicates count as done")
    c = sub.add_parser("closure")
    c.add_argument("--grid", required=True, choices=["rf", "rg", "nh4", "conf"])
    c.add_argument("--degree", type=int, default=1)
    c.add_argument("--chosen", default="")
    c.add_argument("--workers", type=int, default=8)
    c.add_argument("--rules-sha256", default="")
    c.add_argument("--out", required=True)
    r = sub.add_parser("run")
    r.add_argument("--scope", default="development")
    a = ap.parse_args(argv)
    return dict(verify=cmd_verify, simulate=cmd_simulate, closure=cmd_closure, run=cmd_run)[a.cmd](a)
