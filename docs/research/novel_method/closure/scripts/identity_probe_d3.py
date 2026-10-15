"""Spec §3 test 8 on the closure forms (outcome-free): can video identity be predicted from the item-centred moment
regressors at the selected detrend degree? Six-channel block (P6/PT input) and the unit-weighted composite (P0).
Learner-grouped CV on training rows of split 0; permutation 95% band over whole learners."""
from __future__ import annotations

import json
import sys

from cairn import design
from cairn import features as F
from cairn import inference as I

if __name__ == "__main__":
    k, out = int(sys.argv[1]), sys.argv[2]
    res = {}
    for set_name in ("development", "locked_pooled"):
        S = I.build_structure(design.build(set_name), reps=1, degrees=(k,))
        sp = S.splits[0]
        tr = sp.anch_train
        for v in (I.six_variant(k), I.unit_variant(k)):
            x = I.moment_columns(S, sp, v, sp.block(v).m)[S.anch_index]
            r = F.identity_probe(x[tr], S.anch_video[tr], S.person[S.anch_index][tr], n_perm=49)
            res[f"{set_name}|{v.name}"] = r
            print(set_name, v.name, r, flush=True)
    json.dump(res, open(out, "w"), indent=2, default=float)
