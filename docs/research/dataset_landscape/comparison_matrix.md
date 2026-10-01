# Dataset comparison matrix

Evidence cutoff: **2026-10-01**. Every dataset name links to a note with sources, rates, access, quality limitations and reuse analysis. Values are reported unless marked calculated/nominal. NR/NV are unresolved, not zero. No numerical ranking: the criteria conflict and their importance depends on the eventual scientific question.

## Cohort, measurement and outcomes

| Dataset | Independent units and recording extent | Physiological/behavioral breadth | Outcome strength and experimental control |
|---|---|---|---|
| [BBBD (2026)](dataset_notes/bbbd.md) | 178 across 5 experiments; ~110 h gaze, 65 h EEG; complete multimodal N unknown | Research EEG, ECG, EOG, gaze/pupil/head, some respiration; no EDA/PPG | Actual video quizzes plus manipulation and self-report; common stimuli; order/repetition and experiment differences constrain causality |
| [Digit span (2022)](dataset_notes/digit_span_ds003838.md) | 86; 65 EEG; 64 metadata-complete across listed modalities/behavior; 162 trials/person | EEG, ECG, PPG, pupil/eye, item-level recall | Strong auditory memory/passive control and objective recall; fixed control-block placement, demographic concentration |
| [DREAMT (2024; v2.2 2026)](dataset_notes/dreamt.md) | 100 independent nights; ~7 h/night nominal | PSG EEG/EOG/ECG/EMG/respiration/SpO2 plus E4 PPG/EDA/motion/temp | Clinical sleep scoring, rich patient context; reference includes PSG inputs, single clinic/night |
| [LLaMAC (2025)](dataset_notes/llamac.md) | 108 retained; ~90 h clip exposure calculated | EEG, PPG, EDA, temp, respiration | Experienced affect, liking/familiarity; dimensional ratings after clips, block/context confounds |
| [SENSE-42 (2026)](dataset_notes/sense42.md) | 42; 84 h nominal; consent-dependent ECG/video | EEG, ECG, respiration, webcam, detailed mouse/keyboard | Dense task behavior, five-minute KSS/TLX; spontaneous state and interface familiarity confounds |
| [BALLADEER (2026)](dataset_notes/balladeer.md) | 164 children; substantial task/modality attrition | EEG, EDA/HR, eye events, games and clinical tests | Clinically assessed ADHD/controls; sex, age, device/task and recruitment imbalance |
| [IMPROVE (2025)](dataset_notes/improve.md) | 120; ~60 h nominal | Consumer EEG outputs, eye, HR, task-limited EDA, inertial, audiovisual and interaction logs | Phone manipulation, pre/post quiz and interruptions; partly predictor-refined labels |
| [MMV (2024)](dataset_notes/mmv.md) | 18 × 4 days; ~144 h nominal | EEG/EOG, ECG/PPG, EDA, EMG, eye | Repeated BCI tasks; ocular vigilance label is not independent of eye inputs |
| [Mixed emotion (2024)](dataset_notes/mixed_emotion.md) | 73 retained; ~13–19.5 h clip exposure nominal | EEG, PPG, GSR, face | Separate positive/negative reports; brief clips and mixed category validation |
| [I DARE (2024)](dataset_notes/idare.md) | 63; 2.8 h picture exposure calculated | EEG, PPG, SC, EMG, eye | Randomized standardized images, individual SAM; very short autonomic events |
| [MPD-DF (2026)](dataset_notes/mpd_df.md) | 50 × ~2 h; shorter/missing records | EEG, ECG, EOG, respiration | Physician fatigue staging, but substantially based on EEG; time-on-task confound |
| [DEJA-VU (2026)](dataset_notes/dejavu.md) | 28 people, 34 sessions; ≤12.75 h nominal | EEG, ECG, EMG, GSR in VR | Emotional transition sequences, pre/post reports; stimulus timing about ±0.5 s |
| [Enhanced VA (2025)](dataset_notes/enhanced_va.md) | 64, single visit; ≥40.5 h nominal task exposure | EEG, ECG, aggregated perfusion index | Video affect and MMST; stress/task/order inseparable in key contrasts |
| [Public exhibit (2026)](dataset_notes/public_exhibit.md) | 21,539 usable ≥1 signal; 7,646 all 3; unique visitors uncertain | BVP, EDA, temperature | Brief broad-population affect reports; extreme quality attrition, short windows |
| [EmpathicSchool (2025)](dataset_notes/empathicschool.md) | 30; ~40 h reported | E4 wearable and face/video features | Repeated stress reports/task TLX; many missing recovery tasks |
| [WEMAC (2024)](dataset_notes/wemac.md) | 100 women retained from 144; wide ages | BVP/GSR/temp during VR and subsequent speech | Rich experienced affect; speech not concurrent with viewing; substantial attrition |
| [MultiPhysio-HRC (2025/26)](dataset_notes/multiphysio_hrc.md) | 55 day 1, 42 day 2 | EEG/ECG/EDA/EMG/resp, face AUs/voice | Cognitive/VR/manual/robot tasks and questionnaires; movement/task confounds |
| [EMBRACE (2025)](dataset_notes/embrace.md) | 36 dyads, recurring people; unique N unknown | Two-person EEG/ECG/resp/EMG/kinematics | Randomized cooperative/competitive motor conditions; shared movement confound |
| [SEED-VII (2024/25)](dataset_notes/seed_vii.md) | 20 × 4 sessions; ~78.3 h clip exposure | EEG + eye | Emotion/intensity, many clips; small N and stimulus/session dependence |
| [COG-BCI (2023)](dataset_notes/cog_bci.md) | 29 × 3 weekly sessions; >100 h | EEG/ECG and task behavior | Multiple controlled cognitive tasks, RT/accuracy/KSS/RSME |
| [CASE (2019)](dataset_notes/case.md) | 30; ~20 h nominal | ECG/BVP/EDA/resp/temp/EMG | Dense simultaneous valence/arousal; annotation motor/latency confounds |
| [StressID (2023)](dataset_notes/stressid.md) | 65; exact duration NV | ECG/EDA/resp + audio/video | Several stressor families and self-report; speech/task signatures |
| [K-EmoCon (2020)](dataset_notes/k_emocon.md) | 16 dyads/32 people; 172.92 dyad-min | Consumer EEG, wearables, audiovisual | Self/partner/observer affect; post-hoc annotation and dyadic dependence |
| [AMIGOS (2018/21)](dataset_notes/amigos.md) | 40; varying long-video/complete subsets | EEG, ECG/GSR, face/body video | Affect/personality/mood and group context; missingness and group dependence |
| [DEAP (2011/12)](dataset_notes/deap.md) | 32; 21.3 h clip exposure; face 22 | EEG and peripheral physiology incl. BVP | Clip-level affect; highly familiar small-sample benchmark |
| [WESAD (2018)](dataset_notes/wesad.md) | 15 usable, single visit | Chest and wrist physiology/motion, no EEG | Lab stress protocol/self-report; motion/speech/task confounding |

## Practical readiness and scientific opportunity

“Strong” below means the design makes the evaluation possible, not that it has already passed. Cross-modal learning includes missing-sensor prediction, shared representation or transfer; reconstructing redundant channels is not automatically new neuroscience.

| Candidate family | Access / standardization / timing | Subject-independent and cross-modal potential | Saturation and remaining opportunity |
|---|---|---|---|
| BBBD | Open CC BY; BIDS/code; strong trigger/drift method, unmeasured residual; corrected labels essential | Strong person IDs and several stimulus/experiment domains, but small number of videos and incomplete modality overlap | Low verified independent reuse, **substantial antecedent science**. Rigorous individual prediction and missingness remain plausible; synchrony/attention/quiz association already occupied |
| Digit span | Open CC0; BIDS; shared EEG/cardiac amplifier; eye alignment needs audit | Good controlled cross-modal comparison at N=64 complete metadata; one language/mostly young women | Moderate direct scientific reuse; EEG/pupil overload, PPG load and pupil–ECG fusion already studied. Behavioral error information beyond task difficulty is plausible |
| DREAMT | Restricted DUA; CSV/versioned docs; 2026 alignment fix | Strong wearable-to-PSG reference; patient holdout possible, external/home validity absent | At least two substantive methods papers; large surrounding sleep literature. Clinical heterogeneity and sensor failure remain possible angles |
| LLaMAC | Open CC BY, 3.08 GB; CSV/code; sync assertion lacks measured validation | Good N for held-out people, and 50 shared clips support content holdout; no ECG/gaze | Low verified reuse, descriptor already classifies affect. Subjective/intended disagreement and robustness plausible |
| SENSE-42 | Restricted CC BY metadata, code CC0; flat files; consent/sync audit | Rich performance linkage, N=42 limits flexible models; webcam not calibrated eye | Descriptor plus CHI sleepiness prediction. Full prior analysis must be inspected before a novelty claim |
| BALLADEER | Open CC BY, 13.63 GB; software timing and heterogeneous devices | Clinically meaningful, but all-modality N and device/task separation uncertain | New release; platform/attention studies predate it. Fair, matched diagnostic associations possible; clinical deployment unsupported |
| IMPROVE | Request/license, 2.83 TB; scripts; software timestamp alignment | Strong observable behavior, weaker native neural/cardiac content | Phone/head/gaze distraction already studied. Learning outcomes beyond label-refined behavior may remain |
| MMV | ScienceDB access/terms need verification; raw+features | Excellent repeats/breadth, only 18 independent people; ocular target circularity | Descriptor already tests fusion/temporal models. Sensor-failure and independent-outcome checks more valuable than another PERCLOS classifier |
| Mixed emotion / I DARE | Mixed restricted; I DARE project open; license/raw details incomplete | N=73/63 promising; stimulus holdouts and label provenance essential | Low verified reuse, respective mixed-class baseline/physiological validation already present |
| MPD-DF / Enhanced VA | Raw/derived archives; details of native rate or license incomplete | Person holdouts feasible; target built from EEG or condition limits interpretation | Young releases; straightforward classification occupied or likely easy due to task/order |
| DEJA-VU / EMBRACE / MultiPhysio-HRC | Uneven timing/format/access certainty | True transitions, interaction and repeat tasks; unique-person grouping essential | Relatively young; movement/context artifacts provide both challenge and alternative explanation |
| Public exhibit / WEMAC | Open-route descriptions, some file/rights uncertainties | Diversity/scale or age range strong; missingness and cross-phase alignment constrain fusion | Original affect/fear questions already active. Selection effects and generalization more credible than universal emotion claims |
| EmpathicSchool / StressID / K-EmoCon | Code and documented release/request routes; non-BIDS | Audio/video–physiology useful; task/dyad holdout needed | Existing stress/affect fusion or annotation analyses. Low verified counts are not proof of open novelty |
| COG-BCI / SEED-VII | Public/request respectively; clear repeated sessions | Cross-day/task structure strong, N=29/20 weak; COG-BCI BIDS | Cross-session and cross-dataset classification already studied; use as demanding comparators |
| CASE / AMIGOS / DEAP / WESAD | Mature docs but different licenses/preprocessing | Useful reference tests; independent people remain few | Saturated standard tasks. A method-only accuracy gain or generic fusion claim is weak primary motivation |

## Comparisons that determine the decision

**BBBD versus digit span:** BBBD offers more people, more eye/body channels and meaningful naturalistic quiz outcomes; digit span offers much cleaner sensory control, ECG plus PPG, objective item-level recall and clearer task structure. Digit span wins on experimental control; BBBD wins on breadth of still-open empirical evaluations and operational public release size. Neither dominates on every criterion.

**BBBD versus DREAMT:** DREAMT offers longer clinical recordings, professionally scored reference states and clinically relevant heterogeneity. BBBD offers gaze and cognitively rich stimuli/outcomes. DREAMT is preferable for wearable sleep validation; it should not be demoted merely because it is clinical or lacks educational labels. Selecting it now would narrow the project to sleep more strongly than BBBD narrows it to video-related cognition.

**BBBD versus LLaMAC/SENSE-42/IMPROVE:** LLaMAC has EDA/PPG and better affect-specific reports; SENSE-42 has actual interaction dynamics; IMPROVE has phone manipulations and pre/post tests. BBBD's research-grade EEG/eye/ECG pairing, larger sample and open structured release provide more combined scientific flexibility, conditional on valid label joins and signal overlap.

**BBBD versus BALLADEER/public exhibit:** Larger or clinically richer headline samples do not guarantee larger usable multimodal cohorts or cleaner inference. BALLADEER's device/task and sex/diagnosis imbalance and the public exhibit's short, incomplete, visitor-level recordings carry greater identification risks for a general starting study.

**No pooled accuracy leaderboard:** labels, rates, split units, population and preprocessing differ too much. A 90% random-window classifier on one resource is not evidence that it is better than another resource with lower honest person-held-out performance.
