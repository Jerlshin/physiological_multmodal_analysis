# M06 — Evaluation, leakage and inference contract

2026-10-04. This contract freezes how every number in the baseline study is produced. Feature formulas are in [protocol.md](protocol.md) §6. The inference choice is justified by the [precision simulation](precision_and_independence.md).

## 1. Independence units

- **People.** The independent unit is the experiment-qualified person. Every exposure, window and quiz item of a person stays in one fold.
  - **E4 ↔ E5 are disjoint by construction (F).** The export code partitions one upstream experiment by `doIntervention` into the two released experiments ([acquisition](../selected_dataset/acquisition_protocol.md)).
  - **E3 ↔ E4/E5 (L/U).** The original authors count them as separate cohorts (P03 recruits 32 + 96; P04 analyses 152 people additively). No identity certificate exists. A shared human would make some regime-A test people "seen" in training through their other cohort. This bias is optimistic, and its size is bounded by the overlap. Experiment-stratified results are always reported.
- **Content.** Canonical video, never local task ID. "Related" (`mnYSMhR3jCI`) appears in E3 and E4 and is always held out jointly in B and C.
- **Not independent units:** item rows, windows, folds and repetitions.

## 2. Access regimes (frozen operational definitions)

| Regime | Training data for a test cell (p, v) | Content effect | Features available | Reported as |
|---|---|---|---|---|
| **A — new learner, known content** | All cells of people outside p's outer fold. Content v is present through other people | Training mean of the same experiment × video | Reference-free (RF) + synchrony (SYN). SYN reference = training people of the same experiment × video; training people use leave-self-out references | **Confirmatory** (H1, H2) |
| **B — new learner, new content, no reference** | Cells of people outside p's fold **and** canonical video ≠ v | None for v. Prediction offset = training mean of p's experiment | RF only. No statistic from any recording of v other than p's own | Descriptive, per video. Pooled interval explicitly conditional on the 8 videos |
| **C — new content with an unlabeled reference cohort** | As B | As B | RF + SYN against a reference cohort: the **other half** of v's viewers in the same experiment, from a person-stratified 2-way split, cross-fitted. No labels of v are used; p is never in its own reference | Descriptive, paired with B on identical cells |

**Implication (I).** For a linear predictor, a video-level shift in the features does not change the within-video ranking of learners. B therefore differs from C essentially through the synchrony features. That reference-dependence question is tested with full precision **inside A** (H2a: SYN beyond RF). B and C add the content-transfer dimension.

## 3. Resampling design

- **A.** Outer person-grouped 10-fold CV, stratified by experiment, repeated **R = 50** for the point estimate. The interval method is fixed in §6.
- **B and C.** Leave-one-canonical-video-out crossed with person-grouped 5-fold, stratified by experiment, repeated R = 20.
- **Inner loop**, inside every training set: ridge penalty chosen from λ ∈ {10⁻³ … 10³} × n_train (13 log-spaced values), by person-grouped 5-fold CV minimizing MSE.
- **Seeds.** Fold seeds are recorded. The same outer folds are used for every model compared on the same set (paired comparisons).

## 4. Leakage controls (all mandatory)

1. All of the following are fit **inside the training portion of each split**: standardization, imputation (training mean plus missing indicator), penalty selection, content effects, CorrCA spatial filters, SYN reference means, and any data-driven feature threshold. Nothing is fit on the full release.
2. In A, CorrCA filters are fit on training people's processed EEG, pooled over their training cells. In B/C they are fit on training videos only. Filters are never fit on a test person or a held-out video.
3. SYN for a training person uses a leave-self-out reference. SYN for a test person uses the training reference (A) or the other reference half (C). The test person's outcome, attention status or quality never selects a reference.
4. A test person's other cells are never used: no person-level normalization or calibration from the person's own data. This keeps E3's per-video chronology.
5. No outcome-derived quantity enters features or Q. Item difficulty, video difficulty and reliability come only from training labels where used, and only as content effects.
6. The E5 first-view signal is never paired with the E5 quiz in the primary E5 analysis.
7. Upstream preprocessing is per recording and label-free (bounded in [M01](measurement_provenance.md)). No step of this study fits across the full release.
8. Pupil-block and raw-route analyses rerun the **entire** pipeline. Precomputed full-release features are never reused.
9. QC thresholds, sets, features, penalties grid and seeds are frozen in the [protocol](protocol.md). Any change is a logged deviation, rerun for every model.

## 5. Model families (no search beyond this list)

| ID | Inputs (always on identical cells and folds) | Role |
|---|---|---|
| M0 | Content effect (A) / experiment mean (B, C) | Reference floor |
| M1 | M0 + admissible covariates C | Nonsignal information |
| **M2** | M1 + quality Q | **Primary baseline** |
| M3 | M2 + RF | Reference-free physiology |
| M4 | M2 + SYN (A, C) | Synchrony only |
| **M5** | M2 + RF + SYN (A); M2 + RF (B); M2 + RF + SYN_C (C) | **Primary full model** |
| M-EEG / M-ECG / M-gaze | M2 + that modality's RF + SYN | H2(b–d) |
| M5+pupil | M5 + pupil RF + SYN on PAS-four | Secondary block |

**Learner:** ridge regression on standardized inputs with the content offset; predictions clipped to [0, 1]. No other learner enters any confirmatory or secondary comparison in the baseline study.

**Explanatory companion (labelled explanatory):** a crossed REML mixed model with person and content random intercepts and the M5 inputs as fixed effects. It is fit once on the full PAS-core and is never presented as predictive evidence.

**Shortcut diagnostics (descriptive):**

- (i) quality-only model M0 + Q;
- (ii) an experiment- and video-identity probe: held-out accuracy of predicting the video from X;
- (iii) matched random features: an M2 + Gaussian-noise block of the same dimension.

The confirmatory null reference is the person-block permutation in §6.

## 6. Metrics and inference

**Primary metric.** Person-balanced skill = 1 − mean_p MSE_p(M5) / mean_p MSE_p(M2), on the exact score.

**Reported alongside:**

- cell-weighted skill;
- ΔRMSE and ΔMAE in quiz items (× 12);
- skill ÷ reliable-variance share (per experiment);
- per-video and per-experiment skill;
- out-of-fold calibration slope and intercept;
- the state skill: double-centred by person and content, among people with at least two cells.

**Inference: three roles, each assigned to the procedure that calibrated best in the [design simulation](precision_and_independence.md):**

1. **Detection (H1 and H2): person-block Freedman–Lane permutation test.**
   - Residualize the tested feature block on content dummies, C, Q and any blocks already in the comparison model, by full-data OLS. This uses no outcomes.
   - Permute whole-learner residual blocks among learners of the same experiment with an identical tested-video pattern; learners with a unique pattern stay fixed.
   - Add back the fitted part.
   - Recompute the CV statistic: the person-balanced loss difference over R = 10 outer repetitions whose folds are **paired** across observed and permuted data.
   - Use 999 permutations. p = (1 + #{null ≥ observed}) / 1000, one-sided.
   - Simulated performance: false detection 0.063 under the null (Monte Carlo-compatible with 0.05); power 0.93 at 2δ.
   - **H2** applies the same scheme to the added block (SYN for H2a; one modality's block for H2b–d), with Holm adjustment over the four p-values.
2. **Estimation (reported 90% interval): nested CV** (Bates, Hastie & Tibshirani 2024, Alg. 1 with the eq. 15 bias correction and MSE clipping), with 200 nested repetitions on the person-balanced loss difference, divided by the CV baseline MSE.
   - Simulated coverage of the dataset-conditional target: 0.86–0.90.
   - It is labelled as such and is **not** the H1 decision rule.
3. **Futility (ruling out an effect): corrected resampled-t upper bound with z = 3.0, compared with 2δ = 0.10.**
   - Calibrated to about 5% error at the boundary; rules out 0.10 in 91% of null datasets.
   - Ruling out δ = 0.05 itself cannot be done with controlled error at n = 68 and is **not** claimed.

The person bootstrap of out-of-fold losses and the cell-wise permutation are **not** used. In simulation the first undercovers (0.67–0.79) and the second rejects too often under the null (0.080).

**B and C** report:

- per-video skill;
- a pooled within-content skill with a two-way (person × video) bootstrap interval, labelled **"conditional on the 8 sampled videos; approximate; undercovers the content population in simulation"**.

No p-values are reported for B or C.

**Decision table for H1:** [estimand §6](estimand_and_hypotheses.md#6-pre-declared-interpretation-of-h1).

## 7. What is reported regardless of result

- The full case flow and selection report.
- Every prespecified model, set and sensitivity analysis, including failures.
- Per-video results.
- Criterion reliability.
- The exploratory origin of the design: the whole release informed QC and formulation.
- The fact that internal CV is not an untouched confirmation.
