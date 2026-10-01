# IMPROVE

**Disposition: strongest direct educational-behavior alternative; weaker neural/cardiac measurement than BBBD.**

Sources: [Daza et al., Scientific Data, 31 July 2025](https://doi.org/10.1038/s41597-025-05681-7); [ScienceDB](https://doi.org/10.57760/sciencedb.14565); [official GitHub](https://github.com/BiDAlab/IMPROVE); [Becerra et al., SIIE 2024](https://doi.org/10.1109/SIIE63180.2024.10604582). The 2024 preprint and 2025 descriptor are one work.

| Item | Evidence / limitation |
|---|---|
| Cohort | 120 UAM engineering students, 61 men/59 women, 18–32 years, mean 21. Three balanced groups of 40. |
| Protocol/duration | About 30 min each (roughly 60 participant-hours nominal): short HTML MOOC, reading, 8-item pre/post tests. Phone allowed, visible-but-forbidden, or removed; controlled messages and natural phone use. One session/person. Allocation balancing is not proof of random assignment. |
| Signals/rates | 16 sources include single-channel NeuroSky EEG-derived bands/attention/meditation, Tobii eye 120 Hz, Huawei HR 1 Hz, Fitbit HR 0.2 Hz, inertial, mouse/keyboard, screen capture, audio and cameras 20/30 fps. EDA is measured during pre/post tests, not established as continuous throughout. Native EEG waveform availability/rate NV. |
| Synchronization/processing | Common Unix timestamps/software coordination, no quantified residual jitter. Raw and filtered exports; short gaps up to 5 s interpolated, longer gaps flagged; HR smoothed over 15 s. Not BIDS. |
| Labels | 145 supervised phone interruptions refined with gaze/head behavior; pre/post knowledge, questionnaires and task logs. Vendor “attention” is a model output, not ground truth. |
| Missing/artifacts | Looking at a phone causes informative gaze loss; motion and contact affect wearable data. Refined labels derived from gaze/head can leak those predictors into the target. |
| Access/license/size/code | 2.83 TB reported. Research access requires a signed license/request through official route; no application submitted. Exact redistribution terms NV. Example filtering, event-processing and analysis code available; documentation strong. |

Supports analysis of observable phone behavior and short-session performance changes. The rare combination of interaction logs, phone manipulations and pre/post tests is valuable. Cannot infer generalized cognitive engagement, causally attribute learning changes without allocation details, treat proprietary EEG attention as a validated latent state, or predict long-term educational attainment.

At least two peer-reviewed related works were identified: SIIE 2024 distraction/biometric analysis and the 2025 descriptor, which already reports phone-related biometric effects and refined annotations. Exact participant overlap of earlier platform demonstrations remains NV. New “phone distraction from head/gaze” claims require special caution. Opportunities may lie in outcomes beyond visible interruption, generalization across learners/groups and informative sensor missingness. All records of a person must stay together; report results with the original observer labels separately from predictor-refined labels.

