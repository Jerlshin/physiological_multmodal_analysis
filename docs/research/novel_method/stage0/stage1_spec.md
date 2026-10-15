# Stage 1 specification — design simulation and outcome-free implementation

2026-10-13. Stage 1 is **outcome-free**. It ends with a calibrated simulation report and a validated `src/cairn`. Stage 2 (development outcome access) needs a separate, explicit user authorization (plan §23) and a frozen human anchor set.

## 1. The Stage-1 simulation (exact definition)

**Purpose.** Calibrate T1, T2 and their intersection (plan §20.1), and set the minimum useful item effect and the development stop rule, on the **real incidence, anchor structure and signals**, with synthetic outcomes.

### 1.1 Incidence

Built from outcome-free manifests:

| Set | Data |
|---|---|
| Development | E3 attentive tested exposures (6 videos) + E1 session 1 on Light bulbs, Internet, Birth rate. Only cells with an eligible outcome *flag* (`gate_behavior_eligible`, an availability flag; values not read) and gaze QC ≤ 0.50 |
| Locked primary | E4 session-2 cells (Stars, Immune, Related) |
| Locked secondary | E5 session-2 cells (same videos) |
| Items | The anchorable items of each video from the anchor table. Provisional anchors are used in Stage 1; the frozen human set is used in Stage 2+ |

- Shared anchors keep their sharing.
- Diffuse and non-anchorable items are kept as items with a zero moment term (they still inform β and θ).

### 1.2 Signals

**Real moment terms only.**

- Each learner's anchored moment terms come from the real per-second channels (§3), computed under the **regime's reference rule**:
  - development: leave-learner-out attentive peers within the training fold;
  - lock: training-fold peers, or the unlabelled other half-cohort for regime C.
- For the locked cohorts, the moment terms of the tested exposures are computed from their signals. These are outcome-free, and their use was already disclosed for G01-R.
- No learner's outcomes are needed or read.

### 1.3 Generating model

```
logit P(y_pvj = 1) = beta_vj + theta_pv + lambda_true * x*_pvj [+ confound terms]
beta_vj  ~ N(m_beta, s_beta^2)    m_beta in {0.4, 0.8}; s_beta in {0.8, 1.2}   (accuracy about 0.6-0.7 on 4-option items)
theta_pv = u_p + w_pv;  u_p ~ N(0, tau^2), tau in {0.5, 1.0};  w_pv ~ N(0, 0.3^2)
x*_pvj   = latent moment state; observed x_pvj = real anchored moment term (z-scored within the set)
           constructed so that corr(x, x*) = sqrt(rho), rho in {0.2, 0.4, 0.7}
lambda_true per SD of x*: OR in {1.00 (null), 1.15, 1.25, 1.35, 1.50}
```

**Signal construction.** x* is built from the observed x plus independent noise, scaled so the observed–true correlation is √ρ. The observed covariance structure of x is kept exactly: autocorrelation across shared anchors, missingness, and person-level heterogeneity in variance.

### 1.4 Null and confound scenarios

Type-I error is assessed under each:

| Scenario | Construction | What it checks |
|---|---|---|
| N0 | λ = 0 | Pure null |
| N1 (fatigue / position) | β depends on item position; θ depends on the learner's engagement trend (slope of the channels over the video) | The circular-shift null must hold |
| N2 (person confound) | u_p is correlated (r = .5) with whole-video engagement ē | λ must stay unbiased (within-learner identification) |
| N3 (data loss, not content-timed) | Outcomes depend on the learner's *overall* invalid fraction | T2 must not reject |
| N4 (content-timed data loss) | Outcomes depend on in-window long-episode loss (NH4 true) | T2 should reject for the validity channel only |

### 1.5 Analysis per replicate

The analysis is identical to Stage 2, at reduced inference budget:

| Step | Specification |
|---|---|
| Models | IRT-M2, IRT-whole, CAIRN-linear (primary), B9 (Lallé-style pooled classifier) |
| CV | Learner-grouped CV, R = 3 repetitions |
| T1 | Learner-block Freedman–Lane, B = 199 |
| T2 | Permutation of **distinct anchor moments** within video, B = 199; circular shift ≥ 30 s as sensitivity |
| Intersection | Intersection–union of T1 and T2 at α = .05 |
| Development stop rule | Plan §20.5 (i)–(ii), evaluated on the development set |

### 1.6 Replicates

≥ 500 per null scenario and ≥ 200 per alternative. Seeds are fixed and recorded in the manifest.

### 1.7 Pass criteria

All must hold for Stage 2 to be proposed:

1. False detection of T1, T2 and the intersection is **≤ .07** in N0–N3. For T2 in N3, T2 must also not reject in more than 7% of replicates.
2. The **development stop rule** (go-to-lock) fires in ≤ 10% of N0–N3 replicates.
3. The minimum useful item effect δ_item is fixed from the simulation as the OR (at ρ = .4) where development power reaches 80%. It is reported with its ΔAUC_wp and S_item equivalents.
4. **Locked power:** report the power of the E4 (and E4 + E5) intersection test at δ_item. If E4 alone is below .80 at OR ≤ 1.35, the confirmatory design is **revised before Stage 2**, by one of the declared options:
   - (a) E4 + E5 as one locked cohort, with experiment intercepts;
   - (b) one-sided T1 and T2;
   - (c) NH1 confirmatory on E4 + E5 with NH2–NH5 descriptive.

   The chosen option is recorded with a decision ID before any outcome is read.

### 1.8 Compute

About 1–3 CPU-days at B = 199. A Freedman–Lane fit needs about 1 s of ridge/Laplace work. Use 5 workers under `caffeinate`, as G01-R did.

## 2. `src/cairn` implementation

### 2.1 Existing modules (Stage 0, tested)

| Module | Responsibility |
|---|---|
| `paths`, `exposures` | Constants; outcome-free exposure list (whitelisted columns) |
| `extract` | 10 Hz ocular series from the verified archives (frozen validity rule) |
| `timeline`, `transcripts` | Stimulus alignment; recording-clock transcripts |
| `channels` | 1 Hz reference-free and reference-relative channels; `reference_stats` refuses self-inclusion |
| `pooling` | Kernels and anchored moment terms (hard / Gaussian; lag, width) |
| `anchors` | Item bank (no responses); R1 retriever; anchor table; `gate_g_an`; `freeze` (human-only) |
| `encoder` | Label-free linear masked encoder, reference distiller, random encoder |
| `stats` | Two-way decomposition, AUC, logistic / softmax, grouped K-fold |
| `gate` | Gated item-outcome loader. Refuses without a CAIRN freeze + scoped authorization; logs every access |

### 2.2 To implement in Stage 1 (outcome-free)

| Module | Responsibility | Key requirement |
|---|---|---|
| `design` | Item-level incidence per set: (learner, video, item, anchor-id) from manifests, eligibility flags and the anchor table | Never reads outcome values; asserts the set definitions of plan §15.2 |
| `item_keys` | Map the forensic item table's `question_no` to the item bank's (video, local item) | Outcome-free: question hashes and `gate_closure_quiz_content_map.csv`. Verified before any access |
| `features` | Per learner × video: moment terms per anchor (regime-specific references, fold-safe standardization), person-path summaries ē / ē^anch, C, Q, experiment | Cached by split identity (as G01-R); fit statistics from training learners only |
| `model` | Penalized Rasch GLMM: item easiness (shrunk to the video mean), learner level (C, Q, ē^anch, experiment), u_p (Laplace), moment λ_c; kernel lag / width grid | Deterministic; ≤ 20 configurations in nested CV; IRT-M2, IRT-whole and CAIRN variants share the code |
| `baselines` | B0–B9 behind one interface | See §5 |
| `inference` | T1 (learner-block Freedman–Lane on held-out item log-loss), T2 (distinct-anchor permutation; circular shift), nested-CV intervals, ΔAUC_wp, S_item | Exact reuse of permutation logic patterns from `g01r.inference` where applicable |
| `simulate` | §1 generator and replicate runner | Same analysis code path as real runs |
| `manifest` | Experiment manifests (§6) and run records | Hash-bound |
| `cli` | `python -m cairn {verify, simulate, run}`; `run` calls the gate | `run` refuses without the freeze and authorization |

## 3. Leakage tests (must pass before Stage 2)

1. **Learner independence:** every row of a learner (all videos, items, seconds) falls in one fold. Asserted per split.
2. **Reference rule:**
   - `reference_stats` refuses the target learner (exists).
   - Regime A references contain only training-fold learners.
   - Regime C references contain only the other half-cohort and never use outcome, condition or quality to select.
3. **Normalization isolation:** standardization, KDE bandwidths and any CorrCA filters are fitted on training learners. The test perturbs a test learner's data and checks that no fitted statistic changes.
4. **Pretraining isolation** (if an encoder is used): fitted per outer fold without test-fold learners (asserted in `encoder_stage0.py`; carried into `features`).
5. **Anchor freeze:** every run verifies that the anchor-table hash equals the frozen hash and refuses otherwise. The anchors were built without outcomes (protocol blinding; documented).
6. **Outcome gate:**
   - no outcome file is opened before authorization (exists: mocked `read_parquet` test);
   - locked scopes need a preregistration URL (exists).
7. **Temporal alignment:** a round-trip test, source time → recording time → source time, on the timeline table. Anchors in FAIL seconds are rejected.
8. **Identity probes:** item-centred moment terms at chance (balanced accuracy within the 95% permutation band) on each run's training data.
9. **Permutation-null sanity:** with shuffled outcomes (synthetic), T1 and T2 p-values are uniform (KS test) on a small replicate set.
10. **Determinism:** the same manifest gives bit-identical predictions.

## 4. Anchor verification (before Stage 2)

1. G-AN passes on two human annotation files (`cairn.anchors.gate_g_an`).
2. The adjudication log is complete. Every disputed item is resolved or set diffuse.
3. `cairn.anchors.freeze()` writes the anchor freeze record. Its SHA-256 enters the CAIRN freeze record (`analysis_freeze_cairn/FREEZE_RECORD.json`, field `anchor_freeze_sha256`).
4. Report agreement between human and provisional (R2) anchors as a descriptive check of R2's quality. R2 is never used for inference once human anchors exist.

## 5. Baseline interface

```python
class ItemModel(Protocol):
    name: str
    def fit(self, train: ItemData, config: dict, rng: np.random.Generator) -> "ItemModel": ...
    def predict_proba(self, test: ItemData) -> np.ndarray        # P(correct) per (learner, item)
    def n_params(self) -> int: ...
```

`ItemData` holds:

- per item: incidence, moment terms, person-path features, item ids, video and experiment;
- outcomes only for training rows, populated by the gated loader.

Video-level baselines (B1–B4) are wrapped so that `predict_proba` returns the predicted video score for every item of the video. This keeps video- and item-level metrics comparable.

| Tier | Model | Notes |
|---|---|---|
| B0 | Video mean; IRT-0 (item easiness only) | |
| B1 / B2 | Frozen G01-R M2 / M-gaze / M3 / M4 | Imported from `g01r.models`, unchanged |
| B3 | Whole-video features → elastic net, RF, GBM, GPBoost, TabPFN v2 | Optional dependencies pinned in `requirements-cairn.lock` |
| B4a | Frozen FM embeddings | Optional (GPU / PyTorch) |
| B4b | Attention-MIL over per-second channels | PyTorch |
| B5 | IRT-M2, IRT-whole | |
| B6 | **CAIRN-linear (primary)** | |
| B7 / B8 | Encoder variants (ablation A4); + pupil (ablation) | |
| **B9 (new)** | **Lallé-style pooled classifier** | Reference-free gaze features in each item's window, item identity dropped, learner-grouped CV |

## 6. Experiment manifests

One JSON per run, hash-bound, written before fitting:

```json
{
  "run_id": "...", "stage": "1-simulation | 2-development | 4-locked",
  "code_sha256": "...", "environment_lock": "requirements-cairn.lock sha256",
  "inputs": {"series10_manifest": "...", "channels_1hz": "...", "timeline_table": "...", "anchor_table": "...",
             "anchor_freeze_sha256": "... (Stage 2+)", "item_bank": "74fc8c2f..."},
  "set": "development | locked_primary | locked_secondary", "regime": "A | C",
  "models": ["IRT-M2", "CAIRN-linear", "..."], "grid": {"...": "..."},
  "cv": {"outer": "learner-grouped 5-fold", "repetitions": 10, "inner": 5},
  "inference": {"T1_B": 999, "T2_B": 999, "circular_shift_min_s": 30},
  "seeds": {"cv": 0, "perm": 1, "sim": 2},
  "outcome_access": "none | gate.load_item_outcomes(scope=...)"
}
```

## 7. Reproducibility requirements

- **Environment.**
  - The frozen `.venv` stays untouched.
  - Stage 1 uses a new `.venv-cairn`, with numpy, scipy, pandas and pyarrow pinned to the frozen versions, plus optional `torch==2.x` and `lightgbm` / `tabpfn` pinned in `requirements-cairn.lock`. This follows the `.venv-ext` precedent (JRP-002).
- **Determinism.** Every random step takes a recorded seed. CV folds are a deterministic function of learner ids and the seed (`cairn.stats.group_kfold`).
- **Caches.**
  - `data/derived/cairn/` (git-ignored) holds series, channels and moment terms, each with a manifest and hashes.
  - Synchrony-type caches are keyed by split identity.
- **Records.** Every run writes its manifest, its outputs with hashes and a log. Stage-0 evidence is hash-listed in `stage0/evidence/SHA256SUMS`.
- **Freeze before access.** The CAIRN freeze (code, configuration, frozen anchors, timeline, manifests) is committed by the user and verified at every outcome access, as for G01-R.
