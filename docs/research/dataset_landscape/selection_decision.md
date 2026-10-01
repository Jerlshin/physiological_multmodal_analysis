# Dataset decision

Decision date: **2026-10-01**. Status: **select BBBD release 1.1 as the primary dataset for acquisition and data-quality verification; retain OpenNeuro ds003838 as the strongest general alternative.** DREAMT is the strongest clinical/sleep alternative. No modelling architecture or final paper problem statement is selected.

This is a research judgment under the user's broad scope, not a universal ranking. Selection favors the combination of independent participants, interpretable behavioral outcomes, multiple physiological systems, documented timing, reproducible access and remaining scientific room. It does not award points for being a 2026 paper. [The comparison matrix](comparison_matrix.md) and [dataset notes](candidate_datasets.md) document the alternatives and negative evidence.

## Why BBBD is selected

1. **It preserves several scientifically defensible directions.** Research-grade EEG, eye/pupil/head, ECG/EOG and some respiration can be related to actual video-specific quiz performance and experimental conditions. A final problem can emerge from the data audit rather than being imposed in advance. [Descriptor](https://doi.org/10.1038/s41597-026-07215-1).
2. **Its independent cohort is comparatively substantial.** The paper reports 178 people across five experiments, versus 18 in MMV, 20 in SEED-VII, 29 in COG-BCI and 32–40 in older affect benchmarks. This advantage is conditional: 178 is not the complete multimodal sample, and about 110 h gaze is not 110 h EEG. The public duration summary reports only 65 h EEG. [Official mirror summary](https://www.nemar.org/dataset/nm000147).
3. **Its practical scientific infrastructure is unusually good.** Public BIDS-organized data, event/phenotype metadata, raw-labelled and processed representations, preprocessing/conversion code and an active changelog make reproducibility more attainable. The corrected ZIPs total about 27 GB, materially easier to inspect than IMPROVE's reported 2.83 TB. [Archive](https://zenodo.org/records/22968459), [code](https://github.com/madjens/bbbd-dataset).
4. **Its weaknesses can be made explicit in evaluation.** People, videos, experiments and conditions provide meaningful grouping variables and different generalization questions. They also expose confounds rather than hiding them in a single pooled classification table. This is an inference about research utility, not evidence that all such splits are sufficiently powered.
5. **Its newly accessible recordings offer room beyond its original analyses.** Earlier work established eye/heart/brain synchrony, attention and memory associations. A new study must address a different unresolved empirical question and stronger evaluation. New public bytes create opportunity, not automatic novelty. [PNAS 2021](https://doi.org/10.1073/pnas.2016980118), [PNAS Nexus 2022](https://doi.org/10.1093/pnasnexus/pgac020).

## Why the strongest alternative does not displace it

**Digit span / ds003838** is preferable for tightly controlled memory-load research. Auditory stimuli, constant visual input, passive-listening controls and scored item recall offer stronger identification of cognitive effects. It also has native 1000 Hz EEG/ECG/PPG, unlike BBBD's common 128 Hz released representation. However, direct participant metadata show only **64 with all listed modalities/behavior available**, and the cohort is 74 women/12 men, mainly young Russian-speaking adults. Its core physiological findings are already well occupied: EEG/pupil overload, PPG amplitude versus load, cardiac aperiodic activity, and even pupil–ECG ML fusion in a 2026 thesis. BBBD has a broader combination of population size, channels, naturalistic stimuli and outcomes for the present uncommitted project. [Dataset](https://doi.org/10.1038/s41597-022-01414-2), [reuse thesis](https://oa.upm.es/97820/).

**DREAMT** would overtake BBBD if the later priority becomes clinically anchored wearable sleep modelling: 100 patients with concurrent PSG and wrist physiology, expert sleep labels and diverse sleep-disorder severity. It does not lose because it is “less new.” It narrows the work to sleep and requires restricted access; its 2026 alignment correction and existing WatchSleepNet transfer study also require care. [Current release](https://physionet.org/content/dreamt/2.2.0/), [WatchSleepNet](https://proceedings.mlr.press/v287/wang25a.html).

LLaMAC would be the more natural starting point if experienced affect and EDA/PPG become essential. COG-BCI is preferable if genuine repeated days are mandatory. SENSE-42 is preferable if continuous computer-interaction performance is central. These are explicit sensitivity conditions, not competing problem statements chosen now.

## Material scientific risks

| Risk | Consequence for a future study |
|---|---|
| **Quiz corrections released 2026-09-25** | Experiments 4–5 had participant/answer mapping and correctness problems. Pin Zenodo 1.1; do not combine older downloads or still-pending individual web matrices. Recompute/check score joins before outcome analysis. |
| Incomplete multimodal coverage | Headline 178 can shrink substantially for particular modality/outcome combinations. Power and representativeness must use the resulting independent cohort, not windows or modality-hours. |
| Fixed attend→distract order and repeated videos | Arithmetic, repetition, order and attention effects are entangled. A good condition classifier is not proof of a general attention biomarker. |
| Common stimulus | A model may recognize a video or shared sensory dynamics. Unseen-person performance alone is insufficient for content-general claims. |
| Artifact processing | Extensive pupil/gaze interpolation, 16 Hz electrical contamination in Exp. 4–5 and variable EOG mapping can create or erase apparent cross-modal relationships. |
| Limited labels/content | Immediate quizzes are not long-term learning or continuous attention labels; only 11 unique videos limit stimulus-domain generalization. ASRS is not clinical diagnosis. |
| Prior work | Synchrony predicting attention/memory and cross-modal synchrony covariation are already published. Another generic fusion model would have a weak novelty argument. |
| Undocumented timing precision/native fidelity | Documented trigger/drift correction does not establish residual millisecond precision. Resampling limits what coupling and cardiac analyses can safely claim. |

Sources and exact discrepancies are detailed in [BBBD note](dataset_notes/bbbd.md), [release evidence](evidence/bbbd_release_manifest.md), and [inference register](../inference_register.md).

## Opportunity classes, not a selected paper

Potentially valuable work could assess individual behavioral information beyond shared-video responses, robustness under real sensor missingness, transfer across people/stimuli/experimental contexts, or cross-modal learning that distinguishes common input from complementary information. These opportunities remain hypotheses. They must survive a dedicated task-specific literature review and a feasibility audit before claiming novelty. No claim of a first model, first fusion strategy or causal mechanism is made.

The dataset's particular value is that these questions can be confronted with both synchronized systems and measured behavior. An analysis must distinguish subject-specific prediction, condition discrimination, stimulus recognition and mechanistic explanation; success at one does not establish the others.

## Could datasets be combined later?

Yes, but initially as **separate domains for validation**, not concatenated labels. BBBD + digit span could examine robustness of shared EEG/ECG/pupil relationships across naturalistic video and controlled memory; quiz score and digit recall must retain their different meanings. COG-BCI can test cross-day/task stability. LLaMAC/CASE may be useful if a later question genuinely concerns affect and overlapping peripheral signals. DREAMT offers ECG/PPG/EEG pairing in a very different clinical state, but its labels cannot be relabeled as attention or educational engagement.

Before combining, audit participants and source lineage for overlap, acquisition/filtering differences, eye luminance confounds, event alignment, label semantics, licenses and preprocessing. Do not pool BBBD with its own antecedent subsets as if they were independent external data. Cross-dataset performance can fail because of sensor/population changes rather than refuting an underlying physiological relationship.

## Unknowns that must be resolved before committing to a paper

1. Archive 1.1 participant counts and experiment-scoped IDs; valid corrected quiz joins, missing sub09 outcome and partial-credit scoring; whether any people recur across experiments.
2. Actual sample sizes and valid hours for each modality/outcome intersection, sex/demographic composition after quality filtering, and missingness by condition/video/person.
3. Availability of untouched native-rate data, filtering/resampling parameters, interpolation masks and sample/clock alignment residuals.
4. Exp. 5 intervention/control allocation, order and randomization; discrepancy between text/caption and website subject counts.
5. Severity of 16 Hz contamination and feasibility of artifact-independent brain–body analyses; ocular/cardiac contamination and processing-induced correlations.
6. Whether held-out-video/experiment evaluations have enough unique stimuli and independent people to support the eventual claim.
7. Complete task-specific reuse search, including papers not using the BBBD acronym; precise third-party stimulus/reuse rights where redistribution is contemplated.

These are verification gates, not an instruction to begin modelling. The present decision is complete at landscape-review level. If label identity cannot be reconciled, meaningful modality intersections prove too small, or the viable question duplicates prior work, **reopen the choice rather than force BBBD to win**. Use ds003838 for a controlled general alternative, or the explicitly better-fitting domain resource once the scientific scope becomes clearer.
