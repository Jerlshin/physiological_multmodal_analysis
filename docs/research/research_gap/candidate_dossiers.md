# Serious-candidate dossiers

2026-10-03. Eight questions received detailed screening. Four are shortlisted. **F** refers to [audited facts](audit_contract.md); **L** to the [source register](bibliography.md); **I/H/U** distinguish interpretation, proposed hypothesis and unresolved evidence. Every statistical/methodological proposal below is unimplemented. Counts are ceilings under existing provisional QC, not power calculations or certified unique-human counts.

## G01 — Incremental individual validity across people and content

**Research question (H).** At the end of an educational video, do EEG, ECG and ocular measurements improve estimates of an individual's immediate quiz performance beyond permissible nonsignal predictors, and under which content/reference-access conditions does this improvement persist?

**Scientific motivation (I).** A group-level physiological response to a video can be reproducible without being an informative individual learning measure. Establishing this distinction matters before physiological feedback, personalization or sensor deployment is justified. Immediate quiz criterion validity remains narrower than learning gain.

**Established literature (L).** P01/P03 demonstrate gaze/multimodal synchrony–quiz associations; P04 combines EEG and traits. L03–L09 show contextual variability, negative/qualified synchrony findings, alternative gaze-cluster measures, and prior-knowledge/neural-similarity interactions. L42 already reports cross-person EEG learning-effect classification. Thus prediction, fusion, state/trait contrasts and cross-validation are occupied.

**Exact unresolved gap (I/U).** The searched evidence does not establish a common answer to *incremental individual utility under matched populations and declared known/novel-content reference access*, with measurement selection and quiz semantics challenged together. This is a narrowly scoped unresolved synthesis, not a verified absence theorem. L08 full methods could narrow it further.

**Why BBBD / usable data (F/I).** Repeated content, multiple sensors, direct quizzes, quality records and distinct protocols permit these competing explanations to be tested in one resource. E3–5 provide up to 94 qualified people / 324 tri-modal direct observations / 8 videos. E3+4 first tested exposure supports only 57 / 216 / 8; E5 is repeated exposure and must be separate. E1 supplies ocular-only evidence under its own protocol; E2 outcomes remain excluded.

**Independence/generalization.** Group all observations by qualified person and canonical video. Separate new people/known content, new people/new content without peers, and explicitly reference-assisted new content. Cross-experiment person identity is unresolved. Eight content units limit population-wide conclusions.

**Confounds/limitations.** Prior knowledge is unmeasured in a common eligible form; content difficulty, stable person differences, order, scoring, missingness and upstream preprocessing can explain apparent associations. No inference that physiology causes learning. Quality adjustment is a sensitivity analysis because looking away may be behavior.

**Baselines.** Training-only intercept/content effects where available; permissible traits with missing indicators; quality/availability alone; separate EEG, ECG, gaze and pupil summaries; ridge/additive mixed models; late/early fusion; train-only ISC/CorrCA/PCA; GCM when its reference requirements are met. Frozen pretrained representations and matched random features are optional later baselines.

**Potential contribution (H).** A modest outcome-contrast or nuisance-aware training objective that preserves useful learner differences across content, paired with an explicit reference-access evaluation. Existing simple models must be allowed to win. No method novelty is established by combining losses; the objective needs a distinct failure analysis and ablation against existing representation work.

**External need.** Recommended for strong Q1 claims; another educational cohort with objective tests is the closest validation. Another BBBD experiment is internal transport. Emotion/stress transfer validates only a method component.

**Falsification/weakening.** Gains disappear against content/quality/covariate baselines; intervals rule out a prespecified useful effect; benefits require unlabeled peers but are advertised as reference-free; direction changes across score definitions or content; or independent replication fails. Wide intervals mean inconclusive, not falsified.

**Novelty risk / closest work.** High: P03/P04, Adler 2025, Bühler 2024, John 2025, Chen 2026; FactorCL/CoMM and physiological representation work constrain methods.

**Expected contribution / status (I).** A defensible account of when physiology adds useful individual criterion information and what information/calibration it requires. **Rank 1, conditional primary**; no broad “learning biomarker” or architecture commitment.

## G02 — Selective measurement and validity under actual sensor availability

**Research question (H).** How does quality-dependent availability change the validity and coverage of physiological quiz estimation, and can an available-sensor policy retain useful performance for the full eligible outcome-observed population?

**Motivation (I).** A measure that works only after discarding poorly tracked participants can misrepresent practical usefulness and the population served. Real censoring may matter more than synthetic modality dropout.

**Established literature (L).** Sauter and John already consider eye-data quality; ICYM²I (L11) explicitly studies biased modality informativeness and corrects training/evaluation under MAR/positivity. QA-MoE (L12) models quality-aware routing; missing-covariate prediction (L14) distinguishes prediction from parameter recovery. MC² and related conformal work address availability-dependent uncertainty.

**Gap (I/U).** A BBBD-specific gap concerns *observable policy utility across actual eligibility/quality patterns*, rather than estimating a hypothetical fully clean population without identification. A general novel method requires more than continuous masks or applying IPW to physiology. It remains unknown whether quality is outcome-informative after permissible adjustment.

**Why BBBD / usable data (F).** E3–5 have 120 qualified people / 446 valid outcome observations before sensor QC, versus 94 / 324 in the tri-modal intersection. Mask histories and whole-video quality summaries expose real selection. E1 is a separate ocular policy; E2 cannot enter outcome-population denominators. Features missing through QC need an explicitly defined fallback.

**Independence/generalization.** Split people before policy fitting, imputation, threshold tuning or weighting; cluster by content. Evaluate on held-out eligible outcome-observed cases even when all candidate sensors are unavailable. Report per-pattern counts and risk, with no guarantee for unsupported patterns or future shifts.

**Confounds/limitations.** Off-screen gaze can be meaningful behavior, not failure. Masks may encode protocol/person characteristics. Observed quality–outcome association cannot prove MNAR; absent clean signals are not recoverable truth. There may be poor overlap/positivity and tiny strata. All-population means all observed eligible quiz cases, not absent nonparticipants.

**Baselines.** Complete-case model and coverage report; imputation plus indicators; direct available-subset predictors; covariate-only fallback; simple quality weighting; modality dropout; QA-MoE-type routing; ICYM²I only when target and assumptions match. Patternwise conformal is a comparator only where data/assumptions support it.

**Potential contribution (H).** A conservative policy that chooses sensor-dependent estimates or fallback using estimated incremental utility and limited-data uncertainty, coupled to explicit selection sensitivity. If adaptive abstention is used, compare risk at equal coverage and specify what happens to abstained learners. Novel theory is not presumed.

**External need.** A second naturally incomplete physiological dataset is necessary for a general selection-policy method; a second educational dataset is needed for a general educational-validity claim.

**Falsification/weakening.** Real eligibility barely changes conclusions; masks-only/fallback is as useful as physiology; gains arise solely from discarded hard cases; policy cannot improve risk at matched coverage; weighting depends on unverifiable extreme assumptions.

**Novelty risk.** Very high for algorithmic framing: L11–L16 and L38–L41; high for eye-quality-only framing: L05/L07. **Rank 2**, scientifically important companion to G01.

**Expected contribution (I).** Establish which learners are covered by a physiological measure, with an honest observed-data estimand and bounded missing-data conclusions.

## G03 — Behavioral utility of training-only EEG

**Research question (H).** When EEG improves individual quiz estimation, can that incremental behavioral information improve an ECG+eye student for new people/content without EEG at prediction, beyond ordinary student supervision and nuisance transfer?

**Motivation (I).** Removing a cap is useful only if the resulting measurement preserves meaningful information. Distillation accuracy alone does not show that knowledge about learning, rather than stimulus or acquisition patterns, was transferred.

**Established literature (L).** EEG-privileged peripheral learning dates to L17; eye-only reconstruction L18; EmotionKD, CMCRD, PhysioGMC, PULSE and BioKD cover adaptive transfer, subject generalization, shared/private representations and unreliable teachers. L24 establishes educational LUPI. P03 establishes brain–body mapping.

**Gap (I/U).** The defensible question is the *source and survival of a teacher's incremental behavioral utility* on educational outcomes with content and quality controls. Neither “EEG teacher,” “confidence weighting,” “contrastive distillation” nor “subject invariant” is a new contribution. A residual-utility objective is a hypothesis awaiting a targeted method comparison.

**Why BBBD / data (F).** Simultaneous EEG/ECG/eye and objective quizzes support controlled teacher/student comparisons. E3–5 complete teacher intersection: 94 / 324 / 8; ECG+eye student ceiling: 94 / 327 / 8. Removing EEG currently adds only three observations, not more qualified people. First-view subset is smaller. ECG and EyeLink remain required; no webcam/PPG data exist here.

**Independence/generalization.** Teacher training, pseudo-targets and utility estimation must be nested within training people/content; use out-of-fold teacher estimates for utility diagnostics. All views/windows stay together. Evaluate known versus novel content and calibration access explicitly.

**Confounds/limitations.** Teacher might be weaker, more overfit or more quality-sensitive than student. Teacher confidence is not utility. Differences in parameter count, augmentation, tuning budget and extra unlabeled data can explain gains. Shared stimulus information is not an identified brain mechanism.

**Baselines.** Same-data direct student, multimodal teacher, CCA/LUPI, ordinary logit/feature KD, representative CMCRD/PhysioGMC/PULSE/BioKD mechanisms adapted fairly, response residuals without KD, shuffled/matched teacher controls. Compare only feasible methods with the same outcome and information budget.

**Potential contribution (H).** Train against out-of-fold teacher improvement over a permissible nuisance baseline, potentially using within-content outcome contrasts. Need to show why existing uncertainty/utility weighting fails and how small-sample estimates are stabilized. This remains a method sketch, not claimed novelty.

**External need.** Yes for strong sensor-reduction generalization; another educational cohort with paired sensors. Actual lower-cost hardware is required before home/wearable claims.

**Falsification/weakening.** EEG adds no reproducible incremental utility; direct student matches KD; a nuisance-only teacher gives the same gain; transfer vanishes on new content or external data. Failure of the teacher-advantage prerequisite ends this branch.

**Novelty risk / expected contribution.** Highest collision risk among shortlisted candidates, particularly L20–L24. If successful, identifies conditions in which expensive physiological sensing improves training but is unnecessary for a valid criterion estimate. **Rank 3, dependent on G01**.

## G04 — Same-content transport across exposure protocols

**Research question (H).** Does a physiological quiz estimator trained on single tested exposure remain useful under repeated viewing with preview/incentive/intention changes, and vice versa, when tested material is shared?

**Motivation (I).** A score predictor can be useful in one instructional protocol but cease to be a comparable measure in another. Shared content offers a limited way to reduce content/protocol entanglement.

**Established literature (L).** BBBD P03/P04 already analyze experiments and synchrony; L03/L08/L09/L43 demonstrate context and knowledge dependence. L35/L36 and general domain methods already address cross-context generalization.

**Gap (I/U).** The remaining bounded question is transport across the actual E4/E5 bundles on their three identical tested videos, with matched outcome/scoring/access. It is not a clean intervention effect or a new generic domain adaptation setting.

**Why BBBD / data (F).** E4+5 offer 91 outcome-observed qualified people / 273 quizzes before sensor QC; tri-modal QC yields 70 / 200 / 3. E4's tested second block contains new videos; E5's final quiz follows repetition and altered instructions. E3 adds six videos with only one overlapping tested video across these protocols.

**Independence/generalization.** Bidirectional experiment holdout, qualified-person grouping, separate within-protocol baselines. Cross-experiment participant uniqueness must be certified before calling it new-person transport. Unsupervised target calibration, if permitted, is a different setting and must be evaluated separately.

**Confounds/limitations.** Cohort, order, repetition, preview, intention and incentives co-vary. Three common videos cannot identify a general distribution of protocols/content. Differences in mean difficulty or score variance can alter metrics. No causal reward, attention or repetition claim.

**Baselines.** Source-only regularized predictors; source-trained content baseline; within-target oracle benchmark clearly labeled unavailable at deployment; simple recalibration under a declared calibration budget; domain pooling and lightweight domain adaptation. No target outcome use in zero-label transport.

**Potential contribution (H).** A transport diagnostic separating shifts in baseline outcome distribution from changes in conditional physiological utility; potentially a conservative adaptation rule. Existing shift/recalibration methods are baselines, not novel ingredients.

**External need.** Essential for broad protocol claims: independent cohorts, more common videos and preferably crossed/randomized protocol assignments. E4→E5 is not external validation.

**Falsification/weakening.** Simple source content/mean baselines explain apparent transfer; uncertainty precludes useful distinctions; identity overlap invalidates the new-person claim; no reproducible protocol difference. Stable transport would refute a proposed fragility hypothesis but support the measurement.

**Novelty risk / contribution.** Moderate–high conceptual occupancy but a specific data opportunity. A useful bounded limit on the portability of an educational physiological criterion. **Rank 4**, preferably a G01 stress test.

## G05 — Preserve individual outcome information during multimodal alignment

**Research question (H).** Does maximizing cross-modal/shared-response agreement discard learner differences that matter for immediate quiz performance?

**Motivation.** A representation optimized to make modalities or viewers agree may privilege common stimulation over useful individual variation.

**Established work / gap (L/I).** FactorCL/CoMM already preserve unique and synergistic task information; PhysioGMC separates subject-related structure; PhysioOmni and PULSE use shared/private representations. L08 contrasts similarity across individuals/events; L10 models sensory contributions. The unestablished part is outcome-specific loss of information under the exact educational/reference-access setting, not the general alignment critique.

**BBBD / data (F).** E3–5 EEG/ECG/eye whole-video outcomes, same 94 / 324 / 8 ceiling; repeated viewers of common videos make shared-response comparisons possible. E3+4 first-view ceiling 57 / 216 / 8.

**Independence.** Fit all SSL and reference transformations on training people/content for inductive claims. Using unlabeled test people or content changes the access regime even without quiz labels.

**Confounds.** Person identity is partly predictive but not inherently nuisance; removing it indiscriminately can destroy valid signal. No common prior-knowledge baseline; high-dimensional information measures poorly identified at this sample size; upstream provenance unresolved.

**Baselines / method opportunity.** Train-only CorrCA/PCA, supervised ridge, late fusion, shared/private contrastive objectives, frozen FM and matched random features. An outcome-contrast objective could be tested inside G01; any “synergy” claim needs a separately validated estimator and estimand.

**External requirement.** Essential for representation-method claims; larger and genuinely different cohorts/content.

**Falsification.** Alignment preserves or improves held-out incremental utility; method works only with transductive references; direct simple features dominate; no stable signal beyond controls.

**Novelty risk / expected contribution.** Very high ingredient overlap. Potential explanation for a measurement failure, but **merge into G01/G03**, not a standalone architecture paper.

## G06 — Criterion robustness to quiz scoring

**Research question (H).** Do sensor utility and learner ordering remain stable when immediate quiz performance means exact correctness rather than correct-option endorsement with no incorrect-option penalty?

**Motivation.** A physiological result can appear robust while depending on a permissive outcome definition.

**Established work / gap (L/I).** The repository has already reconstructed both scores; fractional outcomes are not binomial successes. General score-validity/psychometric theory is established and not comprehensively surveyed for a new standalone method here. The remaining empirical question is sensitivity of a future physiological conclusion, not a discovery that scoring matters.

**BBBD / data (F).** Item-level records and both scores are available; 98 audited item responses receive full partial credit despite extra wrong choices. Eligible outcomes: 147 / 581 including E1; E3–5 120 / 446; sensor analyses use their smaller matched sets. E2 and the duplicated E3 item block remain excluded.

**Independence.** Quiz items nest within content and repeat across people; they are not independent learners. Content holdout includes its item set. Any item-difficulty calibration must be trained, not computed from test answers.

**Confounds.** Response style, number of correct options, video-specific item difficulty, no common anchor scale across all content, tiny item/person counts. Exact-set scoring is interpretable but is not certified latent “true learning.” Repeated E5 exposure changes the criterion context.

**Baselines / method opportunity.** Paired estimates under both definitions; exact-item Bernoulli models versus appropriate bounded/fractional video-score models; training-only item/video effects; reliability sensitivity. A complex IRT model needs identifiability/anchor evidence before adoption.

**External requirement.** Item-rich, independently calibrated pre/post assessments for a general psychometric claim; not required merely to report BBBD score sensitivity.

**Falsification.** Results remain materially unchanged within useful precision; the proposed fragility concern weakens. If they differ, report the construct dependence without choosing the score that favors the model.

**Novelty risk / contribution.** Little standalone novelty demonstrated. **Mandatory supporting analysis** that protects G01–G04 from target-definition artifacts.

## G07 — Uncertainty for crossed clusters and missing modalities

**Research question (H).** Can one obtain useful uncertainty guarantees for new learners and content when modality availability and repeated outcomes violate simple exchangeability?

**Motivation.** A point estimate can be unusable if its uncertainty is systematically understated for missing sensors or new material.

**Established work / gap (L/I).** MC² handles modality patterns; Lee et al. hierarchical data; Oliveira et al. nonexchangeable data; L40/L41 fairness and mask-conditional coverage. A general crossed learner–content result might remain, but its novelty and assumptions require dedicated mathematical review. No existing guarantee is automatically transferred to BBBD.

**BBBD / data (F).** 94 complete-QC qualified people, eight videos; per-experiment and per-mask calibration partitions can be much smaller. Whole-video quiz outcomes only.

**Independence.** Person and video dependence cross rather than form one simple nested hierarchy. Leave-video-out repetitions do not create many independent content draws. Protocol shift adds a different distribution problem.

**Confounds / limits.** Tiny strata make conditional coverage weak or vacuous; choosing among many patterns/methods consumes calibration information. Nominal coverage is not a finite-sample proof under arbitrary MNAR/domain shift.

**Baselines / potential method.** Grouped split conformal, patternwise calibration, hierarchical methods under their actual assumptions, empirical cluster-aware intervals and transparent risk–coverage curves. A new theorem plus simulations could justify a separate theory project; no such theorem has been established here.

**External need.** Multiple larger repeated-measure datasets and explicit missingness simulations are necessary; BBBD can be a small case study.

**Falsification.** Guarantee requires unjustified independence or trivial intervals; existing methods already cover the formulation; realistic strata provide no informative calibration.

**Novelty risk / contribution.** High, unresolved theory competition. **Defer standalone**; use uncertainty conservatively in other candidates without marketing a new guarantee.

## G08 — Temporal encoding and item-level brain–body dynamics

**Research question (H).** Which coordinated physiological events predict recall of particular educational facts?

**Motivation.** Local encoding evidence could explain why specific material is learned.

**Established work / gap (L/I).** P03 already studies temporal brain–body mapping; John uses annotated programming-video content; Chen studies event-level neural similarity. Item-specific encoding remains scientifically meaningful, but BBBD's current evidence does not support its required labels.

**BBBD / data (F).** Whole-video outcomes and aligned exported waveforms exist. Certified native residual timing and item-to-video timestamps do not. No item-timed response/encoding ground truth; repeated E5 exposure further obscures where encoding occurred.

**Independence.** Learner/video/item grouping is required; giving every window the final score creates repeated weak labels, not validated temporal targets.

**Confounds / limitations.** Common sensory input, autocorrelation, order, clock uncertainty and quiz relevance confound directed/temporal claims. Boundary alignment does not establish subsecond physiological synchrony.

**Baselines / potential method.** If new annotation and timing evidence eventually exist: content-event baselines, whole-video predictors, temporal nulls preserving autocorrelation, and existing temporal synchrony approaches. No proposed architecture can repair missing ground truth.

**External need.** A dataset or new study with validated event annotations, native triggers and appropriate memory outcomes is necessary for the intended mechanistic claim.

**Falsification / novelty risk.** Unverifiable timing or item mapping already defeats current feasibility. P03/L07/L08 further occupy broad temporal novelty.

**Expected contribution / status.** Could explain encoding under an appropriate design. **Rejected for current BBBD primary**; do not reopen native forensics merely to rescue it.

