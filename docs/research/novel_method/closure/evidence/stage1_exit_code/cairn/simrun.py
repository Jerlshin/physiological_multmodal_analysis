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
