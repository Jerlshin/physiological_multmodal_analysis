"""Deterministic, label-addressed random streams.

Every random quantity in the pipeline (outer folds, inner folds, half-cohort
reference splits, permutations, bootstrap weights, synthetic data) is drawn
from a generator addressed by the frozen base seed plus a tuple of labels.
Reordering computations or running them in parallel therefore never changes
the numbers, and the same split is reproduced by any process.
"""
from __future__ import annotations

import hashlib

import numpy as np


def _label_words(labels) -> list[int]:
    text = "\x1f".join(str(x) for x in labels).encode()
    digest = hashlib.sha256(text).digest()
    return [int.from_bytes(digest[i:i + 4], "little") for i in range(0, 32, 4)]


def seed_sequence(base_seed: int, *labels) -> np.random.SeedSequence:
    return np.random.SeedSequence(entropy=int(base_seed), spawn_key=tuple(_label_words(labels)))


def rng_for(base_seed: int, *labels) -> np.random.Generator:
    return np.random.default_rng(seed_sequence(base_seed, *labels))


def seed_int(base_seed: int, *labels) -> int:
    """A 63-bit integer seed (for recording in run metadata)."""
    return int(seed_sequence(base_seed, *labels).generate_state(2, np.uint32).view(np.uint64)[0] >> 1)
