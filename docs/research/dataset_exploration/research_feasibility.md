# Research-question feasibility — no final question selected

**OUR INFERENCE** grounded in audited files. Counts below are the provisional basic-QC, directly linkable memory-outcome subset for the indicated sensor combination. A direction can need a smaller cohort once traits/reference/timing eligibility is imposed. These are ceilings for candidate design, not a power analysis or promised predictive accuracy.

| candidate | direction | feasibility | usable_people | usable_videos | usable_person_video_observations | modalities |
| --- | --- | --- | --- | --- | --- | --- |
| C01 | Incremental behavioral information | MEDIUM | 120 | 11 | 444 | eeg+ecg+eye |
| C02 | Reliability under observed sensor failure | MEDIUM | 120 | 11 | 444 | eeg+ecg+eye |
| C03 | Transport across experimental settings | MEDIUM | 120 | 11 | 444 | eeg+ecg+eye |
| C04 | Reduced-sensor outcome measurement | MEDIUM | 120 | 11 | 447 | ecg+eye |
| C05 | Temporal item-linked evidence | LOW | 120 | 11 | 444 | eeg+ecg+eye |
| C06 | Falsifiable representation benefit | LOW | 120 | 11 | 444 | eeg+ecg+eye |
| C07 | Reproducibility and measurement validity | HIGH | 149 | 11 | 578 | eeg |


| candidate | confounds | timing | prior_occupancy | second_dataset |
| --- | --- | --- | --- | --- |
| C01 | Only11 videos; heterogeneous quiz scoring/chronology; selection and globally processed EEG | Whole-video plausible; derivative provenance unresolved | P03 multimodal quiz association and P04 EEG+trait models | Likely useful for external validation; labels must retain domain semantics |
| C02 | Natural failure varies by experiment/person/video; quality-based selection | Whole-video quality/outcome analysis plausible; fine timing unsupported | P03 complete-case exclusions; explicit robustness occupancy not verified | Useful to test new sensor/population failures |
| C03 | 4/5 share3 canonical videos; outcome after different exposure histories; cohort identity unknown | Aggregate transport only until clocks/provenance clarified | P03 replication/P04 spatial-filter transfer | Likely needed for genuinely external transport |
| C04 | EEG teacher fit/reference scope; mixed labels; small independent content | Aggregate feasible; no lag-based teacher claim | P03 EEG-to-body linear prediction and P01 webcam precedent | Useful for an operational low-cost measurement claim |
| C05 | No reliable item-content timestamps or device residuals; interpolation can span minutes | Insufficient for proposed fine timing/directional analysis | P02 frequency work and P03 10s temporal work | A dataset with native triggers/item timestamps likely necessary |
| C06 | Small independent N;11 videos; P05/pretraining lineage unknown; stimulus shortcuts | Aggregate representations possible after provenance gate | CorrCA/PCA strong precedent; modern competitors not fully accessed | Likely necessary for robust representation/transfer claims |
| C07 | Current metric/key defects demonstrable; original executed inputs still missing | Released aggregate definitions auditable; exact original reproduction conditional | All P01–P04/descriptor predate or differ from current release | Not necessary to demonstrate release integrity; helpful for measurement generality |


[Complete feasibility matrix](evidence/research_feasibility.csv) also records generalization unit, independent-observation limits, outcomes, missingness and evidence paths. C07 HIGH refers to released measurement/integrity auditing; exact published-analysis reproduction remains MEDIUM/conditional on original inputs. C02's measured masks are valuable but are not proof that robustness/calibration can be evaluated without selection bias.

Reframe C01/C04 as incremental, independently evaluated behavioral information rather than generic physiology-to-learning novelty. Reframe C03 as protocol/exposure transport, not isolated reward causality. Abandon sub-second/directional C05 claims on the current release until native timing and item alignment exist; multi-second descriptive alternatives would still need sensitivity controls. Defer architecture-led C06/foundation-model work until the competitor/pretraining and sample-size gates are resolved. Long-term learning gain, clinical diagnosis and a pure attention biomarker are unsupported outcome interpretations. No candidate is chosen.
