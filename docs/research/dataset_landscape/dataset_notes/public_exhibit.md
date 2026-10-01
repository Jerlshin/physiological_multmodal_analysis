# Public-exhibit emotion physiology dataset

**Disposition: strongest scale/diversity challenge to laboratory affect datasets; not primary for precise multimodal neuroscience.**

Sources: [Girgis, Lavoie & Blain-Moraes, Scientific Reports, 20 April 2026](https://doi.org/10.1038/s41598-026-48250-7); [official OSF](https://doi.org/10.17605/OSF.IO/PN9RQ).

| Item | Evidence / limitation |
|---|---|
| Cohort | Public Montreal science exhibit, 2017–March 2025. Headline nearly 25,000 visitors/~80,000 instances; results report **21,539 with at least one quality signal**, **7,646 with all three**, yielding 23,911 complete signal instances. Visits are not verified globally unique people; repeat attendance possible. |
| Demographics/protocol | Broad age bands from ≤5 to ≥50 and self-reported sex; unattended viewing of four randomly selected short clips from a 15-clip pool (11–42 s), brief baseline. |
| Signals/rates/duration | BVP 75 Hz, EDA and temperature 15 Hz; processed together at 15 Hz, often 10 s analysis windows. No EEG/eye data. Total retained duration NV; summed video instances do not equal independent subjects. |
| Labels | Love/calm/sadness/fear/frustration/other and 1–5 intensity. Very short self-report-driven elicitation. |
| Data/sync/artifacts | Contact sensors with substantial dropout, saturation and quality-tail exclusions. Synchronized export, quantitative residual error NR; raw native-rate availability and persistent person IDs NV. |
| Access/license/size/code | OSF open route; data license/full bytes and complete code availability need repository inspection. Article CC BY-NC-ND: link/describe figures rather than adapt them. Non-BIDS. |

Supports population heterogeneity, measurement missingness and falsification of easy physiological-emotion assumptions. Large scale and broad ages are unusual. Cannot safely claim universal emotion signatures, high-resolution HRV from downsampled short segments, independent persons across all visits or precise neural mechanisms.

The original paper already tests emotion classifiers, intended-video versus self-report labels and subgroup/quality filtering. It finds weak generalizable emotion discrimination overall despite some easier video-specific contrasts. At least this empirical descriptor verified; no independent reuse verified. Quality filtering and resampling/oversampling order require audit before adopting benchmark splits. Useful opportunities concern selection bias, calibration and informative failure; these are not automatically solved by the large headline N.

