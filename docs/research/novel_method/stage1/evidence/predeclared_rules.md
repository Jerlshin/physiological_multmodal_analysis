# Stage-1 decision rules, declared before the corresponding simulations were run

Written 2026-10-13, before the N1 decision run and before the main grid. Simulation results are outcome-free, but rules are fixed first so that design choices cannot drift toward favourable numbers.

## R-A: primary form under the fatigue/position confound (S1-D06)

**Trigger.** In a 72-replicate pilot (B = 99), the plan-literal CAIRN-linear rejected under N1 (development: T1 .11, T2 .17, T2c .11; 18 replicates). The moment regressor carries each learner's linear engagement trend over the recording, which co-varies with item position.

**Candidate fix.** The plan's own robustness control (§18) is a learner-specific trend term. Here it takes its fold-safe, within-recording form: each cell's per-second channels are linearly detrended before anchored pooling (mean kept; only the cell's own seconds are used).

**Experiment** (grid `n1decision`, B = 199, R = 3, K = 5). Raw and detrended CAIRN-linear are evaluated on the same simulated outcomes:

- E4 and development: N1 and N0, 200 replicates each;
- OR 1.5 at ρ = .4: 100 replicates each.

**Rule:**

1. If the **raw** form keeps T1, T2 and T1 ∧ T2 at ≤ .07 under N1 in **both** sets, raw stays primary. This is the plan-literal form.
2. Otherwise, if the **detrended** form keeps T1, T2 and T1 ∧ T2 at ≤ .07 under N1 and N0 in both sets, the detrended form becomes primary, whatever its power cost. The cost is reported.
3. Otherwise neither form is calibrated under N1. The form with the lower maximum N1 false-detection rate is used, and the confirmatory design must add a further control before preregistration. This is reported as an unresolved Stage-1 failure.

T2c (circular shift) is reported but is not part of the rule: it is a sensitivity null.

## R-B: adequacy of the locked design (spec §1.7 item 4; user instruction of 2026-10-13)

1. **Minimum useful effect.** It is taken from plan §20.2 unchanged: S_item ≥ .01 **and** ΔAUC_wp ≥ .02 over IRT-M2. It is **not** lowered to reach power. The simulation maps it to an odds ratio per SD of the latent moment state (at ρ = .2, .4, .7) as the smallest OR on the grid whose **mean planned-procedure estimate** meets both thresholds; interpolation is in log OR.
2. **Detectability criterion** (spec §1.7 item 4). The power of the E4 intersection test (T1 ∧ T2, α = .05 each) at OR ≤ 1.35 with ρ = .4.
3. **E4 is adequate** only if its NH1 power is ≥ .80 at the minimum useful effect **and** criterion 2 holds. Otherwise the confirmatory design is revised before Stage 2. Options are tried in this order:
   - (a) a pooled E4 + E5 lock;
   - the frozen development direction (1 df), which is not a declared option and needs explicit user approval;
   - (c) NH1-only confirmatory, with NH2–NH5 descriptive;
   - combinations of the above.

   The first option or combination that reaches .80 at the minimum useful effect, with false detection ≤ .07 in N0–N3, is recommended. If none reaches it, that is reported as the finding. **The threshold is not lowered.**
4. **Option (b), one-sided tests.** T1 and T2 are already one-sided permutation tests (improvement only), so (b) cannot add power. It is recorded as vacuous rather than counted as a redesign.

## R-C: development stop rule (plan §20.5; spec §1.7 item 2)

go = T2 p < .10 **and** CV ΔAUC_wp ≥ .01. Criterion (iii), the outcome-free construct check, was already met in Stage 0 (AUC .89). The go rate must be ≤ .10 in every null scenario N0–N3.

## R-D: calibration criterion (spec §1.7 item 1)

A test passes if its empirical false-detection rate is ≤ .07 in N0–N3. The binomial 95% interval is reported alongside. With 500 replicates and a true rate of .05, the estimate exceeds .07 with probability about .02.

## Addendum (written before the main grid, after the N1 decision run started): R-B2, ordering of redesign options

**Why the addendum.** An infinite-data mapping of the generator (no fitted model) shows that the plan's useful thresholds lie at large effects. At ρ = .4, S_item ≥ .01 needs OR ≈ 1.7 and ΔAUC_wp ≥ .02 needs OR ≈ 2.25. The externally plausible effects (OR 1.15–1.5) are therefore below the useful thresholds. Two consequences follow:

- The alternative grid is extended to OR 3.0 at ρ = .4.
- A more efficient detection statistic is evaluated. It is the **likelihood-ratio (LR) statistic**: the full-data conditional log-likelihood gain of CAIRN-linear over IRT-M2. It uses the *same* learner-block (T1) and moment-relocation / circular-shift (T2, T2c) permutation nulls.

The predictive questions are still answered by the cross-validated S_item and ΔAUC_wp against the unchanged thresholds.

**Candidate confirmatory designs.** Each one is (cohort) × (statistic) × (moment parametrization). They are listed in increasing order of departure from the plan as written:

| # | Cohort | Statistic | Moment parametrization |
|---|---|---|---|
| 1 | E4 | CV log-loss | CAIRN-linear refitted in the lock (plan as written) |
| 2 | E4 | CV | frozen development direction (1 df) |
| 3 | E4 | LR | refitted |
| 4 | E4 | LR | frozen direction |
| 5 | E4 + E5 pooled | CV | refitted |
| 6 | E4 + E5 pooled | CV | frozen direction |
| 7 | E4 + E5 pooled | LR | refitted |
| 8 | E4 + E5 pooled | LR | frozen direction |

**Admissibility.** A design is admissible only if T1, T2 and T1 ∧ T2 are each ≤ .07 in N0–N3 (500 replicates). For the pooled designs this is checked on the pooled set.

**Choice.**

- The first admissible design that reaches NH1 power ≥ .80 at OR 1.35 (ρ = .4) is recommended.
- If none does, the admissible design with the smallest NH1 MDE at ρ = .4 is recommended, and the shortfall is reported.
- The useful thresholds (S_item ≥ .01, ΔAUC_wp ≥ .02) are never changed.

Designs 2–8 go beyond spec §1.7's declared options (a)–(c), apart from pooling (option a). Any of them needs explicit user approval and a decision ID before Stage 2.

## Addendum R-E (written 2026-10-14 after the main grid finished, before the follow-up run): non-linear fatigue on the recommended design

**Why.** Under R-B2, the recommended design is #7: pooled E4 + E5, likelihood-ratio statistic, moment block refitted in the lock. All its tests are ≤ .07 in N0–N3 (500 replicates each). The non-linear fatigue null N1q, however, was run only on E4 and development, with 200 replicates each. In E4 the primary T2 was .075 (15/200; Wilson 95% interval .046–.12), T2lr .070 and NH1 .050.

**Run** (grid `addendum`, B = 199, R = 3, K = 5, same code path, circular shift included):

- N1q on the pooled lock: 500 replicates.
- N1q on E4: extended from 200 to 500 replicates. Replicates 200–499 continue the same seed sequence.

The declared 200-replicate E4 value and the 500-replicate value are both reported.

**Rule.**

1. If, on the pooled lock under N1q at 500 replicates, T1lr, T2lr and NH1lr (design 7) and T1, T2 and NH1 (design 5) are each ≤ .07, design 7 stands with the linear within-recording detrending.
2. Otherwise design 7 needs an additional non-linear temporal control before preregistration, for example a quadratic within-recording detrend. That control must be specified and re-simulated. Until then the shortfall is reported as an open Stage-1 item.

The E4 500-replicate N1q result is descriptive, because E4 alone is no longer the recommended confirmatory set.
