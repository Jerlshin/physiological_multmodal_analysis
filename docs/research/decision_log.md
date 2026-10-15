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

Detailed decisions are **BID-001–027** in the [phase-local log](research_gap/decision_log.md). Earlier entries are unchanged. No real quiz outcome was read in this phase.

| ID | Decision | Evidence / reason | Revisit trigger |
|---|---|---|---|
| D052 | Implement the frozen G01-R protocol as the production package `src/g01r`. It includes population and case flow, outcome-blind features (processed and raw routes), split-specific synchrony under explicit reference-access rules, the ridge baselines, metrics, inference, the analysis registry, MLflow-mirrored tracking and a machine-enforced outcome-access gate. Operational clarifications IS-001…IS-027 were fixed before outcome access | [Baseline implementation](baseline_implementation/README.md); [implementation spec](baseline_implementation/implementation_spec.md) | Any change to a bound file is a logged deviation and requires a new freeze |
| D053 | Keep the person-block permutation test as the H1/H2 detection procedure; the declared fallback is not triggered | [Validation](baseline_implementation/validation_report.md): production V1 false detection 0.060, power 0.973, futility error 0.050; real-feature V2 false detection 0.030 / 0.065 | — |
| D054 | **Verdict: READY FOR PREREGISTRATION / ANALYSIS FREEZE.** The freeze manifest is written and verified. Committing it, depositing the preregistration and writing the authorization record are user actions | [Readiness verdict](baseline_implementation/readiness_verdict.md) | First step after authorization: `python -m g01r run --analysis H1_H2` |
| D055 | **Freeze finalization: READY TO COMMIT AND PREREGISTER.** The preregistration is final; the gate requires a committed freeze and re-verifies at every access; the reused synchrony caches are verified bit-identical and bound; H3 reading clarified (IS-028). No scientific decision changed | [Freeze finalization](baseline_implementation/freeze_finalization.md) | Any change to a bound file before authorization requires a rebuilt freeze; after it, a logged deviation |
| D056 | **Freeze committed** as `6ba87fe` (tag `g01r-freeze-v1`; manifest `a2594996…`), with the H3 reading (IS-028) confirmed as final. The preregistration snapshot is built and checksummed. Real outcomes remain locked | [Freeze record](../../analysis_freeze/FREEZE_RECORD.md) | Next: user deposits the preregistration, then writes the authorization record |

## Amendment — Real-outcome authorization and first confirmatory run (H1/H2), 2026-10-05

Detailed decisions are **CHR-001–009** in the [phase-local log](research_gap/decision_log.md). Earlier entries are unchanged. No scientific specification changed.

| ID | Decision | Evidence / reason | Revisit trigger |
|---|---|---|---|
| D057 | Authorize real-outcome access after the OSF deposit (https://osf.io/uh397/overview; author Jerlshin), only after `verify-freeze` passed; re-verified after authorization | [Phase report](confirmatory_h1h2/README.md); `AUTHORIZATION.json` `0bd14a35…`, commit `33e61e6` | Any change to a bound file makes the loader refuse access |
| D058 | Execute run-book step 1 (`H1_H2`) exactly as frozen. Run `20261005T104908Z_c57b28d6` FINISHED; one logged outcome access | [Run provenance](confirmatory_h1h2/README.md#run-provenance) | — |
| D059 | **H1: bounded negative** (Ŝ 0.021, p 0.082, U₃ 0.079). **H2: H2a and H2d rejected (Holm), H2b and H2c not** — all detected increments below δ | [Results](confirmatory_h1h2/h1h2_results.md) | No H2/H3 result revises H1 |
| D060 | Next: complete run-book steps 2–5 per preregistration §13/§15; no new modelling. Not started | [Recommendation](confirmatory_h1h2/h1h2_results.md#recommendation-for-the-next-phase-not-started) | User decision |

## Completion of the preregistered G01-R plan (run-book steps 2–5), 2026-10-06/07

Detailed decisions are **PCD-001–013** in the [phase-local log](research_gap/decision_log.md). Earlier entries are unchanged. No scientific specification changed.

| ID | Decision | Evidence / reason | Revisit trigger |
|---|---|---|---|
| D061 | Execute run-book steps 2–5 exactly as frozen (14 runs, 14 logged outcome accesses, freeze `VERIFIED` before and after every step). H1/H2 untouched; nothing added | [Phase report](preregistered_completion/README.md); decision log PCD-001…PCD-008 | — |
| D062 | **H1 final: bounded negative, robust.** All eight H3 estimates (0.009–0.021) keep the sign and stay below δ | [Results](preregistered_completion/results_steps2_5.md) | An external replication |
| D063 | **H2 final:** H2a confirmed and reference-dependent, reappearing on new content with unlabelled same-protocol references (B − C < 0 in 8/8 videos) but not across protocols. H2d confirmed in regime A, with its quality robustness untested by design. H2b and H2c not supported anywhere | [Final report §2](preregistered_completion/final_report.md#2-final-status-of-each-h2-component) | — |
| D064 | **Close the preregistered phase.** Bottleneck: criterion noise without a pretest, n = 68, and behaviour-entangled quality variables, relative to a sub-δ ocular-synchrony effect. Ranked next: (1) the John 2025 external ocular replication as time-stamped; (2) a gaze-ISC versus quality/looking-away separation study; (3) prospective cohort design; (4) deployable synchrony references. No new modelling on BBBD. **Not started** | [Final report §12–§13](preregistered_completion/final_report.md#12-the-empirical-bottleneck-for-the-next-phase) | User decision; external data download needs authorization |

## External ocular replication on John et al. 2025, 2026-10-07

Detailed decisions are **JRP-001–010** in the [phase-local log](research_gap/decision_log.md). Earlier entries are unchanged. No BBBD outcome was read and no bound BBBD file changed.

| ID | Decision | Evidence / reason | Revisit trigger |
|---|---|---|---|
| D065 | Open the John 2025 replication as the next step, on the user's instruction to "do the next step". Do not develop new models on BBBD | M08 licenses method work only after a detected H1 (H1 was bounded negative); PCD-013 ranks this replication first | — |
| D066 | Run the plan exactly as time-stamped (`ef1df1b`), with clarifications IJ-001…018 and results-informed amendments A1/A2 (estimate-only) fixed and hash-bound before the single outcome access. The BBBD→John transport check is deferred, because it needs a new BBBD outcome access | [Clarifications](external_john2025/implementation_clarifications.md); [phase record](external_john2025/README.md) | User decision on the transport check |
| D067 | **Primary result: detected.** The gaze block adds held-out information beyond the pretest-adjusted baseline: Ŝ 0.079, p 0.002, 90% interval −0.05 to 0.21. Robust to eye QC (A1) and to decomposed quality (A2). The increment sits mainly in reference-free gaze, not ISC | [Results](external_john2025/results.md) | A second ocular cohort or the transport check |
| D068 | Next (not started), ranked: (1) registered explanatory follow-up and final-model card on John; (2) Lallé 2025 second ocular cohort (reference-free gaze); (3) BBBD→John transport; (4) prospective design. Still no new architectures or EEG/ECG work | [Phase README](external_john2025/README.md#ranked-next-steps-not-started) | User decision; downloads and new outcome accesses need authorization |

## Novel-method phase (post-preregistration method development, planning), 2026-10-08

The user explicitly opened a new method-development phase. G01-R and the John replication remain unchanged historical evidence. No outcome was read, nothing was downloaded, and no model was trained. Phase record: [novel_method/](novel_method/README.md).

| ID | Decision | Evidence / reason | Revisit trigger |
|---|---|---|---|
| D069 | Open a post-preregistration method-development phase on the user's instruction. M08 ("no method work after a bounded-negative H1") governed the preregistered program. This phase follows the final report's own condition for new architectures: a new, separately preregistered protocol reported as post hoc relative to G01-R | [Final report §13](preregistered_completion/final_report.md#13-ranked-recommendation-for-the-next-methodological-direction-not-implemented); [critical review #18](novel_method/critical_review.md) | — |
| D070 | Run two outcome-free audits of the existing 128 Hz cache: gaze/pupil and EEG windowed decompositions. Whole-video features keep about 10% of windowed gaze-ISC variance (10 s). About 16% of that variance is reliable person × moment structure. EEG proxies show little time-localized structure | [Evidence](novel_method/evidence/README.md) | CorrCA windowed EEG check (Stage 0c) |
| D071 | Select **CAIRN** (content-anchored item-response network) as the primary direction. Use the whole-video tabular (B3), foundation-model (B4a) and MIL (B4b) approaches as baselines. Merge latent-state and stimulus-reference ideas as ablations. Reject confounder-adversarial raw-signal networks and regime-D calibration as the primary | [Plan §5–§7](novel_method/research_plan.md#5-candidate-methodological-directions) | Development stop rules (§20.5) |
| D072 | Revisit the G08 rejection ("temporal item encoding"). Item texts with R/C tags exist for all 11 videos. Second-scale anchors do not need the native sub-second timing. New gate: reconstruct the stimulus trim (recorded durations differ from YouTube; Enzyme is longer than its reported duration) | [Plan §1.2 E11–E12, §11.2](novel_method/research_plan.md#112-content-anchors-stage-0-outcome-blind-frozen-and-hash-bound-before-any-outcome-linkage) | G-TL / G-AN failure |
| D073 | Partition:<br>• development = E3 + E1 (Light bulbs, Internet, Boys/girls);<br>• locked primary = E4; locked secondary = E5;<br>• reserved descriptive = E1 Stars/Immune;<br>• label-free only = E2 and untested exposures (fold-safe);<br>• external = Lallé (if its data terms allow), John (restricted, never pretraining), webcam (transport) | [Plan §15, §19](novel_method/research_plan.md#15-development--evaluation-split-strategy) | Access or licence outcomes |
| D074 | Modality roles. Gaze is primary. In-window validity and head position are behavioural channels (NH4). Pupil, EEG and HR are development-gated secondary channels; EEG is also gated by an outcome-free Stage-0 check. Respiration is excluded. Covariates and recording-level quality stay in the person path | [Plan §7.4](novel_method/research_plan.md#74-modality-decisions-from-evidence) | Stage 0c; development selection rule |
| D075 | Plan v1.1 after critical review (R1–R15). Stop after planning. Next user actions:<br>• transcript/video access for anchoring;<br>• clarify Lallé, John-item and webcam data terms;<br>• optionally commit to time-stamp the plan | [Critical review](novel_method/critical_review.md); [plan §23](novel_method/research_plan.md#23-staged-implementation-roadmap) | User decision |

## Novel-method Stage 0 (feasibility, novelty close-out, Stage-1 preparation), 2026-10-13

Executed on the user's instruction. No outcome was read and no CAIRN model was fitted. G01-R and John remain unchanged. Phase record: [novel_method/stage0/](novel_method/stage0/README.md). Local IDs: S0-D01–S0-D16 in [stage0/decisions.md](novel_method/stage0/decisions.md).

| ID | Decision | Evidence / reason | Revisit trigger |
|---|---|---|---|
| D076 | Open Stage 0 with these boundaries: no outcome access, no supervised fit, no Stage 2. Design analyses use development and label-free exposures only. Public stimulus media are git-ignored and not redistributed | User instruction; [entry state](novel_method/stage0/entry_state.md) | — |
| D077 | **Novelty narrowed.** "First content-anchored item-level prediction" is withdrawn after Lallé 2025 (read at code level). Claims: N-a′ (psychometric identification), N-d (falsification, central), N-b′ (peer-relative, no peer-free variant), N-e. Lallé's method is added as baseline B9. EyeBench claim corrected (text-only ≈ text + gaze) | [Literature close-out](novel_method/stage0/literature_closeout.md) | Lallé paper text; new prior art |
| D078 | **G-TL:** 10/11 PASS, Immune PARTIAL. Enzymes explained (two concatenated eHow videos). Substitute replication criterion for the three E3-only videos. Validator rule v2 (documented post hoc correction of v1) | [Timeline audit](novel_method/stage0/timeline_audit.md) | New stimulus provenance |
| D079 | **Anchors are provisional** (R1 lexical + R2 LLM-assisted; never frozen): 105/131 anchorable, development 87/107 in 59 distinct moments. G-AN needs two human annotators; protocol and package ready | [Anchor audit](novel_method/stage0/anchor_audit.md) | Human annotations |
| D080 | **Modalities:** gaze alignment, dynamics and validity primary; pupil ablation; head, EEG and ECG diagnostic only (EEG fails the plan's Stage-0 reliability criterion, SB .06); speed and respiration rejected | [Signal feasibility §8](novel_method/stage0/signal_feasibility.md#8-modality-decisions-for-stage-1) | Development selection rule (pupil) |
| D081 | **Architecture:** CAIRN-linear is the pre-specified primary (learned encoder = ablation A4); regime B dropped (distillation R² < 0); NH4 uses long invalid episodes; T2 permutes distinct anchor moments | Signal feasibility §6; plan [S0-4], [S0-8] | Stage-2 development results |
| D082 | **Stage-1 specification:** exact simulation, pass criteria, lock redesign path if power is low, leakage tests, gated loader (`cairn.gate`, implemented and tested), baseline interface, manifests, reproducibility | [Stage-1 spec](novel_method/stage0/stage1_spec.md) | — |
| D083 | **Verdict: GO to Stage 1.** Stage 2 needs a G-AN-frozen human anchor set, a passing simulation, a CAIRN freeze and explicit user authorization. Plan amended to v1.2 | [Reassessment](novel_method/stage0/reassessment.md#12-verdict) | User decision |

## Novel-method Stage 1 (outcome-free implementation and design simulation), 2026-10-13 – 2026-10-14

Executed on the user's instruction ("Stage 1 only"). No outcome of any cohort was read; every simulated outcome is synthetic. G01-R, John and the Stage-0 record are unchanged. Phase record: [novel_method/stage1/](novel_method/stage1/README.md). Local IDs: S1-D01–S1-D19 and S1-I01–S1-I13 in [stage1/decisions.md](novel_method/stage1/decisions.md).

| ID | Decision | Evidence / reason | Revisit trigger |
|---|---|---|---|
| D084 | Open Stage 1 only. No outcome access, no Stage 2, commits left to the user. Entry state recorded: G01-R freeze VERIFIED, 130 tests OK, access logs unchanged, Stage-0 hashes 64/64 | [Entry state](novel_method/stage1/entry_state.md) (S1-D01) | — |
| D085 | `.venv-cairn` reads the frozen `.venv` read-only; no package added. Optional Stage-2 baseline dependencies are deferred, because installing them needs a download | S1-D02 | User authorizes installs |
| D086 | **CAIRN-linear made explicit:**<br>• within-cell and within-item centring of the moment regressor;<br>• fixed ridges, with variance components from each fold's IRT-M2 base;<br>• corrected marginal prediction;<br>• one λ shared by R/C items;<br>• hard-span kernel, with a 12-configuration lag/width grid for development | S1-D03, S1-D04, S1-D07, S1-D11 | Development results |
| D087 | **Simulation:** real incidence, anchors and signals; synthetic outcomes, with learner, item, video and shared-moment dependence. 500 replicates per null (development, E4, pooled), B = 199 for nulls and 99 for alternatives. Rules fixed before each run, hash-stamped | S1-D05, S1-D08; [predeclared rules](novel_method/stage1/evidence/predeclared_rules.md) | — |
| D088 | **Primary form: within-recording detrended CAIRN-linear** (pre-declared rule R-A). The plan-literal form fails under the fatigue/position confound (T1/T2 up to .10) | S1-D06 | — |
| D089 | Likelihood-ratio statistic and frozen development direction evaluated as redesign candidates under the unchanged permutation nulls | S1-D09; R-B2 | — |
| D090 | **Calibration PASS:** every planned test ≤ .07 in N0–N3 (E4, development, pooled). The exception, the pooled frozen-direction LR under N2 (.078), is excluded | S1-D12 | Human anchors |
| D091 | **Stop rule unchanged** (false go ≤ .008). **The minimum useful effect is unchanged** (S_item ≥ .01 and ΔAUC_wp ≥ .02, ≈ OR 2.1–2.2 at ρ = .4). δ_item = OR 1.49 is recorded as detectable, not useful | S1-D13, S1-D14 | — |
| D092 | **Lock design revised (needs user decision).**<br>• E4 alone: NH1 power .32 at OR 1.35; .97 at the useful effect.<br>• **Ready now: pooled E4 + E5 lock, plan's CV statistic, NH1 confirmatory** (declared options a + c). MDE 1.48; .51 at OR 1.35. Passes N0–N3 and non-linear fatigue.<br>• **Upgrade: the same lock with the LR statistic.** MDE 1.43; .66 at OR 1.35. Needs approval plus a non-linear trend control: under non-linear fatigue its single tests reach .08 (rule R-E) | S1-D15 | User decision |
| D093 | **NH4 attribution:** gaze-only channels reject in 15–26% of content-timed-loss nulls. A gaze test conditional on in-window validity must be specified and simulated before any "beyond data loss" claim | S1-D16 | — |
| D094 | **N-d scope made precise:** the randomization nulls do not exclude learner-specific temporal trends; the within-recording trend control does, and it is part of the method. The claim's content is unchanged | S1-D17 | — |
| D095 | **Stage 1 complete; stop.** Plan amended to v1.3 ([S1-1]–[S1-13]). Stage-0 code provenance preserved (S1-D19). Stage 2 needs the gates in [stage1/README.md](novel_method/stage1/README.md#remaining-gates-before-stage-2) | Stage-1 report | User decisions |

## Novel-method closure phase (outcome-free completion before Stage 2), 2026-10-14 – 2026-10-15

Executed on the user's instruction. No outcome of any cohort was read; every simulated outcome is synthetic. G01-R, John, Stage 0 and Stage 1 are unchanged: the Stage-1-exit code is archived and verified, and the hash lists still verify. Phase record: [novel_method/closure/](novel_method/closure/README.md). Local IDs: C-D01 onward in [closure/decisions.md](novel_method/closure/decisions.md). Rules declared before the runs: [closure/evidence/predeclared_rules.md](novel_method/closure/evidence/predeclared_rules.md) (`591913ad…`).

| ID | Decision | Evidence / reason | Revisit trigger |
|---|---|---|---|
| D096 | Open the closure phase: resolve everything outcome-free before Stage 2. No outcome access; commits, annotation and authorization stay user acts | User instruction (C-D01) | — |
| D097 | Stage-1 provenance kept verifiable. The complete Stage-1-exit `src/cairn` is archived and hash-checked; Stage-0 modules are never edited; each closure run uses a frozen code snapshot | C-D02 | — |
| D098 | Temporal control chosen by rule R-F among polynomial within-recording detrends d ∈ {1, 2, 3}, with two out-of-family fatigue nulls (cubic, exponential). Estimand: deviation from the learner's own degree-d\* course | C-D03 | — |
| D099 | The likelihood-ratio statistic (same T1/T2/T2c permutation nulls) is the decisive candidate; the CV statistic is the certified fallback. Usefulness stays cross-validated | C-D04 | User does not ratify LR |
| D100 | Five moment-block parametrizations compared by rule R-G, with power averaged over six truth directions and a declared robustness constraint | C-D05 | — |
| D101 | E4/E5 heterogeneity kept interpretable by closed testing (H_pool, then H_E4 and H_E5), with per-cohort λ̂ and usefulness | C-D06 | — |
| D102 | NH4 attribution: the gaze block conditional on the in-window validity term (rule R-I) | C-D07 | — |
| D103 | Strong baselines B3/B4a/B4b/B7 implemented in a separate `.venv-cairn-ml` (package and weight downloads read as authorized by the instruction to complete them). TabPFN ≥ 2.5 (licence gated) and EEG foundation models are not used | C-D08 | Stage 2 |
| D104 | Rule R-J (re-simulation on human anchors) declared, with pass criteria, a fallback order and a power floor put to the user | C-D09 | — |
| D105 | G-AN tooling and protocol addendum v1.1 (format validation, receipts, κ, consensus rule, worksheet, recording-clock table, anchor freeze companion), declared before any annotation | C-D10 | — |
| D106 | CAIRN freeze tooling verified against the Stage-0 gate. Authorization is printed as a template and never written by code | C-D11 | — |
| D107 | Stage-2 (DAP-1) and Stage-4 runners implemented, gated, and dry-run on synthetic outcomes. R = 10 channel caches precomputed | C-D12 | — |
| D108 | **R-F result: d\* = 3 (cubic detrend).** The only degree with all 60 decisive cells ≤ .07 (maximum .066). d = 1: 11 exceedances, up to .135. d = 2: one, .074 under the out-of-family cubic null. Pooled power cost at OR 1.5: .01–.05 | C-D13 | Rule R-J |
| D109 | **R-G result: P6** (six-channel isotropic ridge). All five candidates are admissible. Only P6 and PT are robust; P0, PD and PA fail the robustness constraint (P0 .23 under a single-channel truth; PD .46 with independent development/lock directions). P6 is within .02 of PT and is the smaller departure | C-D14 | — |
| D110 | **Final confirmatory design (lock-design decision; needs the user's ratification at the freeze).**<br>• Pooled E4 + E5 lock; CAIRN-linear with P6 block and cubic detrend.<br>• NH1 = T1lr ∧ T2lr (likelihood-ratio statistic, B = 999).<br>• Closed testing of E4 and E5; CV statistic as certified fallback; NH4 attribution by the conditional test; NH2–NH5 descriptive.<br>**Rule R-H passed** on an independent 22,100-replicate run: pooled LR ≤ .068, E4/E5 elementary ≤ .043, CV ≤ .065, development false go ≤ .010.<br>**Power** at ρ = .4: .58 at OR 1.35, .89 at 1.5, MDE 1.45. Closed-testing MDE: E4 1.85, E5 1.70. CV-fallback MDE ≈ 1.55 | C-D15; [design_config.json](novel_method/closure/design_config.json) | Rule R-J on human anchors; the user declines LR |
| D111 | **NH4 attribution test adopted (rule R-I):** the gaze block conditional on in-window validity. It is calibrated (≤ .062) where the unconditional test reached .35 under content-timed loss | C-D17 | Rule R-J |
| D112 | **Baselines validated (rule R-K):** all 17 are deterministic and fold-safe, and pass the negative control; all anchored learners pass the positive control. Flexible whole-video learners do not beat IRT-whole on a moderate person-level signal; a post hoc functional check shows they do learn a strong one | C-D16 | Stage 2 |
| D113 | **Closure phase complete; stop at the human / authorization boundary.**<br>• Plan amended to v1.4 ([C-1]–[C-12]).<br>• Exit checks pass: G01-R VERIFIED; 203 tests OK; `cairn verify` passed; Stage-0 64/64; Stage-1 record 194/194 plus 27/27 archived exit modules; gate refuses; access logs unchanged.<br>• Remaining: G-AN, rule R-J on human anchors, ratification and commit, CAIRN freeze, development authorization | [closure/README.md](novel_method/closure/README.md) | User decisions |
