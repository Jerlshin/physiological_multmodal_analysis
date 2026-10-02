# Prior-work comparison and coverage

Read with [paper dossiers](prior_work.md) and [source registry](evidence/source_registry.md). All result values are from original papers, not our reproduction. `E` means BBBD experiment; historic N may differ from release 1.1. Unknown is not “no.”

## Paper × participants × modalities × task × representation × model × validation × result

| Paper | BBBD participants | Modalities analyzed | Task/target | Representation | Model/analysis | Validation actually reported | Main result |
|---|---|---|---|---|---|---|---|
| P01 PNAS 2021 | E1–3: 27/31/30 historical cohorts; metric-specific exclusions | Gaze X/Y,pupil; webcam extension outside BBBD | Condition; immediate quiz | Eye ISC, weighted ISC extension | ROC, ANOVA, correlations; constrained weighted combination | Lab cohort/style replication; webcam LOSO weighting outside BBBD; no joint person/content quiz holdout established | Lab AUC.944±.033; per-video quiz r.61±.06 |
| P02 Cell2021 | E2 ECG N27 of 31 | ECG→HR | Attention manipulation, HR synchrony | HR ISC, frequency bands | ANOVA, paired tests, shuffle null | Within-person contrasts; no BBBD held-out quiz prediction | F(1,104)=70.64;26/27 decline in ISC |
| P03 Nexus 2022 | E4+5 N92 historic; E3 N29; E2 N29; quiz43, eye-complete41 | EEG,HR,gaze,pupil,respiration,saccade rate,head | Cross-modal synchrony; brain→body prediction; quiz association | CorrCA, ISC/WSC, multimodal PCA,10s dynamics | OLS, PCA, correlation, permutation | **LOSO EEG→body**; **two-video train/one-video test EEG significance**; quiz relation cohort-level | PC1 52%variance; quiz r.59; modality-specific quiz associations |
| P04 iScience2025 | E2–5 N152 historic; phenotype-specific subsets | EEG + EOG cleaning + GPA/WMC/ASRS | Quiz performance and state/trait relationships | Five EEG CorrCA ISC components; trait scores | GLMM, mediation assumptions | Cross-cohort spatial-filter application; no held-out quiz error; experiment random intercept | ISC1 quiz t4.11,p7.67e−5; GPA/WMC significant |
| S01 SciData2026 | Release178; measure-specific pairs | All reported signal classes | Resource validation | PSD, alpha, rates, pupil IQR/statistic ambiguity | Paired t-tests by experiment | Technical checks, not predictive validation | Alpha distraction d.7; quality/correction summaries; code-statistic issues |
| P05 IEEE 2026 lead | **Unknown** | EEG in title; actual use unknown | Attentive/distracted in title | Unknown | Unknown | Unknown | Unknown; original full text needed |

P01's shorthand counts are the article's cohort descriptors; per-result sample sizes differ. Do not add Ns across papers: they reuse participants. [Cohort mapping](participants.md)

## Explicit answers to the proposed gap questions

| Question | Evidence-backed answer | Classification / next requirement |
|---|---|---|
| Which modality combinations were never tested? | P03 already combines EEG/HR/gaze/pupil/respiration-derived ISC in PCA and compares brain–body mappings; P04 adds EEG+traits. No exhaustive evaluation of every subset was found. | OPEN: no justified “never” claim. A controlled incremental-value/ablation study may remain (INF-025). |
| Has ECG been underused? | P02 centers on ECG; P03 includes HR synchrony/coupling and quiz association; S01 cardiac validation. | VERIFIED: ECG is not unused. Relative underuse of waveform/morphology or outcome-generalization remains an inference, not an established fact. |
| Has fusion been properly investigated? | Multimodal common-factor analysis exists; held-out fusion benefit over unimodal plus behavioral/stimulus controls was not established in inspected papers. | OUR INFERENCE: specify a validation target rather than dismissing existing fusion. |
| Subject-independent generalization? | P03 uses LOSO EEG→body; P01 webcam extension uses LOSO weights in separate cohorts. | VERIFIED for those tasks. Joint independent behavioral forecasting remains OPEN. |
| Video-independent generalization? | P03 holds out a video for EEG component significance. | VERIFIED for statistical validation; not the same as unseen-video quiz generalization. |
| Cross-experiment generalization? | P03 replicates relationships; P04 transfers spatial filters across cohorts. | VERIFIED partial evidence. Strict held-out experiment predictive calibration with overlap audit not found. |
| Self-supervised/foundation models? | None verified in P01–P04 or S06; P05 methods inaccessible; additional indexing gaps possible. | OPEN bounded negative finding (INF-026). Foundation-model pretraining may already include mirrored BBBD EEG; check manifests. |
| Multimodal contrastive learning? | No confirmed use in reviewed dataset papers. | OPEN novelty candidate, not proof of absence or sufficient scientific problem. |
| Missing-modality robustness? | Papers report/drop missing cases, but no deliberate natural+synthetic missingness evaluation verified. | OUR INFERENCE / OPEN design opportunity (INF-027). |
| Cross-modal distillation? | P03's linear cross-modal prediction is precedent; teacher–student outcome transfer not verified. | OPEN narrower gap; distinguish prediction from distillation. |
| Physiology→learning outcomes? | P01 eye–quiz, P03 multimodal–quiz, P04 EEG+traits–quiz already exist. | VERIFIED occupied; prospective generalization/incremental value is narrower. |
| Temporal dynamics? | P03 10s overlapping ISC and frequency-specific WSC; P02 HR frequency analyses. Related auditory studies model dynamics. | VERIFIED occupied; no generic “first temporal” claim. |
| Leakage or inappropriate validation? | Descriptive cohort analyses do not estimate strict inductive prediction. Group references, shared stimuli and preprocessing require split-aware construction for a future benchmark. | OUR INFERENCE: identify the estimand; do not label all earlier associations “leaky” (INF-021–023). |

## What a genuinely new claim would need to distinguish

A proposed direction should specify the held-out unit (person, video, experiment), outcome provenance, reference cohort availability, preprocessing fit scope, actual modality combination and incremental comparator. Holding out windows answers none of the person/content questions by itself. A new architecture without a scientifically meaningful target or credible independent evaluation is not yet a research gap.

[Coverage diagram](figures/prior_work_coverage.svg) is a visual index of **confirmed coverage**, not model quality or an exhaustive census.
