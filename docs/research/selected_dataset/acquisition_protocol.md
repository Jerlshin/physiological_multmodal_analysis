# Acquisition and experiment reconstruction

Source IDs resolve in the [registry](evidence/source_registry.md). The following is the best-supported reconstruction from S01 Methods, P01/P03 Methods, official experiment descriptions and S06 export code. Conflicting generic README text is not treated as protocol authority.

## Shared setting and purpose

**VERIFIED FACT.** Adults watched short publicly available educational videos individually, generally in a sound-controlled booth with a 27-inch 1920×1080 monitor approximately 60 cm away, stereo speakers described as separated by approximately 60°, ambient LED lighting and white surrounding fabric. The descriptor says no chin rest. P02's historical methods describe a 19-inch/headphone arrangement; this is an unresolved acquisition-description discrepancy for the overlapping video cohort, not a reason to overwrite the current descriptor. Eye calibration used nine positions and recalibration when drift exceeded about 2°. P01 describes drift checks after stimuli; the descriptor refers to condition-level checks. [S01; P01; P02]

## Viewing blocks and tests

| BBBD experiment | Block/session 1 | Intermediate testing/instructions | Block/session 2 | Scientifically interpretable contrast |
|---|---|---|---|---|
| 1, N=27 | Five videos, intentional learning | Informed about quizzes; questions after each video | Same five, same order, silent serial subtraction | Attentive first exposure vs arithmetic during repeated exposure |
| 2, N=31 | Same five, incidental learning | Domain-knowledge questionnaire before viewing; unannounced cumulative memory questions after attentive block | Same five, same order, subtraction | Same compound contrast; quiz concerns preceding attentive exposure |
| 3, N=29 | Six videos, intentional learning, diverse presentation styles | Told about tests; questions after videos | Same six in same order, subtraction | Compound attention/order/repetition contrast, plus stimulus/style variation |
| 4, N=43 | Three videos, attentive: local stim04–06 | No arithmetic; incidental protocol | Three different videos, attentive: stim01–03; tested on this latter set | Different content and block order; not an attend/distract pair |
| 5, N=48 | Three videos, initial incidental viewing: stim01–03 | Reward per correct answer announced and upcoming questions previewed | Same three viewed again with incentive/intention, then tested | Combined reward, preview, intention, order and repeated exposure |

For 1–3, distraction is silent repeated subtraction of seven from a randomly selected prime between 800 and 1,000. There is no verified time-resolved record of whether subtraction was actually performed. Instructions are experimental conditions, not measured attention states. P01 reports randomized video, question and answer-option order; repeated distracted viewing uses the same subject-specific video order. This does **not** counterbalance condition order. [P01 Methods; S01]

**OPEN QUESTION — allocation (INF-006).** The descriptor figure describes intervention/control randomization, but the inspected materials do not establish a reproducible allocation sequence or balance checks. S06 loads one upstream `experiment_4/Experiment_6_demographics.mat` and partitions participants by `doIntervention` into released Experiments 4 and 5. This is evidence of a shared source experiment, not evidence that all Exp. 5 participants were randomized internally. Since Exp. 4 sees different second-block videos while Exp. 5 repeats its first-block videos, a simple between-group contrast does not isolate reward. Verify allocation, exposure and test chronology before causal language.

**VERIFIED FACT — conflicting readmes.** S06's Exp. 4 README correctly lists two attentive blocks with different stimuli, then pastes text describing distracted repeated viewing; its opening also says five videos. The descriptor, experiment-specific table and export branch support the six-video/two-attentive-block interpretation. Preserve the contradiction and test filenames/event logs against it. Do not assign all `ses-02` records the label “distract.” [S06; INF-007]

## Stimuli and content overlap

Eleven unique video identities are listed in [stimuli.csv](evidence/stimuli.csv), transcribed from S02 Table 2. Published durations may differ from the exact trimmed recordings; use actual event boundaries, not the current YouTube player or a rounded table duration. The mapping crosses experiments, so “hold out experiment” does not necessarily mean “hold out content.”

| Video shorthand | Experiments |
|---|---|
| Stars | 1, 2, 4, 5 |
| Light bulbs | 1, 2, 4 |
| Immune system | 1, 2, 4, 5 |
| Internet | 1, 2 |
| Boys/girls | 1, 2 |
| Mosquitoes | 3, 4 |
| Related | 3, 4, 5 |
| Work/energy; dielectrics; planets/suns | 3 only |
| Enzyme | 3, 4 |

Exp. 3 styles include presenter plus animation, presenter plus glass board, and animation plus writing hand. Each style is represented by only a few content examples, so style/content cannot be assumed separable. Questions concern the presented content, with recognition/comprehension distinctions described in P01; whether those tags are included in current quiz schemas is unresolved.

## Synchronization and segmentation

**VERIFIED FACT.** The authors align devices to a virtual stimulus clock using shared onset/offset markers and embedded flash/beep events detected with a Cedrus StimTracker. A linear timestamp transformation corrects relative offset and clock drift; recordings are clipped to the video and resampled to a shared 128 Hz grid. Electrical acquisition is 2,048 Hz and EyeLink is 500 Hz. Native source handling involved BDF and, for some streams/experiments, LSL. [S01 signal acquisition/synchronization; S06]

**OUR INFERENCE (INF-008).** Identical released sample rates do not demonstrate millisecond residual alignment. Source timestamp mappings, trigger counts, dropped events, interpolation and resampling filters can alter apparent cross-modal lag. Before timing or directionality claims, estimate residual alignment from events/waveforms per file and report uncertainty. No residual-error distribution was found in the inspected documentation.

**VERIFIED FACT — storage semantics.** The export code writes one participant/session/stimulus record at 128 Hz and maps Exp. 4 first-block tasks to IDs 4–6. Exported BDF is reconstructed from MATLAB arrays and may pad to full records; native-acquisition BDF and release BDF must not be conflated. File durations, padding and event endpoints require archive inspection. [S06 raw writers; code audit]

See [experiment/synchronization diagram](figures/protocol_and_signal_provenance.md) for the acquisition-to-release chain and [open questions](open_questions.md) for reconstruction gates.
