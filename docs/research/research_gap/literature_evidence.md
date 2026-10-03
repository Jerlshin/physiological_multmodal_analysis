# Literature synthesis and novelty challenges

2026-10-03. **L** denotes findings/claims in external literature; **I** denotes our interpretation for this project; **U** denotes an unresolved comparison. IDs link to the [bibliography/access register](bibliography.md). The original P01–P05 dossiers remain authoritative for historical BBBD analyses. Reported results are not replicated here.

## The scientific gap is narrower than “physiology predicts learning”

**L: P01–P04, L01–L09, L42.** Eye and EEG synchrony have been associated with quiz performance; multimodal synchrony and a joint component have been related to quizzes; traits and EEG have been modeled together. Outside BBBD, neural alignment, gaze measures and EEG learning-outcome classifiers already exist. P03 includes held-out linear brain-to-body prediction and a specific video-held-out CorrCA analysis; L42 reports subject-held-out EEG classification. Therefore neither first physiological prediction, first multimodal contribution, first cross-subject experiment nor first use of video holdouts is defensible.

**I.** A potentially useful question concerns the *conditions under which an outcome measure is valid*: whether adding physiological channels improves individual quiz estimation beyond readily available covariates, under declared reference-cohort access, content transfer and measurement failure. This is a measurement/transport question, not a claim that cross-validation itself is novel. Its journal strength depends on resolving an empirically important contradiction and validating the resolution beyond one small release.

## Closest educational and construct-validity competitors

| Source and evidence tier | What is established or explicitly investigated | What our formulation must not claim | Remaining distinction / limitation |
|---|---|---|---|
| P01, RR; PNAS 2021 | Gaze/pupil synchrony and tests in lab plus outside-lab studies; webcam prediction precedent | First ocular learning measure or first practical extension | Current audited BBBD outcome population differs; new work must establish incremental validity and declare references |
| P02, RR; Cell Reports 2021 | Cardiac synchrony under attention manipulation; recall in other cohorts | First cardiac attention/memory finding | Do not assign other-cohort recall results to BBBD Exp.2; that experiment's released behavior is excluded |
| P03, RR; PNAS Nexus 2022 | Multiple physiological synchronies, their shared component and quiz association; held-out cross-modal prediction | First brain–heart–eye fusion, temporal dynamics or cross-modal mapping | Association of a pooled/shared component is not an assessment of all requested deployment risks |
| P04, RR; iScience 2025 | EEG synchrony, traits and immediate test performance; state-versus-trait framing | First evidence beyond ASRS/WMC/GPA or first state/trait contrast | Current question needs participant/content/availability-specific out-of-sample criteria; no common prior-knowledge adjustment is possible in eligible BBBD |
| L03, FT; Adler 2025 | Classroom and online explanation-video studies with academic performance and gaze measures; learning–attention results vary by setting | First warning that synchrony does not consistently predict learning | Supports the importance of boundary conditions, but our proposed explanation remains untested |
| L04, FT; Bühler 2024 | 84 quality-retained learners, thought probes, gaze synchrony and posttest; pretest-adjusted regressions | First distinction between measured attention and learning | Synchrony references are grouped using known probe responses for explanatory analysis; not a deployable unknown-state reference rule |
| L05, IX; Sauter 2022 | Webcam synchrony/quiz replication with unreliable sampling, three videos/27 participants in indexed original | First quality-related failure of a learning biomarker | BBBD has richer joint physiology and recorded quality variation, but that alone is not methodological novelty |
| L06, IX; Liu 2023 | Direct independent examination of gaze synchrony and attentional engagement | Universal monotonic “more synchrony means better learning” assumption | Full original methods still need retrieval for a detailed contrast; do not rely on secondary discussion as fully audited evidence |
| L07, FT; John 2025 | Multiple meaningful gaze foci; cluster membership and post-knowledge regression controlling prior knowledge/missing gaze; temporally annotated programming content | First heterogeneous attention measure, first missing-gaze covariate, first content-relevant analysis | One instructional video; reported analyses are explanatory. It is a necessary reference-assisted comparator and an external-data lead, not an obsolete ISC straw man |
| L08, IX; Chen 2026 | Different prior-knowledge/neural-similarity relationships across individuals versus events, with different learning associations | First separation of within/between-person effects; first challenge to a universal similarity–learning relation | Full methods not obtained; BBBD lacks matching baseline knowledge/event labels. Strong novelty risk remains until read |
| L09/L43, PA/IX; Gu 2024 / De Felice 2025 | Instructor presentation or social gaze changes multimodal synchrony–learning relationships | General claim that context-dependent brain–eye relationships are unstudied | fMRI/social fNIRS designs supply stronger contextual manipulations than BBBD; BBBD cannot inherit their mechanistic interpretation |

**I.** Contradictory studies are not proof that the earlier BBBD associations are artifacts. Different stimuli, outcomes, constructs and measurement quality can all change results. BBBD can test a subset of these explanations; it cannot identify prior-knowledge mechanisms or resolve the entire attention–learning theory.

## Missingness, reliability and calibration: substantial novelty already occupied

**L11 — ICYM²I, FT, ICLR 2026.** The paper explicitly treats missing modalities as distribution shift that distorts estimated predictive and information-theoretic modality value. Its double inverse-probability weighting adjusts both training and evaluation under stated MAR and positivity assumptions. The target is value if modalities were fully observed; its examples include ECG/chest radiographs, other multimodal benchmarks and synthetic data. MNAR sensitivity is discussed. This is the closest methodological competitor to any proposed “selection-corrected modality utility” paper.

**I.** Continuous quality, physiological data or BBBD do not negate L11's priority. The defensible distinction would be an observed available-sensor policy evaluated for all eligible outcome-observed learners, plus a separate analysis of selection sensitivity. Such a risk can be evaluated without recovering missing waveforms under the same observed-data distribution; this does not identify hypothetical fully measured utility or guarantee deployment transport. That prediction/inference distinction is itself established (L14), not our new theorem.

**L12 — QA-MoE, FT, IJCAI 2026.** Separates reliability estimation from routing and selects useful modalities under noise/missingness in clinical tasks. Learned evidential quality, sparse subset selection and robust fusion are explicit contributions. **I:** merely adding quality gates or an MoE to BBBD is not enough. Missing-data distributions and continuous tracking corrections need a scientific estimand and external evidence; quality gates may otherwise exploit experiment identity.

**L13 — MC², FT, MLMI 2026 workshop.** Calibrates by modality-availability pattern using Mondrian conformal prediction, with within-pattern exchangeability assumptions. Its experiments expose conditional coverage problems when calibration and test availability differ. **I:** “first calibrated missing-modality model” is unavailable. BBBD adds repeated people/crossed content and tiny pattern-specific calibration sets; those are validity obstacles, not automatic novelty. Neither pattern conditioning nor a nominal 90% label establishes coverage under arbitrary protocol shift.

**L14–L16, L40–L41.** Predicting with incomplete covariates, hierarchical repeated-measure inference, nonexchangeable conformal analysis, fairness and mask-conditional coverage have independent statistical literatures. Josse et al. explicitly distinguish prediction from parameter recovery, with assumptions for consistency; Lee et al. handle repeated-measure hierarchy. The similarly titled arXiv:2411.13479 concerns linear aggregation hierarchies and is **not** the appropriate repeated-person theorem. No theorem from these sources is asserted to cover BBBD's crossed person–content–missingness design without further analysis.

**L38–L39.** iMML and ICCV missing-modality work further occupy broad incomplete-data methodology. “Unbiased recovery” and unbiased population modality value can be different targets. A fair comparison must match the target and assumptions, rather than listing methods with similar names.

## Privileged sensors and reduction: no first-distillation claim survives

| Source | Existing scope | Consequence for a BBBD contribution |
|---|---|---|
| L17, ICASSP 2016, IX | EEG privileged at training; CCA maps peripheral features for test-time peripheral emotion recognition | EEG-to-peripheral privilege is at least a decade old |
| L18, ACM MM 2021, IX | Eye-only input generates multimodal emotion features | EEG-free eye deployment is established |
| L19, ACM MM 2023, PA | EEG/GSR multimodal teacher to GSR student, adaptive feedback | Adaptive physiological KD is established |
| L20, CMCRD 2025, FT | Contrastive EEG/eye distillation; correctness/confidence guidance; LOSO; both transfer directions | Cross-subject EEG→eye and suppressing harmful teacher guidance are direct competitors |
| L21, PhysioGMC 2026, FT | Clinical ECG/ABP plus wearable PPG during training; PPG only at test; label-relevant versus subject-specific representations; subject-disjoint evaluation | Sensor reduction combined with subject invariance and contrastive learning is already occupied |
| L22, PULSE v3 2026, FT | Frozen privileged teacher; shared/private decomposition, multilayer matching, reconstruction; WESAD and STRESS | This exact collection of familiar ingredients cannot be advertised as new. Per-person baseline normalization also defines an access regime to match |
| L23, BioKD 2026, FT | Selective physiological-to-video distillation with reliability gating, emotion datasets | Reliability-aware physiological teaching is occupied even outside sensor-to-sensor transfer |
| L24, EDM 2026, FT | Privileged think-aloud/observer information trains a behavioral-log cognitive-state model; participant folds, quality groups | First LUPI in learning/education is unavailable; quality-stratified teaching is also precedent |

**I.** A remaining scientific question is whether a privileged EEG teacher transfers *individual behavioral information* rather than shared stimulus/protocol/quality structure. This needs direct student-only supervision, CCA and ordinary KD baselines, matched data/training budgets, out-of-fold teachers and nuisance-preserving teacher controls. BBBD has no validated wearable PPG/webcam stream, and removing the cap does not make EyeLink a low-cost home sensor. “Brain information transferred” would overstate what behavioral improvement can identify.

## Representation learning and foundation models: use as tools, not the gap

**L25, FT.** PhysioOmni already combines shared/private physiological tokenization, masked pretraining and arbitrary missing-modality handling. Its corpus includes public and private sources; splits vary by downstream dataset. The EEG/ECG sampling and scaling requirements differ from BBBD exports. **I:** do not silently resample unknown-unit data into a checkpoint or call self-supervision on held-out BBBD people inductive evaluation. A private corpus is a lineage uncertainty, not proof of contamination.

**L26–L29.** BIOT handles heterogeneous biosignal inputs; SleepFM uses multimodal self-supervision and explicit supervised comparators; CBraMod/REVE are established EEG baseline families. Their source tasks and data scale do not establish educational validity. BBBD is not adequate for training a general-purpose foundation model from scratch.

**L30–L31.** FactorCL and CoMM explicitly challenge redundant-only alignment and model shared/unique or synergistic task information. **I:** “preserve modality-specific information” and shared/private modules are insufficient novelty. With only dozens of people per protocol, apparent high-dimensional mutual-information/PID estimates would require stronger estimator validation than an ablation accuracy difference.

**L32–L34, PA, 2026 preprints.** Current work already evaluates EEG foundation models across low-resource conditions, probes their encoded features, and tests dataset identity/random initialization controls. L34's current v3 title and five-model scope supersede its earlier search-index title. **I:** adding BBBD to a foundation-model leaderboard or showing embeddings recognize experiment is weak as a standalone paper. Useful contributions must explain a learning-measurement failure and demonstrate a remedy or a precisely bounded impossibility/limitation beyond this one dataset.

## Generalization is a research question only when the target changes meaningfully

**L35–L37.** Cross-context mind-wandering detection, MMLA generalizability frameworks and physiological learning fusion predate this project. Existing BBBD papers already use particular person/content holdouts. **I:** the contribution cannot be “we finally use LOSO.” It can be a demonstrated boundary between known-content/reference-assisted association and learner-specific validity on new content, with matching baselines and honest uncertainty. Three or six held-out videos are not a large population of domains.

## Candidate-specific novelty verdict

| Candidate | Closest threats | Defensible residue | Verdict |
|---|---|---|---|
| G01 individual behavioral validity | P03/P04; L03–L09; L36/L42 | Crossed content/person and reference-access-specific incremental evidence, tested against measurement selection and score semantics | Strongest scientific framing; novelty conditional, external replication needed |
| G02 selective measurement validity | L05/L07/L11–L16/L38–L41 | Whether actual censoring changes who receives valid predictions, and whether available-sensor policies retain useful criterion validity | Strong relevance; generic missingness/calibration contribution already occupied |
| G03 privileged reduction | L17–L24/P03 | Identifying when a teacher's behavioral contribution survives removal rather than copying nuisance structure | Method room but high collision risk; subordinate until G01 establishes useful EEG evidence |
| G04 bounded protocol transport | P03/P04/L03/L08/L35 | Same-content transport across the actual single/repeated-exposure bundles, with domain-specific uncertainty | Scientifically useful boundary test; only three shared videos, weak standalone generalization claim |
| G05 representation beyond common stimulus | L10/L21/L25/L30–L34 | Outcome-specific preservation under precisely specified access and nuisance controls | Merge into G01/G03; insufficient standalone novelty/data |
| G06 score-definition robustness | Existing quiz scoring/psychometric methodology; P04's outcome model | Whether a claimed physiological learning result depends on partial versus exact-set definition | Essential validation; no general psychometric theory identified here |
| G07 missing-modality calibration theorem | L13/L15/L16/L40/L41 | A genuinely new crossed-cluster theorem would need a separate mathematical project | Too little BBBD calibration data; not the primary empirical paper |
| G08 temporal encoding of quiz items | P03/L07/L08 | Potentially meaningful with item timestamps and native timing | Unsupported by current audit; reject as BBBD primary |

No claim of “no prior work” is justified. The recommendation is a conditional scientific validation program, with methods chosen only after the competing explanations and attainable precision are specified.
