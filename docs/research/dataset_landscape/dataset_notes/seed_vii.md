# SEED-VII

**Disposition: strong recent EEG–eye affect benchmark; narrower physiology and small N.**

Sources: [official SJTU page](https://bcmi.sjtu.edu.cn/home/seed/seed-vii.html); [Jiang et al., original IEEE paper](https://doi.org/10.1109/TAFFC.2024.3485057), online 23 October 2024, TAFFC 16(2):969–985, 2025. Distinguish this release from other SEED-family datasets.

| Item | Evidence / limitation |
|---|---|
| Cohort/protocol | 20 adults, 10 women/10 men, 19–26, mean 22.5 ± 1.8; four sessions, 20 clips each, 80 unique clips. Total clip time 14,097.86 s/person (~78.32 participant-hours for all 20), not audited retained signal duration. |
| Modalities/rates | 62-channel EEG native 1000 Hz, processed 200 Hz; Tobii Pro Fusion eye data. Exact eye rate NV; no ECG/EDA/respiration stream established. |
| Labels/repeats/controls | Seven intended emotion classes and retrospective continuously reviewed intensity; repeated sessions. Session number encodes stimulus set, not necessarily chronological visit order. Emotion coverage and sequence differ across sessions; personality-based recruitment limits population scope. |
| Data/sync/artifacts | Raw CNT, eye TSV and features, timestamp/event association; quantified residual error and full missingness map NV. EEG/ocular contamination and retrospective annotation delay matter. |
| Access/license/size/code | Academic request agreement, precise redistribution terms/current size NV. Official feature/extraction examples, non-BIDS organization. Good protocol documentation. |

Supports EEG–eye complementarity, emotion intensity and cross-session assessment. Many stimuli are useful for stimulus-held-out analyses despite only 20 people. Cannot support full autonomic brain–body inference, clinical diagnosis or generalized emotion ground truth from clip categories.

Original work already develops multimodal adaptive fusion, adversarial cross-subject generalization and intensity-based sample selection. [2026 cross-dataset EEG work](https://www.mdpi.com/2079-9292/15/10/1971) explicitly includes SEED-VII; [MMSTG-Net, IEEE JBHI 2026](https://doi.org/10.1109/JBHI.2026.3667946) already evaluates EEG–eye fusion with cross-modal contrastive alignment and subject-independent tests. At least original plus two reuse works identified; do not use citation totals of SEED/SEED-IV as SEED-VII saturation. Emerging resource in a mature benchmark ecosystem. Remaining opportunities require participant and stimulus/session controls rather than new fusion machinery alone.
