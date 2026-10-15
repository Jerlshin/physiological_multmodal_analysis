# Closure-phase decision rules, declared before the corresponding simulations

Written 2026-10-14, after the Stage-1 record was read and the closure code was written and piloted. The pilots used tiny replicate counts with B = 19, wrote only to scratch space, and their outcomes were not read for any decision. **No closure simulation result exists when this file is first hash-stamped.**

Every outcome in these simulations is synthetic. The generator, real incidence, provisional anchors, real per-second channels and Stage-1 nulls N0–N4 / N1q are unchanged from Stage 1 ([simulation_methods.md](../../stage1/simulation_methods.md)). Rules are fixed first so that no design choice can drift toward favourable numbers.

## 0. What this phase must decide, and why

Stage 1 left three linked problems open:

1. **Temporal confounding (S1-D15, rule R-E).** Linear within-recording detrending removes a linear fatigue confound. Under a quadratic fatigue confound (N1q), single tests still reach .072–.082, the worst being the pooled likelihood-ratio (LR) tests.
2. **Power.** The admissible designs reach at most .66 at OR 1.35 (ρ = .4). Stage 1 showed that **estimating the moment direction over six channels** is the dominant power loss: E4 MDE 1.34 for an oracle 1-df test, 1.62 with a frozen direction, 1.70 with the direction refitted.
3. **The lock design**, including the role of E5, has not been finalized.

## 1. Common elements

**Calibration criterion (continues R-D).** A test passes a null scenario if its false-detection rate at one-sided α = .05 is **≤ .07**.

- Decisive nulls use **1,000 replicates** (Wilson 95% half-width ≈ .014). The probability that a test with a true rate of .05 exceeds .07 is about .002 per comparison.
- B = 199 for nulls. B = 99 for alternatives (an exact test with a coarser grid; it can only understate power).

**Statistic for the decisive comparisons: likelihood ratio (LR).** This is the full-data conditional log-likelihood gain over IRT-M2, under the unchanged T1 (learner-block Freedman–Lane), T2 (moment relocation) and T2c (circular shift) nulls. NH1 = T1 ∧ T2.

- Stage-1 rule R-B2 already ranked the LR design (design 7) first among admissible designs. It was held back only by R-E.
- The CV statistic remains the **fallback**. It is certified in the confirmation run (§4).
- Usefulness is still judged only by cross-validated S_item and ΔAUC_wp against the unchanged thresholds (S_item ≥ .01 **and** ΔAUC_wp ≥ .02).

**New out-of-family temporal nulls.** These are defined in `cairn.simulate`:

- **N1c (cubic fatigue):** the learner's real cubic Legendre coefficient of the engagement course × P3(2a − 1).
- **N1e (exponential vigilance decrement):** the learner's real coefficient on exp(−2(x + 1)) × that shape.

Both keep N1/N1q's quiz-position and person terms. Their strength is matched to N1q by RMS over the anchor-position range: κ = .473 (N1c) and .703 (N1e), against .6 for N1q.

**New truth directions for power.** In Stage 1 the latent moment state was always the equal-weight composite, which would unfairly favour any parametrization built on that composite. The power comparisons here therefore average over:

| Truth | Definition |
|---|---|
| `composite` | Equal weights on the six sign-aligned channels (as in Stage 1) |
| `random` | A sign-coherent random direction w = s ⊙ \|g\|, g ~ N(0, I), drawn per replicate; development and lock share it |
| `logdens` | Single channel |
| `gaze` | Equal weights on the four gaze channels |
| `validity` | In-window long loss only |
| `random` + `dev_truth = random_indep` | Lock and development directions drawn independently |

## 2. R-F — the temporal control (decides the detrend degree d\*)

**Candidates.** d ∈ {1, 2, 3}: a Legendre polynomial trend of degree d is removed from each per-second channel of each recording, over the recording's own seconds, before anchored pooling (mean kept). It applies to both the moment terms and the anchored person-path summary.

- d = 1 is the Stage-1 primary.
- The control is fold-safe by construction: it uses one cell's own seconds and no other learner.

**Variants tested.** Both extremes of the R-G parametrization family:

- **P6:** six channels, isotropic ridge 100 (Stage-1 form);
- **P0:** the 1-df unit-weighted composite.

**Grid** (`closure_grid("rf")`):

| Set | Nulls (replicates each) | Alternatives (200 replicates each) |
|---|---|---|
| Pooled lock | N0, N1, N1q, N1c, N1e (1,000) | OR 1.5, ρ = .4, truths `composite` and `random` |
| E4 | N0, N1, N1q, N1c, N1e (1,000) | as above |
| Development | N0, N1, N1q, N1c, N1e (500) | as above |

**Rule.**

1. **d\* is the smallest d** such that, for both P6 and P0, on both the pooled lock and E4, T1lr, T2lr and NH1lr are each ≤ .07 under every one of N0, N1, N1q, N1c and N1e.
2. If no d qualifies, d\* is the d with the smallest maximum of those rates. The shortfall is then reported as unresolved, and the item-position term of plan §18 is the next control to specify and simulate.
3. Development rates and T2clr are reported but do not decide.
4. The power cost of each d (OR 1.5) is reported. **It does not override the calibration rule.**

**Estimand consequence (declared now).** The moment effect becomes the effect of the anchored engagement's deviation from the learner's own degree-d\* polynomial course over the recording. Learner-specific trends of degree ≤ d\* are, by definition, not part of the estimand.

## 3. R-G — parametrization of the moment block (decides the confirmatory statistic's form)

**Fixed:** pooled E4 + E5 lock, LR statistic, NH1 = T1lr ∧ T2lr, degree d\*.

**Candidates.** All are evaluated on the same outcomes and the same permutation draws per null (`inference.lr_tests_joint`).

| ID | Parametrization | Why it is a candidate |
|---|---|---|
| **P6** | Six channels, isotropic ridge 100 | Stage-1 design 7 |
| **PT** | Six channels, **anisotropic ridge**: ridge 1 along the unit-weighted direction w0 (re-standardized), ridge 100 on its 5-dimensional complement | A prior centred on the outcome-free construct direction. It keeps P6's flexibility off that direction |
| **P0** | 1 df: unit-weighted composite w0 (signs from the Stage-0 outcome-free construct check; weights equal) | Removes direction estimation, the dominant Stage-1 power loss. Unit-weighted composites are robust in small samples (Dawes 1979; Wainer 1976) |
| **PD** | 1 df: the direction of P6 fitted on the full (simulated) development cohort, frozen | Stage-1 designs 6 and 8 |
| **PA** | Adaptive: exact single-step min-p of P0 and P6 over the same permutation draws | Hedges between the fixed and the estimated direction |

**Grid** (`closure_grid("rg")`, pooled lock):

- **Nulls:** N0, N1, N2, N3, N1q, N1c, N1e, 1,000 replicates each.
- **Power:** OR 1.35 and 1.5 at ρ = .4 under the six truth scenarios of §1, 300 replicates each.

**Rule.**

1. **Admissible:** T1lr, T2lr and NH1lr are each ≤ .07 in all seven nulls.
2. **Score:** mean NH1lr power over the 12 cells (6 truths × 2 ORs).
3. **Robustness constraint:** the minimum over the 12 cells must be ≥ P6's minimum − .05.
4. **Choice:** the admissible, robust candidate with the highest score. A candidate within .02 of the best score is preferred if it departs less from the plan, in the order P6, PT, P0, PD, PA.
5. If no candidate other than P6 is admissible and robust, P6 (design 7 with the d\* control) is the choice.

The truth scenarios include single-channel and independent-direction truths so that P0 and PT are not rewarded for the generator's equal-weight assumption.

## 4. R-H — final confirmatory structure and its confirmation run

**Structure (declared now; the R-G result fills in the parametrization):**

- **Confirmatory family:** H_pool (no moment effect in E4 or E5), H_E4 and H_E5.
- **Closed testing:** NH1 on the pooled lock at α = .05. Only if it rejects are NH1 on E4 alone and on E5 alone each tested at α = .05, with the identical frozen procedure.
  - Each is an α-level test of its own hypothesis, and the closure of {H_E4, H_E5} is {H_E4 ∩ H_E5, H_E4, H_E5}.
  - Family-wise error over the three claims is therefore controlled at .05 in the strong sense.
  - **E4 keeps its primary role as the first-named elementary claim.** E5's different construct (answer search after question preview) is reported separately.
- **Heterogeneity (descriptive):** λ̂ in E4 and in E5, with model-based intervals, and their difference. Usefulness metrics are reported per cohort.
- **NH2–NH5** stay descriptive (spec option c).
- **Lock budget:** B = 999 per permutation test; R = 10 for the CV usefulness metrics.
- **CV fallback:** the same design with the CV statistic (T1, T2 on held-out log-loss). It is used if the user does not ratify the LR statistic.

**Confirmation run** (`closure_grid("conf")`, selected parametrization at d\*):

- **Pooled nulls** N0, N1, N2, N3, N1q, N1c, N1e: 1,000 replicates each, with the E4 and E5 elementary tests on the same outcomes and the CV fallback's T1/T2.
- **Power curves:**
  - ρ = .4, ORs 1.15–3.0, truths `composite` and `random`, 300 replicates each;
  - ρ = .2 and .7, `random` truth, 200 replicates each.
- **Sensitivities:** no local dependence, 2PL, guessing, heterogeneity, E5 effect halved, E5 effect absent; 2PL and guessing nulls (500 replicates).
- **Development:** nulls (500 replicates) and ORs (300 replicates) with the stop rule.

**Pass criteria:**

- Pooled T1lr, T2lr and NH1lr ≤ .07 in all seven nulls.
- The E4 and E5 elementary NH1lr ≤ .07 in all seven nulls.
- CV fallback T1, T2 and NH1 ≤ .07 in all seven nulls.
- False go ≤ .10 in every development null.

If the selected design fails, the next-best R-G candidate (admissible and robust) is confirmed in the same way. The failure is reported.

## 5. R-I — NH4 attribution (S1-D16 / [S1-11])

**Test.** The gaze block (`logdens`, `rho5`, `sacc`, `disp5`) is tested **conditional on the in-window validity term**. The validity moment column stays at the true anchors in every permutation, and only the gaze block is permuted or relocated. LR statistic, T1lr/T2lr, at degree d\*.

**Grid** (`closure_grid("nh4")`):

- N4, N0 and N3 (500 replicates each) on the pooled lock, E4 and development;
- gaze-truth power at OR 1.5 (200 replicates).

**Rule.** If T1lr, T2lr and NH1lr are ≤ .07 under N4, N0 and N3 in all three sets, the conditional test becomes the pre-specified NH4-attribution test (descriptive secondary). Otherwise no claim that gaze carries behaviour beyond data loss is made, and NH4 stays validity-only.

## 6. R-J — re-simulation on the frozen human anchors (declared now, run after G-AN)

**Run:** the confirmation grid's nulls (pooled with the E4/E5 elementary tests and the CV fallback; development with the stop rule), plus the OR 1.35 and 1.5 power entries. It uses the frozen design on the frozen human anchor table.

**Pass criteria:** those of §4.

**Outcomes:**

- **Pass:** the design stands, and power on the human anchor structure is reported. **No threshold changes.**
- **Calibration fails:**
  - first, the CV fallback is used if it passes;
  - otherwise the next degree d\* + 1 is specified and simulated.
  
  In either case no outcome is accessed until a passing design is recorded.
- **Power floor:** if pooled NH1 power at OR 1.5 (`random` truth) falls below .50, this is reported as a material change and put to the user **before** Stage 2. There is no automatic redesign.

## 7. R-K — strong baselines (outcome-free validation)

New baselines are validated only on real incidence and real signals with synthetic outcomes. Every one of them must:

1. **Interface:** fit on training rows only, through `ItemData`, which refuses outcomes on test rows. Predict every test row.
2. **Fold safety:** every cross-recording statistic is fitted on training learners. This covers standardization, references, embedding normalization, pretraining corpora and text–transcript similarity scaling. The check perturbs a test learner and confirms no fitted quantity moves.
3. **Negative control:** under N0, the mean CV S_item over replicates is not above 0 by more than 2 Monte Carlo SE.
4. **Positive control:**
   - whole-video baselines must gain over IRT-M2 when outcomes depend on whole-video engagement (N2: person-level engagement);
   - item-level learned-pooling baselines must gain under a strong anchored effect (OR 3, ρ = .7).
5. **Determinism:** the same seed gives identical predictions (CPU).
6. **Budget:** ≤ 20 configurations in nested CV. Parameter counts, wall time and peak memory are recorded.

**Scope.** Baselines are **not** used for any CAIRN design decision here. The strongest competing baseline is selected in development (plan §16). A comparison under the CAIRN generator favours CAIRN by construction, so it is reported only as a positive control, never as evidence of superiority.
