# Stage-1 entry state (2026-10-13)

Recorded before any Stage-1 output was written. The logs are in [evidence/](evidence/): `entry_time.txt`, `verify_freeze_entry.log`, `unittest_entry.log`, `entry_sha256.txt` and `stage0_sha256_check_entry.log`.

## 1. Instruction

The user accepted Stage 0 and asked for **Stage 1 only**, following [research plan v1.2](../research_plan.md) and [stage0/stage1_spec.md](../stage0/stage1_spec.md). The instruction:

- **No** development, locked or external outcome access.
- Keep the Stage-0 modality decision and the CAIRN-linear primary, unless Stage-1 evidence logically requires a change.
- Redesign the confirmatory procedure now if locked power is inadequate, **without weakening the effect threshold**.
- Stop after Stage 1.

## 2. Repository and frozen material

| Check | Result |
|---|---|
| HEAD | `ade5102` (branch `main`); Stage-0 and planning work still uncommitted (a user action) |
| `PYTHONPATH=src .venv/bin/python -m g01r verify-freeze` | **`VERIFIED`** |
| Full test suite (`unittest discover -s tests`) | **130 tests, OK** (2 skipped) |
| BBBD outcome-access log `analysis_freeze/outcome_access_log.jsonl` | 15 lines, SHA-256 `2ea691fa…` (unchanged since G01-R) |
| John outcome-access log | 1 line, SHA-256 `766489e7…` (unchanged) |
| CAIRN freeze / authorization / access log (`analysis_freeze_cairn/`) | **absent** |
| Stage-0 evidence (`stage0/SHA256SUMS`) | **64/64 files OK** |
| Provisional anchor table | SHA-256 `69ce6c83…` (machine anchors, not frozen) |
| Item bank | SHA-256 `74fc8c2f…` |

## 3. What Stage 1 may and may not read

| Allowed (outcome-free) | Never read |
|---|---|
| 10 Hz series and per-second channels of every exposure, **including the tested exposures of E4 and E5** (spec §1.2; their use was disclosed for G01-R) | `quiz_items.parquet`, `quiz_video_outcomes.parquet`, `item_difficulty.csv`, `quiz_aggregate_comparison.parquet` and any other outcome-valued file |
| Availability flags: `gate_behavior_eligible` through the frozen `g01r.population.tested_cells` whitelist; gaze basic-QC flags | Any learner response, score or correctness |
| Item bank (texts, options, number of keyed options, R/C) and the release questionnaire **sidecars** (`stimuli_questionnaire.json`: question and option texts only) | The release questionnaire **TSV** files (they hold responses) |
| Stage-0 timeline and provisional anchors | John 2025 or any external data |

**Disclosure.** Stage 0 kept locked-cohort signals out of *design analyses* (S0-D03). Stage 1 uses the E4/E5 tested-exposure signals, as the Stage-1 spec prescribes, to compute their moment terms. The power and calibration simulations therefore rest on the real locked-cohort signal structure. The outcomes are synthetic, and no outcome of any cohort enters any computation.

## 4. Environment

| Item | Value |
|---|---|
| Frozen `.venv` | Python 3.14.5, numpy 2.5.3, scipy 1.18.1, pandas 3.0.6, pyarrow 25.0.1. **Not modified** |
| `.venv-cairn` (new) | Created with `uv venv --offline`. It **adds no package**: one path file exposes the frozen `.venv` site-packages read-only. An offline install from cache was impossible (wheels not cached), and a download needs user authorization. Optional Stage-2 baseline dependencies are therefore not installed |
| `requirements-cairn.lock` | Pins the identical scientific stack; documents the deferred optional dependencies |
| Machine | 10 CPU cores; simulations use 9 single-threaded worker processes under `caffeinate` |
