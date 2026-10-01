# MMV — MultiModal Vigilance

**Disposition: strong repeated-session vigilance resource; too few people and too much label circularity for default primary selection.**

Sources: [Wei et al., Scientific Data, 10 August 2024](https://doi.org/10.1038/s41597-024-03729-8); [ScienceDB](https://doi.org/10.57760/sciencedb.ai.00010).

| Item | Evidence / limitation |
|---|---|
| Cohort | 18 adults, 12 men/6 women, age 24 ± 2.54; 16 students and 2 workers. |
| Protocol/duration | Four sessions on separate days, two RSVP and two SSVEP BCI sessions; approximately 2 h each, about 144 h nominal before losses/calibration distinctions. Many repeated windows but only 18 independent people. |
| Signals/rates | EEG/EOG, ECG, PPG, EDA, two EMG channels and eye tracking. Neuroscan/BIOPAC/EyeLink streams reported at 1000 Hz; aligned processed signals at 200 Hz. Native raw CNT/EDF/MAT, processed trials and features. |
| Synchronization | Common task events across recording systems; event alignment described, residual offset/drift statistics NR. |
| Outcomes | PERCLOS eye-closure-derived vigilance, estimated every 4 s with 60 s smoothing; BCI/task behavior. PERCLOS is an operational ocular measure, not independent clinical sleepiness truth. |
| Controls/repeats | Subject and session IDs permit unseen-person and unseen-day tests, two BCI paradigms. Fixed prolonged visual tasks, flicker and time-on-task restrict generalization. |
| Missing/artifacts | Subject 15 session 2 loses ECG after 3300 s; supplied ECG features use PPG substitution. Eye-loss labels may involve manual supplementation. Preserve provenance; a substituted modality is not independent evidence. |
| Access/license/size/code | Official ScienceDB route; exact current access workflow, data license and bytes NV. Structured subject files and MATLAB/Python processing examples; no BIDS claim verified. Detailed descriptor. |

Supports within-person vigilance dynamics and cross-day/task robustness. Distinctive value is broad concurrent physiology and genuine repeated days. Cannot claim EEG/eye fusion predicts an independent vigilance construct when the label is calculated from eye behavior, nor generalize to natural driving from BCI flicker tasks.

The descriptor already benchmarks temporal/neural approaches and modality combinations, including EEG–EOG fusion; more modalities do not automatically improve results. At least one descriptor/baseline verified. A 2025 IEEE paper titled “Physiologically Guided Cross-Modal Fusion for Robust Vigilance Estimation” was discovered, but exact MMV use was not verified; do not count it yet. Less explored candidates: sensor failures, session transfer and prediction against independent task performance. Subject-held-out splits plus session/time blocks and smoothing-boundary exclusions are essential. No architecture or task is selected.

