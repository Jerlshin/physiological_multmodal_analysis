# Novel-method phase — post-preregistration method development (planning)

Opened 2026-10-08 on the user's instruction to develop a novel, high-performing and scientifically defensible method for BBBD, motivated by the evidence from G01-R and the John 2025 replication. **Status: RESEARCH AND ARCHITECTURE PLAN COMPLETE AND REVIEWED. No training campaign started.**

**Closure phase — 2026-10-14 to 2026-10-15: [closure/](closure/README.md).** Status: **CLOSURE COMPLETE; stopped at the human / authorization boundary.** No outcome of any cohort was read; every simulated outcome is synthetic.

- **Temporal control.** A cubic within-recording detrend is the primary form (rule R-F). The linear form fails under non-linear fatigue (up to .135).
- **Design (D110; ratification needed).**
  - Pooled E4 + E5 lock; LR statistic under the unchanged T1/T2 nulls; NH1 confirmatory; closed testing of E4 and E5; CV fallback.
  - Calibration ≤ .068 in seven nulls. MDE OR 1.45; the E4 claim's MDE is 1.85.
- **Parametrization.** P6 (six channels) kept. The 1-df and frozen-direction alternatives gain average power only by assuming the true direction (rule R-G).
- **NH4.** A conditional gaze-given-validity test is adopted (rule R-I).
- **Baselines.** 17 strong baselines (TabPFN v2, GPBoost, MantisV2, MOMENT, attention-MIL, text-conditioned attention, TCN, …) are implemented and validated.
- **Ready.** G-AN tooling and protocol addendum, freeze tooling, Stage-2 / lock runners, the rule R-J command.
- **Plan amended** to v1.4 ([C-1]–[C-12]).

**Stage 1 — 2026-10-13 to 2026-10-14: [stage1/](stage1/README.md).** Status: **Stage 1 complete; stopped before Stage 2.** No outcome of any cohort was read; every simulated outcome is synthetic.

- **Infrastructure.** `src/cairn` is implemented and tested: incidence, item keys, recording clock, fold-safe features and references, penalized Rasch GLMM, T1/T2/T2c permutation tests, baselines, simulation, manifests and a gated CLI. All spec §3 leakage tests pass.
- **Primary form.** CAIRN-linear stays the primary, now **detrended within each recording**. The plan-literal form fails under a fatigue/position confound.
- **Calibration.** Every planned test is ≤ .07 under the four null scenarios (500 replicates each).
- **Power.** E4 alone: NH1 power .32 at OR 1.35, .97 at the minimum useful effect. The useful threshold is unchanged and corresponds to OR ≈ 2.1–2.2.
- **Redesign (needs your decision).** A pooled E4 + E5 lock with the plan's CV statistic is ready now: MDE 1.48, power .51 at OR 1.35. A likelihood-ratio upgrade (MDE 1.43) needs approval and a non-linear trend control.
- **Clustering** does not inflate the moment effect's variance; estimating the moment direction does.
- **Plan amended** to v1.3 ([S1-1]–[S1-13]).
- **Next:** the gates in [stage1/README.md](stage1/README.md#remaining-gates-before-stage-2).

**Stage 0 — 2026-10-13: [stage0/](stage0/README.md).** Status: **Stage 0 complete (computational parts); GO to Stage 1 under conditions; G-AN awaits human annotators.** No outcome accessed; no supervised fit.

- **Novelty narrowed.** Lallé 2025 already does item-anchored retention prediction from gaze. CAIRN's central claim is now psychometric identification with built-in falsification.
- **Timelines.** 10/11 timelines recovered (Immune partial). Enzymes is explained: two concatenated eHow videos.
- **Anchors.** Provisionally 105/131 items anchorable (development 87/107, in 59 distinct moments). The anchors are machine/LLM-assisted, not frozen.
- **Modalities.** Gaze is primary; pupil is ablation only; head, EEG and ECG are diagnostic only (EEG fails the reliability check).
- **Representation.** CAIRN-linear is the pre-specified primary; the learned encoder is an ablation; the peer-free variant is dropped.
- **Plan amended** to v1.2 ([S0-1]–[S0-8]).
- **Next:** human annotation (G-AN) and Stage 1 (outcome-free simulation and implementation). Stage 2 needs explicit authorization.

## Boundaries of this phase

- **Historical evidence stays unchanged.** G01-R (preregistered) and the John replication are not re-analysed, re-labelled or presented as confirmatory evidence for the new method. Everything proposed here is **post hoc relative to them**, as the G01-R final report requires for new architectures.
- **No outcome was read.**
  - No BBBD or John outcome, item response or score was opened.
  - The BBBD access log still has 15 entries and the John log 1.
- **The only computations** are two outcome-free audits of the existing signal cache ([evidence/](evidence/README.md)).
- **Nothing external was done:** no download, annotation, OSF deposit or author contact.

## Documents

| Document | Content |
|---|---|
| [research_plan.md](research_plan.md) | The plan, v1.1: synthesis, gap, candidates, selected method (CAIRN), novelty, diagram, mathematics, preprocessing, training, parameters, compute, splits, baselines, ablations, robustness, external validation, success/failure criteria, paper, risks, roadmap |
| [literature_review.md](literature_review.md) | Updated prior-art map N01–N43 (2023–2026 emphasis), access tiers, novelty-if-adapted per method, dataset assessment |
| [critical_review.md](critical_review.md) | Sceptical review of v1.0, with 18 concerns and revisions R1–R15 |
| [evidence/](evidence/README.md) | Outcome-free temporal-structure audits (gaze, pupil, EEG) and their scripts |

## Headline

- **Gap.** Physiological learning prediction has been posed at the wrong granularity: whole-video summary → video score. That representation keeps only about 10% of windowed ocular-synchrony variance (outcome-free audit). The item-level variance that makes up half of the score's within-video variance is treated as noise. No predictive, leakage-safe model links engagement **at the moments that carry each item's content** to **that item's correctness** in video learning.
- **Method.** CAIRN (content-anchored item-response network) has four parts:
  - outcome-blind item anchors from item text ↔ transcript alignment;
  - a per-second, peer-relative engagement encoder pretrained without outcomes;
  - anchored pooling;
  - a Rasch-type item-response head with person, item and within-learner moment terms.

  Gaze is primary. EEG, ECG and pupil are evidence-gated secondary channels.
- **Evaluation.**
  - Develop on E3 + E1 (three videos).
  - Lock E4 (new learners, new protocol, two new videos) as the primary confirmatory cohort and E5 as secondary.
  - Validate externally on Lallé (if its data terms allow) and on John (restricted).
  - The core test is the intersection of two tests: CAIRN beats an item-level baseline, **and** true anchors beat randomized anchors.
- **Expected value.** A new, falsifiable item-level capability, with a likely small video-level gain. Development stop rules protect the locked cohorts if the effect is absent.

## Next actions (require user decisions) — v1.1 list; see [stage0/README.md](stage0/README.md) §16 for the current list

1. Authorize transcript and video access for the 11 public stimulus videos, for anchoring only (Stage 0a).
2. Authorize clarifying the Lallé data terms; checking John posttest item texts outcome-blind; and checking the Madsen 2021 webcam data terms (Stage 0d).
3. Optionally commit this phase to time-stamp the plan before Stage 0.

Decision-log entries D069–D075 and inference-register entries INF-094–INF-100 record this phase.
