# SENSE-42

**Disposition: strong recent HCI alternative; smaller cohort and restricted/consent-dependent coverage.**

Sources: [Zhang et al., Scientific Data, accepted paper published 26 June 2026](https://doi.org/10.1038/s41597-026-07726-x); [Zenodo 20328099](https://zenodo.org/records/20328099); [official code/documentation](https://github.com/Catherine9811/HCI-SENSE-42); [CHI EA 2026 analysis](https://doi.org/10.1145/3772363.3798603). Archive displays July 2025; distinguish archival date from descriptor publication.

| Item | Evidence / limitation |
|---|---|
| Cohort | 42 adults, 21 men/21 women, 18–40, mean 26.8 ± 4.5; varied backgrounds. Medication/caffeine usual use retained for ecological realism. |
| Protocol/duration | Two-hour continuous simulated desktop use, about 84 nominal participant-hours; file management, typing, browsing and switching; macOS/Windows-like interfaces within person. Many task blocks, one visit/person. |
| Signals/rates | 32-channel BioSemi EEG 1024 Hz; three-lead ECG from auxiliary channels; respiration belt, processed 32 Hz WAV; webcam and per-frame keyboard/mouse behavior at 144 Hz logging. Webcam is not a calibrated eye tracker. |
| Raw/processed/synchronization | Raw BDF, cleaned SET, ECG FIF, respiration WAV and behavioral files; event-locked physiology. Exact residual trigger statistics and webcam alignment require primary full-text/file verification; accepted PDF unavailable through the inspected web route. Do not use secondary-mirror numerical claims as validated evidence. |
| Labels/controls | KSS, NASA-TLX and attentiveness every five minutes, task performance/RT; PSQI/ESS and traits. Controlled noise and task environment, spontaneous alertness rather than randomized sleep deprivation. |
| Coverage/artifacts | GitHub marks ECG/webcam sharing as consent-dependent; archive description says all agreed to authorized research. Reconcile those statements and file counts. Movement/typing, self-report interruption, interface familiarity and time-on-task matter. |
| Access/license/size/code | Zenodo restricted request, CC BY 4.0 metadata; GitHub code CC0 (separate license). Actual data bytes NV; 1.7 TB “data volume” is download traffic, not archive size. Flat modality directories, not BIDS. Rich Python/R/PsychoPy scripts, some marked work-in-progress. |

Supports within-session alertness, interaction behavior and physiological associations in realistic but controlled HCI. Unusually useful because logs link actual performance to dense physiology. Cannot equate subjective sleepiness with clinical sleep disorder, infer accurate pupil/gaze from ordinary webcam without validation, or claim real-world cross-day deployment.

At least descriptor plus CHI EA 2026 analysis identified. The latter already studies prediction of sleepiness fluctuation; detailed methods/results were not accessible, so its full novelty footprint remains a **decision-relevant unknown**, not proof that fusion is untouched. Opportunities could involve interface/trait generalization and sensor availability, subject to that review. Hold out subjects and task contexts; five-minute labels repeated over many windows are not independent observations.

