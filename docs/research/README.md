# Research project: evidence and problem formulation

**Current phase — 2026-10-15:** [Novel-method closure phase — outcome-free completion before Stage 2](novel_method/closure/README.md). No outcome of any cohort was read; simulated outcomes are synthetic. **Status: CLOSURE COMPLETE; stopped at the human / authorization boundary.**

- **Temporal control.** A **cubic** within-recording detrend replaces the linear one. It is the only degree calibrated under quadratic, cubic and exponential fatigue (60 decisive cells ≤ .066).
- **Design (D110; needs your ratification).**
  - Pooled E4 + E5 lock; NH1 = T1 ∧ T2 on the likelihood-ratio statistic; closed testing of E4 and E5; CV fallback certified.
  - Power: MDE OR 1.45 (ρ = .4); .58 at OR 1.35 and .89 at 1.5. E4 claim MDE 1.85.
  - All calibration checks ≤ .068.
- **NH4.** The gaze-given-validity test is calibrated (≤ .062).
- **Baselines.** 17 strong ML/DL/FM baselines are implemented and validated outcome-free.
- **Infrastructure.** G-AN tooling and protocol addendum v1.1, freeze tooling, and the Stage-2 / lock runners are ready and dry-run.
- **Next:** two human annotators (G-AN), rule R-J on the frozen human anchors, ratification and commit, the CAIRN freeze, and your development authorization ([run-book](novel_method/closure/gan/README.md)).

**Previous phase — 2026-10-14:** [Novel-method Stage 1 — outcome-free implementation and design simulation](novel_method/stage1/README.md). No outcome of any cohort was read; simulated outcomes are synthetic. **Status: STAGE 1 COMPLETE; stopped before Stage 2.**

- **Primary method.** CAIRN-linear stays primary, in a within-recording detrended form. The plan-literal form fails calibration under a fatigue/position confound.
- **Calibration.** T1, T2, their intersection and the development stop rule are calibrated (≤ .07; false go ≤ .008).
- **Power.** E4 alone has .32 power at OR 1.35; it has .97 power at the unchanged minimum useful effect (≈ OR 2.16).
- **Lock redesign (needs user decision).** Pooled E4 + E5 with NH1 confirmatory is ready now: MDE 1.48. A likelihood-ratio upgrade (MDE 1.43) needs a non-linear trend control first.
- **Next:** human anchors (G-AN), the lock-design decision, a non-linear trend control, the NH4 conditional test, the CAIRN freeze and an explicit Stage-2 authorization.

**Previous phase — 2026-10-13:** [Novel-method Stage 0 — feasibility, novelty close-out and Stage-1 preparation](novel_method/stage0/README.md). Everything is outcome-free: no outcome was accessed and no CAIRN model was fitted. **Status: STAGE 0 COMPLETE (computational parts); GO to Stage 1 under conditions; gate G-AN awaits two human annotators.**

- **Novelty, narrowed.** Lallé et al. (AIED 2025) already predict per-item retention from gaze in content-tied video windows. CAIRN's claim narrows to psychometric identification: item easiness + learner level + a within-learner moment effect, with anchor-randomization falsification and outcome-blind, reliability-gated anchors.
- **Stage 0a.** Stimulus timelines are recovered for 10 of 11 videos; Immune is partial. The Enzymes stimulus is two concatenated public videos.
- **Stage 0b.** Provisional machine/LLM-assisted anchors: 105/131 items, development 87/107. Not frozen; human annotation package ready.
- **Stage 0c.** Gaze moment-level structure is present and construct-sensitive. EEG time-resolved synchrony is unreliable, so it stays a diagnostic. A learned label-free encoder does not beat handcrafted channels, so CAIRN-linear is primary.
- **Next:** human anchor annotation and Stage 1 (outcome-free simulation and implementation, [spec](novel_method/stage0/stage1_spec.md)). Stage-2 outcome access needs explicit user authorization.

**Previous phase — 2026-10-08:** [Novel-method development, planning](novel_method/README.md). This is post-preregistration: everything in it is post hoc relative to G01-R and the John replication, which stay unchanged. **Status: RESEARCH AND ARCHITECTURE PLAN COMPLETE AND REVIEWED; no training, outcome access or download.** [Plan v1.1](novel_method/research_plan.md):

- **Gap.** Whole-video summaries keep only about 10% of windowed ocular-synchrony variance (outcome-free audit). No predictive model links engagement at the moments carrying each quiz item's content to that item's correctness.
- **Method.** CAIRN, a content-anchored item-response network. It has outcome-blind item anchors, a per-second peer-relative engagement encoder pretrained without outcomes, and a Rasch-type head with person, item and within-learner moment terms. Gaze is primary; EEG, ECG and pupil are evidence-gated secondary channels.
- **Evaluation.** Develop on E3 + E1 (three videos). Lock E4 (primary) and E5. Validate externally on Lallé (if its terms allow) and John (restricted). The core test: CAIRN beats an item-level baseline **and** true anchors beat randomized anchors. Development stop rules protect the locked cohorts.
- **Next:** user decisions on transcript/video access for anchoring and on external data terms. [Literature review](novel_method/literature_review.md); [critical review](novel_method/critical_review.md).

**Previous phase — 2026-10-07:** [External ocular replication on John et al. 2025](external_john2025/README.md), the next step ranked first when G01-R closed. The plan was time-stamped (`ef1df1b`) before download. The features were frozen and hash-bound before the single logged outcome access, and the frozen G01-R statistical code was reused unchanged. **Status: REPLICATION COMPLETE.** [Results](external_john2025/results.md):

- **Primary (confirmatory): the BBBD gaze block adds held-out information about posttest performance beyond the pretest and eye-data loss** in an independent cohort.
  - Ŝ = 0.079, permutation p = 0.002, 112 learners.
  - The size is imprecise: 90% interval −0.05 to 0.21; 2.26 → 2.17 items RMSE.
- **Not a prior-knowledge proxy:** the increment is larger with the pretest in the baseline (secondary, without it: 0.066, p = 0.006).
- **Robust to eye-QC policy** (0.082 / 0.079 / 0.096), and **not absorbed by explicit blink, loss and off-screen measures** (0.109). Both are declared, results-informed estimates.
- **Composition differs from BBBD:** the increment sits mainly in reference-free gaze, not gaze ISC (estimates).
- **Not run:** the BBBD→John transport check, which needs a new BBBD outcome access (user decision). Ranked next steps are in the [phase README](external_john2025/README.md#ranked-next-steps-not-started).

**Previous phase — 2026-10-06/07:** [Completion of the preregistered G01-R plan](preregistered_completion/README.md) (run-book steps 2–5). All 17 registry analyses ran exactly as frozen: 14 new runs, 14 logged outcome accesses, and the freeze `VERIFIED` before and after every step. **Status: PREREGISTERED PHASE COMPLETE.** [Integrated final report](preregistered_completion/final_report.md); [per-analysis records](preregistered_completion/results_steps2_5.md):

- **H1: bounded negative, robust.** All eight H3 estimates keep the sign and stay below δ (0.009–0.021).
- **H2a (synchrony > reference-free) confirmed and reference-dependent.** It reappears on new videos with an unlabelled half-cohort reference (regime C better than B in 8 of 8 videos). It does not transfer across protocols, and it stays below δ over the baseline (C 0.020 [−0.014, 0.045]).
- **H2d (gaze) confirmed in regime A.** Its robustness to the eye-quality policy was not a prespecified analysis. The full-model increment halves at the strictest eye QC.
- **EEG and ECG (H2b, H2c):** no support in any prespecified analysis.
- **About 82% of the held-out signal beyond content is nonsignal** (covariates and quality).
- **Bottleneck and next direction (not started):** a noisy criterion without a pretest, n = 68, and behaviour-entangled eye-quality variables. Ranked first: the time-stamped John 2025 external ocular replication.

**Previous phase — 2026-10-05 (evening):** [Real-outcome authorization and first confirmatory run (H1/H2)](confirmatory_h1h2/README.md). The OSF preregistration is deposited (https://osf.io/uh397/overview). `verify-freeze` passed; outcome access was authorized (commit `33e61e6`) and re-verified; the frozen `H1_H2` run `20261005T104908Z_c57b28d6` completed with one logged outcome access. **Status: H1/H2 BASELINE COMPLETE AND DOCUMENTED.** [Results](confirmatory_h1h2/h1h2_results.md):

- **H1 (primary): bounded negative.** Ŝ = 0.021 (90% nested-CV interval −0.033 to 0.072), permutation p = 0.082; increments ≥ 0.10 ruled out (U₃ = 0.079); 0.05–0.10 not ruled out.
- **H2 (Holm):** synchrony beyond reference-free features (H2a, Holm p = 0.020) and the gaze block (H2d, 0.027) detected, both below δ = 0.05; EEG (H2b) and ECG (H2c) not detected.
- **Next (not started):** run-book steps 2–5 (H3.1–H3.6, descriptive/explanatory/diagnostic analyses, full report), as the preregistration commits.

**Previous phase — 2026-10-05:** the [Baseline Implementation & Analysis Freeze package](baseline_implementation/README.md) is complete, and the freeze and preregistration package are [finalized](baseline_implementation/freeze_finalization.md). **Freeze committed** (`6ba87fe`, tag `g01r-freeze-v1`; [record](../../analysis_freeze/FREEZE_RECORD.md)). **Status: READY FOR PREREGISTRATION SUBMISSION.**

- **Pipeline.** `src/g01r` implements the frozen G01-R protocol: population and case flow, outcome-blind features (processed and raw routes), split-specific synchrony under explicit reference-access rules, the prespecified ridge baselines, metrics, inference, run tracking (MLflow) and a machine-enforced outcome-access gate.
- **Validated before any outcome access.** On production code, false detection is 0.060, power at 2δ is 0.973 and the futility error is 0.050. On the real features with synthetic null outcomes, false detection is 0.030 (pure null) and 0.065 (nuisance null).
- **Feature QC.** Outcome-blind; 0% of learners lost.
- **Real outcomes remained locked in that phase.** The next steps were user actions: commit the freeze, deposit the [preregistration](baseline_implementation/preregistration.md), and write the authorization record. The first confirmatory step is then `python -m g01r run --analysis H1_H2`.

**Previous phase — 2026-10-04:** the [Experimental Design & Pre-model Readiness package](experimental_design/README.md) is complete. **Verdict: GO for baseline implementation of the revised question G01-R** under a [frozen protocol](experimental_design/protocol.md).

- **What changed from G01.** Regime A (new learners, known content) is the confirmatory test on EEG+ECG+gaze for 68 people / 259 cells / 8 videos. Content transfer, E5 and E1 are descriptive. Negative conclusions are limited to effects ≥ 0.10.
- **Basis.** A simulation of the actual crossed design and calibration of the decision procedures.
- **Provenance.** OQ-06 is bounded for the frozen feature route, not resolved.
- **Scope.** No physiology–outcome association has been computed yet.

**Earlier phase — 2026-10-03:** a substantial [Research Gap Discovery & Problem Formulation report](research_gap/README.md) is complete: 71 search queries, 43 scoped external references, 24 candidate directions, eight full dossiers and a ranked four-problem shortlist. The conditional primary question is **individual validity of physiological quiz measures across people, content and declared reference access**. Read the [comparison](research_gap/candidate_space.md), [primary formulation](research_gap/primary_problem.md), and [pre-model gates](research_gap/pre_model_gates.md).

The user's new instruction authorizes conditional formulation and supersedes the previous stage-only restriction below. It does **not** close OQ-06, restore Exp.2 behavioral eligibility or establish a publication-ready novelty claim. No predictive model was developed. Current tri-modal ceiling remains **94 qualified people / 324 direct observations / 8 videos**; restricting to first tested exposure in Exp.3+4 gives **57 / 216 / 8**. Later independent educational validation is recommended for the intended strong Q1 contribution.

## Historical stage summaries (superseded where explicitly amended above)

**Blocking-issue follow-up — 2026-10-02:** [targeted and dataset-wide checks](dataset_exploration/gate_closure.md) strongly support the ECG filter configuration but leave OQ-06 blocking for actual EEG/eye options, native lineage and physical calibration. Exp.2's content mapping is verified; historical aggregate scores disagree and response permutations remain unavailable, so its behavioral targets are excluded. Current direct EEG+ECG+eye behavioral ceiling: **94 people / 324 observations / 8 videos**. The full transition to Research Gap & Problem Formulation is **not yet ready**. Earlier audit totals below remain forensic release-key counts.

**Dated amendment — 2026-10-02:** the substantial [Dataset Exploration & Empirical Readiness Report](dataset_exploration/README.md) is now available. All five BBBD v1.1 archives have been acquired and verified, and dataset-wide signal/outcome auditing is complete at the documented lightweight-QC level. **OQ-06 derivative execution/scaling provenance remains blocking**; Exp.2 answer-order canonicalization also needs review before behavioral pooling. The earlier landscape-stage status below is retained as historical context and is superseded for acquisition/QC status by this dated amendment. No model or final paper question has been selected.

- [Selected-dataset knowledge base and prior-art review](selected_dataset/README.md).
- [Empirical audit reports, manifests and evidence](dataset_exploration/README.md).
- [Current P0 disposition](dataset_exploration/open_questions_resolved.md) and [remaining scientific gates](dataset_exploration/open_questions_remaining.md).

Current stage completed: **dataset landscape and selection, 2026-10-01**. No modelling code, final architecture or paper problem statement has been created.

- [Dataset decision](dataset_landscape/selection_decision.md): BBBD release 1.1 primary, conditional on data integrity; ds003838 strongest general alternative; DREAMT strongest clinical/sleep alternative.
- [Comparison matrix](dataset_landscape/comparison_matrix.md): 26 principal datasets across cohort, outcomes, measurement, feasibility and literature occupancy.
- [Candidate catalogue](dataset_landscape/candidate_datasets.md): 30 dataset/family notes, including screened candidates and longitudinal alternatives.
- [Search protocol](dataset_landscape/search_protocol.md) and [52-batch query log](dataset_landscape/evidence/search_log.md): methods, scope and reproducibility limitations.
- [Exclusion log](dataset_landscape/exclusion_log.md): negative findings and conditions for reconsideration.
- [Inference register](inference_register.md) and [decision log](decision_log.md): facts, interpretations, unknowns and decision changes.
- [Bibliography](literature/bibliography.md): primary sources, repositories and empirical reuse, with lower-bound rather than invented publication counts.
- [Evidence artifacts](dataset_landscape/evidence/README.md): source-attributed table, corrected release checksums, small metadata snapshots and ds003838 cohort audit.

Readiness boundary: public metadata and literature reviewed; full biosignal datasets and restricted releases not acquired. The selected dataset still needs participant/outcome joins, modality overlap, timing and signal-quality verification before a final research question or modelling starts.
