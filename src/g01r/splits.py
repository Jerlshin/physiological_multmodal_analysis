"""Person-grouped, experiment-stratified resampling (protocol §11; evaluation contract §3).

People and canonical videos are the independent units: every exposure of a person stays
in one fold, and regime B/C holds out a canonical video in every experiment jointly.
All assignments are drawn from label-addressed seeds (:mod:`g01r.rng`) and returned as
arrays so they can be stored and hashed as split identity.
"""
from __future__ import annotations

import hashlib

import numpy as np

from .population import AnalysisSet
from .rng import rng_for


def person_folds(exp_of_person: np.ndarray, K: int, rng: np.random.Generator) -> np.ndarray:
    """Fold per person; people are dealt round-robin within experiment after a random permutation,
    continuing the deal across experiments so overall fold sizes differ by at most one."""
    fold = np.empty(len(exp_of_person), int)
    offset = 0
    for e in np.unique(exp_of_person):
        idx = np.flatnonzero(exp_of_person == e)
        fold[rng.permutation(idx)] = (np.arange(len(idx)) + offset) % K
        offset += len(idx)
    return fold


def outer_folds(aset: AnalysisSet, K: int, R: int, base_seed: int, *labels) -> np.ndarray:
    """R x n_person array of outer fold labels."""
    return np.stack([person_folds(aset.exp_of_person, K, rng_for(base_seed, *labels, "outer", r)) for r in range(R)])


def inner_folds(train_persons: np.ndarray, k_inner: int, base_seed: int, *labels) -> dict:
    """Inner fold per training person (random person permutation dealt modulo k)."""
    persons = np.unique(train_persons)
    rng = rng_for(base_seed, *labels, "inner")
    assign = rng.permutation(len(persons)) % k_inner
    return dict(zip(persons.tolist(), assign.tolist()))


def bc_splits(aset: AnalysisSet, fold_of_person: np.ndarray):
    """Leave-one-canonical-video-out x person fold (regime B/C): yields (video, fold, test, train)."""
    fold = fold_of_person[aset.person]
    for v in range(aset.n_video):
        for k in np.unique(fold_of_person):
            test = (aset.video == v) & (fold == k)
            if not test.any():
                continue
            train = (aset.video != v) & (fold != k)
            yield v, int(k), test, train


def split_identity(*arrays) -> str:
    h = hashlib.sha256()
    for a in arrays:
        a = np.ascontiguousarray(a)
        h.update(str(a.shape).encode())
        h.update(a.tobytes())
    return h.hexdigest()
