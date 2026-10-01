# Dataset landscape search protocol

Search and decision date: **2026-10-01** (Europe/Berlin). Scope: human multimodal physiological/behavioral recordings suitable for a new publication-quality AI/ML study. No target disorder, educational intervention, architecture, or paper hypothesis was fixed before searching.

## Search design

This is a documented, purposive landscape review, not a registered systematic review or an exhaustive bibliometric census. Discovery used web search, publisher full text, official repositories, repository APIs, project documentation, and backward/forward citation chasing. The exact query batches and returned discovery links are retained in [the search log](evidence/search_log.md). Search results are leads; factual claims preferentially use original papers and official records. Publisher access, indexing lag, acronym collisions, and restricted datasets limit completeness.

Priority window: releases or substantial updates in 2024–2026, through the search date. Publication date, collection date, archive release, metadata modification, and mirror creation are treated separately. Older datasets enter when they provide superior controls, labels, longitudinal structure, or essential benchmarks. A 2026 mirror of 2022 recordings is not a new cohort.

## Sources searched

| Source family | Route used and limitations |
|---|---|
| Scientific Data / Nature / Scientific Reports | Broad and domain-restricted discovery; original HTML methods, data records, validation, tables, references and rights inspected for leading candidates. |
| IEEE | Dataset-name and topic searches, DOI records, author/project repositories and arXiv versions. No authenticated IEEE Xplore export; some pages inaccessible. |
| ACM | Domain/topic and named-dataset searches; official project pages, DOI records, CHI/ICMI/NeurIPS-related proceedings. ACM full text was not consistently accessible. |
| Elsevier / ScienceDirect | Discovery and original abstracts for Cognitive Load, fatigue, human–robot interaction and cross-session evaluation; some full text inaccessible. |
| Springer / Wiley / Frontiers | Original papers and reuse studies, including cognitive-load and I DARE sources. |
| PubMed / PMC | Dataset papers, physiological validation and reuse. PMC full text used where available. |
| arXiv / bioRxiv / proceedings | New resources, version history and author manuscripts; preprints distinguished from peer-reviewed papers and deduplicated. |
| PhysioNet | Official descriptions, version changes, signals, access and license for DREAMT and n-back/music; clinical comparators screened. |
| OpenNeuro / NEMAR | Official dataset records and metadata; ds003838 participant table inspected directly. Mirror dates and transformed copies identified separately. |
| OSF | Official project/repository links for public-exhibit affect and prior BBBD studies; no implication that every OSF file was accessible. |
| Zenodo / Figshare / ScienceDB | Record pages, API metadata, file sizes/checksums where exposed, restrictions, code links and release dates. Download-traffic statistics excluded from dataset sizes. |
| University / laboratory / GitHub repositories | Author-controlled documentation and reuse evidence; code licenses not substituted for data licenses. |
| Kaggle | Discovery only; retained only when a scientific original could be established. No anonymous or synthetic mood table accepted as physiological ground truth. |

All of these routes were searched on 2026-10-01. Web discovery of a database is not the same as a native database search with a reproducible export. Exact engine rankings may change; the saved query/result log captures the observed leads.

## Query families

1. Broad: multimodal physiological dataset + EEG/ECG/PPG/EDA/respiration/eye tracking + 2024/2025/2026.
2. Domains: learning, educational video, attention, cognitive load, vigilance, fatigue, stress, emotion, sleep, clinical sensing, human–robot interaction, social interaction.
3. Repository/publisher restrictions: Nature, IEEE, ACM, PubMed, arXiv, PhysioNet, OpenNeuro, OSF, Zenodo, Figshare, university sources.
4. Identity resolution: exact title/acronym + dataset, DOI, download, GitHub, license, participants, sampling, synchronization.
5. Reuse: exact title/acronym/accession + classification, fusion, cross-subject, cross-session, 2025/2026; follow original references and linked publications.
6. Adversarial checks: exclusions, missing signals, corrected labels, resampling, consent, trial versus participant split, earlier publications using the same recordings.

## Inclusion and exclusion

Serious consideration requires scientifically traceable human recordings, at least two relevant synchronized signal/behavior streams, interpretable protocol/outcomes, and either obtainable data or a documented request route. Small or restricted resources can be considered, but access and statistical limitations count against selection. EEG is valuable, not compulsory. Multiple EEG channels alone do not constitute multiple physiological systems.

Exclude from primary selection when provenance cannot be verified, the public data are merely promised, only a tiny released subset is available, labels cannot support the intended interpretation, signal alignment is inadequate for the proposed class of analyses, or an older benchmark offers little new scientific leverage. These are reasons for this decision, not declarations that a dataset has no research value. Preserve exclusions in [exclusion_log.md](exclusion_log.md).

## Extraction and appraisal rules

Each serious candidate receives a note covering cohort, protocol and duration, modalities/rates, processing, synchronization, labels, identity/repeats, controls, artifacts/missingness, access/license/size, standardization/code, reuse, safe claims and remaining opportunities. **NV** means not verified in the accessible sources; **NR** means not reported in the inspected source. Neither means absent. Native, resampled and derived signals are distinguished. Nominal durations are explicitly calculated estimates, not audited usable hours. Modality-hours must not be added to manufacture independent sample size.

Use qualitative, criterion-specific comparisons; no weighted numerical score. Prefer independent outcomes and interpretable controls over channel counts, recency and headline accuracy. Evaluate independent units (subjects, dyads, videos, sessions), subject/stimulus leakage, label construction, and physiological plausibility. A reported synchronization method is not proof of measured timing accuracy.

Literature counts are **verified lower bounds in this search**, separated into descriptors, empirical analyses, preprints, theses and code. Citation counts and download counts are not reuse counts. A title match alone is not proof of dataset use. “No additional reuse verified” is not “unused.” New opportunities remain hypotheses pending a targeted novelty review after dataset inspection.

## Stopping and audit boundary

The search covered the principal recent alternatives and older control/benchmark families, then closed with targeted checks of leading contenders and late-discovered SENSE-42, LLaMAC, COG-BCI and EMBRACE. This bounded review supports a dataset decision; it does not certify all raw files. No modelling, signal preprocessing, account creation, data-use agreement, or author contact was performed. Public metadata were inspected, and a small ds003838 participant table was summarized. Restricted access remains an explicit unknown, not an assumed approval.

## Local evidence and rights

Metadata summaries, derived factual tables, source links and release checksums are saved under `evidence/`. No third-party participant videos or full copyrighted articles are redistributed. CC BY sources are attributed; CC0 participant metadata are reduced to aggregate statistics. Figures from sources with noncommercial/no-derivatives or unresolved terms are linked and described instead of copied. See [evidence/README.md](evidence/README.md).
