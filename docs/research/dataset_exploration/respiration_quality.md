# Respiration and auxiliary streams

**EMPIRICALLY VERIFIED IN THIS AUDIT.** Respiration is confined to experiments 4–5. Raw belt-waveform and derived breath-rate presence, amplitude ranges, whole-file variance, finite/zero values, exact constant runs and low-frequency PSD were audited. [Respiration/channel summaries](evidence/channel_qc.parquet), [regional flat runs](evidence/physiology_flat_runs.parquet), [breath peak timestamps](evidence/peak_qc.parquet).

| experiment | status | modality | files | people | hours | basic_QC_flags |
| --- | --- | --- | --- | --- | --- | --- |
| 4 | aligned_release_raw | respiration | 258 | 43 | 19.219 | 0 |
| 4 | author_processed | breath_rate | 258 | 43 | 19.219 | 0 |
| 5 | aligned_release_raw | respiration | 288 | 48 | 24.972 | 0 |
| 5 | author_processed | breath_rate | 288 | 48 | 24.972 | 0 |


| experiment | files | peak_count | duplicates | median_file_breaths_per_minute | min_file_breaths_per_minute | max_file_breaths_per_minute | max_broad_interval_failure_fraction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4 | 258 | 19890 | 0 | 17.764 | 8.573 | 21.907 | 0.000 |
| 5 | 288 | 26792 | 0 | 18.754 | 11.224 | 26.352 | 0.000 |


The 8-second PSD estimator provides only coarse respiration-frequency characterization: its 0.125 Hz resolution limits slow-rate discrimination. Derived breath-peak intervals provide a separate author-processed rate proxy. The exporter/pipeline uses a chest-tension belt and Hilbert-envelope “volume”; neither is calibrated tidal volume. Do not apply ECG plausibility thresholds to breath peaks merely because both are stored in the same peak table. Native belt saturation limits and exactly executed peak/filter options remain unknown.

EOG and head coverage is in [signal QC](signal_quality.md). EOG six-channel numbering does not supply an anatomical montage. Head position is tracker target geometry, not orientation/pose; transformed “velocity” semantics in the pinned code are unconventional and were not treated as ordinary derivatives of 3-D displacement.
