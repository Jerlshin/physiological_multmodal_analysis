# G01-R run-book steps 2–5 — per-analysis results records

Runs of 2026-10-06/07, tracking experiment `g01r-confirmatory`, produced by the frozen commands in the [run book](../baseline_implementation/analysis_freeze.md#run-book-after-authorization) under the [preregistration](https://osf.io/uh397/overview) and the freeze `g01r-freeze-v1`. Provenance, commands and gate logs: [README.md](README.md). Integrated interpretation: [final_report.md](final_report.md).

Every number below is copied from a run's `result.json` (copies in [evidence/runs/](evidence/runs/)) or tabulated from it by [`summarize_steps2_4.py`](evidence/summarize_steps2_4.py). That script never reads outcomes. Its only derived values are:

- case flow and quality/missingness per set, from the frozen outcome-free ledger and feature tables;
- numerical run diagnostics;
- descriptive position flags relative to 0, δ and 2δ.

**No specification was changed, no analysis was re-run, and nothing was added after outcome access.** The H1/H2 results ([h1h2_results.md](../confirmatory_h1h2/h1h2_results.md)) are unchanged and are not re-interpreted here.

Notation as in the H1/H2 report. Ŝ = person-balanced skill of the full over the base model (R = 50 outer repetitions); δ = 0.05; 2δ = 0.10. "Interval" means the prespecified interval of each analysis:

- regime A: nested CV, 90%, 200 repetitions;
- regimes B/C: two-way person × video bootstrap, 90%, B = 2000, conditional on the 8 videos;
- transport: stratified person bootstrap of the loss difference, conditional on the fitted source model.

## Status labels

| Label | Items in this document |
|---|---|
| **Robustness / sensitivity (H3)** | H3.1–H3.6 (and H3.7, reported with H1/H2). Estimate and interval only; reading per IS-028 (same sign as the primary Ŝ and same side of δ = robust). No test; H1 is not re-evaluated |
| **Secondary block (estimate only)** | M5+pupil vs M2 within H3.3 |
| **Descriptive** | Regimes B and C (D_BC), CAS policy, E5 regime A, E4↔E5 transport, E1 ocular regime A |
| **Explanatory** | Crossed REML model (X_explanatory); never predictive evidence |
| **Diagnostic** | Shortcut (ii) identity probe |
| **Confirmatory** | None in steps 2–5. The only confirmatory tests are H1 and H2a–d (step 1) |

**Multiplicity.** The preregistration defines exactly two error-controlled families: H1 (α = 0.05, one-sided) and H2a–d (Holm). Steps 2–5 contain **no test**, so they carry no multiplicity adjustment and cannot produce a "significant" result. The B/C and transport intervals are explicitly labelled conditional and approximate. The explanatory model's Wald p-values are model-conditional and unadjusted by design. With 19 slope coefficients, its smallest p (0.021) would not survive any family-wise correction: the Bonferroni bound is 19 × 0.021 = 0.39. This bound is arithmetic shown for orientation only, not a prespecified step.

---

## 1. Overview

| Analysis | Step | Status | Set (people / cells / videos) | Comparison | Estimate | Interval | Reading |
|---|---|---|---|---|---|---|---|
| H1 (reference) | 1 | Confirmatory | PAS-core 68 / 259 / 8 | M5 vs M2 | **0.021** | [−0.033, 0.072] | Bounded negative (p = 0.082; U₃ = 0.079) |
| H3.1 partial credit | 2 | Robustness | PAS-core 68 / 259 / 8 | M5 vs M2 | 0.019 | [−0.041, 0.079] | Robust |
| H3.6 GPA in C | 2 | Robustness | PAS-core 68 / 259 / 8 | M5 vs M2 | 0.015 | [−0.035, 0.061] | Robust |
| H3.2 eye QC 0.30 | 3 | Robustness | 65 / 223 / 8 | M5 vs M2 | 0.009 | [−0.021, 0.038] | Robust |
| H3.2 eye QC 0.70 | 3 | Robustness | 69 / 265 / 8 | M5 vs M2 | 0.017 | [−0.032, 0.058] | Robust |
| H3.3 PAS-four, M5 | 3 | Robustness | 57 / 216 / 8 | M5 vs M2 | 0.019 | [−0.029, 0.072] | Robust |
| H3.3 PAS-four, M5+pupil | 3 | Secondary block | 57 / 216 / 8 | M5+pupil vs M2 | 0.032 | [−0.029, 0.100] | Same sign, below δ |
| H3.4 raw-export route | 3 | Robustness | PAS-core 68 / 259 / 8 | M5 vs M2 | 0.021 | [−0.040, 0.076] | Robust |
| H3.5 without α < 0.30 video | 3 | Robustness | 68 / 234 / 7 | M5 vs M2 | 0.016 | [−0.038, 0.063] | Robust |
| H3.7 cell-weighted (from step 1) | 1 | Robustness | PAS-core 68 / 259 / 8 | M5 vs M2 | 0.013 | [−0.045, 0.068] | Robust |
| Regime B | 4 | Descriptive | PAS-core 68 / 259 / 8 | M5_B (M2 + RF) vs M2 | −0.025 (within-content) | [−0.049, −0.006] | Worse than baseline on new content |
| Regime C | 4 | Descriptive | PAS-core 68 / 259 / 8 | M5 (M2 + RF + SYN_C) vs M2 | 0.020 (within-content) | [−0.014, 0.045] | Not distinguishable from 0; below δ |
| B − C per video | 4 | Descriptive | 8 videos | — | −0.006 to −0.066 | — | Negative (C better) in 8 of 8 videos |
| CAS policy | 4 | Descriptive | CAS 72 / 302 / 8 | Policy vs M2 | −0.00002 (person-balanced) | none prespecified | No gain from the available-sensor policy |
| E5 regime A | 4 | Descriptive | E5-core 46 / 128 / 3 | M5 vs M2 | −0.023 | [−0.141, 0.098] | Uninformative; negative point |
| Transport E4 → E5 | 4 | Descriptive | 39 → 46 people, 3 videos | M5 vs M2 | −0.143 | loss diff [−0.0091, −0.0012] | M5 worse after transport |
| Transport E5 → E4 | 4 | Descriptive | 46 → 39 people, 3 videos | M5 vs M2 | 0.018 | loss diff [−0.0003, 0.0015] | Not distinguishable from 0 |
| E1 ocular regime A | 4 | Descriptive | E1-gaze 26 / 121 / 5 | M5_E1 (gaze RF + SYN) vs M2 | **0.261** | [−0.104, 0.584] | Large point estimate; very imprecise |
| Explanatory REML | 4 | Explanatory | PAS-core 68 / 259 / 8 | — | 19 slopes; none with Wald p < 0.05 among RF/SYN | Wald 95% | Not predictive evidence |
| Identity probe (shortcut ii) | 4 | Diagnostic | PAS-core 68 / 259 / 9 units | RF + SYN → unit | accuracy 0.502 | — | Majority rate 0.147: features carry content identity |

Machine-readable versions:

- [h3_summary.csv](evidence/tables/h3_summary.csv), [regime_A_steps2_4.csv](evidence/tables/regime_A_steps2_4.csv);
- [bc_pooled.csv](evidence/tables/bc_pooled.csv), [bc_per_video.csv](evidence/tables/bc_per_video.csv), [cas.csv](evidence/tables/cas.csv), [transport.csv](evidence/tables/transport.csv);
- [explanatory_fixed_effects.csv](evidence/tables/explanatory_fixed_effects.csv), [explanatory_variance.csv](evidence/tables/explanatory_variance.csv), [identity_probe.csv](evidence/tables/identity_probe.csv);
- the frozen collator's output, [g01r_report/](evidence/g01r_report/report.md).

## 2. Case flow by analysis set

From the frozen ledger ([case_flow_by_set.csv](evidence/tables/case_flow_by_set.csv)). Sets differ from PAS-core only by their frozen rule; no cell was dropped at analysis time. Each outcome loader joined an eligible score to every cell, and it raises on any missing outcome.

| Set | Rule relative to PAS-core | People | Cells | Videos | E3 people / cells | E4 people / cells | Cells removed / added vs PAS-core |
|---|---|---|---|---|---|---|---|
| PAS-core | EEG + ECG + gaze QC, eye-correction ≤ 0.50 | 68 | 259 | 8 | 29 / 148 | 39 / 111 | — |
| PAS-core eye30 | Eye-correction ≤ 0.30 | 65 | 223 | 8 | 29 / 130 | 36 / 93 | −36 / +0 (3 E4 learners lost) |
| PAS-core eye70 | Eye-correction ≤ 0.70 | 69 | 265 | 8 | 29 / 151 | 40 / 114 | −0 / +6 (1 E4 learner added) |
| PAS-four | + pupil QC | 57 | 216 | 8 | 24 / 124 | 33 / 92 | −43 / +0 |
| PAS-core alpha30 | Without `bYgV9nvgJ3E` | 68 | 234 | 7 | 29 / 123 | 39 / 111 | −25 / +0 |
| CAS | All eligible E3+E4 (no sensor QC) | 72 | 302 | 8 | 29 / 173 | 43 / 129 | −0 / +43 |
| E5-core | E5 repeat viewing, EEG + ECG + gaze QC | 46 | 128 | 3 | — | — | E5 only |
| E4-core | E4 part of PAS-core | 39 | 111 | 3 | — | 39 / 111 | — |
| E1-gaze | E1, gaze QC | 26 | 121 | 5 | — | — | E1 only |

Quality and feature missingness per set are outcome-free ([quality_missingness_by_set.csv](evidence/tables/quality_missingness_by_set.csv)):

- **Core features.** No core RF feature is missing in any complete-case set (PAS-core, its eye/alpha variants, PAS-four, E5-core).
- **Pupil.** Pupil RF is missing in 28 PAS-core cells and in none of PAS-four.
- **CAS.** CAS carries the incomplete cells: gaze missing 21, EEG missing 14, ECG RF missing 11, gaze RF missing 24.
- **EEG 16 Hz excess.** The extreme value (max 8.06 dB; set median −0.12 dB) belongs to the one pre-identified E4 learner. That learner is in every PAS-core-based set; in PAS-four the set maximum is 7.15 dB.
- **E5.** The maximum 16 Hz excess in E5-core is 2.0 dB.

## 3. Robustness: H3.1–H3.6 (with H3.7)

Common to all H3 records:

- **Model/comparison:** M5 (M2 + RF + SYN) vs M2 (content + C + Q), regime A, person-grouped experiment-stratified 10-fold CV × 50.
- **Reference access:** regime A. SYN references come from training learners only, with leave-self-out for training learners, recomputed in every split. The comparison is fold-paired with H1 wherever the set is PAS-core: H3.1, H3.4 and H3.6 have split identity `f62f7ae3…`, equal to H1's.
- **Decision:** none; no test and no futility bound by design (IS-028).
- **Multiplicity:** not applicable.

**Reading per IS-028: all eight H3 estimates (H3.1–H3.7, incl. both H3.2 thresholds) keep the positive sign of Ŝ = 0.021 and stay below δ. Every H3 analysis is therefore robust.** None of them revises H1.

| | Estimate (Ŝ) | Nested-CV 90% | Centre | Root/SE | Contains 0 / δ | Upper < 2δ | Cell-wtd | ΔRMSE (items) | E3 / E4 | Per-video positive (range) |
|---|---|---|---|---|---|---|---|---|---|---|
| H1 | 0.021 | [−0.033, 0.072] | 0.020 | 2.18 | yes / yes | yes | 0.013 | 0.022 | 0.013 / 0.026 | 5 of 9 (−0.025, 0.060) |
| H3.1 partial | 0.019 | [−0.041, 0.079] | 0.019 | 2.37 | yes / yes | yes | 0.010 | 0.020 | 0.002 / 0.029 | 4 of 9 (−0.062, 0.072) |
| H3.2 eye30 | 0.009 | [−0.021, 0.038] | 0.009 | 1.33 | yes / **no** | yes | 0.014 | 0.010 | 0.009 / 0.009 | 6 of 9 (−0.029, 0.066) |
| H3.2 eye70 | 0.017 | [−0.032, 0.058] | 0.013 | 2.03 | yes / yes | yes | 0.009 | 0.018 | 0.006 / 0.025 | 4 of 9 (−0.032, 0.064) |
| H3.3 four (M5) | 0.019 | [−0.029, 0.072] | 0.022 | 2.75 | yes / yes | yes | 0.012 | 0.021 | 0.014 / 0.021 | 5 of 9 (−0.025, 0.039) |
| H3.3 four (M5+pupil) | 0.032 | [−0.029, 0.100] | 0.036 | 2.16 | yes / yes | yes (0.0999) | 0.017 | 0.035 | 0.015 / 0.042 | 6 of 9 (−0.027, 0.059) |
| H3.4 raw | 0.021 | [−0.040, 0.076] | 0.018 | 2.12 | yes / yes | yes | 0.011 | 0.023 | 0.026 / 0.018 | 6 of 9 (−0.024, 0.048) |
| H3.5 alpha30 | 0.016 | [−0.038, 0.063] | 0.012 | 2.00 | yes / yes | yes | 0.009 | 0.017 | 0.008 / 0.022 | 3 of 8 (−0.030, 0.066) |
| H3.6 GPA | 0.015 | [−0.035, 0.061] | 0.013 | 2.15 | yes / yes | yes | 0.010 | 0.016 | 0.012 / 0.018 | 5 of 9 (−0.018, 0.052) |
| H3.7 cell-weighted | 0.013 | [−0.045, 0.068] | — | — | yes / yes | yes | — | — | — | — |

No per-video H3 estimate reaches 2δ. "Contains δ" and "upper < 2δ" describe the reported interval; they are not tests.

### H3.1 — partial-credit outcome

1. **Sample/case flow.** PAS-core 68 / 259 / 8, identical cells and folds to H1; outcome = `normalized_partial_score` (one logged access, 2026-10-06T12:32:27Z).
2. **Model.** M5 vs M2.
3. **Estimate.** Ŝ = 0.019; ΔRMSE 0.020 items; base/full person-balanced MSE 0.03000 → 0.02943.
4. **Interval.** [−0.041, 0.079].
5. **Decision.** None (no test).
6. **δ / 2δ.** Below δ; the interval contains 0 and δ and its upper limit is below 2δ.
7. **Multiplicity.** None.
8. **Reference access.** Regime A.
9. **Quality/missingness.** As PAS-core. All 8 clipped-at-0 predictions (M2 7, M5 1) are in the extreme-16 Hz learner's highest cell.
10. **Numerical.** No non-finite predictions; no penalty at the grid ends.
11. **Relation to H1/H2.** Contextualizes: score semantics do not move the estimate.

### H3.6 — GPA added to C

1. **Sample.** PAS-core 68 / 259 / 8; GPA missing for 20 of 68 learners (74 cells), handled by the prespecified missing indicator.
2. **Model.** M5 vs M2, both with GPA in C.
3. **Estimate.** 0.015; ΔRMSE 0.016 items.
4. **Interval.** [−0.035, 0.061].
5. **Decision.** None.
6. **δ / 2δ.** Below δ; the interval contains 0 and δ; its upper limit is below 2δ.
7. **Multiplicity.** None.
8. **Reference access.** Regime A.
9. **Quality/missingness.** As PAS-core; clipping at 0 again only in the extreme-16 Hz learner (M2 11 predictions over 2 cells; M5 14 over 1 cell).
10. **Numerical.** No failures; no penalty at the grid ends.
11. **Relation to H1/H2.** Contextualizes: an academic-achievement covariate absorbs a little of the increment (0.021 → 0.015) without changing its sign or side of δ.

### H3.2 — eye-correction QC thresholds 0.30 and 0.70

1. **Sample.**
   - eye30: 65 / 223 / 8. 36 PAS-core cells with gaze-correction fraction in (0.30, 0.50] are removed (E3 18, E4 18), and 3 E4 learners are lost entirely.
   - eye70: 69 / 265 / 8. 6 cells with fraction in (0.50, 0.70] are added (max 0.62), and 1 E4 learner joins.
2. **Model.** M5 vs M2 on each set; new folds per set (cold nested CV).
3. **Estimate.** eye30 **0.009**; eye70 0.017 (primary at 0.50: 0.021).
4. **Interval.** eye30 [−0.021, 0.038]; eye70 [−0.032, 0.058].
5. **Decision.** None.
6. **δ / 2δ.** Both below δ. The eye30 interval lies entirely below δ (upper 0.038); the eye70 interval contains δ. Both upper limits are below 2δ.
7. **Multiplicity.** None.
8. **Reference access.** Regime A, references restricted to each set's training learners.
9. **Quality.** eye30 gaze-correction median 0.124 (PAS-core 0.149); eye70 median 0.150, max 0.62. Clipping at 0 occurs only in the extreme-16 Hz learner: eye30 M2 64 / M5 41 predictions over all 3 of that learner's cells; eye70 5 / 12 over 1 cell.
10. **Numerical.** No non-finite predictions; no penalty at the grid ends. Root/SE 1.33 (eye30), 2.03 (eye70).
11. **Relation to H1/H2.**
    - The **full-model increment is smallest under the strictest eye-quality policy** (0.009, about half the primary) and does not grow when the policy is relaxed (0.017).
    - This narrows the H1 reading: no part of the full-model increment depends on admitting poorer eye recordings, and the estimate shrinks in the subset with cleaner eye recordings.
    - **H3.2 estimates M5, not M-gaze.** No prespecified analysis re-estimates the gaze block (H2d) or the synchrony increment (H2a) under other eye-QC thresholds. Doing so now would be post hoc.

### H3.3 — PAS-four, without and with the pupil block

1. **Sample.** PAS-four 57 / 216 / 8 (E3 24 / 124; E4 33 / 92); 43 PAS-core cells without pupil QC excluded.
2. **Models.** M5 vs M2 (robustness); M5+pupil (adds RF-P pupil variability and SYN-P pupil ISC) vs M2 (secondary block).
3. **Estimate.** M5 0.019; M5+pupil 0.032. The pupil block's addition is the difference of the two estimates, 0.013; it has no interval or test of its own.
4. **Interval.** M5 [−0.029, 0.072]; M5+pupil [−0.029, 0.100].
5. **Decision.** None.
6. **δ / 2δ.** Both below δ; both intervals contain 0 and δ. The M5+pupil upper limit reaches 0.0999, i.e. 2δ.
7. **Multiplicity.** None.
8. **Reference access.** Regime A.
9. **Quality.** Pupil correction max 0.48 (PAS-core 0.96). The extreme-16 Hz learner is represented only by its 7.15 dB cell. **No prediction is clipped** in any model.
10. **Numerical.** No failures; no penalty at the grid ends.
11. **Relation to H1/H2.** M5 is robust. The pupil block points in the same (ocular) direction as H2d but adds no confirmatory weight.

### H3.4 — raw-export feature route

1. **Sample.** PAS-core 68 / 259 / 8; identical cells and folds to H1.
2. **Model.** M5 vs M2. EEG, gaze and pupil features are recomputed from the raw exports (IS-021). ECG timing and Q are unchanged. SYN is recomputed from raw signals, with raw-route caches.
3. **Estimate.** 0.021 (processed 0.021). E3 0.026 (processed 0.013); E4 0.018 (processed 0.026).
4. **Interval.** [−0.040, 0.076].
5. **Decision.** None.
6. **δ / 2δ.** Below δ; the interval contains 0 and δ; its upper limit is below 2δ.
7. **Multiplicity.** None.
8. **Reference access.** Regime A.
9. **Quality.** Pupil RF missing in 29 cells (processed 28). Clipping at 0 only in the extreme-16 Hz learner (M2 16 predictions, M5 26, over 2–3 of that learner's cells).
10. **Numerical.** No failures; no penalty at the grid ends.
11. **Relation to H1/H2.**
    - The H1 estimate does **not** depend on the released processed derivatives. This bounds the OQ-06 provenance concern for M5.
    - Raw and processed gaze features are near-identical (BII-006: ρ ≥ 0.999), so H3.4 is mainly a test of the EEG (and pupil) route.
    - The ocular findings are route-invariant by construction. H3.4 cannot speak to them beyond that.

### H3.5 — excluding the low-reliability video

1. **Sample.** 68 / 234 / 7 (E3 29 / 123; E4 39 / 111); `bYgV9nvgJ3E` (exact α = 0.18) removed.
2. **Model.** M5 vs M2.
3. **Estimate.** 0.016.
4. **Interval.** [−0.038, 0.063].
5. **Decision.** None.
6. **δ / 2δ.** Below δ; the interval contains 0 and δ; its upper limit is below 2δ.
7. **Multiplicity.** None.
8. **Reference access.** Regime A.
9. **Quality.** As PAS-core; clipping at 0 only in the extreme-16 Hz learner.
10. **Numerical.** No failures; no penalty at the grid ends.
11. **Relation to H1/H2.** Contextualizes. Removing the least reliable criterion does not enlarge the increment, so low criterion reliability on that one video is not masking a larger effect.

## 4. New-content and reference-access behaviour: regimes B and C (D_BC)

1. **Sample.** PAS-core 68 / 259 / 8. Leave-one-canonical-video-out × person-grouped 5-fold × 20 repetitions; the jointly held-out "Are We All Related" (`mnYSMhR3jCI`) contributes 61 cells (E3 24 + E4 37). Each cell is predicted with neither its video nor its person in training.
2. **Models.**
   - **B:** M5_B = M2 + RF (reference-free; no statistic from any other viewer of the held-out video) vs M2.
   - **C:** M5 = M2 + RF + SYN_C vs M2. SYN_C uses a cross-fitted, unlabelled half-cohort reference: the other half's viewers of the held-out video.
   - B and C are paired on identical cells.
   - Offsets for unseen content are training experiment means (IS-012).
3. **Estimates** (person-balanced within-content skill, the primary B/C metric):
   - **B −0.025**, absolute skill −0.014;
   - **C 0.020**, absolute skill 0.010.
4. **Intervals** (two-way bootstrap, 90%, B = 2000; "conditional on the 8 sampled videos; approximate; undercovers the content population in simulation"):
   - **B [−0.049, −0.006]**;
   - **C [−0.014, 0.045]**.
5. **Decision.** None; B/C carry no p-values by design.
6. **δ / 2δ.**
   - B lies entirely below 0.
   - C contains 0, and its upper limit (0.045) is below δ.
   - Both lie below 2δ.
7. **Multiplicity.** None.
8. **Reference access.**
   - B: none (reference-free).
   - C: unlabelled half-cohort reference on the new video, with no person overlap with the target.
9. **Quality.** As PAS-core. B/C predictions are all finite and none is clipped (prediction range 0.16–0.65).
10. **Numerical.** No failures; all 2000 bootstrap replicates finite in both regimes.
11. **Relation to H1/H2.** Changes and narrows the interpretation (see per-video table and [final report §2–§3](final_report.md)).

Per video (cell-weighted within-content skill; [bc_per_video.csv](evidence/tables/bc_per_video.csv)):

| Video | Cells | B (M2 + RF) | C (M2 + RF + SYN_C) | B − C |
|---|---|---|---|---|
| `30o4omX5qfo` | 27 | −0.056 | −0.036 | −0.020 |
| `VVAKFJ8VVp4` | 38 | −0.019 | 0.024 | −0.043 |
| `bYgV9nvgJ3E` | 25 | −0.003 | 0.005 | −0.007 |
| `e0NT9i4Qnak` | 26 | −0.069 | −0.019 | −0.051 |
| `lkRZKqDdwzU` | 24 | −0.052 | 0.005 | −0.057 |
| `mnYSMhR3jCI` | 61 | −0.015 | 0.051 | −0.066 |
| `rkntp3_cZl4` | 22 | −0.057 | −0.016 | −0.041 |
| `zQGOcOUBi6s` | 36 | −0.008 | −0.002 | −0.006 |

Reading, limited to what these descriptive estimates show:

- **The reference-free block does not transfer to new content.** B is negative in all 8 videos, and its pooled interval excludes 0 from below. This mirrors regime A, where RF alone is −0.028, about the size of the matched-noise control (−0.021).
- **Synchrony with an unlabelled peer reference adds information on new content in every video.** B − C is negative in 8 of 8 videos (−0.006 to −0.066). The pooled C − B gap (0.045) is about the size of the confirmatory H2a increment in regime A (0.047).
- **This is not a useful new-content predictor.** C's pooled skill over the nonsignal baseline is 0.020, its interval contains 0, and its upper limit is below δ. Per protocol, the "content-library-specific validity" phrase requires a positive A result; that did not occur, so it is not used.

## 5. Coverage-set policy (D_CAS)

1. **Sample.**
   - CAS 72 / 302 / 8, of which 259 cells are PAS-core and 43 are not (E3 25, E4 18). Frozen CAS folds over CAS people.
   - The selection report is the pre-outcome [analysis_population.md](../experimental_design/analysis_population.md), which shows that complete cases scored higher. Nothing new is computed.
2. **Model.** Policy = M5 where PAS-core features exist (M5 trained on PAS-core training cells, with PAS-core training references), M2 otherwise; compared with M2 trained on all CAS training cells (IS-020).
3. **Estimate.**
   - Policy vs M2, person-balanced over all 302 cells: **−0.00002**.
   - Cell-weighted: −0.010.
   - On the 259 core cells: −0.012.
   - On the 43 non-core cells: 0 (identical by construction).
4. **Interval.** None prespecified.
5. **Decision.** None.
6. **δ / 2δ.** ≈ 0, well below δ.
7. **Multiplicity.** None.
8. **Reference access.** Regime A within CAS folds, with references from PAS-core training learners.
9. **Quality/missingness.** CAS includes the incomplete cells (gaze missing 21, EEG missing 14); M2 uses Q's missing indicators for them.
10. **Numerical.** No failure reported; the runner logs only aggregates.
11. **Relation to H1/H2.** Contextualizes. In the realistic available-sensor setting, physiology adds nothing over the nonsignal-plus-quality model. The core-cell value differs from H1's because M2 is trained on more cells (CAS) and the folds differ. It is descriptive and not comparable with H1 as a test.

## 6. Other protocols: E5 regime A, E4↔E5 transport, E1 ocular regime A

### D_E5 — repeat-exposure regime A

1. **Sample.** E5-core 46 / 128 / 3, at the repeat viewing.
2. **Model.** M5 vs M2.
3. **Estimate.** **−0.023**; cell-weighted −0.027; ΔRMSE −0.026 items. Every video is negative: `VVAKFJ8VVp4` −0.049, `mnYSMhR3jCI` −0.009, `zQGOcOUBi6s` −0.007.
4. **Interval.** [−0.141, 0.098] (root/SE 3.15).
5. **Decision.** None.
6. **δ / 2δ.** Point below 0; the interval contains 0 and δ; its upper limit is below 2δ.
7. **Multiplicity.** None.
8. **Reference access.** Regime A within E5.
9. **Quality.** Max 16 Hz excess 2.0 dB; pupil RF missing in 17 cells. 3 M2 predictions are clipped at 0 in one cell (16 Hz rank 40, not extreme).
10. **Numerical.** No non-finite predictions; no penalty at the grid ends.
11. **Relation to H1/H2.** Contextualizes. No sign of an increment under the incentivized repeat-viewing protocol, but the estimate is very imprecise (3 videos, 46 learners); the design anticipated power far below 0.8.

### D_transport — E4 ↔ E5 on the 3 shared videos

1. **Sample.** E4-core 39 / 111 and E5-core 46 / 128 (disjoint cohorts by construction); one fit on the whole source, one prediction of the whole target.
2. **Model.** M5 vs M2. Synchrony references and content offsets come from the source cohort. The recalibrated variant replaces the offsets with target video means and **uses target labels**.
3. **Estimates** (person-balanced skill):

   | Direction | Source offsets | Recalibrated (uses target labels) |
   |---|---|---|
   | E4 → E5 | **−0.143** | −0.065 |
   | E5 → E4 | 0.018 | 0.028 |

4. **Intervals** (stratified person bootstrap of the loss difference M2 − M5, conditional on the fitted source model):

   | Direction | Source offsets | Recalibrated |
   |---|---|---|
   | E4 → E5 | **[−0.0091, −0.0012]** | [−0.0054, 0.0011] |
   | E5 → E4 | [−0.0003, 0.0015] | [−0.00001, 0.0017] |

5. **Decision.** None. The bootstrap function also returns an internal `detect` flag (all false); it is not a prespecified decision and is not used.
6. **δ / 2δ.**
   - E4 → E5: M5 is worse than M2; the loss-difference interval lies below 0.
   - E5 → E4: positive, below δ, with the interval containing 0.
7. **Multiplicity.** None.
8. **Reference access.** Source-cohort references on the same canonical video (cross-protocol).
9. **Quality.** As E4-core and E5-core.
10. **Numerical.** No failure. The smoke-test failures of D_transport occurred before the freeze and were fixed then.
11. **Relation to H1/H2.** Contextualizes. The physiological model does not carry across the E4 (incidental, end-of-block test) and E5 (incentivized repeat) protocols in the E4 → E5 direction.

### D_E1 — ocular-only regime A in E1

1. **Sample.** E1-gaze 26 / 121 / 5. C = age and sex; Q = gaze and pupil correction, gaze missing, pupil absent (IS-022).
2. **Model.** M5_E1 = M2 + gaze RF (dispersion, saccade rate) + gaze SYN vs M2.
3. **Estimate.** **0.261**; cell-weighted 0.307; ΔRMSE 0.343 items; person-balanced MSE 0.0416 → 0.0307. Positive in all 5 videos (0.20–0.45).
4. **Interval.** **[−0.104, 0.584]** (centre 0.240; root/SE 1.47).
5. **Decision.** None (descriptive).
6. **δ / 2δ.** The point is about 5δ. The interval contains 0, δ and 2δ.
7. **Multiplicity.** None.
8. **Reference access.** Regime A within E1 (training-learner gaze references).
9. **Quality.** Gaze-correction median 0.110 (PAS-core 0.149); no EEG/ECG by design.
10. **Numerical warnings, reported and not acted on:**
    - The penalty sits at the lower grid end in 5.0% (M2) and 5.2% (M5_E1) of splits, i.e. near-unpenalized fits.
    - 100 of 6,050 M5_E1 predictions (and 5 M2 predictions) are clipped at 1. All are in video `3IaYhG11ckA`, in four learners.
11. **Relation to H1/H2.**
    - This contextualizes H2d: the only other cohort with an ocular-only model shows a much larger ocular point estimate, in the same direction.
    - It is a 26-person, 5-video descriptive estimate whose interval includes 0.
    - The E1 recordings are also the substrate of the original authors' published gaze-synchrony findings (P01), so this is not an independent replication.

## 7. Explanatory crossed REML model (X_explanatory)

1. **Sample.** PAS-core 68 / 259 / 8; fit once in-sample.
2. **Model.** Person and experiment × video random intercepts. Fixed effects: intercept, E4 indicator and the standardized non-constant M5 inputs. SYN uses full-cohort leave-self-out references (IS-017). Converged.
3. **Estimates** (per SD; Wald SE; [table](evidence/tables/explanatory_fixed_effects.csv)):
   - RF and SYN: SYN3 gaze ISC +0.031 (SE 0.017, p 0.065); SYN1 EEG ISC +0.028 (0.020, 0.15); RF1 posterior alpha +0.017 (0.015, 0.25). RF2, RF3, RF4, RF5, RF6 and SYN2 are all |β| ≤ 0.016 with p ≥ 0.44.
   - Quality: pupil correction −0.041 (0.018, 0.021); 16 Hz excess −0.023 (0.014, 0.10); gaze correction +0.022 (0.015, 0.14).
   - Covariates: all p ≥ 0.24.
   - Variance components: person 0.0085, content 0.0047, residual 0.0190 (shares 26%, 15%, 59%).
4. **Interval.** Wald 95% (in the table).
5. **Decision.** None; explanatory only.
6. **δ / 2δ.** Not applicable (not a skill).
7. **Multiplicity.** None prespecified; nothing would survive a family-wise correction (see top).
8. **Reference access.** Full-cohort leave-self-out (labelled explanatory; it uses references unavailable to any predictive regime).
9. **Quality.** As PAS-core; the Q terms are in the model.
10. **Numerical.** Converged; no warnings.
11. **Relation to H1/H2.** Contextualizes, without evidential weight:
    - Within the ocular block, the in-sample association sits on gaze ISC, not on dispersion or saccade rate.
    - The largest single association with the score is a quality variable (pupil correction).

## 8. Shortcut diagnostic (ii): identity probe (S_identity_probe)

1. **Sample.** PAS-core 68 / 259; 9 experiment × video units; frozen regime-A folds, first 10 repetitions (100 splits). **No outcome access** (none logged).
2. **Model.** Ridge one-vs-rest classifier from RF + SYN (regime-A training references) to the unit, with an inner person-grouped penalty (IS-018).
3. **Estimate.** Held-out accuracy **0.502**; majority rate 0.147; frequency-matched chance 0.116.
4. **Interval.** None prespecified.
5. **Decision.** None (diagnostic).
6. **δ / 2δ.** Not applicable.
7. **Multiplicity.** None.
8. **Reference access.** Regime A.
9. **Quality.** As PAS-core.
10. **Numerical.** Completed in 0.6 s on cached features; no warnings.
11. **Relation to H1/H2.**
    - The physiological features carry strong content (experiment × video) identity: 3.4× the majority rate.
    - This does **not** create a content shortcut in H1/H2, by design:
      - every regime-A model has the experiment × video offset and is fitted to within-content residuals;
      - the Freedman–Lane test residualizes the tested block on experiment × video dummies;
      - B/C use within-content losses.
    - It does mean that much of the features' variance is between-content rather than between-learner.

## 9. Step 5 — collated report

`python -m g01r report --experiment g01r-confirmatory --out results/report` collated the latest FINISHED run of all 15 executed registry analyses (exit 0; [log](evidence/logs/09_step5_report.log)); the output is copied to [evidence/g01r_report/](evidence/g01r_report/report.md). Its numbers equal those above and the step 1 tables.

## 10. Failures, warnings and operational notes

- **Model or computational failures:** none. All 14 step 2–4 runs `FINISHED`, exit 0, with frozen configuration, no overrides, code SHA-256 `ead83bb6…` (the freeze aggregate) and no MLflow errors.
- **Numerical warnings:**
  - D_E1: penalty at the lower grid end in about 5% of splits, and clipping at 1 (above).
  - Every PAS-core-based run: clipping at 0 confined to the pre-identified extreme-16 Hz learner (BII-007, CHR-007).
  - D_E5: 3 predictions clipped at 0 in one non-extreme cell.
  - No non-finite prediction anywhere.
- **Not altered:** no learner removed, no model refitted, no threshold changed.
- **Operational, not scientific:**
  - The host Mac slept during H3.2-eye70, from 2026-10-06T21:45Z to 2026-10-07T02:49Z (about 5 h, with brief maintenance wakes; system sleep was set to 1 min idle; [log 10](evidence/logs/10_operational_sleep_events.log)). The run resumed, so only wall time changed.
  - `caffeinate` was then attached to the remaining runs.
  - Step 3 took 28.4 h of wall time against the run book's 20–30 h estimate (eye30 5.6 h; eye70 9.1 h including the sleep; four 5.5 h; raw 4.4 h; alpha 3.8 h). Step 4 took 1.7 h.
