# Preregistration — G01-R baseline study (secondary data analysis)

> **Status: final text, not deposited.** Prepared 2026-10-05 for deposit by the user, for example as an OSF "Preregistration in secondary data analysis". Depositing is an external action that requires the user's authorization; nothing has been submitted. The text is frozen together with the analysis: only the fields in the deposit-time table below are completed at deposit.

## Deposit-time fields

These values cannot be written into the repository before the freeze is committed. Complete them in the deposit form or the deposited copy, and change nothing else.

| Field | Value |
|---|---|
| Authors and affiliations | `<to be completed by the user>` |
| Freeze commit (git) | `<output of git rev-parse HEAD after the freeze commit>` |
| Deposit date | `<date of deposit>` |

## 0. Frozen references

| Element | Identifier |
|---|---|
| Statistical analysis plan | [protocol.md](../experimental_design/protocol.md) v1.0, frozen at git commit `ef1df1b3014ccc85f5ac956bd192b6b0d39c3e34` and unchanged since, with its companion documents [estimand_and_hypotheses.md](../experimental_design/estimand_and_hypotheses.md) and [evaluation_contract.md](../experimental_design/evaluation_contract.md). The only later change to these documents is the dated H3 clarification in estimand §5 (2026-10-05, before any outcome access). The versions in the freeze commit are authoritative |
| Operational clarifications | [implementation_spec.md](implementation_spec.md) v1.1 (IS-001…IS-029), all written before any outcome access |
| Configuration (every numeric constant) | `configs/g01r_protocol_v1.toml`, SHA-256 `f34f1b03b65723dc30c07f4eb0f848150cd2672877e310ab2290244627d63fff` |
| Freeze manifest | `analysis_freeze/freeze_manifest.json`, SHA-256 `a2594996ac122348ffacff8a0a100f7dc035aa6848c7df23b0ca939e310f2149`. It binds the documents above, every production source file, the analysis registry, the population ledger, the outcome-blind feature tables, the signal and synchrony caches, the validation evidence, the data archives, the dependency lock and the base seed |
| Freeze tag | Annotated git tag `g01r-freeze-v1` on the freeze commit; the commit hash is a deposit-time field |
| Analysis plan as code | `src/g01r/registry.py`: 17 registered analyses (15 executed, 2 derived from H1_H2) |
| Software | Python 3.14.5; numpy 2.5.3, scipy 1.18.1, pandas 3.0.6, pyarrow 25.0.1; exact environment in `requirements-baseline.lock` |

Where this document summarizes, the protocol and the implementation specification are authoritative. If they ever appear to disagree, the protocol governs and the discrepancy is reported as a deviation (§17).

## 1. Study information

**Working title.** Do whole-video EEG, ECG and gaze add individual information about immediate quiz performance on educational videos? A crossed, incremental and decomposed validity study in BBBD v1.1.

**Research question (G01-R).** For new adult learners viewing previously characterized short educational videos, do whole-video EEG, ECG and gaze measurements add individual information about immediate video-specific quiz performance beyond permissible nonsignal information and measurement quality? How much of any such information:

- depends on peer-reference synchrony;
- survives held-out content without peer references;
- is video-specific rather than stable-learner information?

All of this is assessed against a low-reliability criterion (median within-video internal consistency 0.45; 47–58% of within-video variance is reliable in E3/E4).

**Estimand.** For access regime g, analysis set S and sensor feature set F:

  Skill_g(F) = 1 − E_p[MSE_p(𝒜_{C,Q,F})] / E_p[MSE_p(𝒜_{C,Q})]

where p is a new learner, MSE_p is that learner's mean squared error over their tested videos (person-balanced), predictions are clipped to [0, 1], and 𝒜 is the frozen pipeline trained at this sample size. It is the expected held-out incremental skill of the procedure, not the oracle information content of physiology and not a causal quantity.

**Minimum useful effect.** δ = 0.05 (relative MSE reduction). Negative conclusions are limited to ruling out 2δ = 0.10, because δ itself cannot be ruled out with controlled error at n = 68.

### Hypotheses

| ID | Status | Statement (regime A, PAS-core, exact score unless stated) | Comparison |
|---|---|---|---|
| **H1** | Primary, confirmatory | Skill_A(RF + SYN) > 0: the full model adds information beyond the nonsignal baseline. H0: Skill_A ≤ 0. One-sided α = 0.05 | M5 vs M2 |
| **H2a** | Secondary, confirmatory (Holm family of 4) | Synchrony adds information beyond the reference-free features | M5 vs M3 |
| **H2b** | as H2a | The EEG block (RF1, RF2, SYN1) adds information | M-EEG vs M2 |
| **H2c** | as H2a | The ECG block (RF3, RF4, SYN2) adds information | M-ECG vs M2 |
| **H2d** | as H2a | The gaze block (RF5, RF6, SYN3) adds information | M-gaze vs M2 |
| **H3** | Robustness, estimation only | H1's estimate under the seven prespecified sensitivity analyses (§11) | M5 vs M2 (and M5+pupil vs M2) |

H1 and H2 are separate families. H2 is tested and reported whatever the H1 result; its family-wise error is controlled by Holm's procedure over the four tests. The descriptive and exploratory aims are listed in §12; none carries a confirmatory claim.

## 2. Data description

- **Dataset.** Brain, Body, and Behavior Dataset (BBBD) v1.1, Zenodo record 22968459. Public; the five archives used were downloaded once, MD5-verified against the record and are read in place (SHA-256 bound in the freeze manifest).
- **Design.** Adults watched short educational videos while EEG (64 channels, processed release), ECG R-peaks, gaze and pupil were recorded; each tested video has a multiple-choice quiz (timing below).
- **Cohorts and chronology** (source-verified in [estimand §1](../experimental_design/estimand_and_hypotheses.md#1-chronology-now-source-verified)):

  | Cohort | Instruction | Quiz timing | Forecast point for cell (person, video) |
  |---|---|---|---|
  | E3 | Intentional | After each video | End of that viewing |
  | E4 | Incidental (not told about tests) | After the block of three tested videos | End of that viewing |
  | E5 | Previewed, incentivized repeat viewing | After the repeat block | End of the repeat viewing |
  | E1 | Intentional | After each video | End of that viewing |

- **Excluded data.** E2 behaviour (not behaviourally eligible in the audit). The person's other exposures never enter a cell's features, normalization or calibration.
- **Measurement provenance.** Features use the authors' released processed derivatives; whether any upstream step pooled across recordings or used labels (OQ-06) is bounded but unresolved ([M01](../experimental_design/measurement_provenance.md)). A prespecified raw-export route is the sensitivity analysis.

## 3. Prior knowledge of the data (disclosure)

- **What the investigators accessed before this preregistration.** The investigators audited the whole release:
  - file integrity and signal quality;
  - outcome distributions and psychometrics (reliability, variance components);
  - case flow and the selection of complete cases on outcomes.

  The design (QC thresholds, analysis sets, choice of outcome, δ, inference procedures) was therefore informed by exploratory access. Internal cross-validation protects model evaluation; it does not make this an untouched confirmation.
- **What was not done.** No association between any physiological measure and any quiz outcome has been computed by anyone in this project. The physiological feature tables were generated and quality-checked without outcomes. Every model fit so far used simulated or synthetic outcomes drawn from outcome-only psychometric parameters (simulated features in V1; the real features in V2 and the end-to-end dry runs).
- **Enforcement.** Real outcomes are readable through one code path only. It refuses access unless an authorization record, written by the user after this deposit, references the freeze manifest and the manifest still verifies against the code, configuration, documents, feature tables, caches and data. Every access is logged.

## 4. Units and sample

People and canonical videos are the independent units, not cells, windows or items. A cell is one experiment-qualified person × one canonical video at its tested exposure.

| Set | People / cells / videos | By experiment | Role |
|---|---|---|---|
| **PAS-core** | **68 / 259 / 8** | E3 29 / 148 / 6; E4 39 / 111 / 3 | H1, H2, regimes B and C, state skill, H3.1/H3.4/H3.6/H3.7 |
| PAS-four (+ pupil QC) | 57 / 216 / 8 | E3 24 / 124; E4 33 / 92 | H3.3, pupil block |
| PAS-core, eye-correction threshold 0.30 / 0.70 | 65 / 223 / 8; 69 / 265 / 8 | — | H3.2 |
| PAS-core without `bYgV9nvgJ3E` (exact α < 0.30) | 68 / 234 / 7 | E3 29 / 123 / 5; E4 39 / 111 / 3 | H3.5 |
| CAS (all eligible E3+E4) | 72 / 302 / 8 | E3 29 / 173; E4 43 / 129 | Coverage-set policy; selection report |
| E5-core | 46 / 128 / 3 | — | E5 regime A; transport target/source |
| E4-core (E4 part of PAS-core) | 39 / 111 / 3 | — | Transport source/target |
| E1-gaze | 26 / 121 / 5 | — | Ocular-only regime A |

- **Sample size.** Fixed by the existing data; no data will be added. Membership is frozen and reproduced cell for cell from the design-phase manifest ([analysis_set_manifest.csv](../experimental_design/evidence/analysis_set_manifest.csv)).
- **Justification.** Simulation of this exact incidence on the production code: power 0.973 to detect a procedure skill of 2δ = 0.10, false detection 0.060 (§14).
- **Stopping rule.** There are no interim analyses and no stopping for efficacy or futility. "Futility" in this document means the U₃ bound used to state a bounded negative result (§10).

## 5. Eligibility, quality control and exclusions

All rules were fixed before this deposit and are applied by frozen code ([M03](../experimental_design/analysis_population.md)).

1. **Tested cell.** E3 session 1 attend viewing; E4 session 2 tested block; E5 session 2 repeat viewing; E1 session 1.
2. **Outcome eligibility.** The audit's behavioural eligibility for the memory quiz. One E3 cell (sub-01, stimulus 3, duplicate item) is quarantined.
3. **Basic QC per modality file** (audit configuration, unchanged): file present; non-finite samples ≤ 1%; exact-zero samples ≤ 95%; not grossly flat (EEG: ≤ 8 flat channels; other modalities: not all channels flat); gaze and pupil: correction fraction ≤ 0.50.
4. **Set definitions.** PAS-core requires EEG, ECG and gaze QC; PAS-four adds pupil QC; E1-gaze requires gaze QC. The H3.2 sets change only the eye-correction threshold.
5. **Not excluded.** No video is excluded in the primary analysis (low reliability is handled by H3.5); no QC threshold is re-tuned; no outlier removal on outcomes or features; no cross-experiment identity merge.
6. **Feature-level QC** (outcome-blind, done): no PAS-core learner lost (REVISE trigger at > 15% not fired).

## 6. Variables

- **Outcome.** Primary: the proportion of the video's quiz items answered with exactly the keyed option set (`normalized_exact_score`, scale [0, 1], one item = 1/12). Sensitivity (H3.1): partial credit. No transformation and no item-response modelling.
- **Reference-free physiology (RF)**, per exposure over the whole video ([protocol §6](../experimental_design/protocol.md#6-feature-dictionary-frozen-no-outcome-based-selection); IS-002–IS-006):
  - RF1 posterior relative alpha and RF2 frontal-midline relative theta (Welch, 16 Hz contamination excluded);
  - RF3 heart rate and RF4 ln RMSSD (from released R-peaks);
  - RF5 gaze dispersion and RF6 saccade rate;
  - RF-P pupil variability (PAS-four only).
- **Synchrony (SYN)**, recomputed inside every split from that split's permitted reference people only, with leave-self-out references for training people (IS-007, IS-008):
  - SYN1 EEG CorrCA ISC (3 components; shrinkage γ = 0.5);
  - SYN2 heart-rate ISC; SYN3 gaze ISC; SYN-P pupil ISC (PAS-four only).
- **Quality Q** (in every baseline): gaze and pupil correction fractions; pupil file-absence; EEG zeroed-sample fraction; EEG 16 Hz excess; gaze-missing and EEG-missing indicators.
- **Covariates C:** age; sex (M = 1, F = 0, otherwise a missing indicator); ASRS inattention and hyperactivity item sums; digit span (valid 3–7, otherwise missing plus an indicator). E1: age and sex only. GPA enters only in H3.6.
- **Content identity:** experiment × canonical video.
- **Missing data.** A feature with < 60 s of valid data is missing. Missing values are imputed with the training-split mean, and each physiological block carries a missing indicator (IS-011). No outcome is missing in any analysis set by construction.

## 7. Models

Learner: ridge regression on standardized inputs with a content offset; predictions clipped to [0, 1]. No other learner and no model search.

| Model | Inputs | Role |
|---|---|---|
| M0 | Content effect (A) / experiment mean (B, C) | Reference floor |
| M1 | M0 + C | Nonsignal information |
| **M2** | M1 + Q | **Primary baseline** |
| M3 | M2 + RF | Reference-free physiology |
| M4 | M2 + SYN | Synchrony only |
| **M5** | M2 + RF + SYN (A); M2 + RF (B); M2 + RF + SYN_C (C) | **Primary full model** |
| M-EEG / M-ECG / M-gaze | M2 + that modality's RF + SYN | H2b–d |
| M5+pupil | M5 + RF-P + SYN-P, on PAS-four | Pupil block (H3.3) |
| M5-E1 | M2(E1) + gaze RF + SYN | E1 ocular-only |
| M0+Q | M0 + Q | Shortcut diagnostic (i) |
| M2+noise | M2 + 9 Gaussian noise columns (fixed seed) | Shortcut diagnostic (iii): matched random features |

## 8. Pipeline and resampling

**Inside every training split** ([protocol §8](../experimental_design/protocol.md#8-pipeline-order-inside-every-training-split)):

1. Content effects from training labels: the experiment × video mean (A); the experiment mean (B/C).
2. Residual target on training cells.
3. CorrCA filters and synchrony references from training people (A) or the reference half (C) only.
4. Features for training people with leave-self-out references, and for test people.
5. Training-mean imputation with indicators; standardization.
6. Ridge penalty from person-grouped inner 5-fold CV over 13 values (10⁻³…10³ × n_train).
7. Refit on the full training split.
8. Prediction = content offset + ridge output, clipped to [0, 1].

**Resampling.**

- **Regime A:** person-grouped, experiment-stratified 10-fold CV, R = 50 repetitions; all models on identical folds.
- **Regimes B/C:** leave-one-canonical-video-out × person-grouped 5-fold × 20 repetitions. "Are We All Related" (in E3 and E4) is always held out jointly. Regime C uses a person-level random half split per repetition; the test reference is the other half's viewers of the held-out video.
- **Seeds:** base seed 20261004; every stream is addressed by labels (IS-009), so comparisons on a set share folds, inner folds and permutations.

## 9. Metrics

- **Primary:** person-balanced skill Ŝ = 1 − mean_p MSE_p(full) / mean_p MSE_p(base), from the R = 50 out-of-fold predictions.
- **Also reported:** cell-weighted skill; ΔRMSE and ΔMAE in quiz items; skill ÷ reliable-variance share (per experiment); per-experiment and per-video skill; calibration slope and intercept; state skill; for B/C, the within-content skill (primary for B/C) and absolute skill.

## 10. Inference and decision rules

- **H1 detection.** Person-block Freedman–Lane permutation test (IS-014, IS-026):
  - the tested block (RF + SYN) is residualized by full-data OLS on experiment × video dummies, C and Q, using no outcomes;
  - whole-learner residual blocks are exchanged among learners of the same experiment with an identical tested-video pattern;
  - statistic: the person-balanced loss difference M2 − M5 over repetitions 1–10 of the 50, with folds paired between observed and permuted data;
  - B = 999 permutations; p = (1 + #{null ≥ observed}) / (B + 1), one-sided.
- **H2.** The same test for each added block (H2a: SYN, with RF also residualized out; H2b–d: one modality's RF + SYN). Holm adjustment over the four p-values; reject when the adjusted p ≤ 0.05.
- **Reported interval.** Nested CV (Bates, Hastie & Tibshirani 2024, Alg. 1 with the eq. 15 bias correction and MSE clipping), 200 repetitions, 90%, divided by the baseline MSE. It is an estimate of uncertainty, not the decision rule.
- **Futility bound U₃.** Corrected resampled-t upper bound with z = 3.0 over the 500 fold-level person-mean differences, divided by the person-balanced baseline MSE (IS-025).
- **H1 decision table** (pre-declared; [estimand §6](../experimental_design/estimand_and_hypotheses.md#6-pre-declared-interpretation-of-h1)):

  | Result | Conclusion |
  |---|---|
  | p ≤ 0.05 and Ŝ ≥ 0.05 | Incremental individual information detected, with a point estimate of practically useful size |
  | p ≤ 0.05 and Ŝ < 0.05 | Information detected, but practically small |
  | p > 0.05 and U₃ < 0.10 | Increments ≥ 0.10 ruled out at this sample size and for this procedure; 0.05–0.10 remains possible |
  | Otherwise | Inconclusive; never reported as absence |

  A positive A result with a negative B result is reported as content-library-specific validity; an A result driven by synchrony (H2a) as reference-dependent validity.
- **Declared fallback** (decided before outcome access): if the production false detection had exceeded 0.07 in V1 or V2, detection would use the stratified person bootstrap (detect if the lower 90% bound of the person-level loss difference exceeds 0). **Status: not triggered.** The detection procedure is the permutation test, fixed in `validation_verdict.json`, which the confirmatory code reads.
- **Regimes B/C.** Two-way (person × video) bootstrap, B = 2000, 90% percentile interval, labelled "conditional on the 8 sampled videos; approximate". No p-values.
- **Not used.** The person bootstrap as an interval (undercovers) and the cell-wise permutation (anti-conservative), per simulation.

## 11. Robustness analyses (H3; estimate and interval only)

Each reruns the full pipeline and reports Ŝ (M5 vs M2) and its nested-CV 90% interval, with no new tests:

1. Partial-credit outcome.
2. Eye-correction QC thresholds 0.30 and 0.70.
3. PAS-four, without (M5) and with (M5+pupil) the pupil block.
4. The prespecified raw-export feature route (EEG, gaze and pupil from raw exports; ECG timing and Q unchanged; IS-021).
5. Excluding content with exact α < 0.30 (`bYgV9nvgJ3E`).
6. GPA (valid GPA plus a missing indicator) added to C.
7. Cell-weighted instead of person-balanced skill (from the H1 fits).

**Reading (IS-028; final interpretation).** H3 is a prespecified robustness/sensitivity analysis.

- For each analysis we state whether Ŝ keeps the sign of the primary Ŝ and whether it stays on the same side of δ = 0.05.
- Agreement on both is described as robust; any disagreement is described as sensitivity to that analysis.
- H3 introduces no additional confirmatory test and does not revise the H1 conclusion. No p-value or futility bound is computed for H3, so the H1 decision category is not re-evaluated.

## 12. Descriptive and exploratory analyses (no confirmatory claims)

| Analysis | Content |
|---|---|
| Regime B | New learner and new video, reference-free (M5 = M2 + RF): per-video skill and a pooled within-content interval conditional on the 8 videos |
| Regime C | New video with a cross-fitted unlabelled half-cohort reference (M5 with SYN_C), paired with B on identical cells; B − C per video |
| State skill (exploratory) | Nested-CV interval of the double-centred (person and content) loss difference, among people with ≥ 2 cells |
| Coverage-set policy | On CAS: M5 where PAS-core features exist, M2 otherwise; risk against M2 on all 302 cells, with the selection report |
| E5 regime A | M5 vs M2 on E5-core, at the repeat viewing |
| E4 ↔ E5 transport | Train on one cohort, test on the other, on the 3 shared videos; synchrony references and content offsets from the source cohort; a target-mean-recalibrated variant is labelled as using target labels; stratified person-bootstrap interval |
| E1 regime A | Ocular-only M5-E1 vs M2 |
| Explanatory model | Crossed REML mixed model (person and content random intercepts; M5 inputs as fixed effects), fit once on PAS-core; labelled explanatory and never presented as predictive evidence |
| Shortcut diagnostics | (i) quality-only M0+Q vs M0; (ii) held-out accuracy of predicting the experiment × video unit from RF + SYN, against the majority rate; (iii) M2+noise vs M2 |

Any analysis not listed in this document or in the registry will be labelled post hoc.

## 13. Reporting commitments (regardless of result)

- Every registered analysis is run to completion and reported, including null, negative and failed results. If an analysis fails computationally, the failure and its reason are reported; a replacement analysis would be a logged deviation.
- The case flow and selection report; criterion reliability; per-video and per-experiment results; every prespecified model and set; the three shortcut diagnostics, with the matched-noise control next to H1.
- The exploratory-origin disclosure (§3) and the statement that internal cross-validation is not an untouched confirmation.
- Every number with its unit of independence (people and content). No participant-level data in publications.

## 14. Validation of the inference before outcome access

Production code, before any outcome access ([validation_report.md](validation_report.md)):

| Check | Result | Target |
|---|---|---|
| V1 false detection (300 simulated null datasets) | 0.060 (MC SE 0.014) | ≤ 0.07 |
| V1 power at 2δ | 0.973 | ≥ 0.80 |
| V1 futility error at 0.10 | 0.050 | ≤ 0.05 |
| V2 false detection, real features, synthetic pure null (200) | 0.030 | ≤ 0.07 |
| V2 false detection, real features, synthetic nuisance null (200) | 0.065 (MC SE 0.017) | ≤ 0.07 |
| V2 planted real-feature signal (skill ≈ 0.10; sanity check) | detected 0.92 | — |

The futility error sits at its target, so a "≥ 0.10 ruled out" conclusion carries about 5% error, as declared.

## 15. Execution order

1. H1 and H2 (one run on PAS-core, which also yields H3.7 and the state interval).
2. H3.1 and H3.6; then H3.2–H3.5.
3. The descriptive, explanatory and diagnostic analyses.
4. The results report.

The order is an execution order only. All steps are completed and reported whatever the H1 result.

## 16. Known limitations stated in advance

- **Measurement provenance.** OQ-06 is bounded, not resolved. Claims concern the released processed measurements; the raw-export route is the sensitivity analysis.
- **Criterion.** The criterion is noisy, and its reliable part is mostly a stable learner level. An increment mainly means physiology identifies higher-performing learners; prior knowledge was not measured.
- **Content inference.** With 8 videos there is no content-population inference.
- **Cohort identity.** E3 versus E4/E5 participant identity is uncertified; a shared person would bias regime A optimistically.
- **Conditional estimand.** Complete cases are conditional on obtaining usable measurements; complete cases scored higher (selection report).
- **Pre-outcome observations** (inference register BII-005–BII-007):
  - EEG ISC correlates with gaze dispersion (ρ = 0.48), so H2b is read as "EEG-recorded synchrony", not non-ocular neural information.
  - The raw-route posterior alpha agrees only moderately with the processed one (ρ = 0.60).
  - The baseline can under-regularize an extreme quality value and inflate point estimates; the matched-noise control is reported next to H1, and detection requires p ≤ 0.05.

## 17. Deviations

- Any change to a frozen element after this deposit is a deviation. It is logged in the [decision log](../research_gap/decision_log.md) with the date, the reason and whether it was made before or after seeing physiology–outcome results. Every affected model is rerun, and both versions are reported.
- Technically, any change to a bound file makes the outcome loader refuse access until the freeze is rebuilt and a new authorization written, so no deviation can go unrecorded.
