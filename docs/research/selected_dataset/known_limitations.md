# Known limitations and boundaries of evidence

Use [quality assessment](data_quality.md) for actionable checks. This file separates what is documented from what we infer.

## VERIFIED FACT

- Conditions in experiments 1–3 occur in fixed order, with arithmetic and repeated exposure in the second block. Experiment 4 uses different content in its two attentive blocks; experiment 5 bundles incentive, preview and repeated viewing. [S01/P01; INF-006–007,028]
- Only11 distinct video identities underlie all experiments. Historical papers substantially reuse the same people; four publications are not four independent replications of the complete dataset. [S02/P01–P04; INF-003,029]
- Release continuous signals are128 Hz despite faster acquisition. Authors' resampling/alignment and exported BDF padding limit what can be recovered from a raw directory. [S01/S06; INF-015]
- Static code, descriptor and earlier paper preprocessing specifications differ; exact executed configurations are not fully established. [S06/P04; INF-011–014]
- Sept. 2026 quiz corrections postdate all four empirical papers; original analysis-label provenance is unresolved. [S04; INF-016]
- Existing results already cover eye/heart/brain synchrony, multimodal PCA, linear brain–body prediction, time/frequency effects and EEG/trait–quiz relationships. [P01–P04; INF-022,024]

## AUTHOR-REPORTED LIMITATION

- Electrical16 Hz contamination in some recordings from experiments 4–5 and inconsistent EOG electrode-location mapping. [S01 Methods]
- Eye tracking requires substantial artifact interpolation; reported correction fractions are high and variable. [S01 preprocessing]
- Observational eye synchrony–score associations do not determine their causal origin. [P01 Discussion/Results]
- Immediate retention, brief sessions and short videos do not establish durable knowledge transfer or longer-form educational performance. [P04 Limitations]
- GPA is self-reported, missing for many participants and restricted by college attendance. [P04 Limitations/Methods]
- P03's synchrony/coupling observations do not uniquely identify psychological mechanisms or causal direction. [P03 Discussion]

## OUR INFERENCE

- BBBD is stronger for carefully qualified association and independent-outcome evaluation than for pure attention-state labeling, causal intervention attribution, clinical inference or large-model pretraining from scratch. [INF-001,010,017,026,028]
- A low-cost physiology claim needs direct incremental comparison: ECG has already been analyzed, and multimodal PCA already exists. A new modality combination alone does not establish a scientific advance. [INF-025]
- Total hours cannot compensate for few independent people/videos. Subject- or video-level uncertainty is more relevant than treating thousands of correlated windows as independent samples. [INF-029,033]
- Artifact interpolation, missingness and preprocessing can create or erase modality coupling. Demonstrating robustness to these factors would be a scientific contribution only if measured against meaningful outcomes and failure mechanisms. [INF-027,030–031]
- Broad literature novelty remains provisional because P05 and separate supplements are inaccessible and citation indexing is incomplete. [INF-026,034]

## OPEN QUESTION

Exact native-file availability; per-participant montage/reference; valid complete-case cohort; missingness mechanisms; residual alignment precision; corrected scoring; relation between published and release IDs; question-type tags; trial-level digit-span availability; actual engagement ratings; sex-field totals; cross-experiment repeat participants; intervention randomization and chronology; whether the public notebook reproduces published statistics. These are tracked individually in [open questions](open_questions.md).

The limits do not disqualify the whole dataset. They constrain the questions it can answer and determine the audit work needed before research-problem formulation.
