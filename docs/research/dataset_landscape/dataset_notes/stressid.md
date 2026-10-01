# StressID

**Disposition: credible stress/audio–video–physiology alternative; lower verification depth than finalists.**

Sources: [Chaptoukaev et al., NeurIPS Datasets and Benchmarks 2023](https://proceedings.nips.cc/paper_files/paper/2023/file/5f09bfe6730e9627a9f800d01a8ad5cd-Paper-Datasets_and_Benchmarks.pdf); [official project](https://project.inria.fr/stressid/); [author code](https://github.com/robustml-eurecom/stressID).

| Item | Evidence / limitation |
|---|---|
| Cohort/protocol | 65 participants; cognitive, emotional and speech stressor tasks with baseline/recovery. Detailed age/sex distribution, exact task count and duration require primary technical documentation verification. |
| Modalities | ECG, EDA, respiration plus audio/video; no EEG. Sampling rates and native/raw file inventory not independently verified here. |
| Labels/controls/repeats | Self-report/condition stress labels, repeated tasks within subject, task/participant identifiers. Speaking and movement differ systematically by task. Longitudinal repeat visits not established. |
| Synchronization/quality | Multimodal alignment described at resource level; residual precision and exact missingness not verified. Do not adopt third-party delivery-specific exclusion lists as official facts. |
| Access/license/size/code | Research license/request route via official project; no request submitted. Data terms/bytes NV. Code explicitly BSD-3; this is not the data license. Feature extraction, classification and label-analysis notebooks available. Not BIDS verified. |

Supports multimodal laboratory stress and comparisons among stressor families. Cannot establish clinical stress diagnosis or unconstrained workplace performance; a classifier may learn speech/task identity.

The original NeurIPS work already includes classification and fusion/label analyses. At least one peer-reviewed work verified; reuse saturation not fully resolved because direct project access was limited. Potential task-held-out robustness and missing-modality work require a focused follow-up. The 65-person sample is useful, but incomplete access/metadata verification and absence of EEG make it less compelling than the selected brain–body candidates.

