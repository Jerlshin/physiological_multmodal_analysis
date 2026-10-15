# Literature close-out (Stage 0d): closest-paper risks and the novelty verdict

2026-10-13. This pass was adversarial: it searched for work that would **invalidate or narrow** CAIRN. Access tiers follow [literature_review.md](../literature_review.md):

| Tier | Meaning |
|---|---|
| FT | Full text, or code, read |
| AB | Abstract only |
| SN | Snippet only |

Downloaded copies are kept outside the repository (licensing); hashes are listed in [evidence/literature_sources.json](evidence/literature_sources.json).

## 1. What was obtained

| Work | Best version obtained | Tier now | Notes |
|---|---|---|---|
| **N15 — Lallé, Nikneshan, Lambert, Luengo & Abou-Hassan, AIED 2025** (LNCS 15878:135–148, doi 10.1007/978-3-031-98417-4_10) | **Public code and data repository** (gitlab.lip6.fr/mocah-public/eye_tracking_green_chem_video): `train_model.py`, `emdat_feature_sets.py`, `generate_segs.py`, `QCM to Tobii time.py`, LICENCE. The full description of the dataset and protocol is in Becquet et al. 2026 (N16, FT). Abstract (HAL, Springer) | **FT (methods via code) + AB (paper text)** | The paper's PDF was not readable: the publisher (Springer) and HAL serve bot challenges, which were **not** circumvented, and the author page does not resolve. **Reported retention numbers are therefore unverified.** User action: download the PDF in a browser and add it to the close-out |
| **N16 — Becquet, Lallé, Luengo & Abou-Hassan, arXiv 2605.20211 (2026)** | arXiv PDF | **FT** | Same dataset as N15: N = 70; 7-min green-chemistry video; Tobii Nano; free (self-paced) viewing; 18 attention self-report time points; 20 s segments; factual recall test. Gemini 3 visual prompting does not beat baselines (macro F1 ≤ .50 vs .59 for N15's classifiers) |
| **L08 — Chen J, Li X, He M, Chen X & Zhang D, *NeuroImage* 338:122062 (2026)** | PubMed abstract (E-utilities); Elsevier full text is subscription-only; no preprint found | **AB** | Methods not obtainable. User action: institutional access |
| N09 — EyeBench (Shubi et al., NeurIPS 2025 D&B) | Paper PDF (proceedings) + **official results files** (github.com/EyeBench/eyebench `results/eyebench_benchmark_results/auroc.csv`) | **FT** | Corrects our earlier claim (§3) |
| **N44 (new) — Lan, Brinton, Yang & Chiang, "Behavior-Based Latent Variable Model for Learner Engagement", EDM 2017** | Abstract | AB | Closest *psychometric* analogue (§2) |
| N45 (new) — COIVis, Zhou et al., *IEEE TVCG* 32(7), 2026 (arXiv 2512.06834) | Abstract | AB | Concept-of-interest gaze analytics in MOOC videos; descriptive |
| N46 (new) — SAVVY, Zhou et al., arXiv 2607.29413 (2026) | Abstract | AB | Attention visualization from multimodal signals for teachers; descriptive |
| N47 (new) — AttentiveLearn, Liu et al., CHI 2026 (arXiv 2603.05324) | Abstract | AB | Gaze-personalized post-lecture quizzes in VR; field study, no learning gain shown |
| N48 (new) — Bodonhelyi et al., mind-wandering review and multimodal benchmark, arXiv 2604.09569 (2026) | Abstract | AB | 14 datasets; target is mind-wandering, not item retention |
| N49 (new) — Madsen, Kuppa & Parra, BBBD, *Scientific Data* 2026 (s41597-026-07215-1; PMC13284221) | Europe PMC full text | **FT** | Lists the YouTube durations and IDs; **no trim information**; lists `lkRZKqDdwzU` only for Enzymes (cf. timeline audit) |
| N50 (new) — Cao et al., "Signals of Success and Struggle", CHI 2026 (arXiv 2603.18798) | Abstract | AB | Ocular/cardiac early performance prediction in a game; not video learning |
| N51 (new) — LEXIC, arXiv 2607.08152 (2026) | Abstract | AB | Source of the "text-aware 56–63% AUROC; gaze-only at chance" summary of EyeBench |

**Searches.** 14 web queries this pass. Areas covered:

- the two closest papers;
- item- and segment-level quiz prediction from gaze, EEG or physiology in video;
- explanatory IRT with process data;
- knowledge tracing with physiology;
- question-locked ISC;
- 2025–2026 gaze-plus-foundation-model education work;
- reuse of BBBD.

No paper reusing BBBD for item-level or segment-level analysis was found.

## 2. Comparison with the closest works

| Dimension | **Lallé 2025 (N15)** | **Chen 2026 (L08)** | **Davidesco 2023 (N01)** | **Lan 2017 (N44)** | **EyeBench 2025 (N09)** | **CAIRN (planned)** |
|---|---|---|---|---|---|---|
| Task | Detect self-reported attention (18 probes) and **per-item retention** (QCM correct/incorrect) | Relate prior-knowledge profiles to EEG neural similarity; event-level outcomes | Relate classroom EEG synchrony to learned vs not-learned questions | Predict unobserved in-video quiz responses | Predict reading comprehension (per question) and other reader traits | Predict per-item correctness from engagement at each item's content moment |
| Signals | Tobii Nano gaze (~60 Hz): fixations, saccades, pupil, head distance, **dynamic AOIs** | EEG (theta, alpha) | EEG | Clickstream (pauses, rewinds, speed) | Reading eye movements + text | EyeLink gaze; validity episodes; (pupil ablation); EEG and ECG only as diagnostics |
| Temporal granularity | Windows of 10–30 s ending at the item's content, or the item's content span | Events (learning segments) | Question segments ≥ 3 s | Whole video (one engagement value per video) | Trial (one passage) | Per second → pooled over each item's anchor |
| Use of content | **Yes:** author-specified item content spans (15–19 items); hand-drawn AOIs on screen content | Event segmentation of the physics video | Teacher's explanation of each question located in transcripts | In-video question tied to its video | Text-aware models | Outcome-blind anchors from item text ↔ transcript, with a published protocol and agreement gate |
| Target | **Item-level** retention | Event-level and person-level outcomes | Question-level (learned / not) | Item-level | Item-level (comprehension question) | **Item-level**; video level secondary |
| Prediction vs explanation | **Held-out prediction**: 8-fold StratifiedGroupKFold by participant, F1 | Explanatory (correlation / IS-RSA) | Explanatory (multilevel models, ANOVA) | Held-out prediction of responses | Held-out prediction | Held-out prediction plus **randomization tests** |
| Learner / content splits | New learners; **same items** (one video) | — | — | Random held-out responses | Unseen reader / unseen text / both | New learners; **new content** (Stars, Immune locked); **new protocol** (E4) |
| Architecture | NB, LR, SVM, RF, feed-forward nets (± self-attention); PCA; SMOTE; pre/in/post fusion | IS-RSA | Statistics | Latent variable model: engagement from behaviour → latent knowledge → responses | RoBERTa-based fusion, CNNs, LSTMs | Penalized Rasch-type GLMM over anchored per-second channels (CAIRN-linear primary) |
| Peer / reference signals | **No** (reference-free features and AOIs) | Inter-subject similarity (explanatory) | Inter-subject synchrony | No | No | **Yes**: per-second peer-relative alignment (leave-self-out / unlabelled peers) |
| Psychometric modelling | **No**: item identity is dropped (`Sc_id`); no item difficulty or person term; weighted F1 over pooled items | No | Multilevel (explanatory) | **Yes** (latent ability, engagement) | No (but a text-only baseline, see §3) | **Yes**: item easiness + learner level + **within-learner** moment effect |
| Outcome-blind anchoring | Spans are author-specified; blindness and reliability **not documented** | n/a | Located by researchers; not documented as blind | n/a | n/a | Required, gated, hash-frozen |
| Leakage controls | Participant-grouped CV | n/a | n/a | — | Reader / text splits | Learner-grouped, fold-safe references and normalization, gated outcome loader, identity probes |
| Falsification nulls | **None** (no shuffled or shifted windows) | No | No | No | No | **Anchor permutation and circular shift** (T2, co-primary) |
| External validation | No (one dataset) | No | No | No | Several datasets (reading) | Locked new-protocol cohort + external (Lallé; John if item texts are obtained) |

## 3. Corrections to the earlier literature record

1. **EyeBench (N09).** The earlier summary was "gaze-only models at chance; text-aware 56–63% AUROC; content awareness is what makes it work". The official results show a different picture:
   - A **text-only RoBERTa without any gaze reaches 61.1 AUROC** (OneStop, test, all regimes).
   - RoBERTEye-Fixation reaches 61.9, MAG-Eye 62.9 and PostFusion 61.1.
   - In the unseen-reader / seen-text regime: text-only 66.3 vs 67.3–67.7 with gaze.
   - **[F]** Most "text-aware" performance is **item knowledge, not gaze**. Gaze adds only about 1–3 AUROC points.
   - **[I]** This is the clearest external evidence that item-level metrics must be read as increments over an item-only baseline. CAIRN already does this (ΔAUC_wp over IRT-M2, [R6]).
   - It also says the **plausible size of the moment increment is small**: in reading, where gaze is on the tested words, it is about 1–3 points.
   - The plan's minimum useful item effect (ΔAUC_wp ≥ 0.02) is therefore **ambitious, not conservative**.
2. **Lallé dataset (N41).**
   - The "per-item 'already knew' response", described as an item-specific prior-knowledge control, was **not found** in the code or in Becquet 2026.
   - `PriorKnowledge` appears only as a **person-level** fairness attribute.
   - The claim is withdrawn until the dataset documentation shows otherwise.
   - Data terms: the repository carries only a **BSD-3 software licence** ("Copyright (c) 2025, XXX"). Becquet 2026 says the data were "shared publicly". Reuse terms for the data are still not explicit (user action: ask the authors).
3. **Davidesco 2023 (N01)** and **Chen 2026 (L08)** remain **explanatory**. Chen's within-individual, event-level analysis is an explanatory precedent for the *within-learner* logic of N-c. Its methods are not verified.

## 4. Novelty verdict

### 4.1 The collision

**[F]** Lallé et al. (2025) already pose **content-anchored, item-level retention prediction from eye-tracking during an educational video, evaluated on held-out learners**:

- each quiz item has a video content span;
- gaze features are computed in windows tied to that span;
- a per-item correct/incorrect label is predicted with participant-grouped CV.

**This collides with CAIRN's problem formulation claim N-a**, as far as N-a reads "physiological learning prediction as a content-anchored item problem for video learning". **That part of N-a is withdrawn.**

### 4.2 What Lallé (and every other work found) does not do

1. **Psychometric identification.**
   - Lallé pools items and drops item identity. Its F1 therefore mixes item difficulty, person ability and moment-level engagement. EyeBench's text-only baseline shows how much of an item-level score item knowledge alone can produce.
   - No work separates a **within-learner, within-video moment effect** from item easiness and the learner level in predictive form, for physiology during learning.
   - Lan 2017 does person, item and engagement for clickstream, with one engagement value per video, not per moment or per item.
2. **Falsification built into the estimand.** No work tests anchored windows against **permuted or circularly shifted anchors**. That test is the only way to show that the *content timing* carries the information, rather than item-level modelling, data loss or temporal trends.
3. **Outcome-blind, reproducible anchoring.** No work publishes an anchoring protocol with blinding, inter-annotator agreement and a hash-frozen anchor set. Lallé's spans are author-specified, with no reliability or blinding reported.
4. **Peer-relative per-second representation for item prediction.** Lallé uses reference-free features and hand-drawn AOIs. Peer-relative gaze at the anchored moment is new as an item predictor. Stage 0 shows it is the strongest construct channel and that its item-centred moment terms are free of content identity.
5. **Inductive evaluation across content and protocol**, with a locked, preregistered cohort.
   - Lallé: one video, seen items.
   - CAIRN: new content and a new protocol in a locked cohort, plus external replication.

### 4.3 Revised contribution statement

The claim moves from *a new problem formulation* to *the first psychometrically identified and falsifiable test of whether content-anchored engagement predicts which items learners miss*. It is a measurement-and-method contribution:

| ID | Status | Claim |
|---|---|---|
| **N-a′ (narrowed)** | Kept | A **psychometric** item-response formulation, beyond item easiness and the learner level, with **outcome-blind, reliability-gated anchors**. **Not claimed:** first item-anchored gaze prediction (Lallé 2025) |
| N-b′ (narrowed) | Kept | A peer-relative per-second representation for item prediction, with unlabelled peers on new content. **Peer-free distillation dropped** (Stage 0: R² < 0) |
| N-c | Kept | Within-learner identification. **Not claimed:** first within-individual event-level analysis (Chen 2026, explanatory) |
| N-d | Kept, now the **central claim** | Falsification as part of the method: anchor permutation, circular shift, in- vs out-of-window data loss |
| N-e | Kept | New learners, new content, a locked new-protocol cohort, external replication |

### 4.4 Does a newer method look like a stronger direction?

No. The 2025–2026 work found is either explanatory (L08), descriptive analytics (COIVis, SAVVY), training-free foundation models that fail (Becquet 2026), or mind-wandering benchmarks without item targets. None offers a stronger route to item-level prediction from video-learning physiology. EyeBench points the same way as CAIRN's design: the item-only baseline is the bar.

**Lallé's dataset is now more valuable to CAIRN, not less:**

- It is the only public external cohort with item-mapped segments.
- It provides a direct head-to-head: Lallé-style pooled classifiers versus psychometric anchoring on the same data.

The external-validation plan should add **"Lallé's own windows and classifiers" as an external baseline**, subject to data terms.

## 5. Unresolved

| Item | Required action |
|---|---|
| Lallé 2025 paper text (reported retention F1, whether item difficulty was discussed) | User downloads the PDF in a browser |
| Chen 2026 methods | Institutional access |
| Lallé data reuse terms | Contact the authors |
| Kok 2023 (N12) and N05 | Not re-verified in this pass |
