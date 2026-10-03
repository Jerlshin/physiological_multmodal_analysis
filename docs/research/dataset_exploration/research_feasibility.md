# Research-question feasibility — no final question selected

**OUR INFERENCE — updated 2026-10-02.** The current behavioral ceilings exclude Experiment 2. The original release-key ceilings remain in the CSV as historical audit fields; they do not certify response-option provenance. Counts below reuse exactly the prior direct-test/exposure rule and provisional QC. OQ-06 still blocks a full multimodal transition. [Gate findings](gate_closure.md).

| candidate | direction | feasibility | usable_people | usable_videos | usable_person_video_observations | modalities |
| --- | --- | --- | --- | --- | --- | --- |
| C01 | Incremental behavioral information | MEDIUM | 94 | 8 | 324 | eeg+ecg+eye |
| C02 | Reliability under observed sensor failure | MEDIUM | 94 | 8 | 324 | eeg+ecg+eye |
| C03 | Transport across experimental settings | MEDIUM (3–5 only) | 94 | 8 | 324 | eeg+ecg+eye |
| C04 | Reduced-sensor outcome measurement | MEDIUM | 94 | 8 | 327 | ecg+eye |
| C05 | Temporal item-linked evidence | LOW | 94 | 8 | 324 | eeg+ecg+eye |
| C06 | Falsifiable representation benefit | LOW | 94 | 8 | 324 | eeg+ecg+eye |
| C07 | Reproducibility and measurement validity | HIGH | 119 | 8 | 429 | eeg |

| candidate | confounds | timing | prior_occupancy | second_dataset |
| --- | --- | --- | --- | --- |
| C01 | Only 8 videos in the multimodal behavioral subset; heterogeneous quiz scoring/chronology; selection and globally processed EEG | Whole-video plausible; derivative provenance unresolved | P03 multimodal quiz association and P04 EEG+trait models | Likely useful for external validation; labels must retain domain semantics |
| C02 | Natural failure varies by experiment/person/video; quality-based selection | Whole-video quality/outcome analysis plausible; fine timing unsupported | P03 complete-case exclusions; explicit robustness occupancy not verified | Useful to test new sensor/population failures |
| C03 | Exp.2 incidental-learning behavior excluded; 4/5 share 3 videos; different exposure histories; cross-experiment human overlap unresolved | Aggregate transport only until clocks/provenance clarified | P03 replication/P04 spatial-filter transfer | Likely needed for genuinely external transport |
| C04 | EEG teacher fit/reference scope; mixed labels; small independent content | Aggregate feasible; no lag-based teacher claim | P03 EEG-to-body linear prediction and P01 webcam precedent | Useful for an operational low-cost measurement claim |
| C05 | No reliable item-content timestamps or device residuals; interpolation can span minutes | Insufficient for proposed fine timing/directional analysis | P02 frequency work and P03 10s temporal work | A dataset with native triggers/item timestamps likely necessary |
| C06 | Small independent N; 8 videos; P05/pretraining lineage unknown; stimulus shortcuts | Aggregate representations possible after provenance gate | CorrCA/PCA strong precedent; modern competitors not fully accessed | Likely necessary for robust representation/transfer claims |
| C07 | Release integrity includes all records; behavioral ceilings exclude Exp.2. P01 Exp.2 aggregate non-equivalence established; original response permutations and executed figure inputs unavailable | Released aggregate definitions auditable; exact original reproduction conditional | All P01–P04/descriptor predate or differ from current release | Not necessary to demonstrate release integrity; helpful for measurement generality |

[Complete matrix](evidence/research_feasibility.csv); [exact before/after counts](evidence/gate_closure_feasibility_counts.csv). C01/C02/C04 remain conditional MEDIUM with smaller cohorts. C03 permits bounded 3–5 protocol comparisons; incidental-versus-intentional behavioral transport is ineligible. C05/C06 remain LOW. C07 HIGH concerns demonstrable release measurement/integrity, which may inspect all records; its table counts are the conservative behavioral subset, and exact historical-paper reproduction remains conditional.

Exp.3 is the strongest remaining first-view multimodal quiz cohort (24 people / 124 observations / 6 videos). Exp.4 contributes 33 / 92 / 3 single-exposure tested observations; Exp.5 contributes 37 / 108 / 3 repeat/preview/incentive observations. Exp.2 remains available for signal/condition measurement within provenance limits. None of these counts guarantees power, fixes selection bias or selects a final question. Preserve separate partial/exact outcomes, chronology, masks and people/video grouping. Absolute amplitude, fine timing/directional claims and unverifiable preprocessing invariance remain constrained. No model is developed.
