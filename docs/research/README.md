# Research project: evidence and problem formulation

**Current phase — 2026-10-05:** the [Baseline Implementation & Analysis Freeze package](baseline_implementation/README.md) is complete, and the freeze and preregistration package are [finalized](baseline_implementation/freeze_finalization.md). **Verdict: READY TO COMMIT AND PREREGISTER.**

- **Pipeline.** `src/g01r` implements the frozen G01-R protocol: population and case flow, outcome-blind features (processed and raw routes), split-specific synchrony under explicit reference-access rules, the prespecified ridge baselines, metrics, inference, run tracking (MLflow) and a machine-enforced outcome-access gate.
- **Validated before any outcome access.** On production code, false detection is 0.060, power at 2δ is 0.973 and the futility error is 0.050. On the real features with synthetic null outcomes, false detection is 0.030 (pure null) and 0.065 (nuisance null).
- **Feature QC.** Outcome-blind; 0% of learners lost.
- **Real outcomes remain locked.** The next steps are user actions: commit the freeze, deposit the [preregistration](baseline_implementation/preregistration.md), and write the authorization record. The first confirmatory step is then `python -m g01r run --analysis H1_H2`.

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
