# Stage-0 entry state (2026-10-13)

Recorded before any Stage-0 work. Logs and hashes are in [evidence/](evidence/):

- `verify_freeze_entry.log`
- `unittest_entry.log`
- `entry_sha256.txt`
- `incidents.log`

## 1. Repository and freeze

| Check | Result |
|---|---|
| HEAD | `ade5102` (branch `main`): "Complete the preregistered G01-R plan (run-book steps 2-5) and close the phase" |
| Freeze tag | `g01r-freeze-v1` (freeze commit `6ba87fe`; manifest `a2594996…`) |
| `PYTHONPATH=src .venv/bin/python -m g01r verify-freeze` (10:19:09Z) | **`VERIFIED`** |
| `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests` (10:19:20Z) | **109 tests, OK** (2 skipped) |
| BBBD outcome-access log `analysis_freeze/outcome_access_log.jsonl` | **15 lines**; last entry 2026-10-07T18:38:23Z; SHA-256 `2ea691fa…`. Unchanged since the G01-R phase |
| John outcome-access log `docs/research/external_john2025/evidence/outcome_access_log.jsonl` | **1 line** (2026-10-07T21:38:19Z); SHA-256 `766489e7…`. Unchanged |
| Planning-phase evidence (`novel_method/evidence/SHA256SUMS`) | All 16 files OK |
| John evidence (`external_john2025/evidence/SHA256SUMS`) | All OK |

## 2. Uncommitted work at entry

Commits are user actions (JRP-010).

| Status | Path | Phase |
|---|---|---|
| modified | `.gitignore` (`.venv-ext/`, `data/john2025/`) | John |
| modified | `docs/research/README.md`, `decision_log.md`, `inference_register.md`, `research_gap/decision_log.md` | John + planning |
| untracked | `docs/research/external_john2025/`, `src/john2025/`, `tests/test_john2025.py`, `requirements-john2025.lock`, `results/` | John |
| untracked | **`docs/research/novel_method/`** (plan v1.1, critical review, literature review, evidence) | **Planning (this phase's input)** |
| modified | `.DS_Store` files | OS artefacts |

**Recommended user action:** commit the planning phase separately, before the Stage-0 files, to time-stamp the plan. Until then, ordering is evidenced by the entry hashes in `evidence/entry_sha256.txt` (taken 2026-10-13T10:19Z, before any Stage-0 output existed).

## 3. Historical / frozen material that Stage 0 must not modify

Verified unmodified at the end of Stage 0 (see the README §"Exit checks"):

- `analysis_freeze/` (freeze manifest, cache index, authorization, access log, record);
- every file bound by the G01-R freeze manifest (`src/g01r`, `configs/`, `tests/` G01-R files, bound docs);
- `docs/research/{dataset_exploration, dataset_landscape, selected_dataset, research_gap, experimental_design, baseline_implementation, confirmatory_h1h2, preregistered_completion, external_john2025}/`;
- `src/john2025/`, `src/bbbd_audit/`, `data/bbbd/`, `data/john2025/`, `data/derived/g01r/`, `data/derived/john2025/`;
- the planning documents `novel_method/{research_plan.md, literature_review.md, critical_review.md, README.md, evidence/}`. These may be **amended** only by dated, labelled additions (see the README), never silently.

Stage-0 additions are confined to:

| Location | Content |
|---|---|
| `docs/research/novel_method/stage0/` | Stage-0 documents and evidence |
| `src/cairn/` | New package |
| `tests/test_cairn.py` | New tests |
| `data/stimuli/` | Git-ignored: public videos, captions, literature copies |
| `data/derived/cairn/` | Git-ignored: derived caches |
| `.gitignore` | One line: `data/stimuli/` |

Plus dated amendments to the plan, literature review, phase README, research index, decision log and inference register.

## 4. Disclosures

1. **Pre-existing outcome-derived artefacts (2026-10-02 forensic audit, before any CAIRN work).**
   - Files: `docs/research/dataset_exploration/evidence/quiz_items.parquet` (item-level rows, including answers and correctness), `quiz_video_outcomes.parquet`, `quiz_aggregate_comparison.parquet`, `item_difficulty.csv`, `gate_closure_quiz_content_summary.json`, `gate_closure_historical_quiz_comparison.json`.
   - The audit reconstructed scores from item rows for all experiments, including E4/E5. That was a data-integrity use, never linked to physiology. It is disclosed here because CAIRN's locked cohorts are defined at the **item** level.
   - **Not opened in Stage 0**, except item 2 below. Only the Parquet *schema* (column names) of `quiz_items.parquet` was read, to specify the gated loader.
2. **Incidental exposure (2026-10-13 ≈ 10:2xZ).**
   - While checking a file header, the first 600 bytes of `gate_closure_quiz_content_summary.json` were printed.
   - They contained, for E1 "domain" questions: 1,269 rows, 27 people, key values [1.0], an **experiment-wide** mean score of 0.535, and answer-option counts.
   - No item-, video- or learner-level value was shown.
   - The file was not opened again, and no Stage-0 decision depends on it.
   - Logged in `evidence/incidents.log`.
3. **Use of locked-cohort signals.** Stage-0a pooled the peer gaze of all experiments, including E4 session 2 and E5 session 2, to estimate the stimulus timeline. No outcomes were involved; the result is a property of the stimulus files, and the mappings are reproduced by non-locked groups. All Stage-0c design analyses exclude those exposures.

## 5. Environment

| Item | Value |
|---|---|
| Frozen `.venv` | Python 3.14, numpy 2.5.3, scipy 1.18.1, pandas 3.0.6, pyarrow; no scikit-learn, no PyTorch. **Not modified** |
| `yt-dlp` | System 2026.03.17 (HTTP 403 on media). A current `yt-dlp` 2026.08.19 was installed in a session scratch virtualenv, used **only** to fetch the public stimulus media. Not a project dependency |
| `ffmpeg` / `ffprobe` | System (Homebrew) |
| Machine | 10 CPU cores, 16 GB RAM, about 21 GB free disk at entry |
