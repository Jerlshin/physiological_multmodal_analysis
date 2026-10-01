# WESAD

**Disposition: essential wearable stress reference; unsuitable as the sole foundation for a new generic classifier paper.**

Sources: [Schmidt et al., ACM ICMI 2018](https://doi.org/10.1145/3242969.3242985); [UCI official record, DOI 10.24432/C57K5T](https://archive-beta.ics.uci.edu/dataset/465/wesad%2Bwearable%2Bstress%2Band%2Baffect%2Bdetection).

| Item | Evidence / limitation |
|---|---|
| Cohort/protocol | 17 recruited, 15 released after device failures; 12 men/3 women, age 27.5 ± 2.4. Baseline, Trier Social Stress Test, amusement and meditation. Roughly two-hour laboratory protocol; usable labeled hours must be summed, not assumed to equal setup duration. |
| Signals/rates | RespiBAN ECG, EDA, EMG, respiration, temperature and acceleration 700 Hz; E4 BVP 64 Hz, acceleration 32, EDA/temperature 4. No EEG/gaze. |
| Raw/sync/IDs | Native wearable streams plus synchronized subject-level exports/pickles and labels; subject IDs retained. One visit, repeated phases rather than longitudinal measurements. Exact residual timing audit NV. |
| Labels/controls/artifacts | Protocol states plus PANAS/STAI/SAM/SSSQ. Stress tasks involve speaking/movement distinct from baseline, so task recognition can masquerade as stress inference. Contact/motion and two excluded recordings; no assumption of no missingness. |
| Access/license/size/code | UCI record explicitly CC BY 4.0 and links external download; compressed size roughly 2.5 GB in common distribution, not locally audited. Detailed README, non-BIDS; original feature baselines and many independent implementations. |

Supports wearable stress-protocol discrimination and peripheral modality comparison. Cannot establish generalized stress diagnosis, fine emotion truth, workplace transportability or stable person-independent performance from only 15 people.

Literature is very crowded; beyond original, recent studies explicitly compare subject-dependent/independent evaluation ([IEEE Access](https://doi.org/10.1109/ACCESS.2024.3525459)) and user-bias/representation learning ([Springer](https://doi.org/10.1007/s11760-025-04500-1)). At least three works verified including original, a small lower bound. Missing-modality and cross-dataset claims also need dedicated novelty checks. Keep as a secondary benchmark for failure modes; select BBBD/digit span for broader brain–body science and DREAMT for clinical wearable reference.

