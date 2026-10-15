"""Outcome-free trend-leakage diagnostic (closure C-D03, supporting rule R-F).

A slow, learner-specific fatigue confound biases the moment effect only through the part of the moment regressor
that is a smooth function of anchor position **within** a learner x video cell. For each detrend degree d in
{0 (raw), 1, 2, 3}, this script measures that part on the **real** signals (no outcome): the pooled within-cell R^2
of the unit-weighted moment regressor on Legendre polynomials P1..P3 of anchor position, against a permutation
reference in which the anchor positions are shuffled among each video's moments (same regressor, no temporal order).

    python trend_leakage.py <out.json>
"""
from __future__ import annotations

import json
import sys

import numpy as np

from cairn import design
from cairn import features as F
from cairn import inference as I


def within_cell_r2(x, pos, cell, deg_poly=3):
    num = den = 0.0
    for c in np.unique(cell):
        m = cell == c
        if m.sum() < deg_poly + 2:
            continue
        xc = x[m] - x[m].mean()
        X = np.polynomial.legendre.legvander(2 * pos[m] - 1, deg_poly)[:, 1:]
        X = X - X.mean(0)
        b, *_ = np.linalg.lstsq(X, xc, rcond=None)
        num += float(((X @ b) ** 2).sum())
        den += float((xc ** 2).sum())
    return num / den if den > 0 else np.nan


def main(out):
    res = {}
    for set_name in ("locked_pooled", "development"):
        S = I.build_structure(design.build(set_name), with_splits=False, degrees=(0, 1, 2, 3))
        can = S.canonical
        rows = S.inc.rows[S.inc.rows.anchorable]
        pos = rows.anchor_pos.to_numpy(float)
        rng = np.random.default_rng(0)
        out_set = {}
        for d in (0, 1, 2, 3):
            v = I.unit_variant(d) if d else I.direction_variant(I.UNIT_W, name="u-raw")
            x = I.moment_columns(S, can, v, can.block(v).m)[S.anch_index, 0]
            obs = {k: within_cell_r2(x, pos, S.anch_cell, k) for k in (1, 2, 3)}
            null = []
            for _ in range(200):
                pp = pos.copy()
                for vid in np.unique(S.anch_video):
                    sel = S.anch_video == vid
                    mom = S.anch_moment[sel]
                    um = np.unique(mom)
                    cen = {m: pos[sel][mom == m][0] for m in um}
                    perm = dict(zip(um, rng.permutation(um)))
                    pp[sel] = [cen[perm[m]] for m in mom]
                null.append(within_cell_r2(x, pp, S.anch_cell, 3))
            out_set[f"degree_{d}"] = dict(r2_P1=obs[1], r2_P1_P2=obs[2], r2_P1_P3=obs[3],
                                          r2_P1_P3_shuffled_mean=float(np.mean(null)),
                                          r2_P1_P3_shuffled_q95=float(np.quantile(null, .95)),
                                          excess_over_shuffled=obs[3] - float(np.mean(null)))
        res[set_name] = out_set
    out = open(out, "w")
    json.dump(res, out, indent=2)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
