# Dataset profile

**VERIFIED FACT — identity and purpose.** BBBD is a consolidated release of five laboratory educational-video experiments from the Parra laboratory at City College of New York. It links time-aligned neural, ocular, cardiac and (in two experiments) respiratory measurements with immediate video quizzes and selected participant questionnaires. It was collected to examine attention, stimulus-driven intersubject synchrony and learning, with deliberate distraction or motivation manipulations in some cohorts. It is not a diagnostic ADHD dataset, a long-term learning study, or a set of independent labeled time windows. [S01 Methods; P01–P04, all in the source registry](evidence/source_registry.md)

| Property | Best-supported reconstruction |
|---|---|
| Current selected version | Zenodo 1.1, Sept. 25, 2026; record 22968459 |
| Recruitment → released | 186 → 178 people; eight excluded; per-experiment final counts 27, 31, 29, 43, 48 |
| Population | Adult NYC community/CCNY recruitment; 18–57 years; reported mean 25.79, SD 7.93 |
| Setting | Individual laboratory viewing in a sound-controlled booth, generally 1–2 hour visit |
| Independent content | 11 unique educational videos reused across experiments; do not mistake the table's 22 entries for 22 independent stimuli |
| Experimental units | Person × experiment × viewing block × stimulus; BIDS `ses` encodes viewing blocks, not established longitudinal visits |
| Signals | Gaze/pupil all experiments; EEG, ECG, EOG and head tracking principally 2–5; respiration 4–5; Exp. 1 head availability needs reconciliation |
| Native → release sampling | BioSemi electrical/respiratory streams 2,048 Hz, EyeLink 500 Hz → video-aligned 128 Hz continuous exports |
| Behavioral measurements | Immediate quiz answers/correctness or partial credit; domain questions where available; ASRS and digit span in 2–5; self-report demographics including GPA |
| Public size | Five ZIPs total 26,973,110,601 bytes; this is archive metadata, not downloaded or QC-approved volume |
| Prior publication | Four confirmed empirical antecedents, one descriptor; another classifier-paper lead needs original methods |

Sources: [S01–S06; P01–P05](evidence/source_registry.md). Counts refer to release documentation, not a verified all-modality complete-case cohort.

**VERIFIED FACT — provenance and release history.** The descriptor's 2025 preprint (10.1101/2025.04.29.651259) and 2026 article describe the same resource. The 2021 and 2022 papers used portions of the underlying collection before the complete public release; the 2025 iScience article additionally analyzes EEG/traits/quiz outcomes. The claim that most recordings are newly public does not mean their scientific questions are unstudied. The September 2026 release corrects Exp. 4/5 questionnaire participant mappings and correctness fields, supplies long-format partial-score records, and removes Exp. 5 sub-09. The website separately flags pending individual-matrix corrections. [S01 Data Records; S04; P01–P04]

**OUR INFERENCE — distinctive value (INF-001).** BBBD's strength is its jointly recorded physiology and actual behavioral outcomes during shared, repeatable naturalistic stimuli, with multiple related protocols. It supports asking whether physiology adds information beyond stimulus and participant traits. Its value comes with a small number of independent videos and a modest number of people per protocol.

**OPEN QUESTION — hours and coverage (INF-002).** Current official homepage totals are EEG 91.2 h, ECG 93.5 h, EOG 94.4 h, head 92.5 h, gaze/pupil 110.6 h and respiration 44.2 h. An earlier NEMAR landscape entry reported 65 EEG h. These scopes/versions have not been reconciled. Do not add modality-hours to obtain independent observation time or use homepage hours as a valid-data mask. [S05; prior landscape note]

**VERIFIED FACT — access/license.** Official site licenses downloadable data CC BY 4.0, including commercial use with attribution. Cite the descriptor, exact release and applicable antecedent papers. Public download does not require a data-use agreement in the inspected documentation. The code snapshot has no standalone LICENSE file in its inspected tree; clarify code reuse terms rather than infer them from the data license. Original YouTube stimuli have separate rights and may change; dataset licensing does not automatically license their redistribution. [S03; S05 about; S06 tree]

**OPEN QUESTION — original acquisition dates, duplicate recruitment and rights.** Exact collection dates per experiment, whether anyone participated across cohorts, complete native acquisition-file retention and video-file redistribution permission are not established by the reviewed sources. These are explicit audit/clarification items, not assumed absent.

For file layout, transformations and source disagreements see [modalities](modalities.md) and [code audit](evidence/code_audit.md). For scientifically strongest/weakest uses see the [readiness report](research_readiness.md).
