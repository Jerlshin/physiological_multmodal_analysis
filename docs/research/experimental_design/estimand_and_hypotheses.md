# M02 — Construct, chronology, estimand and hypotheses (G01 challenged and revised)

2026-10-04. Inputs: [primary formulation](../research_gap/primary_problem.md), [audit contract](../research_gap/audit_contract.md), outcome-only psychometrics ([script](evidence/outcome_psychometrics.py), [results](evidence/outcome_psychometrics.json), [per-video reliability](evidence/outcome_reliability_by_video.csv)), protocol sources verified in this phase, and the [precision simulation](precision_and_independence.md). **No physiological variable entered any computation in this document.**

## 1. Chronology, now source-verified

| Cohort | Learning instruction | When the quiz was taken | Forecast point for cell (person p, video v) | Source |
|---|---|---|---|---|
| E3 | Intentional: told about tests | After **each** video, in the attend block; before the distracted re-viewing | End of viewing v, before quiz v | P01 Methods (BBBD E3 = P01 Exp. 3): "questions … would be presented after each video and followed the procedure of experiment 1"; attend-block quizzes precede the distracted block (FT, L) |
| E4 | **Incidental**: not informed of the test | After the second attentive block of three new videos, for those three videos | End of viewing v; other block-2 videos may intervene before the quiz | S01: "They were tested on the last 3 videos they watched. Participants were not informed they would be tested." (FT, L) |
| E5 | Previewed, incentivized second viewing | End of the second (repeat) viewing block | End of the **repeat** viewing of v | S01: incentive per correct answer, questions shown, same videos watched again (FT, L) |
| E1 | Intentional | After each video | End of viewing v | P01 Exp. 1 (FT, L) |

**Consequence (I).** E3 and E4 differ in learning instruction (intentional vs incidental), test delay (immediate vs end of block) and block position. Together they form the "first-view" substrate, but **not a homogeneous protocol**. Every analysis uses experiment × video content effects and reports experiment-stratified results. E5's final quiz follows preview, incentive and re-exposure. First-view E5 signals are never labelled with that quiz as first-view learning.

**Frozen forecast information set** for cell (p, v):

- signals from **that exposure only**;
- that exposure's quality and availability;
- the admissible person covariates;
- experiment and canonical-video identity;
- the training data permitted by the access regime.

The person's other exposures are excluded from the primary analysis, so the E3 "after each video" chronology is honoured.

## 2. Outcome: exact-set correctness stays primary (rule 1 applied)

| E3+E4 first view (72 people / 302 cells) | Exact-set | Partial credit |
|---|---:|---:|
| Mean (SD) | 0.456 (0.201) | 0.528 (0.184) |
| Floor / ceiling cells | 0.3% / 0.3% | 0% / 0.3% |
| Distinct values | 13 | 68 |
| Median within-video internal consistency (KR-20/α) | **0.45** | 0.52 |
| Crossed variance components, person / video / residual | 0.0129 / 0.0080 / 0.0202 | 0.0135 / 0.0013 / 0.0193 |

Neither pre-declared construct failure occurs:

- floor and ceiling are both ≪15%;
- the α gap is 0.07, below the 0.10 threshold.

**Exact-set correctness remains primary; partial credit is the mandatory sensitivity outcome (F/I).** Partial credit gives full credit for selecting every option, while 26% of E3 and about 9% of E4 items have multiple keys. Its smaller video variance mainly reflects that leniency on multi-key items. The choice involved no physiology.

### Criterion reliability is the binding scientific constraint (F, new)

Within-video variance of the exact score splits as follows (per-video α, REML person variance):

| Cohort | Stable person | Reliable person × video ("state") | Item-sampling error |
|---|---:|---:|---:|
| E3 | 34% | 13% | 53% |
| E4 | 43% | 15% | 42% |
| E5 | 57% | 6% | 37% |
| E1 | 62% | 6% | 32% |

Implications (I):

1. **Ceiling.** No predictor can explain more than about 47–58% of within-video variance in E3/E4. A physiological skill is therefore also reported as a share of the reliable variance.
2. **Person versus state.** Roughly three quarters of the reliable individual variance is a stable learner level shared across videos. An improvement for new learners mainly means physiology identifies *higher-performing learners*. That level could reflect prior knowledge, ability, test-taking or a trait-like engagement disposition, which BBBD cannot separate. The video-specific "state" component is small. Testing it is a separate and much less precise question.
3. **Per-video criterion quality varies.** One E3 video (`bYgV9nvgJ3E`, "Planets & Suns") has exact α = 0.18 and partial α ≈ 0. It is kept in the primary analysis; no post hoc exclusion is made. A sensitivity analysis excludes content with exact α < 0.30, a measurement rule declared here, and per-video results are always shown.

### Minimum useful effect (rule 2 applied)

Observing **one** additional quiz item reduces held-out MSE for the remaining items by only **0.021** on average (E3+E4; [items](evidence/one_item_equivalent_items.csv)). Inter-item correlations are low. The floor therefore applies: **δ = 0.05**, defined as a relative reduction in held-out MSE against the full nonsignal baseline (person-balanced).

Interpretation:

- **Observed score:** δ corresponds to a predictive partial correlation of about 0.22 with the observed score.
- **Reliable variance:** it corresponds to about 10% of the reliable within-video variance.
- **Quiz items:** it is worth more than two quiz items.

A physiological increment below δ is treated as practically negligible for individual measurement, even if non-zero.

## 3. Admissible covariates and quality variables (frozen)

| Variable | Status | Reason |
|---|---|---|
| Experiment × canonical-video content effect | **Admissible** in A (training-cell mean). In B/C only the training experiment mean | Known content library versus new content |
| Age; sex (M/F, otherwise missing indicator) | **Admissible** | Pre-existing; complete in the analysis sets |
| ASRS inattention and hyperactivity (item-derived 0–4 sums) | **Admissible** (stable trait) | Complete in E3–E5. Supplied offsets are inconsistent, so item sums are used. Collection timing is not certified, so it is treated as a pre-existing characteristic (I) |
| Digit span (maximum span; values outside 3–7 set missing, plus indicator) | **Admissible** | Valid in 66 of 68 primary people. The weighted score is unreconstructable and excluded |
| GPA | **Sensitivity only** | Valid in 48 of 68; selective, scale-heterogeneous, plausibly MNAR |
| Tired / caffeine / study time | Excluded | Inconsistent coding; small cohorts |
| E4/E5 feedback (watched-before, question difficulty, self-rated prior knowledge, educational) | **Inadmissible** | Post-quiz or of uncertain timing; absent in E3. "Question difficulty" presupposes the quiz |
| Q (cell quality): gaze correction fraction; pupil correction fraction (with absence indicator); EEG zeroed-sample fraction (median over channels, processed); EEG 16 Hz excess (median dB) | **Admissible**, in every baseline | Measurement quality; looking-away and tracker failure are not separable, so Q may carry behaviour (see §5) |
| M (availability) | Constant within complete-case sets; used in the coverage-set (CAS) policy analysis | — |

There is **no common pre-knowledge measure** in eligible E3–E5. "Beyond prior knowledge" is not a claim this study can make.

## 4. Estimand

For regime g ∈ {A, B, C}, analysis set S and sensor feature set F, let the frozen pipeline 𝒜 be trained on a sample of the study's size. The estimand is

  **Skill_g(F) = 1 − E_p[ MSE_p(𝒜_{C,Q,F}) ] / E_p[ MSE_p(𝒜_{C,Q}) ]**

where:

- p is a new learner drawn from the analysis-set population;
- MSE_p is that learner's mean squared error over their tested videos (person-balanced weighting);
- predictions are clipped to [0, 1] on the exact-score scale.

This is the **expected held-out incremental skill of the procedure at this sample size**: the target that cross-validation actually estimates (Bates et al. 2024, L). It is not the oracle information content of physiology, which is larger, and it is not a causal or mutual-information quantity. The simulation reports both, so a small estimate is not misread as an oracle bound.

Companion summaries:

- cell-weighted skill;
- ΔMSE, ΔRMSE and ΔMAE in quiz items (× 12);
- skill as a share of reliable variance;
- per-video and per-experiment skill;
- the within-person "state" skill: double-centred by person and content, among people with at least two cells.

## 5. Revised research question and hypotheses (EDD-004)

**G01-R.** For new adult learners viewing previously characterized short educational videos, do whole-video EEG, ECG and gaze measurements add individual information about immediate video-specific quiz performance beyond permissible nonsignal information and measurement quality? How much of any such information:

- depends on peer-reference synchrony;
- survives held-out content without peer references;
- is video-specific rather than stable-learner information?

All of this is assessed against an explicitly low-reliability criterion.

Changes relative to G01 and why:

| Element | G01 (2026-10-03) | G01-R (frozen) | Evidence |
|---|---|---|---|
| Confirmatory scope | A, B and C on equal footing | **Only A is confirmatory.** B and C are bounded secondary analyses conditional on the 8 sampled videos | Simulated precision: B undercovers and is underpowered at the content-population level ([precision](precision_and_independence.md)) |
| Reference-access question | B versus C across new content | Decomposed. (i) In A, the synchrony block versus reference-free features: same people, adequate precision. (ii) B and C descriptive | A linear predictor's within-content ranking is unchanged by video-level feature shifts. B versus C therefore differs essentially through synchrony features, which A tests more precisely (I) |
| "Individual information" | Undifferentiated | Overall incremental skill (H1), plus a **separate, exploratory** state component | Reliable variance is about 75% stable-learner |
| Sensors | EEG + ECG + eye (gaze AND pupil), 57/216/8 | **EEG + ECG + gaze, 68/259/8**; pupil is a secondary block | [Provenance decision](measurement_provenance.md) |
| E5 / E1 | Stress test / supplementary | Descriptive replications; no confirmatory claim | Simulated power far below 0.8 at plausible effects |
| Language | "Learning performance" | "Immediate video-specific quiz performance", with criterion reliability reported | Reliability findings, no pretest |
| Negative conclusions | "Useful effect ruled out" | Only "effects ≥ 2δ = 0.10 ruled out". The 0.05–0.10 range stays unresolved | Futility calibration ([precision](precision_and_independence.md)) |

**H1 (primary, confirmatory).** In regime A on PAS-core with the exact score, Skill_A(RF + SYN) > 0. RF is the reference-free block (6 core features; 7 with pupil); SYN is the synchrony block (3 core features; 4 with pupil). Test: the person-block Freedman–Lane permutation test, one-sided α = 0.05 ([M06 §6](evaluation_contract.md#6-metrics-and-inference), calibrated in [precision](precision_and_independence.md)). Interpretation follows the decision table in §6.

**H2 (secondary, confirmatory family, Holm-adjusted, four tests):**

- (a) Skill_A(RF + SYN) − Skill_A(RF) > 0: the synchrony increment beyond reference-free features, i.e. reference dependence;
- (b)–(d) single-modality additions to the baseline: EEG, ECG and gaze.

**H3 (robustness, estimation only, no new tests).** H1's estimate keeps its sign and its decision category under:

- the partial score;
- quality policies (eye-correction threshold 0.3 and 0.7 instead of 0.5);
- the four-sensor set with pupil;
- the raw-export feature route;
- excluding content with α < 0.30;
- GPA as an added covariate.

**Descriptive aims (intervals, no confirmatory p-values).** These are:

- B: reference-free transfer to each held-out video, plus a two-way-bootstrap pooled interval explicitly conditional on the 8 videos.
- C: reference-assisted new-content synchrony, using cross-fitted unlabeled reference halves.
- State skill.
- Coverage-set (CAS) policy analysis and selection report.
- E5 within-protocol A, and E4↔E5 transport on the three shared videos.
- E1 ocular-only A.

**Competing explanations kept explicit:**

- content difficulty, handled by content effects;
- stable learner characteristics including unmeasured prior knowledge, which cannot be separated;
- quality and availability selection, handled by Q in the baseline, the CAS and the selection report;
- score semantics (partial credit);
- reference access (H2a, B and C);
- genuine portable criterion information.

## 6. Pre-declared interpretation of H1

Revised after the M04 calibration (EDD-014).

Inputs:

- p = person-block permutation p-value;
- Ŝ = point estimate of Skill_A;
- U₃ = corrected-t upper bound with z = 3.0;
- [L, U] = nested-CV 90% interval, always reported.

| Result | Conclusion permitted |
|---|---|
| p ≤ 0.05 and Ŝ ≥ δ | Incremental individual information detected, with a point estimate of practically useful size |
| p ≤ 0.05 and Ŝ < δ | Information detected, but the estimate is below the useful threshold. Reported as non-zero yet practically small |
| p > 0.05 and U₃ < 2δ = 0.10 | Moderate or large increments (≥ 0.10) are **ruled out** at this sample size and for this procedure. Increments in 0.05–0.10 remain possible. This is a bounded negative result, not "physiology carries no information" |
| Otherwise | **Inconclusive.** Never reported as absence |

**Narrowing relative to the original rule (I).** "Useful increment (≥ δ) ruled out" cannot be concluded with controlled error at n = 68:

- P(rule out δ | null) is only 0.60 at the calibrated boundary error;
- the uncalibrated bound would wrongly rule out δ in 17% of datasets where it is true.

The negative claim is therefore limited to 2δ. This change was made before any physiology–outcome computation.

A positive A result with negative B is evidence for **content-library-specific** validity. A positive A driven by SYN (H2a) is evidence for **reference-dependent** validity. Either result is reported as a narrower measure, not as failure to replicate.
