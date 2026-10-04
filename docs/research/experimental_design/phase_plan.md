# Phase plan — Experimental Design & Pre-model Validation

Opened 2026-10-04. Input: the completed [research-gap package](../research_gap/README.md), with G01 as the conditional primary problem and [M01–M08](../research_gap/pre_model_gates.md) as the evidence queue. The output is a frozen, falsifiable protocol plus a GO / REVISE / STOP verdict. The phase does **not** fit an outcome predictor that uses physiology, does not search over models, and does not develop architectures.

Evidence classes: **F** audited/repository fact · **L** external literature · **I** inference/decision · **H** untested hypothesis · **U** unresolved.

## Work packages

| WP | Gate | Question to settle | Method | Output |
|---|---|---|---|---|
| WP1 | M01 | Can the selected whole-video measurements be used despite OQ-06, and under which claims? | Read the pinned upstream preprocessing code for **fit scope**: per recording, per person or pooled? Classify each unresolved item by whether it threatens (a) leakage, (b) the construct or (c) only absolute-unit claims | [measurement_provenance.md](measurement_provenance.md) |
| WP2 | M02 | Estimand, hypotheses, primary/sensitivity outcomes, chronology, admissible covariates | Protocol sources, item-level outcome psychometrics (no physiology), covariate timing/missingness ledger | [estimand_and_hypotheses.md](estimand_and_hypotheses.md) |
| WP3 | M03 | Exact case flow per sensor policy | Deterministic ledger script over the audited tensor/eligibility tables, using the **pre-existing** QC thresholds | [analysis_population.md](analysis_population.md), `evidence/` |
| WP4 | M04 | Independence and attainable precision of the real crossed learner × content design; minimum useful effect | Identity evidence review; outcome variance components; Monte Carlo design simulation of the frozen estimator and inference on the actual incidence | [precision_and_independence.md](precision_and_independence.md) |
| WP5 | M05 | Does the closest work already answer the estimand? | Targeted literature closeout (delegated, then verified) | [novelty_closeout.md](novelty_closeout.md) |
| WP6 | M06 | Splits, access regimes, leakage controls, baselines, metrics, inference | Synthesis of WP1–WP4. The inference method is chosen by **simulated calibration**, not convenience | [evaluation_contract.md](evaluation_contract.md) |
| WP7 | M07 | Is there a usable independent educational validation cohort? | Repository/API/licence check of the prioritized leads (delegated, then verified) | [external_validation.md](external_validation.md) |
| WP8 | M08 | When would a bespoke method be justified? | Baseline-family definition and failure-mode criteria | [method_necessity.md](method_necessity.md) |
| WP9 | — | One implementable document | Consolidated statistical analysis plan | [protocol.md](protocol.md) |
| WP10 | — | Verdict | Apply the rules below | [readiness_verdict.md](readiness_verdict.md) |

## Decision rules declared before any computation in this phase

These rules were written before the outcome psychometrics, ledger or simulations were run. Later changes must be logged as deviations.

1. **Outcome.** Exact-set correctness stays primary unless a *construct* failure appears, not a predictive one. Construct failures are: more than 15% of analysis cells at the floor or the ceiling, or exact-set within-video internal consistency materially below partial credit (KR-20/α lower by more than 0.10). Partial credit is always the mandatory sensitivity outcome. Neither score is ever chosen by association with physiology.
2. **Minimum useful effect δ.** δ is the relative reduction in held-out MSE against the full nonsignal baseline. It is set to `max(0.05, one-item-equivalent skill)`, where the one-item-equivalent skill is the held-out relative MSE reduction obtained by observing **one** additional quiz item when predicting the remaining items of the same video. It is estimated from outcomes only. Rationale: physiology that is worth less than one quiz question fails the [hard relevance test](../research_gap/primary_problem.md).
3. **Precision adequacy** for a regime to carry a confirmatory claim, under the actual design and frozen pipeline:
   - (a) the type-I error of the chosen test is ≤ 0.07 at nominal 0.05;
   - (b) power is ≥ 0.80 to exclude Δ ≤ 0 when the true skill is 2δ;
   - (c) when the true skill is 0, P(upper 95% bound < δ) is ≥ 0.80, so a null result is informative.

   A regime that fails (b) or (c) is downgraded to descriptive/conditional reporting. If the primary regime fails, the claim is narrowed, or the verdict is REVISE or STOP.
4. **Population/QC.** The audit's existing thresholds (`audit_config.json`) are frozen. Sensitivity thresholds are declared in advance and never selected afterwards.
5. **Units of evidence.** Precision is computed over qualified people and canonical videos. Windows and item rows are never counted as independent.
6. **External data.** A dataset is called usable only after access, files, licence, outcome and cohort independence have been checked at the repository level.

## Verdict rule

- **GO**: the primary regime meets rule 3; the estimand, population, outcome, chronology, covariates, regimes, splits, leakage controls, baselines, metrics and inference are frozen; and OQ-06 is bounded for the frozen feature route.
- **REVISE**: a frozen element cannot be made defensible without changing the research question. Any such change made in this pass is recorded, and the verdict then applies to the revised question.
- **STOP**: no defensible regime reaches adequate precision, or provenance prevents valid measurement.
