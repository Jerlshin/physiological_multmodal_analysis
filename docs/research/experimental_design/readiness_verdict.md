# Pre-model readiness verdict

2026-10-04. The rules were declared in the [phase plan](phase_plan.md) before any computation.

## Verdict: **GO — ready for baseline implementation of the revised question G01-R**

The original G01 formulation did **not** pass the gates as stated. It was **revised within this pass** (EDD-004, EDD-014), and every element of the revised protocol is frozen. The GO applies to G01-R and the [frozen protocol](protocol.md) only. It does **not** authorize:

- a bespoke architecture;
- a model search;
- a content-population or tri-modal external claim;
- any claim about learning gain, retention, prior knowledge or causation.

**G01-R** (full text in [M02 §5](estimand_and_hypotheses.md#5-revised-research-question-and-hypotheses-edd-004)). For new adult learners on previously characterized short educational videos, do whole-video EEG, ECG and gaze measurements add individual information about immediate video-specific quiz performance beyond permissible nonsignal information and measurement quality? How much of it depends on peer-reference synchrony, survives held-out content and is video-specific rather than stable-learner information? All of this is assessed against a criterion of within-video reliability about 0.45–0.57.

## Why not the original G01, and why not STOP

**What failed or narrowed (F/I):**

1. **Reference-free content transfer cannot be a confirmatory claim.** Eight canonical videos, six of them from one cohort, leave content-population inference undercovered in simulation (two-way bootstrap ≤ 0.92 at nominal 0.90, person bootstrap ≤ 0.79). Per-video skill SD is 0.03–0.11. Regimes B and C are therefore descriptive and conditional on the sampled videos.
2. **"Useful effect ruled out" cannot be established at δ = 0.05.** With error controlled at the boundary, a null dataset rules out δ only 60% of the time. Negative conclusions are narrowed to effects ≥ 2δ = 0.10, which are ruled out 91% of the time with about 4% boundary error.
3. **The criterion is noisy, and its reliable part is mostly a stable learner level.** Within-video variance is about 34–43% stable person, 13–15% reliable person × video and 42–53% item error. "Learning-state" interpretations are therefore exploratory, and positive findings mainly concern identifying higher-performing learners.
4. **The prior tri-modal set (with pupil) is less precise and less well-founded.** EEG + ECG + gaze becomes primary; pupil is a secondary block.
5. **E5 and E1 cannot confirm anything on their own.** Power is below 0.6 at plausible effects.

**What passed (F/I):**

| Requirement | Result |
|---|---|
| Valid confirmatory test | Person-block permutation; simulated false detection 0.063 (Monte Carlo-compatible with 0.05) |
| Power at 2δ | **0.93** |
| Useful negative bound | Effects ≥ 0.10 can be ruled out |
| Leakage | OQ-06 bounded to within-recording, label-free upstream operations |
| Novelty | No retrieved work estimates this crossed, incremental, decomposed quantity |
| External route | A verified CC-BY ocular dataset with a pretest exists |

A positive, a bounded negative and an inconclusive result are all reportable and scientifically meaningful. Hence **not STOP**.

## Gate status

| Gate | Status | Basis |
|---|---|---|
| M01 provenance | **Bounded** for the frozen route; OQ-06 itself not resolved | [measurement_provenance.md](measurement_provenance.md) |
| M02 construct / chronology | **Closed** | [estimand_and_hypotheses.md](estimand_and_hypotheses.md) |
| M03 population | **Closed** (ledger frozen; assertions in tests) | [analysis_population.md](analysis_population.md) |
| M04 independence / precision | **Closed with narrowing** | [precision_and_independence.md](precision_and_independence.md) |
| M05 novelty | **Closed**, with residual risk (Chen 2026 full methods unread) | [novelty_closeout.md](novelty_closeout.md) |
| M06 evaluation / inference | **Closed** | [evaluation_contract.md](evaluation_contract.md) |
| M07 external | **Partially satisfied**: ocular regime-A route verified and plan time-stamped; tri-modal and content-population routes require a prospective cohort | [external_validation.md](external_validation.md) |
| M08 method necessity | **Closed**: no bespoke method; licensing failure modes pre-declared | [method_necessity.md](method_necessity.md) |

## What is now frozen

| Element | Frozen as |
|---|---|
| Estimand | Person-balanced held-out incremental skill of the procedure at study size, relative to M2 |
| Hypotheses | H1 confirmatory; H2 Holm family of 4; H3 estimation-only robustness; descriptive aims listed |
| Primary population | PAS-core: E3+E4 first tested view, EEG/ECG/gaze basic QC; 68 / 259 / 8 |
| Outcome | Exact-set score (primary); partial credit (sensitivity) |
| δ | 0.05; futility threshold 2δ = 0.10 |
| Chronology | Forecast after the tested viewing and before its quiz; exposure-only information set |
| Covariates C | Age, sex, ASRS item sums, valid digit span. GPA: sensitivity. Feedback: inadmissible |
| Quality Q | Gaze and pupil correction fractions, EEG zeroed fraction, EEG 16 Hz excess |
| Features | 6 RF + 3 SYN (core) + 2 pupil; formulas in protocol §6. Processed derivatives; raw-export sensitivity |
| Regimes | A confirmatory; B and C descriptive with exact operational definitions |
| Independence and resampling | Person-grouped, experiment-stratified 10-fold × 50; B/C leave-one-video-out × person 5-fold × 20 |
| Leakage controls | M06 §4 (9 rules) |
| Models | M0–M5 and single-modality ridge models only |
| Metrics | Person-balanced skill plus companions |
| Inference | Permutation detection; nested-CV interval; calibrated futility bound |
| E3/E4/E5/E1 roles | E3+E4 primary; E5 repeat-exposure descriptive and E4↔E5 transport; E1 ocular descriptive |
| External | John 2025 ocular replication plan; prospective-cohort requirements |

## Conditions that do not block baseline implementation (must be honoured)

1. **Preregistration.** Before any physiology–outcome computation, deposit a time-stamped preregistration citing the protocol commit and disclosing the exploratory history. This needs user authorization for the external deposit.
2. **Re-validate the operating characteristics on production code.** Reproduce the simulated characteristics with the production pipeline before touching real outcomes (protocol §17.3). If the permutation test's false-detection rate exceeds 0.07 in the production simulation, H1 falls back to the bootstrap test (0.035–0.058 false detection, 0.81 power at 2δ). That fallback is declared now.
3. **Outcome-blind feature freezing.** Freeze the feature table with its QC report (and hash) before joining outcomes.
4. **OQ-06 framing.** Claims are about the *released processed measurements*. Sending the author query (user authorization required) would strengthen the publication claims.
5. **Not a publication claim.** A strong Q1 claim needs at least the John 2025 ocular replication. A tri-modal or content-general claim needs a prospective cohort.

## What the next phase (baseline implementation) should do

1. Implement the feature, split and inference modules exactly per [protocol §6–§11](protocol.md), with the unit tests listed in §17.
2. Re-run `precision_simulation.py` and `inference_calibration.py --person` against the production functions. Confirm the operating characteristics.
3. Generate the outcome-blind feature table for all sets. Report feature QC and missingness. Freeze and hash it.
4. Deposit the preregistration (user action).
5. Run H1, then H2, H3 and the descriptive analyses. Report every prespecified item using the [decision table](estimand_and_hypotheses.md#6-pre-declared-interpretation-of-h1).
6. With user authorization, download John 2025 and run the [time-stamped external plan](external_analysis_plan_john2025.md) independently of the BBBD results.
7. Revisit [M08](method_necessity.md) only once the baseline results are in.

## STOP / REVISE triggers that remain live

- **Production simulation** shows false detection > 0.07 for both the permutation and the bootstrap tests → **REVISE** the inference before analysis.
- **Feature-level QC.** Frozen features fail QC so widely that PAS-core loses more than 15% of learners → **REVISE** the population, outcome-blind, and re-run the precision analysis.
- **Novelty.** Chen 2026, or a newly found paper, turns out to estimate the same crossed incremental quantity → **REVISE** the contribution framing.
- **Contradictory provenance.** An author or provenance statement reveals a pooled or label-using upstream step → **STOP** the processed route; use the raw-export route only.
