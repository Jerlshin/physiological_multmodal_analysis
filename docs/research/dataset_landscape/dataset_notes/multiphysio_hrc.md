# MultiPhysio-HRC

**Disposition: promising 2025/26 industrial task-transfer resource; not selected due to confounds and incomplete release audit.**

Sources: [Bussolan et al., author preprint, October 2025](https://arxiv.org/abs/2510.00703); [official project](https://automation-robotics-machines.github.io/MultiPhysio-HRC.github.io/); [Zenodo 2026 release](https://zenodo.org/records/18668043).

| Item | Evidence / limitation |
|---|---|
| Cohort | 55 on day one, 42 returning on day two; 48 men/7 women, mean age 27.98 ± 10.22. Institutional/engineering recruitment; retained per-task intersection NV. |
| Protocol/duration | Cognitive tasks (Stroop/n-back), VR affect, manual and robot-assisted battery disassembly/assembly. Two days and multiple tasks; total recorded hours NV. |
| Modalities/rates | Twelve dry EEG channels plus ECG, EDA, EMG and respiration, reported 256 Hz; facial action units ~2 fps and voice. Raw per-device format/completeness requires archive audit. |
| Labels/controls | STAI, NASA-TLX, SAM and robot-attitude questionnaires; manual/robot comparisons. Physical movement, task mechanics, order and familiarity may explain stress/load differences. |
| Synchronization/quality | Timestamp-aligned multimodal collection, residual timing accuracy NR. Dry EEG and industrial movement artifacts; participants missing second day. Paper's EMG filter description extending to 500 Hz conflicts with 256 Hz acquisition and needs clarification. |
| Access/license/size/code | Public project/Zenodo route; exact dataset license, bytes, BIDS compliance and full preprocessing release NV. Methods/baseline descriptions available. |

Supports domain shifts from controlled cognition to interaction tasks, multimodal workload/self-report associations and two-day robustness. Cannot establish task-independent stress, robot safety or causal health benefits without stronger controls.

Descriptor/preprint already benchmarks stress/load classifiers and leave-one-subject-out evaluation. Per-subject feature/label normalization described in the baseline raises a deployment question: if held-out target statistics or labels are used, results are not zero-calibration generalization. At least one work verified, preprint/journal versions not double-counted. Opportunities concern movement-confound controls and calibration/transfer, subject to explicit access and normalization audits.

