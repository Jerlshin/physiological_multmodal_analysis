# DREAMT

**Disposition: strongest clinical/sleep alternative; could become primary if clinical wearable validation is prioritized.**

Sources: [PhysioNet v2.2.0, 2026-06-02](https://physionet.org/content/dreamt/2.2.0/); [Wang et al., Addressing Wearable Sleep Tracking Inequity, CHIL 2024](https://proceedings.mlr.press/v248/wang24a.html); [WatchSleepNet, 2025](https://proceedings.mlr.press/v287/wang25a.html); [author code](https://github.com/WillKeWang/WatchSleepNet_public). Both proceedings records were directly verified.

| Item | Evidence and qualification |
|---|---|
| Cohort | 100 unique Duke sleep-clinic participants, collected May–September 2022. Mean age 56.2 ± 16.6, BMI 33.7 ± 8.6; 68 obese/severely obese, 23 severe OSA. Sex/race composition requires participant metadata access. |
| Protocol/duration/repeats | One laboratory overnight PSG with concurrent wrist wearable; approximately 23:00–06:00. Roughly 700 participant-hours is a protocol estimate, **not** a summed usable total. One night per person does not support longitudinal stability claims. |
| Signals/rates | E4 BVP 64 Hz, acceleration 32, EDA/temperature 4, HR 1, event-based IBI. Current release also includes PSG EEG/EOG/EMG/ECG, airflow, thorax/abdomen, oxygen saturation and movement/snore. PSG 200→100 Hz; unified PSG/wearable files 100 Hz, wearable-only files 64 Hz. |
| Raw/processed/synchronization | Resampled timestamp-aligned CSV, imputed/gap-handled values. These are not untouched native waveforms. **v2.2 fixes acceleration-to-PSG misalignment**. Residual error and mask availability need inspection. |
| Labels/controls | Expert 30 s W/N1/N2/N3/REM scoring and sleep-health metadata. Preparation P is mapped to W in 100 Hz files: avoid training on preparation as genuine scored wake without checking. Clinical protocol, not randomized disease exposure. |
| Missingness/artifacts | Two people each have 15 min missing labels after PSG restart; four others one epoch. Wrist contact/motion, stage imbalance and variable alignment/imputation remain relevant. |
| Access/license/size | Restricted PhysioNet account/data-use route; Restricted Health Data License 1.5.0. Access was not requested. Full byte size NV behind access. Do not assume downloadable means unrestricted redistribution. |
| Documentation/standardization/code | Strong version notes, metadata descriptions and author methods code; no BIDS compliance established. Public description is clear, files not audited. |

Supports wearable-to-clinical reference comparisons, sleep-state estimation, modality availability and robustness across sleep-disorder phenotypes. Its unusual advantage is clinically scored physiology paired with a deployable wearable in a clinically relevant cohort. Sleep-stage scoring is not an external diagnosis of every neurological state, and PSG-based scoring is partly derived from the very EEG/EOG/EMG channels used by a full-PSG predictor. Wrist-only prediction against PSG offers a cleaner measurement-validation interpretation. Cannot establish home performance, multi-night reliability, causal disease mechanisms or educational engagement.

At least **two peer-reviewed methodological works** were verified: the 2024 dataset/baseline paper and WatchSleepNet 2025. The latter already uses cross-domain ECG/PPG interval information and transfer involving large sleep cohorts; ordinary cross-modal sleep staging is occupied. Relatively recent full-PSG release may support less explored missing-sensor and phenotype-conditional calibration studies, but the sleep-staging field itself is highly mature. Hold out whole people/nights and keep normalization/pretraining provenance explicit. Access, updated alignment, true PSG/wearable overlap, demographic imbalance and reference-label handling are the principal decision risks.
