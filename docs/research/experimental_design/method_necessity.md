# M08 — Method necessity: when a bespoke method would be justified

2026-10-04. **Verdict: no bespoke method is justified now.** The baseline study uses only the ridge family in [M06 §5](evaluation_contract.md#5-model-families-no-search-beyond-this-list). This document fixes which observed failure, if any, would license method development afterwards, and what that method would have to beat.

## Why simple models are the right first instrument (I)

The study has 68 independent learners, 8 content units and a criterion whose within-video reliability is about 0.45–0.57. Under the simulated design, even the *oracle* linear information is attenuated by roughly a third when learned from 61 training people (expected procedure skill 0.067 at oracle 0.10; see [precision](precision_and_independence.md)). Any added flexibility enlarges that estimation loss. A bespoke architecture would be underdetermined by the independent evidence. It would also be indistinguishable from the shortcuts the design is meant to exclude: content identity, quality, experiment.

## Failure modes that could justify later method work

| Observed baseline pattern (pre-declared) | Interpretation | Licensed next step | Must beat |
|---|---|---|---|
| H1 detected; H2a shows the gain is **SYN-only**; B ≈ 0 | Validity depends on peer references | A reference-free *approximation* of synchrony is a candidate, e.g. predicting the content-locked reference from stimulus features. Needs **many more content units**, so external or prospective data | M4 in A; C with a declared reference budget |
| H1 detected; state skill ≈ 0; information is person-level | Physiology identifies stable learner differences, not episode-specific engagement | A new **regime D**: person calibration from the same learner's earlier, labelled or unlabelled, videos. This is a new estimand, not a better network | M2 with person-level covariates; within-person baselines |
| H1 detected **only** with EEG (H2b), and EEG + ECG + gaze > ECG + gaze | EEG carries unique information | G03 (training-only EEG) becomes **eligible**. Its prerequisite is met | Direct ECG+gaze student, CCA, ordinary KD, matched-noise teacher (G03 dossier) |
| Gains vanish under the CAS policy or concentrate in high-quality cells | Selection-dependent validity | G02 (available-sensor policy) analysis | Complete-case versus policy risk at matched coverage |
| M5 ≤ M2, but the explanatory mixed model shows large in-sample association | Estimation variance, overfitting, or in-sample inflation | Prespecified dimension reduction or stronger shrinkage. Not a new architecture | M5 |
| H1 inconclusive or useful effect ruled out | Insufficient information at this scale or for this criterion | **No method development.** Report the bounded result; pursue the external ocular replication or a prospective cohort | — |

## Constraints on any future method

- **Distinct mechanism.** Combining shared/private losses, contrastive alignment, reliability gates or KD is not novel by itself ([literature](../research_gap/literature_evidence.md)). The method must answer a documented failure from the table above.
- **Matched comparison.** Same cells, folds, information budget and tuning budget as the ridge baselines. A matched random-feature control is required for any learned representation.
- **Parameter budget.** Free parameters fitted on BBBD outcomes must stay well below the number of independent learners. Representations with more capacity must be pretrained on **external** unlabelled data, frozen, and checked for pretraining-corpus overlap with BBBD.
- **Confirmation.** A method claim needs an external cohort ([M07](external_validation.md)). Ocular-only methods can be confirmed on John 2025. Tri-modal methods currently cannot be confirmed anywhere.
