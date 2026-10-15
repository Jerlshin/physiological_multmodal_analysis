"""Outcome-free reliability of the anchored moment term per cohort (closure C-I; informs E4/E5 heterogeneity).

For each set, the unit-weighted composite of the six standardized channels (degree-3 within-recording detrend; the
closure primary form) is pooled over each anchor window twice, from odd and from even seconds. Both halves are
centred within learner x video and within item (the moment-regressor construction). The split-half correlation over
anchorable rows, Spearman-Brown corrected, estimates the reliability of the observed moment term.
Signals only; no outcome."""
from __future__ import annotations

import json
import sys

import numpy as np

from cairn import design
from cairn import features as F
from cairn import inference as I


def halves(S, sp, k):
    sc = F.compute_split(S.inc, sp.train_persons)
    arr = sc.detrended(k)
    sign = np.array([F.ENGAGED_SIGN[c] for c in F.PRIMARY])
    rows = S.inc.rows[S.inc.rows.anchorable]
    n_s = np.array([S.inc.n_s[v] for v in rows.video])
    lo, hi = F.window_bounds(rows.start.to_numpy(float), rows.end.to_numpy(float), n_s)
    pos = {}
    for v, idx in sc.cell_index.items():
        for i, ci in enumerate(idx):
            pos[ci] = (v, i)
    out = np.full((len(rows), 2), np.nan)
    for r, (c, a, b) in enumerate(zip(S.anch_cell, lo, hi)):
        v, i = pos[c]
        comp = np.nanmean(arr[v][i, a:b] * sign, axis=1)
        sec = np.arange(a, b)
        for h in (0, 1):
            x = comp[sec % 2 == h]
            out[r, h] = np.nanmean(x) if np.isfinite(x).any() else np.nan
    return out


if __name__ == "__main__":
    k = int(sys.argv[1])
    res = {}
    for s in ("development", "locked_primary", "locked_secondary"):
        S = I.build_structure(design.build(s), with_splits=False, degrees=(k,))
        H = halves(S, S.canonical, k)
        ok = np.isfinite(H).all(1)
        allrows = ok.copy()
        x = [F.moment_regressors(np.where(ok, H[:, h], 0.0)[:, None], S.anch_cell, S.anch_item, allrows)[:, 0] for h in (0, 1)]
        r = float(np.corrcoef(x[0][ok], x[1][ok])[0, 1])
        res[s] = dict(rows=int(ok.sum()), split_half_r=r, spearman_brown=2 * r / (1 + r))
        print(s, res[s], flush=True)
    json.dump(res, open(sys.argv[2], "w"), indent=2)
