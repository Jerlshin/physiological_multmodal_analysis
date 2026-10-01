# COG-BCI

**Disposition: strong older repeated-session control/transfer comparator.**

Sources: [Hinss et al., Scientific Data, 10 February 2023](https://doi.org/10.1038/s41597-022-01898-y); [Zenodo v4, December 2022](https://zenodo.org/records/7413650); [questionnaire code](https://github.com/Marcels-2-Neurons/Subjective_Questions/tree/main).

| Item | Evidence / limitation |
|---|---|
| Cohort/duration | 29 adults, 18 men/11 women, mean 23.9 ± 3.20; three separate weekly sessions, over 100 h reported. |
| Protocol/labels | MATB, n-back, PVT and flanker tasks; objective accuracy/RT/task demand, RSME effort and KSS sleepiness. Repeated tasks/visits with subject/session IDs are especially valuable for cross-day robustness. |
| Signals/rates | 64-channel ActiCap EEG 500 Hz plus ECG; no rich eye/EDA/respiration suite established. Exact ECG channel rate/placement needs record headers. |
| Data/sync | Raw unfiltered acquisition, BIDS-organized, LSL/LabRecorder synchronization and event logs. Empirical residual timing error NR. |
| Missing/artifacts | Version 4 corrected electrode-name mismatch; standard EEG ocular/muscle artifacts. Detailed dropout/complete-session intersections require file audit. |
| Access/license/size/code | Open Zenodo, 31.7 GB displayed; CC BY 4.0 reported for dataset. Descriptor strong, questionnaire code available; author validation described, complete turnkey preprocessing code not established. |

Supports cross-task/session workload and vigilance research more directly than BBBD's single-visit experiments. Cannot equate difficulty with experienced workload or transfer from 29 young volunteers to safety-critical workers. EEG–ECG learning is feasible, but physiological breadth is smaller than BBBD/digit span.

At least descriptor plus two peer-reviewed uses verified: [cross-attention subject-independent load classification](https://pmc.ncbi.nlm.nih.gov/articles/PMC11655798/) and [EEG preprocessing/source-localization evaluation](https://pmc.ncbi.nlm.nih.gov/articles/PMC11994696/). Further 2025/26 cross-session and cross-dataset analyses were identified. Workload decoding and cross-session generalization are already active research topics, not unoccupied opportunities. Keep as a controlled external comparator; favor it if cross-day stability becomes essential.

