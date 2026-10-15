# Results — external ocular replication on John et al. 2025

Run `20261007T213818Z`, 2026-10-07 21:38–22:39 UTC, exit 0. There was one outcome access, after the feature freeze `ead43998…` verified. Every analysis comes from the registry in `src/john2025/analysis.py`, frozen before access. The plan, clarifications and amendments are in [implementation_clarifications.md](implementation_clarifications.md). The source table is [tables/comparisons.csv](evidence/tables/comparisons.csv).

**Notation.**

- Ŝ = held-out skill = 1 − MSE(full)/MSE(base), over 10-fold person CV × 50 repetitions. There is one cell per person, so person-balanced and cell-weighted skill coincide.
- δ = 0.05; 2δ = 0.10.
- "Items" means points on the 13-item posttest.

**Evidence classes.**

- **Confirmatory:** the primary contrast (the plan's one-sided test).
- **Secondary:** the plan's second contrast.
- **Estimate-only:** the pupil block, the model ladder and the declared amendments A1/A2.

## 1. Data, case flow and outcome

| Step | People |
|---|---|
| Workbook `Quest` rows / instructional-video EDFs | 121 / 118 |
| EDF + `Quest` (plan population) | 117 |
| Excluded by the frozen QC (invalid > 0.50) | 5 (posttest mean 0.40, range 0.08–1.00) |
| **Primary set** | **112** (posttest mean 0.504, SD 0.199 ≈ 2.6 items) |
| A1 sets: QC ≤ 0.30 / ≤ 0.70 | 105 / 116 |

**Recordings.** All 118 are EyeLink 1000 at 500 Hz, right eye, 1680 × 1050, with no sample gaps. The video window is 946.70 s in every file.

**Outcome semantics.** These were recorded at the single access. The workbook scores items as 0, 0.5 or 1, so the outcome is the supplied partial-credit proportion; the item sum equals `knowPost_sum` for every row. As in BBBD, people excluded for eye data scored lower than those analysed.

## 2. Primary contrast (confirmatory): gaze block beyond the pretest-adjusted baseline

M5p = age, sex, condition, pretest, Q-ext + gaze dispersion, saccade rate, gaze ISC; compared with M2p = the same without the gaze block.

| Quantity | Value |
|---|---|
| **Ŝ (M5p vs M2p)** | **0.079** |
| Permutation test (Freedman–Lane, R = 10, B = 999) | **p = 0.002** (observed ΔMSE 0.0025; null 95th percentile 0.0006) |
| 90% nested-CV interval (200 repetitions) | **−0.050 to 0.215** (centre 0.082; root/SE 1.25) |
| Skill across the 50 CV repetitions | 0.042 to 0.118 (positive in every repetition) |
| ΔRMSE / ΔMAE | 0.091 / 0.066 items (RMSE 2.26 → 2.17 items) |
| Calibration slope, full model | 1.04 |
| Futility bound (z = 3) | 0.273 (does not rule out 2δ) |
| **Pre-declared reading (IJ-013)** | **detected, with a point estimate of useful size (≥ δ)** |

**What this establishes.**

- **On an independent cohort**, with the plan time-stamped before any participant file was downloaded, features frozen before the outcome was read, and a test calibrated on these features (false detection 0.045 / 0.050):
  - the BBBD gaze block, with the frozen ridge procedure, adds **detectable held-out information** about immediate posttest performance;
  - it does so **beyond prior knowledge (pretest) and eye-data loss**.
- **Its size is not pinned down.** The point estimate, 0.079, is above δ, and every CV repetition is positive. The procedure-level 90% interval, however, runs from −0.05 to 0.21.
- **The test and the interval differ by design.** The interval also carries training-set variability at n = 112, so the detection and the size statements must be kept separate.
- **In absolute terms the gain is small:** about 0.09 of a quiz item in RMSE.

## 3. Secondary contrast: gaze block without the pretest (BBBD H2d analogue)

| Quantity | Value | BBBD H2d (M-gaze vs M2) |
|---|---|---|
| Ŝ (M5-ext vs M2-ext) | **0.066** | 0.031 |
| Permutation p | **0.006** | 0.027 (Holm) |
| 90% nested-CV interval | −0.009 to 0.148 | — |

**The increment is larger with the pretest in the baseline (0.079) than without it (0.066).** On this evidence the gaze information is not a proxy for prior knowledge. That was BBBD's main interpretive gap.

## 4. Where the increment sits: the model ladder (estimates only)

| Step (primary set) | Ŝ | Range over 50 repetitions | Held-out RMSE after the step (items) |
|---|---|---|---|
| M0: training mean | — | — | 2.60 |
| + age, sex, condition (M1 vs M0) | 0.006 | −0.035 to 0.027 | 2.60 |
| **+ pretest (M1p vs M1)** | **0.198** | 0.157 to 0.233 | 2.32 |
| + Q-ext (M2p vs M1p) | 0.055 | 0.033 to 0.091 | 2.26 |
| **+ reference-free gaze only (M3p vs M2p)** | **0.058** | 0.015 to 0.088 | 2.19 |
| + gaze ISC only (M4p vs M2p) | 0.018 | −0.018 to 0.039 | 2.24 |
| ISC beyond reference-free gaze (M5p vs M3p; H2a analogue) | 0.023 | −0.013 to 0.050 | 2.17 |
| Full model M5p vs M2p (primary) | 0.079 | 0.042 to 0.118 | 2.17 |

**Shares of the full model's held-out MSE reduction over M0 (30.5%), in the order above:**

| Block | Share |
|---|---|
| Covariates | 2% |
| Pretest | 64% |
| Quality | 14% |
| Gaze | 19% |

The gaze share is close to BBBD's physiology share (18%). The absolute total is larger because the pretest carries most of the signal.

**Composition differs from BBBD.**

- In John, most of the gaze increment comes from the **reference-free** features: dispersion and saccade rate (0.058).
- Gaze ISC adds about 0.02 on top of them. On its own it adds 0.018, and its repetition ranges include 0.
- In BBBD the reverse held: reference-free features hurt (−0.028), and synchrony carried the increment (H2a, 0.047).

So the **gaze block** replicates, but the "the ocular signal is synchrony" reading from BBBD does not carry over. These are estimates without tests, and the two cohorts differ in tracker, language, video length (16 min versus about 2.4–6.4 min) and test.

## 5. Pupil block (secondary, estimates only)

| | Ŝ |
|---|---|
| M5p + pupil ISC vs M2p | 0.061 |
| Pupil ISC beyond M5p | **−0.019** (−0.044 to 0.012 over repetitions) |

Pupil synchrony adds nothing. This agrees with BBBD's decision to keep pupil secondary.

## 6. Amendment A1: robustness to eye-QC policy (results-informed, estimates only)

| QC threshold | People | Ŝ (M5p vs M2p) | Range over repetitions | BBBD M5 analogue (H3.2) |
|---|---|---|---|---|
| ≤ 0.30 | 105 | **0.082** | −0.007 to 0.134 | 0.009 |
| ≤ 0.50 (primary) | 112 | 0.079 | 0.042 to 0.118 | 0.021 |
| ≤ 0.70 | 116 | **0.096** | 0.016 to 0.126 | 0.017 |

**Unlike BBBD, where the increment halved under the strictest eye QC, the John gaze increment is stable across all three policies.** It does not shrink when the data are cleaner. This was the gaze block's main untested robustness question in G01-R.

## 7. Amendment A2: beyond explicit attention/data-loss measures (results-informed, estimates only)

Q-ext was replaced, in both models, by its decomposition into three shares of the window:

- short blinks (≤ 500 ms);
- long loss (> 500 ms: track loss or looking away);
- off-display gaze.

| Comparison | Ŝ |
|---|---|
| Gaze block beyond decomposed quality (M5p_QD vs M2p_QD) | **0.109** (0.053 to 0.164 over repetitions) |
| Decomposed vs single quality (M2p_QD vs M2p) | −0.057 |

**Reading.**

- The gaze information is **not** absorbed by explicit blink, data-loss and off-screen measures.
- The decomposition itself predicts worse than the single invalid fraction: its two extra columns cost more than they add.
- The larger 0.109 therefore partly reflects a weaker baseline. Absolute held-out RMSE is 2.19 items for M5p_QD and 2.17 for M5p.

## 8. The working model on this cohort

The best registered model is **M5p**: age, sex, condition, pretest, invalid-sample fraction, gaze dispersion, saccade rate and gaze ISC, fitted by ridge.

| Measure | Value |
|---|---|
| Held-out RMSE | **2.17 items** of 13 |
| Cohort mean predictor | 2.60 items |
| Pretest-only model (M1p) | 2.32 items |
| Out-of-sample MSE reduction over the mean | 30.5% |
| Calibration slope | 1.04 |
| Penalty at the lower grid end | in no split |

Prior knowledge does most of the work. Gaze adds a detectable, independently replicated increment on top of it.

## 9. Numerical diagnostics

| Check | Result |
|---|---|
| Null calibration of the primary test on these features (outcome-free) | False detection 0.045 (pure) and 0.050 (nuisance), MC SE 0.015. Under the nuisance null the gaze block's mean Ŝ is −0.031, so adding it to an informative baseline costs about 3% by itself |
| Penalty at the lowest grid value | 0% of splits for every model in the primary and A1 sets (BBBD E1 had about 5%) |
| Median log10 penalty | M2p 1.0, M5p 1.5 (moderate shrinkage) |
| Clipping | Predictions clipped to [0, 1] by the frozen rule; full calibration slopes 1.02–1.04 |

## 10. What this does and does not establish

**Does establish (confirmatory external evidence for the plan's question):**

- the BBBD gaze block adds held-out individual information about immediate posttest performance in an independent cohort;
- it does so beyond age, sex, condition, pretest and eye-data loss;
- the point estimate is above δ.

**Also supported (estimates only):**

- robustness to eye-QC policy (A1);
- not absorbed by explicit blink, loss or off-screen measures (A2);
- larger, not smaller, after adjusting for the pretest.

**Does not establish:**

- **A precise size.** The 90% interval is −0.05 to 0.21.
- **That synchrony is the active component.** In John the increment sits mainly in reference-free gaze features (descriptive).
- **The direction or mechanism of any single feature.** No explanatory model was registered for John.
- **Generalization across content.** There is one video.
- **Any EEG, ECG or tri-modal claim.**
- **Learning gain.** The posttest is immediate, with a short, low-scoring pretest (7 items, mean 1.9), so prior knowledge is adjusted for only imperfectly.

## 11. Relation to the G01-R conclusions

| G01-R statement ([final report](../preregistered_completion/final_report.md)) | John 2025 | Updated reading |
|---|---|---|
| H2d: gaze block small but detectable in BBBD regime A | Detected externally (p 0.002 with pretest; 0.006 without) | **Replicated** in an independent cohort |
| "Cannot separate higher-scoring learners from prior knowledge" (limitation 1) | The increment survives, and grows, with the pretest in the baseline | **Addressed for gaze in John**; BBBD itself remains unresolved |
| "Robustness to eye-quality policy untested" (§6) | Stable at 0.30 / 0.50 / 0.70 | **Robust in John** |
| "Gaze ISC carries the ocular association, not dispersion or saccade rate" | Reference-free gaze carries most of the increment | **Not replicated**; composition is cohort-dependent |
| H1 (EEG + ECG + gaze) bounded negative | Not testable (ocular only) | Unchanged |
