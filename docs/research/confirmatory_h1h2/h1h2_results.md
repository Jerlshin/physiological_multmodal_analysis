# G01-R confirmatory H1/H2 baseline — results and preregistered interpretation

First real-outcome analysis, 2026-10-05. Run `20261005T104908Z_c57b28d6` (tracking experiment `g01r-confirmatory`), produced by the frozen command `python -m g01r run --analysis H1_H2 --workers 5` under the [preregistration](https://osf.io/uh397/overview) and the freeze `g01r-freeze-v1`. Provenance and commands: [README.md](README.md).

Every number below is copied from the run's [`result.json`](evidence/result.json) or tabulated from it by [`summarize_h1h2.py`](evidence/summarize_h1h2.py), which never reads outcomes. **Nothing in the analysis was changed, re-run, re-tuned or supplemented after outcome access.** The interpretation applies the pre-declared rules in [estimand §6](../experimental_design/estimand_and_hypotheses.md#6-pre-declared-interpretation-of-h1), [protocol §11–§12](../experimental_design/protocol.md#11-inference-and-multiplicity) and [preregistration §10–§11](../baseline_implementation/preregistration.md#10-inference-and-decision-rules).

Notation: Ŝ = person-balanced skill = 1 − mean_p MSE_p(full) / mean_p MSE_p(base), from 50 repetitions of person-grouped, experiment-stratified 10-fold CV. Positive means the full model predicts held-out learners better. δ = 0.05; 2δ = 0.10.

## Status labels used in this report

| Label | Meaning | Items |
|---|---|---|
| **Confirmatory** | Preregistered test with a pre-declared decision rule and error control | H1 (one-sided α = 0.05); H2a–d (Holm family of 4) |
| **Prespecified estimate** | Preregistered quantity reported with the confirmatory run, no test | Ŝ, nested-CV interval, U₃, ΔRMSE/ΔMAE, calibration, per-experiment and per-video skill, all other regime-A comparisons |
| **Robustness (H3)** | Prespecified estimate only; IS-028 reading | H3.7 cell-weighted skill (derived from the H1 fits) |
| **Exploratory** | Prespecified, no confirmatory claim | State skill (D_state, derived from the H1 fits) |
| **Diagnostic** | Prespecified shortcut diagnostics, or numerical checks of the run | Shortcut (i) and (iii); λ, clipping, folds, nulls |
| **Not run in this phase** | Later runbook steps | H3.1–H3.6, B/C, CAS, E5, transport, E1, explanatory model, shortcut (ii) identity probe |

---

## 1. Case flow and sample size

All analyses in this run use one frozen set, **PAS-core: 68 people / 259 cells / 8 canonical videos (9 experiment × video units)**. The set identity hash (`8a682fc0…`) and the split identity hash (`f62f7ae3…`) equal those of the pre-outcome dry runs, so the folds are the frozen ones. The outcome loader joined an eligible exact score to all 259 cells (it raises on any missing outcome); no cell was dropped at analysis time.

Case flow (frozen ledger, [case_flow.csv](../baseline_implementation/evidence/population/case_flow.csv)):

| Stage | E3 people / cells / videos | E4 people / cells / videos |
|---|---|---|
| Design tested cells | 29 / 174 / 6 | 43 / 129 / 3 |
| Eligible outcome | 29 / 173 / 6 | 43 / 129 / 3 |
| + EEG QC | 29 / 160 / 6 | 43 / 128 / 3 |
| + ECG QC | 29 / 154 / 6 | 43 / 128 / 3 |
| **+ gaze QC = PAS-core** | **29 / 148 / 6** | **39 / 111 / 3** |

| Analysis in this run | People | Cells | Units of resampling |
|---|---|---|---|
| Point estimates, all 11 models | 68 | 259 | 50 reps × 10 person folds = 500 outer splits |
| H1/H2 permutation tests | 68 | 259 | Reps 1–10 (100 paired splits), B = 999 person-block permutations |
| Nested-CV interval (H1, H3.7, state) | 68 (state: people with ≥ 2 cells) | 259 | 200 nested repetitions |
| Futility bound U₃ | 68 | 259 | J = 500 fold-level person-mean differences |
| Per-experiment | E3 29; E4 39 | 148; 111 | — |
| Per-video | 22–38 per unit | 22–38 per unit | 9 experiment × video units |

## 2. Primary H1 estimate and uncertainty (confirmatory)

M5 (M2 + RF + SYN) versus M2 (content + covariates + quality), regime A, exact score:

| Quantity | Value |
|---|---|
| **Ŝ (person-balanced)** | **0.0206** |
| Person-balanced MSE, M2 → M5 | 0.03168 → 0.03103 (Δ = 0.00065) |
| ΔRMSE / ΔMAE in quiz items | 0.022 / 0.018 items (of 12) |
| **Nested-CV 90% interval** (200 reps) | **[−0.033, 0.072]** (bias-corrected centre 0.020; root/SE = 2.18) |
| **Permutation p** (one-sided, B = 999, reps 1–10) | **0.082** (81 of 999 null statistics ≥ observed) |
| Observed skill on reps 1–10 (test statistic scale) | 0.0166 |
| **Futility bound U₃** (z = 3, J = 500) | **0.0786** |
| Calibration slope / intercept, M2 | 0.942 / 0.027 |
| Calibration slope / intercept, M5 | 0.938 / 0.029 |
| Ŝ ÷ reliable-variance share | E3 0.028; E4 0.045 |
| Person bootstrap of the loss difference (declared fallback; **non-decisional**, not triggered) | 90% [−0.00008, 0.00141]; would not detect |

## 3. Comparison with δ = 0.05

- The point estimate Ŝ = 0.021 is **below δ** (about 40% of δ).
- The 90% interval [−0.033, 0.072] **contains both 0 and δ**. The data cannot rule δ in or out, as the design anticipated ("δ itself cannot be ruled out with controlled error at n = 68").
- On the estimand's own calibration ([estimand §2](../experimental_design/estimand_and_hypotheses.md#minimum-useful-effect-rule-2-applied)), observing one additional quiz item reduces held-out MSE by 0.021 on average, and δ is worth more than two items. Ŝ = 0.021 is therefore roughly the information of one extra quiz item. In raw units the RMSE gain is 0.022 items on the 12-item scale.

## 4. Interpretation relative to 2δ = 0.10 and the futility rule

- U₃ = 0.0786 < 0.10, so the corrected-t bound **rules out procedure skills ≥ 0.10** (pre-declared error ≈ 5%, validated at 0.050).
- Applying the pre-declared table: p = 0.082 > 0.05 and U₃ < 0.10 → **"Moderate or large increments (≥ 0.10) are ruled out at this sample size and for this procedure. Increments in 0.05–0.10 remain possible. This is a bounded negative result, not 'physiology carries no information'."** The code's category is `bounded_negative`.
- The range 0.05–0.10 is unresolved by design and stays unresolved.

## 5. H2a–H2d with Holm adjustment (confirmatory family)

Same person-block Freedman–Lane test, B = 999, paired reps 1–10; Holm over the four p-values; reject when adjusted p ≤ 0.05. H2 was tested as a separate family regardless of H1, as preregistered.

| Test | Added block | Base → full | Ŝ (R = 50) | p | Holm p | Decision |
|---|---|---|---|---|---|---|
| **H2a** | SYN (EEG, ECG, gaze synchrony), beyond RF | M3 → M5 | 0.047 | 0.005 | **0.020** | **Reject H0** |
| H2b | EEG (RF1, RF2, SYN1) | M2 → M-EEG | −0.004 | 0.228 | 0.456 | Not rejected |
| H2c | ECG (RF3, RF4, SYN2) | M2 → M-ECG | −0.011 | 0.811 | 0.811 | Not rejected |
| **H2d** | Gaze (RF5, RF6, SYN3) | M2 → M-gaze | 0.031 | 0.009 | **0.027** | **Reject H0** |

Holm steps: 4 × 0.005 = 0.020; 3 × 0.009 = 0.027; 2 × 0.228 = 0.456; 1 × 0.811 = 0.811 (monotone).

Both rejected increments have point estimates **below δ** (0.047 and 0.031). The preregistration attaches no interval or futility bound to H2, so their size is read only through Ŝ: detected, practically small by the δ criterion.

## 6. Baseline-versus-physiology comparisons (prespecified estimates)

All on identical cells and folds (R = 50). Only H1 carries an interval, and only H1/H2 carry tests.

| Comparison | What is added | Ŝ person-balanced | Ŝ cell-weighted | ΔRMSE (items) | E3 | E4 |
|---|---|---|---|---|---|---|
| M1 vs M0 | Covariates C | 0.036 | 0.045 | 0.040 | 0.071 | 0.009 |
| M2 vs M1 | Quality Q | 0.052 | 0.056 | 0.057 | 0.058 | 0.047 |
| **M5 vs M2 (H1)** | RF + SYN | **0.021** | 0.013 | 0.022 | 0.013 | 0.026 |
| M3 vs M2 | RF only | −0.028 | −0.032 | −0.029 | −0.049 | −0.013 |
| M4 vs M2 | SYN only | 0.039 | 0.033 | 0.042 | 0.050 | 0.031 |
| M5 vs M3 (H2a) | SYN beyond RF | 0.047 | 0.043 | 0.051 | 0.060 | 0.038 |
| M-EEG vs M2 (H2b) | EEG RF + SYN | −0.004 | −0.004 | −0.005 | −0.011 | 0.000 |
| M-ECG vs M2 (H2c) | ECG RF + SYN | −0.011 | −0.013 | −0.011 | −0.019 | −0.005 |
| M-gaze vs M2 (H2d) | Gaze RF + SYN | 0.031 | 0.023 | 0.033 | 0.032 | 0.030 |
| M2+noise vs M2 (shortcut iii) | 9 Gaussian noise columns | −0.021 | −0.025 | −0.022 | −0.033 | −0.013 |
| M0+Q vs M0 (shortcut i) | Quality only | 0.069 | 0.083 | 0.079 | 0.111 | 0.038 |

Reading, limited to what these estimates support:

- **Matched-noise control next to H1** (pre-declared, BII-007): adding nine pure-noise columns costs 0.021 of skill; M5's +0.021 is therefore about 0.04 above what the pipeline does with uninformative columns. The reference-free block alone (M3, −0.028) performs **like or slightly worse than the noise control**.
- **Why H2a is detected while H1 is not.** H2a compares M5 with M3, and M3 is itself below M2 (−0.028). The synchrony increment of 0.047 is measured from that lowered base. It is a valid confirmatory finding that synchrony adds information beyond the reference-free features. It is not evidence that the full model beats the baseline, which H1 did not detect. The SYN-only model M4 (+0.039 versus M2) has no test and no interval.
- **Quality is informative.** Quality variables alone (M0+Q) and on top of covariates (M2 vs M1, 0.052) predict the quiz score. This is exactly why Q is in the primary baseline. Every physiological claim here is net of Q.

## 7. Modality-specific and multimodal results (prespecified)

| Model | Modalities | Ŝ vs M2 | Status |
|---|---|---|---|
| M-gaze | Gaze RF + SYN | 0.031 | Confirmatory (H2d rejected) |
| M-EEG | EEG RF + SYN | −0.004 | Confirmatory (H2b not rejected) |
| M-ECG | ECG RF + SYN | −0.011 | Confirmatory (H2c not rejected) |
| M3 | All RF | −0.028 | Estimate |
| M4 | All SYN | 0.039 | Estimate |
| M5 | All RF + SYN (multimodal) | 0.021 | Confirmatory (H1 not detected; bounded negative) |

The only modality block with detected incremental information is gaze; EEG and ECG blocks show none (negative point estimates; no bound applies to H2). The multimodal model is not detectably better than the baseline and is estimated below the gaze-only model. Under the pre-outcome constraint BII-005 (EEG ISC correlates with gaze dispersion, ρ = 0.48), any EEG synchrony contribution would in any case be read as "EEG-recorded synchrony", not non-ocular neural information. The pupil block (H3.3) and the E1 ocular-only model are not part of this run.

## 8. Content heterogeneity and participant-balanced summaries

**Per experiment** (person-balanced; people / cells): see the E3/E4 columns in §6. H1: E3 0.013 (29 / 148), E4 0.026 (39 / 111); as a share of reliable within-video variance, 0.028 and 0.045.

**Per experiment × video** (cell-weighted skill within each unit; one cell per person per unit; descriptive, no inference with 8 videos):

| Unit | Cells | M5 vs M2 (H1) | M5 vs M3 (H2a) | M-gaze vs M2 (H2d) | M-EEG vs M2 | M-ECG vs M2 | M3 vs M2 | M4 vs M2 | Noise vs M2 |
|---|---|---|---|---|---|---|---|---|---|
| E3 `30o4omX5qfo` | 27 | −0.023 | 0.027 | −0.030 | 0.004 | −0.024 | −0.051 | 0.008 | −0.042 |
| E3 `bYgV9nvgJ3E` (α = 0.18) | 25 | 0.004 | 0.005 | 0.028 | −0.017 | −0.018 | −0.001 | −0.013 | −0.041 |
| E3 `e0NT9i4Qnak` | 26 | −0.025 | 0.044 | 0.008 | −0.021 | −0.018 | −0.071 | 0.036 | −0.052 |
| E3 `lkRZKqDdwzU` | 24 | 0.009 | 0.071 | 0.016 | −0.007 | −0.026 | −0.067 | 0.052 | −0.037 |
| E3 `mnYSMhR3jCI` | 24 | 0.018 | 0.065 | 0.029 | 0.015 | −0.023 | −0.050 | 0.064 | −0.040 |
| E3 `rkntp3_cZl4` | 22 | −0.001 | 0.028 | 0.034 | −0.038 | 0.004 | −0.030 | 0.018 | 0.007 |
| E4 `VVAKFJ8VVp4` | 38 | 0.026 | 0.056 | 0.034 | −0.001 | −0.024 | −0.031 | 0.038 | −0.022 |
| E4 `mnYSMhR3jCI` | 37 | 0.060 | 0.055 | 0.049 | 0.018 | 0.013 | 0.005 | 0.070 | −0.019 |
| E4 `zQGOcOUBi6s` | 36 | −0.016 | −0.001 | 0.001 | −0.018 | 0.001 | −0.014 | −0.021 | 0.007 |

- H1 (M5 vs M2) is positive in 5 of 9 units and ranges from −0.025 to 0.060; no unit reaches 2δ.
- The two detected H2 increments are broadly spread rather than driven by one video: H2a is positive in 8 of 9 units; H2d in 8 of 9.
- The low-reliability video `bYgV9nvgJ3E` contributes little in either direction (H1 0.004). Its exclusion is H3.5, not run here.
- Per-video values rest on 22–38 learners each and are conditional on these 8 videos.

**Participant balance.** The primary metric weights every learner equally regardless of their number of cells (E3 learners have up to 6 cells, E4 learners 3). The cell-weighted counterpart is H3.7 below.

**H3.7 cell-weighted skill (robustness; derived from the H1 fits):** 0.013, nested-CV 90% [−0.046, 0.068]. Same sign as the primary Ŝ (positive) and the same side of δ (below). Under the IS-028 reading this agreement is **robust**. H3.7 adds no test and does not revise the H1 conclusion.

**State skill (exploratory; derived from the H1 fits):** point −0.010, nested-CV 90% [−0.056, 0.035], among learners with ≥ 2 cells. There is no indication that the full model captures video-specific (within-learner) variation. This is consistent with the pre-outcome expectation that the reliable criterion variance is about three-quarters stable-learner level.

## 9. Quality and reference-access diagnostics

| Diagnostic | Result | Reading |
|---|---|---|
| Shortcut (i): M0+Q vs M0 | Ŝ = 0.069 (E3 0.111, E4 0.038) | Recording quality and availability variables predict quiz scores on their own. Q is in every baseline, so H1/H2 are net of this |
| Shortcut (iii): M2+noise vs M2 | Ŝ = −0.021 | The pipeline does not reward uninformative columns; reported next to H1 as pre-declared |
| Shortcut (ii): identity probe | **Not run** (runbook step 4) | Pending |
| Reference access, regime A | SYN references from training learners only, leave-self-out within training; recomputed per split (IS-007/IS-008) | H2a shows the regime-A increment depends on these peer references. Whether it survives held-out content (B) or a cross-fitted half-cohort reference (C) is untested here (runbook step 4, D_BC) |
| Extreme quality cell (BII-007) | All predictions clipped at 0 for M2 (16 of 12,950) and M5 (14) belong to the 3 cells of one E4 learner. That learner has the three most extreme EEG 16 Hz excess values in PAS-core (7.1–8.1 dB; set median −0.12 dB). [Table](evidence/tables/clipped_at_zero_by_cell.txt) | Anticipated before outcome access. It affects base and full models alike. Reported, not altered: no cell was removed and no model refitted |

## 10. Model and numerical failures

**None.** The run finished with status `FINISHED` and exit code 0. MLflow logged no errors. Checks ([run_diagnostics_models.csv](evidence/tables/run_diagnostics_models.csv), [run_digest.json](evidence/tables/run_digest.json)):

- No non-finite predictions in any of the 11 models × 50 reps × 259 cells.
- Every learner was tested exactly once per repetition (10 folds in each of 50 reps).
- Ridge penalties: the median selected penalty is 10⁰ × n_train for every penalized model except M3 (10^0.5). The grid's ends were selected in at most 0.4% of splits (M0+Q at the lower end) and 0.2% (M1 at the upper end); none for M2–M5 or the H2 models.
- All five permutation nulls are complete (999 finite values each).
- The declared fallback detection procedure was not triggered (`detection_procedure = permutation`, fixed by `validation_verdict.json`).

**Operational note (not a failure).** Wall time was 6.7 h (24,098 s), against the runbook's estimate of 3–4 h. The nested-CV interval needed 12,900 new synchrony plans (cache 7,903 → 20,803 entries), at about 30–50 plans per minute. The analysis itself was not altered. All frozen cache entries still verify (append-only rule).

## 11. Confirmatory conclusions

**H1 (primary).** Not rejected: p = 0.082 > 0.05. Pre-declared category: **bounded negative.**

- At n = 68 learners and 8 videos, the frozen pipeline's incremental held-out skill from whole-video EEG + ECG + gaze over content, covariates and quality is estimated at 0.021 (90% interval −0.033 to 0.072).
- Increments of 0.10 or more are ruled out (U₃ = 0.079).
- Increments between 0.05 and 0.10 are not ruled out.
- This is **not** evidence that physiology carries no information.

**H2 family (Holm, family-wise α = 0.05).**

- **H2a rejected** (Holm p = 0.020): synchrony features add held-out information beyond the reference-free features (Ŝ = 0.047, below δ).
- **H2d rejected** (Holm p = 0.027): the gaze block adds information beyond the nonsignal baseline (Ŝ = 0.031, below δ).
- **H2b (EEG) and H2c (ECG) not rejected** (Holm p = 0.456, 0.811).

**Joint reading, within the pre-declared rules.**

- The detected information is small (below δ wherever it is detected), ocular (gaze) and reference-dependent (synchrony, in regime A with training-learner references).
- The pre-declared phrase "a positive A driven by SYN is reference-dependent validity" presupposes a positive H1, which did not occur. This report therefore does not describe G01-R as showing reference-dependent *validity*; it reports the H2a finding as such.
- No H2 finding upgrades or revises the H1 conclusion.

## 12. Confirmatory, descriptive, sensitivity and exploratory findings, separated

| Class | Findings in this run |
|---|---|
| **Confirmatory** | H1 not detected, bounded negative (≥ 0.10 ruled out). H2a and H2d rejected; H2b and H2c not rejected |
| **Prespecified estimates (no test)** | Ŝ and its interval; U₃; ΔRMSE/ΔMAE; calibration; skill ÷ reliable share; all other regime-A comparisons (M1, M2, M3, M4, M5 vs M3, single-modality); per-experiment and per-video skills |
| **Sensitivity / robustness (H3)** | H3.7 cell-weighted only: 0.013 [−0.046, 0.068], robust in sign and side of δ. H3.1–H3.6 not yet run |
| **Exploratory** | State skill −0.010 [−0.056, 0.035] |
| **Diagnostic** | Shortcut (i) 0.069; shortcut (iii) −0.021; clipping traced to the pre-identified extreme-quality learner; no numerical failure |
| **Not computed (would be post hoc if added)** | Intervals or tests for M4, M-gaze or any per-feature decomposition; re-analysis without the extreme-quality learner; any alternative learner or feature set. None was run |

## Limitations carried into interpretation

- **Exploratory-origin disclosure.** The whole release was audited before the design; internal cross-validation is not an untouched confirmation.
- **Criterion.** About half of within-video variance is item-sampling error. Most reliable variance is stable-learner level, so even detected increments mainly identify higher-scoring learners.
- **Content.** 8 videos; no content-population inference. Regimes B/C are not yet run.
- **Measurement provenance.** OQ-06 is bounded, not resolved. These are results for the released processed measurements (raw route = H3.4, not yet run).
- **Cohort identity.** E3 versus E4 participant identity is uncertified. A shared person would bias regime A optimistically; the estimates here are small regardless.
- **Conditional estimand.** Complete cases are conditional on usable recordings. Quality itself predicts scores (shortcut i).

## Recommendation for the next phase (not started)

Based only on what this frozen run showed:

1. **Complete the preregistered plan before anything else.** Preregistration §13/§15 commits to running and reporting every registered analysis whatever the H1 result. The next frozen steps are:
   - run-book step 2: H3.1 partial credit and H3.6 GPA;
   - step 3: H3.2–H3.5;
   - step 4: D_BC, D_CAS, D_E5, D_transport, D_E1, X_explanatory, S_identity_probe;
   - step 5: the collated report.

   Three of these bear directly on today's findings:
   - **D_BC** (regimes B/C) asks whether the gaze and synchrony information survives held-out content, with and without peer references. That is the open question behind H2a.
   - **S_identity_probe** (shortcut ii) checks whether the physiological features mainly encode the experiment × video unit.
   - **H3.4** (raw route) and **H3.2** (eye-QC thresholds) test whether the gaze-related increments depend on the processed derivatives and the eye-quality policy.
2. **Budget compute realistically.** Step 1 took 6.7 h against an estimate of 3–4 h. Step 3 (five cold nested CVs, estimated at 20–30 h) should be planned at roughly 1.5–2× that.
3. **Keep the H2 findings at their confirmed scope.** They support "small, sub-δ, gaze and synchrony increments in regime A". They do not support a useful multimodal measure. Any gaze-only or synchrony-only model, feature decomposition or re-analysis without the extreme-quality learner would be post hoc and must be labelled exploratory if ever run.
4. **Defer new modelling.** Novel architectures, representation learning or foundation-model work would be a new, separately justified and separately preregistered question. This baseline gives no confirmatory basis for expecting a useful (≥ δ) multimodal increment in this dataset: effects ≥ 0.10 are ruled out for this procedure, and the detected increments are below δ. Such work would need an external dataset with a more reliable criterion (cf. the external-validation plan) rather than further mining of BBBD.
