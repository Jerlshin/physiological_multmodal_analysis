# BALLADEER

**Disposition: strong pediatric clinical candidate; not primary because coverage and diagnostic confounding need substantial audit.**

Sources: [Trujillo et al., Scientific Data, 12 February 2026](https://doi.org/10.1038/s41597-026-06758-7); [Figshare dataset, v2](https://doi.org/10.6084/m9.figshare.28676042); [coverage table](https://www.nature.com/articles/s41597-026-06758-7/tables/1).

| Item | Evidence / limitation |
|---|---|
| Cohort | 164 children aged 6–18, mean 12.4; 66 girls/98 boys. 62 ADHD (14 girls/48 boys), 102 controls (52/50). Specialist DSM-5 diagnoses; controls recruited by snowball sampling. Collection June 2022–December 2024. |
| Protocol and repeats | Two assessment days with Attention Slackline levels, Attention Robots, CogniFit, age-specific Nesplora and questionnaires. Three Slackline levels of about 5 min each; total usable hours NR. Participant identifiers link tasks, but this is not longitudinal prognosis. |
| Signals/rates | CGX 30-channel EEG 500 Hz in Slackline; Emotiv 14-channel EEG, device settings 64–256 Hz, in other tasks. Empatica EmbracePlus EDA/HR; Tobii 5 eye-related events. Per-file actual rates and full gaze versus event-only content NV. HR is not an ECG waveform. |
| Coverage | Slackline: 140 EEG versus 99–100 wearable versus 151–154 eye/behavior participants by level. Robots: 132 EEG, 95 wearable, 145 eye, 150 behavioral. CogniFit: 129 EEG, 84 wearable. These marginal counts do not give the all-modality intersection. |
| Synchronization/raw | Raw CSV/JSON and task events, shared software session start/stop; no hardware trigger chain or measured residual precision established. Not confirmed BIDS. |
| Outcomes/controls | ADHD status, attention-task responses, clinical questionnaires and cognitive test scores. Task difficulty manipulation helps; device, task, age, sex, recruitment and possible medication effects complicate interpretation. |
| Access/license/size/code | Open Figshare v2 (17 April 2026), CC BY 4.0; API file total 13,633,870,282 bytes. Detailed architecture/coverage documentation; acquisition backend described, no complete public preprocessing pipeline verified. |

Supports within-task associations, developmental/diagnostic subgroup comparisons and robust multimodal assessment research. Unusually valuable for clinically characterized children, a group poorly represented in adult video datasets. Cannot establish screening deployment, disease-specific brain markers, medication response or long-term prognosis. Separate hardware families are entangled with tasks; a random-window diagnostic classifier could learn person, sex, age, movement or device.

At least the descriptor was verified; it cites earlier attention-game/platform work, whose exact overlap with released participants is unverified and is not counted as independent reuse. No additional independent full-dataset empirical reuse verified. Apparent low saturation does not remove strong confounds. Opportunities include cross-task robustness and missing-sensor analysis with age/sex/task-matched comparisons. Hold out children across every task/day; evaluate whether device changes are separable from task changes. Needed: consent/file coverage, medication/comorbidity fields, rates, all-modality counts and diagnosis-blind preprocessing.

