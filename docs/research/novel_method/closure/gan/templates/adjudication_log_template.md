# CAIRN anchor adjudication log

The coordinator fills in the preamble before adjudication starts. Each decision is entered once and never edited; a later correction is a new entry that references the earlier one. This file is hash-bound by the anchor freeze.

## Preamble

| Field | Value |
|---|---|
| Coordinator | |
| Annotator 1 code / file SHA-256 (receipt) | |
| Annotator 2 code / file SHA-256 (receipt) | |
| Adjudicator code | |
| Gate G-AN result (median centre difference, median IoU, κ on type) | |
| Items to adjudicate | |
| Practice video (public URL; not a BBBD stimulus) and the two practice items with reference spans | |
| Protocol versions | ANNOTATION_PROTOCOL.md v1.0 + ADDENDUM v1.1 |

## Decisions

One row per disputed item. The same decisions go into `adjudication_worksheet.csv`, which `cairn gan consensus` reads.

| # | Video | Item | Annotator 1 (type; source; span) | Annotator 2 (type; source; span) | R2 (non-binding) | Decision (type; source; span) | Reason | Adjudicator | UTC |
|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | |
