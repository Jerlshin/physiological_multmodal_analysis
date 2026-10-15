# Annotation protocol — addendum v1.1 (closure phase, 2026-10-14)

This addendum completes [ANNOTATION_PROTOCOL.md v1.0](../../stage0/annotation/ANNOTATION_PROTOCOL.md). That file is hash-bound in `stage0/SHA256SUMS` and stays unchanged; this addendum takes precedence only where it adds a rule.

It was written **before any human annotation exists**. It specifies three things the v1.0 text left to the coordinator's judgement: how agreeing items are combined, which values the files must use, and how protocol-format errors are returned. It changes no content rule, gate threshold or blinding requirement.

## 1. Machine-checked file format (rule V)

Every returned file is checked with `python -m cairn gan validate <file>` (`cairn.gan.validate_file`). The checks are:

| Field | Allowed values |
|---|---|
| Columns | Exactly those of [annotation_template.csv](../../stage0/annotation/annotation_template.csv) |
| `annotator_id` | One human code per file (for example `H1`). Codes beginning `R1`, `R2`, `LLM`, `CLAUDE`, `GPT` or `AUTO` are refused |
| Items | All 131 item-bank items, each exactly once |
| `type` | `localized`, `multi_span`, `diffuse`, `absent` |
| `key_check` | `supported`, `partial`, `not_in_video`, `inconsistent` |
| `confidence` | 1, 2, 3 |
| `visual_only` | `yes`, `no` |
| `category` | Copied from the item bank; must match |
| Span (localized, multi_span) | A source of that video; 0 ≤ start < end ≤ source duration; a `localized` span is at most 45 s |
| `extra_spans` | `start-end` or `start-end@source`, `;`-separated |

**Format errors are returned to the annotator.** The coordinator names the field and the rule, never a suggested content. Each return and resubmission is logged in the receipt log (§3).

## 2. Combining the two files (rule A)

Run `python -m cairn gan agreement H1.csv H2.csv --out <dir>`. It reports gate G-AN, Cohen's κ on `type` and per-video agreement, and writes the adjudication worksheet.

**An item needs adjudication** if the two types differ, or if both are `localized` with centres more than 10 s apart.

- **A1 — agreeing items** are combined mechanically by `python -m cairn gan consensus` (`cairn.gan.consensus`):
  - the agreed type;
  - for span-carrying types, the element-wise mean of the two spans when both used the same source, otherwise annotator 1's span;
  - confidence = the lower of the two;
  - `key_check` = the common value, or `partial` if they differ;
  - `visual_only` = `yes` if either said yes.
- **A2 — disputed items** take the adjudicator's decision row from the worksheet: `decision_type`, `decision_source`, `decision_start_s`, `decision_end_s`, `decision_reason`, `adjudicator_id`.
  - Each decision is also written to the adjudication log.
  - A disputed item without a complete decision stops the consensus step (error).
- **A3 — unresolved items** are entered as `diffuse` (protocol v1.0 §3 step 6).

R2, the LLM-assisted provisional sheet, appears **only** in the adjudication worksheet, as a non-binding column. Annotators never see it.

**If G-AN fails**, the protocol is revised and **every** item is re-annotated (v1.0 §3 step 5). Spans are never selected item by item to pass the gate.

## 3. Receipt and custody (rule R)

- Each file is hashed and validated on arrival with `python -m cairn gan receive <file>`. This appends to `closure/gan/receipts.jsonl`.
- The two annotators' files and the adjudicated file are never edited after receipt. Corrections are resubmissions with new hashes.
- The freeze (`python -m cairn gan freeze H1 H2 ADJ LOG --out closure/gan/freeze`) binds by hash:
  - both human files, the adjudicated file, the adjudication log and the item bank, through the Stage-0 `cairn.anchors.freeze`;
  - the Stage-0a timeline;
  - the recording-clock anchor table and the agreement report, through the companion record.

## 4. Practice items (protocol v1.0 §3 step 1)

The coordinator chooses **one public educational video that is not one of the 11 BBBD stimuli** and writes two items for it, one recognition and one comprehension, with a reference answer span. The practice video, items and reference spans are recorded in the adjudication log's preamble. Practice annotations are not part of any file.

## 5. Independence and blinding attestations

Before receiving the package, each annotator signs [templates/blinding_attestation.md](templates/blinding_attestation.md). The adjudicator signs it before adjudication.

Annotators and the adjudicator must not be members of the team that will see development outcomes (v1.0 §4). The coordinator may be, but then never annotates or adjudicates.
