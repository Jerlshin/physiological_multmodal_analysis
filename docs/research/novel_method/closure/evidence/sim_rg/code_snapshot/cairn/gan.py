"""Gate G-AN tooling for the two-human-annotator process (plan §11.2; ANNOTATION_PROTOCOL.md; closure C-D10).

A new module, so that the Stage-0 ``cairn.anchors`` (hash-bound in ``stage0/SHA256SUMS``) stays byte-identical. It
reuses that module's definitions (spans, IoU, centre difference, the G-AN thresholds, ``gate_g_an``, ``freeze``)
and adds what the coordinator needs between receiving two annotation files and the anchor freeze:

1. :func:`validate_file`: schema, completeness and value checks of one annotator's CSV;
2. :func:`receive`: hash-on-receipt log (append-only);
3. :func:`agreement`: gate G-AN plus Cohen's kappa on ``type`` (promised by the protocol, §3 step 4), per-video
   agreement and the adjudication worksheet (items whose centres differ by > 10 s or whose types disagree);
4. :func:`anchor_table`: the adjudicated table on the recording clock, in the format ``cairn.design`` reads,
   with the Stage-0 anchorability rule (S0-D08);
5. :func:`compare_to_r2`: descriptive agreement of the adjudicated human set with the provisional machine set
   (spec §4 item 4); R2 is never used for inference once human anchors exist;
6. :func:`freeze_human_set`: runs ``cairn.anchors.freeze`` (refuses machine raters and refuses unless G-AN passes)
   and binds the recording-clock table and the agreement report in a companion record.

No learner data, outcome or response is read anywhere in this module.
"""
from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from . import anchors as A
from .paths import SOURCES, STAGE0_EVIDENCE, VIDEOS, YOUTUBE, sha256_bytes, sha256_file

TEMPLATE_COLUMNS = ["annotator_id", "video", "item", "source", "span_start_s", "span_end_s", "extra_spans", "type",
                    "category", "confidence", "key_check", "visual_only", "ambiguity_note"]
TYPES = ("localized", "multi_span", "diffuse", "absent")
KEY_CHECKS = ("supported", "partial", "not_in_video", "inconsistent")
MACHINE_IDS = ("R1", "R2", "LLM", "CLAUDE", "GPT", "AUTO")
SPAN_TYPES = ("localized", "multi_span")       # types that must carry an evidence span


def source_duration(source: str) -> float | None:
    p = YOUTUBE / source / f"{source}.info.json"
    if not p.exists():
        return None
    return float(json.loads(p.read_text()).get("duration") or 0) or None


# ----------------------------------------------------------------------------- 1. validation
def validate_file(path: Path) -> dict:
    """Errors (blocking) and warnings for one annotator file. The file is valid iff ``errors`` is empty."""
    errors, warnings = [], []
    try:
        a = pd.read_csv(path, dtype={"source": str})
    except Exception as e:                                  # unreadable file
        return dict(path=str(path), valid=False, errors=[f"unreadable: {e}"], warnings=[])
    missing = [c for c in TEMPLATE_COLUMNS if c not in a.columns]
    if missing:
        return dict(path=str(path), valid=False, errors=[f"missing columns {missing}"], warnings=[])
    ids = set(a.annotator_id.astype(str).str.strip())
    if len(ids) != 1:
        errors.append(f"one annotator per file expected, found {sorted(ids)}")
    if any(i.upper().startswith(MACHINE_IDS) for i in ids):
        errors.append(f"annotator_id {sorted(ids)} looks like a machine rater; human annotators only")
    bank = A.item_bank()
    want = set(zip(bank.video, bank.item))
    got = list(zip(a.video, a.item.astype(int)))
    if len(got) != len(set(got)):
        errors.append("duplicate (video, item) rows")
    if set(got) != want:
        errors.append(f"items: {len(want - set(got))} missing, {len(set(got) - want)} unknown "
                      f"(expected the {len(want)} item-bank items)")
    cat = dict(zip(zip(bank.video, bank.item), bank.category))
    for r in a.itertuples():
        tag = f"{r.video} item {r.item}"
        if r.type not in TYPES:
            errors.append(f"{tag}: type '{r.type}' not in {TYPES}")
            continue
        if r.key_check not in KEY_CHECKS:
            errors.append(f"{tag}: key_check '{r.key_check}' not in {KEY_CHECKS}")
        if str(r.visual_only).strip().lower() not in ("yes", "no"):
            errors.append(f"{tag}: visual_only must be yes/no")
        try:
            if int(r.confidence) not in (1, 2, 3):
                raise ValueError
        except (TypeError, ValueError):
            errors.append(f"{tag}: confidence must be 1, 2 or 3")
        if (r.video, int(r.item)) in cat and str(r.category) != cat[(r.video, int(r.item))]:
            errors.append(f"{tag}: category '{r.category}' differs from the item bank ('{cat[(r.video, int(r.item))]}')")
        vid = A.NAME_TO_ID.get(r.video)
        if r.type in SPAN_TYPES:
            if vid is None or str(r.source) not in SOURCES.get(vid, []):
                errors.append(f"{tag}: source '{r.source}' is not a source of this video {SOURCES.get(vid)}")
            try:
                s0, s1 = float(r.span_start_s), float(r.span_end_s)
            except (TypeError, ValueError):
                errors.append(f"{tag}: span times must be numbers")
                continue
            if not (math.isfinite(s0) and math.isfinite(s1) and 0 <= s0 < s1):
                errors.append(f"{tag}: span must satisfy 0 <= start < end")
            dur = source_duration(str(r.source))
            if dur and s1 > dur + 1:
                errors.append(f"{tag}: span end {s1} s beyond the source duration {dur} s")
            if r.type == "localized" and s1 - s0 > A.LOCALIZED_MAX_S:
                errors.append(f"{tag}: localized span {s1 - s0:.1f} s exceeds {A.LOCALIZED_MAX_S:.0f} s (use diffuse/multi_span)")
        if isinstance(r.extra_spans, str) and r.extra_spans.strip():
            for piece in r.extra_spans.split(";"):
                if not re.fullmatch(r"\s*\d+(\.\d+)?\s*-\s*\d+(\.\d+)?\s*(@[\w-]+)?\s*", piece):
                    errors.append(f"{tag}: extra_spans piece '{piece}' is not 'start-end' or 'start-end@source'")
        if isinstance(r.ambiguity_note, str) and len(r.ambiguity_note.split()) > 25:
            warnings.append(f"{tag}: ambiguity_note longer than 25 words")
    return dict(path=str(path), annotator=sorted(ids), rows=len(a), valid=not errors, errors=errors, warnings=warnings)


# ----------------------------------------------------------------------------- 2. receipt
def receive(path: Path, log: Path) -> dict:
    """Hash a returned file on receipt and append to an append-only receipt log (protocol §3 step 3)."""
    rec = dict(utc=datetime.now(timezone.utc).isoformat(timespec="seconds"), file=str(path), sha256=sha256_file(path),
               validation=validate_file(path))
    Path(log).parent.mkdir(parents=True, exist_ok=True)
    with Path(log).open("a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


# ----------------------------------------------------------------------------- 3. agreement
def cohen_kappa(a: list, b: list, labels=TYPES) -> float:
    a, b = np.asarray(a), np.asarray(b)
    po = float(np.mean(a == b))
    pe = float(sum(np.mean(a == l) * np.mean(b == l) for l in labels))
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def _span(r, k):
    return A.Span(str(getattr(r, f"source_{k}")), float(getattr(r, f"span_start_s_{k}")), float(getattr(r, f"span_end_s_{k}")))


def agreement(h1_path: Path, h2_path: Path) -> tuple[dict, pd.DataFrame]:
    """Gate G-AN (``cairn.anchors.gate_g_an``), Cohen's kappa on type, per-video agreement and the adjudication
    worksheet. Both files must validate first."""
    for p in (h1_path, h2_path):
        v = validate_file(p)
        if not v["valid"]:
            raise ValueError(f"{p} does not validate: {v['errors'][:5]}")
    h1 = pd.read_csv(h1_path, dtype={"source": str})
    h2 = pd.read_csv(h2_path, dtype={"source": str})
    gate = A.gate_g_an(h1, h2)
    m = h1.merge(h2, on=["video", "item"], suffixes=("_1", "_2"))
    rows = []
    for r in m.itertuples():
        both = r.type_1 == "localized" and r.type_2 == "localized"
        cd = A.centre_diff(_span(r, 1), _span(r, 2)) if both else np.nan
        io = A.iou(_span(r, 1), _span(r, 2)) if both else np.nan
        reasons = []
        if r.type_1 != r.type_2:
            reasons.append("type differs")
        if both and cd > A.GAN_CENTRE_S:
            reasons.append(f"centres {cd:.1f} s apart (> {A.GAN_CENTRE_S:.0f})")
        rows.append(dict(video=r.video, item=int(r.item), type_1=r.type_1, type_2=r.type_2, centre_diff_s=cd, iou=io,
                         source_1=r.source_1, start_1=r.span_start_s_1, end_1=r.span_end_s_1,
                         source_2=r.source_2, start_2=r.span_start_s_2, end_2=r.span_end_s_2,
                         key_check_1=r.key_check_1, key_check_2=r.key_check_2,
                         needs_adjudication=bool(reasons), reasons="; ".join(reasons)))
    w = pd.DataFrame(rows)
    per_video = w.groupby("video").apply(lambda g: pd.Series(dict(
        items=len(g), both_localized=int(g.centre_diff_s.notna().sum()),
        median_centre_diff_s=float(g.centre_diff_s.median()) if g.centre_diff_s.notna().any() else None,
        median_iou=float(g.iou.median()) if g.iou.notna().any() else None,
        type_agreement=float((g.type_1 == g.type_2).mean()), to_adjudicate=int(g.needs_adjudication.sum()))),
        include_groups=False)
    report = dict(gate=gate, kappa_type=cohen_kappa(list(m.type_1), list(m.type_2)),
                  type_agreement=float((m.type_1 == m.type_2).mean()),
                  key_check_agreement=float((m.key_check_1 == m.key_check_2).mean()),
                  items_to_adjudicate=int(w.needs_adjudication.sum()),
                  per_video=per_video.reset_index().to_dict(orient="records"),
                  files={str(h1_path): sha256_file(h1_path), str(h2_path): sha256_file(h2_path)})
    return report, w


def adjudication_worksheet(w: pd.DataFrame, with_r2: bool = True) -> pd.DataFrame:
    """The disputed items, with empty decision columns. R2 (machine, non-binding) is shown only here, at
    adjudication, as the protocol allows."""
    d = w[w.needs_adjudication].copy()
    if with_r2:
        r2 = pd.read_csv(STAGE0_EVIDENCE.parent / "annotation" / "anchors_R2_llm_provisional.csv", dtype={"source": str})
        r2 = r2.rename(columns={"type": "r2_type", "source": "r2_source", "span_start_s": "r2_start", "span_end_s": "r2_end"})
        d = d.merge(r2[["video", "item", "r2_type", "r2_source", "r2_start", "r2_end"]], on=["video", "item"], how="left")
    for c in ("decision_type", "decision_source", "decision_start_s", "decision_end_s", "decision_reason", "adjudicator_id"):
        d[c] = ""
    return d


def consensus(h1_path: Path, h2_path: Path, decisions_path: Path | None, adjudicator_id: str) -> pd.DataFrame:
    """The adjudicated file (protocol addendum v1.1, rule A1-A3), in the annotation template format.

    A1. Items that need no adjudication (same type; for two localized spans, centres <= 10 s apart): the type is the
        agreed type; a span-carrying type gets the element-wise mean of the two spans when both used the same source,
        otherwise annotator 1's span; confidence = the lower of the two; key_check = annotator 1's if equal, else
        'partial'; visual_only = 'yes' if either said yes.
    A2. Disputed items take the adjudicator's decision row from the worksheet (decision_type, decision_source,
        decision_start_s, decision_end_s, decision_reason). A disputed item without a complete decision is an error.
    A3. An item the adjudicator cannot resolve is entered as decision_type 'diffuse' (protocol §3 step 6)."""
    h1 = pd.read_csv(h1_path, dtype={"source": str}).set_index(["video", "item"])
    h2 = pd.read_csv(h2_path, dtype={"source": str}).set_index(["video", "item"])
    _, w = agreement(h1_path, h2_path)
    dec = pd.read_csv(decisions_path, dtype={"decision_source": str}).set_index(["video", "item"]) if decisions_path else None
    rows = []
    for r in w.itertuples():
        a, b = h1.loc[(r.video, r.item)], h2.loc[(r.video, r.item)]
        row = dict(annotator_id=adjudicator_id, video=r.video, item=r.item, source="", span_start_s=np.nan, span_end_s=np.nan,
                   extra_spans=a.extra_spans if isinstance(a.extra_spans, str) else "", type=a.type, category=a.category,
                   confidence=int(min(a.confidence, b.confidence)),
                   key_check=a.key_check if a.key_check == b.key_check else "partial",
                   visual_only="yes" if "yes" in (str(a.visual_only).lower(), str(b.visual_only).lower()) else "no",
                   ambiguity_note="")
        if not r.needs_adjudication:
            if a.type in SPAN_TYPES:
                if str(a.source) == str(b.source):
                    row.update(source=str(a.source), span_start_s=(float(a.span_start_s) + float(b.span_start_s)) / 2,
                               span_end_s=(float(a.span_end_s) + float(b.span_end_s)) / 2)
                else:
                    row.update(source=str(a.source), span_start_s=float(a.span_start_s), span_end_s=float(a.span_end_s))
        else:
            if dec is None or (r.video, r.item) not in dec.index:
                raise ValueError(f"{r.video} item {r.item} needs an adjudication decision")
            d = dec.loc[(r.video, r.item)]
            if str(d.decision_type) not in TYPES or not isinstance(d.decision_reason, str) or not d.decision_reason.strip():
                raise ValueError(f"{r.video} item {r.item}: decision_type and decision_reason are required")
            row.update(type=str(d.decision_type), ambiguity_note=f"adjudicated: {d.decision_reason}"[:200])
            if d.decision_type in SPAN_TYPES:
                row.update(source=str(d.decision_source), span_start_s=float(d.decision_start_s), span_end_s=float(d.decision_end_s))
        rows.append(row)
    return pd.DataFrame(rows)[TEMPLATE_COLUMNS]


def verify_package() -> dict:
    """Re-hash the git-ignored annotation package against stage0/annotation/package_manifest.json."""
    from .paths import STAGE0, STIMULI
    m = json.loads((STAGE0 / "annotation" / "package_manifest.json").read_text())
    bad, n = [], 0
    for order, name in enumerate(VIDEOS.values(), start=1):
        stem = f"{order:02d}_{name.replace(' ', '_')}"
        for kind in ("items", "transcript"):
            n += 1
            f = STIMULI / "annotation_package" / f"{stem}_{kind}.csv"
            if not f.exists() or sha256_file(f) != m[name][f"{kind}_sha256"]:
                bad.append(f.name)
    return dict(files=n, verified=n - len(bad), mismatches=bad, passed=not bad)


FORBIDDEN_IN_BUNDLE = ("anchors_R2", "anchors_provisional", "R1", "quiz_items", "quiz_video_outcomes", "item_difficulty",
                       "quiz_aggregate", "quiz_content_summary", "historical_quiz")


def bundle(out_zip: Path, annotator_code: str) -> dict:
    """One annotator's package as a zip: the 22 item-sheet and transcript files (verified against the package manifest),
    protocol v1.0, addendum v1.1, the response template pre-filled with the annotator code and the 131 (video, item)
    keys, and the blinding attestation. Machine proposals (R1, R2) and every outcome-derived file are excluded by
    construction and checked by name. The zip's member hashes are returned (record them in the receipt log)."""
    import io
    import zipfile

    from .paths import STAGE0, STIMULI
    if annotator_code.upper().startswith(MACHINE_IDS):
        raise ValueError("annotator codes must be human codes")
    pk = verify_package()
    if not pk["passed"]:
        raise RuntimeError(f"annotation package does not verify: {pk['mismatches']}")
    closure = Path(__file__).resolve().parents[2] / "docs/research/novel_method/closure/gan"
    members = {f"package/{f.name}": f.read_bytes() for f in sorted((STIMULI / "annotation_package").glob("*.csv"))}
    members["ANNOTATION_PROTOCOL.md"] = (STAGE0 / "annotation" / "ANNOTATION_PROTOCOL.md").read_bytes()
    members["ANNOTATION_PROTOCOL_ADDENDUM_v1.1.md"] = (closure / "ANNOTATION_PROTOCOL_ADDENDUM_v1.1.md").read_bytes()
    members["blinding_attestation.md"] = (closure / "templates" / "blinding_attestation.md").read_bytes()
    bank = A.item_bank()
    tmpl = pd.DataFrame({c: "" for c in TEMPLATE_COLUMNS}, index=range(len(bank)))
    tmpl["annotator_id"], tmpl["video"], tmpl["item"], tmpl["category"] = annotator_code, bank.video.values, bank.item.values, bank.category.values
    buf = io.StringIO()
    tmpl.to_csv(buf, index=False)
    members[f"response_{annotator_code}.csv"] = buf.getvalue().encode()
    for name in members:
        if any(f in name for f in FORBIDDEN_IN_BUNDLE):
            raise AssertionError(f"forbidden file in bundle: {name}")
    out_zip = Path(out_zip)
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in members.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 14, 0, 0, 0))   # fixed time: reproducible bytes
            z.writestr(info, data)
    return dict(zip=str(out_zip), zip_sha256=sha256_file(out_zip), annotator=annotator_code,
                members={n: sha256_bytes(d) for n, d in members.items()})


# ----------------------------------------------------------------------------- 4. recording-clock table
def anchor_table(adjudicated_path: Path) -> pd.DataFrame:
    """The adjudicated human set on the recording clock, in the columns ``cairn.design.anchor_table`` requires,
    with the Stage-0 anchorability rule (S0-D08): localized (one span <= 45 s) AND fully shown AND every second
    of the span passes G-TL AND key not inconsistent with the video."""
    v = validate_file(adjudicated_path)
    if not v["valid"]:
        raise ValueError(f"adjudicated file does not validate: {v['errors'][:5]}")
    adj = pd.read_csv(adjudicated_path, dtype={"source": str})
    bank = A.item_bank()
    table = pd.read_csv(STAGE0_EVIDENCE / "timeline_table.csv")
    seconds = pd.read_csv(STAGE0_EVIDENCE / "timeline_seconds.csv")
    rows = []
    for it in bank.itertuples():
        a = adj[(adj.video == it.video) & (adj.item == it.item)].iloc[0]
        localized = a.type == "localized" and float(a.span_end_s) - float(a.span_start_s) <= A.LOCALIZED_MAX_S
        rec = dict(rec_start_s=None, rec_end_s=None, rec_centre_s=None, shown_fraction=0.0, timeline_pass_fraction=0.0,
                   timeline_tier=None)
        if a.type in SPAN_TYPES:
            rec = A.to_recording(it.canonical_video_id, A.Span(str(a.source), float(a.span_start_s), float(a.span_end_s)),
                                 table, seconds)
        rows.append(dict(canonical_video_id=it.canonical_video_id, video=it.video, item=it.item, question_no=it.question_no,
                         category=it.category, k_keyed=it.k_keyed, has_graph=it.has_graph, type=a.type,
                         confidence=int(a.confidence), key_check=a.key_check, visual_only=a.visual_only,
                         source=str(a.source), src_start_s=a.span_start_s, src_end_s=a.span_end_s,
                         extra_spans=a.extra_spans if isinstance(a.extra_spans, str) else "", localized=localized, **rec))
    df = pd.DataFrame(rows)
    df["anchorable"] = (df.localized & (df.shown_fraction >= 0.99) & df.timeline_tier.notna()
                        & (df.key_check != "inconsistent"))
    return df


def compare_to_r2(human: pd.DataFrame, provisional: Path = STAGE0_EVIDENCE / "anchors_provisional.csv") -> dict:
    """Descriptive agreement of the human recording-clock table with the provisional machine table (spec §4.4)."""
    p = pd.read_csv(provisional)
    m = human.merge(p, on=["canonical_video_id", "item"], suffixes=("_h", "_r2"))
    both = m[m.anchorable_h & m.anchorable_r2]
    cd = (both.rec_centre_s_h - both.rec_centre_s_r2).abs()
    return dict(items=len(m), anchorable_human=int(m.anchorable_h.sum()), anchorable_r2=int(m.anchorable_r2.sum()),
                anchorable_both=len(both), anchorable_agreement=float((m.anchorable_h == m.anchorable_r2).mean()),
                median_centre_diff_s=float(cd.median()) if len(cd) else None,
                frac_centre_within_10s=float((cd <= 10).mean()) if len(cd) else None)


def moment_count(table: pd.DataFrame, videos=None, gap: float = 10.0) -> int:
    """Distinct anchor moments (single linkage at ``gap`` s), as the T2 null uses them."""
    from .design import moment_groups
    t = table[table.anchorable]
    if videos is not None:
        t = t[t.video.isin(videos)]
    return int(sum(len(set(moment_groups(g.rec_centre_s.to_numpy(float), gap))) for _, g in t.groupby("video")))


# ----------------------------------------------------------------------------- 5. freeze
def freeze_human_set(h1: Path, h2: Path, adjudicated: Path, adjudication_log: Path, out_dir: Path) -> dict:
    """Anchor freeze: ``cairn.anchors.freeze`` (G-AN must pass; human raters only) writes ``ANCHOR_FREEZE.json``;
    this function then writes the recording-clock table ``anchors_frozen.csv`` and ``ANCHOR_FREEZE_COMPANION.json``
    binding the table, the agreement report and the human-vs-R2 comparison to the freeze hash."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rec = A.freeze(h1, h2, adjudicated, adjudication_log, out_dir / "ANCHOR_FREEZE.json")
    tab = anchor_table(adjudicated)
    tab_path = out_dir / "anchors_frozen.csv"
    tab.to_csv(tab_path, index=False, float_format="%.2f")
    report, _ = agreement(h1, h2)
    comp = dict(anchor_freeze_sha256=sha256_file(out_dir / "ANCHOR_FREEZE.json"), freeze_sha256=rec["freeze_sha256"],
                anchor_table=str(tab_path), anchor_table_sha256=sha256_file(tab_path),
                anchorable=int(tab.anchorable.sum()), moments_locked=moment_count(tab, ["Stars", "Immune", "Related"]),
                agreement=report, human_vs_r2=compare_to_r2(tab),
                utc=datetime.now(timezone.utc).isoformat(timespec="seconds"))
    comp["companion_sha256"] = sha256_bytes(json.dumps(comp, sort_keys=True, default=str).encode())
    (out_dir / "ANCHOR_FREEZE_COMPANION.json").write_text(json.dumps(comp, indent=2, default=str))
    return comp


VIDEO_ORDER = list(VIDEOS.values())
