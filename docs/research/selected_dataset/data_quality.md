# Dataset quality and risk assessment

This is a documentation/code assessment, not signal inspection. **No subject or file has yet been QC-approved by this review.** Sources resolve in the [registry](evidence/source_registry.md); stable judgments are tracked in the [inference register](../inference_register.md).

| Risk | Evidence category and observed basis | Scientific consequence / next check |
|---|---|---|
| Fixed attend→distract order in 1–3 | VERIFIED FACT: S01/P01 protocol | OUR INFERENCE (INF-028): order, repetition, fatigue and arithmetic can explain discrimination. Name the compound task; no post-hoc split can remove this design confound. |
| Incentive/preview/repetition bundle in 5 | VERIFIED FACT: S01 Exp. 5 | OUR INFERENCE: reward cannot be isolated from question preview, intention or re-exposure. Check allocation with 4 before intervention-effect claims. |
| Exp. 4 block/content dependence | VERIFIED FACT: first3 and latter3 videos differ | OUR INFERENCE: a session classifier can be a video-identity classifier. Preserve local-to-canonical stimulus IDs. |
| Small stimulus sample / unequal reuse | VERIFIED FACT:11 unique videos, shared across cohorts | OUR INFERENCE (INF-029): content/style/difficulty and low-level audiovisual dynamics can dominate apparent generalization. Hold out canonical videos, not just task numbers. |
| Participant/cohort imbalance | VERIFIED FACT:27–48 released people per experiment; distinct trait/age distributions | OPEN: class and quality-approved sample counts. Report people, videos and valid seconds separately; large groups must not determine all aggregate metrics. |
| Missing modalities differ by design | VERIFIED FACT:EEG/ECG absent from 1; respiration confined4–5 | OUR INFERENCE (INF-030): availability can identify experiment/protocol. Natural dropout is not equivalent to uniform random channel masking. |
| Missing files within expected design | VERIFIED FACT: P03 lost gaze for2/43 quiz cases; historical ECG exclusions | OPEN: current per-person/session/video missingness, co-failure and reasons; compute manifest before complete-case analysis. |
| Large eye interpolation | AUTHOR-REPORTED LIMITATION: S01 gaze22%±19%, pupil32%±25% corrected | OUR INFERENCE (INF-031): smooth interpolated segments may distort dynamics/coupling and hide failure. Quantify fraction and longest gap per file/condition; retain masks. |
| Electrical16 Hz in 4–5 | AUTHOR-REPORTED LIMITATION: S01/S05 | OUR INFERENCE: beta-band, harmonic and coupling effects may be instrumental. Map affected channels/subjects/sessions; do not automatically delete an entire band or claim neural oscillation. |
| EOG numbering inconsistent | AUTHOR-REPORTED LIMITATION: S01 | OUR INFERENCE: numbered EOG channels are not anatomically comparable; test montage and regression adequacy. |
| Residual EEG eye/cardio/movement artifacts | OUR INFERENCE: recording physics plus processed regression/RPCA; not a quantified residual finding | Assess raw/cleaned coherence/topography and sensitivity to ocular regressors. Correlation does not establish neural coupling. |
| Filter/provenance differences | VERIFIED FACT:0.05/0.3/0.5 Hz specifications; hardware/ECG discrepancies | OPEN: identify actual derivative options by release; sensitivity analysis may be necessary, but do not silently “correct” historical processing. |
| Zero fill and BDF padding | VERIFIED FACT:S06 code branches | OPEN: actual affected intervals. Exclude padding from durations; distinguish zeros, NaNs and true baseline values. |
| Unverified lag accuracy | VERIFIED FACT:linear clock mapping described, no residual-error distribution found | OUR INFERENCE: equal128 Hz grids do not warrant directionality/phase claims. Reconstruct triggers and latency uncertainty. |
| Quiz mapping/version changes | VERIFIED FACT:S04 correction after all four empirical papers | OPEN: original-paper input labels vs corrected archive. Reproduce joins before evaluating scientific results. |
| Surplus phenotype IDs | VERIFIED FACT:repository reference audit in 1–3 | OPEN: legitimate excluded participants or mapping error? Check exact files, don't discard unmatched rows without ledger. |
| HRV statistic mismatch | VERIFIED FACT:S06 notebook operates directly on peak times | OUR INFERENCE: labeled RMSSD may instead be RMS interval; published numerical impact OPEN (INF-019). |
| Pupil mean/IQR mismatch | VERIFIED FACT:code computes IQR; caption agrees, prose ambiguous | Do not equate a variability change with dilation (INF-020). |
| Outcome heterogeneity | VERIFIED FACT:partial credit, intentional/incidental timing, preview/re-exposure, differing questions | OUR INFERENCE: pooled raw scores need item/denominator/timing awareness. Learning gain needs an appropriate baseline, not just a post-test. |
| GPA/ASRS measurement limits | AUTHOR-REPORTED LIMITATION:P04 missing/self-reported GPA, immediate outcome and brief videos | OUR INFERENCE: selection, imputation and scale offsets may affect association; no clinical diagnosis or causal mediation from cross-sectional traits alone. |
| Quality exclusions can select behavior | OUR INFERENCE: movement/blinks and task/trait may covary | Compare missingness/quality by outcome and condition; avoid conditioning exclusively on the cleanest, most engaged people. |

## Class imbalance is currently an open empirical question

The planned two-block design does not establish equal class counts after file loss, video trimming, artifact removal or participant selection. Experiments 4–5 have no distract class. Quiz correctness and score distribution depend on item difficulty and scoring; ASRS cutoffs would create arbitrary clinical-looking classes without diagnostic reference. Do not publish a class-balance number before archive inspection. [S01; S06; INF-032]

## Leakage channels to check before any development

These are **OUR INFERENCES**, not accusations that every prior paper made these mistakes. [INF-021–023, INF-033]

1. **Person overlap:** windows or videos from the same person in train and test; repeated-view sessions reveal identity and exposure history. Use experiment-qualified participant IDs and inspect cross-experiment duplicates.
2. **Content overlap:** identical videos under different local names or in different experiments cross a supposed content boundary. Exact video identity, trimming and common segments need a manifest.
3. **Temporal overlap:** adjacent/overlapping windows and filter/interpolation context cross a split. Split independent units before windowing; quantify noncausal context for any proposed online setting.
4. **Reference leakage:** ISC templates, median viewers, CorrCA/PCA, scaling, feature selection or imputation fitted using held-out people, outcomes or condition labels. Declare fixed reference, train-only reference, or transductive estimand explicitly.
5. **Outcome leakage:** join keys accidentally pair wrong quiz rows; question preview or post-test physiology is used to predict a supposedly pre-exposure outcome; aggregate target is duplicated across many windows and evaluated as if independent labels.
6. **Quality/site/version shortcuts:** interpolation masks, missing channels,16 Hz noise or exporter differences identify experiment and thereby target distribution. Include nuisance-only diagnostics in later design.
7. **Pretraining contamination:** public mirrors may enter foundation-model pretraining. Inspect training manifests and dates before claiming unseen-dataset evaluation; this review has not established that contamination occurred.

## Minimum data-audit deliverables for the next stage

A checksummed1.1 archive inventory; person/session/video/modality availability tensor; valid-sample and mask summary; channel/unit/reference dictionary; trigger residual and duration/padding audit; phenotype join/scoring audit; historical-paper cohort map; and a record of all exclusions with reasons. These are prerequisites to choosing a defensible estimand, not permission to start model fitting.
