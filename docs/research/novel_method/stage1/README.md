# Novel-method Stage 1 — outcome-free implementation and design simulation

2026-10-13 to 2026-10-14. Executed on the user's instruction to carry out **Stage 1 only**, following [research plan v1.2](../research_plan.md) and [stage0/stage1_spec.md](../stage0/stage1_spec.md). **Status: STAGE 1 COMPLETE. Stopped before Stage 2. No outcome of any cohort was accessed.**

| Document | Content |
|---|---|
| [entry_state.md](entry_state.md) | Repository and freeze state before any Stage-1 output |
| [simulation_methods.md](simulation_methods.md) | Generator, scenarios, analysis per replicate, runs |
| [simulation_report.md](simulation_report.md) | Results: calibration, power, MDE, usefulness mapping, redesign, clustering, joint T1/T2, stop rule, NH4, sensitivity |
| [decisions.md](decisions.md) | S1-D01–S1-D19 and S1-I01–S1-I13; global D084–D095 and INF-112–INF-123 |
| [evidence/](evidence/) | Pre-declared rules (hash-stamped), run manifests and replicates, code snapshots, tables, figures, `summary.json`, verify and test logs, `SHA256SUMS` |

Odds ratios (OR) are per SD of the latent moment state at reliability ρ = .4 unless stated. Power is at one-sided α = .05.

## Answers to the questions set for Stage 1

### 1. Type-I error of every planned primary test

500 replicates per null; B = 199; R = 3 × 5-fold learner-grouped CV. These are the maxima over the pure null (N0), fatigue/position (N1), person confound (N2) and non-timed data loss (N3). Per-scenario values: [simulation_report §2](simulation_report.md#2-type-i-error-of-every-planned-test).

| Test | E4 | Development | E4 + E5 pooled |
|---|---|---|---|
| T1 (learner-block Freedman–Lane, CV) | .058 | .060 | .058 |
| T2 (moment relocation, CV) | .050 | .048 | .066 |
| T2c (circular shift, CV) | .048 | .046 | .066 |
| **NH1 = T1 ∧ T2 (plan)** | **.042** | **.040** | **.042** |
| T1lr / T2lr / T2clr (likelihood-ratio) | .064 / .064 / .052 | .058 / .056 / .062 | .066 / .060 / .068 |
| **NH1lr** | **.050** | **.036** | **.052** |
| NH4 validity test (T2 / T2lr; N0, N3) | .050 / .062 | .058 / .050 | .060 / .068 |
| Development stop rule (false go) | — | **.008** | — |

**All pass the ≤ .07 criterion.** The one failure among the candidate redesigns is the frozen-direction LR test on the pooled lock under N2 (.076 / .078), which was therefore excluded.

Under the added non-linear fatigue null (N1q, 500 replicates), linear detrending leaves a residual confound:

- every intersection stays ≤ .068;
- single tests reach .072–.082. The worst are the pooled LR tests (T1lr .082, T2lr .080) and E4 CV T2 (.074).

This is what decides the lock design under rule R-E (question 6).

The parametric full-data Wald tests, by contrast, reach .12–.34 under the temporal confound. The learner-cluster sandwich over-rejects even under N0 (.086 in E4).

### 2. Power curves

Figure: [evidence/figures/power_nh1_rho04.png](evidence/figures/power_nh1_rho04.png). Full grids for ρ = .2 / .4 / .7 are in simulation_report §3.

| Set and statistic | OR 1.15 | 1.25 | 1.35 | 1.50 | 1.75 | 2.00 | 2.50 |
|---|---|---|---|---|---|---|---|
| E4, NH1 (plan, CV) | .08 | .12 | **.32** | .51 | .84 | .95 | 1.0 |
| E4, NH1 (LR) | .10 | .18 | .34 | .53 | .85 | .95 | 1.0 |
| **Pooled E4 + E5, NH1 (CV): design 5** | .12 | .33 | **.51** | .85 | .99 | 1.0 | 1.0 |
| Pooled E4 + E5, NH1 (LR): design 7 | .14 | .36 | .66 | .93 | 1.0 | 1.0 | 1.0 |
| Development, NH1 (CV) | .09 | .26 | .49 | .83 | .99 | 1.0 | 1.0 |

### 3. Minimum detectable effects (80% power)

| Set | NH1 CV | NH1 LR | At ρ = .4: S_item / ΔAUC_wp at the MDE (population) |
|---|---|---|---|
| E4 | 2.37 / **1.72** / 1.47 | 2.24 / 1.70 / 1.47 | ≈ .010 / .010 |
| Pooled E4 + E5 | 1.82 / 1.48 / 1.35 | 1.73 / **1.43** / 1.31 | ≈ .005 / .006 |
| Development | 1.82 / 1.49 / 1.33 | 1.73 / 1.44 / 1.31 | .006 / .007 |

MDEs are listed as ρ = .2 / .4 / .7. Spec §1.7(3) defines δ_item as the OR where development NH1 reaches 80%: **1.49** (S_item .006, ΔAUC_wp .007). It is recorded as the minimum *detectable* effect, **not** as the minimum useful effect (S1-D14).

### 4. Do T1 and T2 behave correctly jointly?

**Yes, as tests:**

- each is calibrated;
- their intersection is conservative (NH1 ≤ .042 in N0–N3);
- under alternatives they reject together, so the intersection costs 3–8 power points against the better single test.

**But they are nearly redundant** (p-value correlation .93–.98 under the nulls), and T2 does **not** protect against learner-specific temporal trends. In the plan-literal form, T2 and T2c rejected at .09–.10 under N1. The protection comes from the within-recording detrending, which is now part of the primary method (S1-D06). The falsification claim N-d is unchanged in content, with its scope stated precisely (S1-D17).

### 5. Does clustering materially change the earlier analytic power estimate?

**Clustering itself: no.** The moment regressor is centred within learner × video and within item, so learner, item and video effects are orthogonal to it.

- In E4, 46% of anchorable responses share a moment with another item. The implied within-moment residual correlation is small (about .07).
- The empirical variance of λ̂ equals its model-based variance (ratio 1.03 in E4, 0.94 pooled, 0.79 development).
- Even the naive independent-response Wald test is calibrated under N0.

**The earlier estimate is still far too optimistic, for another reason.** The plan §20.3 / [S0-7] analytic MDE was OR ≈ 1.33. A 1-df oracle Wald test on the true composite confirms about 1.34. The planned procedure, however, must:

- estimate the moment direction over six channels from about 31 training learners per fold;
- test by permutation;
- pass two tests.

Its E4 MDE is **1.72**, equivalent to the analytic test with about 1/3.4 of the responses. Direction estimation dominates this loss (simulation_report §6).

### 6. Is E4 sufficiently powered?

- **For the prespecified minimum useful effect: yes.** The plan §20.2 threshold, S_item ≥ .01 and ΔAUC_wp ≥ .02, is unchanged. It corresponds to OR ≈ 2.16 at ρ = .4 (3.13 at ρ = .2; 1.80 at ρ = .7). E4 NH1 power there is .97 (1.0 at the OR where the cross-validated estimate meets the threshold on average, 2.57).
- **For the plausible-effect criterion of spec §1.7(4) (OR ≤ 1.35): no.** Power is .32, and .51 at OR 1.5.
- **The redesign is therefore triggered** (pre-declared rule R-B3). Plausible effects (OR 1.15–1.5) lie below the useful threshold. At those effects E4 can neither detect them reliably nor would they count as useful.

**Redesign (S1-D15, rules R-B2 and R-E; needs your decision).** Eight candidate designs were declared before the main grid:

| # | Design | Max false detection | Power OR 1.35 | MDE |
|---|---|---|---|---|
| 1 | E4, CV (plan as written) | .058 | .32 | 1.72 |
| **5** | **Pooled E4 + E5, CV (declared options a + c), NH1 confirmatory, NH2–NH5 descriptive** | **.066 (N1q .070)** | **.51** | **1.48** |
| 7 | Pooled E4 + E5, LR statistic | .066 (N1q **.082**) | .66 | 1.43 |
| 8 | Pooled, LR, frozen development direction | .078 (inadmissible) | .74 | 1.39 |

The other four (frozen-direction and LR variants on E4, and CV with frozen direction pooled) are in simulation_report §5.

- **No admissible design reaches .80 at OR 1.35.** The shortfall is reported, and the threshold was not weakened.
- **By the declared choice rule (R-B2)**, design 7 has the smallest MDE.
- **The pre-declared non-linear-fatigue check (R-E) then fails for design 7:** pooled N1q gives T1lr .082 and T2lr .080. Design 5 passes it (T1 .066, T2 .070, NH1 .056).
- **Result:**
  - **Design 5 is the design ready now.** It is a pooled E4 + E5 lock with the plan's CV statistic, NH1 confirmatory and NH2–NH5 descriptive, built only from declared spec options. MDE 1.48; power .51 at OR 1.35 and .85 at 1.5.
  - **Design 7 is an optional upgrade.** It reaches MDE 1.43 (power .66 at 1.35) and needs (i) your approval of the LR statistic and (ii) a non-linear within-recording trend control, specified and validated by simulation. That is about 3 h of compute on the pooled lock.
- **What either design changes.** E5 moves from separate secondary cohort into the confirmatory test, with experiment-specific item easiness. Design 7 also replaces the test statistic with the full-data likelihood-ratio gain under the *same* permutation nulls.
- **What it costs if E5 differs.** If E5's effect is half of E4's, pooled power at OR 1.5 falls from .93 to .55.

### 7. Changes required before preregistration

| # | Change | Status |
|---|---|---|
| 1 | Primary form = within-recording detrended CAIRN-linear (S1-D06), with the explicit centring and estimation rules (S1-D03, S1-D04, S1-D07) | In force (plan v1.3 [S1-1]–[S1-4]) |
| 2 | **Lock design: design 5 (ready now) or design 7 (upgrade; needs change 10)**, recorded under a decision ID before any outcome is read. Either choice changes E5's role. E4-only remains possible only by accepting power .32 at OR 1.35 | **Your decision** |
| 3 | If design 7: define the LR statistic in the preregistration (full-data conditional log-likelihood gain over IRT-M2, leave-one-learner-out references, the same T1/T2/T2c nulls). S_item and ΔAUC_wp stay cross-validated | Needs approval |
| 4 | Minimum useful effect unchanged. Disclose that the cross-validated S_item is biased downward in small cohorts (pure-null mean −.011 in E4, −.006 pooled) | In force ([S1-8]) |
| 5 | NH4: specify a gaze-block test conditional on in-window validity and simulate it under N4 before any "behaviour beyond data loss" claim | Open (S1-D16) |
| 6 | N-d wording: randomization nulls plus a within-recording trend control | In force ([S1-10]) |
| 7 | Lock budget B = 999, R = 10. Kernel and hyperparameters selected in development and frozen | In force (S1-D18, S1-D11) |
| 8 | Re-run the decisive simulations (N0–N3 at 500 replicates; ρ = .4 alternatives) on the **frozen human anchors**, for development and the chosen lock. The number of moments drives T2 and power (E4 has 19) | After G-AN |
| 9 | Report the realistic expectation honestly: at plausible effects, the most likely result is a development stop (go ≤ .25 at OR ≤ 1.5) or the "Weak" category | In the record (S1-I13) |
| 10 | **Non-linear temporal control.** Linear detrending leaves single tests at .072–.082 under non-linear fatigue. Specify a non-linear within-recording control (for example quadratic detrending) and simulate it: N0–N3, N1, N1q and power. This is required for design 7 and advisable for every design (E4 CV T2 .074 under N1q) | **Open** (rule R-E) |

### 8. Implementation and test status

| Component | Status |
|---|---|
| `src/cairn` Stage-1 modules (spec §2.2) | **Implemented.** `design`, `item_keys`, `clock`, `features`, `model`, `inference`, `baselines`, `simulate`, `simrun`, `analysis`, `manifest`, `checks`, `cli`, `paths_stage1` |
| Kernel lag / width grid (spec §2.2) | Implemented: `design.KERNEL_GRID`, 12 configurations; selection is a Stage-2 task |
| Baseline ladder (spec §5) | B0, B1/B2 (frozen G01-R), B5, B6 and B9 implemented behind `ItemModel`. B3, B4a/b and B7/B8 are stubs that raise `MissingDependency`, because their packages need a download (S1-D02) |
| Gated outcome loader | `cairn.gate` (Stage 0). `python -m cairn run --scope development` → **REFUSED**, exit 2, verified at exit |
| Manifests | Hash-bound, written before fitting. Stage 2+ refuses provisional anchors and requires `anchor_freeze_sha256` |
| Leakage tests 1–10 (spec §3) | **All pass.** Learner independence, reference rule, normalization isolation, pretraining isolation, anchor freeze, outcome gate, temporal round trip, identity probe, permutation-null uniformity on the stored simulations, determinism |
| `python -m cairn verify` (full) | **PASSED**: gate, incidence, item keys, anchor hash, timeline round trip, fold safety, identity probe, determinism ([verify_exit.json](evidence/verify_exit.json)) |
| Full test suite (`unittest discover -s tests`) | **170 tests, OK** (2 skipped, both pre-existing G01-R / John conditions); 40 of them are Stage-1 tests ([unittest_exit.log](evidence/unittest_exit.log)). Entry: 130 OK |
| G01-R `verify-freeze` | **VERIFIED** at exit |
| Reproducibility | Each replicate depends only on (seed, set, scenario, replicate). The current `src/cairn` reproduced stored replicates **bit for bit** (E4 N0, development N1, pooled OR 1.35). The runs' code snapshots are kept under `evidence/sim*/code_snapshot/` |

### 9. Files changed in Stage 1

**New source and tests:**

- `src/cairn/`: `__main__.py`, `analysis.py`, `baselines.py`, `checks.py`, `cli.py`, `clock.py`, `design.py`, `features.py`, `inference.py`, `item_keys.py`, `manifest.py`, `model.py`, `paths_stage1.py`, `simrun.py`, `simulate.py`;
- `tests/test_cairn_stage1.py`.

**Stage-0 source:** unchanged. `src/cairn/paths.py` was extended during Stage 1 and then restored byte-identical to its Stage-0 hash (S1-D19); `stage0/SHA256SUMS` is 64/64 OK.

**Environment:**

- `requirements-cairn.lock` (new);
- `.gitignore` (adds `.venv-cairn/`);
- `.venv-cairn/` (git-ignored; reads the frozen `.venv` read-only).

**Stage-1 record (all new), in `docs/research/novel_method/stage1/`:**

- `README.md`, `entry_state.md`, `decisions.md`, `simulation_methods.md`, `simulation_report.md`, `scripts/report.py`;
- `evidence/`: entry and exit logs and hashes, `predeclared_rules.md` and `.sha256`, `summary.json`, `tables/` (16 files), `figures/` (4);
- simulation runs, each with `MANIFEST.json`, `run.log` and the replicates as JSONL:
  - `sim/` (86 files, 16,800 replicates, plus a code snapshot);
  - `sim_addendum/` (800 replicates, plus a code snapshot);
  - `sim_n1decision/` (1,000 replicates).

The evidence folder is 48 MB, mostly JSONL.

**Amended:**

- `docs/research/novel_method/research_plan.md` (v1.3, [S1-1]–[S1-13]);
- `docs/research/novel_method/README.md`;
- `docs/research/README.md`;
- `docs/research/decision_log.md` (D084–D095);
- `docs/research/inference_register.md` (INF-112–INF-123).

**Git-ignored caches:** `data/derived/cairn/stage1/` (fold-safe channel caches, outcome-free).

**Outside the repository:** the project memory note.

**Nothing else changed:** no G01-R, John or Stage-0 file, frozen environment or access log.

### 10. Outcome access

**No outcome access occurred.** No development, locked or external outcome file was opened, and no learner response, score or correctness value was read. Every outcome in the simulations is synthetic. At exit:

| Check | Entry | Exit |
|---|---|---|
| BBBD outcome-access log | 15 lines, `2ea691fa…` | **15 lines, `2ea691fa…`** (unchanged) |
| John outcome-access log | 1 line, `766489e7…` | **1 line, `766489e7…`** (unchanged) |
| `analysis_freeze_cairn/` (freeze, authorization, access log) | absent | **absent** |
| `python -m cairn run --scope development` | — | **REFUSED** (no CAIRN freeze) |
| Stage-0 evidence and code hashes | 64/64 | **64/64** |
| G01-R freeze | VERIFIED | **VERIFIED** |

Files read by Stage 1 are listed in [entry_state.md §3](entry_state.md#3-what-stage-1-may-and-may-not-read). They are outcome-free: per-second signals, availability flags, the item bank and questionnaire sidecars, timelines and provisional anchors. Nothing was downloaded, annotated, deposited, sent to an author or committed.

## Remaining gates before Stage 2

Stage 2 means development item-outcome access, logged. It may start only when **all** of the following hold:

1. **G-AN passes.** Two human annotation files pass `cairn.anchors.gate_g_an`. The adjudication log is complete. `cairn.anchors.freeze()` writes the anchor freeze record, whose SHA-256 enters the CAIRN freeze (spec §4). The manifest and gate refuse provisional anchors for Stage 2+.
2. **Simulation re-run on the frozen human anchors** (change 8). Calibration (≤ .07 in N0–N3) and the chosen lock design's power are confirmed on the human moment structure.
3. **Lock-design decision recorded.** You choose design 5, design 7 (only after change 10) or E4-only (accepting its power), and it gets a decision ID before any outcome is read (spec §1.7(4)).
4. **Commit and CAIRN freeze.** You commit the Stage-0/1 work. A CAIRN freeze record (`analysis_freeze_cairn/FREEZE_RECORD.json`, with `anchor_freeze_sha256`) is created and verified by `cairn.gate`.
5. **Explicit authorization.** A scoped "development" outcome-access authorization from you; every access is logged. `python -m cairn run --scope development` currently refuses (verified).
6. **Optional:** authorization to download the optional baseline packages (torch, lightgbm, catboost, gpboost, tabpfn) if B3, B4 and B7/B8 are to run in Stage 2. Without them, the B0, B1/B2, B5, B6 and B9 rungs run.

**Before preregistration (Stage 3):** changes 2–5 and 10 above.
