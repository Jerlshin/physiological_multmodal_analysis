"""Stage 0c - outcome-free feasibility of the per-second ocular representation.

Scope: in-scope exposures (development + label-free; no tested exposure of a locked cohort);
anchored analyses use development videos and the provisional anchors only (Stars/Immune anchors
are locked content and are not used). Nothing here reads a quiz outcome.

Analyses
--------
A  variance decomposition of every 1 Hz channel (person / stimulus-locked moment / person x
   moment) at 1 s and 10 s, attentive viewings, per experiment x video unit;
B  anchored moment terms z - e_bar for development anchors: item vs person x item shares;
   reliability of the person x item part (odd/even-second split = upper bound; attend vs
   distract viewing of the same learner = test-retest lower bound); channel redundancy;
C  missingness behaviour: invalid episodes, their composition, stimulus-locking, persistence,
   attend vs distract, head motion during invalid seconds;
D  construct check: attentive vs distracted viewing (E1-E3), within-learner effect sizes and
   held-out-learner AUC per channel family;
E  content-identity probes: video identity from whole-video means, from anchored moment terms
   and from item-centred moment terms (learner-grouped CV);
H  pupil-gaze coupling (gaze-position artefact in the reference-relative pupil).
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from cairn.channels import ALL_CHANNELS, REF_FREE, REF_REL
from cairn.paths import BIN_HZ, DERIVED, STAGE0_EVIDENCE
from cairn.pooling import anchored_moment_terms
from cairn.stats import (auc, balanced_accuracy, group_kfold, logistic_fit, logistic_predict, softmax_fit,
                         softmax_predict, spearman_brown, standardize, variance_shares)

SEED = 41
ATTENTIVE = {"intentional_attend", "incidental_attend", "attend_untested_content", "incidental_first"}
CH = [c for c in ALL_CHANNELS if c not in ("head_z", "head_motion")]          # head absent in E1
OUT = STAGE0_EVIDENCE / "signal"


def load():
    d = pd.read_parquet(DERIVED / "channels_1hz.parquet")
    s = pd.read_parquet(DERIVED / "channels_scope.parquet")
    a = pd.read_csv(STAGE0_EVIDENCE / "anchors_provisional.csv")
    return d, s, a


def mats(d: pd.DataFrame, uids: list[str], ch: str, win: int = 1) -> np.ndarray:
    g = d[d.uid.isin(uids)]
    M = g.pivot(index="uid", columns="t", values=ch).reindex(uids).to_numpy(float)
    if win > 1:
        n = M.shape[1] // win
        with np.errstate(invalid="ignore"):
            M = np.nanmean(M[:, : n * win].reshape(len(uids), n, win), axis=2)
    return M


# ------------------------------------------------------------------ A
def part_a(d, s):
    rows = []
    att = s[s.condition.isin(ATTENTIVE)]
    for (e, vid), g in att.groupby(["experiment", "canonical_video_id"]):
        if len(g) < 8:
            continue
        for ch in ALL_CHANNELS:
            for win in (1, 10):
                M = mats(d, list(g.uid), ch, win)
                if np.isfinite(M).sum() < 100 or np.all(np.isnan(M)):
                    continue
                v = variance_shares(M)
                rows.append(dict(experiment=e, video=vid, channel=ch, window_s=win, n=len(g), **v))
    A = pd.DataFrame(rows)
    A.to_csv(OUT / "A_variance_units.csv", index=False, float_format="%.4f")
    w = A.groupby(["channel", "window_s"]).apply(lambda x: pd.Series({k: np.average(x[k].dropna(), weights=x.n_cells[x[k].notna()]) for k in ("person", "moment", "residual", "resid_lag1")}), include_groups=False)
    w.to_csv(OUT / "A_variance_summary.csv", float_format="%.3f")
    return w


# ------------------------------------------------------------------ B
_BY = {}


def by_uid(d):
    if not _BY:
        _BY.update({u: g.sort_values("t") for u, g in d.groupby("uid")})
    return _BY


def anchored_table(d, s, a, ch_list, split=None):
    """Long table of moment terms (uid, item, channel values) for development anchors.
    split: None | 'odd' | 'even' (seconds used for both the anchor and the whole-video mean)."""
    dev = a[(a.role == "development") & a.anchorable]
    rows = []
    for vid, an in dev.groupby("canonical_video_id"):
        an = an.sort_values("item")
        for r in s[s.canonical_video_id == vid].itertuples():
            E = by_uid(d)[r.uid][ch_list].to_numpy(float)
            if split:
                keep = (np.arange(len(E)) % 2 == (1 if split == "odd" else 0))
                E = np.where(keep[:, None], E, np.nan)
            Z = anchored_moment_terms(E, an.assign(localized=True))
            for j, it in enumerate(an.itertuples()):
                rows.append(dict(uid=r.uid, learner=r.qualified_participant_id, experiment=r.experiment, session=r.session,
                                 condition=r.condition, video=vid, item=it.item, **{c: Z[j, i] for i, c in enumerate(ch_list)}))
    return pd.DataFrame(rows)


def double_centre(T: pd.DataFrame, ch: str) -> pd.Series:
    x = T[ch] - T.groupby(["video", "item", "condition"])[ch].transform("mean")
    return x - T.assign(_x=x).groupby("uid")["_x"].transform("mean")


def part_b(d, s, a):
    att = s[s.condition.isin(ATTENTIVE) | (s.condition == "arithmetic_repeat")]
    T = anchored_table(d, att, a, CH)
    To = anchored_table(d, att, a, CH, "odd")
    Te = anchored_table(d, att, a, CH, "even")
    rows = []
    for ch in CH:
        At = T[T.condition.isin(ATTENTIVE)].dropna(subset=[ch])
        tot = At[ch].var()
        item_part = At.groupby(["video", "item"])[ch].transform("mean")
        resid = double_centre(At, ch)
        # odd/even split (upper bound)
        o = To[To.condition.isin(ATTENTIVE)].set_index(["uid", "item", "video"])
        e = Te[Te.condition.isin(ATTENTIVE)].set_index(["uid", "item", "video"])
        oo = double_centre(o.reset_index(), ch).to_numpy()
        ee = double_centre(e.reset_index(), ch).to_numpy()
        ok = np.isfinite(oo) & np.isfinite(ee)
        r_oe = float(np.corrcoef(oo[ok], ee[ok])[0, 1]) if ok.sum() > 50 else np.nan
        # test-retest: attentive (session 1) vs distracted (session 2) viewing, same learner and video, E1-E3
        Tc = T.copy()
        Tc["dc"] = np.nan
        for cond_set in (ATTENTIVE, {"arithmetic_repeat"}):
            sub = Tc.condition.isin(cond_set)
            Tc.loc[sub, "dc"] = double_centre(Tc[sub], ch).to_numpy()
        p1 = Tc[Tc.experiment.isin([1, 2, 3]) & (Tc.session == 1)].set_index(["learner", "video", "item"]).dc
        p2 = Tc[Tc.experiment.isin([1, 2, 3]) & (Tc.session == 2)].set_index(["learner", "video", "item"]).dc
        j = pd.concat([p1, p2], axis=1, keys=["s1", "s2"]).dropna()
        r_tr = float(np.corrcoef(j.s1, j.s2)[0, 1]) if len(j) > 50 else np.nan
        rows.append(dict(channel=ch, n=len(At), item_share=float(item_part.var() / tot), person_x_item_share=float(resid.var() / tot),
                         r_odd_even=r_oe, reliability_odd_even_SB=spearman_brown(r_oe), r_attend_distract=r_tr, n_retest=len(j)))
    B = pd.DataFrame(rows)
    B.to_csv(OUT / "B_anchored_reliability.csv", index=False, float_format="%.4f")
    At = T[T.condition.isin(ATTENTIVE)]
    R = pd.DataFrame({ch: double_centre(At, ch) for ch in CH}).corr()
    R.to_csv(OUT / "B_anchored_channel_correlations.csv", float_format="%.3f")
    T.to_parquet(DERIVED / "stage0_anchored_terms.parquet", index=False)
    return B, R


# ------------------------------------------------------------------ C
def part_c(d, s):
    from cairn.channels import load as load10
    from cairn.extract import CHANNELS
    ix = {c: i for i, c in enumerate(CHANNELS)}
    ep = []
    for r in s.itertuples():
        a = load10(r.uid)
        inv = a[ix["valid"]] < 0.5
        blink = a[ix["blink"]] > 0.5
        offs = a[ix["onscreen"]] < 0.5
        # run lengths of invalid episodes (bins)
        x = np.r_[0, inv.astype(int), 0]
        starts, ends = np.flatnonzero(np.diff(x) == 1), np.flatnonzero(np.diff(x) == -1)
        lens = (ends - starts) / BIN_HZ
        long_ = lens >= 1.0
        ep.append(dict(uid=r.uid, condition=r.condition, experiment=r.experiment, invalid_frac=float(inv.mean()),
                       blink_coded_frac_of_invalid=float((inv & blink).sum() / max(inv.sum(), 1)),
                       offscreen_frac_of_invalid=float((inv & offs).sum() / max(inv.sum(), 1)),
                       episodes_per_min=float(len(lens) / (len(inv) / BIN_HZ / 60)),
                       long_episodes_per_min=float(long_.sum() / (len(inv) / BIN_HZ / 60)),
                       median_episode_s=float(np.median(lens)) if len(lens) else np.nan,
                       frac_invalid_time_in_long=float(lens[long_].sum() / max(lens.sum(), 1e-9))))
    C = pd.DataFrame(ep)
    (DERIVED / "stage0_participant_level").mkdir(parents=True, exist_ok=True)
    C.to_csv(DERIVED / "stage0_participant_level" / "C_missingness_exposures.csv", index=False, float_format="%.4f")   # participant-level: git-ignored
    summ = C.groupby(C.condition.isin(ATTENTIVE).map({True: "attentive", False: "distracted"})).median(numeric_only=True)
    # head motion during invalid vs valid seconds (E2-E5)
    hm = d.merge(s[["uid", "condition"]], on="uid")
    hm = hm[hm.head_motion.notna()]
    hm["invalid"] = hm.valid < 0.5
    within = hm.groupby(["uid", "invalid"]).head_motion.median().unstack().dropna()
    head = dict(n_exposures=len(within), median_ratio_invalid_over_valid=float((within[True] / within[False]).median()),
                frac_exposures_higher_when_invalid=float((within[True] > within[False]).mean()))
    return summ, head


# ------------------------------------------------------------------ D
def part_d(d, s):
    m = d.groupby("uid")[list(CH)].mean().join(s.set_index("uid")[["qualified_participant_id", "experiment", "session", "condition", "canonical_video_id"]])
    m = m[m.experiment.isin([1, 2, 3])]
    m["distract"] = (m.condition == "arithmetic_repeat").astype(int)
    pair = m.reset_index().pivot_table(index=["qualified_participant_id", "canonical_video_id"], columns="distract", values=list(CH))
    dz = {}
    for ch in CH:
        diff = (pair[(ch, 1)] - pair[(ch, 0)]).dropna()
        dz[ch] = dict(mean_diff=float(diff.mean()), dz=float(diff.mean() / diff.std()), n_pairs=len(diff))
    fams = {"reference_free": [c for c in REF_FREE if c in CH], "reference_relative": [c for c in REF_REL if c in CH],
            "validity_only": ["valid", "onscreen", "blink"], "all": list(CH)}
    res = {}
    y = m.distract.to_numpy()
    groups = m.qualified_participant_id.to_numpy()
    for name, cols in fams.items():
        X = m[cols].to_numpy(float)
        pred = np.full(len(y), np.nan)
        for tr, te in group_kfold(groups, 5, SEED):
            Xtr, Xte = standardize(X[tr], X[te])
            w = logistic_fit(Xtr, y[tr], l2=1.0)
            pred[te] = logistic_predict(w, Xte)
        res[name] = dict(auc=auc(y, pred), n=len(y), n_learners=int(len(np.unique(groups))))
    return dz, res


# ------------------------------------------------------------------ E
def part_e(d, s, T):
    out = {}
    att = s[s.condition.isin(ATTENTIVE)]
    dev = sorted(T.video.unique())
    # (1) whole-video means -> video identity
    m = d[d.uid.isin(att.uid)].groupby("uid")[list(CH)].mean().join(att.set_index("uid")[["qualified_participant_id", "canonical_video_id", "experiment"]])
    m = m[m.canonical_video_id.isin(dev)]
    for fam, cols in (("reference_free", [c for c in REF_FREE if c in CH]), ("reference_relative", [c for c in REF_REL if c in CH])):
        out[f"whole_video_{fam}"] = _probe(m[cols].to_numpy(float), m.canonical_video_id.to_numpy(), m.qualified_participant_id.to_numpy())
    # (2) anchored moment terms (person-centred) and (3) item-centred
    At = T[T.condition.isin(ATTENTIVE)].dropna(subset=list(CH))
    for fam, cols in (("reference_free", [c for c in REF_FREE if c in CH]), ("reference_relative", [c for c in REF_REL if c in CH])):
        X = At[cols].to_numpy(float)
        out[f"moment_terms_{fam}"] = _probe(X, At.video.to_numpy(), At.learner.to_numpy())
        Xc = X - At.groupby(["video", "item"])[cols].transform("mean").to_numpy()
        out[f"moment_terms_item_centred_{fam}"] = _probe(Xc, At.video.to_numpy(), At.learner.to_numpy())
    # (4) protocol identity from item-centred moment terms within videos shown in several experiments
    multi = At[At.video.isin(At.groupby("video").experiment.nunique().loc[lambda x: x > 1].index)]
    cols = list(CH)
    Xc = multi[cols].to_numpy(float) - multi.groupby(["video", "item"])[cols].transform("mean").to_numpy()
    out["protocol_from_item_centred_moment_terms"] = _probe(Xc, multi.experiment.astype(str).to_numpy(), multi.learner.to_numpy())
    return out


def _probe(X, y, groups):
    cls, yi = np.unique(y, return_inverse=True)
    pred = np.full(len(yi), -1)
    for tr, te in group_kfold(groups, 5, SEED):
        Xtr, Xte = standardize(X[tr], X[te])
        W = softmax_fit(Xtr, yi[tr], len(cls), l2=1.0)
        pred[te] = softmax_predict(W, Xte)
    return dict(balanced_accuracy=balanced_accuracy(yi, pred), chance=1 / len(cls), n=len(yi), n_classes=len(cls))


# ------------------------------------------------------------------ H
def part_h(d, s):
    from cairn.channels import load as load10
    from cairn.extract import CHANNELS
    ix = {c: i for i, c in enumerate(CHANNELS)}
    r2 = []
    for r in s[s.condition.isin(ATTENTIVE)].itertuples():
        a = load10(r.uid)
        n = a.shape[1] // BIN_HZ * BIN_HZ
        gx = np.nanmean(a[ix["gx"], :n].reshape(-1, BIN_HZ), 1)
        gy = np.nanmean(a[ix["gy"], :n].reshape(-1, BIN_HZ), 1)
        p = by_uid(d)[r.uid].pupil_rel.to_numpy()[: len(gx)]
        gx, gy = gx[: len(p)], gy[: len(p)]
        ok = np.isfinite(gx) & np.isfinite(gy) & np.isfinite(p)
        if ok.sum() < 60:
            continue
        X = np.column_stack([np.ones(ok.sum()), gx[ok], gy[ok], gx[ok] ** 2, gy[ok] ** 2, gx[ok] * gy[ok]])
        beta, *_ = np.linalg.lstsq(X, p[ok], rcond=None)
        res = p[ok] - X @ beta
        r2.append(1 - res.var() / p[ok].var())
    return dict(median_r2_pupil_rel_on_gaze_position=float(np.median(r2)), q25=float(np.quantile(r2, .25)), q75=float(np.quantile(r2, .75)), n=len(r2))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d, s, a = load()
    A = part_a(d, s)
    print("A done", flush=True)
    B, R = part_b(d, s, a)
    print("B done", flush=True)
    C, head = part_c(d, s)
    print("C done", flush=True)
    dz, auc_d = part_d(d, s)
    print("D done", flush=True)
    T = pd.read_parquet(DERIVED / "stage0_anchored_terms.parquet")
    E = part_e(d, s, T)
    print("E done", flush=True)
    H = part_h(d, s)
    summary = dict(A_variance=A.reset_index().to_dict("records"), B_anchored=B.to_dict("records"),
                   C_missingness=C.reset_index().to_dict("records"), C_head=head, D_paired_dz=dz, D_auc=auc_d,
                   E_identity=E, H_pupil=H)
    (OUT / "signal_feasibility_summary.json").write_text(json.dumps(summary, indent=2, default=float))
    print(json.dumps({k: v for k, v in summary.items() if k in ("C_head", "D_auc", "E_identity", "H_pupil")}, indent=2, default=float))
    print(A.round(3).to_string())
    print(B.round(3).to_string())


if __name__ == "__main__":
    sys.exit(main())
