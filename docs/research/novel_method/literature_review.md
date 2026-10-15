# Updated literature review and prior-art map (2023–2026 emphasis)

2026-10-08. This review **extends** the earlier records; it does not replace them:

- [research-gap bibliography L01–L43](../research_gap/bibliography.md) and [synthesis](../research_gap/literature_evidence.md);
- [BBBD prior-work dossiers P01–P05](../selected_dataset/prior_work.md);
- [novelty close-out](../experimental_design/novelty_closeout.md).

New records are numbered **N01–N43**. Earlier IDs are cited where they still carry weight.

**Access tiers** (as in the earlier phases):

| Tier | Meaning |
|---|---|
| FT | Relevant full-text sections read |
| AB | Abstract or official landing page read |
| SN | Search-result text only; a lead, not evidence |
| FD | Foundational work cited from established knowledge, not re-fetched in this pass |

Load-bearing novelty claims rest only on FT/AB records. **Two closest-paper risks remain open:**

- **N15 (Lallé et al., AIED 2025):** full text not obtained;
- **L08 (Chen et al., NeuroImage 2026):** full methods not obtained.

Both must be read before any novelty claim is submitted ([research plan §22](research_plan.md#22-major-publication-risks)).

**Stage-0 amendment, 2026-10-13 [S0-1].** The close-out is in [stage0/literature_closeout.md](stage0/literature_closeout.md).

- **N15** is now read at code level, through the public repository, and its dataset protocol in full through N16. Its paper text is still not obtained, because the publisher and HAL bot challenges were not circumvented. It **collides** with the first clause of claim N-a.
- **L08** is verified at abstract level (PubMed). Its methods are subscription-only.
- **N09** numbers are corrected.
- **N41's "already knew" claim** is withdrawn.
- **N44–N51** are added (§2.I).

## 1. Search scope and method

- **Queries:** 42 web queries and 24 page/API fetches in this pass, across 15 areas:
  - moment-level engagement and memory;
  - item-level comprehension prediction from gaze;
  - attention detection in educational video;
  - explanatory IRT with process data;
  - knowledge tracing with physiology;
  - EEG, ECG, gaze and time-series foundation models and their benchmarks;
  - tabular foundation models;
  - mixed-effects machine learning;
  - multiple-instance learning for long recordings;
  - confounder-free training;
  - missing-modality fusion;
  - reference-free synchrony estimation;
  - video saliency;
  - stimulus-tracking encoding models;
  - public datasets with gaze or EEG during educational video.
- **Fetching:** primary sources were fetched where accessible (arXiv, bioRxiv, NeurIPS/ICML/ICLR proceedings, OSF API, publisher landing pages).
- **Blocked:** Springer and Nature returned authentication redirects; ACM returned 403. Those records are tiered AB or SN accordingly.
- **Status:** this is a targeted, saturation-driven review for the method decision, not a systematic review.

## 2. Prior-art map

Columns:

- **Problem:** what the work actually solves.
- **Contribution:** its architectural or analytic contribution.
- **Scale:** its evaluation scale.
- **Fit:** whether its assumptions match BBBD.
- **Code:** availability.
- **Ours:** trainability on our resources.
- **Novelty if adapted:** whether adapting it would be genuine novelty or only application.

### A. Moment-level engagement and memory for specific content (closest *scientific* prior art)

| ID | Work (tier) | Problem / contribution | Scale | Fit to BBBD | Code | Novelty if adapted |
|---|---|---|---|---|---|---|
| N01 | Davidesco, Laurent, Valk, West, Milne, Poeppel & Dikker, *Psychological Science* 2023; bioRxiv 644047 (FT preprint) | EEG alpha brain-to-brain synchrony in a simulated classroom. Lectures were transcribed and the teacher's explanation of each test question located; segments ≥ 3 s retained. Synchrony was higher for "learned" than "not learned" questions. Multilevel models and ANOVA. **No cross-validation or held-out prediction** | 31 students, 4 lectures, 10-item tests | High conceptually: item-to-segment linkage by transcript. Live teacher, EEG only | Not verified | **Closest precedent for item anchoring.** Association, not a predictive model; no IRT decomposition, reference-relative representation or falsification nulls. Adapting its analysis to BBBD would be application |
| N02 | Cohen & Parra, *eNeuro* 2016 (AB) | EEG ISC during narratives relates to memory three weeks later, between persons | 72 people | Same lab lineage as BBBD | — | Between-person, not item-level |
| N03 | Song, Finn & Rosenberg, *PNAS* 2021 (AB) | fMRI connectivity tracks moment-to-moment engagement, which predicts event recall | fMRI cohorts | Event-level memory; fMRI | — | Mechanistic precedent for event-level engagement → memory |
| N04 | Hasson, Furman, Clark, Dudai & Davachi, *Neuron* 2008 (FD) | Higher ISC during later-remembered movie events | fMRI | Event-level subsequent memory | — | Foundational |
| L08 | Chen, Li, He, Chen & Zhang, *NeuroImage* 338:122062, 2026 (AB, verified via PubMed 42302884) | EEG IS-RSA in online physics learning. Frontal theta similarity relates to between-person outcomes; within individuals, event-level alpha similarity is negatively associated with event outcomes in low-prior-knowledge learners only | — | Event-level outcomes, prior knowledge | — | **[S0-1]** Explanatory; no evidence of held-out prediction. Precedent for within-individual event-level analysis (N-c, explanatory). Methods subscription-only |
| N05 | "Decoding EEG for optimizing naturalistic memory", bioRxiv 2023.08.25.553563 (SN) | Item-level subsequent-memory decoding from EEG during naturalistic encoding | — | Item-level memory decoding | — | Lead; verify before citing as evidence |
| N06 | Silvan Ortubay, Parra & Madsen, arXiv 2409.13084, 2024 (AB) | A deep network estimates 10-s gaze ISC from face and eye movements **without a reference cohort**. R² 0.26–0.30 on unseen subjects | 83 people, educational videos | Same lab and video types. Webcam/face, not EyeLink | GitHub (stated) | Occupies the "reference-free ISC estimation" motivation. Our reference distillation must be framed relative to it |
| N07 | "Intersubject correlation as a predictor of attention: a systematic review", *BMC Psychology* 2025 (SN; publisher blocked) | Review of ISC → attention/learning | — | — | — | Context |

### B. Predicting learning or comprehension from gaze (item-level and video-level)

| ID | Work (tier) | Problem / contribution | Scale | Fit | Code | Novelty if adapted |
|---|---|---|---|---|---|---|
| N08 | Shubi, Meiri, Hadar & Berzak, EMNLP 2024 (AB) | **Question-level** reading comprehension predicted from eye movements with multimodal language models. New-item / new-participant / both splits. "Highly challenging", but eye movements carry signal | OneStop (N10) | Reading, where gaze lands on the tested words. In video, gaze is on a shared visual stream | Promised | Methodological precedent for item-level prediction with person/item splits |
| N09 | Shubi, Reich, Gruteke Klein, Angel, Prasse, Jäger & Berzak, EyeBench, NeurIPS 2025 D&B (AB; numbers SN) | Benchmark of predictive models from reading eye movements, with new reader / new text / both splits. Reported (SN): **text-aware models reach 56–63% AUROC on comprehension; gaze-only models are at chance**. **[S0-1] Verified (FT, official results `auroc.csv`):** text-only RoBERTa **without gaze** 61.1 AUROC (OneStop, test, all regimes) vs RoBERTEye 61.9 and MAG-Eye 62.9. Most "text-aware" performance is item knowledge, and gaze adds about 1–3 points | Several datasets | Calibrates what item-level gaze prediction can achieve. **Content awareness is what makes it work** | github.com/EyeBench/eyebench | Supports content anchoring as the necessary ingredient. Its numbers must be verified from the paper before quoting |
| N10 | OneStop Eye Movements, 360 participants (AB) | Large reading corpus with 486 comprehension questions | 360 | Reading | Public | Not usable for video pretraining |
| N11 | Wang, Xie & Liu, *Frontiers in Education* 2025 (FT) | Crossed student × item logistic GLMM during **quiz-taking**: fixation intensity OR ≈ 1.30/SD, regression rate OR ≈ 0.81/SD. No held-out test | 34 students, 320 attempts | Gaze while answering, not while learning | — | Shows the explanatory-IRT-with-gaze pattern exists. Our item covariates come from the *learning episode*, anchored to content |
| N12 | Kok et al., *Cognitive Science* 2023 (AB) | "With-me-ness" (looking where the teacher refers) and comprehension; human raters predict comprehension from gaze visualizations | Small | Content-referenced gaze; needs frames | — | Content-relative gaze precedent |
| N13 | Srivastava et al., LAK 2021 "Are you with me?" (SN; ACM 403) | Video-watching attention measured by eye tracking | — | — | — | Lead |
| N14 | Bühler, Bozkir, Goldberg, Sümer, D'Mello, Gerjets, Trautwein & Kasneci, *IJAIED* 2025 (AB) | Lab-to-wild generalization of video-based mind-wandering detection. F1 0.44–0.46 within; 0.35 across settings | 135 + 15 | Mind-wandering probes (absent in BBBD) | — | Shows cross-setting transfer is hard |
| N15 | Lallé et al., "Automated Detection of Attention and Retention in Educational Videos Using Eye-Tracking, Dynamic Areas of Interest and Feature Fusion", AIED 2025 (title SN; F1 via N16) | Gaze features with dynamic AOIs detect self-reported attention (F1 ≈ 0.59) and **retention** | 70 learners, 7-min video | **Closest applied competitor.** Whether "retention" is item-anchored is **unverified** | Dataset on GitLab | **Must read before claiming novelty.** If item-anchored retention detection is already done, our claim narrows to the psychometric decomposition, reference-relative encoding, falsification design and cross-protocol inductive evaluation. **[S0-1] Read at code level: collision confirmed.** It predicts per-item retention from gaze in 10–30 s windows tied to author-specified item content spans, with 8-fold participant-grouped CV. Item identity is dropped: no item difficulty, no learner term, no randomization nulls, no peer signals, one video. The claim narrows as anticipated |
| N16 | Becquet, Lallé, Luengo & Abou-Hassan, arXiv 2605.20211, 2026 (FT) | A VLM (Gemini 3) on gaze-overlaid video for attention detection on 20-s segments **fails to beat statistical baselines** (F1 ≤ 0.50 vs 0.59) | 70 learners, ~1,033 segments | Same dataset as N15 | — | Evidence that generic foundation models do not solve gaze-in-context attention |
| L04, L05, L06 | Bühler 2024; Sauter 2022; Liu 2023 (inherited) | Gaze synchrony, attention and tests; mixed replication | — | — | — | Context for heterogeneity |
| L07 / John | John et al., *Sci Rep* 2025, and our replication (FT) | Gaze clusters and posttest. Our replication: the gaze block adds held-out information beyond the pretest (Ŝ 0.079) | 112 learners, 1 video | External ocular cohort; POI content segments annotated | OSF | — |

### C. Psychometrics and item-response modelling

| ID | Work (tier) | Relevance |
|---|---|---|
| N17 | De Boeck, Bakker, Zwitser, Nivard, Hofman, Tuerlinckx & Partchev, *J Stat Softw* 39(12), 2011 (AB) | IRT as GLMM with **person, item and person-by-item covariates**. The statistical backbone of our item head; no novelty claimed for it |
| N18 | van der Linden 2007 hierarchical response / response-time framework (SN); multilevel IRT with process data (SN) | Joint modelling of responses and process data. Our process data are pre-test learning-episode signals, not response-time data |
| N19 | Hedge, Powell & Sumner 2018 (inherited) | Reliability paradox: within-person effects can be robust when between-person differences are unreliable. Motivates the within-person moment effect |

### D. Representation learning and foundation models

| ID | Work (tier) | Finding relevant to BBBD | Use in this plan |
|---|---|---|---|
| N20 | EEG-FM-Bench, Xiong et al., ICML 2026 (AB) | 14 datasets / 10 paradigms. Data or model scale alone does not determine transfer; objective alignment and adaptation matter | Baseline tier only |
| N21 | EEG-FM-Compass, Liu et al., *Natl Sci Rev* 2026 (AB) | "Specialist models trained from scratch remain competitive"; "linear probing is frequently insufficient"; larger FMs do not necessarily generalize better | Expect small gains from frozen EEG FMs at n ≈ 60 |
| N22 | AdaBrain-Bench, Wu et al. 2025 (AB) | Cross-subject / few-shot BCI benchmark of brain FMs | Baseline protocol reference |
| N23 | OmniEEG-Bench, NeuroAtlas 2026 (SN) | Classical baselines match FMs on low-channel sleep EEG (SN) | Context |
| L28 / L29 / L26 | CBraMod (ICLR 2025), REVE (NeurIPS 2025), BIOT (NeurIPS 2023) (inherited) | Checkpoints exist. Rates and channel conventions must be matched; BBBD EEG is 128 Hz with uncertified units | Frozen-embedding baselines (B4a) |
| N24 | LaBraM, Jiang, Zhao & Lu, ICLR 2024 (FD) | EEG FM | B4a candidate |
| L34 | Zare 2026 negative-control protocol (inherited) | FMs encode dataset identity | Identity-probe diagnostics on any embedding |
| N25 | HuBERT-ECG (medRxiv 2024) and ECG-FM (2025) (AB) | 12-lead/single-lead ECG FMs; strong for diagnosis | **Not used**: BBBD cardiac information enters as R-peak timing; diagnostic morphology is not the construct |
| N26 | MOMENT (ICML 2024, FD); Mantis / MantisV2 (2025; ICLR 2026) (AB) | General time-series FMs; frozen embeddings for classification | Frozen-embedding baseline for gaze/pupil channels (B4a) |
| N27 | GLASS, arXiv 2601.12534 (SN); Gaze-READ / GazeMTM (MOMENT-based gaze embeddings) (SN) | Self-supervised gaze representations by forecasting or masking | Masked/forecast pretraining objectives for our encoder are **not novel**; cited as such |
| N28 | CEBRA, Schneider, Lee & Mathis, *Nature* 2023 (AB) | Contrastive embeddings consistent across subjects, with auxiliary variables | Time-contrastive alternative; would emphasize shared, stimulus-locked structure, which we deliberately remove |
| N29 | Deep CCA / deep multi-way CCA for shared EEG responses (SN) | Learned shared-response extraction | Nonlinear CorrCA alternatives; EEG branch option |
| L25 / L30 / L31 | PhysioOmni, FactorCL, CoMM (inherited) | Shared/private multimodal SSL | Generic multimodal SSL is occupied; not claimed |

### E. Small-data tabular, mixed-effects and weakly supervised baselines

| ID | Work (tier) | Use |
|---|---|---|
| N30 | TabPFN v2, Hollmann et al., *Nature* 2025 (AB) | Strong small-n regression baseline on whole-video features (B3) |
| N31 | TabArena, NeurIPS 2025 D&B (AB) | Tabular FMs excel on small data; GBMs remain strong. Justifies both in B3 |
| N32 | Grinsztajn, Oyallon & Varoquaux, NeurIPS 2022 (AB) | Tree models beat deep nets on medium tabular data. Supports B3 over deep tabular models |
| N33 | GPBoost, Sigrist, *JMLR* 2022 (AB) | Boosting with grouped random effects (person). A strong repeated-measures baseline (B3) |
| N34 | Attention-based MIL, Ilse et al. 2018 (FD); "Rethinking EEG-Based Disease Diagnosis: decoupling instance representation learning from subject-level supervision", arXiv 2607.27274, 2026 (SN) | **Unconstrained learned temporal pooling** with recording-level labels. Our main deep baseline (B4b) and the key contrast to anchored pooling |

### F. Fusion, missingness, nuisance and shortcut robustness

| ID | Work (tier) | Relevance |
|---|---|---|
| N35 | MultiModN, Swamy et al., NeurIPS 2023 (AB) | Sequential modular fusion robust to MNAR missingness, including education tasks. Missingness-robust fusion is occupied |
| L11 / L12 | ICYM²I (ICLR 2026); QA-MoE (IJCAI 2026) (inherited) | Missingness-distorted modality value; quality-aware MoE. Quality gating is not our contribution |
| N36 | Zhao, Adeli & Pohl, *Nat Commun* 2020, confounder-free training (BR-Net) (AB) | Adversarial independence from confounders. Optional regularizer; ablation only |
| N37 | Geirhos et al., *Nat Mach Intell* 2020, shortcut learning (FD) | Framing for content-identity and quality shortcuts |

### G. Alternatives to peer references (stimulus-tracking)

| ID | Work (tier) | Relevance |
|---|---|---|
| N38 | Neural tracking / TRF studies linking EEG tracking of the speech envelope to comprehension, e.g. Vanthornhout et al. (bioRxiv 421727, SN) | Encoding-model reference instead of peers. EEG branch extension; needs the stimulus audio |
| N39 | Video saliency SOTA: ViNet-S/-A (2025), SalFoM, CASP-Net (2023) (SN/AB) | A stimulus-predicted gaze reference for regime B. Needs the video frames |
| N40 | Educational content linking for MOOC remediation (arXiv 2012.15826) (SN) | NLP precedent for linking questions to video segments. Our anchoring protocol is not novel as NLP |

### H. Datasets assessed for pretraining, auxiliary use or external validation

| ID | Dataset (tier) | People / content | Signals | Outcome | Licence / access | Recommended role |
|---|---|---|---|---|---|---|
| — | **John 2025** (OSF 4rn5q; FT, our replication) | 112 / 1 video (16 min) | EyeLink 500 Hz; cEEGrid ear-EEG (not downloaded) | 7-item pretest, 13-item posttest | CC-BY 4.0 | **Untouched external validation, restricted.** Never used for pretraining or tuning. Item anchoring needs the posttest item texts (unverified) |
| N41 | **Lallé green chemistry** (GitLab mocah-public; N16 for N) | 70 (53 with quiz per the delegated listing) / 1 video (7.5 min), self-paced | Tobii ~60 Hz | 15 items mapped to segments; per-item "already knew" (delegated listing; verify) | Only a BSD-3 *software* licence; data terms unclear | **Primary external test of the item-level effect**, including an item-specific prior-knowledge control, once terms are clarified. **[S0-1]** No per-item "already knew" found (`PriorKnowledge` is a person-level fairness attribute in the code). N = 70 over two cohorts (2023: 19 items; 2024: 15 items). Free (Panopto) viewing. Item content spans are in the code |
| N42 | **Madsen 2021 classroom / at-home webcam** (OSF m7gj4; listing verified via API) | Classroom 82 / at-home 1,012 (P01); per-video webcam gaze `data_eye`, `T_answers`, `T_demographics` files | Webcam gaze | Per-video answers; item granularity **unverified** | No licence on OSF | Cross-sensor transport and large-N item-difficulty evidence. **Not independent content** (same videos, same lab) |
| N43 | **HBN-EEG** (Shirazi et al., bioRxiv 2024.10.03.615261; AB) | Thousands of children / 4 videos incl. *Fun with Fractals* | 128-ch EEG + 120 Hz eye tracking | None relevant | Verify the licence | Optional label-free pretraining of the encoder; ablate |
| — | Bühler 2024, Bodonhelyi 2026 | — | — | — | Not released | Not usable now |

### I. Added in Stage 0 (2026-10-13) [S0-1]

| ID | Work (tier) | Relevance |
|---|---|---|
| N44 | Lan, Brinton, Yang & Chiang, "Behavior-Based Latent Variable Model for Learner Engagement", EDM 2017 (AB) | Clickstream engagement per video → latent knowledge → in-video quiz responses. The closest **psychometric** analogue; one engagement value per video, not per moment or item, and behavioural logs only |
| N45 | COIVis, Zhou et al., *IEEE TVCG* 32(7), 2026; arXiv 2512.06834 (AB) | Concept-of-interest alignment of gaze in MOOC videos; descriptive visual analytics |
| N46 | SAVVY, Zhou et al., arXiv 2607.29413, 2026 (AB) | Attention visualization from multimodal signals for teachers; descriptive |
| N47 | AttentiveLearn, Liu, Feick, Bierhoff & Maedche, CHI 2026; arXiv 2603.05324 (AB) | Gaze-personalized post-lecture quizzes in VR; no learning gain shown |
| N48 | Bodonhelyi et al., arXiv 2604.09569, 2026 (AB) | Mind-wandering review and multimodal benchmark (14 datasets); no item-retention target |
| N49 | Madsen, Kuppa & Parra, BBBD, *Scientific Data* 2026; PMC13284221 (FT) | Stimulus table with YouTube durations; **no trim information**; Enzymes listed with one source only |
| N50 | Cao, Sweetser, Chen & Zhu, CHI 2026; arXiv 2603.18798 (AB) | Ocular / cardiac early performance prediction in a game; not video learning |
| N51 | LEXIC, arXiv 2607.08152, 2026 (AB) | Source of the earlier "text-aware 56–63%; gaze-only chance" summary of EyeBench (superseded by N09 FT) |

## 3. What the literature establishes, and what it leaves open

**Established (do not claim):**

1. Synchrony and gaze relate to learning at the whole-video level (P01–P04; L01–L09; our G01-R and John results).
2. Engagement at specific moments relates to memory for those moments, in explanatory analyses: N01, N03, N04, L08.
3. Item-level comprehension can be predicted from gaze **in reading**, only with content-aware models (N08, N09).
4. Attention can be detected in educational video from gaze with dynamic AOIs (N15, N16), and ISC can be estimated without a reference cohort (N06).
5. IRT with person-by-item covariates is standard (N17).
6. Generic EEG/ECG/time-series foundation models give limited low-data gains (N20, N21). Generic multimodal SSL, missingness-robust fusion and quality gating are occupied (L11, L12, L25, L30, L31, N35).

**Not found** (bounded search; the N15/L08 full-text risks apply). No predictive, leakage-safe model for **video learning** that:

- **(a)** anchors physiological engagement to the content each quiz item tests, with anchors derived outcome-blind from item text;
- **(b)** represents engagement relative to the stimulus-locked peer distribution, deployable with unlabelled peers on new content;
- **(c)** decomposes item correctness into person, item and person × moment components, so the moment effect is identified within person and immune to person-level and content-identity shortcuts;
- **(d)** builds falsification into evaluation: shuffled or circularly shifted anchors; localized versus diffuse items; in-window versus out-of-window data loss;
- **(e)** is evaluated on new learners, new content and a locked new-protocol cohort, with external replication.

Each ingredient has precedent. Their combination into a falsifiable predictive measurement model is the proposed contribution ([research plan §8](research_plan.md#8-precise-novelty-argument)).

**[S0-1] After the close-out:**

- **(a)** is partly occupied by N15. It anchors item retention to content windows with held-out learners, but without outcome-blind, reliability-gated anchors.
- **(b)–(e)** remain unoccupied.

## 4. Implications for the method choice (evidence → consequence)

| Evidence | Consequence |
|---|---|
| EyeBench: gaze-only item-level prediction at chance; text-aware 56–63% AUROC (N09, SN). **[S0-1] FT:** text-only 61.1 vs text + gaze 61.9–62.9 | ~~Anchoring is necessary, not decorative~~ **[S0-1]** Item knowledge explains most item-level performance. Gaze increments are small (about 1–3 AUROC points). **Item-level claims must be increments over an item-only baseline** (ΔAUC_wp vs IRT-M2), and effects are expected to be small |
| EEG-FM benchmarks: limited low-data cross-subject gains (N20, N21) | EEG FMs are a baseline tier, not the method |
| VLM attention detection fails to beat statistical baselines (N16) | Generic large models do not remove the need for task structure |
| Davidesco 2023: segment–question linkage feasible by transcript; association found (N01) | Anchoring protocol feasible. The predictive, inductive version is open |
| TabArena / TabPFN / GBMs strong on small tabular data (N30–N33) | The whole-video baseline tier must include them, or a gain over ridge alone is not credible |
| MIL learns pooling from recording labels (N34) | Unconstrained learned pooling is the decisive deep baseline for "anchors versus learned attention" |
| Silvan Ortubay 2024: reference-free ISC estimation (N06) | Reference distillation is a supporting component, not the headline |
