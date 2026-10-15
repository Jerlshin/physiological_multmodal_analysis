# External ocular replication on John et al. 2025 (OSF 4rn5q)

Phase run 2026-10-07. It is the next step ranked first when the preregistered G01-R phase closed ([final report §13](../preregistered_completion/final_report.md#13-ranked-recommendation-for-the-next-methodological-direction-not-implemented), PCD-013).

**Why this step, and not a new model on BBBD.** The pre-declared [M08 rules](../experimental_design/method_necessity.md) license new method work only after a *detected* H1. On BBBD, H1 was a bounded negative. M08 therefore prescribes no method development on BBBD and an external ocular replication instead.

The only signal that survived on BBBD was the small gaze-block increment (H2d, Ŝ 0.031). BBBD could not say whether it is learner criterion information or prior knowledge and eye-quality behaviour. John 2025 adds what BBBD lacks:

- an independent cohort (different lab, tracker unit and language);
- a **pretest**;
- raw EDF files in which data loss can be decomposed.

**Governing documents:**

- the [plan](../experimental_design/external_analysis_plan_john2025.md), time-stamped by commit `ef1df1b` before any John participant-level file was downloaded;
- the [implementation clarifications and declared amendments](implementation_clarifications.md), hash-bound before the posttest was read.

**Results:** [results.md](results.md).

## Headline

**Status: REPLICATION COMPLETE. The plan's confirmatory contrast is detected.**

- **Primary (plan, confirmatory): the gaze block adds held-out information beyond the pretest-adjusted baseline.**
  - Ŝ = 0.079, permutation p = 0.002 (112 people).
  - Pre-declared reading: detected, with a point estimate of useful size.
  - **The size is imprecise.** The 90% nested-CV interval is −0.050 to 0.215. Skill is positive in all 50 CV repetitions (0.042–0.118). In absolute terms RMSE falls from 2.26 to 2.17 items out of 13.
- **Secondary (BBBD H2d analogue, no pretest):** Ŝ = 0.066, p = 0.006.
  - The increment is larger *with* the pretest in the baseline, so it is not a prior-knowledge proxy here.
- **Robust to eye-QC policy (A1):** 0.082 / 0.079 / 0.096 at QC 0.30 / 0.50 / 0.70. BBBD's increment halved under the strictest QC.
- **Not absorbed by explicit blink, loss and off-screen measures (A2):** 0.109.
- **Composition differs from BBBD.** Most of the increment comes from reference-free gaze (dispersion, saccade rate: 0.058). Gaze ISC adds about 0.02 beyond them, and pupil ISC adds nothing (−0.019). These are estimates only.
- **Working model on this cohort (M5p):** held-out RMSE 2.17 items, against 2.60 for the mean and 2.32 for pretest only. The pretest carries 64% of the gain and gaze 19%.
- **Calibration:** the frozen test is calibrated on these features, outcome-free (false detection 0.045 / 0.050).

## Sequence and gate evidence

| UTC (2026-10-07) | Step | Result | Evidence |
|---|---|---|---|
| 20:53–21:05 | Acquire `/Mine/Mine_Eye/edf` + scripts/workbook (`fetch`) | 136 files, 1,475,872,229 bytes, every file's SHA-256 equal to OSF's (3 rate-limited files retried) | [download_manifest.json](evidence/download_manifest.json) |
| ~21:06 | Parse 118 EDFs on the original EDF clock (`parse`) | 500 Hz, right eye, 1680 × 1050, no sample gaps; one `start_video_mine` / `stop_video_mine` each; window 946.70 s for all | [edf_parse_summary.csv](evidence/edf_parse_summary.csv) |
| ~21:10 | Features, 128 Hz series, case flow (`features`) | 117 people; 5 excluded by the frozen QC (> 0.50 invalid); **112** analysed | [case_flow.csv](evidence/case_flow.csv), [person_features.csv](evidence/person_features.csv) |
| — | Equivalence of the chunked gaze ISC with the frozen `reference_correlations` | Bit-identical (real series, gaze and pupil; unit test) | `tests/test_john2025.py` |
| ~21:13–21:37 | Outcome-free calibration of the primary test (`validate`) | False detection 0.045 (pure null), 0.050 (nuisance null); criterion ≤ 0.07 met | [null_calibration_summary.json](evidence/validation/null_calibration_summary.json) |
| 21:37:47 | Feature freeze (`freeze`) | Record `ead43998…`; plan byte-identical to `ef1df1b`; reused `g01r` code equals the BBBD freeze (`ead83bb6…`) | [feature_freeze.json](evidence/feature_freeze.json) |
| 21:38:04 | Gates before access | John freeze `VERIFIED`; BBBD `verify-freeze` `VERIFIED`; BBBD access log still 15 lines; tests 109 + 8 pass | [01](evidence/logs/01_gates_pre_run.log), [02](evidence/logs/02_tests_pre_run.log) |
| 21:38:19 | **The only outcome access** (`run`), after the loader re-verified the freeze | 117 people; item scores {0, 0.5, 1}; item sum equals `knowPost_sum` | [outcome_access_log.jsonl](evidence/outcome_access_log.jsonl) |
| 21:38–22:39 | Every registered comparison (`run`), run `20261007T213818Z` | Exit 0, 61 min. Frozen configuration; no overrides; R = 50, B = 999, 200 nested repetitions; 5 workers | [03](evidence/logs/03_run_stdout.log), [results.json](evidence/results/results.json), [run.json](evidence/results/run.json) |
| 22:40:23 | Post-run gates | John freeze `VERIFIED`; BBBD `verify-freeze` `VERIFIED`; BBBD access log 15 lines; John access log 1 line | [04](evidence/logs/04_gates_post_run.log) |

**Untouched:** no BBBD outcome was read (the BBBD access log stays at 15 entries), and no bound BBBD file changed.

## Commands

```sh
cd /Users/jerlshin/FieldOfInterest/ResearchWork/NTU_research
/opt/homebrew/opt/python@3.14/bin/python3.14 -m venv .venv-ext
.venv-ext/bin/python -m pip install -r requirements-john2025.lock      # eyelinkio wheel from PyPI
export PYTHONPATH=src
.venv-ext/bin/python -m john2025 fetch        # OSF subset, SHA-256 verified
.venv-ext/bin/python -m john2025 parse        # EDF -> archives (outcome-free)
.venv-ext/bin/python -m john2025 features     # features, series, case flow (outcome-free)
.venv-ext/bin/python -m john2025 validate     # synthetic-null calibration (outcome-free)
.venv-ext/bin/python -m john2025 freeze       # feature-freeze record
.venv-ext/bin/python -m john2025 verify       # must print VERIFIED
.venv-ext/bin/python -m john2025 run --workers 5   # gated outcome access + all comparisons
.venv-ext/bin/python docs/research/external_john2025/evidence/summarize.py
```

## Code and environment

| Item | Value |
|---|---|
| Package | `src/john2025/` (13 files). It imports `g01r` read-only and is never imported by it |
| Reused frozen code | `g01r` ridge, pipeline, reference plans, metrics, permutation test, nested CV, futility bound and decision table. Code hash `ead83bb6…` (= BBBD freeze); config `f34f1b03…` |
| Environment | `.venv-ext`: Python 3.14.5; numpy 2.5.3, scipy 1.18.1, pandas 3.0.6, pyarrow 25.0.1 (identical to the BBBD lock); eyelinkio 0.3.0 (bundled SR Research EDF API 4.2); openpyxl 3.1.5. [requirements-john2025.lock](../../../requirements-john2025.lock) |
| Frozen `.venv` | Untouched (BBBD freeze binds its package versions) |
| Data on disk (git-ignored) | `data/john2025/` (raw OSF subset); `data/derived/john2025/` (archives, series, tables) |
| Run store (git-ignored) | `results/runs/john2025/<run id>/` with participant-level predictions |

## Evidence folder

| Path | Content |
|---|---|
| `evidence/download_manifest.json` | Per-file URL, OSF SHA-256/MD5, local SHA-256, status |
| `evidence/edf_parse_summary.csv`, `edf_parse_meta.json` | Per-EDF structure (rates, eye, display, messages, gaps, window) |
| `evidence/person_features.csv`, `feature_definitions.json`, `case_flow.csv` | Outcome-free features and QC flow |
| `evidence/validation/null_calibration_summary.json` | Calibration of the primary test |
| `evidence/feature_freeze.json` | The freeze record |
| `evidence/outcome_access_log.jsonl` | Every posttest access (one) |
| `evidence/results/results.json`, `run.json` | Aggregate results and run provenance (no participant-level values) |
| `evidence/tables/` | Tables written by `summarize.py` |
| `evidence/logs/` | Gate, test and run logs |
| `evidence/SHA256SUMS` | Hashes of this folder's files |

## Deviations and notes

- **No deviation from the plan.** The operational decisions it left open are IJ-001…IJ-018, fixed before access.
- **Not run (IJ-017):** the plan's descriptive BBBD→John transport check. It needs a new BBBD outcome access outside the 17 preregistered G01-R analyses, which is a user decision.
- **Declared amendments A1/A2** are results-informed and estimate-only. The plan's contrast stays primary.
- **Outcome semantics:** the workbook scores some items 0/0.5/1. The outcome is therefore the supplied partial-credit proportion (plan: "scoring supplied in the workbook"), not BBBD's exact-set score.
- **Time-stamping:** no git commit was made during this phase, since commits are user actions here. Ordering is evidenced by the hash-bound freeze record and the access log that quotes its hash. Commit the phase to time-stamp it.

## Ranked next steps (not started)

1. **A registered explanatory follow-up on John.** It answers what the gaze information is: which features carry it and in which direction (for example, lower dispersion meaning gaze held on the content), using per-feature drop-one increments and full-data coefficients. It also fits the final M5p on all 112 learners as a documented "working model" artefact with a model card. This needs **one new logged outcome access**, labelled post hoc relative to the plan.
2. **A second independent ocular cohort: Lallé et al. 2025** (53 learners, 15-item quiz with per-item "already knew"). It is self-paced, so it supports reference-free features only — which is where John's increment sits. It needs clarification of the data-reuse terms (the licence file is a software licence) and authorization to download about 168 MB.
3. **BBBD→John transport (IJ-017).** This tests whether a BBBD-trained reference-free gaze model transfers to John. It needs the user's decision on a new BBBD outcome access outside the preregistered registry.
4. **Design of the prospective cohort** (G01-R recommendation 3). Use this estimate (≈ 0.08, imprecise) and BBBD's (≈ 0.03) in a design simulation. Instrument gaze and quality well; prioritize a pretest and many content units.

**Not recommended:**

- new architectures on BBBD or John;
- EEG- or ECG-specific work;
- re-specifying the confirmatory contrast.

Any feature search on John now uses a cohort that has served as confirmation, so it would be exploratory.
