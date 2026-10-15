"""Parallel, resumable runner for the Stage-1 design simulation (spec §1.6, §1.8).

Tasks are (set, scenario, replicate). Each finished replicate is appended as one JSON line to
``<out>/<set>/<scenario>.jsonl``; a restarted run skips replicates already present, so results are
identical whether or not the run was interrupted (every replicate's randomness derives only from
(base seed, set, scenario, replicate)).
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict
from pathlib import Path

from . import simulate as SIM

BASE_SEED = 20261013
OR_RHO04 = (1.15, 1.25, 1.35, 1.50, 1.75, 2.00, 2.50, 3.00)
OR_RHO02 = (1.50, 2.00, 2.50, 3.00, 4.00)
OR_RHO07 = (1.15, 1.25, 1.35, 1.50, 1.75, 2.00)
NULLS = ("N0", "N1", "N2", "N3")


def task_seed(set_name: str, scenario_key: str) -> int:
    return int(hashlib.sha256(f"{BASE_SEED}|{set_name}|{scenario_key}".encode()).hexdigest()[:8], 16)


B_NULL = 199          # spec §1.5
B_ALT = 99            # alternatives and sensitivity: an exact test with a coarser grid; can only understate power (S1-D08)


def grid(name: str = "main") -> list:
    """Declared Stage-1 grid in priority order: (set, Scenario, replicates, circular-shift null, B)."""
    S = SIM.Scenario
    if name == "pilot":
        return [("locked_primary", S("N0"), 36, True, 99), ("locked_primary", S("ALT", 2.0, 0.7), 18, True, 99),
                ("development", S("N1"), 18, True, 99)]
    if name == "addendum":
        # rule R-E: non-linear fatigue on the recommended pooled design; E4 extended 200 -> 500 (same seed sequence)
        return [("locked_pooled", S("N1q"), 500, True, B_NULL), ("locked_primary", S("N1q"), 500, True, B_NULL)]
    if name == "n1decision":
        # raw vs within-recording-detrended CAIRN-linear under the fatigue/position confound (S1-D06)
        return [(s, S(n), 200, True, B_NULL) for s in ("locked_primary", "development") for n in ("N1", "N0")] + \
               [(s, S("ALT", 1.5, 0.4), 100, True, B_NULL) for s in ("locked_primary", "development")]
    g = []
    # phase A (decisive): E4, then development, then the pooled lock's N0/N1 and power
    for set_name in ("locked_primary", "development"):
        g += [(set_name, S(n), 500, n in ("N0", "N1"), B_NULL) for n in NULLS]
        g += [(set_name, S("ALT", o, 0.4), 200, set_name == "locked_primary", B_ALT) for o in OR_RHO04]
    g += [("locked_pooled", S(n), 500, True, B_NULL) for n in ("N0", "N1")]
    g += [("locked_pooled", S("ALT", o, 0.4), 200, False, B_ALT) for o in OR_RHO04]
    # phase B: completes calibration, reliability range, NH4, non-linear fatigue, secondary lock, realism
    g += [("locked_pooled", S(n), 500, False, B_NULL) for n in ("N2", "N3")]
    g += [(s, S("N1q"), 200, True, B_NULL) for s in ("locked_primary", "development")]
    g += [(s, S("N4"), 200, False, B_NULL) for s in ("locked_primary", "development")]
    for set_name in ("locked_primary", "development", "locked_pooled"):
        g += [(set_name, S("ALT", o, 0.2), 100, False, B_ALT) for o in OR_RHO02]
        g += [(set_name, S("ALT", o, 0.7), 100, False, B_ALT) for o in OR_RHO07]
    g += [("locked_secondary", S(n), 200, n == "N1", B_NULL) for n in ("N0", "N1")]
    for kw in (dict(sigma_q=0.0), dict(two_pl=True), dict(guessing=True), dict(hetero=True)):
        g.append(("locked_primary", S("N0", **kw), 200, False, B_NULL))
        g.append(("locked_primary", S("ALT", 1.5, 0.4, **kw), 100, False, B_ALT))
    g.append(("locked_primary", S("ALT", 1.5, 0.4, truth="logdens"), 100, False, B_ALT))
    g.append(("locked_primary", S("N2", 1.5, 0.4), 100, False, B_ALT))
    g.append(("locked_pooled", S("ALT", 1.5, 0.4, e5_factor=0.5), 100, False, B_ALT))
    return g


def mode_of(grid_name: str) -> str:
    return "n1decision" if grid_name == "n1decision" else "main"


def expand(g: list, B: int | None = None, mode: str = "main") -> list:
    """One task per replicate; ``B`` overrides the per-entry budget (pilot runs only)."""
    out = []
    for set_name, sc, n, t2c, b in g:
        for r in range(n):
            out.append((set_name, sc, r, t2c, B or b, mode))
    # interleave by priority block so early results cover every scenario of a block
    return out


def _path(out: Path, set_name: str, sc) -> Path:
    return out / set_name / f"{sc.key}.jsonl"


def done_reps(out: Path, set_name: str, sc) -> set:
    p = _path(out, set_name, sc)
    if not p.exists():
        return set()
    return {json.loads(line)["rep"] for line in p.read_text().splitlines() if line.strip()}


# ----------------------------------------------------------------------------- worker
_STATE = {}


def _init():
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[v] = "1"
    import warnings
    warnings.filterwarnings("ignore")


def _structures(set_name: str):
    from . import design
    from . import inference as I
    if set_name not in _STATE:
        S = I.build_structure(design.build(set_name))
        _STATE[set_name] = (S, SIM.build_truth(S))
    return _STATE[set_name]


def _work(task):
    set_name, sc, rep, t2c, B, mode = task
    S, T = _structures(set_name)
    Sd = Td = None
    if set_name != "development":
        Sd, Td = _structures("development")
    rec = SIM.run_replicate(S, T, sc, rep, task_seed(set_name, sc.key), B, Sd, Td, t2c=t2c, mode=mode)
    rec["pid"] = os.getpid()
    return set_name, asdict(sc), sc.key, rec


def run(out: Path, grid_name: str = "main", workers: int = 9, B: int | None = None, log=print,
        also_done: tuple = ()) -> dict:
    """``also_done``: earlier output directories whose stored replicates count as done (an extension run
    continues their seed sequence without duplicating them)."""
    import multiprocessing as mp

    out = Path(out)
    tasks = []
    for t in expand(grid(grid_name), B, mode_of(grid_name)):
        tasks.append(t)
    have = {}
    todo = []
    for t in tasks:
        k = (t[0], t[1].key)
        if k not in have:
            have[k] = done_reps(out, t[0], t[1]).union(*(done_reps(Path(o), t[0], t[1]) for o in also_done))
        if t[2] not in have[k]:
            todo.append(t)
    log(f"{len(tasks)} replicates in grid '{grid_name}', {len(todo)} to run, {workers} workers, B override={B}")
    t0 = time.time()
    n = 0
    ctx = mp.get_context("spawn")
    with ctx.Pool(workers, initializer=_init) as pool:
        for set_name, sc_dict, key, rec in pool.imap_unordered(_work, todo, chunksize=1):
            p = out / set_name / f"{key}.jsonl"
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("a") as f:
                f.write(json.dumps(rec, default=float) + "\n")
            n += 1
            if n % 50 == 0 or n == len(todo):
                el = time.time() - t0
                log(f"{n}/{len(todo)} done, {el / 3600:.2f} h elapsed, ETA {(len(todo) - n) * el / n / 3600:.2f} h")
    return dict(replicates=n, seconds=time.time() - t0)


# ----------------------------------------------------------------------------- closure phase (pre-Stage-2)
# Grids declared in docs/research/novel_method/closure/evidence/predeclared_rules.md before each run.
CLOSURE_NULLS_F = ("N0", "N1", "N1q", "N1c", "N1e")
CLOSURE_NULLS_ALL = ("N0", "N1", "N2", "N3", "N1q", "N1c", "N1e")
CLOSURE_TRUTHS = (("composite", ""), ("random", ""), ("logdens", ""), ("gaze", ""), ("validity", ""),
                  ("random", "random_indep"))


def closure_grid(name: str, degree: int = 1, chosen: str = "") -> list:
    """Closure grid entries: (set, Scenario, replicates, B, mode, kwargs). Sets run one after another."""
    S = SIM.Scenario
    g = []
    if name == "rf":                                   # rule R-F: temporal control
        for set_name, n in (("locked_pooled", 1000), ("locked_primary", 1000), ("development", 500)):
            g += [(set_name, S(n0), n, B_NULL, "rf", {}) for n0 in CLOSURE_NULLS_F]
            g += [(set_name, S("ALT", 1.5, 0.4, truth=t), 200, B_ALT, "rf", {}) for t in ("composite", "random")]
    elif name == "rg":                                 # rule R-G: parametrization at the chosen degree
        g += [("locked_pooled", S(n0), 1000, B_NULL, "rg", {}) for n0 in CLOSURE_NULLS_ALL]
        for o in (1.35, 1.5):
            g += [("locked_pooled", S("ALT", o, 0.4, truth=t, dev_truth=dt), 300, B_ALT, "rg", {}) for t, dt in CLOSURE_TRUTHS]
    elif name == "nh4":                                # rule R-I: NH4 attribution
        for set_name in ("locked_pooled", "locked_primary", "development"):
            g += [(set_name, S(n0), 500, B_NULL, "nh4", {}) for n0 in ("N4", "N0", "N3")]
            g += [(set_name, S("ALT", 1.5, 0.4, truth="gaze"), 200, B_ALT, "nh4", {})]
    elif name == "conf":                               # rule R-H: the selected design, full characterization
        kw_l = dict(chosen=chosen, cv_tests=("T1", "T2"), subs=("locked_primary", "locked_secondary"))
        g += [("locked_pooled", S(n0), 1000, B_NULL, "conf", kw_l) for n0 in CLOSURE_NULLS_ALL]
        kw_a = dict(chosen=chosen, subs=("locked_primary", "locked_secondary"))
        for o in OR_RHO04:
            for t in ("composite", "random"):
                g.append(("locked_pooled", S("ALT", o, 0.4, truth=t), 300, B_ALT, "conf", kw_a))
        for o in OR_RHO02:
            g.append(("locked_pooled", S("ALT", o, 0.2, truth="random"), 200, B_ALT, "conf", kw_a))
        for o in OR_RHO07:
            g.append(("locked_pooled", S("ALT", o, 0.7, truth="random"), 200, B_ALT, "conf", kw_a))
        for kw in (dict(sigma_q=0.0), dict(two_pl=True), dict(guessing=True), dict(hetero=True), dict(e5_factor=0.5),
                   dict(e5_factor=0.0)):
            g.append(("locked_pooled", S("ALT", 1.5, 0.4, truth="random", **kw), 200, B_ALT, "conf", kw_a))
        for kw in (dict(two_pl=True), dict(guessing=True)):
            g.append(("locked_pooled", S("N0", **kw), 500, B_NULL, "conf", kw_a))
        kw_d = dict(chosen=chosen, dev_stop=True)
        g += [("development", S(n0), 500, B_NULL, "conf", kw_d) for n0 in CLOSURE_NULLS_ALL]
        g += [("development", S("ALT", o, 0.4, truth="random"), 300, B_ALT, "conf", kw_d) for o in OR_RHO04]
    else:
        raise ValueError(name)
    return g


def closure_degrees(name: str, degree: int) -> tuple:
    return SIM.CLOSURE_DEGREES if name == "rf" else (degree,)


_CSTATE = {}


def _cstruct(set_name: str, degrees: tuple):
    from . import design
    from . import inference as I
    k = (set_name, degrees)
    if k not in _CSTATE:
        S = I.build_structure(design.build(set_name), degrees=degrees)
        _CSTATE[k] = (S, SIM.build_truth(S))
    return _CSTATE[k]


def _cwork(task):
    set_name, sc, rep, B, mode, kw, degree, degrees = task
    S, T = _cstruct(set_name, degrees)
    Sd = Td = None
    if mode == "rg":
        Sd, Td = _cstruct("development", degrees)
    subs = {s: _cstruct(s, degrees) for s in kw.get("subs", ())}
    rec = SIM.run_replicate_closure(S, T, sc, rep, task_seed(set_name, f"{mode}|{sc.key}"), B, mode, degree, Sd, Td,
                                    subs=subs, chosen=kw.get("chosen", ""), cv_tests=kw.get("cv_tests", ()),
                                    dev_stop=kw.get("dev_stop", False))
    rec["pid"] = os.getpid()
    return set_name, sc.key, rec


def run_closure(out: Path, name: str, degree: int = 1, chosen: str = "", workers: int = 8, log=print) -> dict:
    """Run a closure grid set by set (one structure per worker at a time keeps memory bounded); resumable."""
    import multiprocessing as mp

    out = Path(out)
    g = closure_grid(name, degree, chosen)
    degrees = closure_degrees(name, degree)
    total = 0
    t0 = time.time()
    for set_name in dict.fromkeys(e[0] for e in g):
        todo = []
        for s, sc, n, B, mode, kw in g:
            if s != set_name:
                continue
            have = done_reps(out, s, sc)
            todo += [(s, sc, r, B, mode, kw, degree, degrees) for r in range(n) if r not in have]
        log(f"{name}: set {set_name}: {len(todo)} replicates to run, {workers} workers")
        if not todo:
            continue
        ctx = mp.get_context("spawn")
        n_done = 0
        ts = time.time()
        with ctx.Pool(workers, initializer=_init) as pool:
            for s, key, rec in pool.imap_unordered(_cwork, todo, chunksize=1):
                p = out / s / f"{key}.jsonl"
                p.parent.mkdir(parents=True, exist_ok=True)
                with p.open("a") as f:
                    f.write(json.dumps(rec, default=float) + "\n")
                n_done += 1
                if n_done % 100 == 0 or n_done == len(todo):
                    el = time.time() - ts
                    log(f"{name}/{set_name}: {n_done}/{len(todo)} done, {el / 3600:.2f} h, "
                        f"ETA {(len(todo) - n_done) * el / n_done / 3600:.2f} h")
        total += n_done
    return dict(replicates=total, seconds=time.time() - t0)
