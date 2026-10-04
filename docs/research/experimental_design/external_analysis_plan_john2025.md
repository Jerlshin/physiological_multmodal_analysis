# External analysis plan — John et al. 2025 ocular replication (time-stamped before download)

Written 2026-10-04, before any John 2025 participant-level eye or outcome file was downloaded or inspected. Only the public file listing, the licence (CC-BY 4.0) and the small workbook/scripts were seen ([M07](external_validation.md)). Downloading `/Mine` (about 4.1 GB) needs the user's authorization. The git commit containing this file is the time-stamp.

## Question

Does the BBBD gaze block (reference-free + synchrony) add held-out individual information about immediate posttest performance on one instructional video, beyond:

1. age, sex, study condition and gaze-data loss (**M2-ext**);
2. **M2-ext + pretest** (**M2p**, the prior-knowledge-adjusted baseline unavailable in BBBD)?

The primary external contrast is M5-ext versus **M2p**.

## Data

- **Source:** OSF 4rn5q; `/Mine/Mine_Eye/edf` (EyeLink 1000, 500 Hz, right eye) and `ScriptVariables.xlsx` sheet `Quest`.
- **People:** those with both an EDF file and a questionnaire row. The listing shows 117. The paper's 105-person post hoc selection is **not** used; both counts are reported.
- **Outcome:** posttest proportion correct over the 13 `knowPost_*` items, using the scoring supplied in the workbook. Exact versus partial semantics are documented after the outcome-blind inspection in §5.
- **Covariates:** age, sex, condition (0/1), and pretest sum over the 7 `knowPre_*` items (M2p only).

## Frozen feature definitions (mirroring [protocol §6](protocol.md#6-feature-dictionary-frozen-no-outcome-based-selection))

- **Valid samples:** outside EyeLink-parsed blinks with a ±100 ms buffer, finite, and on the display (resolution from the EDF `DISPLAY_COORDS` message).
- **Q-ext:** the invalid-sample fraction.
- **RF:** gaze dispersion (normalized by the display diagonal) and saccade rate (EyeLink-parsed saccades with onset in valid time, per valid minute).
- **SYN:** gaze ISC, the mean of horizontal and vertical Pearson r against the training-fold reference mean on a common 128 Hz grid aligned at video onset. Training people use leave-self-out references.
- **No pupil level.** Pupil ISC only as a secondary block, mirroring PAS-four.
- **QC:** people with invalid fraction > 0.50 are excluded, the same threshold as BBBD. Their count and outcome distribution are reported.

## Evaluation and inference

- **Cross-validation:** person-level 10-fold (one cell per person), repeated R = 50.
- **Model:** ridge with inner 5-fold penalty selection over the same grid.
- **Metrics:** skill = 1 − MSE(M5-ext)/MSE(baseline), plus ΔRMSE/ΔMAE in posttest items.
- **Test:** the same detection test and interval method frozen for BBBD H1 ([precision](precision_and_independence.md)). One-sided α = 0.05 for M5-ext versus M2p. M5-ext versus M2-ext is secondary.
- **Transport check (descriptive):** a BBBD-trained gaze model (scale-free RF features only, outcome standardized within cohort) applied to John. Labelled transport, not replication.

## Outcome-blind steps allowed before the analysis

1. Parse the EDFs.
2. Compute the features and their QC.
3. Freeze the feature table, with its hash recorded.

Only then join the posttest. Any deviation is logged in the [decision log](../research_gap/decision_log.md) with its timing.
