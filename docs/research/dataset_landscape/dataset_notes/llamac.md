# LLaMAC

**Disposition: strongest recent broad affect candidate with over 100 released participants.**

Sources: [Lee & Kim, Scientific Data, 4 December 2025](https://doi.org/10.1038/s41597-025-06165-4); [Figshare v6 data/code](https://doi.org/10.6084/m9.figshare.28748696.v6); [sensor table](https://www.nature.com/articles/s41597-025-06165-4/tables/3).

| Item | Evidence / limitation |
|---|---|
| Cohort | 114 recruited, 108 retained. Recruit sample: 57 men/57 women, 20–57 years, 27.73 ± 9.08. Retained sex/age distribution should be recalculated; not necessarily still balanced. Korean-language stimuli. |
| Protocol/duration/repeats | 50 one-minute videos/person, approximately 150 min full session. About 90 h stimulus exposure across 108 people, not 270 h clean waveform data. Emotion blocks randomized, videos randomized within blocks. One visit/person, repeated trials. |
| Modalities/rates | 14-channel Emotiv EEG 256 Hz; E4 PPG 64, EDA 4, skin temperature 4 Hz; respiration belt 10 Hz. No ECG or eye tracking. |
| Raw/processed/sync | Timestamped per-subject/trial CSV and author preprocessing/validation code. EEG device filtering already applied. Master computer/system-clock timestamps; authors assert drift is prevented, but no empirical device latency/drift validation is supplied. Shared logging clocks alone do not prove sample-level alignment. |
| Labels/controls | Post-video valence/arousal/dominance (1–5), discrete experienced emotion/intensity, liking and familiarity. “Continuous domain” means dimensional ratings, **not continuously sampled annotation**. Intended clip category and experienced emotion are separate. |
| Missing/artifacts | Six participant exclusions for compliance, movement, fear withdrawal, device failure, language and tic disorder; additional channel/trial exclusion table. No ICA in described EEG processing. Block context, video content, culture and familiarity can drive predictions. |
| Access/license/size | Open Figshare, CC BY 4.0, v6 file total 3,075,830,672 bytes. No BIDS claim. Good tabular documentation and preprocessing/LightGBM code. |

Supports subjective affect/liking associations and low-cost multimodal sensing under video elicitation. Larger independent cohort than DEAP/AMIGOS and explicit familiarity make it unusually useful. Cannot establish an objective universal emotion fingerprint, genuine temporal emotion tracking, media commercial success or causal emotional mechanisms.

At least the descriptor with an emotion-classification baseline was verified; no additional independent reuse verified by the cutoff. Its existing classification, dimensional/discrete agreement and familiarity analyses occupy obvious tasks. Fold-level grouping must be audited before interpreting reported accuracy. Less explored possibilities include participant-plus-video transfer, uncertainty due to disagreement between intended/reported emotion, and failure-aware fusion. Hold out people and videos, preserve block information, and do not present same-session trial count as sample size.

