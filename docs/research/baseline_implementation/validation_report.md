# Production validation of the inference (protocol §17.3) — before any outcome access

2026-10-05. **No real quiz outcome was used.**

- V1 uses fully simulated datasets.
- V2 uses the real feature matrices with synthetic outcomes.

Evidence is in [evidence/validation/](evidence/validation/): replicate-level CSVs, the summaries, `validation_verdict.json` and `v1_bit_identity_check.csv`. Each run is tracked in `results/runs/g01r-validation/` and in MLflow.

## V1 — the design simulation re-run through the production pipeline

**What is reused and what is production.**

- **Reused from the design phase:** the generator in `precision_simulation.py`. It covers the actual PAS-core incidence, outcome-only psychometric parameters, nuisance structure, and "proportional" information mixing with the same oracle targets (0 and 0.14) as `inference_calibration.py --person`.
- **Production code:** every fit, split, offset, imputation, penalty choice, permutation, futility bound and interval is computed by `g01r`.
- **Truth:** the production pipeline trained on all 68 learners and scored on 1,500 fresh simulated learners.

**Configuration** (production, frozen): 10 paired permutation repetitions with B = 999; R = 50 point-estimate repetitions; futility corrected-t with z = 3.0 over all 500 folds; nested CV (20 repetitions per dataset in simulation, 200 in the confirmatory run). There are 300 datasets per scenario.

| Scenario | Expected procedure skill | Mean estimate | Permutation detection | Fallback bootstrap detection | P(U₃ < 0.10) | Nested-CV 90% conditional coverage | P(Ŝ ≥ δ) | P(p ≤ .05 and Ŝ ≥ δ) |
|---|---|---|---|---|---|---|---|---|
| Null | −0.009 | −0.007 | **0.060** (MC SE 0.014; 95% CI 0.036–0.093) | 0.057 | 0.937 | 0.907 | 0.007 | 0.007 |
| True skill ≈ 2δ | 0.108 | 0.099 | **0.973** (MC SE 0.009) | 0.817 | **0.050** | 0.880 | 0.837 | 0.837 |

**Targets (protocol §17.3):**

| Target | Result | Status |
|---|---|---|
| False detection ≤ 0.07 | 0.060 | **Met** |
| Power ≥ 0.80 at 2δ | 0.973 | **Met** |
| Futility error ≤ 0.05 at 0.10 | 0.050 | **Met, at the boundary** |

**Reproduction of the design phase within Monte Carlo error:**

| Quantity | Design phase | Production (V1) |
|---|---|---|
| False detection | 0.063 | 0.060 |
| Futility error | 0.043 | 0.050 (difference 0.007 against an MC SE of 0.012) |
| P(rule out 0.10 \| null) | 0.91 | 0.937 |
| Nested-CV coverage | 0.86–0.90 | 0.88–0.91 |
| Power | 0.93 (R = 4 paired repetitions, B = 99) | 0.973 (R = 10, B = 999) |

The production configuration is more powerful, as expected from averaging 10 rather than 4 paired repetitions.

**Futility at the boundary (recorded, not acted on).**

- **Why the error is slightly higher.** The production bound uses all J = 500 fold differences, against J = 40 in the design calibration. The corrected-t standard error is therefore about 9% smaller, so the bound is slightly tighter and the boundary error slightly larger.
- **Why nothing changes.** The result still meets the target, and z = 3.0 is frozen.
- **Reporting consequence.** A "≥ 0.10 ruled out" conclusion carries an error rate of about 5%, as declared. The 95% Monte Carlo interval for that rate is 0.028–0.081.
- **Decision rule unchanged.** The H1 decision table stays as pre-declared.

**Fallback.** It is not triggered; the declared person-bootstrap fallback is less powerful (0.82 versus 0.97) at equal size.

**Bit identity.** Four V1 datasets (two per scenario) were re-run on the final frozen code. Results: bit-identical for all 4 datasets once results pass through the same CSV serialization (raw differences ≤ 1e-16 come from float text formatting); permutation p-values exactly equal ([check](evidence/validation/v1_bit_identity_check.csv)). The production modules on V1's code path were unchanged after V1 started, apart from two bookkeeping dataclass fields.

## V2 — real features, synthetic outcomes

**Design.**

- **Data:** the real PAS-core cells, folds and features, i.e. real C, Q and RF, and SYN recomputed per split from the real signals. Outcomes are drawn from the outcome-only generator.
- **Pure null:** no dependence on anything.
- **Nuisance null:** 30% of the person variance is a linear function of the real C and Q columns. Physiology then carries information only through quantities already in M2, so H1 is still exactly null, but the tested block is collinear with the nuisance.
- **Planted-signal check:** the mean z-score of three real RF features (posterior alpha, heart rate, gaze dispersion) is added with an amplitude giving an expected skill of about 0.10. It checks power on the real feature space and is not a target.
- **Test configuration:** H1 test with 10 paired repetitions and B = 199 (Monte Carlo resolution only; the size of a permutation test does not depend on B); R = 50 for the estimate and the futility bound.

| V2 scenario | Datasets | H1 detection (permutation) | Mean Ŝ (SD) | P(Ŝ ≥ δ) | P(p ≤ .05 and Ŝ ≥ δ) | P(U₃ < 0.10) |
|---|---|---|---|---|---|---|
| Pure null | 200 | **0.030** (MC SE 0.012) | 0.0015 (0.009) | 0.000 | 0.000 | 0.915 |
| Nuisance null (outcomes depend on real C, Q) | 200 | **0.065** (MC SE 0.017) | −0.0049 (0.020) | 0.000 | 0.000 | 0.785 |
| Planted RF signal (expected skill ≈ 0.10) | 100 | 0.920 | 0.097 (0.059) | 0.77 | 0.76 | 0.050 |

**Reading.**

- **Pure null.** On the real, collinear and heavy-tailed feature space with per-split synchrony, the person-block permutation test is conservative (0.030).
- **Nuisance null.** Outcomes depend on C and Q, and the tested block is collinear with them; false detection is 0.065. That is within the 0.07 tolerance and compatible with nominal 0.05 within Monte Carlo error (binomial 95% CI ≈ 0.035–0.11). It is the hardest null for the Freedman–Lane residualization and is recorded as the binding real-feature value.
- **No false useful detections.** No null dataset produced Ŝ ≥ δ, so a false "useful detection" did not occur in 400 real-feature null datasets.
- **Planted signal.** Information planted in real features is detected 92% of the time. The futility bound wrongly rules out 0.10 in 5% of datasets at a true skill just below 0.10, consistent with V1.

## Verdict of the validation step

Every protocol §17.3 target is met on production code, and the real-feature null calibration stays within the false-detection tolerance:

| Check | Value | Target | Status |
|---|---|---|---|
| V1 false detection | 0.060 | ≤ 0.07 | ✓ |
| V1 power at 2δ | 0.973 | ≥ 0.80 | ✓ |
| V1 futility error | 0.050 | ≤ 0.05 | ✓ (boundary) |
| V2 maximum null false detection | 0.065 | ≤ 0.07 | ✓ |

**Detection procedure.** It remains the pre-declared person-block permutation test. The declared fallback is not triggered, as recorded in [validation_verdict.json](evidence/validation/validation_verdict.json), which the confirmatory runner reads.

## End-to-end run of the first confirmatory step (synthetic outcomes)

The exact first post-authorization command was executed end to end on synthetic outcomes: `run --analysis H1_H2` was invoked as `dry-run`, with the frozen configuration except `ncv_reps = 20` (recorded as an override, `frozen=false`). Run `g01r-dryrun-fullscale/H1_H2__20261005T031137Z_0d4efba5`, mirrored to MLflow.

| Check | Result |
|---|---|
| R = 50 point estimates for all 11 regime-A models | ✓ |
| Futility over 500 folds | ✓ |
| Five permutation tests (H1, H2a–d) at B = 999 with 10 paired repetitions | ✓ |
| Holm adjustment | ✓ |
| Nested-CV person/state/cell intervals | ✓ |
| Detection procedure | Read from `validation_verdict.json` (permutation) ✓ |
| H1 decision | "bounded negative", correct for a synthetic null (p = 0.632, Ŝ = −0.0001, U₃ = 0.0001) |
| Artifacts | Predictions, folds, nulls, penalties and `result.json` written; `report` built the tables ✓ |

**Runtime.** 119 s with 5 workers, because all synchrony features were cached.

**The cold nested CV is the dominant cost.** An earlier cold attempt with all 200 nested repetitions was stopped deliberately after 82 min. Its run record stays at status RUNNING, because the process was terminated.

- **Measured throughput.** 50–75 synchrony plans per minute with 5 workers, against 20,000 plans for 200 repetitions. A fully cold H1_H2 run therefore takes about 4.5–6.5 h.
- **What the cache already covers.** The outcome-free synchrony cache now holds:
  - the 500 regime-A splits;
  - nested repetitions 0 to about 69 of H1_H2, about 7,000 plans.
- **Consequence for the real run.** The real H1_H2 run still needs about 13,000 new plans, ≈ 3–4 h.
- **The cache is outcome-free.** Every entry is a deterministic function of the frozen signal caches and code.
- **The cache is verified and bound (freeze finalization).** Most entries were written before the last edit of `features/synchrony.py`, so the frozen code recomputed them and compared bit for bit ([cache_consistency.json](evidence/validation/cache_consistency.json), produced by [cache_consistency.py](evidence/validation/cache_consistency.py)): all CorrCA units, all 500 regime-A splits of PAS-core, a random sample of the cached nested-CV plans, and samples for every other regime-A set. All were identical. Every entry present at the freeze is bound append-only (IS-029). Deleting the cache after the freeze therefore blocks outcome access; a fully cold run would require deleting it before the freeze is rebuilt.

## What V1/V2 do not establish

- **Simulated performance is not a guarantee.** The operating characteristics are properties of the design under the simulated (V1) or synthetic-outcome (V2) mechanisms. They do not guarantee calibration under every real dependence structure.
- **Planted signals are not real effects.** The planted-signal power is a sanity check, not a power claim for real effects.
- **Interval coverage is conditional.** Nested-CV coverage concerns the dataset-conditional procedure target (M04), not oracle information.
