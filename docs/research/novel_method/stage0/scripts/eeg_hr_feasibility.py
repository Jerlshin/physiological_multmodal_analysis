"""Stage 0c - does time-resolved EEG (and HR) carry reliable moment-level information that is
not reducible to ocular activity? Outcome-free; development data only (E3 attentive tested
exposures in the G01-R processed-route cache: 64-ch EEG, 128 Hz, centred, invalid samples 0;
2 Hz instantaneous HR).

EEG: two-fold over learners. CorrCA (G01-R formulation: pooled within- and between-subject
covariance, shrinkage gamma = 0.5) is fitted on one half and applied to the other; windowed
ISC (10 s and 5 s) of components 1-3 is computed within the held-out half (leave-one-out
reference). Each person x window matrix is decomposed (person / window / residual).
Reliability of the residual: (i) component 1 vs component 2; (ii) the same component against two
disjoint reference halves. Coupling: correlation of EEG-ISC residuals with ocular residuals
(validity, blinks, saccades, gaze alignment) and the share of EEG-ISC residual variance left
after regressing those out, with its reliability.

HR: windowed deviation from the leave-one-out peer HR course; decomposition; odd/even
reliability; coupling with ocular residuals.
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd
from scipy.linalg import eigh

from cairn.paths import DERIVED, STAGE0_EVIDENCE
from cairn.stats import spearman_brown, two_way, variance_shares

CACHE = DERIVED.parent / "g01r" / "cache" / "processed"
FS = 128
SEED = 5
GAMMA = 0.5
OUT = STAGE0_EVIDENCE / "signal"


def eeg(uid):
    x = np.load(CACHE / "eeg" / f"{uid}.npy", mmap_mode="r")
    v = np.load(CACHE / "eeg" / f"{uid}_valid.npy")
    return x, v


def corrca_fit(groups: dict, members: set):
    """groups: video -> list of uids; members: uids allowed for fitting."""
    D = None
    Rw = Rb = None
    for vid, uids in groups.items():
        us = [u for u in uids if u in members]
        if len(us) < 2:
            continue
        S = None
        W_ = None
        T = min(eeg(u)[0].shape[0] for u in us)
        for u in us:
            x = np.asarray(eeg(u)[0][:T], dtype=np.float64)
            D = x.shape[1]
            if S is None:
                S = np.zeros_like(x)
                W_ = np.zeros((D, D))
            S += x
            W_ += x.T @ x
        Rw = W_ if Rw is None else Rw + W_
        between = (S.T @ S - W_) / (len(us) - 1)
        Rb = between if Rb is None else Rb + between
    Rb = (Rb + Rb.T) / 2
    Rw = (Rw + Rw.T) / 2
    Rws = (1 - GAMMA) * Rw + GAMMA * np.trace(Rw) / D * np.eye(D)
    ev, V = eigh(Rb, Rws)
    o = np.argsort(ev)[::-1][:3]
    return V[:, o], ev[o]


def windowed_isc(Y: np.ndarray, V: np.ndarray, ref_idx: list[np.ndarray], win: int):
    """Y: people x T (one component), V: people x T validity. ref_idx[i]: reference rows for person i.
    Returns people x windows Pearson r with the reference mean in each window."""
    P, T = Y.shape
    nw = T // win
    out = np.full((P, nw), np.nan)
    Yz = np.where(V, Y, np.nan)
    for i in range(P):
        ref = np.nanmean(Yz[ref_idx[i]], axis=0)
        a = Yz[i, : nw * win].reshape(nw, win)
        b = ref[: nw * win].reshape(nw, win)
        ok = np.isfinite(a) & np.isfinite(b)
        cnt = ok.sum(1)
        a0, b0 = np.where(ok, a, 0), np.where(ok, b, 0)
        with np.errstate(invalid="ignore", divide="ignore"):
            ma, mb = a0.sum(1) / cnt, b0.sum(1) / cnt
            cov = (a0 * b0).sum(1) / cnt - ma * mb
            va = (a0 * a0).sum(1) / cnt - ma ** 2
            vb = (b0 * b0).sum(1) / cnt - mb ** 2
            r = cov / np.sqrt(va * vb)
        r[cnt < 0.5 * win] = np.nan
        out[i] = r
    return out


def resid(M):
    return two_way(M)[3]


def agree(R1, R2):
    a, b = R1.ravel(), R2.ravel()
    ok = np.isfinite(a) & np.isfinite(b)
    return float(np.corrcoef(a[ok], b[ok])[0, 1]) if ok.sum() > 30 else np.nan


def ocular_windows(uids, win_s, nw):
    ch = pd.read_parquet(DERIVED / "channels_1hz.parquet", columns=["uid", "t", "valid", "blink", "sacc", "rho5", "dist"])
    ch = ch[ch.uid.isin(uids)]
    out = {}
    for c in ("valid", "blink", "sacc", "rho5", "dist"):
        M = ch.pivot(index="uid", columns="t", values=c).reindex(uids).to_numpy(float)
        n = min(nw, M.shape[1] // win_s)
        with np.errstate(invalid="ignore"):
            W = np.nanmean(M[:, : n * win_s].reshape(len(uids), n, win_s), 2)
        if n < nw:
            W = np.hstack([W, np.full((len(uids), nw - n), np.nan)])
        out[c] = W
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    s = pd.read_parquet(DERIVED / "channels_scope.parquet")
    e3 = s[(s.experiment == 3) & (s.session == 1)]
    e3 = e3[[(CACHE / "eeg" / f"{u}.npy").exists() for u in e3.uid]]
    groups = {v: list(g.uid) for v, g in e3.groupby("canonical_video_id")}
    people = np.array(sorted(e3.qualified_participant_id.unique()))
    rng = np.random.default_rng(SEED)
    rng.shuffle(people)
    halves = [set(people[: len(people) // 2]), set(people[len(people) // 2:])]
    who = dict(zip(e3.uid, e3.qualified_participant_id))
    rows, coupling = [], []
    for fold in (0, 1):
        fit_members = {u for u in e3.uid if who[u] in halves[fold]}
        W, ev = corrca_fit(groups, fit_members)
        for vid, uids in groups.items():
            test = [u for u in uids if who[u] in halves[1 - fold]]
            if len(test) < 6:
                continue
            T = min(eeg(u)[0].shape[0] for u in test)
            Ys = np.zeros((3, len(test), T))
            Vs = np.zeros((len(test), T), bool)
            for i, u in enumerate(test):
                x, v = eeg(u)
                Ys[:, i] = (np.asarray(x[:T], dtype=np.float64) @ W).T
                Vs[i] = v[:T]
            loo = [np.array([j for j in range(len(test)) if j != i]) for i in range(len(test))]
            half_a = [np.array([j for j in range(len(test)) if j != i and j % 2 == 0]) for i in range(len(test))]
            half_b = [np.array([j for j in range(len(test)) if j != i and j % 2 == 1]) for i in range(len(test))]
            for win_s in (10, 5):
                win = win_s * FS
                isc = [windowed_isc(Ys[c], Vs, loo, win) for c in range(3)]
                isc_sum = np.nansum(np.stack(isc), 0)
                isc_sum[np.all(np.isnan(np.stack(isc)), 0)] = np.nan
                ra = windowed_isc(Ys[0], Vs, half_a, win)
                rb = windowed_isc(Ys[0], Vs, half_b, win)
                vs = variance_shares(isc_sum)
                r_c12 = agree(resid(isc[0]), resid(isc[1]))
                r_ref = agree(resid(ra), resid(rb))
                rows.append(dict(fold=fold, video=vid, window_s=win_s, n=len(test), corrca_eig=list(np.round(ev, 4)),
                                 **{f"isc_{k}": v for k, v in vs.items()},
                                 mean_isc_c1=float(np.nanmean(isc[0])),
                                 r_comp1_comp2=r_c12, rel_comp_SB=spearman_brown(r_c12),
                                 r_refA_refB=r_ref, rel_ref_SB=spearman_brown(r_ref)))
                if win_s == 10:
                    oc = ocular_windows(test, win_s, isc_sum.shape[1])
                    Re = resid(isc_sum)
                    Ro = {c: resid(oc[c]) for c in oc}
                    cors = {c: agree(Re, Ro[c]) for c in Ro}
                    X = np.column_stack([Ro[c].ravel() for c in Ro])
                    y = Re.ravel()
                    ok = np.isfinite(y) & np.all(np.isfinite(X), 1)
                    beta, *_ = np.linalg.lstsq(np.column_stack([np.ones(ok.sum()), X[ok]]), y[ok], rcond=None)
                    r2 = 1 - np.var(y[ok] - np.column_stack([np.ones(ok.sum()), X[ok]]) @ beta) / np.var(y[ok])
                    # reliability of the ocular-residualized EEG part (component 1 vs 2)
                    def resid_on_ocular(M):
                        R = resid(M).ravel()
                        okk = np.isfinite(R) & np.all(np.isfinite(X), 1)
                        b, *_ = np.linalg.lstsq(np.column_stack([np.ones(okk.sum()), X[okk]]), R[okk], rcond=None)
                        out = np.full_like(R, np.nan)
                        out[okk] = R[okk] - np.column_stack([np.ones(okk.sum()), X[okk]]) @ b
                        return out.reshape(M.shape)
                    r_c12_res = agree(resid_on_ocular(isc[0]), resid_on_ocular(isc[1]))
                    coupling.append(dict(fold=fold, video=vid, n=len(test), **{f"r_eeg_{c}": v for c, v in cors.items()},
                                         r2_eeg_on_ocular=float(r2), r_comp1_comp2_after_ocular=r_c12_res))
        print("fold", fold, "done", flush=True)
    E = pd.DataFrame(rows)
    E.to_csv(OUT / "F_eeg_windowed_isc.csv", index=False, float_format="%.4f")
    Cp = pd.DataFrame(coupling)
    Cp.to_csv(OUT / "F_eeg_ocular_coupling.csv", index=False, float_format="%.4f")
    # ---------------- HR
    hr_rows = []
    for vid, uids in groups.items():
        hs = [np.load(CACHE / "hr" / f"{u}.npy") for u in uids if (CACHE / "hr" / f"{u}.npy").exists()]
        if len(hs) < 8:
            continue
        T = min(len(h) for h in hs)
        H = np.vstack([h[:T] for h in hs]).astype(float)
        with np.errstate(invalid="ignore"):
            Hz = (H - np.nanmean(H, 1, keepdims=True)) / np.nanstd(H, 1, keepdims=True)
        dev = np.vstack([Hz[i] - np.nanmean(np.delete(Hz, i, 0), 0) for i in range(len(Hz))])
        for win_s in (10, 30):
            win = win_s * 2
            nw = T // win
            with np.errstate(invalid="ignore"):
                Mw = np.nanmean(dev[:, : nw * win].reshape(len(Hz), nw, win), 2)
                Mo = np.nanmean(dev[:, : nw * win].reshape(len(Hz), nw, win)[:, :, 0::2], 2)
                Me = np.nanmean(dev[:, : nw * win].reshape(len(Hz), nw, win)[:, :, 1::2], 2)
            vsh = variance_shares(np.nanmean(Hz[:, : nw * win].reshape(len(Hz), nw, win), 2))
            r_oe = agree(resid(Mo), resid(Me))
            hr_rows.append(dict(video=vid, window_s=win_s, n=len(Hz), **{f"hr_{k}": v for k, v in vsh.items()},
                                r_odd_even=r_oe, rel_odd_even_SB=spearman_brown(r_oe)))
    Hr = pd.DataFrame(hr_rows)
    Hr.to_csv(OUT / "G_hr_windowed.csv", index=False, float_format="%.4f")
    summ = dict(
        eeg=E.groupby("window_s")[["isc_person", "isc_moment", "isc_residual", "isc_resid_lag1", "mean_isc_c1", "r_comp1_comp2", "rel_comp_SB", "r_refA_refB", "rel_ref_SB"]].median().to_dict("index"),
        eeg_ocular=Cp.median(numeric_only=True).drop(["fold", "n"]).to_dict(),
        hr=Hr.groupby("window_s")[["hr_person", "hr_moment", "hr_residual", "hr_resid_lag1", "r_odd_even", "rel_odd_even_SB"]].median().to_dict("index"),
        n_cells=len(e3), n_learners=int(len(people)))
    (OUT / "F_G_eeg_hr_summary.json").write_text(json.dumps(summ, indent=2, default=float))
    print(json.dumps(summ, indent=2, default=float))


if __name__ == "__main__":
    sys.exit(main())
