# Missingness and selection

**Gate follow-up — 2026-10-02:** Exp.2 score/quality entries below are retained as release-encoding diagnostics; they cannot establish behavioral selection or performance effects. Use the separate gate eligibility view for scientific targets. [Evidence and verdict](gate_closure.md).

**EMPIRICALLY VERIFIED IN THIS AUDIT.** [missingness_map.parquet](evidence/missingness_map.parquet) separates design absence, expected file absence and provisional QC flags. Raw-versus-processed absence remains explicit in the canonical manifest; a processed file is never silently replaced by a raw waveform in complete-case counts. Exp.1 electrical streams and pre-4 respiration are absent by design. Exp.1 head is not released despite conflicting documentation. Partial invalidity and heavy interpolation are sample/file-level states, distinct from absent streams.

Directly linked quiz outcomes by processed-eye basic-QC status:

| experiment | eye_basic_qc | people | person_video_observations | mean_partial_score | mean_exact_score |
| --- | --- | --- | --- | --- | --- |
| 1 | False | 5 | 16 | 0.449 | 0.449 |
| 1 | True | 25 | 119 | 0.677 | 0.677 |
| 2 | False | 9 | 30 | 0.303 | 0.303 |
| 2 | True | 27 | 125 | 0.246 | 0.246 |
| 3 | False | 14 | 43 | 0.412 | 0.308 |
| 3 | True | 24 | 130 | 0.526 | 0.425 |
| 4 | False | 15 | 36 | 0.499 | 0.468 |
| 4 | True | 33 | 93 | 0.595 | 0.563 |
| 5 | False | 13 | 36 | 0.510 | 0.481 |
| 5 | True | 37 | 108 | 0.643 | 0.610 |

These are **EXPLORATORY selection diagnostics**, not causal evidence or significant outcome differences. People contribute multiple video observations and the group-specific person counts can overlap. [Trait diagnostics](evidence/missingness_trait_diagnostics.csv) use person-level availability fractions and observed traits without imputation. [Experiment/condition counts](evidence/missingness_by_condition.csv) and [video/correction burdens](evidence/eye_quality_by_condition_video.csv) expose protocol/content dependence. Score references across repeat exposures in the condition table are explicitly descriptive; the direct-outcome table does not duplicate outcomes across sessions.

**OUR INFERENCE.** Complete-case filtering changes the cohort and can select viewing behavior/trait profiles; missing-at-random is not established. Uniform random modality masking is not a validated model of these failure mechanisms. Preserve masks and failure ledgers; a future protocol must report excluded people, videos and durations and assess sensitivity at predefined correction thresholds.
