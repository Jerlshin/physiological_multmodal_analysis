# MPD-DF — Multimodal Phenotyping Dataset of Driving Fatigue

**Disposition: recent driving-specific candidate; label construction is the main methodological limitation.**

Sources: [Li et al., Scientific Data, 22 January 2026](https://doi.org/10.1038/s41597-026-06634-4); [raw data/questionnaires](https://doi.org/10.6084/m9.figshare.28455737); [processed data](https://doi.org/10.6084/m9.figshare.28113164); [code](https://github.com/ljyTota/MPD-DF).

| Item | Evidence / limitation |
|---|---|
| Cohort | 50 adults, ages 23–59; predominantly women, exact distribution NV. |
| Protocol/duration | Two-hour afternoon simulated driving; speed/gear, sleep and caffeine instructions standardized. Approximately 100 h nominal; 118 min normalized segments give 98.3 h before missingness. One drive/person; time and fatigue strongly entangled. |
| Signals/rates | 32-channel EEG, ECG, two EOG channels and respiration; original EDF and derivatives. Processed EEG 200 Hz, ECG 300 Hz, EOG 30 Hz; native per-channel rates/respiration rate require headers. Video collected but not released. |
| Synchronization | Timestamp alignment with supplied DataAlign.py; no measured hardware alignment precision established. Subject IDs and interval annotations; not BIDS verified. |
| Labels/controls | Physician labels Wake, Fatigue 1–4, Sleep, Artifact using EEG/PSG patterns; questionnaires. Expert annotation is useful but not independent of EEG predictors. Inter-rater reliability NV. |
| Missing/artifacts | Participant 42 early equipment termination; 4/8/9 shorter recordings. Electrode shift, wire pressure and movement documented. Only one Fatigue 4 occurrence outside selected 2 h: cannot promise reliable full five-level classification. |
| Access/license/size/code | Figshare open raw/processed route; displayed raw package about 12.21 GB. Data CC BY 4.0 per release description; code Apache 2.0. Detailed preprocessing code and documented artifacts; exact archive manifest not audited. |

Supports operational physician-scored fatigue and cross-sensor measurement studies in a simulator. Unusual age range and explicit fatigue transitions are useful. Cannot establish road safety benefit, independent physiological discovery of fatigue when EEG determines labels, or generalization to natural traffic/shift work.

At least the descriptor and its signal-validation analysis verified; no additional independent reuse verified. The field of fatigue classification is crowded even if this release is young. Opportunities include non-EEG prediction against expert annotations, uncertainty around transitions and missing-channel robustness. Hold out entire people and contiguous intervals; performance against EEG-derived labels must be described as agreement with the scoring rule. Do not use rare/unobserved stages as a claimed solved target.

