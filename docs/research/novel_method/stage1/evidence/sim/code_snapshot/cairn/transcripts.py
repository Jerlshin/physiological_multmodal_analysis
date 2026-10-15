"""Timed transcripts of the public stimulus videos, mapped onto the BBBD recording clock.

Captions come from YouTube (creator-provided English tracks where they exist, otherwise the
automatic English track) and stay in git-ignored ``data/stimuli``: only derived timing, cue
hashes and short span references enter the repository. The mapping to the recording clock
uses the Stage-0a timeline table; cues in removed source material are marked ``shown=False``.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from .paths import STAGE0_EVIDENCE, YOUTUBE, sha256_bytes

TRACK_PREFERENCE = ("en", "en-GB", "en-orig")


def caption_track(source: str) -> tuple[Path, str]:
    info = json.loads((YOUTUBE / source / f"{source}.info.json").read_text())
    manual = [k for k in (info.get("subtitles") or {}) if k.startswith("en")]
    kind = "manual" if manual else "auto"
    for t in (TRACK_PREFERENCE if manual else ("en-orig", "en")):
        p = YOUTUBE / source / f"{source}.{t}.json3"
        if p.exists():
            return p, f"{kind}:{t}"
    raise FileNotFoundError(source)


def cues(source: str, max_s: float = 6.0) -> pd.DataFrame:
    """Caption cues (start, end in source seconds, text); auto tracks are re-chunked from word timings."""
    path, track = caption_track(source)
    ev = json.loads(path.read_text())["events"]
    words = []
    for e in ev:
        if "segs" not in e:
            continue
        t0 = e["tStartMs"] / 1000
        for s in e["segs"]:
            txt = s.get("utf8", "")
            if txt.strip() == "":
                continue
            words.append((t0 + s.get("tOffsetMs", 0) / 1000, txt, e.get("dDurationMs", 0) / 1000 + t0))
    rows, cur = [], None
    for t, txt, ev_end in words:
        txt = re.sub(r"\s+", " ", txt.replace("\n", " "))
        if cur is None or t - cur["start"] > max_s or (track.startswith("manual") and t != cur["last_t"] and cur["text"].rstrip().endswith((".", "?", "!"))):
            if cur:
                rows.append(cur)
            cur = dict(start=t, end=ev_end, text=txt.strip(), last_t=t)
        else:
            cur["text"] = (cur["text"] + " " + txt.strip()).strip()
            cur["end"] = max(cur["end"], ev_end)
            cur["last_t"] = t
    if cur:
        rows.append(cur)
    df = pd.DataFrame(rows).drop(columns="last_t")
    df["end"] = [min(e, n) for e, n in zip(df.end, list(df.start[1:]) + [df.end.iloc[-1]])]
    df.insert(0, "source", source)
    df.insert(1, "track", track)
    df["text_sha256"] = [sha256_bytes(t.encode()) for t in df.text]
    return df


def to_recording(video_id: str, source: str, tau: float, table: pd.DataFrame | None = None) -> float | None:
    """Recording time of source time ``tau`` (s) under the Stage-0a timeline; None if not shown."""
    t = table if table is not None else pd.read_csv(STAGE0_EVIDENCE / "timeline_table.csv")
    seg = t[(t.canonical_video_id == video_id) & (t.source == source) & (t.video_start_s <= tau) & (tau < t.video_end_s)]
    if seg.empty:
        return None
    r = seg.iloc[0]
    return float(r.rec_start_s + (tau - r.video_start_s))


def transcript(video_id: str, sources: list[str]) -> pd.DataFrame:
    table = pd.read_csv(STAGE0_EVIDENCE / "timeline_table.csv")
    sec = pd.read_csv(STAGE0_EVIDENCE / "timeline_seconds.csv")
    sec = sec[sec.canonical_video_id == video_id].set_index("rec_s")
    out = []
    for src in sources:
        c = cues(src)
        for r in c.itertuples():
            a = to_recording(video_id, src, r.start, table)
            b = to_recording(video_id, src, max(r.start, r.end - 0.01), table)
            status = None
            if a is not None:
                k = int(min(max(a, 0), sec.index.max()))
                status = sec.loc[k, "status"]
            out.append(dict(canonical_video_id=video_id, source=src, track=r.track, src_start_s=round(r.start, 2), src_end_s=round(r.end, 2),
                            rec_start_s=None if a is None else round(a, 2), rec_end_s=None if b is None else round(b, 2),
                            shown=a is not None, timeline_status=status, text=r.text, text_sha256=r.text_sha256))
    df = pd.DataFrame(out).sort_values(["rec_start_s", "source", "src_start_s"], na_position="last").reset_index(drop=True)
    df.insert(1, "cue", range(1, len(df) + 1))
    return df
