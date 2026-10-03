# Research Gap Discovery & Problem Formulation

**Completed substantial exploratory pass: 2026-10-03.** Recommendation: prioritize **G01 — individual validity of physiological quiz measures across people, content and reference-access settings**. This is a conditional primary scientific question. A publication-ready novelty/method claim is not yet established, and OQ-06 remains open. No predictive model was developed.

The review starts from the entire repository research trajectory and the latest empirical audit, then broadens beyond BBBD citations. It records **71 search queries / 38 search-and-reading batches**, **43 external literature records** plus inherited BBBD antecedents, **24 candidate directions**, **eight full dossiers**, and **four shortlisted problems**. Fourteen external records have relevant original full-text sections reviewed; others have explicitly scoped primary-abstract/indexed access. This is a substantial adversarial scoping review, not an exhaustive systematic-review census.

## Ranked shortlist and proposed papers

| Rank | Research problem | Proposed contribution and experimental story | Main risk / likely publication strength |
|---|---|---|---|
| **1 — G01** | When do physiological responses carry useful individual quiz information beyond content, available covariates and measurement quality? | Establish matched-population incremental utility; separate known-content, novel-content and reference-assisted evaluation; challenge scoring/quality explanations; independently replicate the key boundary. Develop a modest method only if an identified failure calls for it | Highest scientific value and strongest conditional Q1 route. Closest learning studies already occupy broad synchrony/state–trait claims; few independent content units and missing prior knowledge limit interpretation |
| **2 — G02** | Does selective sensor availability change whose quiz performance can be estimated validly? | Compare complete-case conclusions with a sensor-availability policy covering all eligible outcome-observed cases; report risk and coverage under real quality patterns; distinguish observed-policy risk from hypothetical clean-signal value | Important measurement problem, but ICYM²I already treats missingness-distorted modality value and QA-MoE treats reliability. Strong Q1 case requires a distinct result plus external real-missingness evidence |
| **3 — G03** | Can training-only EEG preserve demonstrable behavioral information in an ECG+eye system? | First show useful EEG teacher information; compare direct student, CCA and existing KD; test new people/content and nuisance-matched teachers; replicate with suitable external sensors | Most crowded method space. Conditional extension, not immediate primary. No webcam/PPG or low-cost deployment claim is supported by BBBD |
| **4 — G04** | Does a physiological quiz measure transport across different exposure protocols on identical content? | Bidirectional E4/E5 transport, within-protocol baselines, score/quality sensitivity, explicitly budgeted calibration; extend to independent protocols later | Valuable bounded stress test, weaker standalone paper: only three shared videos and bundled cohort/repetition/preview/incentive changes |

The [deep comparison](candidate_space.md) assesses novelty, importance, feasibility, method opportunity, risk and likely Q1 strength. Each [dossier](candidate_dossiers.md) contains the question, motivation, prior findings, precise remaining gap, usable data, independence, confounds, baselines, potential method, external need and falsification criteria.

## Why the leading problem survived

Existing literature already establishes physiological synchrony–learning associations and multiple forms of multimodal prediction. John et al. also offer a heterogeneous gaze measure with prior-knowledge/missing-gaze controls; Chen et al. report knowledge-dependent neural similarity across individuals and events. Therefore the opportunity is a precise boundary of **individual criterion validity**, not the discovery that more modalities or synchrony predict learning. [John 2025](https://www.nature.com/articles/s41598-025-06654-x), [Chen 2026](https://www.sciencedirect.com/science/article/pii/S1053811926003770).

The methodological alternatives were challenged against recent competitors: [ICYM²I, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/883cf7782b794759b98dd604c4adb5a1-Abstract-Conference.html) substantially narrows a missingness-corrected sensor-value claim; [PhysioGMC, IJCAI 2026](https://www.ijcai.org/proceedings/2026/782) and [BioKD, 2026 preprint](https://arxiv.org/html/2608.06023v1) narrow physiological sensor reduction and reliability-aware teaching. These findings caused demotions rather than being treated as token related work.

**Proposed primary question:** After a relevant viewing and before the quiz, do EEG, ECG and eye measurements improve individual immediate quiz estimates beyond permissible covariates, content information and measurement quality—and does this improvement survive new learners and instructional content without relying on undeclared peer references?

The [primary formulation](primary_problem.md) defines the estimand, populations, access regimes, score policy, competing explanations, baseline families, possible training contribution and failure criteria. It makes no claim of causal learning, durable retention or universally valid attention measurement.

The central hypotheses are: (H1) some prespecified sensor information adds a meaningful held-out improvement; (H2) individual information retains useful value on new content without peer references, whereas shared-content/reference dependence does not; (H3) the substantive finding survives prespecified scoring and quality sensitivities. A bounded E4/E5 transport hypothesis is secondary. All are untested. A precise replicated negative result can be informative; an underpowered null cannot establish absence.

## Data constraints that change the research design

The current audit—not historical paper Ns—sets the limits:

- All E2 behavioral targets stay excluded. E3–5 have **120 qualified participant records / 446 valid memory outcomes** before sensor QC.
- Direct EEG+ECG+eye provisional-QC evidence is **94 / 324 / 8 videos**. The first tested-exposure subset E3+4 is only **57 / 216 / 8**. E5 has a different repeated-exposure target.
- ECG+eye provides **94 / 327 / 8**: removing EEG does not substantially increase the number of eligible people under current policy.
- Qualified records are not independently certified unique humans across experiments. Videos, people and repeats—not windows—determine independent evidence.
- Executed EEG/eye preprocessing and relevant provenance remain unresolved under **OQ-06**. No common valid pre-knowledge score, delayed retention outcome, continuous attention truth or item-timed encoding labels are available for the proposed eligible analysis.

These counts were rechecked from existing tables by a [read-only snapshot script](evidence/review_snapshot.py); no QC thresholds, source signals or outcomes were changed. The [audit contract](audit_contract.md) preserves chronology, scoring and measurement limits.

## What must happen next

Before modeling: establish an adequate candidate-specific provenance route; fix the outcome/forecast/access contract; produce a final eligible-case ledger; assess attainable precision under crossed person/content dependence; close the closest-paper novelty questions; freeze evaluation and inferential assumptions; and establish a credible external-data route. [Eight concrete gates with go/no-go rules](pre_model_gates.md).

**Plan later external educational validation.** BBBD alone can support a bounded exploratory study after these gates, but is not a convincing sole basis for the intended broad elite-Q1 story. Another BBBD experiment is internal transport. Affect/sleep datasets can validate a method component, not an educational criterion. John 2025 and Bühler 2024 are promising scientific leads; their usable raw files/licenses and compatibility have not been verified here. A prospective cohort with more independent content and pre/post knowledge may be necessary.

## Traceable record

- [Audit contract](audit_contract.md) and [evidence snapshot/read scope](evidence/README.md).
- [Search protocol](search_protocol.md), [exact query/read log](search_log.md), [machine search metadata](evidence/search_records.json).
- [Bibliography with access tiers](bibliography.md), [machine references](evidence/literature_records.json), [literature synthesis and closest competitors](literature_evidence.md).
- [Broad candidate matrix and comparison](candidate_space.md), [full candidate dossiers](candidate_dossiers.md).
- [Primary problem and hypotheses](primary_problem.md), [pre-model gates and external plan](pre_model_gates.md).
- [Inference register](inference_register.md), [decision evolution](decision_log.md), [rejection rationale](rejection_log.md).

Evidence classes are explicit throughout: **F** audit fact, **L** external literature, **I** our inference, **H** untested hypothesis, **U** unresolved. Historical decisions remain intact; this phase supersedes the earlier “no formulation yet” stage restriction only, not its measurement limitations.

