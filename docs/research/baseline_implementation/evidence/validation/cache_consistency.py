"""Consistency of the outcome-free derived caches with the frozen code (freeze finalization, 2026-10-05).

The confirmatory run reuses two disk caches that earlier pipeline runs wrote:

* ``data/derived/g01r/corrca_stats``: exact CorrCA sufficient statistics per experiment x video unit;
* ``data/derived/g01r/syn_cache``: synchrony features per reference plan.

Most entries were written before the last edit of ``src/g01r/features/synchrony.py``, made shortly
before the freeze manifest was first built. This script recomputes them with the frozen code and
compares bit for bit:

1. every CorrCA unit of every cached set and route, recomputed into a temporary directory;
2. every regime-A outer split of PAS-core (processed route, R x K plans), the plans behind the H1/H2
   point estimates, permutation tests and futility bound;
3. a seeded random sample of the cached nested-CV plans of the primary comparison (M2 vs M5);
4. a seeded random sample of cached outer splits for every other regime-A set and route.

Synchrony is recomputed with the disk cache disabled. No outcome is read. Usage::

    PYTHONPATH=src .venv/bin/python docs/research/baseline_implementation/evidence/validation/cache_consistency.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

import g01r.config as C
from g01r import references as R
from g01r.config import CONFIG_PATH, IMPL_EVIDENCE, load_config
from g01r.design import SYN_BLOCKS, FeatureProvider, plan_key
from g01r.population import AnalysisSet, Population
from g01r.rng import rng_for
from g01r.splits import outer_folds, person_folds

BLOCKS = ("eeg", "hr", "gaze", "pupil")
N_NESTED = 100
N_OTHER = 20
OTHER_A = [("PAS_E34_core", "raw"), ("PAS_E34_four", "processed"), ("PAS_E34_core_eye30", "processed"),
           ("PAS_E34_core_eye70", "processed"), ("PAS_E34_core_alpha30", "processed"), ("E5_core", "processed"),
           ("E1_gaze", "processed")]
COLS = ["experiment", "participant_id", "qualified_participant_id", "session", "local_stimulus_id",
        "canonical_video_id", "condition", "exposure_number"]


def aset_for(pop: Population, name: str) -> AnalysisSet:
    if "+" in name:                                   # transport union, as built in analysis.run_transport_analysis
        a, b = name.split("+")
        return AnalysisSet(name, pop.cells[pop.cells[a] | pop.cells[b]][COLS].reset_index(drop=True))
    return pop.analysis_set(name)


def check_corrca(cfg, pop) -> dict:
    root = C.DERIVED / "corrca_stats"
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for set_dir in sorted(root.iterdir()):
            for route_dir in sorted(set_dir.iterdir()):
                engine = FeatureProvider(cfg, aset_for(pop, set_dir.name), route_dir.name).engine
                saved, C.DERIVED = C.DERIVED, Path(tmp)       # CorrCAStats resolves DERIVED at call time
                try:
                    engine.corrca
                finally:
                    C.DERIVED = saved
                fresh = Path(tmp) / "corrca_stats" / set_dir.name / route_dir.name
                for f in sorted(route_dir.glob("*.npy")):
                    g = fresh / f.name
                    same = g.exists() and np.array_equal(np.load(f, mmap_mode="r"), np.load(g, mmap_mode="r"))
                    rows.append(dict(set=set_dir.name, route=route_dir.name, unit=f.name, bit_identical=bool(same)))
                for g in fresh.glob("*.npy"):
                    g.unlink()
    return dict(units=len(rows), bit_identical=sum(r["bit_identical"] for r in rows),
                mismatches=[r for r in rows if not r["bit_identical"]])


def compare_plans(prov: FeatureProvider, plans: list) -> dict:
    paths = [prov._cache_path(plan_key(p, prov.route, prov.aset.name) + "|" + ",".join(BLOCKS)) for p in plans]
    keep = [i for i, p in enumerate(paths) if p.exists()]
    prov.syn_disk_cache = False
    ok, worst, bad = 0, 0.0, []
    for s in range(0, len(keep), 50):
        chunk = keep[s:s + 50]
        for i, frame in zip(chunk, prov.engine.compute_many([plans[i] for i in chunk], BLOCKS)):
            for block, cols in SYN_BLOCKS.items():
                frame[f"{block}_missing"] = frame[cols].isna().any(axis=1).astype(float)
            a = pd.read_parquet(paths[i])[frame.columns].to_numpy(float)
            b = frame.to_numpy(float)
            if np.array_equal(a, b, equal_nan=True):
                ok += 1
            else:
                bad.append(paths[i].name)
                worst = max(worst, float(np.nanmax(np.abs(a - b))))
    return dict(requested=len(plans), cached=len(keep), bit_identical=ok, worst_abs_diff=worst, mismatches=bad[:20])


def outer_plans(cfg, aset) -> list:
    K, RA = cfg.resampling["outer_folds_A"], cfg.resampling["reps_A"]
    folds = outer_folds(aset, K, RA, cfg.resampling["base_seed"], aset.name, "A")
    return [R.regime_A(aset, folds[r][aset.person] != k, np.ones(aset.n, bool)) for r in range(RA) for k in range(K)]


def nested_plans(cfg, aset, base="M2", full="M5") -> list:
    """The plans prefetched by analysis._task_ncv for every nested repetition."""
    K = cfg.resampling["outer_folds_A"]
    plans = []
    for rep in range(cfg.inference["ncv_reps"]):
        f = person_folds(aset.exp_of_person, K, rng_for(cfg.resampling["base_seed"], aset.name, base, full, "ncv", rep))
        f = f[aset.person]
        for k in range(K):
            trn = f != k
            plans += [R.regime_A(aset, trn & ~(f == j), trn) for j in range(K) if j != k]
            plans.append(R.regime_A(aset, trn, np.ones(aset.n, bool)))
    return plans


def cached_sample(prov, plans, n, seed_label) -> list:
    cached = [p for p in plans if prov._cache_path(plan_key(p, prov.route, prov.aset.name) + "|" + ",".join(BLOCKS)).exists()]
    rng = rng_for(20261004, "cache_consistency", seed_label)
    return [cached[i] for i in sorted(rng.choice(len(cached), size=min(n, len(cached)), replace=False))] if cached else []


def main():
    t0 = time.time()
    cfg = load_config(CONFIG_PATH)
    pop = Population(cfg)
    out = dict(created_utc=datetime.now(timezone.utc).isoformat(), outcomes_read=False)
    out["corrca_stats"] = check_corrca(cfg, pop)
    print("corrca", out["corrca_stats"]["bit_identical"], "/", out["corrca_stats"]["units"], flush=True)

    core = FeatureProvider(cfg, pop.analysis_set("PAS_E34_core"), "processed")
    out["PAS_E34_core_processed_outer_all"] = compare_plans(core, outer_plans(cfg, core.aset))
    print("outer", out["PAS_E34_core_processed_outer_all"], flush=True)
    core = FeatureProvider(cfg, pop.analysis_set("PAS_E34_core"), "processed")
    out["PAS_E34_core_processed_nested_M2_M5_sample"] = compare_plans(
        core, cached_sample(core, nested_plans(cfg, core.aset), N_NESTED, "nested"))
    print("nested", out["PAS_E34_core_processed_nested_M2_M5_sample"], flush=True)
    out["other_regime_A_outer_sample"] = {}
    for name, route in OTHER_A:
        prov = FeatureProvider(cfg, pop.analysis_set(name), route)
        out["other_regime_A_outer_sample"][f"{name}|{route}"] = res = compare_plans(
            prov, cached_sample(prov, outer_plans(cfg, prov.aset), N_OTHER, f"{name}|{route}"))
        print(name, route, res, flush=True)

    syn_root = C.DERIVED / "syn_cache"
    total = sum(1 for _ in syn_root.rglob("*.parquet"))
    checked = [out["PAS_E34_core_processed_outer_all"], out["PAS_E34_core_processed_nested_M2_M5_sample"],
               *out["other_regime_A_outer_sample"].values()]
    out["syn_cache_entries_total"] = total
    out["syn_cache_entries_checked"] = sum(c["cached"] for c in checked)
    out["all_bit_identical"] = (out["corrca_stats"]["bit_identical"] == out["corrca_stats"]["units"]
                                and all(c["bit_identical"] == c["cached"] for c in checked))
    out["elapsed_s"] = time.time() - t0
    path = IMPL_EVIDENCE / "validation" / "cache_consistency.json"
    path.write_text(json.dumps(out, indent=1) + "\n")
    print("ALL BIT-IDENTICAL" if out["all_bit_identical"] else "MISMATCH", "->", path)
    sys.exit(0 if out["all_bit_identical"] else 1)


if __name__ == "__main__":
    main()
