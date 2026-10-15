# Strong baselines — implementation and outcome-free validation (rule R-K)

2026-10-14. Code: [src/cairn/baselines_ml.py](../../../../src/cairn/baselines_ml.py), behind the `ItemModel` interface of `cairn.baselines`.

- **Environment:** `.venv-cairn-ml` ([requirements-cairn-ml.lock](../../../../requirements-cairn-ml.lock)). It is separate from the frozen numerical stack used for every CAIRN and confirmatory computation.
- **Validation:** [scripts/baseline_validation.py](scripts/baseline_validation.py) and [scripts/baseline_report.py](scripts/baseline_report.py), with evidence in [evidence/baselines/](evidence/baselines/).
- **Every outcome below is synthetic.**

## 1. The ladder

| Tier | Model | Item-level use | Configurations (nested, learner-grouped) | Fitted parameters (pooled split) |
|---|---|---|---|---|
| B3 | Elastic net on 49 whole-video features (six channels × mean, SD, 10/50/90% quantiles, lag-1 autocorrelation, slope, SD of 10-s blocks; recording invalid fraction) | Cross-fitted cell-score logit stacked into IRT-M2 | 9 (α × l1 ratio) | ~80 |
| B3 | Random forest (500 trees) | idem | 1 | ~19k nodes |
| B3 | LightGBM | idem | 8 | ~1.6k |
| B3 | CatBoost | idem | 4 | ~4.9k |
| B3 | GPBoost (trees + learner random effect; Sigrist 2022) | idem | 4 | ~1.1k |
| B3 | **TabPFN v2** (Hollmann et al., *Nature* 2025; Apache-2.0 weights) | idem | 1 (in-context) | 0 fitted |
| B3-item | **LightGBM boosted from the IRT-M2 marginal logit** on item rows: whole-video features + the item's anchored-window features | Direct | 8 | ~1.5k |
| B3-item | **GPBoost with crossed learner and item random effects** (binary, Laplace) on the same row features | Direct | 1 | ~0.7k |
| B4a | **MantisV2** (2026), video level: frozen embeddings of each channel's whole recording, training-fitted PCA (8), ridge | Stacked | 9 (ridge) | ~90 |
| B4a | **MantisV2 / Mantis-8M / MOMENT-1-small, anchored** (ablation A4-FM): frozen embeddings of each anchor window, training-fitted PCA (8), window minus recording, CAIRN's Rasch head | Direct | fixed | ~100 |
| B4a | **MOMENT-1-small** (ICML 2024), video level | Stacked | 9 | ~90 |
| B4b | **Gated-attention MIL** (Ilse et al. 2018) over per-second channels, cell score as bag label | Stacked | fixed | ~2.4k |
| B4b-item | **Text-conditioned item attention:** attention softmax(β · relevance(item text, transcript at t)) with β learned; engagement map MLP (or linear); pooled term centred within cell and item; IRT-M2 offset. Epochs chosen on an inner validation split | Direct | 2 declared configurations | ~0.5k |
| B7 | **TCN encoder** (two dilated convolutions, 9-s receptive field, K = 3), masked-span pretraining on the split's training learners only; anchored pooling; CAIRN head (ablation A4) | Direct | fixed | ~2.4k |
| B5, B6, B9 | IRT-M2, IRT-whole, CAIRN-linear, Lallé-style pooled window classifier (Stage 1) | — | — | — |

**Not run, with reasons:**

| Model | Reason |
|---|---|
| **TabPFN ≥ 2.5** | Weights gated behind a non-commercial licence that only the user can accept |
| **EEG foundation models** (CBraMod, REVE, LaBraM) | EEG is excluded from the primary (Stage-0 reliability SB .06; G01-R EEG increment −.004). The BBBD EEG (128 Hz, uncertified units, non-10-20 montage) would need resampling and channel mapping to each model's conventions, which is substantial engineering for a modality that cannot enter CAIRN's claims. Stage 2 can add them if wanted |
| **MOMENT-1-large** | The small checkpoint was used: CPU budget |

Every model fits on the training rows of a split only. `ItemData` refuses outcomes on test rows.

## 2. Validation results

Filled by `scripts/baseline_report.py` ([evidence/baselines/summary.md](evidence/baselines/summary.md)).

### 2.1 Checks on every model (pooled lock, split 0) — `evidence/baselines/checks*.json`

**All 17 ML baselines are deterministic and fold-safe.**

- Refitting gives bit-identical predictions.
- Perturbing one held-out learner's signals leaves **every other held-out prediction bit-identical**, while the perturbed learner's own predictions change.
- The one exception to the last point is elastic net. It shrank to an intercept on that split, so its check is vacuous rather than failed.

### 2.2 Negative and positive controls

Mean held-out S_item over IRT-M2. Pooled lock: 4 replicates per scenario (N2s: 2). Development: 2.

| Model | Pooled N0 (negative) | Pooled N2 (person-level, r = .5) | Pooled N2s (post hoc, r = .9) | Pooled ALT3 (anchored, OR 3, ρ .7) | Development N0 | Development ALT3 |
|---|---|---|---|---|---|---|
| B3 elastic net | −.0006 | −.0021 | +.0141 | −.0008 | −.0025 | +.0009 |
| B3 random forest | −.0016 | +.0040 | +.0088 | −.0013 | −.0012 | −.0003 |
| B3 LightGBM | −.0006 | +.0034 | +.0063 | −.0010 | −.0010 | −.0013 |
| B3 CatBoost | −.0000 | +.0035 | +.0133 | −.0014 | −.0003 | −.0002 |
| B3 GPBoost | +.0003 | −.0000 | +.0022 | −.0003 | +.0002 | −.0015 |
| B3 TabPFN v2 | −.0007 | −.0013 | +.0078 | −.0004 | −.0027 | −.0022 |
| B4a MantisV2, video | +.0011 | −.0009 | +.0049 | −.0015 | +.0001 | +.0014 |
| B4a MOMENT, video | −.0001 | −.0026 | +.0028 | −.0019 | −.0008 | +.0007 |
| B4b attention-MIL | −.0001 | +.0040 | +.0097 | +.0001 | +.0000 | +.0001 |
| B5 IRT-whole | −.0083 | **+.0139** | +.0092 | −.0020 | +.0001 | −.0026 |
| B3-item LightGBM residual | −.0122 | +.0047 | — | **+.0174** | −.0023 | **+.0163** |
| B3-item GPBoost, crossed RE | +.0011 | +.0033 | — | **+.0176** | +.0024 | **+.0195** |
| B4a MantisV2, anchored (A4-FM) | −.0098 | +.0017 | — | **+.0249** | −.0067 | **+.0226** |
| B4a Mantis-8M, anchored (A4-FM) | −.0064 | −.0007 | — | **+.0276** | −.0077 | **+.0221** |
| B4a MOMENT, anchored (A4-FM) | −.0058 | −.0029 | — | **+.0116** | −.0104 | +.0003 |
| B4b text-attention MIL | −.0124 | +.0021 | — | **+.0157** | −.0029 | **+.0147** |
| B4b text-attention, linear | −.0019 | +.0106 | — | **+.0199** | +.0003 | **+.0166** |
| B7 TCN encoder (A4) | −.0075 | +.0045 | — | **+.0376** | +.0002 | **+.0329** |
| B9 Lallé-style | −.0829 | −.0960 | — | −.0643 | −.0690 | −.0261 |
| B6 CAIRN-linear (d = 1, reference) | −.0084 | +.0032 | — | **+.0463** | −.0047 | **+.0420** |

### 2.3 Verdicts (rule R-K)

| Criterion | Result |
|---|---|
| **Negative control** | Passed by every model: no positive mean S_item beyond 2 Monte Carlo SE under N0. Flexible item-level learners pay an overfitting cost under the null (about −.01), as CAIRN does |
| **Anchored positive control** | Passed by every anchored or item-level learner (z = 2.9–36 on the pooled lock). Ranking under the CAIRN generator: CAIRN > TCN > Mantis anchored > text-attention ≈ item-level boosting > MOMENT anchored. This comparison favours CAIRN by construction and is **not** evidence of superiority (R-K) |
| **Person-level positive control (declared, N2, r = .5)** | Met only by IRT-whole (+.014, z 3.5) and by models with a person-level path. The flexible whole-video learners stay at ≤ +.004 (z ≤ 1.6), so **this criterion is not met** for B3, B4a-video and B4b-video |
| **Post hoc functional check (N2s, r = .9; added after seeing N2, labelled post hoc, decides nothing about CAIRN)** | Every whole-video learner gains (+.002 to +.014). So the learners are implemented correctly and do learn a strong person-level signal. Under the declared r = .5 signal, ~190 training cells are too few for 49-feature flexible learners to beat a 6-column linear model. This is the G01-R whole-video finding, reproduced |
| **B9 (Lallé-style)** | Strongly negative everywhere: it has no item-easiness term, so it cannot compete with IRT-M2 at item level. It stays as the closest-prior-method reference (as in Stage 1) |

**Compute per replicate** (5 folds, CPU, one core, under load):

| Range | Models |
|---|---|
| 0.2–40 s | IRT / CAIRN / LightGBM / GPBoost / elastic net / random forest / anchored MantisV2 and MOMENT |
| 3–6 min | CatBoost, TabPFN v2, MantisV2-video, attention-MIL, text-attention, TCN, Mantis-8M anchored |
| 15 min | MOMENT video level (embedding) |

**Implication for Stage 2.** All 17 baselines are ready to run on development outcomes (`stage2.run_ml`). The strongest competing baseline for NH3 is chosen there by development S_item (`stage2.select_strongest`), excluding the anchored FM/TCN front ends: they are CAIRN with a different representation and are reported as ablation A4.

