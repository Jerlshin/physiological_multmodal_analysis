# Literature search and adjudication protocol

Review performed 2026-10-02–03; cutoff **2026-10-03**. This is a substantial targeted scoping and adversarial novelty review, not a PRISMA systematic review or an exhaustive publication census.

## Search design

Start from the complete repository's research trajectory: the 30 dataset/family notes and selection/exclusion rationale; selected-dataset protocol, modality, outcome, source and prior-work records; empirical QC/provenance/eligibility/feasibility reports; global inference and decision registers. Prefer current machine evidence over historical documentary estimates. Review existing validation records rather than rerunning waveforms. [Audit contract](audit_contract.md) records the resulting constraints; [evidence snapshot](evidence/README.md) identifies the inputs and read-only aggregate verification.

Generate a broad problem space before ranking. Search overlapping concept families: learning/quiz/recall; EEG/ECG/gaze/pupil fusion; synchrony and individualized measurement; self-supervised/contrastive/shared-private learning; missing modalities and nonrandom missingness; quality, calibration and selective prediction; privileged sensors/distillation; subject/content/domain transport; physiological and EEG foundation models. Search outside BBBD and retain older priority-establishing work. Chase references from original articles and then search exact titles for current versions and publisher records.

The execution log contains **71 literal search queries across 38 tool batches**, including batches mixing source reads with searches. Searches used the available web search index, primary publisher/proceedings pages, arXiv, institutional/author repositories, PMC and official project pages. Native Scopus, Web of Science and IEEE citation exports were not obtained. Search rankings, returned-hit counts and crawl dates are not publication dates. All queries, opens, finds and failed-access attempts captured in the session stores are retained in [search_records.json](evidence/search_records.json); [readable log](search_log.md) groups them by saved search/read batch family, not exact interleaved wall-clock time. Metadata for incidental hits remains a discovery record, not an endorsement.

## Evidence tiers

| Code | Access established | Permissible use |
|---|---|---|
| FT | Relevant original full-text methods/results/limitations read | Specific method/design comparison; not independent numerical replication |
| PA | Primary abstract, proceedings metadata or author project page | Scope, claimed contribution and publication identity; no invented split/sample details |
| IX | Original source's indexed text available, direct full text blocked | Explicitly scoped abstract/indexed statements; unresolved methods remain open |
| RR | Original-paper analysis inherited from a linked repository dossier | Use precisely the earlier audited claim and access limits |
| LEAD | Secondary source, citation-only lead or inaccessible original | Search queue only; cannot prove a method/result or dataset reuse |

Journal/conference publication, workshop paper and unreviewed preprint are separate statuses. arXiv versions and final papers are one intellectual work where lineage is established. A preprint can invalidate a first-method claim even if it is not peer reviewed. PULSE's renamed versions are not separate papers. An abstract-only negative search never establishes absence of an approach.

## Inclusion and exclusion

Include papers that establish scientific occupancy, contradict a proposed measurement assumption, offer a necessary baseline, or constrain validation/theory. Exclude incidental biomedical applications without a transferable methodological issue, unsupported aggregators, media summaries and architecture lists lacking relevance. Keep adjacent affect/sleep studies when they already solve the proposed physiological learning technique; different labels do not restore methodological novelty. Keep social/fMRI studies as construct precedent without treating their sensors, causal designs or samples as BBBD-compatible.

For every serious candidate ask: What exact claim is already established? What remains unanswered under a different, justified estimand? Can the audited data distinguish competing explanations? What would be a damaging null or counterexample? Would a reviewer reasonably say this is an application of existing methods? Record the answers in the [dossiers](candidate_dossiers.md), [competition analysis](literature_evidence.md), [rejection log](rejection_log.md) and [decision log](decision_log.md).

## Stopping rule and residual coverage risk

This pass stops after every serious family has direct competitors and an explicit remaining-gap assessment, including late 2026 evidence that changes ranking. It does not stop at the first favorable paper. The final sweep added educational gaze-cluster work, prior-knowledge-dependent neural similarity, missingness-adjusted modality utility, physiological distillation, foundation-model diagnostics and modality-conditional calibration.

Remaining retrieval gates: P05's full original methods, the complete September 2026 Chen et al. NeuroImage paper/supplement, inaccessible supplementary material in the BBBD antecedents, and exact training/lineage/license manifests for any model later adopted. Some PMC pages returned CAPTCHA, some publishers 403 and the PDF screenshot request failed; alternate authorized publisher/author HTML or indexed original text was used with its tier recorded. No access control was bypassed. No absence/first-use claim depends on treating a failed fetch as a negative scientific result.

Update the search before preregistration and submission. This phase establishes a defensible priority for validation, not a guarantee of novelty, journal quartile or acceptance.
