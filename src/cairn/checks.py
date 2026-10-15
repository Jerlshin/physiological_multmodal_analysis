"""Outcome-free self-checks behind ``python -m cairn verify`` (Stage-1 spec §3 leakage tests on real data).

Each check returns ``dict(passed=bool, ...)``. Nothing here reads a quiz outcome; the gate checks
confirm that the loader still refuses.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import gate
from .paths import ROOT, sha256_file
from .paths_stage1 import PROVISIONAL_ANCHORS

# Outcome-access logs at the Stage-0 entry (stage0/evidence/entry_sha256.txt); unchanged since G01-R/John.
ACCESS_LOGS = {
    "analysis_freeze/outcome_access_log.jsonl": "2ea691fa4243b7cdf7d2902b0beb8adec2d57c29b12dc63b8eeb5ee198c3d202",
    "docs/research/external_john2025/evidence/outcome_access_log.jsonl": "766489e7797f063842e11dc10a46b6b46ad6ba8fe97414ff796dce03770d11cd",
}
PROVISIONAL_ANCHORS_SHA256 = "69ce6c83b53c5b73571e57316175e243de39d899a190e20180a98a8afa7c0477"


def check_gate() -> dict:
    refused = {}
    for scope in gate.SCOPES:
        try:
            gate.load_authorization(scope)
            refused[scope] = False
        except gate.OutcomeAccessDenied:
            refused[scope] = True
    logs = {p: sha256_file(ROOT / p) == h for p, h in ACCESS_LOGS.items()}
    return dict(passed=all(refused.values()) and all(logs.values()) and not gate.FREEZE_RECORD.exists()
                and not gate.AUTHORIZATION.exists() and not gate.ACCESS_LOG.exists(),
                refused=refused, access_logs_unchanged=logs, cairn_access_log_exists=gate.ACCESS_LOG.exists())


def check_incidence() -> dict:
    from . import design
    out = {}
    for s in ("development", "locked_primary", "locked_secondary", "locked_pooled", "reserved_descriptive"):
        out[s] = design.build(s).summary()
    return dict(passed=True, sets=out)


def check_item_keys() -> dict:
    from . import item_keys
    m = item_keys.key_map()
    return dict(passed=len(m) == 203 and not m.duplicated(["experiment", "canonical_video_id", "item"]).any(),
                rows=len(m), matches=m.match.value_counts().to_dict())


def check_anchor_table() -> dict:
    h = sha256_file(PROVISIONAL_ANCHORS)
    return dict(passed=h == PROVISIONAL_ANCHORS_SHA256, sha256=h, status="PROVISIONAL (machine anchors; Stage-1 use only)")


def check_timeline() -> dict:
    from . import clock
    tab = clock.table()
    bad = n = 0
    for r in tab.itertuples():
        for t in np.arange(r.rec_start_s, r.rec_end_s) + 0.5:
            src, vs = clock.rec_to_source(r.canonical_video_id, t, tab)
            bad += abs(clock.source_to_rec(r.canonical_video_id, src, vs, tab) - t) > 1e-9
            n += 1
    return dict(passed=bad == 0, seconds=n, round_trip_failures=int(bad))


def check_fold_safety(set_name: str = "locked_primary") -> dict:
    """Learner independence, reference rule and normalization isolation on a real split."""
    from . import design
    from . import features as F
    from . import inference as I
    from .channels import load as load_series

    inc = design.build(set_name)
    S = I.build_structure(inc, reps=1, with_splits=True)
    res = {}
    # 1 learner independence: every row of a learner on one side of every split
    ok = True
    for sp in S.splits:
        tr = set(S.person[sp.train])
        te = set(S.person[sp.test])
        ok &= not (tr & te) and len(tr | te) == len(S.persons)
    res["learner_independence"] = bool(ok)
    # 2 reference rule (regime A): training learners only, never the target
    sp = S.splits[0]
    cells = inc.cells
    refs = F.regime_a_references(cells, sp.train_persons)
    people = dict(zip(cells.uid, cells.person))
    rr = all(people[u] in sp.train_persons and people[u] != people[c] for c, us in refs.items() for u in us)
    res["regime_A_reference_rule"] = bool(rr)
    rc = F.regime_c_references(cells, seed=0)
    half = F.regime_c_halves(cells.person, seed=0)
    res["regime_C_other_half_only"] = bool(all(half[people[u]] != half[people[c]] for c, us in rc.items() for u in us))
    # 3 normalization isolation: perturb one test learner's series; training statistics must not move
    test_person = sorted(set(S.persons[S.person[sp.test]]))[0]
    test_uids = set(cells[cells.person == test_person].uid)

    def perturbed(uid):
        a = load_series(uid)
        if uid in test_uids:
            a = a.copy()
            a[:2] = a[:2] * 3.0 + 500.0        # move gaze far away
            a[2] = 1.0 - a[2]                  # invert validity
        return a

    sc0 = F.compute_split(inc, sp.train_persons, cache=False)
    sc1 = F.compute_split(inc, sp.train_persons, load=perturbed, cache=False)
    same_stats = np.allclose(sc0.mu, sc1.mu) and np.allclose(sc0.sd, sc1.sd)
    same_train = True
    for v in inc.n_s:
        idx = [i for i, ci in enumerate(sc0.cell_index[v]) if cells.person.iloc[ci] in sp.train_persons]
        same_train &= np.array_equal(np.nan_to_num(sc0.arrays[v][idx], nan=-9), np.nan_to_num(sc1.arrays[v][idx], nan=-9))
    res["normalization_isolation"] = bool(same_stats and same_train)
    return dict(passed=all(res.values()), set=set_name, **res)


def check_identity_probe(set_name: str = "development", n_perm: int = 19) -> dict:
    """Video identity from item-centred moment terms on training rows of one split (chance expected)."""
    from . import design
    from . import features as F
    from . import inference as I

    inc = design.build(set_name)
    S = I.build_structure(inc, reps=1)
    sp = S.splits[0]
    x = F.moment_regressors(sp.mb_dt.m, S.anch_cell, S.anch_item, sp.anch_train)
    tr = sp.anch_train
    r = F.identity_probe(x[tr], S.anch_video[tr], S.person[S.anch_index][tr], n_perm=n_perm)
    return dict(passed=r["at_chance"], **r)


def check_determinism() -> dict:
    from . import design
    from . import inference as I
    from . import simulate as SIM

    S = I.build_structure(design.build("locked_primary"))
    T = SIM.build_truth(S)
    sc = SIM.Scenario("ALT", 1.35, 0.4)
    a = SIM.run_replicate(S, T, sc, 3, 99, 3, S, T, mode="n1decision")
    b = SIM.run_replicate(S, T, sc, 3, 99, 3, S, T, mode="n1decision")
    keys = [k for k in a if k != "seconds"]
    same = all((a[k] == b[k]) or (isinstance(a[k], float) and np.isnan(a[k]) and np.isnan(b[k])) for k in keys)
    return dict(passed=bool(same), compared=len(keys))


def run_all(quick: bool = False) -> dict:
    checks = dict(gate=check_gate, incidence=check_incidence, item_keys=check_item_keys, anchor_table=check_anchor_table,
                  timeline_round_trip=check_timeline, fold_safety=check_fold_safety)
    if not quick:
        checks.update(identity_probe=check_identity_probe, determinism=check_determinism)
    out = {}
    for k, f in checks.items():
        try:
            out[k] = f()
        except Exception as e:                       # report, do not hide
            out[k] = dict(passed=False, error=f"{type(e).__name__}: {e}")
    out["passed"] = all(v["passed"] for v in out.values())
    return out
