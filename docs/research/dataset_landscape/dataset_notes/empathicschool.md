# EmpathicSchool

**Disposition: useful stress/video–wearable candidate; small and already benchmarked.**

Sources: [Hosseini et al., Scientific Data, 20 November 2025](https://doi.org/10.1038/s41597-025-05812-0); [author repository](https://github.com/CPHSLab/EmpathicSchool); [linked archive](https://doi.org/10.5281/zenodo.7372497). Repository/collection predates descriptor.

| Item | Evidence / limitation |
|---|---|
| Cohort/protocol | 31 recruited, one withdrew; 30 adults 21–35, mean 25.3 ± 4.3, recruited at Louisiana/Tampere. Sex breakdown NV. Nine stress/recovery tasks; roughly 40 h total reported. T9 recovery absent for S7–S30. |
| Signals/rates | E4 BVP 64, acceleration 32, EDA/temperature 4, HR 1 Hz and IBI; face video 30 fps plus landmarks/AUs/emotion-model outputs. Raw videos only where consent permits. No EEG. |
| Labels/repeats | Stress self-report every 2 min, task NASA-TLX; one visit with repeated tasks. Facial emotion probabilities are estimated features, not independent labels. |
| Data/sync/quality | Raw E4, consenting video and processed features; timestamps and task trimming (30 s each end). Common resampling does not establish added sensor information. Motion/contact, severe class imbalance and consent/task missingness. Not BIDS. |
| Access/license/size/code | GitHub/archive route and feature/preprocessing code; exact release license, bytes and video coverage NV. Detailed descriptor including availability table. |

Supports self-reported stress in task conditions and face–wearable complementarity. Cannot establish real-time objective emotion, clinical stress diagnosis or independent validation when facial-model outputs are mistaken for ground truth.

The descriptor already includes feature fusion, several classifiers, leave-one-subject-out evaluation, sequence/change-point analyses and imbalanced-label handling. At least descriptor and earlier linked archive/code identified; archive is not another publication. Generic stress fusion is occupied. Potential lies in consent/missingness and task-held-out robustness, but two-site/protocol differences, only 30 people and lost recovery tasks limit strong claims. Audit overlap/SMOTE placement and group all windows by person.

