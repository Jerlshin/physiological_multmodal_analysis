"""Recording clock <-> public-source clock from the Stage-0a timeline (outcome-free; spec §3 test 7).

Within a timeline segment the map is a constant shift:

    source_time = recording_time + latency_corrected_offset_s

and segments of one source never overlap (removal-only edits), so the inverse is unique.
:func:`window_pass_fraction` is the share of a recording window's seconds that passed gate G-TL;
anchors in FAIL seconds are rejected by :func:`assert_anchors_on_pass_seconds`.
"""
from __future__ import annotations

import math

import pandas as pd

from .paths import STAGE0_EVIDENCE

PASS = ("PASS-A", "PASS-B")


def table() -> pd.DataFrame:
    return pd.read_csv(STAGE0_EVIDENCE / "timeline_table.csv")


def seconds() -> pd.DataFrame:
    return pd.read_csv(STAGE0_EVIDENCE / "timeline_seconds.csv")


def rec_to_source(video_id: str, rec_s: float, tab: pd.DataFrame | None = None) -> tuple[str, float]:
    tab = table() if tab is None else tab
    seg = tab[(tab.canonical_video_id == video_id) & (tab.rec_start_s <= rec_s) & (rec_s < tab.rec_end_s)]
    if len(seg) != 1:
        raise ValueError(f"{video_id}: recording time {rec_s} is in {len(seg)} segments")
    r = seg.iloc[0]
    return r.source, float(rec_s + r.latency_corrected_offset_s)


def source_to_rec(video_id: str, source: str, src_s: float, tab: pd.DataFrame | None = None) -> float:
    tab = table() if tab is None else tab
    seg = tab[(tab.canonical_video_id == video_id) & (tab.source == source) & (tab.video_start_s <= src_s) & (src_s < tab.video_end_s)]
    if len(seg) != 1:
        raise ValueError(f"{video_id}/{source}: source time {src_s} is shown in {len(seg)} segments")
    r = seg.iloc[0]
    return float(src_s - r.latency_corrected_offset_s)


def window_pass_fraction(video_id: str, start: float, end: float, sec: pd.DataFrame | None = None) -> float:
    sec = seconds() if sec is None else sec
    s = sec[(sec.canonical_video_id == video_id) & (sec.rec_s >= math.floor(start)) & (sec.rec_s < math.ceil(end))]
    return float(s.status.isin(PASS).mean()) if len(s) else 0.0


def assert_anchors_on_pass_seconds(rows: pd.DataFrame, sec: pd.DataFrame | None = None) -> None:
    """Raise if any anchorable item's recording window touches a second that failed G-TL."""
    sec = seconds() if sec is None else sec
    a = rows[rows.anchorable].drop_duplicates(["video", "item"])
    bad = [(r.video_name, r.item) for r in a.itertuples() if window_pass_fraction(r.video, r.start, r.end, sec) < 1.0]
    if bad:
        raise AssertionError(f"anchors on G-TL FAIL seconds: {bad}")
