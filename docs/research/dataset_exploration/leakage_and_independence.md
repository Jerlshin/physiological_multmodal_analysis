# Independence and leakage map

**EMPIRICALLY VERIFIED IN THIS AUDIT.** 178 experiment-qualified participant records, 11 canonical videos, 1474 design-expected exposures; independent outcome counts appear in [outcomes](outcome_characterization.md). Blocks are not independent longitudinal visits. Experiments1–3 and5 repeat videos; 4 changes content by block. Person/video exposures are nested in people and crossed with shared videos, not independent windows.

[Formal leakage risk register](evidence/leakage_risk_register.json); [person/video/experiment graph](evidence/independence_graph.json). Cross-experiment same-human identity is unresolved; do not claim independently certified178 unique humans or infer identity from similar traits. The descriptor's participant count remains documentary recruitment evidence.

| Evaluation unit | Feasibility and limits |
| --- | --- |
| Unseen participant | Feasible within cohorts after grouping all blocks/videos by qualified participant; references/scaling/imputation must respect held-out groups. Cross-cohort same-human overlap needs an author statement. |
| Unseen canonical video | Mechanically feasible at11 identities overall, but only3–6 per experiment; item/content/difficulty and audiovisual covariates differ. Local stimulus holdout is insufficient. |
| Unseen participant + unseen video | A crossed holdout is mechanically possible; small independent video N limits precision. Disjoint person and video axes must be enforced simultaneously. |
| Cross-experiment | Protocol/preprocessing/availability shifts and shared videos are substantial; holding out an experiment does not hold out content. 4/5 share one upstream collection. |
| Cross-condition | In1–3 attention/arithmetic/order/repetition are inseparable; within-person condition contrasts do not establish a transferable latent-attention label. |
| Across exposure settings | First/repeat and incidental/intentional/incentive transport is possible descriptively with shared-video controls; not an isolated causal reward effect. |

Adjacent windows, future imputation/scaling, globally fitted artifact transforms, ISC templates, CorrCA/PCA references and repeated quiz targets all have explicit controls in the register. Fit scope of author preprocessing is not fully known; this cannot be retrospectively fixed by a final train/test split. No split was frozen or held-out predictive outcome inspected. This full-release integrity/distribution audit is **EXPLORATORY**; hypotheses chosen using it require a later locked protocol and untouched evaluation/external validation for confirmatory claims.
