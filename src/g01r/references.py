"""Reference-access rules for the synchrony features (protocol §6-§8; evaluation contract §2, §4).

A :class:`ReferencePlan` lists, for every target cell, the cells whose signals form its
reference mean, and the cells allowed to fit the CorrCA spatial filters. Constructors
encode the frozen regimes and assert the leakage rules on construction:

* a target's own person is never in its reference (leave-self-out);
* regime A: references and CorrCA come from training people only;
* regime C: test references are the other half-cohort of the held-out video's viewers
  in the same experiment; training references use the other half among training people;
  CorrCA is fit on training cells (training videos, training people) only;
* transport: references and CorrCA come from the source cohort only.

Plans never see outcomes.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .population import AnalysisSet


@dataclass
class ReferencePlan:
    regime: str
    refs: dict                      # target cell index -> np.ndarray of reference cell indices
    corrca_fit: np.ndarray          # bool mask over cells: cells whose EEG fits the CorrCA filters
    notes: dict = field(default_factory=dict)

    def renamed(self, regime: str) -> "ReferencePlan":
        self.regime = regime
        return self

    def targets(self) -> np.ndarray:
        return np.array(sorted(self.refs), int)

    def check(self, aset: AnalysisSet):
        person = aset.person
        video = aset.video
        for c, r in self.refs.items():
            if (person[r] == person[c]).any():
                raise AssertionError(f"{self.regime}: target {c} has its own person in its reference")
            if (video[r] != video[c]).any():
                raise AssertionError(f"{self.regime}: reference of target {c} watched different content")
        return self


def _by_ev(aset: AnalysisSet):
    ev = aset.ev
    return {e: np.flatnonzero(ev == e) for e in range(aset.n_ev)}


def regime_A(aset: AnalysisSet, train: np.ndarray, targets: np.ndarray) -> ReferencePlan:
    """Reference = training people of the same experiment x video; training targets leave themselves out."""
    train = np.asarray(train, bool)
    person, ev = aset.person, aset.ev
    groups = _by_ev(aset)
    refs = {}
    for c in np.flatnonzero(targets):
        cand = groups[ev[c]]
        refs[int(c)] = cand[train[cand] & (person[cand] != person[c])]
    plan = ReferencePlan("A", refs, train.copy())
    return plan.check(aset)


def half_split(aset: AnalysisSet, rng: np.random.Generator) -> np.ndarray:
    """Person-level 2-way split within each experiment (IS-010): returns half label (0/1) per person."""
    half = np.empty(aset.n_person, int)
    exp_of_person = aset.exp_of_person
    for e in np.unique(exp_of_person):
        idx = np.flatnonzero(exp_of_person == e)
        perm = rng.permutation(idx)
        half[perm] = np.arange(len(idx)) % 2
    return half


def regime_C(aset: AnalysisSet, train: np.ndarray, test: np.ndarray, half: np.ndarray) -> ReferencePlan:
    """Cross-fitted half-cohort references (evaluation contract §2, regime C)."""
    train, test = np.asarray(train, bool), np.asarray(test, bool)
    if (aset.video[test][:, None] == aset.video[train][None, :]).any():
        raise AssertionError("Regime C: held-out content appears in training")
    person, ev = aset.person, aset.ev
    hp = half[person]
    groups = _by_ev(aset)
    refs = {}
    for c in np.flatnonzero(test):
        cand = groups[ev[c]]
        refs[int(c)] = cand[(hp[cand] != hp[c]) & (person[cand] != person[c])]
    for c in np.flatnonzero(train):
        cand = groups[ev[c]]
        refs[int(c)] = cand[train[cand] & (hp[cand] != hp[c]) & (person[cand] != person[c])]
    plan = ReferencePlan("C", refs, train.copy(), notes=dict(half_sizes=np.bincount(half).tolist()))
    return plan.check(aset)


def transport(aset: AnalysisSet, source: np.ndarray, target: np.ndarray) -> ReferencePlan:
    """Source-cohort references on the same canonical video; CorrCA fit on the source cohort."""
    source, target = np.asarray(source, bool), np.asarray(target, bool)
    if (aset.person[source][:, None] == aset.person[target][None, :]).any():
        raise AssertionError("Transport: source and target cohorts share a person")
    person, ev, video = aset.person, aset.ev, aset.video
    refs = {}
    for c in np.flatnonzero(source):
        cand = np.flatnonzero((ev == ev[c]) & source)
        refs[int(c)] = cand[person[cand] != person[c]]
    for c in np.flatnonzero(target):
        refs[int(c)] = np.flatnonzero((video == video[c]) & source)
    return ReferencePlan("transport", refs, source.copy()).check(aset)


def full_leave_self_out(aset: AnalysisSet) -> ReferencePlan:
    """Explanatory companion only (labelled explanatory): all other viewers of the same experiment x video."""
    allc = np.ones(aset.n, bool)
    return regime_A(aset, allc, allc).renamed("explanatory_full_lso")
