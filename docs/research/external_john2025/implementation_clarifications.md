# Implementation clarifications and declared amendments — John 2025 replication

Written 2026-10-07, **before any John 2025 posttest value was read**. This file is bound by SHA-256 in [evidence/feature_freeze.json](evidence/feature_freeze.json). The outcome loader (`src/john2025/outcomes.py`) refuses to read the posttest unless that freeze verifies, and it logs the record's hash with every access in [evidence/outcome_access_log.jsonl](evidence/outcome_access_log.jsonl).

**Governing plan:** [external_analysis_plan_john2025.md](../experimental_design/external_analysis_plan_john2025.md). It was time-stamped by commit `ef1df1b` (2026-10-04), before any John participant-level file was downloaded. The freeze checks that the plan is still byte-identical to that commit.

**What was seen before this file was written (outcome-free):**

- the 118 EDF files;
- the workbook's `LeVi` sheet;
- the `Quest` columns read by `population.py`: participant, age, sex, condition, pretest items;
- the column names of `Quest`;
- the fact that the two workbook copies have identical `Quest` content (an equality check only).

No `knowPost_*` value was printed, summarized or joined to any feature.

**Authorization.** On 2026-10-07 the user asked Claude to "understand everything and do the next step". The next step recorded in the closed G01-R phase is this replication ([final report §13](../preregistered_completion/final_report.md), PCD-013). That instruction was taken as the authorization the plan requires for the download. Only the subset the plan uses was fetched: `/Mine/Mine_Eye/edf` and the scripts/workbook, 1.48 GB in total. The EEG folders and the non-educational "Bang" clip were not fetched.

## Clarifications (IJ)

The plan fixes the question, data, features, models, CV and inference. The items below fix what it leaves operational.

| ID | Topic | Decision | Why |
|---|---|---|---|
| IJ-001 | Nesting of the primary contrast | **M5p = M2p + gaze RF + gaze ISC**, compared with **M2p** (the plan's "M5-ext versus M2p"). Secondary: **M5-ext = M2-ext + gaze blocks**, compared with **M2-ext** | An increment "beyond" a baseline needs the full model to contain that baseline. Every BBBD contrast was nested in this way |
| IJ-002 | Video window and onset | `[start_video_mine, stop_video_mine)` on the EDF clock. Each of the 118 files contains each message exactly once, and every window is 946.70 s | The plan aligns "at video onset". The authors' scripts assume onset = recording start + 3000 ms; the observed offset is 3011–3033 ms |
| IJ-003 | Q-ext | 1 − valid / expected 500 Hz samples in the window. No file has a sample gap, so expected = recorded | "Invalid-sample fraction" |
| IJ-004 | 128 Hz grid | The mean of the valid 500 Hz samples in each 1/128-s bin from onset; a bin without a valid sample is NaN. Per-person length is ⌊window × 128⌋ (121,175–121,180 bins), NaN-padded with the frozen `_pad` | The plan fixes a 128 Hz common grid but not the resampling |
| IJ-005 | Display | `DISPLAY_COORDS 0 0 1679 1049` in all files, so 1680 × 1050 and diagonal 1981.1 px. "On the display" means 0 ≤ x < 1680 and 0 ≤ y < 1050 | Plan; mirrors the BBBD rule |
| IJ-006 | Blink buffer | EyeLink ENDBLINK intervals: samples with start − 100 ms ≤ t ≤ end + 100 ms are invalid | Plan (±100 ms) |
| IJ-007 | Saccade onset "in valid time" | An EyeLink ENDSACC event whose start lies in the window and whose nearest sample (within 1 ms) is valid | Plan |
| IJ-008 | Covariates | Age in years; `sex_n` (binary 1/2, no other value); `condition` (0/1); pretest = sum of the 7 `knowPre` items, equal to `knowPre_sum` in all 121 rows. No missing values. Mental effort, exertion and EEG comfort are not used | Plan |
| IJ-009 | Outcome | The mean of the 13 `knowPost` items as scored in the workbook, cross-checked against `knowPost_sum`. Whether the items are binary or partial is recorded at the first access (the plan's exact/partial note) | Plan |
| IJ-010 | Pupil (secondary block) | Pupil valid = a valid gaze sample with finite pupil > 0. The pupil is z-scored over its valid samples in the window and resampled as in IJ-004. SYN-P is reported as estimates (M5p_pupil versus M2p and versus M5p), with no test. There is no pupil-level feature | Plan: "pupil ISC only as a secondary block" |
| IJ-011 | Evaluation machinery | The frozen `g01r` functions, unchanged (the code hash must equal the BBBD freeze), with the frozen configuration `f34f1b03…`: 10-fold person CV × R = 50; inner 5-fold ridge; 13-value grid; clip [0, 1]; base seed 20261004 with label-addressed streams keyed by the set name (`JOHN2025_mine`). There is one cell per person, the content offset is the training mean (one video), and the cohort is coded as a single experiment | Plan: "same … as frozen for BBBD H1" |
| IJ-012 | Test and interval | Freedman–Lane person-block permutation test on the first 10 paired repetitions, 999 permutations. The tested block (gaze RF + gaze ISC) is residualized on an intercept + C + P + Q (primary) or C + Q (secondary). All people are exchangeable (one protocol, one video). The interval is nested CV at 90% with 200 repetitions | Plan |
| IJ-013 | Reading the primary result | The BBBD H1 decision table: detected-useful / detected-small / bounded-negative / inconclusive, with δ = 0.05. It uses the corrected resampled-t upper bound (z = 3) against 2δ = 0.10 | The plan names only the test and the interval. The categories are fixed here, before access |
| IJ-014 | Repetitions | R = 50, as in the plan. The M07 summary's "repeated 20 times" is superseded by the time-stamped plan | Plan governs |
| IJ-015 | Population and QC | 117 people = 118 EDFs ∩ 121 `Quest` rows. A020523 has an EDF but no row; 4 rows have no EDF. The frozen QC excludes 5 people (invalid > 0.50), leaving **112**. The paper's post hoc 105 is not used | Plan |
| IJ-016 | Gaze-ISC computation | A chunked evaluation of the frozen `reference_correlations`, **bit-identical** on real series and in `tests/test_john2025.py` | Memory/time only |
| IJ-017 | **Not run: the plan's BBBD→John transport check** | Training on BBBD needs **a new BBBD outcome access outside the 17 preregistered G01-R analyses** (the OSF registration does not include the John plan). Left for the user's decision | Outcome-access discipline of the BBBD freeze |
| IJ-018 | Validation before access | Outcome-free calibration of the primary test on these real features: 200 pure-null and 200 nuisance-null synthetic score vectors, 199 permutations each. Criterion: false detection ≤ 0.07, the BBBD bound. If it fails, the declared BBBD fallback (stratified person bootstrap) decides the primary result | Mirrors BBBD V2 |

## Declared amendments (results-informed, estimate-only)

As the BBBD final report requires, these were prompted by the G01-R results and are declared as such. The plan's original contrast stays primary, and none of them carries a test.

| ID | Analysis | Motivation (G01-R final report) |
|---|---|---|
| A1 | The primary contrast re-estimated on eye-QC sets ≤ 0.30 (105 people) and ≤ 0.70 (116), the BBBD H3.2 thresholds | §5–§6: the gaze block's robustness to eye-quality policy was untested by design |
| A2 | Q replaced, in both the baseline and the full model, by its decomposition into three window shares: **short blinks** (parsed blinks ≤ 500 ms), **long loss** (parsed "blinks" > 500 ms, i.e. track loss or looking away) and **off-display gaze**. Also M2p_QD versus M2p | §6, §12: separate looking-away and data loss from criterion information. In these files EyeLink parses every pupil loss as a blink (non-blink loss is 0 for all 117 people), so duration is the available separator |
| Ladder | M1 vs M0, M1p vs M1, M2p vs M1p, M2p vs M2-ext, M3p (RF only) vs M2p, M4p (ISC only) vs M2p, M5p vs M3p (H2a analogue) | Locate any increment, as in the BBBD ladder; estimates only |

**Time-stamping in this session.** Git commits are the user's action here. Ordering is therefore evidenced by the hash-bound freeze record, written before the first access, and by the append-only access log that quotes its hash. Committing the phase is recommended.
