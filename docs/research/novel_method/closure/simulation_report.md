# Closure-phase simulations — results

2026-10-14. **Every outcome in this report is synthetic.** No outcome of any cohort was read.

- Methods: [simulation_methods.md](simulation_methods.md).
- Rules fixed before the runs: [evidence/predeclared_rules.md](evidence/predeclared_rules.md) (`591913ad…`, stamped 06:14:40Z, before the first run).
- The tables are generated from the stored replicates by [scripts/report.py](scripts/report.py) into [evidence/tables/](evidence/tables/report_tables.md). Each decision is recomputed there by `cairn.closure_analysis`.

Unless stated otherwise:

- "OR" is the odds ratio per SD of the latent moment state at reliability ρ = .4;
- rates are at one-sided α = .05;
- the null rates rest on 1,000 replicates (Wilson half-width ≈ .014).

| Run | Replicates | Manifest | Code |
|---|---|---|---|
| `rf` (R-F) | Pooled 5,400, E4 5,400; development: see §1.4 | `853adbf7…` | `evidence/sim_rf/code_snapshot/` |
| `rg` (R-G) | 10,600 | `cc897a8c…` | `evidence/sim_rg/code_snapshot/` |

## 1. Rule R-F — the temporal control

### 1.1 Decision: d\* = 3

**Maximum false-detection rate over the decisive cells.** These are T1lr, T2lr and NH1lr under N0, N1, N1q, N1c and N1e:

| Degree | Pooled, P0 | Pooled, P6 | E4, P0 | E4, P6 | Cells > .07 (of 60) |
|---|---|---|---|---|---|
| 1 (Stage-1 form) | **.135** | **.079** | **.094** | **.077** | 11 |
| 2 (quadratic) | **.074** | .064 | .070 | .068 | 1 |
| **3 (cubic)** | .064 | .066 | .060 | .057 | **0** |

**By null scenario** (maximum over sets, parametrizations and the three tests):

| Degree | N0 | N1 (linear) | N1q (quadratic) | N1c (cubic, out of family) | N1e (exponential, out of family) |
|---|---|---|---|---|---|
| 1 | .060 | .041 | **.135** | **.077** | .061 |
| 2 | .064 | .047 | .068 | **.074** | .062 |
| 3 | .066 | .051 | .064 | .054 | .060 |

The circular-shift sensitivity test T2clr (not decisive) peaks at .107 / .076 / .067 for d = 1 / 2 / 3.

**What this shows:**

- **Linear detrending is not enough.** Under quadratic fatigue, the 1-df composite rejects in 13.5% of null replicates (T1lr) and the plan's intersection in 9.8%.
- **The quadratic control is almost enough.** It fails in one cell: the out-of-family cubic null, pooled P0, T2lr .074 (Wilson .059–.092). Without the out-of-family null, d = 2 would have been chosen. The declared out-of-family check changed the decision.
- **The cubic control** keeps every decisive cell at or below .066, including under the exponential null, which it was not built for.

### 1.2 Why P0 is the most exposed

The simulated fatigue terms use each learner's real **composite** engagement course (sign-aligned, equal weights). So a slow confound projects fully onto the unit-weighted direction, and P0 carries it undiluted, while P6 spreads it over six heavily shrunk coefficients.

This is a deliberately severe test for any composite-based statistic, and P0 passes it only at d = 3.

### 1.3 Power cost of the control

NH1lr power at OR 1.5, ρ = .4:

| Set | Truth | P0, d = 1 / 2 / 3 | P6, d = 1 / 2 / 3 |
|---|---|---|---|
| Pooled | composite | .985 / .990 / .975 | .930 / .920 / .900 |
| Pooled | random (sign-coherent) | .945 / .935 / .920 | .910 / .890 / .860 |
| E4 | composite | .840 / .815 / .785 | .635 / .605 / .515 |
| E4 | random | .685 / .705 / .635 | .525 / .500 / .470 |

- On the pooled lock the cubic control costs .01–.05 at OR 1.5.
- In E4 alone it costs up to .12 for P6: three short videos, Stars only 184 s, so a cubic removes a larger share of between-moment contrast.

### 1.4 Outcome-free corroboration and estimand

**Trend leakage.** [evidence/trend_leakage.json](evidence/trend_leakage.json) measures, on the real signals, the within-cell R² of the unit-weighted moment regressor on Legendre polynomials P1–P3 of anchor position, against a reference with positions shuffled among each video's moments:

| Degree | Pooled lock | Development |
|---|---|---|
| Raw | +.042 | +.076 (above the 95% band) |
| d = 1 | .000 | +.035 |
| d = 2 | −.046 | +.005 |
| d = 3 | −.090 | −.038 |

Real recordings therefore carry slow, position-aligned engagement structure beyond chance; it is removed by d = 2–3. At d = 3 the regressor is *less* aligned with position than a shuffled reference: the control also removes some genuine between-moment contrast. That is the power cost of §1.3, accepted under rule R-F because calibration comes first.

**Estimand (declared in R-F).** The moment effect is the effect of the anchored engagement's deviation from the learner's own cubic engagement course over the recording. Fatigue- or time-on-task trends of degree ≤ 3 are by construction not part of it.

**Development part of R-F (descriptive, 500 replicates per null; completed after R-G).** At d = 3, NH1lr ≤ .052 in every null. Two single tests reach .072 (P6 T1lr, N1c) and .076 (P6 T2lr, N1e), inside the ±.02 sampling band at this size. Development tests are exploratory. The stop rule's false-go rate under the final design is ≤ .010 in every null (§4.4).

## 2. Rule R-G — parametrization of the moment block (at d\* = 3)

Pooled lock, LR statistic. All candidates are evaluated on the same outcomes and the same permutation draws.

### 2.1 Calibration

Maximum T1lr / T2lr / NH1lr over N0, N1, N2, N3, N1q, N1c and N1e (1,000 replicates each):

| P6 | PT | P0 | PD | PA |
|---|---|---|---|---|
| .058 | .059 | .060 | .064 | .055 |

**All five candidates are admissible.** The full table is in [rg_null_rates.csv](evidence/tables/rg_null_rates.csv).

### 2.2 Power by truth direction

NH1lr power, 300 replicates per cell. Figure: [rg_power_by_truth.png](evidence/figures/rg_power_by_truth.png).

| Truth | OR | P6 | PT | P0 | PD | PA |
|---|---|---|---|---|---|---|
| Equal-weight composite | 1.35 | .563 | .577 | **.837** | .697 | .773 |
| | 1.5 | .873 | .883 | .960 | .933 | .947 |
| Random, sign-coherent (shared by development and lock) | 1.35 | .540 | .547 | .717 | .660 | .657 |
| | 1.5 | .867 | .877 | .923 | .913 | .927 |
| `logdens` only | 1.35 | .537 | .540 | **.233** | .620 | .477 |
| | 1.5 | .837 | .840 | **.343** | .900 | .737 |
| Gaze only | 1.35 | .563 | .567 | .727 | .653 | .650 |
| | 1.5 | .900 | .903 | .920 | .957 | .917 |
| Validity only | 1.35 | .553 | .557 | .343 | .700 | .483 |
| | 1.5 | .857 | .857 | .577 | .923 | .820 |
| Random, development ≠ lock | 1.35 | .543 | .553 | .663 | **.457** | .637 |
| | 1.5 | .860 | .870 | .927 | .777 | .907 |
| **Mean (score)** | | .708 | **.714** | .681 | **.766** | .744 |
| **Minimum** | | .537 | **.540** | .233 | .457 | .477 |

The frozen development direction's mean cosine with the truth is .74–.85 when development and lock share the direction, and .52–.59 when they do not.

### 2.3 Decision: P6

**Robustness constraint** (minimum ≥ P6's minimum − .05 = .487): only P6 and PT pass it.

- PD has the highest mean, but it falls to .457 when the development direction does not transfer to the lock. That is a real risk here, because E3/E1 (intentional, immediate quiz) and E4/E5 (incidental; question-previewed) are different protocols.
- P0 is the most powerful under the equal-weight truth, but it collapses under single-channel truths.
- PA hedges P0 and P6 and pays for it: .477 under `logdens`.

**Choice between the two robust candidates:** PT is .006 better than P6 on the score, within the .02 tie band, so P6 is chosen as the smaller departure from the plan.

**Why PT ≈ P6.** On ~2,000 anchorable rows, a ridge of 100 shrinks the six coefficients only moderately. Freeing the composite direction therefore adds little, while the complement still adds its five degrees of freedom to the null distribution of the LR gain.

### 2.4 Cost and disclosure

The robustness constraint gives up average power for protection against direction misspecification:

- **at OR 1.35:** the design has .54–.56 power under every truth, where P0 would have between .23 and .84;
- **at OR 1.5:** .84–.90.

The usefulness estimate of P6 is biased downward under the null: mean CV S_item −.0058 pooled, against −.0014 for the 1-df forms. As in Stage 1 (S1-I09), this is disclosed and the thresholds are not adjusted.

## 3. Rule R-I — NH4 attribution

Gaze block conditional on the in-window validity term. 500 replicates per null, 200 per alternative.

| Set | Conditional (gaze given validity): N4 / N0 / N3 (max of T1lr, T2lr, NH1lr) | Unconditional gaze: N4 (T1lr, T2lr, NH1lr) | Validity only: N4 (NH1lr) | Gaze truth, OR 1.5: conditional vs unconditional NH1lr |
|---|---|---|---|---|
| Pooled lock | .062 / .060 / .060 | .180 / .174 / .152 | 1.00 | .955 vs .960 |
| E4 | .044 / .062 / .058 | .104 / .078 / .070 | .98 | .545 vs .570 |
| Development | .032 / .048 / .048 | .276 / .348 / .238 | — | .890 vs .895 |

**The conditional test is calibrated in every cell (≤ .062) and loses almost no power.** It is adopted as the NH4-attribution test. Without the conditioning, content-timed data loss would be read as gaze behaviour in up to 35% of null replicates. This closes the open item [S1-11].

## 4. Rule R-H — confirmation of the selected design (P6, d = 3, LR, pooled lock)

Run `conf`: manifest `b05add69…`, code `evidence/sim_conf/code_snapshot/`. Its seeds are independent of R-F and R-G, so it replicates their calibration on fresh outcomes.

### 4.1 Calibration (1,000 replicates per null)

| Null | Pooled T1lr | T2lr | **NH1lr** | T2clr | CV-fallback T1 | T2 | **NH1** | E4: T1lr / T2lr / **NH1lr** | E5: T1lr / T2lr / **NH1lr** |
|---|---|---|---|---|---|---|---|---|---|
| N0 | .047 | .047 | .034 | .056 | .043 | .045 | .030 | .065 / .054 / .043 | .044 / .054 / .032 |
| N1 (linear fatigue) | .059 | .051 | .042 | .065 | .052 | .051 | .037 | .044 / .041 / .030 | .054 / .054 / .043 |
| N1q (quadratic) | .047 | .044 | .035 | .053 | .051 | .055 | .032 | .044 / .043 / .033 | .048 / .055 / .038 |
| N1c (cubic) | .049 | .048 | .036 | .049 | .051 | .047 | .034 | .043 / .035 / .029 | .048 / .047 / .034 |
| N1e (exponential) | .046 | .046 | .033 | .053 | .040 | .047 | .029 | .047 / .051 / .035 | .061 / .062 / .043 |
| N2 (person confound) | .039 | .039 | .024 | .046 | .057 | .053 | .032 | .042 / .046 / .036 | .048 / .037 / .030 |
| N3 (non-timed loss) | **.068** | .061 | .053 | .065 | .060 | .065 | .048 | .051 / .053 / .042 | .057 / .057 / .041 |

**Robustness nulls** (500 replicates each):

- 2PL discriminations: T1lr / T2lr / NH1lr = .054 / .056 / .036.
- Guessing floor: .046 / .038 / .030.

**Every pass criterion of R-H holds on the pooled lock:**

- pooled LR tests ≤ .068;
- E4 and E5 elementary NH1lr ≤ .043, and every elementary single test ≤ .065;
- CV fallback ≤ .065.

The development criterion is in §4.4.

### 4.2 Power and minimum detectable effects

NH1lr power on the pooled lock. Figure: [power_closure_vs_stage1.png](evidence/figures/power_closure_vs_stage1.png).

| ρ | Truth | 1.15 | 1.25 | 1.35 | 1.50 | 1.75 | 2.00 | 2.50 | **MDE (80%)** |
|---|---|---|---|---|---|---|---|---|---|
| .4 | Random, sign-coherent | .110 | .317 | **.580** | **.893** | .987 | 1.0 | 1.0 | **1.45** |
| .4 | Equal-weight composite | .107 | .263 | .547 | .893 | .990 | 1.0 | 1.0 | 1.46 |
| .2 | Random | — | — | — | .535 | — | .945 | 1.0 | 1.81 |
| .7 | Random | .250 | .475 | .890 | .990 | 1.0 | 1.0 | — | 1.33 |

**Comparison with Stage 1** (ρ = .4, composite truth):

| Stage-1 design | MDE | Power at OR 1.35 | Calibration under non-linear fatigue |
|---|---|---|---|
| 1 (E4, CV) | 1.72 | .32 | — |
| 5 (pooled, CV) | 1.48 | .51 | — |
| 7 (pooled, LR) | 1.43 | .66 | Failed |
| **Closure design** | **1.46** | **.55** | **Passed** (non-linear and out-of-family fatigue) |

The closure design keeps design 7's efficiency within .03 in MDE and adds calibration under non-linear and out-of-family fatigue, which design 7 lacked.

### 4.3 Closed testing, heterogeneity and sensitivity

**Cohort-specific claims under closed testing** (P[pooled NH1 rejects **and** the cohort's elementary NH1 rejects], ρ = .4, random truth):

| Claim | OR 1.35 | OR 1.5 | OR 1.75 | OR 2.0 | MDE |
|---|---|---|---|---|---|
| E4 | .233 | .467 | .723 | .913 | 1.85 |
| E5 | .280 | .560 | .860 | .973 | 1.70 |

**Sensitivity at OR 1.5** (ρ = .4, random truth; base .893):

| Departure | Pooled NH1lr | E4 claim | E5 claim |
|---|---|---|---|
| No local dependence | .905 | .535 | .570 |
| 2PL discriminations | .815 | .450 | .540 |
| Effect heterogeneity (learner × video) | .775 | .400 | .520 |
| Guessing floor | **.625** | .240 | .330 |
| **E5 effect halved** | **.450** | .290 | .120 |
| **No effect in E5** | **.185** | .140 | .025 |

**Usefulness** (mean CV estimate, ρ = .4, random truth):

| OR | S_item | ΔAUC_wp |
|---|---|---|
| 2.0 | .0079 | .0145 |
| 2.5 | .0151 | .0242 |

- The useful thresholds are reached on average at OR ≈ 2.13 (S_item) and **≈ 2.27 (ΔAUC_wp, binding)**, where power is 1.0.
- Under the pure null, mean CV S_item is −.0058 and ΔAUC_wp −.0014. The P6 estimate's downward bias is disclosed (S1-I09).

**What the sensitivities mean:**

- **The pooled design is only as strong as E5's share of the effect.** If E5 carries half the effect, power at OR 1.5 falls from .89 to .45; if none, to .19.
- Closed testing still lets an E4 effect be claimed when it is large, at a price: the E4 claim reaches 80% only at OR ≈ 1.85.
- The pooled test answers "is there a moment effect in E4 ∪ E5". The cohort claims are what can be said about each protocol.

### 4.4 Development stop rule under the final design

Development set, 500 replicates per null, 300 per OR.

**False "go"** (CV T2 p < .10 **and** CV ΔAUC_wp ≥ .01) is ≤ .010 in every null:

| N0 | N1 | N2 | N3 | N1q | N1c | N1e |
|---|---|---|---|---|---|---|
| .002 | .000 | .000 | .000 | .000 | .010 | .000 |

The development tests (T1lr, T2lr, CV T2) stay ≤ .062.

**Probability of "go"** and development NH1lr power (ρ = .4, random truth):

| OR | 1.15 | 1.25 | 1.35 | 1.50 | 1.75 | 2.00 | 2.50 | 3.00 |
|---|---|---|---|---|---|---|---|---|
| go | .010 | .030 | .070 | .133 | .433 | .673 | .910 | .993 |
| Development NH1lr | .137 | .267 | .567 | .837 | .987 | 1.0 | 1.0 | 1.0 |

The ΔAUC_wp ≥ .01 arm binds (mean CV ΔAUC_wp .010 at OR 1.75). "Go" reaches 80% at OR ≈ 2.2, against a useful OR of ≈ 2.27. The stop rule therefore lets the lock be spent essentially only when the effect is plausibly useful. At plausible effects (OR ≤ 1.5), the most likely trajectory is a development stop (go ≤ .13), and the locked cohorts would then stay untouched. The stop rule is unchanged in form.

### 4.5 CV-fallback power (descriptive add-on)

Declared after the confirmation grid was fixed, and **decides nothing**. Run `cvpow`, manifest `68e4bc6c…`, 200 replicates per OR, ρ = .4, random truth:

| OR | CV NH1 (fallback) | LR NH1lr (same replicates) |
|---|---|---|
| 1.35 | .425 | .590 |
| 1.50 | .750 | .905 |
| 1.75 | .970 | .985 |

The CV fallback's MDE is about 1.55, against 1.45 for LR. Ratifying the LR statistic is worth about .15–.17 power at OR 1.35–1.5.
