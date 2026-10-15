# CAIRN anchor annotation protocol (v1.0, 2026-10-13)

The protocol defines how two human annotators independently mark, for each of the 131 BBBD
post-test items, where in the stimulus video the information needed to answer is presented.
It implements research plan §11.2 (gate G-AN).

The annotations are **outcome-blind** by construction. Annotators must never see:

- learner answers, scores, item difficulties or any learner data.

The following repository files are off-limits to annotators. They hold outcome-derived values from the 2026-10-02 forensic audit:

- `docs/research/dataset_exploration/evidence/quiz_items.parquet`;
- `quiz_video_outcomes.parquet`;
- `item_difficulty.csv`;
- `quiz_aggregate_comparison.parquet`;
- `gate_closure_quiz_content_summary.json`;
- `gate_closure_historical_quiz_comparison.json`.

Annotators also work **blind to the machine proposals R1 and R2**. R2, the LLM-assisted provisional sheet, is a non-binding third opinion consulted only at adjudication.

## 1. Materials (built by `scripts/make_annotation_package.py`)

| Material | Content |
|---|---|
| Video | The public YouTube source(s) of each stimulus. Enzymes uses two sources: `AAZ03aScPr8`, then `lkRZKqDdwzU` |
| Transcript | A timed transcript for each source, with cue start and end in **source-video seconds**. Cues the BBBD stimulus did not show (trimmed material, per the Stage-0a timeline) are marked `NOT SHOWN` |
| Item sheet | Per video: item number, R/C category, question, the four options and which option(s) are keyed. The keyed options are the first *k* options in the item bank, where *k* = `No_correct_options`. The quiz shuffled options for learners |
| Template | [annotation_template.csv](annotation_template.csv) |

**Time base.** Annotators mark times in **source-video seconds**: the YouTube player time of the named source. The mapping to the recording clock is done by code (Stage-0a timeline). Annotators never need it.

## 2. What to mark per item

| Field | Definition |
|---|---|
| `evidence span` (`source`, `span_start_s`, `span_end_s`) | The **shortest contiguous stretch of the video** whose narration and/or visuals contain the information needed to choose the keyed answer over the distractors. Start at the onset of the first phrase or visual that carries the decisive information; end when it is complete. Use the transcript to find it, then refine on the video to about 1 s |
| `anchor centre` | Derived, not marked: the midpoint of the evidence span |
| `extra_spans` | Other stretches that also present needed information, as `start-end;start-end` (source seconds; use `start-end@sourceID` if the source differs) |
| `type` | One of the four types defined below |
| `category` | Copied from the item bank (R = recognition, C = comprehension). Do not re-judge |
| `confidence` | 3 = certain; 2 = probable (paraphrase, mild inference); 1 = weak (inference, visual-only, or several plausible spans) |
| `key_check` | Does the video support the keyed option(s)? `supported` / `partial` / `not_in_video` / `inconsistent` (no option matches what the video says) |
| `visual_only` | `yes` if the decisive information is only on screen (text, label, diagram), not spoken |
| `ambiguity_note` | Free text, at most 25 words, for any unresolved doubt |
| `annotator_id` | A human annotator code (e.g. `H1`, `H2`); never `R1`, `R2` or `LLM` |

The four values of `type`:

| Type | Use when |
|---|---|
| `localized` | All information needed is in **one** contiguous span of **≤ 45 s** |
| `multi_span` | Information from ≥ 2 spans **more than 30 s apart** is needed |
| `diffuse` | Answering requires integrating content spread over > 45 s or the gist of the whole video |
| `absent` | The information is neither spoken nor shown in the shown portion of the video |

### Rules for special item formats

1. **"Mark the INCORRECT …" / "… EXCEPT":** the evidence span is the span that **refutes the keyed statement**. If the keyed statement can only be identified by confirming all other options, use `multi_span`.
2. **"All options are correct":** the span must cover all options. If they lie more than 30 s apart, use `multi_span`.
3. **Calculation or application items:** mark the span that states the rule or formula needed, with `confidence` ≤ 2.
4. **Items with a graph supplied at test time:** mark the span that teaches the concept the graph item tests, and note "graph item".
5. **Repeated content** (a fact stated twice): mark the **first** clear statement as the evidence span and the repetition as an `extra_span`.
6. **Content in trimmed material** (`NOT SHOWN`): mark the span anyway with source times. The code will flag that it was not shown.

## 3. Procedure

1. **Calibration (both annotators together, 30 min).** Two practice items from a non-BBBD video, chosen by the coordinator. They are not among the 131 items.
2. **Independent annotation.** Each annotator works alone, video by video, in a fixed order (Stars → Enzymes as in the item bank). There is no discussion, and neither sees the other's sheet or R1/R2.
3. **Submission.** Each annotator returns one CSV per the template. Files are hashed on receipt (`sha256sum`).
4. **Agreement** (`cairn.anchors.gate_g_an`):
   - centre difference and span IoU for items both annotators marked `localized`;
   - agreement on the localized flag;
   - Cohen's κ on `type`.
5. **Gate G-AN** (plan §11.2): median centre difference ≤ 10 s **and** median IoU ≥ 0.4 over items both marked `localized`. If the gate fails, the protocol is revised and **all** items are re-annotated. Spans are never cherry-picked.
6. **Adjudication** (third person, or both annotators in discussion, with R2 shown as a non-binding opinion):
   - items whose centres differ by > 10 s or whose types disagree are resolved;
   - an item that cannot be resolved becomes `diffuse`;
   - every decision is logged in `adjudication_log.md`: item, both proposals, decision, reason.
7. **Freeze.** `cairn.anchors.freeze()` hash-binds the two human files, the adjudicated table, the adjudication log, the item bank and the Stage-0a timeline. It refuses machine-authored files and refuses unless G-AN passes. The freeze happens **before any item outcome is linked to any signal** (plan §11.2 step 4).

## 4. Effort and roles

- About 2 annotator-days each: 131 items, 11 short videos.
- Annotators need no domain expertise beyond secondary-school science, and should not be members of the analysis team that will see development outcomes.
- The coordinator builds the package, hashes the returns and runs the gate.

## 5. What is published

The adjudicated anchor table, both annotators' sheets (pseudonymous), the adjudication log, the agreement report and this protocol. Transcripts and videos are **not** redistributed. They are regenerated from the public sources by `make_annotation_package.py`, and their cue hashes are recorded.
