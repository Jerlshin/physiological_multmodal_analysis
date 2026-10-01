# DEJA-VU — emotional transitions in virtual reality

**Disposition: transition/VR alternative; synchronization and sample size prevent primary selection.**

Sources: [Ishmakhametov et al., Scientific Data, 20 May 2026](https://doi.org/10.1038/s41597-026-07456-0); [Zenodo v1.0.0, 1 December 2025](https://zenodo.org/records/17773125).

| Item | Evidence / limitation |
|---|---|
| Cohort/repeats | 28 adults, 11 women/17 men, age 20–65, mean 33.1; 34 sessions, six participants return after at least 24 h. |
| Protocol/duration | VR emotional-quadrant scenes with neutral washouts; six sequence arrangements, incomplete coverage. Up to 22.5 min/session gives at most 12.75 nominal session-hours. |
| Modalities/rates | Seven EEG channels 300 Hz, four ECG leads and two EMG channels 512 Hz, three GSR channels 10 Hz. |
| Data/sync | Raw XDF and aligned H5/metadata/SQLite; physiology via LSL but stimulus alignment approximately ±0.5 s from manual/video alignment. BIDS-inspired, not validated compliance. |
| Outcomes/controls | Pre/post SAM/PANAS, discrete emotion and personality; transition conditions. Ratings are not continuous ground truth. VR sensory and motion effects can explain physiology. |
| Missing/artifacts | Small/uneven repeated-session subset; dry EEG/movement, VR discomfort and contact artifacts. Complete channel/session quality matrix NV. |
| Access/license/size/code | Open Zenodo, data CC BY 4.0. Public API totals 3,996,579,943 compressed bytes; paper reports larger unpacked organization (~6.41 GB), not a contradiction by itself. Pipeline code archive included. |

Supports coarse transition/condition responses and limited repeatability analyses. VR transition structure is unusual. Cannot justify millisecond cross-modal timing, causal emotional transitions, continuous affect inference from sparse reports or strong population claims at N=28.

At least descriptor plus its transition validation verified; no additional independent reuse verified. Basic before/after transition analyses are already present. Robustness to transitions and missing signals could be useful, but most return-session tests have only six independent people. Hold out all sessions of each person, then evaluate sequence transfer. The article's physiological validation is evidence of signal responsiveness, not proof of a specific internal emotion.

