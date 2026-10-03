# Conditional primary problem: individual validity of physiological learning measures

2026-10-03. **Decision:** advance G01 to the next validation/design stage. This selects a scientific question, not a model, a confirmed novelty claim or permission to ignore OQ-06. See [decision record](decision_log.md) and [pre-model gates](pre_model_gates.md).

Working paper framing: **When do shared physiological responses provide valid individual information about learning performance?**

“Learning performance” must be operationalized throughout as **immediate video-specific quiz performance**. BBBD cannot establish retained knowledge, gain from baseline, real-time comprehension or a causal educational benefit.

## Problem statement and importance

**L.** Prior studies associate synchrony and other EEG/eye measures with educational outcomes; multimodal synchrony, traits, heterogeneous gaze allocation and context-dependent relationships are already established research topics (P01–P04, L01–L09). Missingness correction, physiological distillation and shared/private representations also have substantial antecedents.

**I.** What remains worth testing is whether physiological observations add useful *individual criterion information* under conditions in which the measurement could actually be used. A group component might mostly identify the video, a participant's stable characteristics, a reference cohort or recording quality. Even a genuine within-study association may not transport to a new learner or new instructional material. Distinguishing these explanations has scientific value regardless of which model has the best average error.

**U.** This is the strongest remaining question in the present review, but not a verified untouched field. In particular, Chen 2026's full methods, John 2025's alternative gaze measures, and the exact BBBD antecedent evaluation designs must anchor any eventual novelty paragraph. The claim should be a specific new empirical/theoretical result, not “first multimodal learning prediction.”

**I. A hard relevance test:** administering a short quiz may be cheaper and more informative than acquiring physiology to predict that quiz. A near-end forecast alone therefore does not justify an educational application. The primary value of this study must be establishing whether widely interpreted physiological measures support individual-level scientific conclusions, and explaining a reproducible boundary or failure. Claims about adaptive teaching, replacing assessment or improving student outcomes require separate evidence. If all that remains is a small error reduction, reject the proposed elite-Q1 framing.

## Target, population and information contract

Let $i$ identify an experiment-qualified participant, $v$ a canonical video, and $e$ its protocol. $Y_{ive}$ is the audited immediate quiz score. $X^S_{ive}$ is the available whole-video information from sensor set $S$, $Q$ records measurement quality, $M$ records availability, and $C$ contains only covariates available before the forecast.

The forecast time is **after the relevant viewing, before seeing quiz responses**. This does not require a real-time algorithm. E5's forecast follows the final repeat; its first view must not receive the final quiz label as though it were an independently tested learning episode.

The provisional primary criterion is normalized **exact-set correctness**, chosen for its direct interpretation: all required choices and no incorrect choices. The supplied normalized partial score is a mandatory sensitivity endpoint. This preference is an **inference**, not a newly validated psychometric scale; the pre-model construct gate must fix it without selecting whichever score yields stronger physiological results. Do not model fractional partial credit as a count of independent Bernoulli successes.

The first-view scientific question uses E3 and the tested new-content block of E4, with experiment-stratified reporting; its tri-modal ceiling is **57 qualified people / 216 observations / 8 videos**. This is not a homogeneous protocol. E5 adds a distinct repeated-exposure test, bringing the wider direct-QC ceiling to **94 / 324 / 8**. E3–5's **120 / 446** outcome-observed population supports separate availability-policy analyses. E1 is an ocular-only supplementary cohort with its own chronology. E2 contributes no behavioral target.

No demographic, GPA, trait or feedback variable is automatically admissible. Verify chronology, meaning and missingness first. There is no common validated pre-knowledge score in eligible E3–5; therefore “beyond prior knowledge” is unavailable as a BBBD claim. Protect participant privacy; no participant-level research data need appear in the paper or this dossier.

## Estimand: incremental predictive utility under a declared setting

For an access/population setting $g$, define held-out risk

$$
R_g(f)=\mathbb{E}_g[(Y-f)^2], \qquad
\Delta_{S,g}=R_g(f_{C,Q,M})-R_g(f_{C,Q,M,X^S}).
$$

Positive $\Delta$ means improvement over the stated baseline on **the same held-out people/observations, target definition and information budget**. It is not causal sensor value, mutual information, mediation or proof of physiological synergy. A single fusion-versus-unimodal difference cannot identify a redundant/unique/synergistic information decomposition.

Use a prespecified, educationally interpretable minimum useful reduction $\delta$, expressed on the actual score scale with a companion absolute-error interpretation. Select it before predictive fitting, informed by item/score resolution and the intended measurement use. No defensible numerical $\delta$ or power claim is available yet.

Report three nested baseline comparisons: permissible $C$; $C$ plus $Q,M$; and each sensor addition on matched data. Adjusting for quality can remove meaningful looking-away behavior as well as artifacts. Consequently these comparisons answer different questions; the adjusted result is not automatically a “pure neural effect.” Stable person factors and moment-to-moment learning are also different targets.

If participant/video contributions are studied descriptively, label those models explanatory. A new-person predictor cannot use a fitted intercept for that unseen person. Demeaning all held-out visits using future observations silently introduces calibration information. Within-content learner contrasts can reduce common video effects but cannot remove unknown prior knowledge or certify causality.

## Three access settings, not one ambiguous generalization score

| Setting | Permitted information | Baseline/reference implication | Supported conclusion |
|---|---|---|---|
| A: new person, previously observed video | Training people and their recordings/labels on that content; no held-out labels | Video effects and training-only same-video ISC reference are available | Individual usefulness for an already characterized content library |
| B: new person, new video, no peer reference | New person's signal and prespecified content metadata; no target-content cohort used in fitting | Training-only general baseline; no test-derived difficulty or ordinary same-video peer ISC | Reference-free content transfer within the limited sampled content |
| C: new video with an unlabeled reference cohort | Separate target-content reference recordings, explicitly budgeted; no quiz labels and no evaluated person in the reference | Reference-assisted synchrony/features permitted; fit/adaptation must be declared | Usefulness conditional on collecting a calibration cohort |

For B, hold out both people and canonical videos from all training, tuning, representation fitting and self-supervision. Merely holding out a person–video cell while retaining that person's other responses is not new-person transfer. For C, reference participants cannot also be the reported evaluation population; group their repeated views together. Unknown test attention or quiz responses cannot determine reference membership.

A and B answer different scientific questions. Comparing them reveals access dependence but does not isolate a causal effect of reference information because the generalization target also changes. Where feasible, compare B and C on matched new content/test people with declared reference budgets.

Eight unique eligible videos—and only six in E3—permit bounded leave-content-out checks, not a claim of universal educational-content generalization. Experiment/content overlap is sparse; E4/E5 share three tested videos and E3 shares only one with that set. A video random-effects variance estimated here can be unstable.

## Precise research questions and competing hypotheses

**RQ1.** For new learners viewing known content, does adding EEG/ECG/eye yield a meaningfully positive $\Delta_{S,A}$ beyond permissible covariates and quality/availability?

**H1.** At least one prespecified sensor set produces $\Delta_{S,A}>\delta$ with adequate uncertainty and sensitivity support. The sensor comparison family must be limited before fitting, not selected among arbitrary combinations until significant.

**RQ2.** Does this individual utility survive new content without peer references, and how much does declared reference access change it?

**H2.** A representation containing individual behavioral information retains useful $\Delta_{S,B}$; a response dominated by common content/reference structure will lose much of its utility. Both are plausible. Success in C alone supports a reference-assisted measure, not a universal personal sensor.

**RQ3.** Is the inference stable under outcome semantics and actual measurement selection?

**H3.** The substantive conclusion persists across prespecified exact/partial scoring and justified quality policies, and is not matched by quality/availability alone. If only complete cases benefit, report a restricted-population result rather than a generally valid measure.

**RQ4 (secondary).** On E4/E5's shared content, does incremental utility transport across their exposure-protocol bundles?

**H4.** Utility may change with repetition/preview/incentive context. This is a bundled transport hypothesis; the data cannot attribute a change to reward, attention or repetition alone.

Competing explanations are recorded explicitly: common stimulus/difficulty; stable learner characteristics including unmeasured prior knowledge; quality/availability selection; scoring definition; reference-cohort access; or genuine portable criterion information. An EEG increment cannot by itself adjudicate among all biological explanations.

## Experimental story and possible methodological contribution

1. **Establish a measurement contract.** Lock score, forecast time, eligible observations, quality policies and allowed reference access. Verify an adequate provenance route before physiological feature fitting.
2. **Test simple incremental validity.** Compare permissible covariates, quality-only models, each modality and regularized fusion on identical cases. Report participant-balanced and exposure-weighted risk as separate summaries so a participant with six videos does not silently count twice as much as one with three.
3. **Challenge common explanations.** Include training-only content effects, matched quality/availability baselines, score sensitivity, appropriate trait covariates, and existing synchrony/heterogeneous-gaze methods in their valid access settings.
4. **Test transport.** Use grouped people/content partitions, then the E4/E5 protocol contrast. Present content-specific estimates and failures instead of only a pooled mean.
5. **Introduce a method only if a documented failure warrants it.** A candidate is a low-complexity objective emphasizing within-content learner outcome contrasts while retaining shared physiological structure only when it improves held-out behavior. Another is a conservative sensor contribution estimated against a nuisance baseline. Neither is new by assertion: compare with existing shared/private objectives, ordinary supervised models and teacher-utility methods before claiming innovation.
6. **Confirm the key finding independently.** Freeze the scientific claim and evaluation before analyzing a new educational cohort. Choose external data to test the identified boundary, not merely to add another leaderboard.

A credible contribution could be a demonstrated distinction between shared-response reproducibility and individualized criterion validity, plus a training/evaluation principle that fixes a reproducible failure. If standard regularized models answer the question well, do not force a new network. If no useful signal is detectable with informative precision, a carefully replicated boundary result may be more significant than a small accuracy gain.

## Validation, uncertainty and failure criteria

All feature selection, scaling, learned filtering, imputation, CorrCA/PCA, self-supervision, teacher generation and tuning must respect the outer information contract. Split-aware fitting cannot undo unidentified upstream operations; OQ-06 stays a separate gate.

Person and content are crossed sources of dependence. Aggregate evaluation by person and show per-video effects; assess small-cluster limitations explicitly. Do not treat CV folds, windows or repeated quiz labels as independent replicates, or assume a naive bootstrap fixes eight content clusters. Decide an appropriate inferential strategy after the precision simulation and target population are fixed.

Label/teacher controls must preserve the structure relevant to their null. Shuffling learner associations within videos or assigning matched-quality alternative teachers can diagnose shortcuts, but exchangeability conditional on traits/protocol is not automatic. Treat such controls as diagnostics unless a valid randomization null is established. Compare pretraining with matched random initialization and track checkpoint training-corpus overlap before using any foundation model.

Report all prespecified sensor and score comparisons, uncertainty, calibration diagnostics where supportable, quality-stratum coverage and failed content/protocol transfers. No guaranteed conformal coverage under arbitrary crossed dependence or domain shift is claimed.

The idea is weakened or rejected if useful improvement is ruled out, if a nonsignal/reference shortcut explains the effect, or if independent replication contradicts it. An imprecise zero is inconclusive. A positive average with unstable content effects supports a narrower measure, not the broad hypothesis. If the required novelty or precision cannot be established, stop the proposed paper before expensive model work and select a different dataset/design.

## Publication scope and external validation decision

The hardest reviewer objections remain live: prior work may already answer the exact validity question; unmeasured prior knowledge may prevent the intended interpretation; the first-view sample may be too small to distinguish useful effects; and an existing regularized model may expose the same boundary without any new training method. The responses are a precise closest-paper comparison, restricted criterion claims, a pre-model precision analysis and independent replication—not a larger architecture. If these do not produce a substantive scientific advance, reformulate rather than presenting routine evaluation practice as a new methodology.

**I. BBBD alone is adequate for a bounded exploratory validity study after gates; it is not a convincing sole basis for the intended broad elite-Q1 claim.** Its many windows do not compensate for few independent learners/content, and the release has already informed hypothesis development.

Plan later external educational validation now. John 2025 provides a promising open-data link and a direct competing gaze measure, but access, files, sensor/outcome coverage and licensing remain unverified. One instructional video would test cross-cohort validity, not broad content transport. A new study with more independent content, documented sensor calibration and pre/post knowledge would answer stronger questions. Other physiological domains can validate a method component but cannot confirm educational criterion validity. Details and go/no-go conditions are in [pre-model gates](pre_model_gates.md).
