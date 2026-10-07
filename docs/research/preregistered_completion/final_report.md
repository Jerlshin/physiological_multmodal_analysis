# G01-R preregistered phase — integrated final report

2026-10-07. This report closes the preregistered G01-R phase. All 17 registry analyses are complete:

- 15 executed: H1_H2, H3.1–H3.6, D_BC, D_CAS, D_E5, D_transport, D_E1, X_explanatory, S_identity_probe;
- 2 derived from H1_H2: H3.7 and the state interval.

Every analysis ran exactly as frozen in `g01r-freeze-v1` under the [OSF preregistration](https://osf.io/uh397/overview). Sources:

- [H1/H2 results](../confirmatory_h1h2/h1h2_results.md) (step 1, unchanged);
- [steps 2–5 per-analysis records](results_steps2_5.md);
- [phase record and provenance](README.md).

**Rules applied throughout:**

- No specification was changed after outcome access, and no post hoc analysis was run.
- Confirmatory claims rest only on H1 and the H2 Holm family.
- Everything else is robustness (H3, IS-028 reading), descriptive, explanatory or diagnostic, and is labelled as such.
- Where a question cannot be answered by a prespecified analysis, this report says so instead of filling the gap.

Notation: Ŝ = person-balanced held-out skill over the stated base; δ = 0.05; 2δ = 0.10.

## Evidence classes used in this report

| Class | Analyses | What it can support |
|---|---|---|
| Confirmatory | H1 (one-sided α = 0.05); H2a–d (Holm, FWER 0.05) | Detection / non-detection; H1's bounded-negative category |
| Robustness (H3) | H3.1–H3.7 | Whether H1's estimate keeps its sign and side of δ; no test |
| Prespecified estimates | Regime-A model ladder, per-experiment, per-video | Sizes; no inference beyond H1's interval |
| Descriptive | B/C, CAS, E5, transport, E1 | Direction and size with conditional or approximate intervals; no p-values |
| Explanatory | Crossed REML | In-sample associations; never predictive evidence |
| Diagnostic | Shortcuts (i)–(iii) | Whether nonsignal or identity information could drive results |

---

## 1. Final scientific status of H1

**H1 (primary, confirmatory): not detected. Final category: bounded negative.**

- Ŝ(M5 vs M2) = 0.021, nested-CV 90% interval [−0.033, 0.072], permutation p = 0.082.
- U₃ = 0.079 < 0.10.
- At n = 68 learners and 8 videos, whole-video EEG + ECG + gaze with the frozen ridge procedure adds no detectable held-out information over content, covariates and quality.
- Increments ≥ 0.10 are ruled out (≈ 5% error). Increments of 0.05–0.10 are not ruled out. This is not evidence that physiology carries no information.

**Robustness (H3, IS-028): all eight robust.** Every prespecified H3 estimate keeps the positive sign and stays below δ:

| Analysis | Ŝ | 90% interval |
|---|---|---|
| H3.1 partial credit | 0.019 | [−0.041, 0.079] |
| H3.2 eye QC 0.30 | 0.009 | [−0.021, 0.038] |
| H3.2 eye QC 0.70 | 0.017 | [−0.032, 0.058] |
| H3.3 four-sensor set | 0.019 | [−0.029, 0.072] |
| H3.4 raw-export route | 0.021 | [−0.040, 0.076] |
| H3.5 without the low-α video | 0.016 | [−0.038, 0.063] |
| H3.6 GPA added | 0.015 | [−0.035, 0.061] |
| H3.7 cell-weighted | 0.013 | [−0.045, 0.068] |

- The full-model estimate ranges from 0.009 to 0.021, and no interval's upper limit exceeds 0.08.
- H3 carries no test, so H1's decision category is neither strengthened nor weakened. The estimate is simply stable.

**Descriptive context:**

- The full model is not better than the baseline in any other regime or cohort that contains EEG and ECG: B −0.025, C 0.020, CAS −0.00002, E5 −0.023, transport E4→E5 −0.143 and E5→E4 0.018.
- None reaches δ.

**Final statement.** In BBBD v1.1, the prespecified multimodal physiological model provides **no useful (≥ δ) and no detectable incremental individual information** about immediate quiz performance. Moderate or large increments (≥ 0.10) are ruled out for this procedure. The small positive point estimate is robust across all prespecified sensitivity analyses.

## 2. Final status of each H2 component

| | Confirmatory result (step 1) | What the later prespecified analyses add | Final status |
|---|---|---|---|
| **H2a — synchrony beyond reference-free features** (M5 vs M3) | **Rejected H0**, Holm p = 0.020; Ŝ = 0.047 (< δ) | **Regime C:** with an unlabelled half-cohort reference on a held-out video, SYN improves on RF-only in **8 of 8 videos** (B − C −0.006 to −0.066; pooled C − B ≈ 0.045). **Transport:** with source-cohort references from a different protocol, the full model is worse (E4→E5 −0.143). **Explanatory:** gaze ISC +0.031 SD⁻¹ (p 0.065), EEG ISC +0.028 (p 0.15) | **Confirmed, small (< δ), reference-dependent.** Descriptively reproduced on new content with an unlabelled same-protocol reference; not carried across protocols |
| **H2b — EEG block** (M-EEG vs M2) | Not rejected; Ŝ = −0.004, Holm p = 0.456 | **Raw route (H3.4):** the full model is unchanged (0.021), so no EEG-route-dependent increment is hidden. **Explanatory:** alpha +0.017 (p 0.25), theta ≈ 0, EEG ISC +0.028 (p 0.15). BII-005: EEG ISC is partly ocular | **Not supported.** No prespecified analysis indicates an EEG contribution |
| **H2c — ECG block** (M-ECG vs M2) | Not rejected; Ŝ = −0.011, Holm p = 0.811 | **Explanatory:** HR, RMSSD and HR ISC all negative or ≈ 0 (p ≥ 0.44) | **Not supported.** No prespecified analysis indicates an ECG contribution |
| **H2d — gaze block** (M-gaze vs M2) | **Rejected H0**, Holm p = 0.027; Ŝ = 0.031 (< δ) | **E1 (descriptive, ocular-only):** 0.261 [−0.104, 0.584], positive in 5 of 5 videos, but 26 people, near-unpenalized fits in about 5% of splits, and the substrate of prior published gaze-ISC work. **PAS-four:** the pupil block adds about 0.013 (same direction). **Explanatory:** the ocular association sits on gaze ISC, not dispersion or saccade rate. **No prespecified analysis re-estimates M-gaze under other eye-QC thresholds, routes or regimes** | **Confirmed, small (< δ), in regime A.** Its robustness to eye-quality policy is **untested by design** (see §5) |

The Holm family stands as tested. Nothing in steps 2–5 is a test, so no H2 decision changes.

## 3. Which findings survive the robustness checks?

| Finding | Reference access | Eye-quality threshold | Raw vs processed | Identity / content shortcut | Quality confounding | Content variation | Verdict |
|---|---|---|---|---|---|---|---|
| **H1 estimate small, positive, < δ; ≥ 0.10 ruled out** | Same in A; C 0.020; B and transport ≤ 0 | Robust (0.009 / 0.017) | Robust (0.021) | Shortcut excluded by design (content offsets; residualized test) | Net of Q by design; estimate halves at the strictest eye QC | 5 of 9 units positive; robust without the low-α video (0.016) | **Survives** as a bounded negative with a stable sub-δ estimate |
| **H2a synchrony > RF** | A (training references) and C (unlabelled half-cohort references, new videos, 8 of 8): yes. Cross-protocol references: not supported | Not re-estimated (no prespecified analysis) | Not re-estimated for H2a; the M5 route is invariant | Excluded by design; features carry strong content identity (probe 0.50 vs 0.15) but tests and B/C metrics are within-content | Net of Q; not re-estimated at other QC thresholds | 8 of 9 units in A, 8 of 8 videos in B−C | **Survives within the same protocol, including on new content. Reference-dependent** |
| **H2d gaze block** | A only (no other regime isolates gaze) | **Not re-estimated** | Gaze features are route-invariant (ρ ≥ 0.999), so trivially robust | As H2a | Partly entangled (§5) | 8 of 9 units in A | **Confirmed in A; robustness to quality policy untested** |
| **RF block hurts** | A −0.028; B −0.025 [−0.049, −0.006] | — | — | — | — | B negative in 8 of 8 videos | **Robust negative**: reference-free whole-video features behave like added noise |
| **No EEG/ECG increment** | — | — | Raw route does not change M5 | — | — | — | **Robust** in every prespecified view |

## 4. Which findings are reference-dependent?

**All positive physiological signal in this study is reference-dependent.**

- **The reference-free block (RF) never helps.**
  - Regime A: −0.028, as bad as nine noise columns (−0.021).
  - Regime B (new content): −0.025, with the conditional interval below 0.
- **Synchrony is the only component that adds information.** It needs a same-video, same-protocol peer reference:
  - training learners (regime A; H2a confirmatory);
  - an unlabelled half-cohort viewing the new video (regime C; descriptive, 8 of 8 videos).
- **When the reference and the model come from a different protocol, the model does not transfer.**
  - E4 → E5 skill −0.143, with the loss-difference interval below 0.
  - E5 → E4 is +0.018, with the interval containing 0.
  - Transport changes offsets, RF and references at once, so it cannot attribute the failure to the reference alone.
- **Even with a reference, the synchrony-containing model's skill over the nonsignal baseline is below δ:**
  - A: M5 0.021; M4 (SYN only, no test) 0.039;
  - C: 0.020, interval upper limit 0.045.

The pre-declared phrase "reference-dependent *validity*" presupposes a positive H1 and is therefore not used. The correct description is a **reference-dependent, sub-δ synchrony increment over reference-free features**.

## 5. Which findings appear quality-dependent?

| Observation | Source | Class |
|---|---|---|
| Quality variables alone predict the score (M0+Q vs M0 0.069; E3 0.111, E4 0.038), and Q adds 0.052 on top of covariates | Shortcut (i); model ladder | Diagnostic / estimate |
| The full-model increment halves under the strictest eye-quality policy (0.009 at ≤ 0.30, vs 0.021 at ≤ 0.50) and does not grow when the policy is relaxed (0.017 at ≤ 0.70) | H3.2 | Robustness |
| The largest in-sample association with the score is a quality variable (pupil correction fraction, −0.041 per SD, Wald p 0.021, unadjusted); gaze correction is +0.022 (p 0.14) | X_explanatory | Explanatory |
| Every PAS-core-based run clips predictions at 0 only for the pre-identified learner with the extreme EEG 16 Hz excess (7–8 dB). This affects base and full models alike | All A runs | Diagnostic |
| The available-sensor policy gains nothing (−0.00002) once incomplete-quality cells are included | D_CAS | Descriptive |

**Reading.**

- H1 and H2 are net of Q by construction, so no confirmatory result is a pure quality artefact.
- The direction of H3.2 (the increment shrinks in the cleaner-eye subset) shows that **part of the small full-model increment co-varies with eye-recording quality**.
- The protocol could not separate looking away from tracker failure (estimand §5), and the prespecified analyses cannot decide which one drives this.

## 6. Does gaze carry robust criterion information, or mainly measurement/behaviour-quality information?

**The prespecified analyses cannot settle this. The evidence leans towards "small, attention-related ocular behaviour, partly overlapping with eye-data quality". It does not support "robust criterion information".**

**For criterion information:**

- **H2d is confirmatory and net of gaze correction fraction and gaze missingness.** These are the variables most directly indexing looking away and tracker loss.
- **The in-sample ocular association sits on gaze ISC** (stimulus-locked synchrony with peers), not on dispersion or saccade rate.
- **Synchrony helps on every held-out video in regime C** (gaze ISC is one of its three components).
- **E1's ocular-only model is positive in all 5 videos.**

**For quality/behaviour entanglement and against robustness:**

- **The increment's size depends on the eye-quality policy.** The full model at the strictest threshold (0.009) is less than half the primary.
- **Quality variables predict scores more strongly than any physiological block.** Q alone is 0.069, against 0.031 for gaze.
- **Gaze ISC is a behavioural measure computed only on valid samples, and validity itself is behaviour.** Attending away lowers both.
- **The E1 estimate is not independent evidence.** It is imprecise (interval −0.10 to 0.58), shows numerical warnings, and its recordings are the substrate of the original authors' gaze-ISC findings.
- **H3.2 re-estimates M5, not M-gaze.** No prespecified analysis tests the gaze block's robustness to quality policy.

**What can be claimed:** a confirmed, sub-δ held-out increment from the gaze block in regime A, net of the prespecified quality variables. **What cannot be claimed:** that it reflects learner criterion information independent of attention-related looking behaviour or eye-data quality.

## 7. Does synchrony carry robust criterion information, and under what reference conditions?

**Yes, in a narrow sense:** synchrony carries held-out information beyond reference-free physiology.

- **Training-learner references (regime A):** confirmatory, H2a Holm p = 0.020, Ŝ 0.047.
- **Unlabelled half-cohort same-protocol references on new content (regime C):** descriptive. It improves on RF-only in 8 of 8 videos, with a pooled gap ≈ 0.045.

Its limits:

| Limit | Evidence |
|---|---|
| Not a useful predictor over the nonsignal baseline | A 0.021 (full model); C 0.020 [−0.014, 0.045] |
| Not shown across protocols | Transport E4→E5 negative; E5 repeat viewing −0.023 |
| Not attributable to non-ocular physiology | The SYN block mixes EEG, ECG and gaze ISC; EEG ISC correlates with gaze dispersion (BII-005, ρ = 0.48); the explanatory weights fall on gaze ISC and EEG ISC, not HR ISC |
| Not video-specific (state) information | State skill −0.010 [−0.056, 0.035]; what synchrony identifies is mainly which learners score higher overall |

## 8. Is there any credible incremental contribution from EEG or ECG?

**No.** No prespecified analysis gives credible support:

- H2b and H2c are not rejected, with negative point estimates (−0.004, −0.011).
- The full model does not change when EEG comes from the raw exports (H3.4).
- No EEG or ECG coefficient reaches nominal significance even in the unadjusted explanatory model.
- The modality analyses are not bounded (H2 carries no futility bound), so this is absence of evidence of a contribution at this sample size, not a bound on its size.
- Any EEG synchrony contribution would in any case read as "EEG-recorded synchrony", which is partly ocular (BII-005).

## 9. How much of the predictive signal is nonsignal or quality information?

These are exact ratios of prespecified person-balanced MSEs on identical cells and folds (step 1): MSE M0 0.03464 → M1 0.03341 → M2 0.03168 → M5 0.03103. M5 reduces held-out MSE by **10.4%** relative to the content-only floor M0.

| Added in the preregistered order | Share of the 10.4% |
|---|---|
| Covariates C (age, sex, ASRS, digit span) | 34% |
| Quality Q | 48% |
| Physiology (RF + SYN) | **18%** |

- About **82% of the held-out signal beyond content is nonsignal**, and quality alone carries about half of it. The shares depend on the order of addition; this is the preregistered nesting.
- Quality alone (0.069) is about 3.4× the physiological increment (0.021).
- Part of that 18% also co-varies with eye quality (§5).
- In the coverage setting, physiology adds nothing (CAS −0.00002).

## 10. What can and cannot be claimed about new-content generalization?

**Can be claimed** (descriptive; conditional on these 8 videos; approximate intervals that undercover the content population):

- For a new video and new learners, the reference-free physiological model is **worse** than the nonsignal baseline: within-content −0.025 [−0.049, −0.006], negative in all 8 videos.
- Adding synchrony against an unlabelled half-cohort reference on the new video brings skill to 0.020 [−0.014, 0.045]. That is not distinguishable from 0, and the interval lies below δ.
- Synchrony improves on reference-free features on every held-out video.

**Cannot be claimed:**

- Generalization to the population of educational videos (8 videos; no content-population inference; no p-values by design).
- Any useful (≥ δ) new-content prediction.
- Generalization across learning protocols: E4 → E5 is negative, and E5's own regime A is −0.023, so instruction, test timing and repetition break transfer.
- "Content-library-specific validity" in the protocol's sense, which requires a positive regime-A result.

## 11. Strongest remaining limitations

1. **Criterion reliability and structure.**
   - About half of within-video score variance is item-sampling error (median α 0.45).
   - The reliable part is mostly stable-learner level: state skill ≈ 0, and the explanatory person variance is 26% versus residual 59%.
   - There is no pretest, so "identifies higher-scoring learners" cannot be separated from "identifies prior knowledge".
2. **Precision.** With 68 learners only ≥ 0.10 can be excluded. The interesting range (0.02–0.10) is unresolved, and the detected increments (0.031, 0.047) are exactly in the range this design cannot size.
3. **Quality/behaviour inseparability for ocular measures.** Looking away and tracker failure are not separable in the released data, quality predicts the score, and the gaze block's robustness to quality policy was not a prespecified analysis.
4. **Content and protocol sampling.** 8 videos and heterogeneous protocols (E3 intentional and immediate, E4 incidental and end-of-block, E5 incentivized repeat). B/C intervals are conditional; transport fails.
5. **Exploratory origin.** The whole release was audited before the design. Internal cross-validation is not an untouched confirmation. The E1 data underlie prior published gaze-synchrony results.
6. **Cohort identity.** E3 versus E4/E5 identity is uncertified; any overlap would bias regime A optimistically.
7. **Conditional estimand.** Complete cases are conditional on usable recordings, and complete cases scored higher.
8. **Provenance.** OQ-06 is bounded, not resolved. H3.4 shows the full-model estimate does not depend on the processed derivatives. Ocular features are route-invariant, so OQ-06 cannot be the source of the ocular findings.

## 12. The empirical bottleneck for the next phase

**The bottleneck is not modelling capacity. It is that BBBD cannot resolve whether a small (~0.03), reference-dependent ocular-synchrony increment is learner criterion information or attention/eye-quality behaviour.** Three features of the data cause this together:

- **(a) A noisy criterion** (12 items, α ≈ 0.45), with no pretest to separate prior knowledge.
- **(b) Too few learners** (68) to size effects below 2δ.
- **(c) Eye-data quality variables that are themselves predictive** and inseparable from looking-away behaviour.

Why more modelling of BBBD is not the lever:

- The reference-free features already perform at the level of matched noise.
- Every prespecified sensitivity analysis leaves the estimate in 0.009–0.021.
- Quality and covariates carry about four-fifths of the held-out signal.
- Flexible learners would mainly fit the content identity that the features already encode (probe accuracy 0.50).

The decisive next quantity is the ocular-synchrony increment **beyond a prior-knowledge baseline and beyond explicit attention/quality measures**, on a more reliable criterion and a larger sample. BBBD can supply none of these three.

## 13. Ranked recommendation for the next methodological direction (not implemented)

1. **Run the already time-stamped external ocular replication (John et al. 2025, OSF 4rn5q), as written in [external_analysis_plan_john2025.md](../experimental_design/external_analysis_plan_john2025.md).**
   - It tests the only surviving signal (gaze block / gaze ISC with training references) on an independent cohort.
   - It has about 117 people, a 13-item posttest and a **pretest-adjusted baseline (M2p)**, which addresses limitation 1.
   - Its plan predates these results. Any amendment prompted by them, such as an eye-QC sensitivity for the gaze block or an explicit attention/quality block, must be dated and declared as results-informed, and the original contrast kept as primary.
   - It needs the user's authorization to download about 4.1 GB.
   - Limits: one video, ocular only, transport labelled as such.
2. **A preregistered measurement-separation study of gaze synchrony versus eye-data quality and looking-away behaviour.**
   - First, outcome-blind on BBBD (and John): how gaze ISC relates to valid-sample fraction, correction fraction and off-screen time.
   - Then preregister a decomposition contrast (gaze ISC beyond an explicit attention/quality block) for the external cohort.
   - This targets limitation 3, the main interpretive gap for H2d.
   - Any outcome-linked version on BBBD would be exploratory and must be labelled so.
3. **Design, but do not yet collect, a prospective cohort powered for δ.**
   - Use these estimates (~0.02–0.05, reference-dependent) in a design simulation of the kind used here.
   - Design features: tens of content units, longer and more reliable item banks, pretest and delayed test, a single protocol, and gaze plus quality instrumentation able to separate looking away from tracker loss.
   - Tri-modal recording is optional: the evidence here gives no reason to prioritize EEG or ECG.
   - This is the only route to content-population inference and to tri-modal external confirmation.
4. **Deployable reference strategies for synchrony** (regime C-style unlabelled or normative reference banks). Regime C suggests same-protocol peer references on new content work; transport suggests cross-protocol references do not. This only becomes worthwhile if items 1–2 confirm that ocular synchrony carries criterion information beyond attention/quality.

**Not recommended on the present evidence:**

- New architectures, representation learning, deep multimodal fusion or foundation-model work on BBBD.
- EEG- or ECG-specific feature engineering on BBBD.
- Any re-analysis of BBBD that removes the extreme-quality learner, changes QC thresholds, or re-estimates the gaze or synchrony blocks under new specifications.

If such analyses are ever wanted, they belong to a new, separately preregistered exploratory protocol and must be reported as post hoc relative to G01-R.

**The preregistered G01-R phase is complete. No new method-development work has been started.**
