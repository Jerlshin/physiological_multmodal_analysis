# Frozen study protocol — G01-R baseline study (statistical analysis plan)

**Version 1.0, frozen 2026-10-04.** This is the single implementable document for the next phase. Rationale and evidence live in the gate documents linked in each section. Changes after freezing must be logged as dated deviations (§16) and rerun across all affected models.

**Disclosure.** The design was developed after exploratory audit of the whole BBBD v1.1 release:

- outcome distributions and psychometrics;
- quality structure;
- case flow.

No physiology–outcome association has been computed by anyone in this project. Internal cross-validation protects model evaluation; it does not make the study an untouched confirmation.

## 1. Question and hypotheses

Full text: [estimand_and_hypotheses.md](estimand_and_hypotheses.md) §5.

- **H1 (primary).** Regime A, PAS-core, exact score: person-balanced incremental skill of M5 over M2 is greater than 0. Person-block permutation test, one-sided α = 0.05.
- **H2 (Holm family of 4).** (a) M5 versus M3, i.e. synchrony beyond reference-free features. (b–d) M-EEG, M-ECG and M-gaze each versus M2.
- **H3.** Robustness estimates (§13).
- **Descriptive aims (§14).** Regimes B and C, state skill, CAS policy, E5, E4↔E5 transport, E1.

The minimum useful effect is **δ = 0.05** (relative MSE reduction). Negative conclusions are limited to ruling out **2δ = 0.10**: δ itself cannot be ruled out with controlled error at n = 68. The decision table is in [estimand §6](estimand_and_hypotheses.md#6-pre-declared-interpretation-of-h1).

## 2. Data

- **Release:** BBBD v1.1 (Zenodo 22968459), the five checksum-verified archives in `data/bbbd/canonical_source/`.
- **Audited tables:** taken from `docs/research/dataset_exploration/evidence/`.
- **E2:** behaviour excluded.
- **Provenance:** bounded per [M01](measurement_provenance.md).

## 3. Analysis sets

Defined by [design_ledger.py](evidence/design_ledger.py); membership is in [analysis_set_manifest.csv](evidence/analysis_set_manifest.csv).

| Set | People / cells / videos | Use |
|---|---|---|
| PAS-core | 68 / 259 / 8 | H1, H2, B, C, state |
| PAS-four | 57 / 216 / 8 | Pupil block; H1 sensitivity |
| PAS-core eye-QC 0.30 / 0.70 | 65 / 223 / 8; 69 / 265 / 8 | H3 quality-policy sensitivity |
| CAS | 72 / 302 / 8 | Coverage policy and selection report |
| E5-core | 46 / 128 / 3 | Repeat-exposure regime A; E4↔E5 transport |
| E1-gaze | 26 / 121 / 5 | Ocular-only regime A |

## 4. Outcome

- **Primary:** `normalized_exact_score` from the gate eligibility table, i.e. the proportion of the video's items answered with exactly the keyed option set.
- **Sensitivity:** `normalized_partial_score`.
- **Scale:** [0, 1]; 1 quiz item = 1/12.
- **Treatment:** no transformation and no item-response modelling in the confirmatory analysis.

## 5. Forecast chronology and information set

- **Forecast point:** the end of the tested viewing of video v, before that video's quiz. For E5, the repeat viewing.
- **Information set:**
  - that exposure's signals only;
  - its Q;
  - covariates C;
  - experiment and canonical-video identity;
  - the training data permitted by the regime ([M02 §1](estimand_and_hypotheses.md#1-chronology-now-source-verified)).
- **Excluded:** no other exposure of the same person enters any feature, normalization or calibration.

## 6. Feature dictionary (frozen; no outcome-based selection)

All features are computed per exposure on the whole video. Released processed derivatives are the primary route; the raw-export route is the sensitivity ([M01](measurement_provenance.md)).

- **Valid gaze/pupil samples:** samples outside the released correction intervals (`*_desc-*` interval files), finite, and within 0 ≤ x < 1920, 0 ≤ y < 1080.
- **Valid EEG samples:** per channel, samples not exactly zero. The author pipeline zeroes artifacts.
- **Missing features:** a feature with fewer than 60 s of valid data is set missing. It is then imputed with the training mean, and a block missing-indicator is added.

### Reference-free features (RF)

| ID | Name | Definition |
|---|---|---|
| RF1 | EEG posterior alpha | Welch PSD per channel (4 s Hann, 50% overlap) over segments without zeroed samples. log10[P(8–12 Hz) / P(1–40 Hz excluding 14.5–17.5 Hz)], median over P3, Pz, P4, PO3, POz, PO4, O1, Oz, O2 |
| RF2 | EEG frontal-midline theta | As RF1 with P(4–8 Hz), median over Afz, Fz, F1, F2, FCz, Cz |
| RF3 | Heart rate | Median of 60/RR over RR in [0.3, 2.0] s, from `desc-rpeak_timestamps` within the video |
| RF4 | ln RMSSD | ln of the RMS of successive RR differences (ms). Pairs are used only when both RR are in [0.3, 2.0] s and \|ΔRR\| < 0.2·RR_prev |
| RF5 | Gaze dispersion | sqrt(var x + var y) of valid processed gaze (pixels) ÷ 2203 (screen diagonal) |
| RF6 | Saccade rate | Count of `desc-saccades` events with onset outside correction intervals ÷ valid gaze minutes |
| RF-P | Pupil variability (PAS-four only) | SD ÷ mean of valid processed pupil |

### Synchrony features (SYN)

Each uses a reference mean over the regime's reference people for the same experiment × video ([M06 §2](evaluation_contract.md#2-access-regimes-frozen-operational-definitions)). A training person's reference always leaves that person out.

| ID | Name | Definition |
|---|---|---|
| SYN1 | EEG ISC | CorrCA fitted on reference/training people's processed EEG (pooled over training cells). Within-subject covariance shrunk toward its mean eigenvalue with γ = 0.5. Sum over components 1–3 of Pearson r between the person's component time course and the reference-mean component time course, on samples valid in both |
| SYN2 | Heart-rate ISC | Instantaneous HR (60/RR at beat times, valid RR only), linearly interpolated to a 2 Hz grid. Pearson r with the reference-mean HR time course |
| SYN3 | Gaze ISC | Mean of Pearson r for horizontal and vertical gaze against the reference-mean gaze time courses, on valid samples (pairwise complete) |
| SYN-P | Pupil ISC (PAS-four only) | Pearson r of the within-recording z-scored pupil against the reference mean |

### Quality (Q, in every baseline)

- Gaze correction fraction.
- Pupil correction fraction, plus a file-absence indicator.
- EEG zeroed-sample fraction: median over 64 channels, processed.
- EEG 16 Hz excess: median dB over channels, as defined in the audit.

### Covariates (C)

- Age.
- Sex (M = 1, F = 0, otherwise a missing indicator).
- ASRS inattention and hyperactivity: item-derived 0–4 sums.
- Digit span: maximum span in [3, 7], otherwise missing plus an indicator.
- E1 uses age and sex only.

## 7. Access regimes

As frozen in [M06 §2](evaluation_contract.md#2-access-regimes-frozen-operational-definitions):

- **A:** new learner, known content. **Confirmatory.**
- **B:** new learner and new canonical video, RF only. **Descriptive.**
- **C:** new video with a cross-fitted unlabelled half-cohort reference. **Descriptive.**

## 8. Pipeline order inside every training split

1. Compute content effects from training labels. In A, the experiment × video mean; in B/C, the experiment mean.
2. Compute the residual target on training cells.
3. Fit CorrCA and form SYN references from training (A) or reference people (C).
4. Compute features for training people with leave-self-out references, and for test people.
5. Impute (training mean plus indicators) and standardize (training mean/SD).
6. Choose the ridge penalty by person-grouped inner 5-fold CV over the 13-value grid.
7. Refit on the full training split.
8. Predict: content offset plus ridge output, clipped to [0, 1].

## 9. Models

M0–M5, M-EEG, M-ECG, M-gaze and M5+pupil, exactly as in [M06 §5](evaluation_contract.md#5-model-families-no-search-beyond-this-list). The learner is ridge only. The explanatory crossed REML model is labelled explanatory.

## 10. Metrics

- **Primary:** person-balanced skill.
- **Also reported:**
  - cell-weighted skill;
  - ΔRMSE and ΔMAE in items;
  - skill ÷ reliable-variance share;
  - per-experiment and per-video skill;
  - calibration slope and intercept;
  - state skill;
  - B/C within-content skill (primary for B/C) and absolute skill.

## 11. Inference and multiplicity

See [M06 §6](evaluation_contract.md#6-metrics-and-inference) and [precision](precision_and_independence.md) for justification.

- **Point estimates:** outer person-grouped 10-fold CV stratified by experiment, R = 50 repetitions.
- **H1 decision:** person-block Freedman–Lane permutation test.
  - The tested block is residualized on content dummies, C, Q and any earlier blocks, using no outcomes.
  - Whole-learner residual blocks are exchanged within experiment × identical video pattern.
  - The statistic is the person-balanced loss difference over R = 10 paired outer repetitions; 999 permutations; one-sided α = 0.05.
- **H2:** the same test on each added block, with Holm adjustment over 4.
- **Reported interval:** nested CV, 90%, 200 repetitions (Bates et al. 2024, with bias correction and clipping), divided by the baseline MSE. Simulated conditional coverage is 0.86–0.90.
- **Futility:** corrected resampled-t upper bound with z = 3.0, compared with 0.10.
- **B/C:** two-way bootstrap, conditional and approximate. No p-values.
- **Not used:** the person bootstrap (undercovers) and the cell-wise permutation (anti-conservative), per simulation.

## 12. Interpretation

Follow the decision table in [estimand §6](estimand_and_hypotheses.md#6-pre-declared-interpretation-of-h1). Inconclusive is never reported as absence. A positive A with negative B is reported as content-library-specific validity. A SYN-driven A is reported as reference-dependent validity.

## 13. Prespecified sensitivity analyses (H3)

Each reruns the full pipeline. Only the H1 point estimate and interval are reported, with no new tests:

1. Partial-credit outcome.
2. Eye-correction QC thresholds 0.30 and 0.70.
3. PAS-four, with and without the pupil block.
4. Raw-export feature route ([M01](measurement_provenance.md)).
5. Exclusion of content with exact α < 0.30 (`bYgV9nvgJ3E`).
6. GPA added to C (valid GPA plus a missing indicator).
7. Cell-weighted instead of person-balanced skill.

## 14. Descriptive analyses

| Analysis | Description |
|---|---|
| Regime B | Per video, plus a pooled conditional interval |
| Regime C | Paired with B on the same cells |
| B−C paired difference | Per video |
| State skill | Interval from the nested-CV procedure applied to the double-centred loss difference |
| CAS policy | M5 where PAS-core features exist, M2 otherwise. Risk is compared with M2 on all 302 cells, alongside the selection report |
| E5 regime A | E5-core |
| E4↔E5 transport | On the 3 shared videos. Models trained on E4-core are tested on E5-core, and the reverse, with within-protocol A as reference. SYN references come from the **source** cohort on the same canonical video. Content offsets are the source cohort's video means. A target-mean-recalibrated variant is reported separately and labelled as using target labels |
| E1 regime A | Gaze RF + SYN; age and sex as C |
| Explanatory model | Crossed REML mixed model |
| Shortcut diagnostics | As in M06 §5 |

## 15. Reporting

Every number comes with its unit of independence: people and content.

- **Case flow:** the case flow and selection table.
- **Reliability:** criterion reliability.
- **Coverage:** all prespecified models and sets, including failures.
- **Per-video:** per-video panels.
- **Disclosure:** the exploratory-origin disclosure.

No participant-level data appear in publications.

## 16. Deviations, time-stamping and preregistration

This file and the evidence scripts are committed to git; the commit hash is the time-stamp. Before any physiology–outcome computation, a preregistration should be deposited, for example on OSF, citing this commit and disclosing the exploratory history. Depositing it is an external action that requires the user's authorization.

Deviations are recorded in [decision_log](../research_gap/decision_log.md) with:

- the date;
- the reason;
- whether the decision was made before or after seeing physiology–outcome results.

## 17. Implementation checklist for the baseline phase

1. **Feature module.** Implement RF/SYN/Q exactly as in §6, in `src/` with unit tests on synthetic signals. Tests must cover the valid-sample rules, the 16 Hz exclusion, leave-self-out references and CorrCA fit scope.
2. **Split module.** Implement person-grouped stratified folds, the B/C crossed holdout and C's half-cohort references. Add tests asserting no person or video overlap and that no test label is read.
3. **Validate the inference code.** Re-run [precision_simulation.py](evidence/precision_simulation.py) and `inference_calibration.py --person` ([script](evidence/inference_calibration.py)) against the production pipeline functions. The simulated operating characteristics must be reproduced within Monte Carlo error before real outcomes are touched. Targets:
   - false detection ≤ 0.07;
   - power ≥ 0.80 at 2δ;
   - futility error ≤ 0.05 at 0.10.

   If the permutation test fails, the declared fallback is the person-bootstrap detection test ([verdict](readiness_verdict.md)).
4. **Generate features without outcomes.** Freeze the feature table, then report feature-level QC and missingness before the outcome join.
5. **Run H1 → H2 → H3 → descriptive analyses.** Produce a results report with every prespecified item.
