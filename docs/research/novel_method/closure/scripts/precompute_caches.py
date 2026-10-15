"""Precompute the fold-safe per-second channel caches for R = 10 CV repetitions (outcome-free; closure C-D12).

Stage 2 (development, R = 10) and the lock (pooled, E4 and E5 elementary analyses, R = 10 for usefulness) need the
split channels of repetitions 3..9 in addition to the Stage-1 repetitions 0..2. Each cache is keyed by the split's
training learners (``cairn.features.split_key``), so computing them now changes no result; it only removes waiting.

    python precompute_caches.py development locked_pooled locked_primary locked_secondary
"""
from __future__ import annotations

import sys
import time

from cairn import design
from cairn import features as F
from cairn import inference as I

if __name__ == "__main__":
    for set_name in sys.argv[1:]:
        inc = design.build(set_name)
        persons = sorted(inc.cells.person.unique())
        strata = inc.cells.groupby("person").experiment.first().reindex(persons).to_numpy()
        import numpy as np
        persons = np.array(persons)
        t0 = time.time()
        n = 0
        for r in range(10):
            fmap = I.stratified_group_folds(persons, strata, I.K_FOLDS, seed=r)
            for f in range(I.K_FOLDS):
                F.compute_split(inc, frozenset(p for p in persons if fmap[p] != f))
                n += 1
        F.compute_split(inc, frozenset(persons))
        print(f"{set_name}: {n + 1} splits ready in {time.time() - t0:.0f} s", flush=True)
