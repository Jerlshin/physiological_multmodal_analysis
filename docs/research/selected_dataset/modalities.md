# Modalities, signal meaning and transformations

Source keys: [S01–S06](evidence/source_registry.md). The term “raw” below distinguishes the **native sensor recording** from the **release's raw directory**. All released continuous streams are described as synchronized/resampled to 128 Hz, including those stored under raw. Native fidelity must not be inferred from the directory name.

## Availability and measurement physics

| Modality | Hardware/placement and measurement | Native rate | Documented experiments | Release/interpretation |
|---|---|---:|---|---|
| EEG | BioSemi ActiveTwo, 64-channel 10/10 scalp cap; ground near POz | 2,048 Hz | 2–5 | BDF at 128 Hz. Scalp electrical potentials, not direct attention labels or independently localized brain sources. Confirm reference, units/scaling and channel order per sidecar. |
| EOG | Six auxiliary electrodes above/below/lateral to both eyes | 2,048 Hz | 2–5 | Ocular electrical potentials used for EEG nuisance regression. Electrode-number-to-location mapping inconsistent across participants; cannot blindly pool numbered channels. |
| ECG | BioSemi electrodes below left collarbone and left lumbar region | 2,048 Hz | 2–5 | Electrical cardiac waveform; not HR/HRV itself. R-peaks estimated at native rate survive as timestamps even when waveform is 128 Hz. |
| Respiratory effort | SleepSense 1387 tension belt around chest, BioSemi acquisition | 2,048 Hz | 4–5 | Relative chest effort. No calibration to tidal volume, oxygenation or airflow established. |
| Gaze | EyeLink 1000, 35 mm lens, nine-point calibration | 500 Hz | 1–5 | Horizontal/vertical gaze in screen pixels; processed normalized and angular variants. Head-free setup and display geometry matter. |
| Pupil | EyeLink optical pupil-size estimate | 500 Hz | 1–5 | Tracker units; absolute diameter in mm not established. Processed variants include head-distance regression and normalization. |
| Head position | EyeLink forehead target | 500 Hz | 2–5 clearly described; 1 disputed | X/Y camera-sensor pixels, Z distance in mm. Not a calibrated 3D pose/IMU or face-video stream. |
| Blinks/saccades/fixations | EyeLink event detection from eye recordings | Discrete events | Where valid eye tracking exists | Detected events/derived annotations, not independent sensors or human ground truth. |

**OPEN QUESTION.** S02 lists only gaze/pupil in Exp. 1, while S05 and S06 raw-eye export imply head availability. Verify nonempty head channels rather than coding Exp. 1 head as present or absent from a summary. GSR is mentioned as a possible origin of 16 Hz contamination on the website, but no released GSR/EDA modality was established. Stimulus videos are visual input, not recordings of participants. [INF-009]

## Six categories that must remain distinct

| Category | BBBD examples | What must not be inferred |
|---|---|---|
| RAW SIGNALS | Native BioSemi voltage and EyeLink measurements; release raw directory contains aligned/resampled versions | Release “raw” is not necessarily 2,048/500 Hz acquisition-original data |
| AUTHOR-PROCESSED SIGNALS | Filtered/cleaned EEG/ECG, interpolated gaze/pupil; head-regressed pupil | Cleaned samples are not all observed samples; transformations can remove meaningful covariance |
| DERIVED FEATURES | R-peak/event times, HR, breath rate, saccade/blink/fixation rates, normalized pupil; study-specific ISC, CorrCA, PCA, alpha power | ISC and HR are computations, not experimental truth; paper features may not be released as ready-made labels |
| GROUND-TRUTH LABELS | Correct-answer keys operationalize quiz scoring; verified stimulus/session identity provides task annotations | Neither supplies a continuous latent-attention trace; ASRS threshold is not diagnostic ground truth |
| EXPERIMENTAL CONDITIONS | Attend, arithmetic distraction, attentive second block, incentive/question-preview repeat | Manipulation assignment is not proof of compliance or a pure construct-specific state |
| BEHAVIORAL OUTCOMES | Quiz responses and scores; digit-span performance; self-reported GPA and questionnaire scores (distinct measurement types) | Immediate quiz score is not durable learning gain, general intelligence or clinical severity |

Sources: S01 preprocessing/data records; S06 schemas; P01–P04 methods. [INF-010]

## Author preprocessing and important implementation differences

**VERIFIED FACT — documented EEG pipeline.** S01 specifies DC-coupled acquisition with hardware fifth-order sinc/CIC decimation (~400 Hz bandwidth at 2,048 Hz), digital 0.05 Hz high-pass plus 60 Hz notch using fifth-order Butterworth/SOS filtering, robust PCA, low-pass 64 Hz, downsampling to 128 Hz, EOG least-squares regression and channel/sample artifact interpolation. Samples beyond four median-centered IQRs plus ±40 ms are corrected using neighboring electrodes. S01 reports corrected proportions: Exp. 2 0.84% ± 2.62%, Exp. 3 1.75% ± 6.09%, Exp. 4 0.32% ± 0.84%, Exp. 5 0.62% ± 1.83%. These are average artifact corrections, not guarantees of artifact-free files.

**VERIFIED FACT — code differs.** S06 `preprocessEEGdata.m` sets high-pass **0.3 Hz**; P04 specifies **0.5 Hz**; S01/P03 specify **0.05 Hz**. S06 makes RPCA/EOG steps option-dependent, changes IQR multiplier depending on RPCA, and can replace remaining NaNs with zeros. The main descriptor's hardware description also differs from the 0.016–250 Hz wording in earlier papers. The actual pipeline used for each release derivative is OPEN until release provenance is checked. [INF-011; code audit]

**VERIFIED FACT — cardiac processing.** S01 describes 0.5 Hz high-pass, 60 Hz notch, peak detection and manual correction. The inspected ECG function instead builds a 0.5–25 Hz band-pass, has participant-dependent peak-height thresholds and rejects inferred rates outside 40–160 bpm. Manual GUI calls are commented while annotation files can be loaded. `HRV` output is initialized to zeros in that function; it is not a valid computed variability feature. Peak timestamps can differ from the visible downsampled maximum for legitimate native-rate/filtering reasons. [S01; S06; INF-012]

**VERIFIED FACT — eye processing.** Author-reported outliers are four-IQR deviations after a 200 ms median detrend; blinks/artifacts with ±100 ms padding are linearly interpolated. Across 1,455 files, corrected fractions average **22% ± 19% gaze** and **32% ± 25% pupil**. This includes blink buffers and tracking failures. S06 additionally exposes option-dependent buffers, masks, morphological closing and interpolation. Its discrete writers export gaze/pupil interpolation intervals. Archive presence and coverage of these masks remain unverified. [S01; S06]

**VERIFIED FACT — derived eye/head features.** The code divides gaze by display resolution, creates angular estimates using recorded resolution, regresses pupil on head Z, then normalizes by its 95th percentile. Event rates use inverse inter-event intervals with interpolation and nearest extrapolation at endpoints, not necessarily count-per-fixed-window rates. “Head velocity” uses the norm of the imaginary Hilbert transform, with log/square-root variants; it is not the ordinary time derivative of physical displacement. One gaze-variation expression mixes differently scaled coordinate columns; audit its units before use. [S06 `postprocessEyelinkData.m`; INF-013]

**VERIFIED FACT — respiration processing.** `preprocessRespirationData.m` may invert polarity using mean minus median; it detects peaks after 0.05–25 Hz fifth-order Butterworth `filtfilt`, enforces a 30-breath/min minimum peak-distance setting, filters calculated rates outside 4–60/min, and interpolates/extrapolates the resulting rate. Its “volume” variable is an absolute Hilbert envelope, not calibrated volume. The returned first waveform column is polarity-adjusted input, while peak detection uses a filtered copy. Low-rate/boundary/short-record behavior needs inspection. [S06; INF-014]

## File layout and metadata interpretation

Each experiment is organized separately:

```text
experimentN/
  dataset_description.json
  participants.tsv, participants.json
  phenotype/              # quiz, ASRS, digit-span and other available questionnaires
  sub-XX/ses-YY/
    eeg/                  # BDF, channel/electrode/coordinate/event metadata
    beh/                  # ECG, EOG, respiration TSV/JSON
    eyetrack/             # gaze, pupil, head TSV/JSON
  derivatives/sub-XX/ses-YY/
    eeg/                  # author-processed BDF
    beh/                  # processed ECG, R-peak/breath events, rates
    eyetrack/             # processed signals, eye events/rates, interpolation intervals
```

S01 states non-EEG raw TSVs are gzip-compressed and headerless; derived TSVs uncompressed with headers. Generic READMEs/notebook patterns sometimes expect compressed derived files. Therefore use actual extensions plus JSON `Columns`, `SamplingFrequency`, `StartTime` and `Units`; never apply one generic parser to all versions. BDF export pads to whole one-second records using zeros; use events/valid-sample bounds to exclude padding. The code describes `DatasetType=derivative` and hardcodes “1.0.0” in generated descriptions despite raw/derived directories, another reason to pin the actual archive rather than regenerate release identity. [S01; S06; INF-015]

**OPEN QUESTIONS.** Complete per-file channel units and voltage scaling, EEG reference history, participant-specific EOG mapping, native timestamp availability, exact anti-alias transfer functions, mask coverage and which feature variants were actually exported require archive-level checking. Do not fill these fields from filenames alone.
