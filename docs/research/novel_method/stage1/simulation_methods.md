# Stage-1 design simulation — methods

2026-10-13. Outcome-free: **every outcome below is synthetic**. Code: `src/cairn/{design, features, model, inference, simulate, simrun, analysis}.py`. Runs are bound by `evidence/sim*/MANIFEST.json`. Rules fixed before the runs are in [evidence/predeclared_rules.md](evidence/predeclared_rules.md).

**Runs.**

| Run | Directory | Purpose | Code |
|---|---|---|---|
| `pilot` | (scratch, not kept) | 72 replicates at B = 99; showed the raw form inflated under N1 | Working tree |
| `n1decision` | `evidence/sim_n1decision/` | Rule R-A: raw versus detrended CAIRN-linear on the same outcomes (1,000 replicates, B = 199) | Working tree at launch; manifest `8d573627…` |
| `main` | `evidence/sim/` | The declared grid (16,800 replicates) | **Frozen copy** in `evidence/sim/code_snapshot/cairn/`, imported first on `PYTHONPATH`; its file hashes are in the manifest (`4e692198…`). Later edits to `src/cairn` are additive (kernel grid, extension runs, analysis fixes, the `paths` split of S1-D19). After them the current code still reproduced stored replicates bit for bit |

## 1. What is real and what is synthetic

| Element | Source |
|---|---|
| Learners, cells, items | **Real incidence**, from availability flags only (`gate_behavior_eligible`, gaze basic QC ≤ .50). Development 55 learners / 229 cells / 9 videos / 2,725 responses (2,205 anchorable); E4 39 / 112 / 3 / 1,344 (977); E5 47 / 129 / 3 / 1,548 (1,119); pooled E4 + E5 86 / 241 / 3 / 2,892 (2,096) |
| Anchors and their sharing | **Real provisional anchor table** (Stage 0b; machine anchors, not frozen). Distinct moments: development 59, E4 19. Items within 10 s share a moment |
| Moment terms | **Real per-second channels** of each learner's own viewing (`loss_long`, `onscreen`, `logdens`, `rho5`, `sacc`, `disp5`), pooled over the item's anchor window |
| Person-level confounders (N1–N3) | **Real**: each learner's engagement slope over the recording, whole-video engagement, recording invalid fraction |
| Item correctness | **Synthetic**, from the generator below |

## 2. Generator

    logit P(y_pvj = 1) = beta_j + a_j (u_p + w_pv) + q_p,m(j) + lambda x*_pvj [+ confound]

| Term | Specification | Dependence it creates |
|---|---|---|
| β_j ~ N(m_β, s_β²) | (m_β, s_β, τ) cycle over the declared grid {.4, .8} × {.8, 1.2} × {.5, 1.0} | **Crossed item effect**: every learner answers the same items |
| u_p ~ N(0, τ²) | | **Learner clustering** across items and videos |
| w_pv ~ N(0, .3²) | | Learner × video clustering |
| q ~ N(0, .5²) per learner × anchor moment | One draw shared by all items in one moment; per learner × item otherwise. Independent of engagement | **Local dependence / repeated observation of one moment**: item-specific prior knowledge of the same content |
| x* = √ρ·x + √(1−ρ)·ε | x is the real anchored engagement composite: sign-aligned equal weights over the six channels, centred within learner × video and item, unit SD. ε is shared by the items of one moment. ρ ∈ {.2, .4, .7} | Measurement error; the moment, not the item, is the unit of the latent state |
| λ = log OR | Per SD of x*. OR ∈ {1.15, …, 3.0} (ρ = .4); {1.5, …, 4.0} (ρ = .2); {1.15, …, 2.0} (ρ = .7) | — |
| a_j | 1 (Rasch); 2PL log-normal(0, .3) as a sensitivity | — |
| Guessing floor | Sensitivity only: .25 for one-keyed items, .10 otherwise | — |
| Effect heterogeneity | Sensitivity only: λ(1 + .5 z_p)(1 + .3 z_v) | — |

Mean simulated accuracy is about .6.

## 3. Null and confound scenarios (spec §1.4)

| Scenario | Construction (λ = 0 unless stated) |
|---|---|
| N0 | Pure null |
| N1 fatigue / position | Three terms: β += −.5 (quiz position − .5); θ += .3 s_pv; and the interaction **.4 s_pv × 2 (anchor position − .5)**. s_pv is the learner's real engagement slope over the recording |
| N2 person confound | u_p correlated .5 with the learner's real whole-video engagement |
| N3 non-timed data loss | θ += −.5 × (real recording invalid fraction, standardized) |
| N4 content-timed data loss (NH4 true) | η += −log 1.5 × (real in-window long-loss term) |
| N1q non-linear fatigue (added in Stage 1) | As N1, with the learner's real engagement **curvature** c_pv (orthogonal quadratic of the course, standardized) in place of the slope, and the interaction **.6 c_pv ((2 (anchor position − .5))² − 1/3)**. A linear within-recording trend cannot remove it, so it tests whether the detrending fix (S1-D06) generalizes |

**Sensitivity scenarios** (E4 unless stated; N0 with 200 replicates and OR 1.5 at ρ = .4 with 100): no local dependence (σ_q = 0); 2PL discriminations; guessing floor; effect heterogeneity; single-channel truth (`logdens` only); N2 with an effect (OR 1.5); pooled lock with the E5 effect halved.

## 4. Analysis per replicate (identical code path to Stage 2)

**Folds.** Learner-grouped, experiment-stratified 5-fold CV, R = 3 repetitions with fixed seeds. Every fold recomputes:

- the references (regime A: training learners on the same video, never the target);
- the channel standardization;
- the item centring.

All of these use the fold's training learners only.

**Models.** All are penalized Rasch GLMMs sharing one solver:

| Model | Terms |
|---|---|
| IRT-M2 (base) | Video intercepts, item easiness, learner random effect, recording quality |
| IRT-whole | Base + whole-video channel means |
| **CAIRN-linear** | Base + anchored engagement in the person path + 6 moment regressors (one λ per channel, shared across R/C). **Primary form: within-recording detrended** (`CAIRN-linear-dt`; S1-D06): each cell's per-second channels lose their linear trend over the cell's own seconds (mean kept) before pooling. The raw form ran only in `n1decision` |
| CAIRN-linear-dir (lock sets) | The moment regressors collapsed onto the direction estimated by CAIRN-linear on an independently simulated development cohort under the same truth; 1 df |
| CAIRN-validity, CAIRN-gaze | NH4 checks |
| B9 | Lallé-style pooled window classifier |

**Statistics.**

| Statistic | Definition |
|---|---|
| CV statistic (plan T1/T2) | Person-balanced held-out item log-loss gain over IRT-M2, averaged over the R repetitions |
| LR statistic (candidate, S1-D09) | Full-data conditional log-likelihood gain over IRT-M2, with references from all other learners and no outcomes |

**Nulls.** The same nulls serve both statistics:

| Null | Construction |
|---|---|
| T1 | Learner-block Freedman–Lane: whole learners' moment-term blocks are exchanged among learners of the same experiment and video pattern; the person path stays in place |
| T2 | Relocation of distinct anchor moments within each video, one permutation for all learners. Items of a moment move together and keep their span lengths |
| T2c | One circular shift per video, ≥ 30 s, with wrap-around, for all learners |

**Decisions.**

- NH1 = T1 ∧ T2, each one-sided at α = .05 (intersection–union).
- Development stop rule: go = T2 p < .10 ∧ CV ΔAUC_wp ≥ .01.

**Budgets.** B = 199 for nulls; B = 99 for alternatives and sensitivities. Replicates:

- 500 per null scenario N0–N3 in development, E4 and the pooled lock;
- 200 per alternative at ρ = .4 (OR 1.15–3.0), and for N1q, N4 and E5 N0 / N1;
- 100 per alternative at ρ = .2 and .7, and per sensitivity alternative.

The circular-shift null (T2c) runs in N0 and N1 (development, E4, pooled), N1q, E5 N1 and the E4 alternatives at ρ = .4.

**Full-data references.** These are reported for the clustering question:

- the GLMM Wald test of λ on the true composite;
- a naive logistic Wald test that treats responses as independent;
- the same with a learner-cluster sandwich SE;
- the plan-literal regressor, z − ē without within-cell centring.

## 5. Mapping effects to usefulness

The plan's minimum useful effect is S_item ≥ .01 **and** ΔAUC_wp ≥ .02 over IRT-M2 (§20.2). It is mapped to an odds ratio in two ways:

| Mapping | Definition |
|---|---|
| Infinite data | Expected log-loss and within-learner AUC of the oracle CAIRN predictor (true λ, true item easiness, latent terms integrated out) against the oracle IRT predictor, by Monte Carlo over the generator |
| Planned procedure | Mean CV estimate of S_item and ΔAUC_wp across replicates |

The minimum useful OR is the smallest OR at which both thresholds are met (log-OR interpolation).
