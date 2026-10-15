"""Stage 0b: outcome-blind item -> content anchors.

Reads only item texts (question, options, number of keyed options, R/C category), the public
transcripts and the Stage-0a timeline. No learner answer, score or correctness is read.

Raters
------
* **R1** - deterministic lexical retriever (TF-IDF cosine between the item and sliding caption
  windows). Reproducible; a non-binding proposer.
* **R2** - LLM-assisted provisional annotation (docs/.../annotation/anchors_R2_llm_provisional.csv).
  Non-binding; it is *not* a human annotator.
* **H1, H2** - two independent human annotators following ANNOTATION_PROTOCOL.md (not yet done).

Only an adjudicated H1/H2 set that satisfies gate G-AN can be frozen (:func:`freeze`).
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .paths import ITEM_BANK, SOURCES, STAGE0, STAGE0_EVIDENCE, STIMULI, VIDEOS, sha256_bytes, sha256_file

NAME_TO_ID = {v: k for k, v in VIDEOS.items()}
BANK_NAMES = {"Stars": "Stars", "Lightbulbs": "Lightbulbs", "Immune": "Immune", "Internet": "Internet",
              "Birth rate": "Birth rate", "Mosquitoes": "Mosquitoes", "Related": "Related",
              "Work-energy": "Work-energy", "Capacitors": "Capacitors", "Planets": "Planets", "Enzymes": "Enzymes"}
LOCALIZED_MAX_S = 45.0          # protocol: one contiguous span of at most 45 s
GAN_CENTRE_S = 10.0             # gate G-AN (plan §11.2): median centre difference <= 10 s
GAN_IOU = 0.4                   # and median IoU >= 0.4 for localized items


# ----------------------------------------------------------------------------- items
def item_bank() -> pd.DataFrame:
    """The 131 post-test items: text, options, number of keyed options, category. No responses."""
    rows = json.loads(ITEM_BANK.read_text())["Questions"]
    head = rows[0]
    recs = [dict(zip(head, r)) for r in rows[1:] if len(r) >= 17 and r[0] != "Video_no"]
    df = pd.DataFrame(recs)
    df = df.rename(columns={"Video_nick_name": "video", "Local_Question_no": "item", "Question_no": "question_no",
                            "Category": "category", "No_correct_options": "k_keyed", "Question": "question"})
    df["item"] = df["item"].astype(int)
    df["question_no"] = df["question_no"].astype(int)
    df["k_keyed"] = df["k_keyed"].astype(int)
    df["canonical_video_id"] = df.video.map(NAME_TO_ID)
    df["options"] = df[["Option_1", "Option_2", "Option_3", "Option_4"]].astype(str).values.tolist()
    df["has_graph"] = df.Graph.notna()
    return df[["canonical_video_id", "video", "item", "question_no", "category", "k_keyed", "question", "options", "has_graph"]]


def items_sha256() -> str:
    return sha256_file(ITEM_BANK)


# ----------------------------------------------------------------------------- R1 retriever
STOP = set("""a an the of to in on and or for is are was were be been being it its this that these those with as at by
from what which who whom why how when where do does did not no all any both each other than then so such into about
there their they them you your we our he she his her i me my can could would should will may might must one two
options option correct incorrect none mark following statement statements choose best answer according video""".split())


def tokens(text: str) -> list[str]:
    ws = re.findall(r"[a-z0-9]+", str(text).lower())
    out = []
    for w in ws:
        if w in STOP or len(w) < 2:
            continue
        for suf in ("ies", "ing", "ed", "es", "s"):
            if w.endswith(suf) and len(w) - len(suf) >= 3:
                w = w[: -len(suf)]
                break
        out.append(w)
    return out


def load_transcript(video_id: str) -> pd.DataFrame:
    return pd.read_csv(STIMULI / "transcripts" / f"{video_id}.csv")


def r1_retrieve(item: pd.Series, tr: pd.DataFrame, width: int = 2) -> dict:
    """Best window of ``width`` consecutive cues (same source, source order) for an item."""
    keyed = item.options[: item.k_keyed]
    q = Counter(tokens(item.question) + tokens(" ".join(keyed)))
    wins = []
    for src, g in tr.sort_values(["source", "src_start_s"]).groupby("source", sort=False):
        g = g.reset_index(drop=True)
        for i in range(len(g)):
            w = g.iloc[i: i + width]
            wins.append(dict(source=src, start=float(w.src_start_s.min()), end=float(w.src_end_s.max()),
                             toks=Counter(tokens(" ".join(w.text)))))
    df_ = Counter()
    for w in wins:
        df_.update(set(w["toks"]))
    n = len(wins)
    idf = {t: math.log((n + 1) / (df_[t] + 1)) + 1 for t in set(q) | set(df_)}

    def vec(c):
        return {t: c[t] * idf[t] for t in c}

    qv = vec(q)
    qn = math.sqrt(sum(v * v for v in qv.values())) or 1.0
    scores = []
    for w in wins:
        wv = vec(w["toks"])
        dot = sum(qv.get(t, 0) * wv[t] for t in wv)
        wn = math.sqrt(sum(v * v for v in wv.values())) or 1.0
        scores.append(dot / (qn * wn))
    order = np.argsort(scores)[::-1]
    best = wins[order[0]]
    second = next((wins[j] for j in order[1:] if wins[j]["source"] != best["source"]
                   or abs((wins[j]["start"] + wins[j]["end"]) / 2 - (best["start"] + best["end"]) / 2) > 20), None)
    return dict(source=best["source"], span_start_s=best["start"], span_end_s=best["end"], score=float(scores[order[0]]),
                margin=float(scores[order[0]] - (scores[wins.index(second)] if second else 0.0)))


# ----------------------------------------------------------------------------- spans and agreement
@dataclass(frozen=True)
class Span:
    source: str
    start: float
    end: float

    @property
    def centre(self) -> float:
        return (self.start + self.end) / 2


def iou(a: Span, b: Span) -> float:
    if a.source != b.source:
        return 0.0
    inter = max(0.0, min(a.end, b.end) - max(a.start, b.start))
    union = max(a.end, b.end) - min(a.start, b.start)
    return inter / union if union > 0 else 0.0


def centre_diff(a: Span, b: Span) -> float:
    return abs(a.centre - b.centre) if a.source == b.source else float("inf")


# ----------------------------------------------------------------------------- recording clock
def to_recording(video_id: str, span: Span, table: pd.DataFrame, seconds: pd.DataFrame) -> dict:
    """Map a source-time span to the recording clock and summarize its timeline status."""
    t = table[(table.canonical_video_id == video_id) & (table.source == span.source)]
    pieces = []
    for r in t.itertuples():
        a, b = max(span.start, r.video_start_s), min(span.end, r.video_end_s)
        if b > a:
            pieces.append((r.rec_start_s + (a - r.video_start_s), r.rec_start_s + (b - r.video_start_s)))
    shown = sum(b - a for a, b in pieces)
    out = dict(rec_start_s=None, rec_end_s=None, rec_centre_s=None, shown_fraction=shown / max(span.end - span.start, 1e-9),
               timeline_pass_fraction=0.0, timeline_tier=None)
    if not pieces:
        return out
    rs, re_ = min(a for a, _ in pieces), max(b for _, b in pieces)
    s = seconds[(seconds.canonical_video_id == video_id) & (seconds.rec_s >= math.floor(rs)) & (seconds.rec_s < math.ceil(re_))]
    ok = s.status.isin(["PASS-A", "PASS-B"])
    tier = None
    if ok.mean() >= 0.999:
        tier = "A" if (s.status == "PASS-A").mean() >= 0.5 else "B"
    out.update(rec_start_s=round(rs, 2), rec_end_s=round(re_, 2), rec_centre_s=round((rs + re_) / 2, 2),
               timeline_pass_fraction=float(ok.mean()) if len(s) else 0.0, timeline_tier=tier)
    return out


def read_annotation(path: Path) -> pd.DataFrame:
    a = pd.read_csv(path)
    a["canonical_video_id"] = a.video.map(NAME_TO_ID)
    return a


def provisional_table(r2_path: Path) -> pd.DataFrame:
    """Item x anchor table on the recording clock from R2 (and R1 for comparison)."""
    bank = item_bank()
    r2 = read_annotation(r2_path)
    table = pd.read_csv(STAGE0_EVIDENCE / "timeline_table.csv")
    seconds = pd.read_csv(STAGE0_EVIDENCE / "timeline_seconds.csv")
    rows = []
    for it in bank.itertuples():
        a = r2[(r2.canonical_video_id == it.canonical_video_id) & (r2.item == it.item)]
        if a.empty:
            raise KeyError(f"R2 has no anchor for {it.video} item {it.item}")
        a = a.iloc[0]
        tr = load_transcript(it.canonical_video_id)
        r1 = r1_retrieve(pd.Series(it._asdict()), tr)
        sp2 = Span(a.source, float(a.span_start_s), float(a.span_end_s))
        sp1 = Span(r1["source"], r1["span_start_s"], r1["span_end_s"])
        rec = to_recording(it.canonical_video_id, sp2, table, seconds)
        localized = a.type == "localized" and (sp2.end - sp2.start) <= LOCALIZED_MAX_S
        rows.append(dict(
            canonical_video_id=it.canonical_video_id, video=it.video, item=it.item, question_no=it.question_no,
            category=it.category, k_keyed=it.k_keyed, has_graph=it.has_graph,
            r2_type=a.type, r2_confidence=int(a.confidence), r2_key_check=a.key_check, r2_visual_check=a.visual_check,
            source=sp2.source, src_start_s=sp2.start, src_end_s=sp2.end, src_centre_s=sp2.centre,
            extra_spans=a.extra_spans if isinstance(a.extra_spans, str) else "",
            r1_source=sp1.source, r1_src_start_s=sp1.start, r1_src_end_s=sp1.end, r1_score=r1["score"], r1_margin=r1["margin"],
            r1_r2_centre_diff_s=centre_diff(sp1, sp2), r1_r2_iou=iou(sp1, sp2),
            localized=localized, **rec))
    df = pd.DataFrame(rows)
    df["anchorable"] = df.localized & (df.shown_fraction >= 0.99) & df.timeline_tier.notna() & (df.r2_key_check != "inconsistent")
    return df


# ----------------------------------------------------------------------------- gate G-AN and freeze
def gate_g_an(h1: pd.DataFrame, h2: pd.DataFrame) -> dict:
    """Gate G-AN on two *human* annotation files (plan §11.2)."""
    m = h1.merge(h2, on=["video", "item"], suffixes=("_1", "_2"))
    both_loc = m[(m.type_1 == "localized") & (m.type_2 == "localized")]
    cd = [centre_diff(Span(r.source_1, r.span_start_s_1, r.span_end_s_1), Span(r.source_2, r.span_start_s_2, r.span_end_s_2)) for r in both_loc.itertuples()]
    io = [iou(Span(r.source_1, r.span_start_s_1, r.span_end_s_1), Span(r.source_2, r.span_start_s_2, r.span_end_s_2)) for r in both_loc.itertuples()]
    flag_agree = float((m.type_1.eq("localized") == m.type_2.eq("localized")).mean())
    res = dict(n_items=len(m), n_both_localized=len(both_loc), median_centre_diff_s=float(np.median(cd)) if cd else None,
               median_iou=float(np.median(io)) if io else None, flag_agreement=flag_agree)
    res["passed"] = bool(cd and res["median_centre_diff_s"] <= GAN_CENTRE_S and res["median_iou"] >= GAN_IOU)
    return res


def freeze(h1_path: Path, h2_path: Path, adjudicated_path: Path, adjudication_log: Path, out: Path) -> dict:
    """Hash-bind an adjudicated human anchor set. Refuses unless G-AN passes on the two human files.

    R1/R2 machine proposals can never be frozen as the anchor set.
    """
    for p in (h1_path, h2_path, adjudicated_path, adjudication_log):
        if not Path(p).exists():
            raise FileNotFoundError(f"G-AN freeze needs {p}")
    h1, h2 = pd.read_csv(h1_path), pd.read_csv(h2_path)
    for h in (h1, h2):
        if "annotator_id" not in h.columns or h.annotator_id.astype(str).str.upper().str.startswith(("R1", "R2", "LLM")).any():
            raise ValueError("Annotation files must come from human annotators (annotator_id column; not R1/R2/LLM)")
    if set(h1.annotator_id) & set(h2.annotator_id):
        raise ValueError("H1 and H2 must be different annotators")
    g = gate_g_an(h1, h2)
    if not g["passed"]:
        raise RuntimeError(f"Gate G-AN not satisfied: {g}")
    rec = dict(gate=g, files={str(p): sha256_file(p) for p in (h1_path, h2_path, adjudicated_path, adjudication_log, ITEM_BANK)},
               timeline={str(p): sha256_file(p) for p in (STAGE0_EVIDENCE / "timeline_table.csv", STAGE0_EVIDENCE / "timeline_seconds.csv")})
    rec["freeze_sha256"] = sha256_bytes(json.dumps(rec, sort_keys=True).encode())
    Path(out).write_text(json.dumps(rec, indent=2))
    return rec
