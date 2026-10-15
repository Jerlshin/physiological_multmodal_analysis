"""Outcome-free map from the release quiz numbering to the item bank (Stage-1 spec §2.2).

The forensic item table (``quiz_items.parquet``, locked) numbers items by the release's
``question_no`` within (experiment, local stimulus). The item bank numbers them by
(video, local item). This module links the two **from item content only**: the release
questionnaire sidecars (``phenotype/stimuli_questionnaire.json``: question and option texts per
stimulus and question number, no responses) are matched by text to the item bank. The forensic
table itself is never opened here; :func:`verify_item_table` checks the map against it *inside*
the gated loader, after authorization.
"""
from __future__ import annotations

import hashlib
import json
import re

import pandas as pd

from .anchors import item_bank
from .exposures import all_exposures
from .paths_stage1 import RELEASE_METADATA

EXPERIMENTS = (1, 3, 4, 5)       # E2 behaviour is quarantined (D038) and not in any CAIRN set


def _norm(s) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", str(s).lower()).split())


def release_items(experiment: int) -> pd.DataFrame:
    """Question and option texts per (local stimulus, question number) from the release sidecar."""
    d = json.loads((RELEASE_METADATA / f"experiment{experiment}" / "phenotype" / "stimuli_questionnaire.json").read_text())
    rows = []
    qs, ans = d["questions"], d["answers"]
    if "memory" in qs:                                    # E1 layout: type -> stim -> q
        qs, ans = qs["memory"], ans["memory"]
    for stim, questions in qs.items():
        sid = int(re.sub(r"\D", "", stim))
        for q, text in questions.items():
            opts = list(ans[stim][q].values()) if isinstance(ans[stim][q], dict) else list(ans[stim][q])
            rows.append(dict(experiment=experiment, local_stimulus_id=sid, question_no=int(q[1:]), question=text,
                             options=opts, question_sha256=hashlib.sha256(str(text).encode()).hexdigest()))
    return pd.DataFrame(rows)


def stimulus_map() -> pd.DataFrame:
    e = all_exposures()
    m = e[["experiment", "local_stimulus_id", "canonical_video_id"]].drop_duplicates()
    if m.duplicated(["experiment", "local_stimulus_id"]).any():
        raise AssertionError("ambiguous local stimulus -> video map")
    return m


def key_map() -> pd.DataFrame:
    """(experiment, local_stimulus_id, question_no) -> (canonical_video_id, item); one-to-one per video."""
    bank = item_bank()
    bank = bank.assign(qn=bank.question.map(_norm), on=bank.options.map(lambda o: tuple(_norm(x) for x in o)))
    smap = stimulus_map()
    out = []
    for exp in EXPERIMENTS:
        r = release_items(exp).merge(smap, on=["experiment", "local_stimulus_id"], how="left", validate="many_to_one")
        if r.canonical_video_id.isna().any():
            raise AssertionError(f"E{exp}: release stimulus without a video")
        for row in r.itertuples():
            b = bank[bank.canonical_video_id == row.canonical_video_id]
            qn, on = _norm(row.question), tuple(_norm(x) for x in row.options)
            hit = b[(b.qn == qn) & (b.on == on)]
            method = "question+options"
            if len(hit) != 1:
                hit = b[b.qn == qn]
                method = "question"
            if len(hit) != 1:
                hit = b[b.on == on]
                method = "options"
            if len(hit) != 1:
                raise AssertionError(f"E{exp} stim {row.local_stimulus_id} q{row.question_no}: {len(hit)} bank matches")
            out.append(dict(experiment=exp, local_stimulus_id=row.local_stimulus_id, question_no=row.question_no,
                            canonical_video_id=row.canonical_video_id, item=int(hit.item.iloc[0]),
                            bank_question_no=int(hit.question_no.iloc[0]), match=method))
    m = pd.DataFrame(out)
    if m.duplicated(["experiment", "canonical_video_id", "item"]).any():
        raise AssertionError("two release questions map to one bank item")
    return m


def verify_item_table(t: pd.DataFrame, m: pd.DataFrame | None = None) -> pd.DataFrame:
    """Attach (video, item) to gated item rows; raise unless every key maps and videos agree.

    Called only on rows returned by :func:`cairn.gate.load_item_outcomes` (after authorization).
    """
    m = key_map() if m is None else m
    j = t.merge(m, on=["experiment", "local_stimulus_id", "question_no"], how="left", suffixes=("", "_map"),
                validate="many_to_one")
    if j.item.isna().any():
        raise AssertionError(f"{int(j.item.isna().sum())} item rows have no item-bank key")
    if "canonical_video_id_map" in j and (j.canonical_video_id != j.canonical_video_id_map).any():
        raise AssertionError("video disagreement between item table and key map")
    return j.drop(columns=[c for c in j.columns if c.endswith("_map")])
