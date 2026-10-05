"""In-split pipeline (protocol §8) and the regime runners (A, B/C, transport, CAS policy).

Order inside every training split:
  1. content effects from training labels (A: experiment x video mean; B/C: experiment mean
     as the offset for unseen content, training-content means for the residual target, IS-012);
  2. residual target on training cells;
  3. CorrCA and SYN references from training (A) / reference people (C) via the reference plan;
  4. features for training people (leave-self-out) and test people;
  5. training-mean imputation with indicators; standardization inside the ridge;
  6. penalty by person-grouped inner 5-fold CV over the 13-value grid;
  7. refit on the full training split;
  8. prediction = content offset + ridge output, clipped to [0, 1].

``fit_split`` receives only the training outcomes; test outcomes are used afterwards for scoring.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import references as refs_mod
from .config import ProtocolConfig
from .models import ModelSpec, fit_predict, impute_train_mean
from .population import AnalysisSet
from .splits import inner_folds, outer_folds, person_folds, split_identity
from .rng import rng_for


@dataclass
class SplitResult:
    train: np.ndarray
    test: np.ndarray
    preds: dict
    lambdas: dict
    designs: dict = field(default_factory=dict)   # model -> (X_all_imputed, cols) for permutation reuse
    offsets_test: np.ndarray | None = None
    resid_train: np.ndarray | None = None
    inner_fold: np.ndarray | None = None
    rep: int = -1
    fold: int = -1


def content_offsets(aset: AnalysisSet, y_train: np.ndarray, train: np.ndarray, test: np.ndarray, regime: str):
    """Returns (offset for test cells, residual target for training cells)."""
    tr = np.flatnonzero(train)
    te = np.flatnonzero(test)
    ev, exp = aset.ev, aset.experiment
    s = np.bincount(ev[tr], y_train, minlength=aset.n_ev)
    c = np.bincount(ev[tr], minlength=aset.n_ev)
    ev_mean = np.divide(s, c, out=np.full(aset.n_ev, np.nan), where=c > 0)
    resid = y_train - ev_mean[ev[tr]]
    exp_mean = {e: y_train[exp[tr] == e].mean() for e in np.unique(exp[tr])}
    if regime == "A":
        off = ev_mean[ev[te]]
        missing = ~np.isfinite(off)
        if missing.any():   # a test unit without training cells: fall back to the experiment mean (logged by caller)
            off[missing] = [exp_mean[e] for e in exp[te][missing]]
    elif regime in ("B", "C"):
        off = np.array([exp_mean[e] for e in exp[te]])
    else:
        raise ValueError(regime)
    return off, resid


class Pipeline:
    def __init__(self, cfg: ProtocolConfig, aset: AnalysisSet, provider, models, seed_label: str | None = None):
        """``seed_label`` addresses every random stream (default: the analysis-set name), so all
        analyses on the same set share outer folds, inner folds and permutations (paired)."""
        self.cfg, self.aset, self.provider = cfg, aset, provider
        self.models = [m for m in models]
        self.analysis_id = seed_label or aset.name
        self.seed = cfg.resampling["base_seed"]
        self.lam_rel = cfg.lambda_grid_rel
        self.min_sd = cfg.raw["model"]["standardize_min_sd"]
        self.k_inner = cfg.raw["model"]["inner_folds"]

    @property
    def needs_syn(self) -> bool:
        return any(self.provider.needs_syn(m.blocks) for m in self.models)

    def fit_split(self, y_train, train, test, plan=None, regime="A", labels=(), keep_design=False,
                  models=None, offsets=None) -> SplitResult:
        aset = self.aset
        train, test = np.asarray(train, bool), np.asarray(test, bool)
        if (train & test).any():
            raise AssertionError("A cell is in both training and test")
        if np.intersect1d(aset.person[train], aset.person[test]).size:
            raise AssertionError("A person is in both training and test")
        y_train = np.asarray(y_train, float)
        if len(y_train) != train.sum() or not np.isfinite(y_train).all():
            raise ValueError("Training outcomes must be finite and aligned with the training mask")
        tr, te = np.flatnonzero(train), np.flatnonzero(test)
        if offsets is None:
            off, resid = content_offsets(aset, y_train, train, test, regime)
        else:
            off, resid = offsets(y_train, train, test)
        syn = self.provider.syn(plan) if (plan is not None and self.needs_syn) else None
        fmap = inner_folds(aset.person[tr], self.k_inner, self.seed, self.analysis_id, *labels)
        inner = np.array([fmap[p] for p in aset.person[tr]])
        result = SplitResult(tr, te, {}, {}, offsets_test=off, resid_train=resid, inner_fold=inner)
        for m in (models or self.models):
            X, cols = self.provider.design(m.blocks, syn)
            Xtr, Xte, _ = impute_train_mean(X[tr], X[te])
            p, lam = fit_predict(Xtr, resid, Xte, inner, self.lam_rel, self.min_sd)
            result.preds[m.name] = np.clip(off + p, *self.cfg.raw["outcome"]["clip"])
            result.lambdas[m.name] = lam
            if keep_design:
                Xall = np.empty((aset.n, X.shape[1]))
                Xall[:] = np.nan
                Xall[tr], Xall[te] = Xtr, Xte
                result.designs[m.name] = (Xall, cols)
        return result


# ---------------------------------------------------------------------------- regime A
@dataclass
class CVResult:
    preds: dict            # model -> R x n predictions (NaN where not tested)
    folds: np.ndarray      # R x n_person outer folds
    lambdas: dict
    designs: list          # per (r, k) SplitResult for r < keep_design_reps
    split_id: str
    notes: dict = field(default_factory=dict)


def run_regime_A(pipe: Pipeline, y: np.ndarray, R: int | None = None, K: int | None = None, keep_design_reps: int = 0,
                 reps=None, plan_fn=None) -> CVResult:
    cfg, aset = pipe.cfg, pipe.aset
    R = R or cfg.resampling["reps_A"]
    K = K or cfg.resampling["outer_folds_A"]
    folds = outer_folds(aset, K, R, pipe.seed, pipe.analysis_id, "A")
    reps = range(R) if reps is None else reps
    preds = {m.name: np.full((R, aset.n), np.nan) for m in pipe.models}
    lambdas = {m.name: [] for m in pipe.models}
    designs = []
    for r in reps:
        if pipe.needs_syn and hasattr(pipe.provider, "syn_many"):
            # Prefetch: one pass over the EEG cache for the repetition's K plans.
            pipe.provider.syn_many([(plan_fn or refs_mod.regime_A)(aset, folds[r][aset.person] != k, np.ones(aset.n, bool))
                                    for k in range(K)])
        for k in range(K):
            test = folds[r][aset.person] == k
            train = ~test
            plan = None
            if pipe.needs_syn:
                plan = (plan_fn or refs_mod.regime_A)(aset, train, np.ones(aset.n, bool))
            res = pipe.fit_split(y[train], train, test, plan, "A", labels=("A", r, k), keep_design=r < keep_design_reps)
            for name, p in res.preds.items():
                preds[name][r, test] = p
                lambdas[name].append(res.lambdas[name])
            if r < keep_design_reps:
                res.rep, res.fold = r, k
                designs.append(res)
    return CVResult(preds, folds, lambdas, designs, split_identity(folds, aset.person))


# ---------------------------------------------------------------------------- regimes B and C
@dataclass
class BCResult:
    preds_B: dict
    preds_C: dict
    folds: np.ndarray
    halves: np.ndarray
    split_id: str


def run_regimes_BC(pipe_B: Pipeline, pipe_C: Pipeline | None, y: np.ndarray, R: int | None = None, K: int | None = None,
                   reps=None) -> BCResult:
    cfg, aset = pipe_B.cfg, pipe_B.aset
    R = R or cfg.resampling["reps_BC"]
    K = K or cfg.resampling["folds_BC"]
    seed = pipe_B.seed
    folds = np.stack([person_folds(aset.exp_of_person, K, rng_for(seed, pipe_B.analysis_id, "BC", "outer", r)) for r in range(R)])
    halves = np.stack([refs_mod.half_split(aset, rng_for(seed, pipe_B.analysis_id, "BC", "half", r)) for r in range(R)])
    preds_B = {m.name: np.full((R, aset.n), np.nan) for m in pipe_B.models}
    preds_C = {m.name: np.full((R, aset.n), np.nan) for m in (pipe_C.models if pipe_C else [])}
    for r in (range(R) if reps is None else reps):
        fold = folds[r][aset.person]
        if pipe_C is not None and pipe_C.needs_syn and hasattr(pipe_C.provider, "syn_many"):
            plans = []
            for v in range(aset.n_video):
                for k in range(K):
                    test = (aset.video == v) & (fold == k)
                    if test.any():
                        plans.append(refs_mod.regime_C(aset, (aset.video != v) & (fold != k), test, halves[r]))
            pipe_C.provider.syn_many(plans)
        for v in range(aset.n_video):
            for k in range(K):
                test = (aset.video == v) & (fold == k)
                if not test.any():
                    continue
                train = (aset.video != v) & (fold != k)
                res = pipe_B.fit_split(y[train], train, test, None, "B", labels=("B", r, v, k))
                for name, p in res.preds.items():
                    preds_B[name][r, test] = p
                if pipe_C is not None:
                    plan = refs_mod.regime_C(aset, train, test, halves[r])
                    res = pipe_C.fit_split(y[train], train, test, plan, "C", labels=("C", r, v, k))
                    for name, p in res.preds.items():
                        preds_C[name][r, test] = p
    return BCResult(preds_B, preds_C, folds, halves, split_identity(folds, halves, aset.person, aset.video))


# ---------------------------------------------------------------------------- E4 <-> E5 transport
def run_transport(pipe: Pipeline, y_source: np.ndarray, source: np.ndarray, target: np.ndarray,
                  y_target_for_recalibration: np.ndarray | None = None):
    """Train on the whole source cohort, predict the target cohort once.

    Offsets: the source cohort's mean for the same canonical video. The recalibrated variant
    (labelled as using target labels) replaces them with the target cohort's video means.
    """
    aset = pipe.aset
    video = aset.video
    src = np.flatnonzero(source)

    def offsets(y_tr, train, test):
        ev = aset.ev
        tr = np.flatnonzero(train)
        s = np.bincount(ev[tr], y_tr, minlength=aset.n_ev)
        c = np.bincount(ev[tr], minlength=aset.n_ev)
        ev_mean = np.divide(s, c, out=np.full(aset.n_ev, np.nan), where=c > 0)
        resid = y_tr - ev_mean[ev[tr]]
        vid_mean = {v: y_tr[video[tr] == v].mean() for v in np.unique(video[tr])}
        off = np.array([vid_mean[v] for v in video[np.flatnonzero(test)]])
        return off, resid

    plan = refs_mod.transport(aset, source, target) if pipe.needs_syn else None
    res = pipe.fit_split(y_source, source, target, plan, "transport", labels=("transport",), offsets=offsets)
    out = {"source_offsets": res.preds}
    if y_target_for_recalibration is not None:
        te = np.flatnonzero(target)
        recal = {}
        yt = np.asarray(y_target_for_recalibration, float)[te]      # full-length outcome array, target cells only
        vm = {v: yt[video[te] == v].mean() for v in np.unique(video[te])}
        shift = np.array([vm[v] for v in video[te]]) - res.offsets_test
        for name, p in res.preds.items():
            recal[name] = np.clip(p + shift, *pipe.cfg.raw["outcome"]["clip"])
        out["target_mean_recalibrated_USES_TARGET_LABELS"] = recal
    return out, res


# ---------------------------------------------------------------------------- CAS policy
def run_cas_policy(pipe_M2: Pipeline, pipe_M5: Pipeline, y: np.ndarray, in_core: np.ndarray, R: int | None = None,
                   K: int | None = None, reps=None):
    """Available-sensor policy on the coverage set: M5 where PAS-core features exist, M2 otherwise.

    Both pipelines share the coverage-set analysis set and folds; M5 is trained on PAS-core
    training cells only and its synchrony references use PAS-core training people only.
    """
    cfg, aset = pipe_M2.cfg, pipe_M2.aset
    R = R or cfg.resampling["reps_A"]
    K = K or cfg.resampling["outer_folds_A"]
    folds = outer_folds(aset, K, R, pipe_M2.seed, pipe_M2.analysis_id, "A")
    m2 = np.full((R, aset.n), np.nan)
    policy = np.full((R, aset.n), np.nan)
    in_core = np.asarray(in_core, bool)
    for r in (range(R) if reps is None else reps):
        for k in range(K):
            test = folds[r][aset.person] == k
            train = ~test
            res2 = pipe_M2.fit_split(y[train], train, test, None, "A", labels=("CAS", r, k))
            m2[r, test] = res2.preds["M2"]
            policy[r, test] = res2.preds["M2"]
            tr5, te5 = train & in_core, test & in_core
            if te5.any():
                plan = refs_mod.regime_A(aset, tr5, in_core)
                res5 = pipe_M5.fit_split(y[tr5], tr5, te5, plan, "A", labels=("CAS_M5", r, k))
                policy[r, te5] = res5.preds["M5"]
    return dict(M2=m2, POLICY=policy), folds
