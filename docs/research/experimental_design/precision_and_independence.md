# M04 — Independence and attainable precision of the actual crossed design

2026-10-04. Scripts:

- [precision_simulation.py](evidence/precision_simulation.py) → [summary](evidence/precision_simulation_summary.csv), [replicates](evidence/simulation_replicates/), [meta](evidence/precision_simulation_meta.json);
- [inference_calibration.py](evidence/inference_calibration.py) → [cell-wise](evidence/inference_calibration_summary_cellperm.csv) and [person-block](evidence/inference_calibration_summary_personperm.csv) summaries.

**No real physiology–outcome association was used or computed.**

- **Outcome parameters** are outcome-only psychometrics.
- **Synthetic physiological nuisance structure** follows the audit's physiology-only variance fractions.
- **Signal strength** is a scenario parameter.

## Independence

| Unit | Count in PAS-core | Status |
|---|---|---|
| Learners | 68 (E3 29, E4 39) | E4 ∩ E5 = ∅ by construction (F). E3 versus E4/E5 identity uncertified: treated as distinct, matching the original authors' additive counts (L/U) |
| Content | 8 canonical videos (6 E3-only, 2 E4-only, 1 shared); 9 experiment × video cells | Content-population inference rests on 8 draws |
| Cells | 259 | Repeated measures within learners and within content. Never treated as independent |

Cross-experiment identity overlap, if present, would only affect regime A test people whose other-cohort data are in training. Any bias is optimistic and bounded by the unknown overlap. Experiment-stratified estimates are reported ([M06 §1](evaluation_contract.md#1-independence-units)).

## Simulation design

**Incidence.** Every synthetic dataset reproduces the **actual** cells of the analysis set from the [manifest](evidence/analysis_set_manifest.csv): the same learners, videos, experiment membership and missing cells.

**Outcome model** (per experiment, from [psychometrics](evidence/outcome_psychometrics.json)). Exact score = clip(round₁₂(μ_e + content_ev + person + person×video + item noise)). The variances are:

| Component | E3 | E4 | E5 | E1 |
|---|---|---|---|---|
| Content | 0.0008 | 0.0104 | 0.0110 | 0.0077 |
| Person | 0.0103 | 0.0153 | 0.0230 | 0.0308 |
| Person × video (reliable) | 0.0039 | 0.0053 | 0.0023 | 0.0030 |
| Item noise, (1 − α) × within-video variance | 0.0159 | 0.0151 | 0.0147 | 0.0159 |

**Covariates and quality.**

- Five traits; one carries 10% of the person variance.
- Three quality variables; one loads −0.25 on ability, mimicking the observed selection.

**Physiology.** p features: 9 for the PAS-core A full model (6 RF + 3 SYN), 11 for PAS-four, 6 for regime B (RF only), and 3 for E1.

- Each feature has 60% stable-person nuisance, 5% content nuisance and 35% residual. These follow the audit's between-person fractions of about 0.6–0.95 and between-video fractions below 0.06.
- Three features also carry a latent information signal g.
- g mixes the trait-unexplained person component and the reliable person × video component, in proportion to their variances ("proportional"). "Person-only" and "state-only" variants are also run.

**Effect scale.**

- **Oracle skill S\*** is the population linear incremental skill, calibrated by bisection on 20,000 synthetic people.
- **Procedure truth** is what the frozen pipeline achieves when trained on the study's n and evaluated on 1,500 fresh learners with the same content (A) or on fresh content (B). This is the estimand.

**Pipeline.** Exactly the frozen [M06](evaluation_contract.md) pipeline:

- ridge with inner person-grouped penalty selection;
- A: person-grouped 10-fold, experiment-stratified, repeated;
- B: leave-one-video-out × person 5-fold.

**Inference compared.**

| Method | What it does |
|---|---|
| Person bootstrap | Bootstrap of out-of-fold person losses, with the fitted models held fixed |
| Corrected resampled t | Nadeau–Bengio, on fold-level differences |
| Nested CV | Bates et al. 2024, Algorithm 1 with the eq. 15 bias correction and MSE clipping; 20 nested repetitions in the main run |
| Permutation test | Freedman–Lane-style: residualized physiology permuted within experiment × video, with paired folds (targeted calibration) |
| B: person bootstrap and two-way (person × video) bootstrap | — |

**Replicates.** 400 per main scenario and 300 per calibration scenario.

## Results — main simulation (400 replicates per scenario)

### Regime A, PAS-core (68 / 259 / 8), exact score

| Oracle S\* | Expected procedure skill (truth) | Mean estimate | SD of estimate | Power, bootstrap / corrected t / nested CV | P(upper 90% bound < δ), corrected t / nested CV | 90% coverage of the expected truth, bootstrap / corrected t / nested CV |
|---:|---:|---:|---:|---|---|---|
| 0 | −0.008 | −0.010 | 0.021 | 0.035 / 0.008 / 0.015 (type-I) | 0.885 / 0.725 | 0.77 / 0.95 / 0.91 |
| 0.05 | 0.024 | 0.021 | 0.033 | 0.25 / 0.14 / 0.10 | 0.40 / 0.29 | 0.67 / 0.86 / 0.86 |
| 0.10 | 0.065 | 0.066 | 0.048 | 0.61 / 0.45 / 0.36 | 0.11 / 0.08 | 0.71 / 0.79 / 0.82 |
| 0.15 | 0.113 | 0.114 | 0.058 | 0.87 / 0.78 / 0.67 | 0.03 / 0.01 | 0.74 / 0.78 / 0.82 |
| 0.20 | 0.168 | 0.158 | 0.060 | 0.98 / 0.94 / 0.83 | ≈0 | 0.76 / 0.81 / 0.83 |
| 0.30 | 0.278 | 0.271 | 0.066 | 1.00 / 1.00 / 0.98 | 0 | 0.79 / 0.84 / 0.88 |

Findings (F for the simulation; I for interpretation):

1. **The estimator is essentially unbiased for the procedure-level estimand.** The procedure's achievable skill lies about 0.02–0.04 below oracle information at n = 68, which is the estimation loss.
2. **The sampling SD of the skill estimate is 0.02–0.07.** Absolute precision is modest even with a perfectly calibrated interval.
3. **Every interval method undercovers once signal is present, and the misses are one-sided.** At truth 0.065, 17% (corrected t) and 14% (nested CV) of upper bounds fall below the truth. Ridge shrinkage makes the spread smaller precisely when the realized estimate is small.
   - The person bootstrap is worst (0.67–0.79).
   - Nested CV covers the dataset-conditional target best: **0.86–0.90 in every scenario** ([summary](evidence/precision_simulation_summary.csv), `cover90_cond_ncv`).
4. **All methods control false detection under the null** (≤ 0.035 here; ≤ 0.058 across all sets). The bootstrap is the most powerful but is badly calibrated as an interval.

### Other sets and regimes (detection power with the bootstrap / corrected t)

| Set / regime | Truth at which power ≈ 0.8 | Under the null: P(upper < δ), corrected t | Verdict |
|---|---|---|---|
| PAS-four (57 / 216) | ≈ 0.13 (bootstrap); ≈ 0.15 (corrected t) | 0.75 | Less precise than PAS-core: supports keeping pupil as a secondary block (EDD-003) |
| E5-core (46 / 128 / 3) | > 0.2 (power 0.57 / 0.44 at truth 0.125) | 0.47 | Descriptive only |
| E1-gaze (26 / 121 / 5) | > 0.24 (power 0.77 / 0.59 at truth 0.236) | 0.29 | Descriptive only |
| B, PAS-core (within-content skill) | Two-way bootstrap power 0.69 at truth 0.12. Coverage of the **content-population** truth: person bootstrap 0.60–0.79; two-way 0.77–0.92. Per-video skill SD 0.03–0.11 | Two-way 0.91 | Descriptive and conditional on the 8 videos. **No content-population inference** (consistent with Westfall et al. 2014; Cameron et al. 2008) |

### State versus person information (PAS-core, state skill = double-centred within-person metric)

| Information type at S\* = 0.10 | Overall skill (truth) | State skill, mean (SD) |
|---|---:|---|
| Proportional (tracks the true score) | 0.065 | 0.024 (0.024) |
| Person-only | 0.070 | −0.018 (0.020) |
| State-only | 0.072 | **0.122 (0.045)** |

The state metric can distinguish *concentrated* video-specific information from person-level information. Under realistic proportional mixing it cannot resolve the small state share. It therefore stays **exploratory**, as declared in [M02](estimand_and_hypotheses.md).

## Results — targeted calibration of the H1 decision procedures (300 replicates per point)

These are the operating points that matter for the pre-declared rules, on PAS-core with the expected procedure skill set to about 0, δ and 2δ:

- [cell-wise permutation summary](evidence/inference_calibration_summary_cellperm.csv);
- [person-block permutation summary](evidence/inference_calibration_summary_personperm.csv);
- replicates in `evidence/simulation_replicates/calibration_*`.

| Procedure | Null (truth −0.009): false detection | Truth ≈ δ (0.054): detection | Truth ≈ 2δ (0.106–0.108): detection |
|---|---:|---:|---:|
| Person bootstrap, lower 90% bound > 0 | 0.053 | 0.46 | 0.81–0.82 |
| Corrected resampled t | 0.003 | 0.30 | 0.70–0.72 |
| Permutation, **cell-wise** within content (Freedman–Lane) | **0.080: invalid** | 0.79 | 0.97 |
| **Permutation, person-block** within experiment × identical video pattern (Freedman–Lane) | **0.063** (Monte Carlo 95% range for a true 0.05 at 300 replicates: about 0.025–0.075) | — | **0.93** |

**Why the cell-wise test fails (I).** It scatters each learner's person-coherent physiology across learners. The permuted features then overfit differently from the real ones, so the null distribution is too narrow.

**Why the person-block test works (I).** It exchanges whole learners: 57 of 68 learners sit in exchangeable same-pattern groups, and the other 11 stay fixed, which can only make the test conservative.

### Futility: ruling out an effect

Futility uses the corrected-t upper bound, centre + z·SE, divided by the baseline MSE, compared with a threshold:

| Threshold | z | P(rule out \| null) | P(rule out \| truth ≈ threshold) |
|---|---:|---:|---:|
| δ = 0.05 | 1.645 | 0.86 | **0.17** (miscalibrated) |
| δ = 0.05 | 2.58 | **0.60** | 0.053 |
| 2δ = 0.10 | 2.58 | 0.95 | 0.060 |
| **2δ = 0.10** | **3.0** | **0.91** | **0.043** (truth 0.106) |

**Ruling out δ = 0.05 cannot be done with controlled error at this sample size. Ruling out 2δ = 0.10 can.**

## Pre-declared rule 3 applied (phase plan)

| Regime / set | (a) false detection ≤ 0.07 | (b) power ≥ 0.80 at 2δ | (c) P(rule out δ \| null) ≥ 0.80 with controlled error | Consequence |
|---|---|---|---|---|
| **A, PAS-core** | ✓ person-block permutation 0.063 | ✓ 0.93 | **✗ at δ** (0.60); ✓ at 2δ (0.91, error 0.043) | **Confirmatory for detection. Negative conclusions narrowed to "effects ≥ 0.10 ruled out"** (EDD-014) |
| A, PAS-four | ✓ | ✗ (bootstrap 0.69, corrected t 0.59 at truth 0.10) | ✗ | Secondary (pupil block) |
| A, E5-core | ✓ | ✗ | ✗ | Descriptive |
| A, E1-gaze | ✓ | ✗ | ✗ | Descriptive |
| B, C | Coverage of the content population fails (≤ 0.92 two-way, ≤ 0.79 person) | — | — | Descriptive, conditional on the 8 videos |

## What the actual design can and cannot distinguish (I)

- **It can detect.** A true procedure-level skill of about 0.10 or more (oracle ≈ 0.14), for new learners on known content, is detected with power ≥ 0.9. False detection is about 5%.
- **It can rule out.** Skill ≥ 0.10 is ruled out with about 91% probability when physiology carries nothing, with about 5% error at the boundary.
- **It cannot resolve** skills between 0 and 0.10, including the useful range 0.05–0.10, as either present or absent. Such outcomes are reported as **inconclusive**, never as absence.
- **It cannot support** content-population claims (B), protocol-specific confirmations (E5) or ocular-only confirmations (E1). Those are descriptive.
- **Interval reporting.** Nested-CV 90% intervals cover the dataset-conditional target at 0.86–0.90. They are the reported intervals, labelled with this simulated coverage.

Inferential chain: the expected procedure skill sits about 0.02–0.04 below oracle information at n = 68. The prior in-sample BBBD associations imply cell-level oracle skills of very roughly 0.1–0.15 (P01/P03/P04; I, a rough translation, not a replication). On that basis, the study is adequately sized to detect effects of the magnitude the literature implies, and to contradict them if they are absent. It is not sized to establish small useful effects.

**Limits of the simulation (U).** It assumes Gaussian latent structure, linear information, the specified nuisance fractions and independent covariates. Real features may be heavier-tailed, collinear with covariates or nonlinearly related to outcomes. Simulated operating characteristics are design evidence, not guarantees.
