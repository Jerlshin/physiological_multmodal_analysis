# Enhanced Valence-Arousal Multimodal Emotion Dataset

**Disposition: recent emotion/stress candidate; strong protocol and evaluation confounds.**

Sources: [Huang et al., Scientific Data, 15 December 2025](https://doi.org/10.1038/s41597-025-06214-y); [ScienceDB](https://doi.org/10.57760/sciencedb.23231).

| Item | Evidence / limitation |
|---|---|
| Cohort | 64 university participants, 33 men/31 women, age 19–26, mean 22.06 ± 2.08. |
| Protocol/duration | Baseline, three ~10 min positive/neutral/negative videos and 8 min MMST (including neutral period). Two order groups of 30/34; stress task always later. At least ~40.5 h nominal video+MMST exposure across 64, actual complete recording duration NV. |
| Signals/rates | 64-channel EEG, ECG 2000 Hz, Huawei perfusion-index measurements. Sensor PI 25 Hz but released analysis uses minute aggregation; not equivalent to raw PPG. EEG native rate requires header verification. |
| Data/sync/repeats | Raw CNT/ACQ and aligned 4 s FIF epochs; subject IDs, one visit. Timestamp/event alignment described, residual synchronization NR; no BIDS verified. |
| Outcomes/controls | SAM and questionnaire traits (including anxiety/depression/stress measures), video/task conditions. Condition labels are not continuously observed affect. Calm/neutral/stress operational definitions require careful separation. |
| Missing/artifacts | Eye/muscle artifacts, device aggregation, task/motor differences; complete missingness map NV. Time/order and MMST demand can substitute for stress prediction. |
| Access/license/size/code | ScienceDB registration/request route; precise license and full bytes NV. Processing examples described; executable released code completeness NV. |

Supports elicited condition associations and exploratory subjective-affect modelling. Cannot establish diagnostic depression/anxiety, task-independent stress or subject-independent performance from pooled random folds. The descriptor's random pooled 10-fold evaluation and high accuracy do not establish generalization to unseen subjects.

At least descriptor plus its condition-classification benchmark verified; no additional independent empirical reuse verified. Basic emotion/stress classification is already done and methodologically weak splits offer a replication opportunity, not automatically a novel paper. Subject- and stimulus-held-out analyses, label provenance and sensor aggregation deserve priority if reconsidered.

