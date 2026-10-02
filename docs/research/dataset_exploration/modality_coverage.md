# Modality coverage and provisional usability

**EMPIRICALLY VERIFIED IN THIS AUDIT.** Counts are experiment-qualified people and person/video exposures, never windows. `eye` requires both author-processed gaze and pupil. EEG/ECG/head use author-processed files; EOG/respiration use released raw files because corresponding cleaned waveform derivatives are not supplied. Raw and processed coverage are also retained separately.

| modalities | stage | requires_valid_quiz | people | person_video_exposures | videos | valid_hours |
| --- | --- | --- | --- | --- | --- | --- |
| eeg | present | False | 149 | 1147 | 11 | 90.991 |
| eeg | present | True | 149 | 578 | 11 | 47.462 |
| eeg | basic_qc | False | 149 | 1147 | 11 | 90.991 |
| eeg | basic_qc | True | 149 | 578 | 11 | 47.462 |
| ecg | present | False | 149 | 1150 | 11 | 91.407 |
| ecg | present | True | 149 | 580 | 11 | 47.666 |
| ecg | basic_qc | False | 149 | 1150 | 11 | 91.407 |
| ecg | basic_qc | True | 149 | 580 | 11 | 47.666 |
| eye | present | False | 177 | 1415 | 11 | 70.236 |
| eye | present | True | 177 | 708 | 11 | 37.648 |
| eye | basic_qc | False | 149 | 1099 | 11 | 66.051 |
| eye | basic_qc | True | 146 | 575 | 11 | 35.911 |
| eeg+ecg | present | False | 148 | 1121 | 11 | 88.875 |
| eeg+ecg | present | True | 148 | 567 | 11 | 46.590 |
| eeg+ecg | basic_qc | False | 148 | 1121 | 11 | 88.875 |
| eeg+ecg | basic_qc | True | 148 | 567 | 11 | 46.590 |
| eeg+eye | present | False | 148 | 1117 | 11 | 57.407 |
| eeg+eye | present | True | 148 | 559 | 11 | 30.636 |
| eeg+eye | basic_qc | False | 123 | 875 | 11 | 54.110 |
| eeg+eye | basic_qc | True | 121 | 453 | 11 | 29.170 |
| ecg+eye | present | False | 148 | 1118 | 11 | 56.537 |
| ecg+eye | present | True | 148 | 559 | 11 | 30.350 |
| ecg+eye | basic_qc | False | 122 | 857 | 11 | 53.045 |
| ecg+eye | basic_qc | True | 120 | 447 | 11 | 28.800 |
| eeg+ecg+eye | present | False | 147 | 1093 | 11 | 56.092 |
| eeg+ecg+eye | present | True | 147 | 550 | 11 | 30.105 |
| eeg+ecg+eye | basic_qc | False | 122 | 854 | 11 | 52.884 |
| eeg+ecg+eye | basic_qc | True | 120 | 444 | 11 | 28.639 |
| eeg+ecg+eye+respiration | present | False | 89 | 520 | 6 | 27.482 |
| eeg+ecg+eye+respiration | present | True | 89 | 259 | 3 | 14.415 |
| eeg+ecg+eye+respiration | basic_qc | False | 72 | 401 | 6 | 25.985 |
| eeg+ecg+eye+respiration | basic_qc | True | 70 | 200 | 3 | 13.597 |


Valid hours are exact sample-mask unions over the common **released** 128 Hz grid, including event-trimmed EEG bounds; this does not establish latent cross-device synchronization precision. Counts with valid quiz include direct test chronology only: session1 in 1–3, session2 stim01–03 in 4, session2 in 5. Exp.5 first viewing has the later final outcome as an explicitly indirect relation and is not counted twice.

Per-experiment complete EEG+ECG+eye+quiz after provisional QC:

| experiment | people | person_video_exposures | videos | valid_hours |
| --- | --- | --- | --- | --- |
| ALL | 120 | 444 | 11 | 28.639 |
| 1 | 0 | 0 | 0 | 0.000 |
| 2 | 26 | 120 | 5 | 6.518 |
| 3 | 24 | 124 | 6 | 8.524 |
| 4 | 33 | 92 | 3 | 6.183 |
| 5 | 37 | 108 | 3 | 7.414 |


[All combinations and experiments](evidence/modality_intersections.csv); [physical raw/processed coverage](evidence/physical_coverage.csv); [missing-file placeholders](evidence/missing_files.parquet). Presence, intrinsic numerical validity, correction burden and eligibility are distinct. Current QC thresholds were set for this audit, not tuned against outcomes; they are candidates for later sensitivity analysis, not a frozen paper inclusion policy.
