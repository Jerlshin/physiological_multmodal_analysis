# Audited data contract for problem formulation

Established 2026-10-03. **F = repository/audit fact; I = our inference; H = untested hypothesis; U = unresolved.** External papers are classified L in the literature register. This contract inherits the current audit; it does not rerun or reopen bounded forensic investigations.

## Authoritative sources and precedence

Use [gate closure](../dataset_exploration/gate_closure.md), [current feasibility](../dataset_exploration/research_feasibility.md), [behavioral eligibility](../dataset_exploration/evidence/gate_closure_behavioral_eligibility.parquet), [current counts](../dataset_exploration/evidence/gate_closure_feasibility_counts.csv), [independence](../dataset_exploration/leakage_and_independence.md), [outcomes](../dataset_exploration/outcome_characterization.md) and [remaining gates](../dataset_exploration/open_questions_remaining.md). Earlier landscape/paper counts are historical when these records supersede them. The new user instruction authorizes conditional problem formulation; it does not resolve OQ-06 or authorize unsupported scientific claims.

## Units and eligible observations

**F.** All five v1.1 archives are verified; the existing audit covers 16,038 continuous files and 180,221 channel records with no parser failures. There are 178 experiment-qualified participant records, 11 canonical videos and 1,457 observed exposures. These are inventory quantities, not independent training examples. Cross-experiment unique-human identity is not independently certified.

| Experiment / exposure linked to quiz | Eligible memory outcomes before signal QC: people / observations / videos | EEG+ECG+eye after existing provisional QC: people / observations / videos | Role |
|---|---:|---:|---|
| 1, first attentive viewing | 27 / 135 / 5 | Unavailable: eye only | Ocular extension, distinct scoring/protocol |
| 2 | Excluded | Excluded from behavioral analysis | Signals/condition characterization only within provenance bounds |
| 3, first attentive viewing | 29 / 173 / 6 | 24 / 124 / 6 | Main within-protocol discovery setting |
| 4, tested single-exposure videos in session 2 | 43 / 129 / 3 | 33 / 92 / 3 | Second bounded protocol; different content/block history |
| 5, tested repeated/previewed/incentivized viewing in session 2 | 48 / 144 / 3 | 37 / 108 / 3 | Separate protocol stress test |
| 3–5 combined | 120 / 446 / 8 | 94 / 324 / 8 | Heterogeneous pooled ceiling, not a uniform experiment |

**F.** All non-Exp.2 eligible memory outcomes total 147 qualified people / 581 outcomes. EEG-only direct-QC ceiling in 3–5 is 119 / 429 / 8; ECG+eye is 94 / 327 / 8. Eye in these counts requires both gaze and pupil. Separate gaze-only/pupil-only policies need an explicit new eligibility ledger. Do not imply removing EEG recovers many excluded learners: the existing paired ceilings differ by only three observations and zero qualified people.

**I, arithmetic from F.** Experiments 3+4 provide 57 qualified people / 216 tri-modal observations / 8 videos under current QC, before further provenance restrictions. Their outcome denominator is 72 / 302. Experiments 4+5 provide 70 / 200 / 3 for matched tri-modal protocol comparisons. These sums do not establish unique-human independence, common outcome calibration, or power. Excluding Experiment 5 from the primary first-exposure analysis is therefore a substantial reduction from the headline 94/324.

**F.** Experiment 3 has six videos, 4/5 share three tested videos, and one tested identity links Experiment 3 to that set. The resulting protocol–content graph is sparse. Three shared videos permit a bounded 4↔5 comparison, not general domain transport. Unseen-content evaluation in Experiment 3 has only six content units.

## Outcome meaning and chronology

- **F.** Exp.2 response-position provenance is insufficiently certified; historical aggregate disagreement is established. Keep all its memory/domain targets excluded. No guessed permutation, historical row substitution, or interpretation of its released low scores as poor learning.
- **F.** The Exp.3 sub-01/stim03 duplicate-item outcome stays quarantined; surplus phenotype IDs stay excluded by keys. Exp.5 sub-09 remains absent.
- **F.** Partial credit in 3–5 rewards selected correct options without penalizing extra incorrect selections. The audit found 98 item rows with full partial credit despite extra wrong selections. Exact-set correctness measures something different. Use both as explicitly different operational outcomes, with one prespecified primary. Fractional totals are not ordinary binomial successes.
- **F.** A final quiz in Exp.5 cannot label both viewings as two independent learning observations. First-view signals predicting that final quiz describe an outcome after intervening exposure/preview/incentive; they do not measure first-view learning.
- **F.** There is no validated common pretest of prior knowledge across eligible 3–5. Selected post-view feedback is not automatically a permissible forecasting covariate. GPA is selective/nonuniform; ASRS is a questionnaire trait, not diagnosis; weighted digit-span semantics are unresolved.
- **I.** The defensible criterion is immediate video-specific quiz performance. It is not durable learning gain, a universal ability scale, engagement truth or an educational intervention's benefit. A post-view/pre-quiz forecast is plausible; real-time forecasting is a separate, unsupported specification.

## Measurement boundaries

**F.** OQ-06 remains open for executed EEG/eye preprocessing options, fit scope, native lineage and calibration. Numerical evidence narrows ECG filtering to causal fifth-order 0.5–25 Hz designed at 2048 Hz in all 1,140 testable pairs, but does not certify physical voltage units or manual peak history. Released raw streams are already aligned/resampled exports. Reprocessing these cannot reconstruct native information or guarantee removal of prior globally fitted transformations.

**F.** Large and sometimes minutes-long eye corrections are real. Off-screen gaze can represent behavior; tracker failure and looking away must not be equated. Existing quality masks are measurement evidence, not latent attention labels. Pupil export cannot simply be described as the normalized/head-regressed variant. Localized 16 Hz contamination remains a flag, not a reason for blanket cohort deletion. Respiratory belt amplitude is uncalibrated.

**F.** Existing exploratory person-level gaze/pupil correction correlations in Experiments 3/4/5 are approximately .933/.639/.805. Marginal between-person fractions for median HR are .940/.951/.957, and for pupil correction .882/.840/.921. These are inherited descriptive summaries across observed exposures, not adjusted variance components, outcome associations, or proof of biological coupling. They motivate grouping and quality controls; they do not establish informative outcome missingness.

**F/I.** Released boundaries support whole-video aggregates more strongly than fine timing. There is no certified native clock-residual distribution or item-content timeline. Do not base a primary question on phase coupling, directed influence, momentary comprehension or item-aligned saliency.

## Independence and information access

Group every viewing and window of each qualified participant. Group canonical videos, not local task IDs. Train transformations, imputation, selection rules, teachers, CorrCA/PCA and any learned reference strictly within permitted training data. Unknown upstream fit scope is an additional gate that a later split cannot repair.

Distinguish: (a) new people, previously observed content with training-cohort references; (b) new people and new content with no target reference cohort; (c) new content with a separately declared unlabeled calibration/reference cohort. Ordinary same-video ISC is not available in (b). A model cannot use held-out peers to construct its reference and call that zero-calibration prediction. Reference cohort selection by the test person's unknown attention/score is impermissible for forecasting.

**F/I.** The full release has already informed exploratory QC, outcome and feasibility decisions. Future internal holdouts can protect model evaluation but cannot retroactively make hypothesis discovery fully untouched. Strong confirmation requires a locked protocol and preferably independent collection. This phase changes no scientific eligibility, QC thresholds, archived bytes or models.
