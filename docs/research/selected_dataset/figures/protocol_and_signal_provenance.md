# What survives from acquisition to a valid research target?

Sources: S01 acquisition/preprocessing; S06 pinned code; P01–P04. This is a documented transformation map, not an assertion that native files or every mask are released. Discrete event timestamps do not become raw signals simply because they are precise.

```mermaid
flowchart TD
    Stim[Educational video: shared stimulus clock] --> Trig[Onset/offset flash and beep + digital triggers]
    NativeB[BioSemi: EEG / EOG / ECG / respiration
2048 Hz native] --> Clock[Linear timestamp mapping
offset + drift correction]
    NativeE[EyeLink: gaze / pupil / head
500 Hz native] --> Clock
    Trig --> Clock
    Clock --> Raw[Aligned / clipped / resampled 128 Hz
release RAW directory]
    NativeB --> Peaks[Native-rate filtered ECG
detected / corrected R-peak times]
    Raw --> Proc[Author processing: filtering / RPCA / regression
interpolation and normalization]
    Proc --> Deriv[AUTHOR-PROCESSED continuous signals]
    Peaks --> Feat[DERIVED features: HR / rates / event times]
    Deriv --> Rep[Study representations: ISC / CorrCA / PCA]
    Mask[Artifact / interpolation masks
coverage to verify] -.-> Proc
    Instr[EXPERIMENTAL CONDITIONS
instructions + exposure + order] --> Join[Participant / experiment / video / exposure join]
    Quiz[BEHAVIORAL OUTCOMES
quiz responses, traits, GPA] --> Join
    Key[SCORING REFERENCE
answer keys + denominator] --> Quiz
    Deriv --> Join
    Feat --> Join
    Rep --> Join
    Join --> Audit[Verified target and predictor semantics
then next-stage problem formulation]
```

The ordering is conceptual: native peak detection and preprocessing can occur before final resampling. The exported raw signal is not acquisition-original, and no continuous ground-truth attention signal appears in this chain. Residual timing precision, exact derivative options and label joins remain audit gates.
