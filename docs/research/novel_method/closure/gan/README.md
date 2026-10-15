# Gate G-AN and the road to the first development outcome — coordinator run-book

Every step below is ready. Steps marked ✋ need a person: annotators, an adjudicator, or you. All commands run from the repository root with `PYTHONPATH=src .venv-cairn/bin/python -m cairn …`, written below as `cairn …`.

**Rules that apply throughout:**

- No step reads any learner outcome until step 9, and step 9 is gated.
- Annotators and the adjudicator are blind to learner data and to the machine proposals. They are not on the analysis team.

| # | Step | Who | Command / action | Output | Stop if |
|---|---|---|---|---|---|
| 0 | Verify the annotation package | coordinator | `cairn gan package` | 22/22 files verify against `stage0/annotation/package_manifest.json` | Any mismatch: rebuild with `stage0/scripts/make_annotation_package.py` and re-verify |
| 1 | ✋ Recruit two annotators and one adjudicator | you | Secondary-school science is enough; not on the analysis team. About 2 annotator-days each | — | — |
| 2 | ✋ Attestations | each person | Sign [templates/blinding_attestation.md](templates/blinding_attestation.md) | Signed copies, hashed into the receipt log | — |
| 3 | Build each annotator's bundle | coordinator | `cairn gan bundle H1 --out gan_private/H1.zip`, then the same for H2 | A zip containing item sheets, transcripts, protocol v1.0, addendum v1.1, a pre-filled response sheet and the attestation. It never contains R1/R2 or outcome files (checked by name). The videos are the public YouTube sources listed in the item sheets | — |
| 4 | ✋ Calibration (30 min) | both annotators + coordinator | Two practice items on one public non-BBBD video (addendum §4) | Recorded in the adjudication log preamble | — |
| 5 | ✋ Independent annotation | H1, H2 | Fill the response sheet per protocol v1.0 + addendum v1.1. Annotators never confer | `H1.csv`, `H2.csv` | — |
| 6 | Receipt | coordinator | `cairn gan receive H1.csv` (and H2) | `closure/gan/receipts.jsonl` gets the hash and validation | Validation errors: return the file for **format** corrections only (addendum §1); receive again |
| 7 | Agreement and G-AN | coordinator | `cairn gan agreement H1.csv H2.csv --out closure/gan/agreement` | `agreement_report.json` (G-AN: median centre difference ≤ 10 s **and** median IoU ≥ .4; κ on type), `agreement_items.csv`, `adjudication_worksheet.csv` | **G-AN fails:** revise the protocol and re-annotate **all** items (no item-wise selection) |
| 8a | ✋ Adjudication | adjudicator | Fill the `decision_*` columns of the worksheet. Log every decision in `adjudication_log.md` (from [templates/adjudication_log_template.md](templates/adjudication_log_template.md)). Unresolvable items become `diffuse` | Worksheet with decisions; log | — |
| 8b | Consensus file | coordinator | `cairn gan consensus H1.csv H2.csv adjudication_worksheet.csv --adjudicator ADJ --out ADJ.csv` | `ADJ.csv` (rule A1–A3), validated | Any disputed item without a complete decision |
| 8c | **Anchor freeze** | coordinator | `cairn gan freeze H1.csv H2.csv ADJ.csv adjudication_log.md --out docs/research/novel_method/closure/gan/freeze` | `ANCHOR_FREEZE.json` (Stage-0 `anchors.freeze`: human raters only, G-AN must pass), `anchors_frozen.csv` (recording clock), `ANCHOR_FREEZE_COMPANION.json` (table hash, agreement, human vs R2, locked-moment count) | Refused (machine rater, failed gate) |
| 8d | **Rule R-J re-simulation** on the human anchors | coordinator (CPU, about 10 h) | `cairn closure --grid rj --config docs/research/novel_method/closure/design_config.json --anchors docs/research/novel_method/closure/gan/freeze/anchors_frozen.csv --out docs/research/novel_method/closure/evidence/sim_rj`, then `python docs/research/novel_method/closure/scripts/rj_evaluate.py <sim_rj> <design_config.json> <anchors_frozen.csv> docs/research/novel_method/closure/gan/freeze/rj_record.json` | `rj_record.json`: passed, criteria, power at OR 1.5, power-floor flag | **Fail:** use the CV fallback, else d\* + 1, re-simulated (rule R-J). **Power below .50:** put the change to the user before going on |
| 8e | ✋ Commit | you | Commit the planning, Stage-0, Stage-1, closure and G-AN work | A git commit time-stamps everything before any outcome | — |
| 8f | **CAIRN freeze** | coordinator | `cairn freeze build --stage development --anchors docs/research/novel_method/closure/gan/freeze --rj docs/research/novel_method/closure/gan/freeze/rj_record.json --config docs/research/novel_method/closure/design_config.json --write` | `analysis_freeze_cairn/FREEZE_RECORD.json`, which binds code, environment locks, design configuration, anchor freeze, anchor table, timeline, R-J record and the rule files | Refused (anchor freeze changed, R-J missing or not passed, no decision ID) |
| 8g | ✋ Authorization | you | `cairn freeze authorization-template --scope development` prints the JSON. **You** write it to `analysis_freeze_cairn/AUTHORIZATION.json`, with your name and time | Authorization binding the freeze record | — |
| 9 | Stage 2 (development, logged) | coordinator | `cairn run --scope development --config docs/research/novel_method/closure/design_config.json --anchors docs/research/novel_method/closure/gan/freeze/anchors_frozen.csv --out results/cairn/development/`, then `run_ml` in `.venv-cairn-ml` | `development_report.json`, `selections.json`; the access is logged in `analysis_freeze_cairn/outcome_access_log.jsonl` | Stop rule says stop: report exploratory negatives; E4/E5 untouched |

**After Stage 2 (Stage 3, not prepared here beyond the code):**

- Write the CAIRN preregistration (OSF).
- Build the lock freeze: `cairn freeze build --stage lock …` with `development_selections` in the design configuration.
- Write the lock authorization with the preregistration URL.
- Then `cairn run --scope locked_primary …` runs the pooled lock and the closed testing of E4 and E5.
