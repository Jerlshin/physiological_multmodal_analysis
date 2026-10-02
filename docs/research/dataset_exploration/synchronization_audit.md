# Synchronization and timing audit

**EMPIRICALLY VERIFIED IN THIS AUDIT.** Raw non-EEG modality boundary spread has median 0.023438s, 95th percentile 0.039062s and maximum 0.039062s across 1457 exposures. Event-trimmed EEG minus median other raw duration has median -0.015625s, 95th absolute percentile 0.039062s and maximum absolute 0.039062s. [Per-exposure boundaries](evidence/timing_boundaries.parquet).

The exported events contain start/end markers generated from array length. End onset = n_samples/128 is an **exclusive** boundary; its one-sample marker duration is not an additional recorded sample. BDF records extend to whole seconds; all inferred padded rows are checked against one export-calibration LSB. `[RecordingDuration=0.5]` is stale/malformed metadata and not an actual recording length. Finite sample-count mismatch is retained, not rounded away.

**OPEN QUESTION.** Native shared flash/beep trigger sequences, clock-fit coefficients and residuals are not present in these event files. Two synthetic array-boundary markers do not permit dropped-native-trigger, clock-drift or residual-latency estimation. ECG/R-peak agreement verifies those two related derivatives, not EEG–eye device alignment. No millisecond precision is inferred from a common 128 Hz grid.

**OUR INFERENCE — recommendation:** whole-video aggregation is the safest supported analysis, after excluding absent/invalid regions. Multi-second windows may be explored with boundary/mask sensitivity and explicit unmeasured alignment uncertainty; exact safe window length cannot be certified. Sub-second coupling, phase, directional or lag claims are insufficiently verified. Reliable item-to-content timestamps are also absent, constraining C05 independently of alignment.
