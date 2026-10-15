"""Stage-4 locked evaluation (plan §23 Stage 4; closure rule R-H). Inert until Stage 3: the gate requires a lock-stage
freeze record and an authorization naming both locked scopes and the CAIRN preregistration URL.

Procedure (frozen in ``design_config.json``; the same functions were validated on synthetic outcomes in the closure
simulations, ``simulate.run_replicate_closure(mode="conf")``):

1. **H_pool** (no moment effect in E4 or E5): NH1 = T1 AND T2 on the pooled E4 + E5 lock with the frozen statistic
   (LR by default; CV if the fallback was frozen), parametrization, detrend degree and development-selected kernel;
   B = 999 each; one-sided alpha = .05.
2. **Closed testing:** only if H_pool is rejected, NH1 on E4 alone and on E5 alone, each at alpha = .05, with the
   identical procedure on the cohort's own rows (strong FWER control at .05 over the three claims).
3. **Heterogeneity (descriptive):** lambda-hat in E4 and in E5 with model-based intervals (1-df forms).
4. **Usefulness:** CV S_item and dAUC_wp (R = 10) pooled and per cohort, nested-CV interval; thresholds unchanged.
5. **Outcome category** (plan §20.4) is reported from 1-4.

``source="synthetic"`` runs the identical code on generated outcomes (dry run; no gate call).
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from . import design
from . import gate
from . import inference as I
from . import manifest as MF
from .paths import sha256_file
from .stage2 import DryRunViolation, _guard_dry_run, load_config, primary_variant, synthetic_outcomes

ALPHA = 0.05
LOCK_SCOPES = ("locked_primary", "locked_secondary")


def gated_lock_outcomes(S: I.SetStructure, purpose: str) -> np.ndarray:
    from . import item_keys
    key = {}
    for scope in LOCK_SCOPES:
        t = item_keys.verify_item_table(gate.load_item_outcomes(scope, purpose))
        key.update({(p, v, int(j)): float(c) for p, v, j, c in zip(t.qualified_participant_id, t.canonical_video_id,
                                                                     t.item, t.recomputed_exact_correct)})
    rows = S.inc.rows
    y = np.array([key.get((p, v, int(j)), np.nan) for p, v, j in zip(rows.person, rows.video, rows.item)])
    if np.isnan(y).any():
        raise AssertionError(f"{int(np.isnan(y).sum())} locked incidence rows have no outcome")
    return y


def nh1(S: I.SetStructure, y: np.ndarray, var: I.Variant, statistic: str, B: int, rng) -> dict:
    if statistic == "LR":
        r = I.lr_tests_joint(S, y, [var], B, rng, ("T1lr", "T2lr", "T2clr"))
        p1, p2 = r[f"{var.name}|p_T1lr"], r[f"{var.name}|p_T2lr"]
    else:
        cv = I.cv_evaluate(S, y, [var])
        r = I.run_tests(S, y, cv, var, B, rng, ("T1", "T2", "T2c"))
        p1, p2 = r["T1"], r["T2"]
    return dict(tests=r, p_T1=p1, p_T2=p2, p_NH1=max(p1, p2), reject=bool(max(p1, p2) <= ALPHA))


def category(pooled_reject: bool, s_item: float, d_auc: float, futility_excludes: bool) -> str:
    """Plan §20.4 categories (video-level NH2 and external replication are added in the report)."""
    if pooled_reject and s_item >= 0.01 and d_auc >= 0.02:
        return "item-level success (NH2 and external replication decide 'strong')"
    if pooled_reject:
        return "weak (detectable, below the useful thresholds)"
    if futility_excludes:
        return "failure (no effect; useful effect excluded)"
    return "inconclusive (not detected; useful effect not excluded)"


def run_lock(out: Path, config: Path, anchors: Path, source: str = "gated", scenario: dict | None = None, seed: int = 0,
             B: int | None = None, R: int | None = None, log=print) -> dict:
    out = Path(out)
    cfg = load_config(config)
    if source == "gated":
        for s in LOCK_SCOPES:
            gate.load_authorization(s)                    # needs the lock freeze + preregistration URL
        if not cfg.get("development_selections"):
            raise RuntimeError("the lock needs the frozen development selections (kernel)")
    elif source == "synthetic":
        _guard_dry_run(out)
    else:
        raise ValueError(source)
    B = int(B or cfg["B_lock"])
    R = int(R or cfg["R_lock"])
    kernel = tuple((cfg.get("development_selections") or {}).get("kernel", (0.0, 0.0)))
    var = primary_variant(cfg)
    stat = cfg["statistic"]
    out.mkdir(parents=True, exist_ok=True)
    m = MF.build(run_id=f"stage4-lock-{source}", stage="4-locked", sets=["locked_pooled", *LOCK_SCOPES], regime="A",
                 models=[var.name, "IRT-M2"], grid=dict(kernel=list(kernel)), cv=dict(repetitions=R), inference=dict(B=B, alpha=ALPHA,
                 statistic=stat), seeds=dict(perm=seed), anchor_table=anchors,
                 outcome_access=("gate.load_item_outcomes(scope=locked_primary, locked_secondary)" if source == "gated"
                                 else f"none: SYNTHETIC dry run {scenario}"),
                 anchor_freeze_sha256=None if source == "synthetic" else json.loads(gate.FREEZE_RECORD.read_text()).get("anchor_freeze_sha256"),
                 extra=dict(design_config_sha256=sha256_file(config), source=source))
    mh = MF.write(m, out / "MANIFEST.json")
    t0 = time.time()
    prov = source == "synthetic"
    struct = {s: I.build_structure(design.build(s, anchors_path=anchors, provisional=prov, kernel=kernel), reps=R,
                                   degrees=tuple(sorted({0, var.degree}))) for s in ("locked_pooled", *LOCK_SCOPES)}
    S = struct["locked_pooled"]
    if source == "gated":
        y = gated_lock_outcomes(S, purpose=f"CAIRN locked evaluation, manifest {mh}")
    else:
        y = synthetic_outcomes(S, scenario or dict(name="ALT", odds_ratio=1.5, rho=0.4, truth="random"), seed)
    pos = {(u, j): i for i, (u, j) in enumerate(zip(S.inc.rows.uid, S.inc.rows.item))}
    rng = np.random.default_rng(seed + 101)
    rep = dict(source=source, synthetic=prov, manifest_sha256=mh, primary=var.name, statistic=stat, kernel=list(kernel))
    rep["H_pool"] = nh1(S, y, var, stat, B, rng)
    rep["closed_testing"] = {}
    for s in LOCK_SCOPES:
        Ss = struct[s]
        ys = y[[pos[(u, j)] for u, j in zip(Ss.inc.rows.uid, Ss.inc.rows.item)]]
        r = nh1(Ss, ys, var, stat, B, rng)
        r["claim"] = bool(rep["H_pool"]["reject"] and r["reject"])     # closed testing
        cv = I.cv_evaluate(Ss, ys, [var])
        r["usefulness"] = I.summarize(Ss, ys, cv, var.name)
        if var.direction is not None:
            lam = I.lambda_hat(Ss, ys, var)
            r["lambda_hat"] = dict(**lam, ci90=[lam["lam"] - 1.645 * lam["se"], lam["lam"] + 1.645 * lam["se"]])
        rep["closed_testing"][s] = r
    cv = I.cv_evaluate(S, y, [var])
    use = I.summarize(S, y, cv, var.name)
    ncv = I.nested_cv(S, y, var, cv=cv, reps=1)
    rep["usefulness"] = dict(**use, nested_cv=ncv)
    futile = bool(ncv["s_item_hi"] < 0.01)
    rep["category"] = category(rep["H_pool"]["reject"], use["s_item"], use["d_auc_wp"], futile)
    rep["seconds"] = time.time() - t0
    rep["finished_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (out / "lock_report.json").write_text(json.dumps(rep, indent=2, default=float))
    log(f"lock {source}: H_pool p={rep['H_pool']['p_NH1']:.3f} reject={rep['H_pool']['reject']}; category {rep['category']}")
    return rep


__all__ = ["run_lock", "DryRunViolation"]
