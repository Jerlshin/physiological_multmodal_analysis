# Stage 0b — outcome-blind content anchoring: audit and handoff

2026-10-13. **Status: PROVISIONAL, NOT FROZEN.**

- Gate G-AN (plan §11.2) needs two independent **human** annotators. None was available in this phase.
- The anchors here come from two **machine** raters:
  - **R1**, a deterministic lexical retriever;
  - **R2**, an LLM-assisted reading of transcripts and items by Claude (claude-opus-5-5) in this session.
- Neither rater is a human annotator, and their agreement is not G-AN.

The anchor set is not frozen, and `cairn.anchors.freeze()` refuses machine-authored files by design.

**Files:**

| File | Content |
|---|---|
| [annotation/anchors_R2_llm_provisional.csv](annotation/anchors_R2_llm_provisional.csv) | R2 sheet: 131 items, source-time spans, type, confidence, key check, visual flag, short rationale |
| [evidence/anchors_provisional.csv](evidence/anchors_provisional.csv) | R1 + R2 on the recording clock, with timeline tier and anchorability |
| [evidence/anchors_provisional_by_video.csv](evidence/anchors_provisional_by_video.csv) | Per-video counts |
| [evidence/anchors_provisional_summary.json](evidence/anchors_provisional_summary.json) | Totals and machine agreement |
| [annotation/ANNOTATION_PROTOCOL.md](annotation/ANNOTATION_PROTOCOL.md), [annotation/annotation_template.csv](annotation/annotation_template.csv), [annotation/package_manifest.json](annotation/package_manifest.json) | The human-annotation package (built by `scripts/make_annotation_package.py`; transcripts are git-ignored) |

## 1. Inputs (outcome-free)

- **Item bank:** the 131 post-test items (`gate_closure_Education_questions.json`, SHA-256 `74fc8c2f…`). Each has a question, four options, the number of keyed options *k* and an R/C category.
- **Transcripts:** YouTube captions. Creator tracks for 9 videos; automatic English tracks for Planets and both Enzymes sources. They are mapped to the recording clock by the Stage-0a timeline.
- **No learner data.**
- The forensic-audit outcome files (`quiz_items.parquet`, `item_difficulty.csv`, …) were not opened. One incidental exposure is disclosed in [entry_state.md](entry_state.md).

**Key convention [F/I].**

- **[F]** The item bank lists the keyed options first: the first *k* options are keyed.
- **[I]** The convention was checked **only against the narration**, never against responses:

| Narration verdict | Items |
|---|---|
| Supported | 109 |
| Partially supported | 15 |
| Not in narration | 3 |
| Questionable | 3 (Mosquitoes 9, Enzymes 8, Enzymes 12) |
| Inconsistent | 1 (**Capacitors 8**: no option matches C = Q/V as narrated) |

- Item-quality flags: Birth rate 3 has options corrupted into durations in the item bank (e.g. "4 days, 11:40:00", an Excel rendering of 106:100).

## 2. Definitions

Full rules are in the protocol.

| Term | Definition |
|---|---|
| **Evidence span** | Shortest contiguous stretch (source seconds) whose narration or visuals let one choose the keyed answer over the distractors |
| **Anchor centre** | The span midpoint, mapped to the recording clock |
| **localized** | One span ≤ 45 s |
| **multi_span** | ≥ 2 spans > 30 s apart |
| **diffuse** | Integration over > 45 s, or gist |
| **absent** | Not spoken or shown |
| **Anchorable** | Localized **and** fully shown in the BBBD stimulus **and** every second of the span passes G-TL **and** the key is not inconsistent |
| **Timeline tier** | A if most of the span's seconds are PASS-A; B otherwise |

## 3. Results (provisional, R2-based)

| | Items | Localized | **Anchorable** | Tier A | R2 confidence 3 | Distinct anchor moments (centres > 10 s apart) | Median span (s) |
|---|---|---|---|---|---|---|---|
| **Development** (9 videos) | 107 | 88 | **87** | 53 | 52 | 59 | 8–32 |
| Locked / reserved (Stars, Immune) | 24 | 23 | 18 | 17 | 14 | 13 | 6–12 |
| **Total** | **131** | **111** | **105** | 70 | 66 | 72 | |

Per video, anchorable / items (distinct moments):

| Video | Anchorable / items | Distinct moments | Note |
|---|---|---|---|
| Stars | 11/12 | 7 | |
| Light bulbs | 10/11 | 6 | |
| Immune | 7/12 | 6 | 5 fail the timeline |
| Internet | 11/12 | 8 | |
| Birth rate | 11/12 | 6 | |
| Mosquitoes | 9/12 | 8 | |
| Related | 8/12 | 6 | |
| Work-energy | 10/12 | 7 | |
| Capacitors | 11/12 | 10 | |
| Planets | 8/12 | 3 | |
| Enzymes | 9/12 | 5 | |

**Not anchorable (26):**

| Reason | Count | Items |
|---|---|---|
| Not localized | 20 | 6 multi-span, 8 diffuse, 3 absent from narration, 3 localized-but-> 45 s |
| Evidence in timeline-failed or not-shown material | 5 | Immune 2, 7, 8, 9, 10 |
| Key inconsistent with the narration | 1 | Capacitors 8 |

**Other facts:**

- 14 items need a visual check: on-screen-only text or diagrams.
- All 59 items of the five E1/E2 videos are recognition (R) items. Comprehension (C) items occur only in the six E3 videos, where 41 of 72 items are C. Among the 87 development anchorable items, 58 are R and 29 are C.

**Machine–machine agreement** (R1 lexical vs R2; localized items; **not G-AN**):

- median centre difference **4.5 s**;
- median IoU **0.47**;
- 65% of centres within 10 s.

**[I]** Most items are lexically locatable. R1 fails mainly on paraphrased, application and comprehension items, where R2's judgment differs.

## 4. Interpretation

1. **[I] Enough items are localizable.**
   - 87 of the 107 development items (81%) have a single, short, shown, timeline-valid evidence span.
   - This exceeds the plan's implicit requirement and the stop rule's "≥ 6 development videos" (all 9 qualify).
2. **[I] But the effective number of moments is smaller than the number of items.**
   - Items share spans: for example, Stars items 3, 5 and 10 all sit in one 12 s sentence.
   - The 87 development items occupy only **59 distinct moments** (Planets 3, Enzymes 5).
   - Within a learner, items sharing a span have identical moment terms.
   - So the moment effect λ is identified from about 59, not 87, distinct regressor values per learner set. **The Stage-1 power simulation must use this real anchor structure.**
3. **[I] A category confound is built in.** Localized items are mostly recognition items, and comprehension items are often diffuse. That is exactly the confound critique #13 [R13] anticipated: localized-vs-diffuse contrasts must condition on category and item easiness.
4. **[I] The locked primary cohort has fewer anchors than the plan assumed.**
   - E4's tested videos (Stars, Immune, Related) give 26 anchorable items, against the 36 the plan's power calculation (§20.3) used.
   - They span about 19 distinct moments.

## 5. Gate G-AN — handoff point

**G-AN is not satisfied and cannot be satisfied without human action.** What is ready:

1. **Protocol:** [annotation/ANNOTATION_PROTOCOL.md](annotation/ANNOTATION_PROTOCOL.md). It covers definitions, special-format rules, blinding (to learner data, the forensic-audit outcome files and R1/R2), calibration, independent annotation, agreement statistics, adjudication and freeze.
2. **Package:**
   - `scripts/make_annotation_package.py` writes item sheets and timed transcripts per video to `data/stimuli/annotation_package/` (git-ignored);
   - the hash manifest is in [annotation/package_manifest.json](annotation/package_manifest.json);
   - videos are fetched from the public sources listed there.
3. **Response template:** [annotation/annotation_template.csv](annotation/annotation_template.csv).
4. **Gate and freeze code:**
   - `cairn.anchors.gate_g_an()` computes G-AN;
   - `cairn.anchors.freeze()` hash-binds human files, adjudication and timeline, and refuses unless G-AN passes and the annotators are human and distinct (tested).
5. **R2 provisional sheet:** a non-binding third opinion for adjudication only.

**Required user action:** recruit two annotators blind to learner data. Expect about 2 annotator-days each. The provisional anchors may be used **only** for outcome-free Stage-1 work: simulation design, pipeline tests and power. **No outcome may be linked to any anchor until the human set is frozen.**
