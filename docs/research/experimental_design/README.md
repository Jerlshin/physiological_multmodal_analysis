# Experimental Design & Pre-model Readiness package

Phase completed 2026-10-04. Input: the [research-gap package](../research_gap/README.md) with G01 as the conditional primary problem and gates M01–M08. Output: a frozen, falsifiable protocol for a baseline study, and a readiness verdict.

**No physiology–outcome association was computed in this phase.** No predictive model of real outcomes was fit, no model search was run and no architecture was developed. All computations used:

- audited bookkeeping;
- outcome-only psychometrics;
- physiology-only nuisance summaries;
- simulated data.

**Verdict:** see [readiness_verdict.md](readiness_verdict.md) (summary at the end of this page).

Evidence classes: **F** audited fact · **L** literature · **I** inference/decision · **H** hypothesis · **U** unresolved.

## Reading order

| Document | Gate | Content |
|---|---|---|
| [phase_plan.md](phase_plan.md) | — | Work packages and decision rules written **before** any computation |
| [measurement_provenance.md](measurement_provenance.md) | M01 | OQ-06 bounded by fit-scope inspection; feature route; pupil demoted to a secondary block |
| [estimand_and_hypotheses.md](estimand_and_hypotheses.md) | M02 | Verified chronology; outcome choice; criterion reliability; δ; covariates; estimand; **G01 → G01-R**; H1–H3; decision table |
| [analysis_population.md](analysis_population.md) | M03 | Case flow and frozen analysis sets; selection report |
| [precision_and_independence.md](precision_and_independence.md) | M04 | Independence units; design simulation on the actual incidence; inference calibration |
| [novelty_closeout.md](novelty_closeout.md) | M05 | Closest work; residual risks |
| [evaluation_contract.md](evaluation_contract.md) | M06 | Regimes A/B/C; resampling; leakage controls; model families; metrics; inference |
| [external_validation.md](external_validation.md) | M07 | Verified external leads; plan; prospective-cohort requirements |
| [external_analysis_plan_john2025.md](external_analysis_plan_john2025.md) | M07 | Time-stamped external replication plan |
| [method_necessity.md](method_necessity.md) | M08 | No bespoke method; pre-declared licensing failure modes |
| [protocol.md](protocol.md) | — | **Single implementable statistical analysis plan** |
| [readiness_verdict.md](readiness_verdict.md) | — | Gate status, what is frozen, next phase |

**Evidence** ([folder](evidence/)) — all scripts run from the repository root:

| Script | Output |
|---|---|
| `design_ledger.py` | Case flow, manifest |
| `outcome_psychometrics.py` | Reliability, variance components, δ |
| `precision_simulation.py` | Design simulation |
| `inference_calibration.py` | Decision-procedure calibration |

Tests: `tests/test_experimental_design.py`. External audit material is in `evidence/external/`.

The decision trail is appended, never overwritten:

- [inference register](../research_gap/inference_register.md), EDI-001 onward;
- [decision log](../research_gap/decision_log.md), EDD-001 onward;
- global pointers in [inference_register.md](../inference_register.md) and [decision_log.md](../decision_log.md).

## What the phase found

1. **OQ-06 is bounded, not resolved (M01).** Every inspected upstream routine fits only on a single recording array and never uses labels or other people. Scale-free whole-video features from the released processed derivatives are therefore usable without cross-person leakage. Absolute-unit, sub-second and "neural mechanism" claims stay excluded.
2. **The chronology is source-verified (M02).**
   - E3: quiz after each video, intentional learning.
   - E4: incidental learning, test at the end of the block.
   - E5: test after preview, incentive and re-viewing.
3. **The criterion is the binding constraint (M02).**
   - Exact-score within-video reliability: α ≈ 0.45–0.57.
   - Reliable variance is about three-quarters stable learner level.
   - One quiz item carries little information (skill 0.021), so δ = 0.05 by the pre-declared floor.
4. **Primary set: EEG + ECG + gaze, 68 learners / 259 cells / 8 videos (M03).** Pupil is a secondary block because of provenance and selection. Excluded cells score lower, so complete-case results are conditional on measurability.
5. **Precision on the real crossed incidence (M04).**
   - **Detection:** a new-learner, known-content increment of about 0.10 is detected with power 0.93 using a person-block permutation test (false detection about 0.06).
   - **Futility:** effects ≥ 0.10 can be ruled out; δ = 0.05 cannot.
   - **Content transfer:** cannot be inferred with 8 videos.
   - **E5 and E1:** too small to confirm anything on their own.
   - **Intervals:** standard CV intervals undercover; nested CV covers best (0.86–0.90).
6. **Novelty (M05).** No retrieved work estimates this quantity. However, P01 already shows held-out quiz prediction from eye ISC in a separate cohort, and Chen 2026 occupies the person-versus-event neural-similarity contrast.
7. **External route (M07).** John 2025 (OSF, CC-BY 4.0, raw EyeLink, item-level pretest and posttest, one video) is verified for an ocular replication. Its analysis plan is time-stamped here. Tri-modal and content-general confirmation need a prospective cohort.
8. **No bespoke method is justified (M08).**

## Verdict

**GO — ready for baseline implementation of the revised question G01-R.**

The broad G01 did not pass as stated. It was narrowed in this pass:

- regime A is the confirmatory test; B and C are descriptive and conditional on the 8 videos;
- negative conclusions are limited to effects ≥ 0.10;
- the state component is exploratory;
- the core sensors are EEG + ECG + gaze.

Everything an implementer needs is frozen in [protocol.md](protocol.md). Conditions, next steps and remaining STOP/REVISE triggers are in [readiness_verdict.md](readiness_verdict.md).
