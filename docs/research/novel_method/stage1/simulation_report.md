# Stage-1 design simulation — results

2026-10-14. **Every outcome in this report is synthetic.** No outcome of any cohort was read. Methods: [simulation_methods.md](simulation_methods.md). Rules fixed before each run: [evidence/predeclared_rules.md](evidence/predeclared_rules.md), hash-stamped in `predeclared_rules.sha256`. The tables below are copied from the generated file [evidence/tables/report_tables.md](evidence/tables/report_tables.md), which `scripts/report.py` writes from the stored replicates. The CSVs and figures are in [evidence/tables/](evidence/tables/) and [evidence/figures/](evidence/figures/), and the machine-readable summary is [evidence/summary.json](evidence/summary.json).

| Run | Replicates | Manifest SHA-256 | Code |
|---|---|---|---|
| `n1decision` | 1,000 | `8d573627…` | Working tree at launch |
| `main` | 16,800 (86 grid entries; all complete, none duplicated) | `4e692198…` | `evidence/sim/code_snapshot/` |
| `addendum` (rule R-E) | 800 | `f2b4b269…` | `evidence/sim_addendum/code_snapshot/` |

Unless stated otherwise, "OR" is the odds ratio per SD of the latent moment state at reliability ρ = .4, and power is the rejection rate at one-sided α = .05.

## 1. Primary form under the fatigue / position confound (rule R-A → S1-D06)

The same simulated outcomes were analysed by both forms: N1 and N0 with 200 replicates each, OR 1.5 with 100.

| Set | Scenario | Form | T1 | T2 | T2c | NH1 |
|---|---|---|---|---|---|---|
| E4 | N1 | raw (plan-literal) | **.085** | **.090** | .075 | .070 |
| E4 | N1 | detrended | .040 | .045 | .040 | .030 |
| Development | N1 | raw | **.100** | **.100** | .075 | .075 |
| Development | N1 | detrended | .055 | .070 | .065 | .045 |
| E4 / development | N0 | detrended | .040 / .040 | .040 / .025 | .030 / .030 | .030 / .020 |
| E4 / development | OR 1.5 | raw → detrended (NH1) | | | | .59 → .53 / .83 → .86 |

- The raw form fails R-A step 1.
- The detrended form passes step 2. Its largest rate is .070: development T2 under N1, 14/200.
- The main grid then re-estimated development N1 with 500 replicates: detrended T1 .060, T2 .048, NH1 .034, inside the bound.

**Why the raw form fails.** A learner's linear engagement trend over the recording reaches the moment regressor. When the outcome also depends on that trend × item position, the regressor carries the confound into λ.

**What this means for T2 and the circular shift.** Neither stopped the confound: raw T2 was .09–.10 and T2c .075. Plan §18 had treated the circular-shift null as the main guard against "fatigue × late items" readings. Stage 1 shows the within-recording trend control is the effective guard, and the randomization nulls do not substitute for it (§8).

## 2. Type-I error of every planned test

False detection at α = .05: 500 replicates per null, Wilson 95% interval half-width ≈ .02. **Pass criterion R-D / spec §1.7(1): ≤ .07 in N0–N3.** "dir" is the frozen-development-direction parametrization.

**Maximum over N0–N3** (the per-scenario values are in the generated tables, §1):

| Test | E4 | Development | E4 + E5 pooled | E5 (200 replicates, N0/N1 only) |
|---|---|---|---|---|
| T1 (CV) | .058 | .060 | .058 | .065 |
| T2 (CV) | .050 | .048 | .066 | .055 |
| T2c (CV, circular shift) | .048 | .046 | .066 | .035 (N1) |
| **NH1 = T1 ∧ T2 (CV; plan)** | **.042** | **.040** | **.042** | .035 |
| T1lr | .064 | .058 | .066 | .060 |
| T2lr | .064 | .056 | .060 | .050 |
| T2clr | .052 | .062 | .068 | .025 (N1) |
| **NH1lr = T1lr ∧ T2lr** | **.050** | **.036** | **.052** | .045 |
| dir T1 / T2 / NH1 | .062 / .066 / .056 | — | .070 / .068 / .050 | ≤ .055 |
| dir T1lr / T2lr / NH1lr | .058 / .066 / .050 | — | **.076 / .078** / .064 | ≤ .055 |
| CAIRN-validity T2 / T2lr (NH4; N0, N3) | .050 / .062 | .058 / .050 | .060 / .068 | .070 / .070 (N0) |
| Development stop rule: go | — | **.008** | — | — |

In N0–N3, every planned test is calibrated at ≤ .07, with one exception: the **frozen-direction LR test on the pooled lock under N2** (T1lr .076, T2lr .078). That makes candidate design 8 inadmissible (§5). Under the added non-linear fatigue null N1q, some single tests exceed the bound (next table).

**Uniformity.** Randomized p-values under N0 pass a KS test for uniformity (p > .03 for all 42 test × set combinations). Two are below .05: pooled T2c .048 and development T2c .036. With 42 checks, about two are expected below .05 by chance.

**Non-linear fatigue N1q** (added in Stage 1; linear detrending cannot remove it):

| Test (primary, detrended) | E4, 200 (declared) | E4, 500 (R-E) | Development, 200 | Pooled, 500 (R-E) |
|---|---|---|---|---|
| T1 / T2 / T2c / NH1 | .060 / .075 / .060 / .050 | .064 / **.074** / .066 / .056 | .050 / .055 / .060 / .025 | .066 / .070 / **.072** / .056 |
| T1lr / T2lr / T2clr / NH1lr | .055 / .070 / .060 / .045 | .060 / .066 / .062 / .048 | .035 / .045 / .040 / .030 | **.082 / .080** / .070 / .068 |

**Linear detrending does not fully remove a non-linear fatigue confound.**

- The intersections stay ≤ .068 everywhere.
- Single tests reach .072–.082 under N1q. The worst are the pooled LR tests (T1lr .082, Wilson interval .061–.11; T2lr .080) and the E4 CV T2 (.074).
- **Rule R-E outcome (pre-declared):** on the pooled lock, the CV tests of design 5 stay ≤ .07 (T1 .066, T2 .070, NH1 .056), but the LR tests of design 7 do not. **Design 7 therefore cannot go to preregistration without an added non-linear temporal control**, for example a quadratic within-recording detrend, specified and re-simulated. Until then this is an open Stage-1 item (§5).

**Full-data reference tests** (oracle regressor, no permutation):

| Scenario | GLMM Wald | Naive Wald (independent responses) | Learner-cluster robust Wald | Literal z − ē |
|---|---|---|---|---|
| N0 (E4 / development / pooled) | .062 / .026 / .036 | .056 / .028 / .040 | **.086** / .056 / .056 | .052 / .050 / .054 |
| N1 | **.128 / .292 / .174** | **.124 / .284 / .168** | **.174 / .336 / .194** | **.136 / .344 / .144** |
| N1q (E4 / development / pooled) | **.106 / .100 / .166** | **.106 / .100 / .164** | **.160 / .140 / .198** | **.074** / **.135** / **.088** |

Under no temporal confound the parametric tests hold, but the learner-cluster sandwich over-rejects with 39 clusters. **Every parametric test breaks under the temporal confound** (up to .34). The permutation tests on the detrended form do not.

## 3. Power curves and minimum detectable effects

Figure: [power_nh1_rho04.png](evidence/figures/power_nh1_rho04.png). The grey curve is the plan §20.3 analytic power for independent responses.

**Power at ρ = .4** (OR 1 = pure null N0):

| Set | Statistic | 1.15 | 1.25 | 1.35 | 1.50 | 1.75 | 2.00 | 2.50 | 3.00 |
|---|---|---|---|---|---|---|---|---|---|
| E4 | NH1, CV (plan) | .08 | .12 | **.32** | .51 | .84 | .95 | 1.0 | 1.0 |
| E4 | NH1, LR | .10 | .18 | .34 | .53 | .85 | .95 | 1.0 | 1.0 |
| E4 | NH1, CV, frozen direction | .09 | .15 | .40 | .65 | .91 | .99 | 1.0 | 1.0 |
| E4 | NH1, LR, frozen direction | .10 | .17 | .45 | .67 | .94 | .99 | 1.0 | 1.0 |
| E4 + E5 pooled | **NH1, CV (design 5)** | .12 | .33 | **.51** | .85 | .99 | 1.0 | 1.0 | 1.0 |
| E4 + E5 pooled | NH1, LR (design 7) | .14 | .36 | .66 | .93 | 1.0 | 1.0 | 1.0 | 1.0 |
| E4 + E5 pooled | NH1, CV, frozen direction | .10 | .34 | .60 | .92 | .99 | 1.0 | 1.0 | 1.0 |
| E4 + E5 pooled | NH1, LR, frozen direction | .13 | .43 | .74 | .96 | 1.0 | 1.0 | 1.0 | 1.0 |
| Development | NH1, CV | .09 | .26 | .49 | .83 | .99 | 1.0 | 1.0 | 1.0 |
| Development | NH1, LR | .10 | .26 | .64 | .91 | 1.0 | 1.0 | 1.0 | 1.0 |
| E4 | Oracle GLMM Wald (true composite) | .32 | .54 | .82 | .93 | .99 | 1.0 | 1.0 | 1.0 |

Monte Carlo SE ≤ .035 per point (200 replicates).

**MDE: OR at 80% power** (log-OR interpolation):

| Set | Statistic | ρ = .2 | ρ = .4 | ρ = .7 |
|---|---|---|---|---|
| E4 | NH1, CV (plan) | 2.37 | **1.72** | 1.47 |
| E4 | NH1, LR | 2.24 | 1.70 | 1.47 |
| E4 | NH1, CV / LR, frozen direction | 2.09 / 2.10 | 1.64 / 1.62 | 1.42 / 1.41 |
| E4 + E5 pooled | NH1, CV | 1.82 | 1.48 | 1.35 |
| E4 + E5 pooled | **NH1, LR** | 1.73 | **1.43** | 1.31 |
| E4 + E5 pooled | NH1, CV / LR, frozen direction | 1.75 / 1.61 | 1.44 / 1.39 | 1.33 / 1.30 |
| Development | NH1, CV / LR | 1.82 / 1.73 | 1.49 / 1.44 | 1.33 / 1.31 |
| E4 / pooled / development | Oracle GLMM Wald | 1.58 / 1.39 / 1.40 | 1.34 / 1.25 / 1.23 | 1.26 / 1.18 / 1.17 |

**MDE in usefulness units at ρ = .4**: the population metrics of the oracle predictor at the MDE, from the generated tables §3.

| Set and statistic | MDE (OR) | λ per SD of observed signal | S_item | ΔAUC_wp |
|---|---|---|---|---|
| E4, NH1 CV | 1.72 | .34 | ≈ .010 | ≈ .010 |
| E4 + E5 pooled, NH1 LR | 1.43 | .23 | ≈ .005 | ≈ .006 |
| Development, NH1 CV | 1.49 | .25 | .006 | .007 |

Both depend on ρ only through the attenuated effect log(OR)·√ρ, so the curves collapse onto one curve per set ([power_vs_observed_effect.png](evidence/figures/power_vs_observed_effect.png)).

## 4. The minimum useful effect and E4 adequacy

The plan §20.2 threshold is **unchanged**: S_item ≥ .01 **and** ΔAUC_wp ≥ .02 over IRT-M2 (R-B1). Figure: [metric_mapping_rho04.png](evidence/figures/metric_mapping_rho04.png).

**Smallest OR meeting both thresholds:**

| Set | ρ = .2 | ρ = .4 | ρ = .7 | Binding threshold |
|---|---|---|---|---|
| E4, population (infinite data) | 3.13 | **2.16** | 1.80 | ΔAUC_wp (S_item ≥ .01 already at 1.70) |
| E4, mean CV estimate (refitted) | > 4.0 (not reached on the grid) | 2.57 | 1.98 | S_item (estimation cost) |
| E4, mean CV estimate (frozen direction) | 3.36 | 2.26 | 1.82 | ΔAUC_wp |
| Pooled, population | 2.98 | 2.11 | 1.74 | ΔAUC_wp |
| Pooled, mean CV estimate (refitted / frozen direction) | 3.05 / 3.05 | 2.13 / 2.12 | 1.74 / 1.75 | ΔAUC_wp |
| Development, population / mean CV | 2.95 / 3.38 | 2.09 / 2.21 | 1.74 / 1.80 | ΔAUC_wp |

**At the minimum useful effect, E4 is well powered**: NH1 power is .97 (CV) and .97 (LR) at OR 2.16, and 1.00 at 2.57. The same holds at ρ = .2 (OR 3.13 → power 1.0) and ρ = .7 (OR 1.80 → .97).

**At the plan's plausible-effect checkpoint, E4 is not.** Spec §1.7(4) checks OR ≤ 1.35 at ρ = .4, and E4 NH1 power there is .32. Plausible effects (OR 1.15–1.5; EyeBench increments of 1–3 AUROC points; INF-103) therefore sit well below the plan's useful threshold. At those effects E4 cannot reliably detect the moment effect. **Under the pre-declared rule R-B3, E4 alone is inadequate and the confirmatory design is revised (§5).**

**The CV usefulness estimate is biased downward in small cohorts.** Under the pure null, mean CV S_item is −.011 in E4 (refitted), −.006 pooled, −.008 in development, and only −.001 to −.002 with the frozen direction. Most of the cost comes from estimating six person-path (ē^anch) and six moment coefficients from 31 training learners per fold. IRT-whole, with six person-level means, costs −.013 in E4.

The consequence: in E4 the refitted model's point estimate reaches S_item .01 only at OR 2.57, against 1.70 in population terms. The threshold is not adjusted; the bias is disclosed.

## 5. Redesign of the confirmatory procedure (rules R-B, R-B2, R-E)

The eight candidate designs were declared before the main grid. A design is admissible if T1, T2 and NH1 are each ≤ .07 in N0–N3 (500 replicates).

| # | Cohort | Statistic | Moment block | Max false detection | Admissible | Power OR 1.35 | Power OR 1.5 | MDE (OR) | Power at minimum useful OR |
|---|---|---|---|---|---|---|---|---|---|
| 1 | E4 | CV (plan as written) | refitted | .058 | yes | .32 | .51 | 1.72 | .97 |
| 2 | E4 | CV | frozen dev direction | .066 | yes | .40 | .65 | 1.64 | 1.00 |
| 3 | E4 | LR | refitted | .064 | yes | .34 | .53 | 1.70 | .97 |
| 4 | E4 | LR | frozen dev direction | .066 | yes | .45 | .67 | 1.62 | 1.00 |
| **5** | **Pooled E4 + E5** | **CV** | **refitted** | **.066** | **yes** | **.51** | **.85** | **1.48** | **1.00** |
| 6 | Pooled | CV | frozen dev direction | .070 | yes | .60 | .92 | 1.44 | 1.00 |
| 7 | Pooled | LR | refitted | .066 (N1q: **.082**) | yes (fails R-E) | .66 | .93 | 1.43 | 1.00 |
| 8 | Pooled | LR | frozen dev direction | **.078** (N2) | **no** | .74 | .96 | 1.39 | 1.00 |

**No admissible design reaches .80 at OR 1.35.** By the declared choice rule (R-B2), the admissible design with the smallest MDE is **design 7**, a pooled E4 + E5 lock with the LR statistic and the moment block refitted. Its MDE is OR 1.43 at ρ = .4. Rule R-E then qualifies that choice (below). **The shortfall against the 1.35 target is reported, not hidden.**

**Rule R-E (N1q on the pooled lock, 500 replicates): design 7 does not stand as-is.** Its LR tests reach .082 (T1lr) and .080 (T2lr) under non-linear fatigue; NH1lr is .068. Design 5's CV tests stay within the bound: T1 .066, T2 .070 (at the bound), NH1 .056.

**Resulting recommendation:**

| Role | Design | Status |
|---|---|---|
| **Ready now** | **Design 5:** pooled E4 + E5 lock, the plan's CV statistic, NH1 confirmatory with NH2–NH5 descriptive. Built only from declared spec options (a) and (c) | Passes every pre-declared check (N0–N3 and N1q). MDE OR 1.48; power .51 at OR 1.35 and .85 at 1.5 |
| **Upgrade** | **Design 7:** the same lock with the LR statistic | Needs (i) your approval of the statistic and (ii) a non-linear within-recording trend control, specified and shown by simulation to keep N0–N3 and N1q ≤ .07. If both hold: MDE about 1.43 (power .66 at OR 1.35), less any power the extra control costs |

The E4-only plan design (design 1) also exceeds the bound in one component under N1q (T2 .074; NH1 .056).

**Conditions and risks of designs 5 and 7:**

- **Pooling changes E5's role.** E5 moves from separate secondary cohort into the confirmatory test, with experiment-specific item easiness.
  - E5 is a different construct: answer search after an incentivized question preview.
  - **If E5's moment effect is half of E4's, pooled power at OR 1.5 falls from .93 to .55.** That is no better than E4 alone (.53). The frozen direction holds up better (.77).
  - The pooled test answers "is there a moment effect in E4 ∪ E5", not "in E4".
- **The LR statistic departs from plan §20.1.** The plan defines T1/T2 on held-out log-loss.
  - The LR statistic is the full-data conditional log-likelihood gain over IRT-M2, under the **same** learner-block, moment-relocation and circular-shift permutations.
  - Usefulness is still judged by the CV S_item and ΔAUC_wp.
  - It is **not** a declared spec §1.7(4) option and needs explicit user approval.
- **Design 5 uses only declared options** (pooling and NH1-only confirmatory), with the plan's CV statistic. It still changes E5's role, so it too must be recorded under a decision ID before any outcome is read.
- **Option (b), one-sided tests:** vacuous. The tests are already one-sided (R-B4).

## 6. Does clustering change the earlier analytic power estimate?

| Set | Anchorable responses | Learners | Distinct moments | Analytic SE (independent) | Oracle GLMM model SE | Empirical SD of λ̂ | Variance ratio | MDE: analytic (two-sided) | MDE: oracle GLMM | MDE: NH1 CV / LR |
|---|---|---|---|---|---|---|---|---|---|---|
| E4 | 977 | 39 | 19 | .066 | .073 | .075 | **1.03** | 1.34 | 1.34 | **1.72 / 1.70** |
| Pooled | 2,096 | 86 | 19 | .045 | .050 | .048 | 0.94 | 1.22 | 1.25 | 1.48 / 1.43 |
| Development | 2,205 | 55 | 59 | .044 | .049 | .043 | 0.79 | 1.21 | 1.23 | 1.49 / 1.44 |

The oracle is a GLMM Wald test of λ on the true composite. It sees the full data, item, video and learner effects, local dependence shared within a moment, and latent noise shared within a moment.

- **Clustering itself barely matters for λ.** The regressor is centred within learner × video and within item, so learner, video and item effects are orthogonal to it. In E4 there are 1.37 anchorable responses per learner-moment, so 46% of them share a moment with another item. The within-moment residual correlation implied by σ_q = .5 is only about .07 on the latent scale, so the design effect is about 1 + .37 × .07 ≈ 1.03. The empirical sampling variance matches the model-based variance (ratio 0.79–1.03), and even the naive independent-response Wald test is calibrated under N0 (.028–.056). Treating responses as independent is therefore not what misleads here. The model SE is about 12% larger than the independence formula, because difficulty heterogeneity spreads p away from .5, not because of dependence.
- **The earlier analytic estimate is still far too optimistic**, for a different reason. The plan §20.3 estimate (S0-7: OR ≈ 1.33 at ρ = .4, 80% power) assumes a known 1-df regressor tested by a Wald test. The planned procedure has to:
  - estimate the moment direction over six channels in 31 training learners;
  - test by permutation, on held-out loss;
  - pass two tests (the intersection).

  The E4 MDE rises from 1.34 to **1.72**. That is equivalent to the analytic test with about 1/3.4 of the responses.
- **What drives the shortfall** (E4, ρ = .4):

  | Step | MDE (OR) |
  |---|---|
  | Analytic, independent, one-sided | 1.29 |
  | Oracle GLMM, true composite | 1.34 |
  | LR, frozen direction | 1.62 |
  | LR, refitted | 1.70 |
  | CV, refitted | 1.72 |

  Direction estimation dominates. The CV-versus-LR choice and the intersection cost little.
- **The real unit of the moment null is the moment.** E4 and the pooled lock have only 19 distinct anchor moments in 3 videos; development has 59. Pooling E5 adds learners, not moments.

## 7. Joint behaviour of T1 and T2

| Set | Scenario | T1 | T2 | Both (NH1) | Spearman ρ of p-values | P(T2 rejects given T1 rejects) |
|---|---|---|---|---|---|---|
| E4 | N0 | .054 | .042 | .038 | .97 | .70 |
| E4 | N1 | .042 | .042 | .030 | .97 | .71 |
| E4 | N2 / N3 | .058 / .058 | .046 / .050 | .040 / .042 | .97 | .69 / .72 |
| Pooled | N0 / N1 | .054 / .050 | .066 / .064 | .042 / .032 | .95 | .78 / .64 |
| Development | N0 / N1 | .032 / .060 | .040 / .048 | .026 / .034 | .93–.94 | .81 / .57 |
| E4 | OR 1.35 / 1.5 | .39 / .54 | .35 / .54 | .32 / .51 | .93–.94 | .82 / .94 |
| Pooled | OR 1.35 / 1.5 | .56 / .90 | .58 / .89 | .51 / .85 | .67–.88 | .91 / .95 |

The LR versions behave the same way: the generated tables have them in §7.

**The two tests behave correctly together:**

- each is calibrated;
- their intersection is conservative (NH1 ≤ .042 in N0–N3, CV);
- under alternatives they reject together, so the intersection costs only 3–8 points of power relative to the better single test.

**They are close to redundant, though.** Their p-values correlate .93–.98 under the nulls. Both nulls break the link between a learner's outcomes and the content-timed moment terms, so without a content-timed confound they have nearly the same null distribution.

**T2 adds falsification value only against confounds that are content-timed but not learner-level.** It does not protect against learner-specific temporal trends: the raw form failed T2 and T2c under N1. The detrending protects against those. Under N4, where data loss itself is content-timed, both reject, correctly, because the moment effect is real; NH4 then attributes it (§9).

## 8. Development stop rule and δ_item (spec §1.7(2–3))

**False "go"** (T2 p < .10 and CV ΔAUC_wp ≥ .01) **is ≤ .008 in every null** (N0 .000, N1 .002, N2 .008, N3 .002, N1q .005). Criterion: ≤ .10. **Pass.**

**Probability of "go"** in development:

| ρ | 1.15 | 1.25 | 1.35 | 1.50 | 1.75 | 2.00 | 2.50 | 3.00 |
|---|---|---|---|---|---|---|---|---|
| .4 | .005 | .010 | .115 | .245 | .515 | **.81** | .955 | 1.0 |
| .7 | .020 | .10 | .24 | .54 | .85 | .97 | — | — |

The ΔAUC_wp ≥ .01 arm binds. "Go" reaches 80% at OR ≈ 1.99 (ρ = .4), close to the minimum useful effect (2.09 in development). **The stop rule is therefore consistent with the usefulness standard:** it lets the lock be spent mainly when the effect is plausibly useful. At plausible effects (OR ≤ 1.5) it most likely stops before the lock (go ≤ .25).

**δ_item as spec §1.7(3) defines it** is the OR where development NH1 power reaches 80%: **1.49 (CV) / 1.44 (LR)** at ρ = .4. In population terms that is S_item .006, ΔAUC_wp .007.

This is the minimum *detectable* development effect. It is **not** adopted as the minimum useful effect: adopting it would lower the item threshold from .01 / .02 to .006 / .007, which the user instruction and R-B1 forbid. The plan §20.2 threshold stands.

## 9. NH4: validity versus gaze

| Set | Test | N0 | N3 | **N4** (content-timed data loss, OR 1.5 per SD of the in-window long-loss term) |
|---|---|---|---|---|
| E4 | CAIRN-validity T2 / T2lr | .036 / .032 | .050 / .062 | **.99 / 1.00** |
| E4 | CAIRN-gaze T2 / T2lr | — | — | **.15 / .135** |
| Development | CAIRN-validity T2 / T2lr | .058 / .050 | .036 / .048 | **1.00 / 1.00** |
| Development | CAIRN-gaze T2 / T2lr | — | — | **.26 / .335** |
| E4 / development | Primary NH1 | — | — | .90 / .99 |
| Development | Stop rule: go | — | — | .62 |

- **NH4 works as specified.** The validity-only model detects content-timed data loss with power ≥ .99 and is calibrated when the loss is not content-timed (N3 ≤ .068).
- **The spec's expectation fails for the gaze channels.** Spec §1.4 expected T2 to reject "for the validity channel only". The gaze-only model (`logdens`, `rho5`, `sacc`, `disp5`) rejects in 15% (E4) and 26% (development) of N4 replicates: seconds with partial loss also move the gaze channels.
- **Required change before preregistration.** Any claim that the reference-relative or gaze share is *behaviour beyond data loss* (plan §22, "show the reference-relative channels' share separately") must use a test of the gaze block **conditional on the in-window validity term**, and that test must be simulated under N4 first. NH4 itself is unaffected.

## 10. Sensitivity (E4)

**Power at OR 1.5, ρ = .4** (100 replicates each; base = 200 replicates):

| Scenario | NH1 CV | NH1 LR | NH1 LR, frozen direction |
|---|---|---|---|
| Base | .51 | .53 | .67 |
| No local dependence (σ_q = 0) | .50 | .54 | .73 |
| 2PL discriminations | .45 | .52 | .78 |
| Guessing floor | **.32** | **.40** | .45 |
| Effect heterogeneity (learner × video) | .42 | .50 | .54 |
| Single-channel truth (`logdens`) | .43 | .48 | .60 |
| N2 person confound + effect | .49 | .50 | .63 |
| Pooled; E5 effect halved | .49 | .55 | .77 |

**Nulls** (E4 N0, 200 replicates each, B = 199):

- **NH1:** ≤ .055 (CV) and ≤ .065 (LR) in every sensitivity scenario.
- **Single tests:** individual rates up to .085 (T2lr without local dependence; Wilson interval .054–.13). With about 60 sensitivity rates at 200 replicates, three or four above .07 are expected by chance at a true .05. None exceeds .07 in the 500-replicate base nulls.

**The guessing floor costs the most power** (four-option items with guessing compress the logit scale). Plausible real-data departures lower E4 power at OR 1.5 to .32–.50. The base-case MDEs are therefore optimistic rather than conservative.

## 11. Person confound (N2) and identification

| Set | Within-cell-centred GLMM λ̂ under N2 (λ = 0) | Plan-literal z − ē λ̂ |
|---|---|---|
| E4 | +.002 | −.007 |
| Pooled | −.001 | −.008 |
| Development | −.002 | −.011 |

- With an effect (OR 1.5), λ̂ is .222 under N2 against .223 without it.
- The moment effect is identified within learner × video, as plan N-c claims. The plan-literal regressor carries a small between-cell component, which is the reason for S1-D03.
- The permutation tests are calibrated under N2. The one exception is the pooled frozen-direction LR (§2).

## 12. Limits of this simulation

- **Synthetic outcomes, real everything else.** The generator is a Rasch GLMM with the declared extensions. Real outcomes may depart in ways not simulated: item-specific prior knowledge correlated with engagement, non-linear dose–response, or effects confined to one category.
- **The latent state is the equal-weight composite of the six channels.** If the true direction is concentrated on one channel, power falls (§10; `logdens` only: .43 vs .51).
- **Anchors are provisional machine anchors.** Human anchors (G-AN) may change the number of moments; E4 has only 19.
- **The lock budget is larger than simulated.** The lock uses B = 999 and R = 10 (plan §20.1); the simulation used B = 199 / 99 and R = 3. Calibration is a property of the permutation test at any B. A larger budget can only raise power slightly.
