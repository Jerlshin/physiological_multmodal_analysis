# Dataset-wide signal QC

**EMPIRICALLY VERIFIED IN THIS AUDIT.** Streamed all 16,038 relevant continuous files, yielding 180,221 recording/channel summaries. Parser failures: 0. Gzip/ZIP members were read to completion; BDF24 calibration, record lengths and channel rates were checked. One EEG recording is at most a bounded series of 32-second chunks; TSV parsing uses 8192-row chunks. No signal-format copy was created.

| experiment | status | modality | files | people | hours | basic_QC_flags |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | aligned_release_raw | gaze | 263 | 27 | 18.099 | 34 |
| 1 | aligned_release_raw | pupil | 263 | 27 | 18.099 | 44 |
| 1 | author_processed | gaze | 263 | 27 | 18.099 | 35 |
| 1 | author_processed | pupil | 263 | 27 | 18.099 | 39 |
| 2 | aligned_release_raw | ecg | 310 | 31 | 21.281 | 37 |
| 2 | aligned_release_raw | eeg | 291 | 30 | 19.856 | 0 |
| 2 | aligned_release_raw | eog | 283 | 29 | 19.342 | 0 |
| 2 | aligned_release_raw | gaze | 302 | 31 | 20.666 | 38 |
| 2 | aligned_release_raw | head | 302 | 31 | 20.666 | 5 |
| 2 | aligned_release_raw | pupil | 302 | 31 | 20.666 | 65 |
| 2 | author_processed | ecg | 283 | 29 | 19.342 | 0 |
| 2 | author_processed | eeg | 291 | 30 | 19.856 | 0 |
| 2 | author_processed | gaze | 297 | 31 | 20.323 | 33 |
| 2 | author_processed | head | 297 | 31 | 20.323 | 0 |
| 2 | author_processed | heart_rate | 283 | 29 | 19.342 | 0 |
| 2 | author_processed | pupil | 297 | 31 | 20.323 | 60 |
| 3 | aligned_release_raw | ecg | 321 | 29 | 27.873 | 0 |
| 3 | aligned_release_raw | eeg | 332 | 29 | 28.935 | 0 |
| 3 | aligned_release_raw | eog | 332 | 29 | 28.887 | 0 |
| 3 | aligned_release_raw | gaze | 323 | 29 | 28.050 | 43 |
| 3 | aligned_release_raw | head | 323 | 29 | 28.050 | 0 |
| 3 | aligned_release_raw | pupil | 323 | 29 | 28.050 | 76 |
| 3 | author_processed | ecg | 321 | 29 | 27.873 | 0 |
| 3 | author_processed | eeg | 322 | 29 | 28.063 | 0 |
| 3 | author_processed | gaze | 323 | 29 | 28.050 | 42 |
| 3 | author_processed | head | 323 | 29 | 28.050 | 0 |
| 3 | author_processed | heart_rate | 321 | 29 | 27.873 | 0 |
| 3 | author_processed | pupil | 323 | 29 | 28.050 | 75 |
| 4 | aligned_release_raw | ecg | 258 | 43 | 19.219 | 0 |
| 4 | aligned_release_raw | eeg | 256 | 43 | 19.095 | 1 |
| 4 | aligned_release_raw | eog | 258 | 43 | 19.219 | 0 |
| 4 | aligned_release_raw | gaze | 252 | 42 | 18.774 | 22 |
| 4 | aligned_release_raw | head | 252 | 42 | 18.774 | 5 |
| 4 | aligned_release_raw | pupil | 252 | 42 | 18.774 | 64 |
| 4 | aligned_release_raw | respiration | 258 | 43 | 19.219 | 0 |
| 4 | author_processed | breath_rate | 258 | 43 | 19.219 | 0 |
| 4 | author_processed | ecg | 258 | 43 | 19.219 | 0 |
| 4 | author_processed | eeg | 255 | 43 | 19.044 | 0 |
| 4 | author_processed | gaze | 247 | 42 | 18.354 | 17 |
| 4 | author_processed | head | 247 | 42 | 18.354 | 0 |
| 4 | author_processed | heart_rate | 258 | 43 | 19.219 | 0 |
| 4 | author_processed | pupil | 247 | 42 | 18.354 | 56 |
| 5 | aligned_release_raw | ecg | 288 | 48 | 24.972 | 0 |
| 5 | aligned_release_raw | eeg | 279 | 47 | 24.149 | 0 |
| 5 | aligned_release_raw | eog | 288 | 48 | 24.972 | 0 |
| 5 | aligned_release_raw | gaze | 288 | 48 | 24.974 | 32 |
| 5 | aligned_release_raw | head | 288 | 48 | 24.974 | 3 |
| 5 | aligned_release_raw | pupil | 288 | 48 | 24.974 | 77 |
| 5 | aligned_release_raw | respiration | 288 | 48 | 24.972 | 0 |
| 5 | author_processed | breath_rate | 288 | 48 | 24.972 | 0 |
| 5 | author_processed | ecg | 288 | 48 | 24.972 | 0 |
| 5 | author_processed | eeg | 279 | 47 | 24.149 | 0 |
| 5 | author_processed | gaze | 285 | 48 | 24.665 | 28 |
| 5 | author_processed | head | 285 | 48 | 24.665 | 0 |
| 5 | author_processed | heart_rate | 288 | 48 | 24.972 | 0 |
| 5 | author_processed | pupil | 285 | 48 | 24.665 | 72 |


The [deterministic config](../../../audit_config.json) defines basic screening: >1% nonfinite values, >95% exact zeros, whole-file flatness (more than eight EEG channels or all channels of another modality), and >50% eye invalid/corrected samples. The 16 Hz threshold is **flag only**. Saturation at export digital limits is tabulated but must not be equated with native ADC saturation: BDF exporters choose a per-file physical range. EEG amplitude/variance and PSD bands, 60 Hz and 16 Hz excess, channel availability and extreme variance ratios are retained.

These thresholds do not detect every artifact, guarantee neural origin, or certify clinical-grade ECG. [Channel tables](evidence/channel_qc.parquet), [numeric summary](evidence/modality_qc_summary.csv), [regional finite constant runs](evidence/physiology_flat_runs.parquet). EOG numbering is ch1–ch6, with no verified participant-specific anatomical montage; missing/flat channels can be counted, but their anatomical equivalence cannot be assumed. Head X/Y are tracker pixels and Z is camera distance in mm; this is not full calibrated 3-D pose. Exp.1 contains no head stream in the verified ZIP.

## Remaining measurement limits

NaNs cannot survive a BDF integer representation; zero NaN count in BDF does not prove acquisition/processing had no missing samples. Exact physical zeros may become one-LSB values during export. Native ADC clipping limits and EEG correction masks are not released. Canonical ECG/respiration sidecars declare mV while numerical excursions reach thousands of declared units; physical voltage scaling needs upstream confirmation. Do not silently convert units or infer cardiac morphology from an unverified scale.
