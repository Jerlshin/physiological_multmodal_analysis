# Critical review of the CAIRN research plan (v1.0 → v1.1)

2026-10-08. This review was written against plan v1.0 from the position of a sceptical reviewer at a strong ML, biomedical-signal, affective-computing or educational-technology venue (IEEE TAC, npj Science of Learning, Computers & Education, Behavior Research Methods). Each concern has a verdict:

| Verdict | Meaning |
|---|---|
| **Accepted → revised** | The plan changed; the tag [R#] marks the change in [research_plan.md](research_plan.md) |
| **Rebutted** | No change; the reason is given |
| **Open** | Can only be resolved by data or reading still to come |

## Summary judgement of v1.0

v1.0 identified a real weakness of the prior work: whole-video aggregation and video-level scores. It proposed a coherent alternative. Its main vulnerabilities were:

1. Novelty claims were stated before the two closest papers were read in full.
2. An item-level AUC could have been inflated by item difficulty.
3. Content overlap between development and the locked cohort weakened the "new content" claim.
4. The plan risked spending the locked cohort on an idea development had already contradicted.
5. Several baselines were named but not equalized.

After revision the plan is defensible as a **falsifiable measurement-and-method study**. Its success depends on an effect that may be small. The reviewer's main residual concern is **whether the reliable moment-level variance (≈ 16% of windowed ISC, E10) is large enough to matter**. Only development data can answer that.

## Concerns and responses

### 1. Is the novelty real? — Accepted → revised [R1]

**Concern.** Moment-level engagement → memory is known from:

- Davidesco 2023 (EEG; transcripts linked to questions);
- Hasson 2008 and Song 2021 (fMRI);
- Chen 2026 (event-level EEG, with prior knowledge).

Item-level comprehension prediction from gaze exists in reading (Shubi 2024; EyeBench 2025). Lallé et al. (AIED 2025) detect "retention" from gaze with dynamic AOIs in an educational video. "First item-level prediction from physiology" is not available, and CAIRN may be a re-assembly.

**Response.**

- §8 now lists what is **not** claimed.
- Claims are restricted to the combination N-a to N-e: outcome-blind anchors in an item-response formulation; reference-relative time-resolved representation; within-learner identification; built-in falsification nulls; inductive new-learner, new-content and new-protocol evaluation.
- Reading Lallé 2025 and Chen 2026 in full is a hard gate (Stage 0d) before the novelty statement is finalized (§22).
- If Lallé already anchors retention to items, the claim narrows and Lallé becomes both prior art and the external test.

**Residual:** open until both papers are read.

### 2. Could a simpler existing method do the same? — Accepted → revised [R2], [R4]

**Concern.** A crossed GLMM with windowed gaze ISC per item window (as in Wang 2025 or De Boeck 2011) may capture everything. The "network" may be decoration. Separately, any gain could come from the item-level likelihood (using 12 responses instead of one mean), not from anchoring.

**Response.**

- **B6 CAIRN-linear** (handcrafted anchored features + IRT head) is an explicit rung of the ladder.
- The selection rule (§12.4) picks the simplest variant within one SE of the best.
- §8 states that if CAIRN-linear matches the encoder, the contribution is the formulation, identification and falsification design, not the encoder [R4].
- **B5 IRT-whole** (item likelihood, whole-video features) and **A7** (item vs video likelihood with identical anchored features) separate "item likelihood" from "anchoring" [R2].
- The anchor-randomization null (T2) is the decisive test that anchoring, not item-level modelling, does the work.

### 3. Can ~55 development learners support the architecture? — Accepted → revised [R3]

**Concern.** Any learned temporal network will overfit 55 learners.

**Response.**

- The encoder (≈ 3k parameters) is trained **only label-free**, on about 1,000+ unlabelled exposures, fold-safe.
- It is then **frozen**. Supervised fine-tuning is limited to a K×K + K adapter, as an ablation (§12.3).
- Supervised parameters excluding item easiness number about 26, the same as the frozen ridge M5 (≈ 29) (§13).
- Item easiness is standard IRT estimated from about 25–47 learners per item, shrunk toward the video mean.
- The moment effect is estimated from about 12 within-learner contrasts per video.

### 4. Can the model exploit leakage? — Accepted → revised [R10]

**Concern.** Possible leakage paths:

- self-supervised pretraining on test learners' unlabelled exposures (transductive);
- peer references containing the test learner;
- anchors chosen after seeing which items people miss;
- standardization or KDE fitted on all data.

**Response.**

- Pretraining is **per outer fold, excluding test-fold learners**. E2 and untested exposures are label-free only (§12.1).
- References follow the G01-R access rules; leave-self-out; never selected by outcome, condition or quality (§15.3).
- Anchors are built blind to all learner data and frozen and hashed before any item-outcome linkage (§11.2).
- All cross-recording statistics are fitted per training split.
- A gated loader enforces the lock (§15.3).

### 5. Is the evaluation fair? — Accepted → revised [R5]

**Concern.** v1.0 listed modern baselines but gave CAIRN a richer tuning budget and compared it with ridge M2, which is too easy a bar.

**Response.**

- Every method gets the same cells, folds, information set and **≤ 20 configurations in nested CV**.
- The "strongest competing baseline" (best of B2–B4) is **selected in development and fixed** before the lock.
- NH3 tests CAIRN against it.
- Absolute performance (RMSE and MAE in items) is reported alongside increments (§16).

### 6. Could gains come from quality or content shortcuts? — Accepted → revised [R12]; partly rebutted

**Concern.** A model that sees validity per second can simply learn "missing data → wrong", or encode which video it is.

**Response.**

- **Content:** explicit item and video offsets; reference-relative channels remove the stimulus-locked component; an identity probe on z − ē is prespecified to be at chance (§18).
- **Quality:**
  - Recording-level Q stays in the baseline person path (M2 continuity).
  - In-window validity is the *object* of NH4, not a nuisance.
  - The anchor-randomization null separates the readings:
    - random hardware loss is not content-timed, so it cannot beat permuted anchors;
    - looking away during specific content can.
  - This turns the G01-R bottleneck (c) into a test (§7.4, §20).

**Rebuttal of the strong form.** Penalizing missing data per se cannot produce *item-specific* gains above the permuted-anchor null. The person-level part of missingness sits in θ and in the baseline.

### 7. Are the baselines strong and recent enough? — Accepted → revised [R5]

**Concern.** Missing baselines would leave the gain claim open:

- tabular foundation models (TabPFN v2);
- mixed-effects boosting (GPBoost);
- MIL / temporal transformers;
- EEG/TS foundation models;
- reading-domain eye-movement models.

**Response.**

- B3 includes TabPFN v2, GBMs and GPBoost.
- B4a includes frozen MOMENT/Mantis and CBraMod/REVE/LaBraM embeddings.
- B4b is attention-MIL / temporal transformer, with and without CAIRN's encoder.

**Rebutted:** EyeBench reading models (RoBERTEye-type) need word-level text alignment of fixations and do not apply to shared-screen video. They are cited as conceptual evidence for content awareness, not run.

### 8. Can the ablations establish the contribution? Is the AUC inflated? — Accepted → revised [R6]

**Concern.** A within-learner AUC is high even for a baseline that only knows item difficulty, since hard items are wrong more often. Reporting CAIRN's raw AUC overstates the contribution.

**Response.**

- The item-level discrimination metric is now **ΔAUC_wp relative to IRT-M2** (§10). Thresholds are stated on the increment (§20.2).
- The A1 nulls (permuted and circular-shifted anchors) run in the locked evaluation as randomization tests, not only in development.

### 9. Is the external evidence truly independent? — Accepted → revised [R11]

**Concern.** The Madsen webcam cohorts share videos, items and lab. John's gaze block was already used confirmatorily. "External replication" could be overstated.

**Response.**

- §19 now includes an independence statement per dataset.
- Webcam is labelled cross-sensor transport.
- A top-venue claim requires **at least one fully independent external replication of NH1** (Lallé, or John with item anchors).
- Without it, the target venues are adjusted (§21, §22).

### 10. Would the paper be publishable if gains are modest? — Accepted → revised [R14]

**Concern.** Video-level gains will likely be < δ. Many venues expect a headline improvement.

**Response.**

- Outcome categories are pre-declared (§20.4).
- The paper is framed around the item-level capability, which video-level models cannot offer at all. The video-level gain is secondary.
- Venues are mapped to categories (§21).
- Even a locked failure is a reportable bounded negative that completes the G01-R / John / CAIRN record.

### 11. Is "engagement" circular? — Accepted → revised [R7]

**Concern.** v1.0 used attend versus distract (E1–E3) both as a pretraining target and as construct evidence. That is circular, and the condition is confounded with repetition and arithmetic.

**Response.**

- Attend versus distract is removed from pretraining and reserved for **outcome-free construct validation only** (§12.1, §18, diagnostic 5).
- Its confounds are stated. It is a sanity check that e(t) indexes viewing engagement at all, not proof of attention.

### 12. Temporal confounds — Accepted → revised [R8]

**Concern.** Learners who fade late in a video both disengage and miss items about late content. That is arguably real attention, but recency and primacy plus fatigue could produce a moment effect without content specificity.

**Response.**

- Item position goes in β; a learner-specific engagement trend goes in θ (§18).
- The **circular-shift null** preserves the anchors' temporal configuration, while the **permutation null** destroys it. Both are reported.
- A content-specific effect must beat the circular shift as well.

### 13. Annotation can confound the localized/diffuse contrast — Accepted → revised [R13]

**Concern.** Annotators may label easy recognition items "localized" and hard comprehension items "diffuse". λ_localized > λ_diffuse could then reflect difficulty or category, not specificity.

**Response.**

- The A9 contrast is estimated conditional on β_{vj} and category (R/C), and reported per category.
- Annotators see only video and items, never learner data.
- The LLM proposer is non-binding.
- Inter-annotator agreement on the flag is reported (§11.2, §17).

### 14. The locked cohort may not test new content — Accepted → revised [R15]

**Concern.** E4's three videos (Stars, Related, Immune) all appear in development: Related in E3, Stars and Immune in E1. The locked evaluation would test only new learners and a new protocol.

**Response.**

- E1's Stars and Immune cells are **removed from development** and kept as a descriptive "known learner, new content" check (§15.2).
- In E4, Stars and Immune are therefore new content relative to development; Related remains known.

### 15. Wasting the locked cohort — Accepted → revised [R9]

**Concern.** Running the lock after development has already shown no anchored signal would burn E4/E5 for nothing and invite post hoc rescue.

**Response.** Development stop rules (§20.5) require, before the lock:

- true anchors beat permuted anchors (exploratory p < 0.10);
- ΔAUC_wp ≥ 0.01;
- a positive outcome-free construct check.

Gate failures (G-TL, G-AN) stop item-level work for the affected videos.

### 16. Is the effect plausibly large enough at all? — Open

**Concern.** The outcome-free audit gives about 16% reliable person × moment ISC variance, an upper bound that may include shared x/y artifacts. Item-level effects may be undetectable even if real.

**Response.** Not resolvable without outcomes.

- The Stage-1 simulation on real features sets power for plausible effects (OR 1.2–1.5 per true-score SD).
- The development stop rule decides whether to spend the locked cohorts.
- The plan does **not** promise a material video-level gain; it states a small expected range (§7.3).

### 17. Is the stimulus timeline recoverable? — Open

**Concern.** Recorded durations differ from YouTube (E11), and Enzyme is *longer* than its reported duration.

**Response.** Gate G-TL (§11.2), with scene-cut ↔ peer-saccade alignment cross-checked against the original P01 materials. Failure excludes the affected videos.

### 18. Does post-preregistration method work on BBBD conflict with M08? — Rebutted (with disclosure)

**Concern.** M08 and the G01-R final report recommended no new architectures on BBBD.

**Response.**

- M08 governed the preregistered program. The final report allows new methods as "a new, separately preregistered exploratory protocol … reported as post hoc relative to G01-R". This plan follows that prescription.
- The report's specific worry, that flexible learners would fit content identity, is addressed by design: reference-relative channels, explicit offsets, identity probe.
- The user's instruction opens the phase.
- The deviation is logged (D069).

## Changes v1.0 → v1.1

| Tag | Change | Plan section |
|---|---|---|
| R1 | "Not claimed" list; novelty conditional on reading Lallé 2025 and Chen 2026 in full | §8, §22, §23 (0d) |
| R2 | B5 IRT-whole baseline; A7 item-vs-video likelihood ablation | §16, §17 |
| R3 | Encoder label-free and frozen; adapter-only fine-tuning; parameter parity with M5 | §12.3, §13 |
| R4 | Contribution defined at formulation level if CAIRN-linear ≈ CAIRN | §8 |
| R5 | Equal tuning budget; strongest baseline fixed in development; TabPFN v2, GPBoost, MIL, FM baselines | §16 |
| R6 | ΔAUC_wp relative to IRT-M2 instead of raw AUC | §10, §20.2 |
| R7 | Attend/distract only for construct validation, not pretraining | §12.1, §18 |
| R8 | Item-position and engagement-trend controls; circular-shift null alongside permutation | §18, §20.1 |
| R9 | Development stop rules protect locked data | §20.5 |
| R10 | Fold-wise label-free pretraining excluding test-fold learners | §12.1, §15.3 |
| R11 | Independence statement; independent external replication required for a top-venue claim | §19 |
| R12 | In-window validity treated as hypothesis NH4 with the randomization null; recording-level Q kept in the baseline | §7.4, §20 |
| R13 | A9 conditional on item easiness and category; annotation blind; LLM non-binding | §11.2, §17 |
| R14 | Pre-declared outcome categories; venue mapping for modest gains | §20.4, §21 |
| R15 | E1 Stars/Immune removed from development so that E4 contains new content | §15.2 |

## Reviewer's bottom line

**Recommendation: proceed to Stage 0.**

- The direction answers the specific failure documented by G01-R.
- It is testable with BBBD plus at least one external cohort.
- It contains falsification tests that a reviewer cannot easily dismiss.
- It does not depend on capacity the data cannot support.

**Main risk:** an effect too small to be useful. That risk is now contained by the development stop rule rather than discovered on the locked cohort.
