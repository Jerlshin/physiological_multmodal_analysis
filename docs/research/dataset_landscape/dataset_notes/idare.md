# I DARE — multimodal affective response dataset

**Disposition: controlled affect candidate; short events and processed-signal uncertainty constrain cardiac research.**

Sources: [Bilucaglia et al., Frontiers in Human Neuroscience, 20 March 2024](https://doi.org/10.3389/fnhum.2024.1347327); [official Figshare project](https://figshare.com/projects/I_DARE/186558).

| Item | Evidence / limitation |
|---|---|
| Cohort | 63 adults, 24 men/39 women; 20–30 years, mean 22.89 ± 2.38. |
| Protocol/duration/repeats | 32 IAPS/OASIS pictures, 5 s each, randomized order, black-screen intervals and post-picture SAM; eyes-closed/fixation baselines. 2.8 h total picture exposure (63 × 32 × 5 s); whole-session duration NR. Repeated trials within one visit. |
| Modalities/rates | 40-channel EEG, EMG, skin conductance and PPG through NVX52 at 1000 Hz; Tobii eye tracking 150 Hz. Processed EEG 512 Hz, SC/PPG 32 Hz. |
| Data/synchronization | Processed MAT with event structures; untouched native waveform availability NV. Initial TTL/software events described; subsequent eye/physio drift and residual timing error NR. Subject IDs, no BIDS verified. |
| Labels/controls | SAM valence/arousal 9-point ratings; reported agreement with stimulus norms only moderate (kappa about .41). Stimulus norms are not each subject's emotional truth. |
| Missing/artifacts | Eye blinks/loss, facial muscle contamination, short trials and physiological latency. Paper describes PPG filtering at 0.001–0.35 Hz, which would remove normal pulse-frequency content if applied literally; inspect raw files/code before HR/HRV analysis. |
| Access/license/size/code | Public Figshare project; exact file-level license, total bytes, raw completeness and executable preprocessing code NV. Article license is not assumed to be data license. Useful event/processing documentation. |

Supports event-related subjective affect and ocular/central/peripheral comparisons to standardized pictures. Same-amplifier physiology and randomized stimuli are unusually useful. Cannot support robust standard HRV estimation from five-second events, temporal emotion trajectories, or clinical emotion dysfunction.

At least the descriptor/physiological validation paper verified; no additional independent empirical reuse verified. A systematic strong ML benchmark was not established in this review. Plausible opportunities include subjective-versus-normative label disagreement and modality quality, with subject and image holdouts. Native PPG/filter verification is a substantive gate, not a cosmetic implementation issue.

