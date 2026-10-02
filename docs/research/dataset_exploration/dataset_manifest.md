# Canonical dataset manifest

**EMPIRICALLY VERIFIED IN THIS AUDIT.** [canonical_manifest.parquet](evidence/canonical_manifest.parquet) contains 16,038 physical continuous-signal records and 3,346 explicit absent-modality/derivative placeholders. [exposure_tensor.parquet](evidence/exposure_tensor.parquet) contains 1,474 design-expected person/video exposures. [stimulus_map.csv](evidence/stimulus_map.csv) maps local task IDs to 11 canonical YouTube identities.

| experiment | people | design_exposures | videos | valid_quiz_person_video_pairs |
| --- | --- | --- | --- | --- |
| 1 | 27 | 270 | 5 | 135 |
| 2 | 31 | 310 | 5 | 155 |
| 3 | 29 | 348 | 6 | 173 |
| 4 | 43 | 258 | 6 | 129 |
| 5 | 48 | 288 | 3 | 144 |


Identifiers use `exp-N:sub-XX`. The record key is experiment + participant + session + local stimulus + representation + modality/member path. Each physical record includes canonical video, exposure number, condition, file bytes, rate evidence, sample counts, observed/QC/valid durations, channel names, units, NaN/Inf/zero counts, padding, correction/event/quiz/metadata availability, QC reasons, and keyed outcome reference/values. `outcome_id` joins the separate [quiz_video_outcomes.parquet](evidence/quiz_video_outcomes.parquet). Traits remain a keyed participant table. This normalized relation prevents duplicating quiz items across modality rows while preserving outcome availability.

Sampling is 128 Hz in inspected BDF headers/raw sidecars. Derivative TSV rates inherit the documented export grid and counterpart timing; absent derivative sidecars are recorded, not invented. Units for derivatives are explicitly unverified. All continuous raw/author-processed streams for EEG, ECG, EOG, gaze, pupil, head, respiration and HR/breath rates were streamed. Blink/saccade/fixation presence is inventoried; those event detectors were not independently validated.

`data_role` separates aligned raw signals, author-processed signals and derived HR/breath-rate features. Questionnaire availability is resolved from observed participant/video rows: complete ASRS item coverage, nonmissing digit-span score or at least one observed video-feedback field. These three fields are also separate; availability does not establish pre-exposure chronology. Final `peak_qc.parquet` uses distinct respiratory interval/rate fields; old experiment peak checkpoints are intermediate input, not the canonical semantic table.

`invalid_sample_bits` is a compact, little-endian packed Boolean invalid/correction union, with length `qc_sample_count`. [masks_expN.parquet](evidence/masks_exp4.parquet) preserve original correction intervals as seconds, not discarded labels. Valid durations count finite/range-valid samples minus released eye-mask unions. EEG's unreleased correction history is unknown. Whole-video usability is provisional; a pass does not certify a neural or clinical measurement.

No native 2048/500 Hz arrays, original clock-fit logs, acquired stimulus movies/hashes or independent acquired-video order log were found in the archives. Canonical URL identity is stronger than local stimulus numbering but does not establish byte-identical acquired trims.
