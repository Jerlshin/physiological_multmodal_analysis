"""Closure rule R-K: outcome-free validation of the strong baselines (run in .venv-cairn-ml).

Real incidence, real per-second signals and provisional anchors; **synthetic outcomes only** (cairn.simulate).
For each replicate, every baseline is fitted on the training rows of each of the 5 learner-grouped folds (R = 1)
and scored on the held-out learners against IRT-M2:

* S_item = 1 - LL(model) / LL(IRT-M2), person-balanced held-out item log-loss skill;
* dAUC_wp, the within-learner x video AUC increment.

Scenarios (rule R-K):

* N0, pure null: negative control (no baseline may show positive skill beyond Monte Carlo noise);
* N2, outcomes depend on person-level whole-video engagement: positive control for whole-video learners;
* ALT, OR 3 at rho = .7 (anchored moment effect): positive control for anchored / learned-pooling learners.

``checks`` mode: determinism (identical refit) and fold safety (perturbing one held-out learner's signals leaves
every other held-out prediction bit-identical) for every baseline on one split.

    python baseline_validation.py run <out_dir> <set> <scenario> <first_rep> <n_reps>
    python baseline_validation.py checks <out_dir>
"""
from __future__ import annotations

import json
import os
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import numpy as np  # noqa: E402
import torch  # noqa: E402

torch.set_num_threads(1)                      # one core per process: the decisive simulations keep the machine
torch.set_num_interop_threads(1)

from cairn import baselines as BL  # noqa: E402
from cairn import baselines_ml as ML  # noqa: E402
from cairn import design  # noqa: E402
from cairn import inference as I  # noqa: E402
from cairn import simulate as SIM  # noqa: E402
from cairn.model import log_loss  # noqa: E402

SCENARIOS = {"N0": SIM.Scenario("N0"), "N2": SIM.Scenario("N2"), "ALT3": SIM.Scenario("ALT", 3.0, 0.7),
             # post hoc functional check (added after the N2 results): a strong person-level link, r = .9
             "N2s": SIM.Scenario("N2", n2_r=0.9)}
BASE_SEED = 20261014


def references():
    return {"IRT-whole (B5)": BL.GLMM(I.WHOLE), "CAIRN-linear-dt (B6)": BL.GLMM(I.CL6_DT), "B9-Lalle": BL.LalleB9()}


def run(out: Path, set_name: str, scen: str, first: int, n: int, only: str = "") -> None:
    S = I.build_structure(design.build(set_name), reps=1)
    T = SIM.build_truth(S)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{set_name}_{scen}{'_' + only if only else ''}.jsonl"
    done = {json.loads(line)["rep"] for line in path.read_text().splitlines()} if path.exists() else set()
    cell_person = S.inc.cells.person.map({p: i for i, p in enumerate(S.persons)}).to_numpy()
    for rep in range(first, first + n):
        if rep in done:
            continue
        rng = np.random.default_rng(np.random.SeedSequence([BASE_SEED, rep, sum(map(ord, scen + set_name))]))
        y, info = SIM.generate(S, T, SCENARIOS[scen], rep, rng)
        models = {**references(), **ML.ml_ladder()}
        if only:                                      # a subset (comma-separated name fragments)
            models = {k: v for k, v in models.items() if any(o in k for o in only.split(","))}
        ll = {k: np.zeros(S.n) for k in ["IRT-M2"] + list(models)}
        pp = {k: np.zeros(S.n) for k in ll}
        secs = {k: 0.0 for k in models}
        npar = {}
        for sp in S.splits:
            ytr = np.where(sp.train, y, np.nan)
            data = BL.ItemData(S, sp, ytr)
            te = sp.test
            pb = BL.GLMM(I.BASE).fit(data).predict_proba(data)
            ll["IRT-M2"][te], pp["IRT-M2"][te] = log_loss(y[te], pb), pb
            for name, m in models.items():
                t0 = time.time()
                p = m.fit(data).predict_proba(data)
                secs[name] += time.time() - t0
                ll[name][te], pp[name][te] = log_loss(y[te], p), p
                npar[name] = m.n_params()
        lb = I.person_balanced(ll["IRT-M2"], S.person)
        rec = dict(set=set_name, scenario=scen, rep=rep, **info)
        for name in models:
            rec[f"{name}|s_item"] = 1 - I.person_balanced(ll[name], S.person) / lb
            rec[f"{name}|d_auc_wp"] = I.delta_auc_wp(y, pp[name], pp["IRT-M2"], S.cell, cell_person)
            rec[f"{name}|seconds"] = secs[name]
            rec[f"{name}|n_params"] = npar[name]
        with path.open("a") as f:
            f.write(json.dumps(rec, default=float) + "\n")
        print(f"{set_name} {scen} rep {rep} done", flush=True)


def _perturbing_loader(target_uids: set):
    from cairn.channels import load

    def loader(uid):
        a = load(uid)
        if uid in target_uids:
            a = a.copy()
            a[:2] = a[:2] * 3.0 + 500.0
            a[2] = 1.0 - a[2]
        return a
    return loader


def checks(out: Path, set_name: str = "locked_pooled", only: str = "") -> None:
    """Determinism and fold safety of every baseline on split 0 (synthetic ALT outcomes)."""
    from cairn import features as F

    S = I.build_structure(design.build(set_name), reps=1)
    T = SIM.build_truth(S)
    y, _ = SIM.generate(S, T, SCENARIOS["ALT3"], 0, np.random.default_rng(7))
    sp = S.splits[0]
    data = BL.ItemData(S, sp, np.where(sp.train, y, np.nan))
    test_people = sorted(set(S.persons[S.person[sp.test]]))
    victim = test_people[0]
    victim_uids = set(S.inc.cells[S.inc.cells.person == victim].uid)
    others = np.flatnonzero(sp.test)
    keep = S.person[others] != list(S.persons).index(victim)

    def predict_all(perturb: bool):
        ML._SC_CACHE.clear()
        ML._REL_CACHE.clear()
        if perturb:
            ML._SC_CACHE[(S.inc.set_name, sp.train_persons)] = F.compute_split(
                S.inc, sp.train_persons, load=_perturbing_loader(victim_uids), cache=False)
        return {name: m.fit(data).predict_proba(data) for name, m in ML.ml_ladder().items() if only in name}

    a, b, c = predict_all(False), predict_all(False), predict_all(True)
    res = {}
    for name in a:
        res[name] = dict(deterministic=bool(np.array_equal(a[name], b[name])),
                         fold_safe=bool(np.array_equal(a[name][keep], c[name][keep])),
                         victim_rows_changed=bool(not np.array_equal(a[name][~keep], c[name][~keep])),
                         max_abs_diff_other_learners=float(np.max(np.abs(a[name][keep] - c[name][keep]))))
    out.mkdir(parents=True, exist_ok=True)
    (out / f"checks{'_' + only if only else ''}.json").write_text(json.dumps(dict(set=set_name, split=0,
                                                                              perturbed_learner=str(victim), results=res), indent=2))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "run":
        run(Path(sys.argv[2]), sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6]), *(sys.argv[7:8]))
    elif mode == "checks":
        checks(Path(sys.argv[2]), only=sys.argv[3] if len(sys.argv) > 3 else "")
    else:
        raise SystemExit(__doc__)
