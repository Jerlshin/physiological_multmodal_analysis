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
    if args.config:                                     # rule R-J: degree and parametrization from the frozen design
        cfg = json.loads(Path(args.config).read_text())
        args.degree, args.chosen = int(cfg["detrend_degree"]), cfg["parametrization"]
    out.mkdir(parents=True, exist_ok=True)
    g = simrun.closure_grid(args.grid, args.degree, args.chosen)
    m = manifest.build(
        run_id=f"closure-sim-{args.grid}", stage="1-simulation", sets=sorted({e[0] for e in g}), regime="A",
        extra=dict(phase="closure", mode=args.grid, degree=args.degree, chosen=args.chosen,
                   degrees=list(simrun.closure_degrees(args.grid, args.degree)), rules=args.rules_sha256),
        models=sorted({v.name for v in SIM.closure_variants("conf" if args.grid in ("conf", "rj", "cvpow") else args.grid,
                                                            args.degree, args.chosen or "P6")["lr"]}),
        grid=[dict(set=s, scenario=sc.key, replicates=n, B=b, mode=mo, kwargs=kw) for s, sc, n, b, mo, kw in g],
        cv=dict(outer=f"learner-grouped, experiment-stratified {I.K_FOLDS}-fold", repetitions=I.R_REPS,
                inner="none (fixed hyperparameters, S1-D04)", cv_seeds=list(range(I.R_REPS))),
        inference=dict(B_null=simrun.B_NULL, B_alternative=simrun.B_ALT, circular_shift_min_s=I.CIRC_MIN_S, alpha=0.05,
                       ridge=dict(intercepts=I.G_PEN, person_path=I.R_F, moment_multi=I.R_M_MULTI, moment_one=I.R_M_ONE)),
        seeds=dict(base=simrun.BASE_SEED, per_task="sha256(base|set|mode|scenario)[:8]", cv=list(range(I.R_REPS))),
        outcome_access="none (synthetic outcomes only)", anchor_table=Path(args.anchors) if args.anchors else manifest.PROVISIONAL_ANCHORS)
    h = manifest.write(m, out / "MANIFEST.json")
    log_path = out / "run.log"

    def log(msg):
        line = f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} {msg}"
        print(line, flush=True)
        with log_path.open("a") as f:
            f.write(line + "\n")

    log(f"start closure grid={args.grid} degree={args.degree} chosen={args.chosen} anchors={args.anchors} manifest={h}")
    res = simrun.run_closure(out, args.grid, args.degree, args.chosen, workers=args.workers, log=log, anchors=args.anchors)
    log(f"finished {res}")
    return 0


def cmd_gan(args) -> int:
    """G-AN coordinator commands (closure C-D10): validate, receive, agreement, table, freeze."""
    import pandas as pd

    from . import gan
    if args.action == "validate":
        rep = gan.validate_file(Path(args.files[0]))
        print(json.dumps(rep, indent=2))
        return 0 if rep["valid"] else 1
    if args.action == "receive":
        print(json.dumps(gan.receive(Path(args.files[0]), Path(args.log)), indent=2))
        return 0
    if args.action == "agreement":
        rep, w = gan.agreement(Path(args.files[0]), Path(args.files[1]))
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "agreement_report.json").write_text(json.dumps(rep, indent=2, default=str))
        w.to_csv(out / "agreement_items.csv", index=False)
        gan.adjudication_worksheet(w).to_csv(out / "adjudication_worksheet.csv", index=False)
        print(json.dumps(dict(gate=rep["gate"], kappa_type=rep["kappa_type"], to_adjudicate=rep["items_to_adjudicate"]), indent=2))
        return 0 if rep["gate"]["passed"] else 1
    if args.action == "bundle":
        print(json.dumps(gan.bundle(Path(args.out), args.files[0]), indent=2))
        return 0
    if args.action == "package":
        rep = gan.verify_package()
        print(json.dumps(rep, indent=2))
        return 0 if rep["passed"] else 1
    if args.action == "consensus":
        h1, h2, *dec = map(Path, args.files)
        tab = gan.consensus(h1, h2, dec[0] if dec else None, args.adjudicator)
        tab.to_csv(args.out, index=False)
        v = gan.validate_file(Path(args.out))
        print(json.dumps(dict(written=args.out, valid=v["valid"], errors=v["errors"][:10]), indent=2))
        return 0 if v["valid"] else 1
    if args.action == "table":
        tab = gan.anchor_table(Path(args.files[0]))
        tab.to_csv(args.out, index=False, float_format="%.2f")
        print(json.dumps(dict(anchorable=int(tab.anchorable.sum()), moments_locked=gan.moment_count(tab, ["Stars", "Immune", "Related"]),
                              human_vs_r2=gan.compare_to_r2(tab)), indent=2))
        return 0
    if args.action == "freeze":
        h1, h2, adj, log = map(Path, args.files)
        print(json.dumps(gan.freeze_human_set(h1, h2, adj, log, Path(args.out)), indent=2, default=str))
        return 0
    raise SystemExit(f"unknown action {args.action}")


def cmd_freeze(args) -> int:
    """CAIRN freeze record (closure C-D11). ``build`` prints the record; ``--write`` writes it (archiving any previous
    record). ``authorization-template`` prints the JSON the user writes to authorize one scope."""
    from . import freezing
    if args.action == "authorization-template":
        print(json.dumps(freezing.authorization_template(args.scope, args.purpose), indent=2))
        return 0
    rec = freezing.build_record(args.stage, Path(args.anchors), Path(args.rj), Path(args.config))
    if args.write:
        print(f"written {freezing.write_record(rec)}")
    print(json.dumps({k: v for k, v in rec.items() if k != "bound_files"}, indent=2))
    return 0


def cmd_dryrun(args) -> int:
    """Synthetic end-to-end run of the Stage-2 development analysis (never touches the gate)."""
    from . import stage2
    from .paths_stage1 import PROVISIONAL_ANCHORS
    sc = json.loads(args.scenario)
    if args.stage == "lock":
        from . import lock
        lock.run_lock(Path(args.out), Path(args.config), Path(args.anchors or PROVISIONAL_ANCHORS), source="synthetic",
                      scenario=sc, seed=args.seed, B=args.B, R=args.R)
        return 0
    stage2.run_development(Path(args.out), Path(args.config), Path(args.anchors or PROVISIONAL_ANCHORS), source="synthetic",
                           scenario=sc, seed=args.seed, B=args.B, R=args.R, kernels=not args.no_kernels)
    return 0


def cmd_run(args) -> int:
    from . import gate
    try:
        gate.load_authorization(args.scope)          # raises unless frozen and authorized
    except gate.OutcomeAccessDenied as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    if not (args.config and args.anchors and args.out):
        print("run needs --config (frozen design), --anchors (frozen table) and --out", file=sys.stderr)
        return 3
    if args.scope == "development":
        from . import stage2
        stage2.run_development(Path(args.out), Path(args.config), Path(args.anchors), source="gated")
        return 0
    if args.scope in ("locked_primary", "locked_secondary"):
        from . import lock
        lock.run_lock(Path(args.out), Path(args.config), Path(args.anchors), source="gated")   # checks both locked scopes
        return 0
    print("the reserved-descriptive scope has no entry point before the lock report", file=sys.stderr)
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
    c.add_argument("--grid", required=True, choices=["rf", "rg", "nh4", "conf", "rj", "cvpow"])
    c.add_argument("--anchors", default=None, help="frozen human anchor table (rule R-J); default: provisional")
    c.add_argument("--config", default=None, help="design_config.json: sets --degree and --chosen (rule R-J)")
    c.add_argument("--degree", type=int, default=1)
    c.add_argument("--chosen", default="")
    c.add_argument("--workers", type=int, default=8)
    c.add_argument("--rules-sha256", default="")
    c.add_argument("--out", required=True)
    g = sub.add_parser("gan")
    g.add_argument("action", choices=["package", "bundle", "validate", "receive", "agreement", "consensus", "table", "freeze"])
    g.add_argument("--adjudicator", default="ADJ")
    g.add_argument("files", nargs="*")
    g.add_argument("--log", default="docs/research/novel_method/closure/gan/receipts.jsonl")
    g.add_argument("--out", default=None)
    fz = sub.add_parser("freeze")
    fz.add_argument("action", choices=["build", "authorization-template"])
    fz.add_argument("--stage", default="development", choices=["development", "lock"])
    fz.add_argument("--anchors", help="directory holding ANCHOR_FREEZE.json and its companion")
    fz.add_argument("--rj", help="rule R-J record (rj_record.json)")
    fz.add_argument("--config", help="frozen design configuration (design_config.json)")
    fz.add_argument("--write", action="store_true")
    fz.add_argument("--scope", default="development")
    fz.add_argument("--purpose", default="Stage-2 development analysis (DAP-1)")
    d = sub.add_parser("dryrun")
    d.add_argument("--out", required=True)
    d.add_argument("--config", required=True)
    d.add_argument("--anchors", default=None)
    d.add_argument("--scenario", default='{"name": "ALT", "odds_ratio": 2.0, "rho": 0.7, "truth": "random"}')
    d.add_argument("--seed", type=int, default=0)
    d.add_argument("--B", type=int, default=99)
    d.add_argument("--R", type=int, default=3)
    d.add_argument("--no-kernels", action="store_true")
    d.add_argument("--stage", default="development", choices=["development", "lock"])
    r = sub.add_parser("run")
    r.add_argument("--scope", default="development")
    r.add_argument("--config", default=None)
    r.add_argument("--anchors", default=None)
    r.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    return dict(verify=cmd_verify, simulate=cmd_simulate, closure=cmd_closure, gan=cmd_gan, freeze=cmd_freeze,
                dryrun=cmd_dryrun, run=cmd_run)[a.cmd](a)
