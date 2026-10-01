# DEAP

**Disposition: essential historical comparator, not a primary novelty foundation.**

Sources: [Koelstra et al., IEEE TAFFC, online 2011 / issue 2012](https://doi.org/10.1109/T-AFFC.2011.15); [official dataset](https://eecs.qmul.ac.uk/mmv/datasets/deap/); [data description](https://eecs.qmul.ac.uk/mmv/datasets/deap/dataset.html); [download terms](https://eecs.qmul.ac.uk/mmv/datasets/deap/download.html). Official pages were intermittently inaccessible during this pass; terms and file inventory need rechecking at acquisition.

| Item | Evidence / limitation |
|---|---|
| Cohort/protocol | 32 adults, 16 women/16 men, 19–37; 40 one-minute music videos each, post-video ratings. 21.3 h stimulus exposure, excluding baseline/setup; one visit, repeated trials, subject IDs. |
| Modalities/rates | 32 EEG plus peripheral EOG/EMG, GSR, respiration, temperature and BVP (not ECG). Native 512 Hz; commonly used processed export 128 Hz. Face video only for 22 participants. |
| Labels/controls | Self-reported valence/arousal/dominance/liking/familiarity, selected music-video stimuli and baseline periods. Shared video content is a major confound. No clinical/educational outcome. |
| Data/sync/artifacts | Raw and processed releases; stimulus-aligned trials, processed EEG filtering/ocular correction. Native-to-video residual precision, complete missingness map and exact current bytes NV. Brain/eye/muscle artifacts remain task dependent. |
| Access/license/code | Academic agreement/request route; not assume CC license or redistribution. Subject/trial MATLAB/Python-friendly exports, not BIDS. Original documentation and extensive community preprocessing, often inconsistent. |

Supports benchmark affect-rating associations and comparison with established methods. Cannot establish deployment, causal emotions or independent test performance from shuffled windows of the same people/videos.

Literature is highly saturated: original multimodal baselines and many later EEG/fusion, graph and cross-dataset studies. Verified recent examples include [HCSFNet](https://doi.org/10.1109/TAI.2024.3523250) and [cross-dataset work](https://doi.org/10.1109/TCDS.2025.3566229); exact totals are not claimed. At least the original plus these two methodological works were identified, representing only a tiny lower bound. Generic fusion, attention networks and binary valence/arousal accuracy are not sufficient novelty. Useful as a secondary robustness benchmark if label scales, channels, missing faces and preprocessing are harmonized without treating datasets as interchangeable.

