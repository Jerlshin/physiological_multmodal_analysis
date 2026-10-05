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

## Blocking-issue follow-up — 2026-10-02

| ID | Decision | Evidence / reason | Revisit trigger |
| --- | --- | --- | --- |
| D037 | Narrow ECG derivative configuration to strong numerical support for causal fifth-order 0.5–25 Hz at native design rate 2048 Hz; keep calibration/manual lineage separate | [All 1,140 testable ECG transfers](dataset_exploration/evidence/gate_closure_ecg_all_pairs.csv), competing responses and synthetic controls; ten all-NaN raw files are untestable | Source-backed invocation/calibration or contrary native evidence |
| D038 | Quarantine all Exp.2 domain/memory targets from scientific pooling, behavioral comparisons and physiology–quiz inference; preserve original release scores and signal/condition use | [Content/order map and historical score non-equivalence](dataset_exploration/gate_closure.md); original participant response permutations are unavailable | Authoritative response-position mapping, keyed cohort lineage and independently reconstructed scores |
| D039 | Revise behavioral feasibility ceilings to 94/324/8 for EEG+ECG+eye and 94/327/8 for ECG+eye; restrict behavioral C03 comparisons to appropriate 3–5 protocols | [Exact before/after counts](dataset_exploration/evidence/gate_closure_feasibility_counts.csv); Exp.3 now strongest remaining first-view multimodal quiz cohort | Exp.2 mapping resolved or justified eligibility/chronology changes |
| D040 | Keep OQ-06 blocking for the full multimodal transition, with a precise remaining evidence requirement; permit only bounded gap mapping using established measurement facts | [Follow-up gate verdict](dataset_exploration/gate_closure.md); EEG/eye recipe, native lineage and absolute calibration not identified by available code/bytes | Executed release provenance or scientifically adequate documented reconstruction route |
| D041 | Preserve earlier audit counts as forensic release-key evidence and expose a separate behavioral eligibility view; make report regeneration reapply the new status | [Eligibility](dataset_exploration/evidence/gate_closure_behavioral_eligibility.parquet), [source hashes](dataset_exploration/evidence/gate_closure_sources.json), updated report generator | New release/source evidence; do not silently overwrite historical inputs |

D034's Exp.2 pooling review is now completed by D038's conservative exclusion; its OQ-06 gate remains open but is narrowed by D037/D040. No original archive was changed, no native reconstruction or model development was started, no final question was selected, and the updated [author query](dataset_exploration/evidence/author_query_draft.md) remains unsent.


## Research-gap discovery and conditional formulation — 2026-10-03

| ID | Decision | Evidence / reason | Revisit trigger |
|---|---|---|---|
| D042 | Begin broad gap discovery and conditional problem formulation under the new user instruction | [Phase report](research_gap/README.md); user explicitly initiates next research phase | This supersedes earlier stage restrictions, not scientific measurement gates |
| D043 | Preserve the current audit contract, E2 exclusion and OQ-06 limits; do not reopen bounded forensics | [Audit contract](research_gap/audit_contract.md); independent aggregate recheck | Candidate-relevant new source evidence only |
| D044 | Screen 24 directions, deeply assess eight and shortlist G01/G02/G03/G04 | [Candidate comparison](research_gap/candidate_space.md), [dossiers](research_gap/candidate_dossiers.md), [rejections](research_gap/rejection_log.md) | Novelty, identification or precision gate changes |
| D045 | Prioritize G01 individual criterion validity as the conditional primary scientific question | Strongest importance/feasibility balance; [primary formulation](research_gap/primary_problem.md) | OQ-06, attainable precision, closest-paper or external-access failure |
| D046 | Demote generic fusion, quality gating, physiological distillation and FM benchmarks as standalone novelty | [Literature comparison](research_gap/literature_evidence.md); ICYM²I, QA-MoE, CMCRD, PhysioGMC, PULSE, BioKD, PhysioOmni and adjacent learning studies | A distinct scientific/methodological result with matched prior comparisons |
| D047 | Separate first-view E3+4 from E5 repeated-exposure evidence, and known/novel/reference-assisted content access | Current direct-QC first-view ceiling 57/216/8; [information contract](research_gap/primary_problem.md) | Explicitly different estimand justified before fitting |
| D048 | Plan independent educational validation and complete pre-model gates before bespoke model work | [Eight gates and external plan](research_gap/pre_model_gates.md); limited content/people and exploratory whole-release exposure | Credible external route and justified design/precision |
| D049 | Stop at formulation/evidence; develop no predictive model in this pass | User boundary; [phase evidence](research_gap/evidence/README.md) | User initiates modeling after appropriate gates |

D040/INF-063 are amended only in phase authorization: conditional formulation is now completed, while OQ-06 remains a scientific prerequisite. G01 is not an unconditional architecture, confirmed novelty claim or journal-acceptance prediction. [Local decisions RGD-001–015](research_gap/decision_log.md) trace the detailed evolution.

## Amendment — Experimental Design & Pre-model Validation phase, 2026-10-04

Detailed decisions are **EDD-001–014** in the [phase-local log](research_gap/decision_log.md). Earlier entries are unchanged.

| ID | Decision | Evidence / reason | Revisit trigger |
|---|---|---|---|
| D050 | Revise G01 → **G01-R**. Regime A on PAS-core is confirmatory; B/C, E5 and E1 are descriptive; the state component is exploratory; negative claims are limited to ≥ 0.10 | [Precision and calibration](experimental_design/precision_and_independence.md) on the actual crossed design | Production re-simulation, or an external replication result |
| D051 | **GO for baseline implementation** under the [frozen protocol](experimental_design/protocol.md) | [Readiness verdict](experimental_design/readiness_verdict.md) | STOP/REVISE triggers listed in the verdict |

## Amendment — Baseline Implementation & Analysis Freeze phase, 2026-10-04/05

Detailed decisions are **BID-001–025** in the [phase-local log](research_gap/decision_log.md). Earlier entries are unchanged. No real quiz outcome was read in this phase.

| ID | Decision | Evidence / reason | Revisit trigger |
|---|---|---|---|
| D052 | Implement the frozen G01-R protocol as the production package `src/g01r`. It includes population and case flow, outcome-blind features (processed and raw routes), split-specific synchrony under explicit reference-access rules, the ridge baselines, metrics, inference, the analysis registry, MLflow-mirrored tracking and a machine-enforced outcome-access gate. Operational clarifications IS-001…IS-027 were fixed before outcome access | [Baseline implementation](baseline_implementation/README.md); [implementation spec](baseline_implementation/implementation_spec.md) | Any change to a bound file is a logged deviation and requires a new freeze |
| D053 | Keep the person-block permutation test as the H1/H2 detection procedure; the declared fallback is not triggered | [Validation](baseline_implementation/validation_report.md): production V1 false detection 0.060, power 0.973, futility error 0.050; real-feature V2 false detection 0.030 / 0.065 | — |
| D054 | **Verdict: READY FOR PREREGISTRATION / ANALYSIS FREEZE.** The freeze manifest is written and verified. Committing it, depositing the preregistration and writing the authorization record are user actions | [Readiness verdict](baseline_implementation/readiness_verdict.md) | First step after authorization: `python -m g01r run --analysis H1_H2` |
| D055 | **Freeze finalization: READY TO COMMIT AND PREREGISTER.** The preregistration is final; the gate requires a committed freeze and re-verifies at every access; the reused synchrony caches are verified bit-identical and bound; H3 reading clarified (IS-028). No scientific decision changed | [Freeze finalization](baseline_implementation/freeze_finalization.md) | Any change to a bound file before authorization requires a rebuilt freeze; after it, a logged deviation |
