# Prior work: original-paper evidence dossiers

Evidence cutoff: **2026-10-01**. Four empirical papers are confirmed to analyze subsets of this collection; S01 is the descriptor, not a fifth independent cohort. P05 is a verifiable publication but its dataset use/methods remain unresolved. Preprints, posters and renamed versions are deduplicated. [Full citations, access limits and code links](evidence/source_registry.md); [search protocol](evidence/search_log.md); [matrix](prior_work_matrix.md).

“Prediction” in a paper can mean an in-sample statistical association, a held-out physiological mapping, or held-out behavioral forecasting. These are recorded separately. A p-value or same-cohort correlation is not an out-of-sample error estimate. We have not rerun any paper.

## P01 — Madsen et al., PNAS, 2021

**Citation:** *Synchronized eye movements predict test scores in online video education*, 118(5):e2016980118; [original article](https://pmc.ncbi.nlm.nih.gov/articles/PMC7865179/).

| Extraction field | Original-paper evidence |
|---|---|
| Dataset subset / participants | Laboratory experiments 1–3 map to BBBD 1–3: reported cohorts 27, 31, 30, with metric-specific exclusions. The article reports 1,182 total including separate classroom 82 and at-home 1,012 samples. Its enrollment/exclusion wording is not a clean release-flow chart; retain analysis-specific N. Current BBBD 3 has 29. |
| Modalities | Eye position X/Y and pupil for lab; webcam eye position/velocity for separate classroom/home experiments. |
| Question / target | Does synchronous looking change with distraction and relate to immediate test accuracy, across intentional/incidental learning, video styles and question types? |
| Preprocessing | EyeLink 500 Hz, calibration, blink/artifact removal with 100 ms buffers and interpolation; pupil luminance-regression sensitivity described in main text but supplement not retrieved. Webcam stream has different quality and preprocessing. |
| Segmentation/windowing | Video-length aligned time series for individual ISC; averages over videos/participants where stated. Frequency-specific fifth-order Butterworth analysis (bandwidth proportional to center frequency), rather than a supervised fixed-window classifier. |
| Features/representations | Per-subject pairwise Pearson correlations averaged against other viewers, then mean of horizontal, vertical and pupil ISC. Webcam extension correlates with median gaze and combines horizontal/vertical/velocity correlations. |
| Models | Repeated-measures ANOVA; threshold ROC; Pearson correlations with quiz; nonnegative weighted ISC with weights summing to one in webcam extension. |
| Validation | Laboratory replication across cohorts/styles and within-subject condition tests. Lab ROC is descriptive within the available cohorts. Webcam weighting fitted with leave-one-subject-out validation. No documented strict joint unseen-person/unseen-video BBBD quiz benchmark. |
| Metrics/results | Lab attention ROC AUC **0.944 ± 0.033** (mean/SD over videos); video-wise quiz correlations **r=0.61 ± 0.06**. Intentional vs incidental quiz relations **r=.61 and .58**. Classroom/home correlations and 14.6% median prediction error belong to those separate collections, not the current BBBD release. |
| Author-reported limitation | Observational relationship does not establish what causes ISC–performance correlation; changing testing delay and motivation complicates intentional/incidental comparison. |
| Our inference / validation risk | Pairwise references use the available cohort and condition-specific groups. A future inductive classifier cannot select an attended/distracted reference using an unknown test label. Median/group-reference construction also needs a train-only or explicitly transductive definition. This does not automatically invalidate the original descriptive analysis. [INF-021] |
| Code / reproducibility | OSF m7gj4 figure-analysis resources; fjxaq materials/questions; GitHub elicit-experiment online code. OSF root verified, full execution not attempted. SI Appendix access failed. Historical-to-1.1 subject/label mapping remains necessary. |
| Modalities/questions not used | No BBBD EEG/ECG/respiratory fusion, missing-modality stress test or prospective deployment assessment. No demonstrated long-term retention outcome in these BBBD experiments. |

## P02 — Pérez et al., Cell Reports, 2021

**Citation:** *Conscious processing of narrative stimuli synchronizes heart rate between individuals*, 36(11):109692; [original PDF](https://par.nsf.gov/servlets/purl/10295211).

| Extraction field | Original-paper evidence |
|---|---|
| Subset / participants | Only its Experiment 2 maps to BBBD 2: 31 recruited, 27 ECG analyses after four poor recordings. Other auditory/clinical cohorts are outside BBBD. |
| Modalities / target | ECG-derived HR; attention-condition modulation of cardiac synchrony. |
| Preprocessing | 2,048 Hz ECG, filtering, R-peak detection/correction, inverse-RR HR interpolation onto a common time base. |
| Segmentation / features | Five video-length records; pairwise HR ISC against attentive references, frequency-resolved correlations; mean HR and variability summaries. |
| Model / validation | Repeated-measures ANOVA, paired contrasts, circular-shift nulls and frequency tests; no supervised held-out behavioral predictor for this BBBD subset. |
| Metric / main result | Attention effect **F(1,104)=70.64, p=6.93×10⁻⁹**; ISC decreased in 26/27 viewers on averaging videos. |
| Limitations / unused modalities | Fixed-order repeated viewing remains; no EEG/eye fusion. The paper's cardiac–recall association belongs to another cohort and cannot establish that result for BBBD 2. |
| Code / reproducibility | OSF mhvy7 contains healthy-participant data and analysis code; root listing verified. STAR Methods read, separate supplement not retrieved. No numerical replication. |
| Unanswered question | Does cardiac information improve unseen-person/video quiz prediction beyond eye/EEG/trait controls? |

Sources: original Results “Attention modulates synchronization … audiovisual narratives,” Figure 3 and STAR Methods; lineage corroborated by P03. The counterbalanced auditory experiment elsewhere in P02 does not remove the order confound from its BBBD video cohort.

## P03 — Madsen & Parra, PNAS Nexus, 2022

**Citation:** *Cognitive processing of a common stimulus synchronizes brains, hearts, and eyes*, 1(1):pgac020; [original article](https://pmc.ncbi.nlm.nih.gov/articles/PMC9802497/).

| Extraction field | Original-paper evidence |
|---|---|
| Dataset subset / participants | Its Experiment 1: 96 recruited/92 retained, corresponding to historical BBBD 4+5 (43+49). Its Experiment 2: 32/29, BBBD 3. Its Experiment 3: 31/29, BBBD 2. Written total 158 differs from sum of recruitment counts 159. Use per-analysis N. |
| Modalities | EEG, ECG→HR, gaze, pupil, respiration, saccade rate, head movement; EOG for cleaning. |
| Question / target | Does shared cognitive processing synchronize multiple signals, does synchrony co-vary across modalities and predict quiz performance, and does EEG linearly predict body signals? |
| Preprocessing | EEG 0.05 Hz high-pass, 60 Hz notch, robust PCA, low-pass/downsample to 128 Hz, channel interpolation and EOG regression, four-IQR/±40 ms outliers; native eye tracking 500 Hz with blink/artifact interpolation; R-peaks→HR. |
| Segmentation/windowing | Full aligned videos; **10-second windows with 50% overlap** for temporal ISC; fifth-order Butterworth bands with logarithmic centers and bandwidth 0.2×center for frequency analyses. |
| Representations | EEG correlated component analysis (CorrCA), sum over 3–9 significant components depending on experiment; pairwise ISC of body/eye signals; standardized cross-modality ISC and PCA. Within-subject correlation (WSC) measures EEG-to-body predictability. |
| Models | CorrCA; ordinary least-squares EEG→physiology mapping; PCA of multimodal ISC; Pearson quiz association; paired/cluster-permutation inference. |
| Participant validation | **WSC uses leave-one-subject-out fitting**, then correlation on the held-out subject. This is real person-independent physiological prediction, not an unseen-person quiz evaluation. |
| Stimulus validation | EEG component significance uses **two videos for training and one for testing**, with circular-shift tests on held-out data. Other condition contrasts fit components using both conditions; PCA/quiz associations are cohort-level analyses. |
| Metrics/results | PC1 explains **52%** of ISC variance (PC2 22%). PC1–quiz **r(39)=.59, p=5.7×10⁻⁵**, 41 complete-eye cases among 43 quiz cases. Individual quiz correlations: EEG .57, gaze .60, pupil .51, HR .30 (p=.05), respiration .01 (p=.94). EEG/HR/eye measures show shared synchrony; respiration/head do not show comparable evidence in the reported analyses. |
| Author-reported limitations | Common processing does not settle specific psychological mechanisms or direction of brain–body effects; people were recorded separately, limiting claims about direct social interaction. |
| Our inference / validation risk | PCA across modality ISC is already a form of multimodal combination; linear cross-modal prediction and temporal dynamics are already studied. PCA/quiz correlation does not establish incremental held-out benefit. Coupling may include common drive/residual artifacts; distinct validation schemes answer different questions. [INF-022] |
| Code / reproducibility | Lab links OSF d4k3q; CorrCA/ISC tools public. OSF root index verified (data/code/figures); full pipeline not run. Supplement unavailable. Historical 92-person and corrected 91-person release sets require mapping. |
| What it did not establish | Missing-modality robustness, modern contrastive/teacher–student learning, joint unseen-person/unseen-video outcome forecasting, causal brain→body interpretation, or corrected-release replication. |

No single “accuracy” can summarize this paper: variance explained, correlation, shuffle significance and attentional effect size are different metrics. Report each with its proper unit of analysis.

## P04 — Madsen & Parra, iScience, 2025

**Citation:** *Attentional state, not trait, predicts test performance in video-based learning*, 28(10):113622; [original article](https://pmc.ncbi.nlm.nih.gov/articles/PMC12538096/). The lab webpage uses a variant title (“State and trait measures …”); DOI identifies the same paper. CNS 2026 poster is repeat dissemination.

| Extraction field | Original-paper evidence |
|---|---|
| Subset / participants | BBBD 2–5, **152** historical participants (31/29/43/49), 93 female, ages 18–57, mean 25.58. Current release has one fewer Exp. 5 participant. ASRS 149; digit span 147; GPA observed 110, 13 median imputations in 123 eligible, 29 noncollege exclusions. |
| Modalities / unused signals | EEG plus EOG nuisance removal; GPA, ASRS and reverse digit-span scores. Explicitly no cardiac, respiratory or eye-signal outcome analysis. |
| Question / targets | Relative contributions of acute EEG synchrony, working memory, GPA and attention-related self-report traits to immediate quiz performance; trait association with EEG ISC and GPA. |
| Preprocessing | EEG 0.5 Hz high-pass (different from S01/P03), 60 Hz notch, robust PCA, low-pass64/downsample128, bad-channel interpolation, EOG regression and four-IQR/±40 ms corrections. |
| Segmentation / representation | Attentive video/block-level EEG ISC, first five CorrCA components; no learned windowed sequence model. Only nonintervention segments are stated to be used from 4/5; align exact quiz chronology separately. |
| Models | Binomial GLMM: quiz ~ GPA + WMC + ASRS inattentive/hyperactive + ISC1…5 + random intercept for experiment, with total possible answers supplied. Normal mixed model for ISC1 from traits; GPA normalized/clipped to[0,1], modeled with logit link and normal distribution. |
| Validation protocol | Condition comparison in 60 people; spatial filters transferred across cohorts. Methods alternately say filters trained on Experiment 3 and, for quiz/mediation, attentive Experiment 2; numbering needs reconciliation with code. No reported held-out behavioral prediction/test-error protocol. Experiment random intercept is not leave-one-experiment-out validation. |
| Metrics/main result | Quiz model: ISC1 **t(109)=4.11, p=7.67×10⁻⁵**; GPA **3.41, p=.0009**; WMC **3.374, p=.001**. WMC→ISC1 **t(142)=2.707, p=.0076**; inattention→GPA **t(115)=−2.14, p=.034**. Nonsignificant other trait coefficients are not proof of no effect. |
| Author-reported limitations | Immediate retention only; brief single-session stimuli; unknown long-term transfer/long-form generalization; variation in motivational appeal; self-reported/absent GPA. |
| Our inference / risks | Directional mediation requires assumptions not established by observational data. Aggregate experiment effect does not guarantee adjustment for stimulus/item difficulty. Binomial counts require compatible score semantics, especially partial-credit penalties. Release correction postdates publication; its impact on the original analysis is unknown. [INF-016, INF-023] |
| Code / reproducibility | OSF u72k3 provides spatial filters and Figure 1–3 MATLAB code/helpers; names verified through API. Full coefficient supplement inaccessible; no execution. Reproduction should pin original analysis inputs and separately test corrected 1.1 inputs. |
| Unanswered questions | Incremental ECG/eye/respiration information conditional on EEG/traits; robust forecast to new people/content; handling actual missing channels; generality of the observed associations under corrected labels. |

This paper rules out presenting “physiology predicts learning rather than condition labels” or “EEG plus participant traits predicts quiz performance” as untouched topics. The narrower prospective/generalization and modality-complementarity questions remain candidates, not proven gaps. [INF-024]

## S01 — dataset descriptor and its technical validation, 2026

S01 documents 178 retained participants and the released modalities/format; its technical validation uses spectra and within-person paired condition tests rather than a learned classifier. EEG alpha is higher during distraction, **t(57)=5.32, p=9.7×10⁻⁷, d=.7**. It reports cardiac, eye and respiratory summaries, with raw/processed availability and known16 Hz contamination. The public notebook supports reproduction in principle but contains statistic/provenance discrepancies detailed in the [code audit](evidence/code_audit.md): the labeled HRV formula and pupil-IQR interpretation are especially important. Do not treat the descriptor as an independent confirmation using new people, or its technical checks as complete artifact/QC certification.

## P05 — Rathnayake et al., IEEE SCSE, 2026: unresolved methods lead

[Publisher DOI](https://doi.org/10.1109/SCSE70081.2026.11499773); [saved publisher metadata](evidence/ieee_publisher_metadata.json). Published March 26,2026, pp.1–6. Discovery through dataset-associated citation listings and exact-title searching. IEEE returned no usable full text; Crossref has no abstract. Search-result adjacent text sometimes reproduces the BBBD descriptor and is not reliable evidence about P05's methods.

| Required extraction field | Current status |
|---|---|
| Dataset subset; participants; actual modalities; research question beyond title; target coding | **NOT VERIFIED** from original paper |
| Preprocessing; segmentation/windowing; features; models; validation; metrics; main numerical result | **NOT VERIFIED** |
| Limitations; code; reproducibility; unused modalities; unanswered questions | **NOT ASSESSABLE** without methods/code |

Do not count P05 as confirmed BBBD reuse, dismiss it, or claim novelty in attention classification until the original paper is obtained. Its title alone suggests a potentially relevant competitor. Companion review R03 is bibliographic context, not a verified second empirical analysis. No author contact was made.

## Related work and exclusions from this collection

- **R01 (2024 Cell Reports):** brain–body directionality during auditory stories, separate 29+38 cohorts with control conditions. Relevant to temporal/cross-modal mechanisms; not a BBBD video experiment. Avoid claiming brain–body temporal modeling is globally new.
- **R02 (CNS 2026):** P04 poster/abstract; deduplicate.
- **R04 (2023 eye synchrony):** independently recruited Zhejiang students, different video/setup. Provides a construct-validity comparison, not BBBD participant reuse.
- **R05 (2023 narrative dynamics):** fMRI movie/rest/scrambled cohorts, not BBBD.
- **Explanation-video classroom study (Adler et al., 2025):** [original article](https://doi.org/10.1007/s10639-024-13292-9), 139 CCNY physics students and 215 online participants; matched classroom videos and before/after quizzes. Distinct collection. Its inconsistent attention–performance relationship is relevant external context; not another BBBD finding.
- **2025/2026 brain–body dynamics preprint:** [author-linked DOI](https://doi.org/10.64898/2025.12.22.696055) describes auditory narratives/rest; accessible author materials should be checked before temporal-mechanism novelty claims. Full preprint access status is recorded in the search log.

Cohen et al.2018 educational EEG and Ki et al.2016 attention manipulation are methodological ancestors cited by these papers. Shared stimuli or authors alone do not prove shared participants. They are not counted as BBBD reanalyses without an explicit lineage match. This review is a reasonably traceable dataset-focused search, not a systematic review of all physiological attention research.
