"""Per-second (1 Hz) engagement channels u_pv(t) (research plan §10), outcome-free and fold-safe.

Reference-free channels come from the learner's own 10 Hz series. Reference-relative channels
compare the learner with a *reference set* of other viewings of the same video, passed in
explicitly; :func:`reference_stats` refuses a reference set that contains the target learner,
so leave-self-out, training-fold-only and unlabelled-half-cohort regimes are all expressed by
the caller's choice of ``ref_uids`` (plan §15.3, "synchrony-reference leakage").

All rates are per second on the recording clock. Standardization is *not* done here: it is
fitted on training learners by the caller (plan §11.1).
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import pandas as pd

from .extract import CHANNELS
from .paths import BIN_HZ, SCREEN_DIAG, SERIES

IX = {c: i for i, c in enumerate(CHANNELS)}
REF_FREE = ("valid", "onscreen", "blink", "sacc", "speed", "disp5", "pupil", "head_z", "head_motion")
REF_REL = ("dist", "logdens", "rho5", "pupil_rel", "valid_rel")
ALL_CHANNELS = REF_FREE + REF_REL


@lru_cache(maxsize=4096)
def load(uid: str) -> np.ndarray:
    a = np.load(SERIES / f"{uid}.npy")
    a.setflags(write=False)
    return a


def _per_second(x: np.ndarray, n_s: int, fn) -> np.ndarray:
    x = x[: n_s * BIN_HZ].reshape(n_s, BIN_HZ)
    with np.errstate(invalid="ignore"):
        return fn(x, axis=1)


def reference_free(a: np.ndarray, n_s: int) -> pd.DataFrame:
    """Reference-free channels at 1 Hz from one exposure's 10 Hz series."""
    gx, gy = a[IX["gx"]], a[IX["gy"]]
    step = np.hypot(np.diff(gx, prepend=np.nan), np.diff(gy, prepend=np.nan)) / SCREEN_DIAG
    out = {
        "valid": _per_second(a[IX["valid"]], n_s, np.nanmean),
        "onscreen": _per_second(a[IX["onscreen"]], n_s, np.nanmean),
        "blink": _per_second(a[IX["blink"]], n_s, np.nanmean),
        "sacc": _per_second(a[IX["sacc"]], n_s, np.nansum),
        "speed": _per_second(step, n_s, np.nanmedian),
    }
    # 5 s dispersion centred on each second
    gxs = pd.Series(gx).rolling(5 * BIN_HZ, center=True, min_periods=BIN_HZ).std().to_numpy()
    gys = pd.Series(gy).rolling(5 * BIN_HZ, center=True, min_periods=BIN_HZ).std().to_numpy()
    out["disp5"] = _per_second(np.hypot(gxs, gys) / SCREEN_DIAG, n_s, np.nanmean)
    p = a[IX["pupil"]]
    with np.errstate(invalid="ignore"):
        pz = (p - np.nanmean(p)) / np.nanstd(p) if np.isfinite(p).sum() > 10 else np.full_like(p, np.nan)
    out["pupil"] = _per_second(pz, n_s, np.nanmean)
    hz = a[IX["head_z"]]
    if np.isfinite(hz).sum() > 10:
        with np.errstate(invalid="ignore"):
            out["head_z"] = _per_second((hz - np.nanmean(hz)) / np.nanstd(hz), n_s, np.nanmean)
        hm = np.sqrt(sum(np.diff(a[IX[c]], prepend=np.nan) ** 2 for c in ("head_x", "head_y", "head_z")))
        out["head_motion"] = _per_second(hm, n_s, np.nanmedian)
    else:
        out["head_z"] = np.full(n_s, np.nan)
        out["head_motion"] = np.full(n_s, np.nan)
    return pd.DataFrame(out)


@dataclass
class RefStats:
    uids: tuple
    people: frozenset
    med_x: np.ndarray        # per second
    med_y: np.ndarray
    spread: np.ndarray       # median distance of reference gaze to the reference median (px)
    pts: np.ndarray          # reference x, y per second: (n_ref, n_s, 2)
    bw: np.ndarray           # KDE bandwidth per second (px), from the reference only
    course_x: np.ndarray     # 10 Hz reference mean gaze course
    course_y: np.ndarray
    pupil: np.ndarray        # per-second reference mean pupil (z within recording)
    valid: np.ndarray


def reference_stats(ref_uids: list[str], people: dict[str, str], n_s: int, exclude_person: str | None = None) -> RefStats:
    """Statistics of a reference set. ``people`` maps uid -> learner id; the reference must not
    contain ``exclude_person`` (raises), which makes self-inclusion impossible by construction."""
    if exclude_person is not None and any(people[u] == exclude_person for u in ref_uids):
        raise ValueError("reference set contains the target learner")
    arrs = [load(u) for u in ref_uids]
    n_b = n_s * BIN_HZ

    def stack(c):
        s = np.full((len(arrs), n_b), np.nan)
        for j, a in enumerate(arrs):
            m = min(n_b, a.shape[1])
            s[j, :m] = a[IX[c], :m]
        return s

    gx, gy = stack("gx"), stack("gy")
    sx = np.nanmean(gx.reshape(len(arrs), n_s, BIN_HZ), axis=2)
    sy = np.nanmean(gy.reshape(len(arrs), n_s, BIN_HZ), axis=2)
    with np.errstate(invalid="ignore"):
        mx, my = np.nanmedian(sx, 0), np.nanmedian(sy, 0)
        spread = np.nanmedian(np.hypot(sx - mx, sy - my), 0)
        n_ok = np.isfinite(sx).sum(0)
        sd = np.sqrt((np.nanvar(sx, 0) + np.nanvar(sy, 0)) / 2)
        bw = np.maximum(1.06 * sd * np.maximum(n_ok, 2) ** (-1 / 5), 20.0)
        pz = stack("pupil")
        pz = (pz - np.nanmean(pz, 1, keepdims=True)) / np.nanstd(pz, 1, keepdims=True)
        pupil = np.nanmean(np.nanmean(pz.reshape(len(arrs), n_s, BIN_HZ), 2), 0)
        valid = np.nanmean(np.nanmean(stack("valid").reshape(len(arrs), n_s, BIN_HZ), 2), 0)
    return RefStats(tuple(ref_uids), frozenset(people[u] for u in ref_uids), mx, my, spread,
                    np.stack([sx, sy], -1), bw, np.nanmean(gx, 0), np.nanmean(gy, 0), pupil, valid)


def reference_relative(a: np.ndarray, rf: pd.DataFrame, ref: RefStats, n_s: int) -> pd.DataFrame:
    gx, gy = a[IX["gx"], : n_s * BIN_HZ], a[IX["gy"], : n_s * BIN_HZ]
    with np.errstate(invalid="ignore"):
        px = np.nanmean(gx.reshape(n_s, BIN_HZ), 1)
        py = np.nanmean(gy.reshape(n_s, BIN_HZ), 1)
        dist = np.hypot(px - ref.med_x, py - ref.med_y) / np.maximum(ref.spread, 10.0)
        # Gaussian KDE log-density of the learner's gaze under the reference at each second
        dx = (px[None, :] - ref.pts[..., 0]) / ref.bw[None, :]
        dy = (py[None, :] - ref.pts[..., 1]) / ref.bw[None, :]
        k = np.exp(-0.5 * (dx ** 2 + dy ** 2)) / (2 * np.pi * ref.bw[None, :] ** 2)
        dens = np.nanmean(k, 0)
        logdens = np.log(dens + 1e-12) + 2 * np.log(SCREEN_DIAG)          # dimensionless (relative to the screen)
        logdens[~np.isfinite(px)] = np.nan
    # rolling 5 s correlation with the reference mean course (x and y averaged)
    w = 5 * BIN_HZ
    rho = []
    for g, c in ((gx, ref.course_x[: n_s * BIN_HZ]), (gy, ref.course_y[: n_s * BIN_HZ])):
        s1, s2 = pd.Series(g), pd.Series(c)
        rho.append(s1.rolling(w, center=True, min_periods=2 * BIN_HZ).corr(s2).to_numpy())
    rho5 = _per_second(np.nanmean(np.vstack(rho), 0), n_s, np.nanmean)
    return pd.DataFrame(dict(dist=dist, logdens=logdens, rho5=rho5,
                             pupil_rel=rf["pupil"].to_numpy() - ref.pupil,
                             valid_rel=rf["valid"].to_numpy() - ref.valid))


def channels(uid: str, ref: RefStats, n_s: int) -> pd.DataFrame:
    a = load(uid)
    rf = reference_free(a, n_s)
    rr = reference_relative(a, rf, ref, n_s)
    out = pd.concat([rf, rr], axis=1)
    out.insert(0, "t", np.arange(n_s))
    return out
