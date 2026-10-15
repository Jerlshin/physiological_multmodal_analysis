"""Stage 0c - label-free encoder: fold-safe pretraining and outcome-free validation.

Five learner-grouped outer folds over all in-scope exposures. In each fold the encoder,
standardization and reference distiller are fitted on training learners only (asserted) and
applied to held-out learners. Validation on held-out learners only:

* masked-centre reconstruction R^2 (vs a neighbour-mean baseline);
* reference distillation R^2 (peer-free prediction of the reference-relative channels);
* construct check: attentive vs distracted viewing (E1-E3) from encoder whole-video means,
  classifier itself learner-grouped (encoder never sees condition labels);
* identity probes on anchored moment terms (development anchors) - person- and item-centred;
* matched-noise control (random projection encoder) for both;
* determinism (refit -> identical parameters).
No quiz outcome is read.
"""
from __future__ import annotations

import hashlib
import json
import sys

import numpy as np
import pandas as pd

from cairn.encoder import LinearMaskedEncoder, RandomEncoder, ReferenceDistiller
from cairn.paths import DERIVED, STAGE0_EVIDENCE
from cairn.pooling import anchored_moment_terms
from cairn.stats import auc, balanced_accuracy, group_kfold, logistic_fit, logistic_predict, softmax_fit, softmax_predict, standardize

PRIMARY = ["valid", "onscreen", "sacc", "disp5", "dist", "logdens", "rho5", "speed"]
FREE = ["valid", "onscreen", "sacc", "disp5", "speed"]
REL = ["dist", "logdens", "rho5"]
ATTENTIVE = {"intentional_attend", "incidental_attend", "attend_untested_content", "incidental_first"}
SEED, K, FOLDS = 13, 3, 5
OUT = STAGE0_EVIDENCE / "signal"


def main():
    d = pd.read_parquet(DERIVED / "channels_1hz.parquet")
    s = pd.read_parquet(DERIVED / "channels_scope.parquet")
    a = pd.read_csv(STAGE0_EVIDENCE / "anchors_provisional.csv")
    dev_anchors = a[(a.role == "development") & a.anchorable]
    by = {u: g.sort_values("t") for u, g in d.groupby("uid")}
    s = s[s.uid.isin(by)].reset_index(drop=True)
    U = {u: by[u][PRIMARY].to_numpy(float) for u in s.uid}
    groups = s.qualified_participant_id.to_numpy()
    rec, dist_r2, ebar, moment = [], [], {}, []
    hashes = []
    for f, (tr, te) in enumerate(group_kfold(groups, FOLDS, SEED)):
        tr_uids, te_uids = list(s.uid[tr]), list(s.uid[te])
        assert not (set(groups[tr]) & set(groups[te])), "test learner in training fold"
        enc = LinearMaskedEncoder(K=K).fit([U[u] for u in tr_uids])
        enc2 = LinearMaskedEncoder(K=K).fit([U[u] for u in tr_uids])
        assert np.array_equal(enc.B, enc2.B), "non-deterministic encoder fit"
        hashes.append(hashlib.sha256(enc.B.tobytes() + enc.V.tobytes()).hexdigest()[:16])
        rnd = RandomEncoder(D=len(PRIMARY), K=K, seed=SEED + f).fit([U[u] for u in tr_uids])
        dst = ReferenceDistiller().fit([by[u][FREE].to_numpy(float) for u in tr_uids], [by[u][REL].to_numpy(float) for u in tr_uids])
        for u in te_uids:
            Z = enc.std.transform(U[u])
            nb = (np.vstack([Z[1:], Z[-1:]]) + np.vstack([Z[:1], Z[:-1]])) / 2
            base = float(1 - ((Z - nb) ** 2).sum() / ((Z - Z.mean(0)) ** 2).sum())
            rec.append(dict(fold=f, uid=u, r2_encoder=enc.r2(U[u]), r2_neighbour_mean=base))
            dist_r2.append(dict(fold=f, uid=u, **dict(zip(REL, dst.r2(by[u][FREE].to_numpy(float), by[u][REL].to_numpy(float))))))
            E = enc.transform(U[u])
            R = rnd.transform(U[u])
            ebar[u] = dict(enc=E.mean(0), rnd=R.mean(0))
            vid = s.loc[s.uid == u, "canonical_video_id"].iloc[0]
            an = dev_anchors[dev_anchors.canonical_video_id == vid].sort_values("item")
            if len(an):
                Ze = anchored_moment_terms(E, an.assign(localized=True))
                Zr = anchored_moment_terms(R, an.assign(localized=True))
                row = s.loc[s.uid == u].iloc[0]
                for j, it in enumerate(an.itertuples()):
                    moment.append(dict(uid=u, learner=row.qualified_participant_id, condition=row.condition, video=vid, item=it.item,
                                       **{f"enc{k}": Ze[j, k] for k in range(K)}, **{f"rnd{k}": Zr[j, k] for k in range(K)}))
    rec, dist_r2, M = pd.DataFrame(rec), pd.DataFrame(dist_r2), pd.DataFrame(moment)
    # construct check (E1-E3 attentive vs distracted), held-out encoder outputs
    c = s[s.experiment.isin([1, 2, 3])].copy()
    y = (c.condition == "arithmetic_repeat").astype(int).to_numpy()
    g = c.qualified_participant_id.to_numpy()
    construct = {}
    for name, X in (("encoder", np.vstack([ebar[u]["enc"] for u in c.uid])),
                    ("random_encoder", np.vstack([ebar[u]["rnd"] for u in c.uid])),
                    ("raw_channel_means", np.vstack([np.nanmean(U[u], 0) for u in c.uid]))):
        pred = np.full(len(y), np.nan)
        for tr, te in group_kfold(g, 5, SEED + 1):
            Xtr, Xte = standardize(X[tr], X[te])
            pred[te] = logistic_predict(logistic_fit(Xtr, y[tr]), Xte)
        construct[name] = auc(y, pred)
    # identity probes on anchored moment terms (attentive, development anchors)
    At = M[M.condition.isin(ATTENTIVE)].dropna()
    ident = {}
    for name, cols in (("encoder", [f"enc{k}" for k in range(K)]), ("random_encoder", [f"rnd{k}" for k in range(K)])):
        X = At[cols].to_numpy(float)
        for label, XX in (("person_centred", X), ("item_centred", X - At.groupby(["video", "item"])[cols].transform("mean").to_numpy())):
            cls, yi = np.unique(At.video, return_inverse=True)
            pred = np.full(len(yi), -1)
            for tr, te in group_kfold(At.learner.to_numpy(), 5, SEED + 2):
                Xtr, Xte = standardize(XX[tr], XX[te])
                pred[te] = softmax_predict(softmax_fit(Xtr, yi[tr], len(cls)), Xte)
            ident[f"{name}_{label}"] = dict(balanced_accuracy=balanced_accuracy(yi, pred), chance=1 / len(cls))
    summ = dict(K=K, context_s=9, channels=PRIMARY, n_params=LinearMaskedEncoder(K=K).fit([U[u] for u in list(s.uid)[:50]]).n_params,
                reconstruction=dict(encoder_r2_median=float(rec.r2_encoder.median()), neighbour_mean_r2_median=float(rec.r2_neighbour_mean.median())),
                distillation_r2_median={c: float(dist_r2[c].median()) for c in REL},
                construct_auc=construct, identity=ident, fold_param_hashes=hashes, deterministic=True,
                n_exposures=len(s), n_learners=int(len(np.unique(groups))))
    (DERIVED / "stage0_participant_level").mkdir(parents=True, exist_ok=True)
    rec.to_csv(DERIVED / "stage0_participant_level" / "J_encoder_reconstruction.csv", index=False, float_format="%.4f")   # participant-level: git-ignored
    (OUT / "J_encoder_summary.json").write_text(json.dumps(summ, indent=2, default=float))
    print(json.dumps(summ, indent=2, default=float))


if __name__ == "__main__":
    sys.exit(main())
