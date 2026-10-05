"""Command-line entry points for the G01-R baseline pipeline.

Pre-authorization (outcome-blind) stages:
    g01r population            rebuild and verify the frozen analysis sets; write the case flow
    g01r extract               outcome-blind feature extraction (processed and raw routes)
    g01r warm-syn              precompute synchrony features for the frozen regime-A splits
    g01r feature-qc            feature-level QC and missingness report (aggregates only)
    g01r validate-v1           production re-validation of the operating characteristics (simulated data)
    g01r validate-v2           null calibration on the real features with synthetic outcomes
    g01r validation-verdict    apply the protocol §17.3 targets; choose the detection procedure
    g01r freeze / verify-freeze
    g01r dry-run               run registry analyses end-to-end on SYNTHETIC outcomes (tracked)

User action after the preregistration deposit (never run automatically):
    g01r authorize --preregistration <DOI/URL> --by <name>

Post-authorization:
    g01r run --analysis H1_H2 | all     real outcomes; refuses without a verified authorization
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import warnings

import pandas as pd

from .config import CONFIG_PATH, IMPL_EVIDENCE, load_config


def _tracker(name, cfg, experiment, **tags):
    from .tracking import RunTracker

    return RunTracker(experiment, name, cfg, tags=tags)


def cmd_population(args):
    from .population import Population

    cfg = load_config()
    with _tracker("population", cfg, "g01r-pipeline", stage="population") as tr:
        summary = Population(cfg).write_ledger(IMPL_EVIDENCE / "population")
        tr.log_json("population_summary.json", summary)
        tr.log_metrics({k: v for k, v in summary.items() if k not in ("by_experiment", "verified_against_frozen_manifest")})
        tr.log_file(IMPL_EVIDENCE / "population" / "case_flow.csv")
    print(json.dumps({k: v for k, v in summary.items() if k != "by_experiment"}, indent=1))


def cmd_extract(args):
    from .features.extract import cache_index, extract
    from .population import Population

    cfg = load_config()
    pop = Population(cfg)
    with _tracker("extract", cfg, "g01r-pipeline", stage="feature_extraction") as tr:
        for route in args.routes:
            cells = pop.cells if route == "processed" else pop.cells[pop.cells.PAS_E34_core]
            frame = extract(cfg, cells, route, workers=args.workers)
            idx = cache_index(route)
            tr.log_frame(f"cache_index_{route}.csv", idx)
            tr.log_metrics({f"{route}.cells": len(frame), f"{route}.cache_files": len(idx),
                            f"{route}.cache_bytes": int(idx.bytes.sum())})


def cmd_warm_syn(args):
    from multiprocessing import get_context

    jobs = [(args.set, args.route, r) for r in range(load_config().resampling["reps_A"])]
    t = time.time()
    with get_context("spawn").Pool(args.workers) as pool:
        for _ in pool.imap_unordered(_warm_rep, jobs):
            pass
    print(f"warm {args.set}|{args.route}: {time.time() - t:.0f}s")


def _warm_rep(a):
    import numpy as np

    from . import references as R
    from .analysis import _context
    from .splits import outer_folds

    set_name, route, r = a
    cfg, aset, prov = _context(str(CONFIG_PATH), (), set_name, route, False)
    K = cfg.resampling["outer_folds_A"]
    folds = outer_folds(aset, K, cfg.resampling["reps_A"], cfg.resampling["base_seed"], aset.name, "A")
    prov.syn_many([R.regime_A(aset, folds[r][aset.person] != k, np.ones(aset.n, bool)) for k in range(K)])
    return r


def cmd_feature_qc(args):
    from . import feature_qc

    cfg = load_config()
    with _tracker("feature_qc", cfg, "g01r-pipeline", stage="feature_qc") as tr:
        rep = feature_qc.run(cfg)
        tr.log_file(IMPL_EVIDENCE / "feature_qc" / "feature_qc.json")
        tr.log_file(IMPL_EVIDENCE / "feature_qc" / "feature_summary.csv")
        tr.log_metrics(dict(revise_trigger_value=rep["revise_trigger"]["value"],
                            revise_trigger_fired=float(rep["revise_trigger"]["fired"])))
    print(json.dumps(rep["revise_trigger"], indent=1))


def cmd_validate_v1(args):
    from .validate import run_v1

    cfg = load_config()
    out = IMPL_EVIDENCE / "validation"
    out.mkdir(parents=True, exist_ok=True)
    with _tracker("validate_v1", cfg, "g01r-validation", stage="V1", nsim=args.nsim) as tr:
        tr.log_params(dict(nsim=args.nsim, n_perm=args.n_perm or cfg.inference["n_permutations"],
                           ncv_reps=args.ncv_reps, workers=args.workers))
        summary = run_v1(str(CONFIG_PATH), nsim=args.nsim, workers=args.workers, n_perm=args.n_perm,
                         ncv_reps=args.ncv_reps, out_dir=out, tracker=tr)
        summary.to_csv(out / "v1_summary.csv", index=False)
        tr.log_frame("v1_summary.csv", summary)
        for _, row in summary.iterrows():
            tr.log_metrics({k: v for k, v in row.items() if isinstance(v, float)}, prefix=row.scenario)
    print(summary.to_string())


def cmd_validate_v2(args):
    from .validate import run_v2

    cfg = load_config()
    out = IMPL_EVIDENCE / "validation"
    out.mkdir(parents=True, exist_ok=True)
    with _tracker("validate_v2", cfg, "g01r-validation", stage="V2", nsim=args.nsim) as tr:
        tr.log_params(dict(nsim=args.nsim, n_perm=args.n_perm, workers=args.workers))
        summary = run_v2(str(CONFIG_PATH), nsim=args.nsim, workers=args.workers, n_perm=args.n_perm, tracker=tr,
                         out_dir=out)
        summary.to_csv(out / "v2_summary.csv", index=False)
        tr.log_frame("v2_summary.csv", summary)
        for _, row in summary.iterrows():
            tr.log_metrics({k: v for k, v in row.items() if isinstance(v, float)}, prefix=row.scenario)
    print(summary.to_string())


def cmd_validation_verdict(args):
    import numpy as np

    cfg = load_config()
    out = IMPL_EVIDENCE / "validation"
    read = dict(keep_default_na=False, na_values=[""])      # the scenario label "null" is not a missing value
    v1 = pd.read_csv(out / "v1_summary.csv", **read).set_index("scenario")
    v2 = pd.read_csv(out / "v2_summary.csv", **read).set_index("scenario")
    t = cfg.validation
    fd = float(v1.loc["null", "detect_perm"])
    power = float(v1.loc["truth_at_2delta", "detect_perm"])
    fut_err = float(v1.loc["truth_at_2delta", "futility_rules_out_threshold"])
    nulls = v2[v2.index.str.contains("null")]
    v2_max = float(nulls.detect_perm.max())
    checks = dict(
        false_detection=dict(value=fd, target=f"<= {t['max_false_detection']}", passed=fd <= t["max_false_detection"]),
        power_at_2delta=dict(value=power, target=f">= {t['min_power_at_2delta']}", passed=power >= t["min_power_at_2delta"]),
        futility_error_at_0_10=dict(value=fut_err, target=f"<= {t['max_futility_error']}", passed=fut_err <= t["max_futility_error"]),
        real_feature_null_false_detection=dict(value=v2_max, target=f"<= {t['max_false_detection']} (all V2 scenarios)",
                                               passed=v2_max <= t["max_false_detection"]),
    )
    detection = "permutation" if checks["false_detection"]["passed"] and checks["real_feature_null_false_detection"]["passed"] \
        else cfg.inference["fallback_detection"]
    verdict = dict(checks=checks, all_passed=all(c["passed"] for c in checks.values()), detection_procedure=detection,
                   rule="protocol §17.3; fallback per readiness verdict condition 2 / EDD-009",
                   v1_reference_design_phase=dict(false_detection=0.063, power_at_2delta=0.93, futility_error=0.043),
                   v1_rows=v1.reset_index().to_dict("records"), v2_rows=v2.reset_index().to_dict("records"))
    (out / "validation_verdict.json").write_text(json.dumps(verdict, indent=2, default=float) + "\n")
    print(json.dumps({k: verdict[k] for k in ("checks", "all_passed", "detection_procedure")}, indent=1, default=float))


def cmd_freeze(args):
    from .freeze import write_manifest

    cfg = load_config()
    path = write_manifest(cfg)
    print(f"wrote {path}")


def cmd_verify_freeze(args):
    from .freeze import environment_differences, uncommitted_bound_files, verify_manifest

    problems = verify_manifest(load_config(), include_caches=not args.skip_caches)
    print("VERIFIED" if not problems else f"MISMATCH: {problems}")
    for diff in environment_differences():
        print(f"NOTE environment differs from the freeze (recorded, not enforced): {diff}")
    uncommitted = uncommitted_bound_files()
    if uncommitted:
        print(f"NOTE {len(uncommitted)} bound files are not committed; `authorize` requires a committed freeze: "
              f"{uncommitted[:5]}")
    sys.exit(0 if not problems else 1)


def cmd_authorize(args):
    from .freeze import authorize

    path = authorize(load_config(), args.preregistration, args.by, args.statement)
    print(f"wrote {path}")


def _run_specs(args, source, experiment):
    from .analysis import RUNNERS, Executor
    from .registry import REGISTRY, get

    cfg = load_config()
    overrides = {}
    if args.ncv_reps is not None:
        overrides["inference.ncv_reps"] = args.ncv_reps
    if args.n_perm is not None:
        overrides["inference.n_permutations"] = args.n_perm
    if getattr(args, "reps_a", None) is not None:
        overrides["resampling.reps_A"] = args.reps_a
    if getattr(args, "reps_bc", None) is not None:
        overrides["resampling.reps_BC"] = args.reps_bc
    if overrides:
        cfg = cfg.with_overrides(**overrides)
    specs = REGISTRY if args.analysis == "all" else [get(a) for a in args.analysis.split(",")]
    ex = Executor(args.workers)
    results = {}
    try:
        for spec in specs:
            if spec.regime == "derived":
                continue
            with _tracker(spec.id, cfg, experiment, analysis=spec.id, role=spec.role, regime=spec.regime,
                          outcome_source=source.describe()) as tr:
                tr.log_params(dict(spec=dict(id=spec.id, set=spec.set_name, regime=spec.regime, outcome=spec.outcome,
                                             route=spec.route, include_gpa=spec.include_gpa, models=list(spec.models)),
                                   workers=args.workers))
                t0 = time.time()
                kwargs = {}
                if spec.regime == "A":
                    kwargs = dict(ncv_reps=cfg.inference["ncv_reps"], n_perm=cfg.inference["n_permutations"])
                res = RUNNERS[spec.regime](spec, cfg, source, tr, ex, **kwargs)
                res["elapsed_s"] = time.time() - t0
                tr.log_json("result.json", res)
                tr.log_metrics(res)
                results[spec.id] = res
                print(f"[{spec.id}] done in {res['elapsed_s']:.0f}s -> {tr.dir}", flush=True)
    finally:
        ex.close()
    return results


def cmd_dry_run(args):
    from .analysis import OutcomeSource

    scenario = {"nuisance_share": args.nuisance_share} if args.nuisance_share else {}
    source = OutcomeSource("synthetic", scenario=scenario, seed_label=args.label)
    _run_specs(args, source, args.experiment)


def cmd_run(args):
    from .analysis import OutcomeSource
    from .freeze import load_authorization

    cfg = load_config()
    auth = load_authorization(cfg)            # raises OutcomeAccessDenied unless authorized and verified
    if args.ncv_reps is not None or args.n_perm is not None:
        raise SystemExit("Confirmatory runs use the frozen configuration only (no overrides)")
    _run_specs(args, OutcomeSource("real", authorization=auth), "g01r-confirmatory")


def cmd_report(args):
    from pathlib import Path

    from .report import write

    path = write(args.experiment, Path(args.out), args.title)
    print(f"wrote {path}")


def main(argv=None):
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    p = argparse.ArgumentParser(prog="g01r", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("population").set_defaults(fn=cmd_population)
    s = sub.add_parser("extract")
    s.add_argument("--routes", nargs="+", default=["processed", "raw"])
    s.add_argument("--workers", type=int, default=6)
    s.set_defaults(fn=cmd_extract)
    s = sub.add_parser("warm-syn")
    s.add_argument("--set", default="PAS_E34_core")
    s.add_argument("--route", default="processed")
    s.add_argument("--workers", type=int, default=5)
    s.set_defaults(fn=cmd_warm_syn)
    sub.add_parser("feature-qc").set_defaults(fn=cmd_feature_qc)
    s = sub.add_parser("validate-v1")
    s.add_argument("--nsim", type=int, default=300)
    s.add_argument("--workers", type=int, default=9)
    s.add_argument("--n-perm", type=int, default=None)
    s.add_argument("--ncv-reps", type=int, default=20)
    s.set_defaults(fn=cmd_validate_v1)
    s = sub.add_parser("validate-v2")
    s.add_argument("--nsim", type=int, default=200)
    s.add_argument("--workers", type=int, default=5)
    s.add_argument("--n-perm", type=int, default=199)
    s.set_defaults(fn=cmd_validate_v2)
    sub.add_parser("validation-verdict").set_defaults(fn=cmd_validation_verdict)
    sub.add_parser("freeze").set_defaults(fn=cmd_freeze)
    s = sub.add_parser("verify-freeze")
    s.add_argument("--skip-caches", action="store_true")
    s.set_defaults(fn=cmd_verify_freeze)
    s = sub.add_parser("authorize", help="USER ACTION after the preregistration deposit")
    s.add_argument("--preregistration", required=True)
    s.add_argument("--by", required=True)
    s.add_argument("--statement", default="Preregistration deposited; real-outcome analysis authorized under the frozen protocol.")
    s.set_defaults(fn=cmd_authorize)
    s = sub.add_parser("report")
    s.add_argument("--experiment", default="g01r-confirmatory")
    s.add_argument("--out", default="results/report")
    s.add_argument("--title", default="G01-R baseline study results")
    s.set_defaults(fn=cmd_report)
    for name, fn in (("dry-run", cmd_dry_run), ("run", cmd_run)):
        s = sub.add_parser(name)
        s.add_argument("--analysis", default="H1_H2")
        s.add_argument("--workers", type=int, default=5)
        s.add_argument("--ncv-reps", type=int, default=None)
        s.add_argument("--n-perm", type=int, default=None)
        if name == "dry-run":
            s.add_argument("--reps-a", type=int, default=None, help="smoke-test override (recorded as non-frozen)")
            s.add_argument("--reps-bc", type=int, default=None, help="smoke-test override (recorded as non-frozen)")
            s.add_argument("--experiment", default="g01r-dryrun-synthetic")
            s.add_argument("--label", default="dryrun")
            s.add_argument("--nuisance-share", type=float, default=0.0)
        s.set_defaults(fn=fn)
    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
