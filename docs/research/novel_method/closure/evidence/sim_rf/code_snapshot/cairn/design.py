"""Item-level incidence per analysis set (plan §15.2; Stage-1 spec §1.1, §2.2), outcome-free.

Cells come from availability flags only: the frozen G01-R eligibility flag
(``gate_behavior_eligible``, read through :func:`g01r.population.tested_cells`, which whitelists
flag columns) and the gaze basic-QC flag (gaze correction fraction <= 0.50). Items come from the
item bank (texts and categories; no responses) and an anchor table. No outcome value, response,
score or correctness key is read here.

Anchor moments
--------------
Items whose anchor centres lie within 10 s of each other (single linkage, the Stage-0 counting
rule) form one *moment*. Moments are the unit of the anchor-randomization null T2 (S0-D14):
items that share a span keep sharing it under every permutation.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .anchors import item_bank
from .gate import SCOPES
from .paths import BIN_HZ, DERIVED, VIDEOS, sha256_file
from .paths_stage1 import PROVISIONAL_ANCHORS

MOMENT_GAP_S = 10.0
# Kernel grid (plan §10 lag delta and extra width omega; spec §2.2). A kernel moves each hard anchor window by
# `lag` seconds and widens it by `pad` seconds on both sides. One kernel is shared by R and C items (S1-D07).
# Selected in development (Stage 2, <= 20 configurations, nested CV) and frozen for the lock (S1-D11).
KERNEL_DEFAULT = (0.0, 0.0)
KERNEL_GRID = tuple((lag, pad) for lag in (-5.0, 0.0, 5.0) for pad in (0.0, 5.0, 10.0, 20.0))

# Plan §15.2. A pooled lock (E4 + E5) is one of the declared Stage-1 redesign options (spec §1.7).
SETS = {
    "development": SCOPES["development"],
    "locked_primary": SCOPES["locked_primary"],
    "locked_secondary": SCOPES["locked_secondary"],
    "locked_pooled": SCOPES["locked_primary"] + SCOPES["locked_secondary"],
    "reserved_descriptive": SCOPES["reserved_descriptive"],
}
# (learners, cells, videos) with eligible outcome flag and gaze QC <= 0.50 (plan §15.2). The plan's
# reserved-descriptive row says 26 learners; the flags give 24 (47 cells and 2 videos agree): S1-I02.
EXPECTED_COUNTS = {
    "development": (55, 229, 9),
    "locked_primary": (39, 112, 3),
    "locked_secondary": (47, 129, 3),
    "locked_pooled": (86, 241, 3),
    "reserved_descriptive": (24, 47, 2),
}
LOCKED_EXPERIMENTS = {4, 5}


def eligible_cells() -> pd.DataFrame:
    """Tested cells with the eligibility and gaze-QC *flags* (frozen G01-R population code)."""
    from g01r.population import tested_cells

    c = tested_cells()
    c = c[c.eligible_outcome & c.gaze_basic_qc.fillna(False).astype(bool)]
    return c[["experiment", "participant_id", "qualified_participant_id", "session", "local_stimulus_id",
              "canonical_video_id"]].reset_index(drop=True)


def cells(set_name: str) -> pd.DataFrame:
    """Cells of an analysis set, joined to the outcome-free 10 Hz series manifest."""
    spec = SETS[set_name]
    c = eligible_cells()
    keep = pd.Series(False, index=c.index)
    for s in spec:
        m = c.experiment == s["experiment"]
        if "videos" in s:
            m &= c.canonical_video_id.isin(s["videos"])
        keep |= m
    c = c[keep]
    man = pd.read_parquet(DERIVED / "series10_manifest.parquet",
                          columns=["experiment", "participant_id", "session", "local_stimulus_id", "uid", "status",
                                   "n_bins", "valid_fraction"])
    c = c.merge(man, on=["experiment", "participant_id", "session", "local_stimulus_id"], how="left", validate="one_to_one")
    if c.uid.isna().any() or (c.status != "ok").any():
        raise AssertionError(f"{set_name}: cells without an ok 10 Hz series")
    c = c.rename(columns={"qualified_participant_id": "person", "canonical_video_id": "video"})
    c["video_name"] = c.video.map(VIDEOS)
    got = (c.person.nunique(), len(c), c.video.nunique())
    if got != EXPECTED_COUNTS[set_name]:
        raise AssertionError(f"{set_name}: incidence {got} != plan §15.2 {EXPECTED_COUNTS[set_name]}")
    return c.sort_values(["experiment", "person", "video"]).reset_index(drop=True)


def anchor_table(path=PROVISIONAL_ANCHORS) -> pd.DataFrame:
    a = pd.read_csv(path)
    need = {"canonical_video_id", "video", "item", "question_no", "category", "k_keyed", "anchorable",
            "rec_start_s", "rec_end_s", "rec_centre_s"}
    missing = need - set(a.columns)
    if missing:
        raise ValueError(f"anchor table lacks {sorted(missing)}")
    for c in a.columns:
        if c.lower() in {"answer", "is_correct", "score", "correct", "response", "recomputed_exact_correct"}:
            raise AssertionError(f"anchor table carries an outcome-like column: {c}")
    return a


def moment_groups(centres: np.ndarray, gap: float = MOMENT_GAP_S) -> np.ndarray:
    """Group index per centre: a new group starts where consecutive sorted centres differ by > gap."""
    order = np.argsort(centres, kind="stable")
    g = np.zeros(len(centres), int)
    if len(centres):
        steps = np.r_[0, (np.diff(centres[order]) > gap).astype(int)]
        g[order] = np.cumsum(steps)
    return g


@dataclass
class Incidence:
    """Item-level incidence of one analysis set. No outcomes."""

    set_name: str
    cells: pd.DataFrame            # one row per learner x video cell
    rows: pd.DataFrame             # one row per (cell, item)
    n_s: dict                      # video -> seconds used on the recording clock
    anchor_sha256: str
    anchor_provisional: bool
    meta: dict = field(default_factory=dict)

    @property
    def persons(self) -> np.ndarray:
        return self.cells.person.unique()

    def summary(self) -> dict:
        r = self.rows
        anch = r[r.anchorable]
        return dict(set=self.set_name, learners=int(self.cells.person.nunique()), cells=len(self.cells),
                    videos=int(self.cells.video.nunique()), item_responses=len(r), anchorable_responses=len(anch),
                    items=int(r.item_key.nunique()), anchorable_items=int(anch.item_key.nunique()),
                    distinct_moments=int(anch.drop_duplicates(["video", "moment"]).shape[0]),
                    anchor_sha256=self.anchor_sha256, anchor_provisional=self.anchor_provisional,
                    kernel=list(self.meta.get("kernel", KERNEL_DEFAULT)))


def build(set_name: str, anchors_path=PROVISIONAL_ANCHORS, provisional: bool = True,
          kernel: tuple = KERNEL_DEFAULT) -> Incidence:
    c = cells(set_name)
    a = anchor_table(anchors_path)
    bank = item_bank()
    n_items = bank.groupby("canonical_video_id").size()
    n_s = {v: int(g.n_bins.min()) // BIN_HZ for v, g in c.groupby("video")}
    # anchor moments per video (anchorable items only)
    a = a.copy()
    a["moment"] = -1
    for v, g in a[a.anchorable].groupby("canonical_video_id"):
        a.loc[g.index, "moment"] = moment_groups(g.rec_centre_s.to_numpy(float))
    a = a.set_index(["canonical_video_id", "item"])
    rows = []
    for cell in c.itertuples():
        items = bank[bank.canonical_video_id == cell.video]
        if len(items) != n_items[cell.video]:
            raise AssertionError("item bank inconsistent")
        for it in items.itertuples():
            an = a.loc[(cell.video, it.item)]
            anchorable = bool(an.anchorable)
            start, end = (float(an.rec_start_s), float(an.rec_end_s)) if anchorable else (np.nan, np.nan)
            if anchorable and end > n_s[cell.video] + 1.0:
                raise AssertionError(f"anchor {cell.video_name} {it.item} ends after the common recording span")
            rows.append(dict(uid=cell.uid, person=cell.person, experiment=int(cell.experiment), video=cell.video,
                             video_name=cell.video_name, item=int(it.item), question_no=int(it.question_no),
                             item_key=f"e{int(cell.experiment)}:{cell.video_name}:{int(it.item)}",
                             category=it.category, k_keyed=int(it.k_keyed), anchorable=anchorable,
                             start=start, end=min(end, n_s[cell.video]) if anchorable else np.nan,
                             moment=int(an.moment) if anchorable else -1,
                             anchor_pos=float(an.rec_centre_s) / n_s[cell.video] if anchorable else np.nan,
                             quiz_pos=(int(it.item) - 1) / (n_items[cell.video] - 1)))
    r = pd.DataFrame(rows)
    _assert_set_definition(set_name, c, r)
    from .clock import assert_anchors_on_pass_seconds
    assert_anchors_on_pass_seconds(r)              # spec §3 test 7: no anchor on a G-TL FAIL second
    kernel = tuple(float(k) for k in kernel)
    if kernel != KERNEL_DEFAULT:
        r = apply_kernel(r, kernel, n_s)
    return Incidence(set_name, c, r, n_s, sha256_file(anchors_path), provisional, meta=dict(kernel=kernel))


def apply_kernel(r: pd.DataFrame, kernel: tuple, n_s: dict) -> pd.DataFrame:
    """Pooling windows of the anchorable rows under kernel (lag, pad), clipped to the recording.
    Moment identity and anchor position stay those of the anchors themselves, so the moment-relocation
    and circular-shift nulls are unchanged in form."""
    lag, pad = kernel
    if pad < 0:
        raise ValueError("pad must be >= 0")
    r = r.copy()
    m = r.anchorable.to_numpy()
    hi = r.video.map(n_s).to_numpy(float)
    start = np.clip(r.start.to_numpy() + lag - pad, 0.0, hi)
    end = np.clip(r.end.to_numpy() + lag + pad, 0.0, hi)
    if (end[m] - start[m] < 1.0).any():
        raise AssertionError(f"kernel {kernel} leaves a window shorter than 1 s")
    r.loc[m, "start"] = start[m]
    r.loc[m, "end"] = end[m]
    return r


def _assert_set_definition(set_name: str, c: pd.DataFrame, r: pd.DataFrame) -> None:
    exps = set(c.experiment)
    if set_name == "development":
        assert exps == {1, 3} and not (exps & LOCKED_EXPERIMENTS), "development must be E1 + E3 only"
        e1 = set(c[c.experiment == 1].video)
        assert e1 == set(SCOPES["development"][1]["videos"]), "E1 development videos"
    elif set_name == "locked_primary":
        assert exps == {4}
    elif set_name == "locked_secondary":
        assert exps == {5}
    elif set_name == "locked_pooled":
        assert exps == {4, 5}
    assert r.groupby("uid").item.nunique().ge(11).all(), "every cell carries all items of its video"
    assert not r.duplicated(["uid", "item"]).any()
