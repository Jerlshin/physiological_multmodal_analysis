"""Stage-2 development analysis (plan §23 Stage 2, §12.4, §16-§17, §20.5; closure development analysis plan DAP-1).

One entry point, two outcome sources and otherwise **one code path**:

* ``source="gated"``: exact-set item correctness through :func:`cairn.gate.load_item_outcomes` (scope
  ``development``; refuses without a verified CAIRN freeze and a user authorization; logs the access), mapped to
  the incidence rows through :func:`cairn.item_keys.verify_item_table`;
* ``source="synthetic"``: outcomes from :func:`cairn.simulate.generate` under a declared scenario (dry run). A dry
  run never calls the gate and refuses to write inside ``analysis_freeze_cairn`` or the results directory of a real
  run; every output is labelled SYNTHETIC.

Steps (DAP-1, fixed in the closure phase; ``docs/research/novel_method/closure/development_analysis_plan.md``):

1. manifest first (hash-bound inputs, design configuration, frozen anchor table);
2. outcomes (one logged gate access);
3. kernel selection over ``design.KERNEL_GRID`` (12 configurations): repetition-level CV S_item of the primary; the
   simplest kernel within one standard error of the best (plan §12.4) is selected and frozen for the lock;
4. development tests of the primary at the selected kernel: LR T1/T2/T2c (confirmatory statistic, exploratory here),
   CV T1/T2 (fallback statistic), usefulness metrics with the nested-CV interval;
5. stop rule (plan §20.5): go iff CV T2 p < .10 and CV dAUC_wp >= .01 (the construct check passed in Stage 0);
6. ladder (numpy side): B0 video mean, IRT-0, IRT-M2, IRT-whole, B9 Lallé, CAIRN parametrizations; ablations:
   validity-only, gaze-only, gaze given validity (NH4 attribution), raw (no detrend) form, P6 / PT / P0;
7. report (JSON + Markdown) and ``selections.json`` (kernel, go/stop) for the lock freeze.

The ML baselines (B3, B4a, B4b, B7) run through :func:`run_ml` in ``.venv-cairn-ml`` on the same folds, with their own
logged gate access.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from . import design
from . import features as F
from . import gate
from . import inference as I
from . import manifest as MF
from .paths import ROOT, sha256_file

SIMPLICITY = sorted(design.KERNEL_GRID, key=lambda k: (k[1], abs(k[0]), k[0]))   # hard span first, then narrow


class DryRunViolation(RuntimeError):
    pass


def load_config(path: Path) -> dict:
    cfg = json.loads(Path(path).read_text())
    for k in ("parametrization", "detrend_degree", "statistic", "B_lock", "R_lock"):
        if k not in cfg:
            raise ValueError(f"design configuration lacks '{k}'")
    return cfg


def primary_variant(cfg: dict) -> I.Variant:
    d = int(cfg["detrend_degree"])
    return {"P6": I.six_variant, "PT": I.aniso_variant, "P0": I.unit_variant}[cfg["parametrization"]](d)


# ----------------------------------------------------------------------------- outcomes
def gated_outcomes(S: I.SetStructure, purpose: str) -> np.ndarray:
    """Exact-set correctness for every row of S (raises unless frozen + authorized; the access is logged)."""
    from . import item_keys
    t = gate.load_item_outcomes("development", purpose)
    t = item_keys.verify_item_table(t)
    key = {(p, v, int(j)): float(c) for p, v, j, c in zip(t.qualified_participant_id, t.canonical_video_id, t.item,
                                                           t.recomputed_exact_correct)}
    rows = S.inc.rows
    y = np.array([key.get((p, v, int(j)), np.nan) for p, v, j in zip(rows.person, rows.video, rows.item)])
    if np.isnan(y).any():
        raise AssertionError(f"{int(np.isnan(y).sum())} incidence rows have no outcome")
    return y


def synthetic_outcomes(S: I.SetStructure, scenario: dict, seed: int) -> np.ndarray:
    from . import simulate as SIM
    T = SIM.build_truth(S)
    sc = SIM.Scenario(**scenario)
    rng = np.random.default_rng(seed)
    w = SIM.random_direction(np.random.default_rng(seed + 1), T.sign) if sc.truth == "random" else None
    y, _ = SIM.generate(S, T, sc, 0, rng, w_truth=w)
    return y


# ----------------------------------------------------------------------------- kernel selection
def per_rep_skill(S: I.SetStructure, y: np.ndarray, var: I.Variant) -> np.ndarray:
    """Person-balanced held-out S_item of ``var`` over IRT-M2, one value per CV repetition."""
    out = []
    for r in sorted({sp.rep for sp in S.splits}):
        sub = [sp for sp in S.splits if sp.rep == r]
        S_r = I.SetStructure(**{**S.__dict__, "splits": sub})
        cv = I.cv_evaluate(S_r, y, [var])
        out.append(I.summarize(S_r, y, cv, var.name)["s_item"])
    return np.array(out)


def select_kernel(set_name: str, anchors: Path, y: np.ndarray, var: I.Variant, R: int, log=print) -> dict:
    rows = []
    for k in design.KERNEL_GRID:
        S = I.build_structure(design.build(set_name, anchors_path=anchors, provisional=False, kernel=k), reps=R,
                              degrees=(var.degree,))
        sk = per_rep_skill(S, y, var)
        rows.append(dict(kernel=list(k), mean=float(sk.mean()), se=float(sk.std(ddof=1) / np.sqrt(len(sk)))))
        log(f"kernel {k}: S_item {sk.mean():+.4f} (SE {rows[-1]['se']:.4f})")
    best = max(rows, key=lambda r: r["mean"])
    thr = best["mean"] - best["se"]
    by = {tuple(r["kernel"]): r for r in rows}
    chosen = next(k for k in SIMPLICITY if by[k]["mean"] >= thr)
    return dict(table=rows, best=best["kernel"], threshold=thr, selected=list(chosen),
                rule="simplest kernel within one SE of the best mean repetition-level S_item (plan §12.4)")


# ----------------------------------------------------------------------------- the run
def _guard_dry_run(out: Path):
    out = Path(out).resolve()
    for forbidden in (gate.FREEZE_DIR.resolve(), (ROOT / "results").resolve()):
        if forbidden == out or forbidden in out.parents:
            raise DryRunViolation(f"a synthetic dry run may not write under {forbidden}")


def run_development(out: Path, config: Path, anchors: Path, source: str = "gated", scenario: dict | None = None,
                    seed: int = 0, B: int | None = None, R: int | None = None, kernels: bool = True, log=print) -> dict:
    out = Path(out)
    if source == "synthetic":
        _guard_dry_run(out)
    elif source != "gated":
        raise ValueError(source)
    if source == "gated":
        gate.load_authorization("development")          # fail fast, before anything is written
    cfg = load_config(config)
    B = int(B or cfg["B_lock"])
    R = int(R or cfg["R_lock"])
    var = primary_variant(cfg)
    out.mkdir(parents=True, exist_ok=True)
    m = MF.build(run_id=f"stage2-development-{source}", stage="2-development", sets=["development"], regime="A",
                 models=[var.name, "IRT-M2", "IRT-whole", "B9", "ablations"], grid=dict(kernels=[list(k) for k in design.KERNEL_GRID]),
                 cv=dict(outer="learner-grouped, experiment-stratified 5-fold", repetitions=R),
                 inference=dict(B=B, alpha=0.05), seeds=dict(cv=list(range(R)), perm=seed),
                 outcome_access=("gate.load_item_outcomes(scope=development)" if source == "gated"
                                 else f"none: SYNTHETIC dry run {scenario}"),
                 anchor_table=anchors, anchor_freeze_sha256=None if source == "synthetic" else
                 json.loads(gate.FREEZE_RECORD.read_text()).get("anchor_freeze_sha256"),
                 extra=dict(design_config=str(config), design_config_sha256=sha256_file(config), source=source))
    mh = MF.write(m, out / "MANIFEST.json")
    log(f"manifest {mh}")
    t0 = time.time()
    inc = design.build("development", anchors_path=anchors, provisional=(source == "synthetic"))
    S0 = I.build_structure(inc, reps=R, degrees=(0, var.degree) if var.degree else (0,))
    if source == "gated":
        y = gated_outcomes(S0, purpose=f"Stage-2 development analysis, manifest {mh}")
    else:
        y = synthetic_outcomes(S0, scenario or dict(name="ALT", odds_ratio=2.0, rho=0.7, truth="random"), seed)
    rep = dict(source=source, synthetic=source == "synthetic", manifest_sha256=mh, primary=var.name,
               started_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"), n_rows=int(S0.n),
               accuracy=float(np.mean(y)))
    # 3 kernel selection
    if kernels:
        ks = select_kernel("development", anchors, y, var, R, log)
    else:
        ks = dict(selected=[0.0, 0.0], rule="not run (kernel fixed at the hard span)", table=[])
    rep["kernel_selection"] = ks
    kernel = tuple(ks["selected"])
    S = I.build_structure(design.build("development", anchors_path=anchors, provisional=(source == "synthetic"),
                                       kernel=kernel), reps=R, degrees=tuple(sorted({0, 1, var.degree})))
    rng = np.random.default_rng(seed + 17)
    # 4 tests and usefulness of the primary
    ablate = [I.WHOLE, var, I.six_variant(var.degree), I.aniso_variant(var.degree), I.unit_variant(var.degree),
              I.CL6, I.Variant(f"CAIRN-validity-dt{var.degree}", channels=(F.PRIMARY.index("loss_long"),), person_anch=True,
                               detrend=True, trend=var.degree),
              I.Variant(f"CAIRN-gaze-dt{var.degree}", channels=tuple(F.PRIMARY.index(c) for c in F.GAZE), person_anch=True,
                        detrend=True, trend=var.degree)]
    ablate = list({v.name: v for v in ablate}.values())
    cv = I.cv_evaluate(S, y, ablate)
    rep["metrics"] = {v.name: I.summarize(S, y, cv, v.name) for v in ablate}
    rep["tests_lr"] = I.lr_tests_joint(S, y, [var], B, rng, ("T1lr", "T2lr", "T2clr"))
    rep["tests_cv"] = I.run_tests(S, y, cv, var, B, rng, ("T1", "T2"))
    rep["nh4_attribution"] = I.lr_tests_joint(S, y, [I.gaze_given_validity_variant(var.degree)], B, rng, ("T1lr", "T2lr"))
    rep["nested_cv"] = I.nested_cv(S, y, var, cv=cv, reps=1)
    if var.direction is not None:
        rep["lambda_hat"] = I.lambda_hat(S, y, var)
    from .simulate import b9_cv
    rep["metrics"]["B9-Lalle"] = dict(s_item=1 - I.person_balanced(b9_cv(S, y), S.person) / I.person_balanced(cv.ll_base, S.person))
    # 5 stop rule
    m_p = rep["metrics"][var.name]
    rep["stop_rule"] = dict(p_T2_cv=rep["tests_cv"]["T2"], d_auc_wp=m_p["d_auc_wp"], construct_check="passed (Stage 0, AUC .89)",
                            go=bool(rep["tests_cv"]["T2"] < 0.10 and m_p["d_auc_wp"] >= 0.01))
    rep["seconds"] = time.time() - t0
    rep["finished_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (out / "development_report.json").write_text(json.dumps(rep, indent=2, default=float))
    sel = dict(kernel=list(kernel), primary=var.name, go=rep["stop_rule"]["go"], manifest_sha256=mh,
               synthetic=source == "synthetic", strongest_baseline=None,
               note="strongest_baseline is filled from the ML-baseline run (run_ml) and the numpy ladder, by best S_item")
    (out / "selections.json").write_text(json.dumps(sel, indent=2))
    log(f"done in {rep['seconds'] / 60:.1f} min; go={sel['go']}")
    return rep


def run_ml(out: Path, anchors: Path, kernel: tuple, source: str = "gated", scenario: dict | None = None, seed: int = 0,
           R: int = 3, log=print) -> dict:
    """ML baselines (B3, B4a, B4b, B7) on the development folds; run in ``.venv-cairn-ml``."""
    from . import baselines as BL
    from . import baselines_ml as ML
    from .model import log_loss
    out = Path(out)
    if source == "synthetic":
        _guard_dry_run(out)
    out.mkdir(parents=True, exist_ok=True)
    S = I.build_structure(design.build("development", anchors_path=anchors, provisional=(source == "synthetic"),
                                       kernel=tuple(kernel)), reps=R)
    y = gated_outcomes(S, "Stage-2 development ML baselines") if source == "gated" else \
        synthetic_outcomes(S, scenario or dict(name="ALT", odds_ratio=2.0, rho=0.7, truth="random"), seed)
    models = ML.ml_ladder()
    ll = {k: np.zeros(S.n) for k in ["IRT-M2", *models]}
    pp = {k: np.zeros(S.n) for k in ll}
    cnt = np.zeros(S.n)
    for sp in S.splits:
        data = BL.ItemData(S, sp, np.where(sp.train, y, np.nan))
        te = sp.test
        p = BL.GLMM(I.BASE).fit(data).predict_proba(data)
        ll["IRT-M2"][te] += log_loss(y[te], p)
        pp["IRT-M2"][te] += p
        for name, mdl in models.items():
            p = mdl.fit(data).predict_proba(data)
            ll[name][te] += log_loss(y[te], p)
            pp[name][te] += p
        cnt[te] += 1
        log(f"split {sp.rep}/{sp.fold} done")
    cell_person = S.inc.cells.person.map({p: i for i, p in enumerate(S.persons)}).to_numpy()
    lb = I.person_balanced(ll["IRT-M2"] / cnt, S.person)
    res = {name: dict(s_item=1 - I.person_balanced(ll[name] / cnt, S.person) / lb,
                      d_auc_wp=I.delta_auc_wp(y, pp[name] / cnt, pp["IRT-M2"] / cnt, S.cell, cell_person))
           for name in models}
    rep = dict(source=source, synthetic=source == "synthetic", kernel=list(kernel), R=R, results=res)
    (out / "development_ml_report.json").write_text(json.dumps(rep, indent=2, default=float))
    return rep


def select_strongest(dev_report: dict, ml_report: dict | None) -> dict:
    """The strongest competing baseline for NH3 (plan §16): the non-CAIRN model with the highest development S_item
    among IRT-whole (B5), B9 and the ML baselines (B3, B4a-video, B4b, item-level boosting). CAIRN variants and the
    anchored FM / TCN front ends (ablation A4) are excluded: they are CAIRN with another representation."""
    cands = {"IRT-whole (B5)": dev_report["metrics"]["IRT-whole"]["s_item"], "B9-Lalle": dev_report["metrics"]["B9-Lalle"]["s_item"]}
    for name, r in (ml_report or {}).get("results", {}).items():
        if "anchored" in name or name.startswith("B7"):
            continue
        cands[name] = r["s_item"]
    best = max(cands, key=cands.get)
    return dict(strongest_baseline=best, s_item=cands[best], candidates=cands)
