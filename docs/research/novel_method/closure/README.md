# Novel-method closure phase — outcome-free completion before Stage 2

2026-10-14 to 2026-10-15. Executed on the user's instruction to resolve, before any real outcome is accessed, everything that can be resolved. Every simulated outcome is synthetic.

**Status:** CLOSURE PHASE COMPLETE. Stopped at the human / authorization boundary. No outcome of any cohort was accessed.

| Document | Content |
|---|---|
| [entry_state.md](entry_state.md) | State before any closure output |
| [evidence/predeclared_rules.md](evidence/predeclared_rules.md) | Rules R-F, R-G, R-H, R-I, R-J, R-K, hash-stamped (`591913ad…`, 06:14:40Z) before the first closure run |
| [simulation_methods.md](simulation_methods.md), [simulation_report.md](simulation_report.md) | The closure simulations and their results |
| [baselines.md](baselines.md) | The 17 strong ML/DL/FM baselines and their outcome-free validation |
| [design_config.json](design_config.json) | **The frozen confirmatory design** (decision D110), read by the freeze, Stage 2 and the lock |
| [development_analysis_plan.md](development_analysis_plan.md) | DAP-1: what Stage 2 computes |
| [gan/](gan/README.md) | G-AN coordinator run-book, protocol addendum v1.1, forms |
| [decisions.md](decisions.md) | C-D01 onward and C-I…; global D096–D113, INF-124 onward |
| [evidence/](evidence/) | Runs (code snapshots, manifests, replicates), tables, figures, checks, logs, `SHA256SUMS` |

## 1. Final recommended method and confirmatory design

**Method: CAIRN-linear, with a cubic within-recording detrend (`CAIRN-linear-dt3`).** It is still the content-anchored, psychometrically identified item-response model. The closure phase changes one thing in it: each recording's per-second channels lose their cubic (not linear) time trend before anchored pooling.

| Component | Specification |
|---|---|
| Channels (1 Hz) | Six primary channels: `loss_long`, `onscreen`, `logdens`, `rho5`, `sacc`, `disp5`. Reference-relative channels use training-fold peers (regime A) |
| Temporal control | Legendre polynomial of degree 3, removed per channel over the recording's own seconds; mean kept (C-D13) |
| Moment term | Anchor-window mean minus recording mean; centred within learner × video and within item (training rows); scaled on training rows |
| Moment block | Six channels, isotropic ridge 100 (P6) |
| Head | Penalized Rasch GLMM: video intercepts, item easiness shrunk to the video mean, learner random effect (Laplace), person path (Q + anchored summary) |
| Kernel | Hard anchor span by default; the development selects among 12 lag/width kernels |
| **Estimand** | The effect, on an item's correctness, of the learner's anchored engagement **relative to their own cubic engagement course**. It is identified within learner × video and against relocated or shifted anchors |

**Confirmatory design** (decision D110; [design_config.json](design_config.json)):

| Element | Specification |
|---|---|
| Cohort | **Pooled E4 + E5 lock**, experiment-specific item easiness |
| Primary test | **NH1 = T1 ∧ T2** on the **likelihood-ratio statistic**: full-data conditional log-likelihood gain over IRT-M2.<br>• T1: learner-block Freedman–Lane;<br>• T2: moment relocation within video;<br>• B = 999 each, one-sided α = .05;<br>• the circular shift is a sensitivity analysis |
| Cohort-specific claims | **Closed testing:** only if H_pool is rejected are E4 and E5 tested alone, each at α. Strong family-wise error control at .05 over the three claims. E4 stays the first-named claim |
| Heterogeneity | λ̂ and usefulness per cohort (descriptive) |
| Usefulness | CV S_item ≥ .01 **and** ΔAUC_wp ≥ .02 over IRT-M2 (R = 10). Unchanged |
| Fallback | The same design with the CV statistic, certified in the confirmation run, used if you do not ratify LR |
| NH4 attribution | The gaze block **conditional on the in-window validity term** (rule R-I) |
| NH2–NH5 | Descriptive |
| Development stop rule | Unchanged in form, re-calibrated for this design |

## 2. What changed and why

Every change was declared before its decisive simulation ([predeclared_rules.md](evidence/predeclared_rules.md), `591913ad…`, stamped before the first run). Each is labelled in the plan as amendment v1.4, tags [C-1] onward.

| Change | Why (outcome-free evidence) |
|---|---|
| **Linear → cubic within-recording detrend** | Rule R-F, 60 decisive cells × 1,000 replicates:<br>• linear: 11 cells > .07, up to .135 under quadratic fatigue;<br>• quadratic: 1 cell (.074) under the **out-of-family** cubic null;<br>• cubic: 0 cells (maximum .066).<br>Outcome-free leakage check: real recordings carry slow position-aligned engagement structure beyond chance, removed by degree 2–3 |
| **CV → LR as the primary statistic (CV kept as certified fallback)** | Stage-1 rule R-B2 ranked the LR design first. The LR design's only blocker was non-linear fatigue (R-E), now resolved. LR also makes B = 999 cheap |
| **Moment parametrization tested, P6 kept** | Rule R-G compared four alternatives on paired permutations and six truth directions:<br>• the 1-df unit-weighted composite (P0);<br>• an anisotropic ridge centred on it (PT);<br>• the frozen development direction (PD);<br>• the adaptive min-p (PA).<br>All are calibrated. The ones with higher average power (PD .77, PA .74 vs P6 .71) depend on a direction assumption: P0 drops to .23 under a single-channel truth; PD to .46 when development and lock directions differ. The declared robustness constraint keeps P6 |
| **Closed testing for E4 / E5** | Keeps E4- and E5-specific claims interpretable inside the pooled lock, with exact FWER control |
| **NH4 attribution specified** | The unconditional gaze test rejects in up to 35% of content-timed-loss nulls. The conditional test is calibrated (≤ .062) and loses almost no power |
| **Estimand made explicit** | The moment effect is defined relative to the learner's own cubic course. Slower trends are not part of the claim (N-d scope, S1-D17, now precise) |
| **Strong baselines** | 17 ML/DL/FM baselines implemented and validated (§4) |
| **Infrastructure** | G-AN tooling and protocol addendum v1.1; freeze tooling; Stage-2 (DAP-1) and Stage-4 runners, dry-run; R-J re-simulation command; R = 10 caches |
| **Unchanged** | Useful thresholds; stop rule; cohorts and partition; modalities; anchors protocol content; G-AN thresholds |

## 3. Calibration, power and major remaining risks

### 3.1 Calibration

Independent confirmation run, 1,000 replicates per null. Every pre-declared criterion of R-H holds ([simulation_report §4](simulation_report.md#4-rule-r-h--confirmation-of-the-selected-design-p6-d--3-lr-pooled-lock)):

| Check | Maximum false detection (bound .07) |
|---|---|
| Pooled T1lr / T2lr / NH1lr. Nulls: pure, linear / quadratic / cubic / exponential fatigue, person confound, non-timed data loss | .068 / .061 / .053 |
| E4 and E5 elementary tests (closed testing) | NH1lr ≤ .043; single tests ≤ .065 |
| CV fallback T1 / T2 / NH1 | .060 / .065 / .048 |
| 2PL and guessing-floor nulls | ≤ .056 |
| Development stop rule, false go | ≤ .010 |
| NH4 conditional test (N4, N0, N3; three sets) | ≤ .062 |

### 3.2 Power

Pooled lock, ρ = .4:

| | OR 1.35 | OR 1.5 | MDE (80%) |
|---|---|---|---|
| NH1, LR | .58 | .89 | **1.45** |
| E4 claim (closed testing) | .23 | .47 | 1.85 |
| E5 claim (closed testing) | .28 | .56 | 1.70 |
| CV fallback | .43 | .75 | ≈ 1.55 |

- The MDE is 1.81 at ρ = .2 and 1.33 at ρ = .7.
- Against Stage 1: design 5 had MDE 1.48; design 7 had 1.43 but was uncalibrated under non-linear fatigue.
- At the minimum useful effect (OR ≈ 2.27 by the mean CV estimate; the ΔAUC_wp arm binds) power is 1.0.
- Development "go" reaches 80% at OR ≈ 2.2.

### 3.3 Major remaining risks

| Risk | What the evidence says |
|---|---|
| **E5 does not carry the effect** | E5 is a different construct (answer search after question preview). If E5's effect is half of E4's, pooled power at OR 1.5 falls from .89 to .45; if E5 has none, to .19. Closed testing keeps E4 claimable, but only for large effects (MDE 1.85) |
| **Effects are probably small** | Plausible effects (OR 1.15–1.5) sit below the useful threshold (OR ≈ 2.27). The most likely trajectory is a development stop (go ≤ .13 at OR 1.5) or the "Weak" category. This is by design: the stop rule protects the lock |
| **Human anchors may differ** | The machine anchors give E4/E5 19 moments. Rule R-J re-certifies on the human set; power below .50 at OR 1.5 goes back to you |
| **Guessing floor / misfit** | A guessing floor lowers power at OR 1.5 to .63; 2PL to .82; effect heterogeneity to .78. Calibration holds under 2PL and guessing nulls |
| **Estimand narrowing** | The cubic control removes engagement trends slower than about a third of a recording. A genuinely slow learning-relevant engagement drift is outside the claim, by declared definition |
| **Downward-biased usefulness estimate** | P6's CV S_item is biased downward (−.006 under the null). Disclosed; thresholds not adjusted |
| **Simulation ≠ reality** | Outcomes are generated by a Rasch-type model on real signals. Untested departures: item-specific prior knowledge correlated with engagement; non-linear dose–response |
| **Novelty** | Unchanged since Stage 0 (Lallé 2025 precedes item-anchored prediction). The contribution rests on psychometric identification plus built-in falsification. A 2026 search found no new collision |

## 4. Status of the strong baselines

[baselines.md](baselines.md). **17 ML/DL/FM baselines are implemented behind the `ItemModel` interface, all deterministic and fold-safe (checked):**

| Tier | Models |
|---|---|
| B3 | Elastic net, random forest, LightGBM, CatBoost, GPBoost, TabPFN v2 (all stacked into IRT-M2); item-level LightGBM residual; GPBoost with crossed learner/item random effects |
| B4a | MantisV2 and MOMENT video-level; MantisV2, Mantis-8M and MOMENT anchored (ablation A4) |
| B4b | Gated-attention MIL; text-conditioned item attention, MLP and linear |
| B7 | TCN encoder with label-free masked pretraining |

**Validation:**

| Control | Result |
|---|---|
| Negative (N0) | Passed by all |
| Anchored positive (OR 3, ρ .7) | Passed by every anchored or item-level learner |
| Declared person-level positive (r = .5) | Met only by IRT-whole |
| Post hoc functional check (r = .9; labelled post hoc) | Every whole-video learner gains |

So the whole-video learners work, but with about 190 training cells they cannot beat a 6-column linear person path on a moderate signal, as G01-R found.

**Not run:**

- TabPFN ≥ 2.5: licence gated.
- EEG foundation models: the modality is excluded from CAIRN's claims, and preprocessing-heavy. Stage 2 can add them.

The strongest competing baseline for NH3 is selected in Stage 2.

## 5. Remaining human-only work

1. ✋ **Recruit two annotators and one adjudicator**: blind, not on the analysis team; about 2 annotator-days each. Run the G-AN process ([gan/README.md](gan/README.md), steps 1–8c).
2. ✋ **Ratify the design** (D110), including the LR statistic and the pooled E4 + E5 lock with closed testing, or choose the certified CV fallback. Your commit of the frozen design is the ratification.
3. ✋ **Commit** the planning, Stage-0, Stage-1, closure and G-AN work before any outcome access.
4. ✋ **Write `AUTHORIZATION.json`** for scope `development` (template printed by `cairn freeze authorization-template`).
5. Optional:
   - accept the TabPFN-2.5 licence if you want it as an extra baseline;
   - authorize the external-data steps of plan §19 (Lallé terms, John item texts, webcam terms);
   - later, the OSF preregistration (Stage 3).

## 6. Is everything computationally possible before Stage 2 complete?

**Yes, with three deliberate exceptions**, each of which needs a human act or would add nothing decision-relevant:

| Exception | Why it is not done |
|---|---|
| Rule R-J re-simulation | Needs the frozen **human** anchors. The command and the pass criteria are ready |
| EEG foundation-model baselines | Deferred with reasons (§4) |
| External-cohort work | Needs your authorization of data terms |

Everything else is done and tested:

- design, calibration and power decisions;
- the NH4 test;
- baselines;
- G-AN tooling and protocol addendum;
- freeze and gate tooling;
- Stage-2 and Stage-4 runners;
- R = 10 caches;
- provenance archives.

The test suite: **203 tests OK** (2 pre-existing skips; 33 new closure tests), and `cairn verify` passes.

## 7. Gates and actions still required before real development outcomes may be authorized

In this order. The tooling enforces each step that has a check:

| # | Gate / action | Enforced by |
|---|---|---|
| 1 | G-AN passes on two human files; adjudication complete; anchor freeze written | `cairn gan freeze`, which refuses machine raters and a failed gate |
| 2 | **Rule R-J passes** on the frozen human anchors with the frozen design (`rj_record.json`). If not: the CV fallback, then d\* + 1. If power at OR 1.5 falls below .50: put the change to the user | `cairn closure --grid rj`, `scripts/rj_evaluate.py` |
| 3 | ✋ Design ratified and committed (D110 / `design_config.json`) | Your commit |
| 4 | **CAIRN freeze record** for stage `development` | `cairn freeze build --write`, which refuses without (1), (2) and a decision ID |
| 5 | ✋ `AUTHORIZATION.json` naming scope `development` and binding the freeze record | The Stage-0 gate refuses otherwise (verified) |
| 6 | Tests and `cairn verify` pass at the frozen commit; then `cairn run --scope development` (one logged access) | Gate + manifest |

The locked cohorts (E4 + E5) stay closed until Stage 3: development selections frozen, CAIRN preregistration, lock freeze, and an authorization with the preregistration URL (enforced by the gate).

