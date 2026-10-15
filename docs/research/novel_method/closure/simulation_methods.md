# Closure-phase simulations — methods

2026-10-14. Outcome-free: **every outcome below is synthetic**.

- Rules fixed before the runs: [evidence/predeclared_rules.md](evidence/predeclared_rules.md), hash-stamped in `predeclared_rules.sha256`.
- Code: `src/cairn/{features, inference, simulate, simrun, closure_analysis}.py`. Each run imports a frozen copy first (`evidence/sim_*/code_snapshot/`; [scripts/snapshot.py](scripts/snapshot.py)), and its manifest binds every file hash.

## 1. What is unchanged from Stage 1

[stage1/simulation_methods.md](../stage1/simulation_methods.md) still applies to everything below:

- the real incidence and provisional anchors;
- the real per-second channels;
- the generator (crossed item, learner and learner × video effects, local dependence per learner × moment, latent moment state with reliability ρ);
- nulls N0–N4 and N1q;
- learner-grouped, experiment-stratified 5-fold CV with R = 3;
- the T1 / T2 / T2c permutation nulls;
- the fixed ridges, and variance components taken from each fold's IRT-M2 base.

## 2. What is new

| Element | Definition | Code |
|---|---|---|
| **Polynomial within-recording detrend** | Degree d ∈ {1, 2, 3}: Legendre polynomials of the recording time, fitted by least squares to each channel of each recording over its finite seconds and removed, keeping the mean. d = 1 reproduces the Stage-1 form (the Stage-1 function is kept as the d = 1 code path) | `features.detrend_poly`; `Variant.trend` |
| **P0 (unit-weighted composite)** | One moment regressor: the six within-cell- and within-item-centred, training-scaled channel regressors combined with equal weights and the outcome-free construct signs (`features.ENGAGED_SIGN`, Stage-0 distracted vs attentive), re-standardized. Ridge 1. Its anchored person-path summary is projected on the same direction | `inference.unit_variant` |
| **PT (anisotropic ridge)** | Six channels rotated to (w0, its orthonormal complement). The w0 column is re-standardized; ridge 1 along it, ridge 100 on the 5-dimensional complement. A Gaussian prior centred on the construct direction | `inference.aniso_variant`, `complement_basis` |
| **PD (frozen development direction)** | Stage-1 designs 6/8: P6 fitted on a simulated development cohort under the same scenario. Its normalized coefficient vector is frozen as a 1-df direction for the lock | `simulate.development_direction` |
| **PA (adaptive)** | Exact single-step min-p of P0 and P6. Every permutation draw is applied to both; each row's p-value is computed against all B + 1 rows; the observed minimum is referred to the row minima (Westfall & Young 1993) | `inference.minp_from_stats` |
| **Joint permutation tests** | One draw per permutation applied to every variant of a replicate, so the variants are compared on paired nulls. For a single variant the p-values equal `run_tests` for the same draws (tested) | `inference.lr_tests_joint` |
| **N1c (cubic fatigue)** | η += −.5 (quiz position − .5) + .3 c3_pv + .473 c3_pv P3(2a − 1). c3_pv is the learner's real cubic Legendre coefficient of the sign-aligned engagement course (standardized); a is the anchor position | `simulate.generate` |
| **N1e (exponential decrement)** | As N1c with the learner's real coefficient on exp(−2(x + 1)), and κ = .703. Strengths are RMS-matched to N1q (tested) | idem |
| **Truth directions** | `composite` (Stage 1); `random`: sign-coherent w = s ⊙ \|g\|, drawn per replicate from its own stream; `logdens`; `gaze`; `validity`; `random` with `dev_truth = random_indep` (development and lock directions independent) | `simulate.truth_regressor`, `random_direction` |
| **Closed testing inside pooled replicates** | The E4 and E5 elementary tests run on the E4 / E5 rows of the same synthetic pooled outcomes, with their own folds and references. The E4 rows of a pooled replicate have the E4-only generator distribution | `simulate.run_replicate_closure(subs=…)` |
| **NH4 conditional test** | The gaze block with the validity moment column held at the true anchors in every permutation (`Variant.nuisance`) | `inference.gaze_given_validity_variant` |

## 3. Runs

Each run is resumable. Replicate randomness depends only on (base seed, set, mode, scenario, replicate). Sets run one after another, so each worker holds one set's structures and peak memory stays at about 6 GB with 8 workers.

| Run | Rule | Directory | Content |
|---|---|---|---|
| `rf` | R-F | `evidence/sim_rf/` | P6 and P0 at d = 1, 2, 3 (paired). LR T1 / T2 / T2c. Nulls N0, N1, N1q, N1c, N1e: 1,000 replicates in the pooled lock and E4, 500 in development. OR 1.5 under composite and random truths: 200 replicates |
| `rg` | R-G | `evidence/sim_rg/` | P6, PT, P0, PD, PA at d\*. Pooled lock. Seven nulls × 1,000 replicates. Six truths × OR {1.35, 1.5} × 300 replicates |
| `conf` | R-H | `evidence/sim_conf/` | Selected design at d\*:<br>• pooled nulls × 1,000 with E4 / E5 elementary tests and CV-fallback T1 / T2;<br>• power curves at ρ = .2 / .4 / .7;<br>• sensitivities;<br>• development nulls and ORs with the stop rule |
| `nh4` | R-I | `evidence/sim_nh4/` | Conditional gaze test, validity-only and gaze-only at d\*. N4, N0, N3 × 500 in the pooled lock, E4 and development; gaze-truth OR 1.5 |
| `rj` | R-J | after G-AN | The `conf` nulls and OR 1.35 / 1.5 on the frozen human anchors (`--anchors`) |

**Budgets:**

- B = 199 for nulls (exact at α = .05 because (B + 1)α is an integer) and B = 99 for alternatives.
- The lock uses B = 999.
- CV R = 3 in the simulations and R = 10 in Stage 2 and the lock.

## 4. Statistics computed from the replicates

- **Rejection rate** at one-sided α = .05 with Wilson 95% intervals.
- **NH1:** the intersection–union p-value max(p_T1, p_T2), for both the LR and the CV statistic.
- **Closed-testing power for E4 (E5):** P(pooled NH1 rejects **and** the E4 (E5) elementary NH1 rejects).
- **MDE:** log-OR interpolation at 80% power.

The decisions are computed mechanically by `cairn.closure_analysis.rule_rf`, `rule_rg` and `conf_checks` from the stored replicates.

## 5. Outcome-free diagnostic (not a decision input)

`scripts/trend_leakage.py` measures, on the real signals, the within-cell R² of the unit-weighted moment regressor on Legendre polynomials P1–P3 of anchor position. It compares that with a reference in which anchor positions are shuffled among each video's moments ([evidence/trend_leakage.json](evidence/trend_leakage.json)).
