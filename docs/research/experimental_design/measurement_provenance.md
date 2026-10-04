# M01 — Measurement provenance: bounding OQ-06 for the selected analysis

2026-10-04. **Verdict: OQ-06 is BOUNDED for the frozen whole-video feature route. It is not resolved.** No new forensic reconstruction was attempted. This gate asks only what the selected analysis needs: does the open provenance threaten (a) leakage, (b) the measured construct, or (c) absolute-unit claims? A design response is fixed for each threat.

Evidence classes: **F** fact, **L** literature, **I** inference/decision, **U** unresolved.

## What remains open (inherited, F)

From [gate closure](../dataset_exploration/gate_closure.md), the following are still open:

- the executed EEG high-pass, reference, RPCA/EOG/interpolation options and their fit scope;
- the eye blink-buffer, interpolation and pupil-transform variant;
- native resampling and clock lineage;
- physical ECG and belt calibration.

The ECG filter is numerically identified: causal fifth-order 0.5–25 Hz in all 1,140 testable pairs. The released aligned raw exports cannot recover discarded native samples.

## New evidence: fit scope of every inspected preprocessing routine (F for code text; I for execution)

| Routine (pinned `5109afa` unless noted) | Operations that estimate anything from data | Scope of every estimate | Uses labels or other people? |
|---|---|---|---|
| `preprocessEEGdata.m` | EOG least-squares regression (outlier-masked); log-power IQR channel rejection; RPCA; IQR artifact masking with a ±40 ms extension; spatial interpolation of bad samples | The single `samples × channels` array passed in | No |
| Historical P03 `preprocessEEGdata.m` (OSF d4k3q) | Same operations; 0.5 Hz high-pass | Same single array | No |
| `preprocessEyelinkData.m` | EDF blink intervals plus buffers; 4×IQR pupil outlier detection around a running median; interpolation; median filtering | Single recording | No |
| `postprocessEyelinkData.m` | Pupil regression on head distance; 95th-percentile normalization; saccade/blink/fixation rates | Single recording | No |
| `preprocessECGdata.m` | `findpeaks` with within-recording percentile height thresholds; rate rejection | Single recording | No |

**I.** No inspected source contains a cross-participant, cross-content or outcome-dependent operation. What stays unknown is whether the array passed in was one exposure or a concatenation of one person's session(s). The worst case is therefore a **within-person, label-free** normalization that may use the same person's later recordings, such as the arithmetic re-viewing block.

This bound rests on code inspection: the pinned tree is not certified as the executed recipe ([gate closure](../dataset_exploration/gate_closure.md)). The residual risk is an undocumented pooled step that no inspected source suggests. It is recorded as U, not dismissed.

## Threat classification and design response

| Open item | (a) Leakage across people/content or from outcomes | (b) Construct threat | (c) Units | Frozen response |
|---|---|---|---|---|
| EEG options/fit scope | Bounded: within-person, label-free (above) | RPCA/EOG regression may remove or reshape neural signal; 16 Hz contamination in E4/E5 | Header µV, but gain chain uncertain | Primary features are **scale-free** (relative log band power, CorrCA-ISC). Claims concern the *released processed measurement*, not native neural quantities. Prespecified sensitivity: a documented raw-export route (below). Beta band excluded because of 16 Hz |
| Possible within-person use of later blocks | Not leakage of labels or of other people | Minor chronology impurity for a strict post-viewing forecast | — | Disclosed limitation. The raw-export sensitivity route is strictly per exposure |
| Eye buffers/interpolation | Bounded: within recording | Interpolated spans are not observed behaviour | Gaze in screen pixels (calibrated geometry) | Gaze features computed on **non-corrected samples only**, using released correction intervals. Correction fraction enters Q, not X |
| Pupil export variant (column 1; not the 95th-percentile-normalized one; head-regression history unknown) | Bounded | Absolute pupil level is luminance-, distance- and calibration-dependent, so person-level comparisons are not interpretable | Arbitrary units | **No absolute pupil level.** Only within-recording scale-free dynamics and ISC. Pupil becomes a **secondary sensor block** (below) |
| Native clock/resampling | n/a | Sub-second lags are not certified (boundary spread ≤ 0.04 s) | — | Whole-video aggregates only. No lag, phase or directional features. ISC computed on slow signals or on the CorrCA summary as in P03/P04 |
| ECG/R-peaks | Bounded | Manual peak history unknown | mV unverified | Only timing-derived features (HR, RMSSD from released peaks, HR-ISC). No amplitude features |
| Respiration, head, EOG | — | Uncalibrated belt; head is motion; EOG is upstream cleaning input | Uncalibrated | **Excluded** from X. Respiration has no defensible rationale ([B18](../research_gap/candidate_space.md)) |

## Frozen feature route

1. **Primary:** author-processed released derivatives (EEG BDF processed, gaze/pupil processed, R-peak timestamps). This is the publicly used BBBD measurement whose validity G01 questions.
2. **Prespecified sensitivity — raw-export route.** It is computed strictly per exposure:
   - **EEG** from released *raw* aligned BDF: 0.5 Hz fifth-order high-pass and 60 Hz notch (zero-phase); common-average reference; per-recording least-squares EOG regression using the released raw EOG channels; samples beyond 4×IQR set missing with a ±40 ms extension; features from the remaining samples.
   - **Gaze/pupil** from raw exports, excluding released correction intervals, with no interpolation.

   A conclusion that changes direction between the two routes is reported as provenance-dependent.
3. The feature dictionary is fixed in [protocol.md](protocol.md) §6. It has 6 core reference-free features and 3 core synchrony features, plus 1 pupil feature of each kind. None was chosen by association with outcomes.

## Primary sensor set: EEG + ECG + gaze; pupil secondary (decision EDD-003)

**I.** The inherited "eye = gaze AND pupil" policy makes pupil QC the main driver of complete-case loss. In first-view E3+E4, requiring pupil removes 11 people and 43 cells (68/259 → 57/216; [case flow](evidence/case_flow.csv)).

The decision rests on measurement grounds, fixed before any physiology–outcome computation:

- pupil export semantics carry the most specific unresolved OQ-06 item;
- pupil correction burden is the highest of all streams (mean ≈ 0.34 versus 0.22 for gaze, [eye quality](../dataset_exploration/eye_quality.md));
- absolute pupil level is not interpretable across people.

**Pupil is therefore a secondary sensor block,** evaluated on the four-sensor set (57/216/8) together with a re-estimate of the primary contrast there. The precision simulation independently shows the larger core set to be more informative ([precision](precision_and_independence.md)). That is a supporting consideration, not the reason.

## What OQ-06 still forbids

- Absolute-amplitude or physical-unit claims.
- "Neural" or "autonomic mechanism" language beyond "the released processed measurement".
- Any sub-second timing, lag or direction claim.
- Treating author-interpolated spans as observed behaviour.

Before any publication claim, the [author query](../dataset_exploration/evidence/author_query_draft.md) remains the authoritative route. It is still unsent: sending requires the user's authorization.
