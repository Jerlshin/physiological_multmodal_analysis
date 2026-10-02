# Research decision log

All entries below were made during the 2026-10-01 landscape review. No earlier work or approvals are implied.

| ID | Decision | Evidence / reason | Revisit trigger |
|---|---|---|---|
| D001 | Keep scope at dataset selection; no model code, architecture or final hypothesis | User's explicit boundary | User initiates next stage |
| D002 | Search 2024–2026 preferentially, retain scientifically strong older resources | Recency is not design quality | New release or substantial correction |
| D003 | Treat sample sizes, rates and dates as version-/modality-specific | Recruitment, release, complete cases and mirrors differ | File manifest contradicts paper |
| D004 | Use qualitative evidence, not an arbitrary weighted score | Control, label quality, ecological breadth and access are competing values | Explicit project priorities emerge |
| D005 | Include clinical sleep, pediatric ADHD, affect, HCI, social and longitudinal alternatives | Avoid assuming educational prediction in advance | A future domain is explicitly chosen |
| D006 | Elevate ds003838 to strongest general alternative | Controlled objective recall, open multimodal data; metadata confirms 64 complete availability flags | BBBD fails audit or controlled cognition is prioritized |
| D007 | Treat DREAMT as strongest clinical alternative | New full-PSG release plus wearable pairing and expert labels | Clinical/sleep priority and access granted |
| D008 | Require corrected BBBD Zenodo 1.1 | September 2026 quiz/ID changes; website individual files may lag | New release or checksum/ID mismatch |
| D009 | Do not treat basic BBBD synchrony or digit-span load fusion as novel | Antecedent papers and 2026 thesis | Full task-specific review identifies a distinct claim |
| D010 | Retain late-discovered LLaMAC/SENSE-42/COG-BCI/EMBRACE | Credible direct alternatives with different strengths | New access/coverage evidence |
| D011 | Reject n-back/music as primary despite many modalities | Only five released people | Larger usable release |
| D012 | Hold MAD/CognitiveLab/EMBRACE full acquisition claims | Stable public raw access or complete release not verified | Official licensed files confirmed |
| D013 | Select BBBD conditionally at landscape level | Best overall combination of independent cohort, meaningful outcomes, research signals and open infrastructure | Label, timing, quality, overlap or novelty gate fails |
| D014 | Prefer future cross-dataset validation over indiscriminate pooling | Labels, sensor physics, populations and prior cohort overlap differ | A defensible harmonization plan exists |
| D015 | Preserve unknowns, exclusions and source limitations | Honest reproducibility; no fictitious complete audit or publication census | Verification supplies missing evidence |

Current decision: [BBBD primary; ds003838 strongest alternative](dataset_landscape/selection_decision.md). Required next work is data acquisition/quality verification, not modelling. No restricted-data agreement was signed, no author was contacted, and no full signal dataset was downloaded in this stage.

## Selected-dataset evidence review — 2026-10-01

This is a later stage within the same date; D001's selection-only scope is superseded by the user's explicit documentation/prior-art review instruction, while its no-model/no-final-problem boundary remains.

| ID | Decision | Evidence / reason | Revisit trigger |
|---|---|---|---|
| D016 | Establish a permanent BBBD knowledge base with separate fact/limitation/inference/open-question categories | User's evidence-review request; [index](selected_dataset/README.md) | New authoritative evidence |
| D017 | Retain corrected Zenodo1.1 as selected release, pin code separately | S03/S04; code commit5109afa predates correction; versions cannot be assumed identical | Actual archive/provenance audit |
| D018 | Count four confirmed empirical antecedents, descriptor separately, P05 as unresolved lead | Original P01–P04 methods; publisher P05 metadata without full text | Original P05 or another traceable reuse |
| D019 | Do not claim ECG, multimodal fusion, temporal analysis or all person/video validation are absent | P02/P03 occupy these topics; P03 has LOSO and video holdout for specific tasks | More specific estimand/gap established |
| D020 | Treat Exp.4 ses-02 as attentive different content, pending event confirmation | S01/S05 and S06 branch outweigh contradictory pasted README prose | File-level events or authoritative correction |
| D021 | Hold target construction until phenotype mappings/scoring are audited | Corrected quiz release and surplus reference IDs (INF-005/016) | Audited1.1 joins and keys |
| D022 | Flag HRV formula and pupil statistic before using descriptor validation as benchmark | Public notebook functions (INF-019/020); actual numerical impact unknown | Reproduction with verified inputs |
| D023 | Treat code inspection as provenance evidence, not an executed release pipeline | Conflicting filter values, options/dependencies and static phenotype copies | Full processing provenance and reproducibility run |
| D024 | Keep novelty claims conditional on bounded search/access limits | Separate supplements and P05 inaccessible; newer adjacent preprints unresolved | Full methods and citation/export update |
| D025 | Carry seven evidence-backed candidate directions into the next stage without selecting one | [Readiness report](selected_dataset/research_readiness.md); INF-025–039 | User initiates gap/problem formulation and audit gates pass |
| D026 | Preserve literature/data-access limits explicitly rather than invent missing details | Original-source verification requirement | Missing sources become available |

No model was developed, no full waveform archive was downloaded, no author was contacted, and no scientific pipeline or paper result was numerically replicated in this review. The completed artifact is a documentation/code evidence base with a concrete acquisition/verification queue.

## Dataset exploration and empirical audit — 2026-10-02

The user's new instruction supersedes the earlier stage's no-download boundary. Earlier entries remain historical; no-model/no-final-problem constraints continue.

| ID | Decision | Evidence / reason | Revisit trigger |
|---|---|---|---|
| D027 | Acquire all five authoritative v1.1 experiment ZIPs with directory-first inspection, bounded resumable ranges and full official MD5/local SHA-256 verification | [Download audit](dataset_exploration/download_and_version_audit.md); each experiment independent; 26,973,110,601 canonical bytes | New release or independent checksum failure |
| D028 | Retain immutable compressed archives and stream bounded chunks directly; create no second full waveform tree | [Storage report](dataset_exploration/storage_and_retention.md); disk/memory efficiency and reproducible source | A scientifically justified native-format processing need |
| D029 | Use keyed experiment-qualified joins, exclude surplus phenotype IDs, quarantine Exp.3 sub-01/stim03 outcome, preserve supplied partial/exact scores | [Quiz integrity](dataset_exploration/quiz_integrity.md); independently recomputed scores and cardinalities | Author response/original corrected item mapping |
| D030 | Use deterministic provisional gross QC and retain correction masks; flag 16 Hz at multiple thresholds without automatic rejection | [Signal QC](dataset_exploration/signal_quality.md); [config](../../audit_config.json); minutes-long eye gaps and localized spectra | Justified paper-specific eligibility/sensitivity protocol after provenance resolution |
| D031 | Report people, canonical videos, person-video exposures and common-grid valid duration rather than independent window counts | [Intersections](dataset_exploration/modality_coverage.md); core direct-quiz QC subset 120/444/11 | New eligibility/outcome chronology or identity evidence |
| D032 | Prefer whole-video characterization; withhold certified sub-second/directional/lag and item-timed claims | [Boundary audit](dataset_exploration/synchronization_audit.md); no native trigger residuals/item timestamps | Original clock-fit/trigger and content-item alignment evidence |
| D033 | Retain supplied peaks/methods and separately compute RMS RR and true RMSSD; use respiratory-specific peak fields | [ECG semantics](dataset_exploration/ecg_quality.md); [respiration](dataset_exploration/respiration_quality.md) | Explicitly justified artifact/beat-processing protocol or original figure inputs |
| D034 | Keep OQ-06 blocking and review Exp.2 option canonicalization before behavioral pooling; do not advance unconditionally to final formulation | [Remaining gates](dataset_exploration/open_questions_remaining.md); exact derivative options/scaling absent | Adequate execution/scaling provenance or documented authorized reconstruction route |
| D035 | Mark whole-release characterization EXPLORATORY; freeze no split and fit no predictive/reference models | User's boundary; [leakage map](dataset_exploration/leakage_and_independence.md); 11 videos and repeated outcomes | User initiates formulation after gates, with an untouched evaluation/external-validation plan |
| D036 | Retain all canonical/scientific artifacts and source snapshots; delete only verified small temporary probes/font caches and log exact bytes/recreation | [Retention manifest](dataset_exploration/evidence/retention_manifest.json); zero canonical or large derived deletion | Disk pressure/new regenerable artifact with verified generating provenance |

No author was contacted; a [concrete query draft](dataset_exploration/evidence/author_query_draft.md) is retained but unsent. No model, predictive performance optimization, final paper question or confirmatory held-out evaluation was developed. The audit materially improves readiness while retaining its blocking and bounded limitations.
