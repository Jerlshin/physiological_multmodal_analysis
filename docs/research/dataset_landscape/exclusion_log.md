# Exclusion and nonselection log

Date: 2026-10-01. Negative findings are retained. “Not primary” does not mean scientifically useless. Some exclusions concern access/evidence rather than study quality. Serious candidates retain individual notes even when excluded.

## Finalist nonselections

| Candidate | Why it does not replace BBBD in this broad project | What would change that judgment |
|---|---|---|
| Digit span ds003838 | Stronger control, but only 64 metadata-complete people, concentrated demographics and several core physiological/fusion analyses already published | Prioritize controlled recall, or BBBD label/coverage audit fails |
| DREAMT | Stronger clinical reference and duration, but sleep-specific scope, restricted access and already active transfer/staging literature | Clinical wearable sleep becomes the priority |
| LLaMAC | Strong affect labels/N and open access; no ECG/gaze, block confounds and insufficient timing validation | Affect/EDA/PPG becomes central |
| SENSE-42 | Rich HCI behavior; N=42, consent-dependent ECG/video and existing sleepiness prediction paper not fully inspected | HCI performance becomes central and coverage/prior-work audit succeeds |
| BALLADEER | Pediatric clinical value, but device/task and age/sex/diagnosis confounds, uneven modalities | A carefully matched developmental question survives coverage and medication audit |
| IMPROVE | Rich education/phone behavior, but consumer neural outputs/slow HR and partly predictor-derived interruption labels; large/requested data | Phone interaction/learning-gain question with independent labels becomes central |
| MMV | Excellent repeated days and sensors; N=18 and ocular-label circularity | Independent performance outcomes or explicit ocular-state measurement is the target |
| Mixed emotion / I DARE | Meaningful affect designs; access/raw/rate uncertainties and brief events | Confirm release integrity and a distinct subjective-affect question |
| MPD-DF / Enhanced VA | Young and broad; EEG-derived or condition labels, time/task confounds | A measurement-agreement or properly controlled transfer question is justified |
| DEJA-VU | N=28 and coarse stimulus timing despite interesting transitions | Coarse VR transitions, not fast coupling, become central |
| MultiPhysio-HRC / EMBRACE | Valuable real interaction; motion/task confounds, repeated people and unresolved format/access details | Access/timing audits and appropriate movement-control designs succeed |
| Public exhibit / WEMAC | Scale or broad demographics are strong; attrition, short signals, visitor identity/cross-phase issues | Selection bias, population heterogeneity or cross-phase affect becomes central |
| EmpathicSchool / StressID / K-EmoCon | Useful video/wearable/social data; smaller independent samples, task/dyad confounds, established original benchmarks | A new hypothesis specifically uses their distinctive annotations/context |
| COG-BCI / SEED-VII | Strong repeat sessions but small N; standard cognitive/emotion decoding active | Cross-day stability becomes a required rather than optional dimension |
| CASE / AMIGOS / DEAP / WESAD | Essential references but familiar small-cohort benchmark tasks saturated | External validation/comparison rather than primary novelty |

## Earlier screening exclusions / holds

| Resource | Evidence and reason | Status |
|---|---|---|
| [MAD 2026](dataset_notes/mad.md) | 18 people, 17 complete physiology, peak-selected clips, ~8 TB claimed; stable licensed public download not verified; descriptor already covers multiple obvious ML tasks | Hold for access |
| [n-back/music](dataset_notes/nback_music.md) | 11 recruited but only 5 released; fixed music order; too few independent people for the proposed publication foundation | Reject primary |
| [CognitiveLab 2025](dataset_notes/cognitivelab.md) | Separate small task cohorts; no stable public source verified; cannot treat it as one complete multimodal cohort | Hold for repository |
| [TILES family](dataset_notes/tiles.md) | Excellent longitudinal behavior; raw multisystem timing and clinical-reference availability differ by release; 2025 benchmark already studies main tasks | Retain domain alternative |
| BIRAFFE-3 | Public release not verified; planned/reported future collection is not currently obtainable data | Do not select on promised N |
| BIRAFFE-2 | Older game/affect resource discovered; not deeply audited after larger/current candidates and established references identified | Screened, lower priority; not called invalid |
| DREAMER | Established 23-person low-cost EEG/ECG affect benchmark, narrower and smaller than selected alternatives | Secondary benchmark only |
| MAHNOB-HCI | Important older EEG/eye/peripheral benchmark; mature affect literature and smaller cohort | Secondary benchmark; current access not audited |
| FACED | Large affective EEG resource, but multiple electrodes alone do not establish multisystem physiological data | Outside primary multisystem requirement |
| Eye-BCI 2025 | Ocular/BCI technical resource, less compelling behavioral/outcome breadth for the current dataset decision | Technical comparator if later relevant |
| MIMIC/SHHS/MESA and large clinical waveform families | Valuable established clinical resources; task/label scope differs and many lack the requested naturalistic behavioral/eye linkage. DREAMT offers direct wrist–PSG pairing and was examined seriously instead | Not inferior in general; external clinical comparators |
| MC-MED and other broad 2025 clinical records | Discovered as clinical alternatives, but complete physiology/behavior linkage and access were not audited in this review | Screening limit recorded; no ranking claim |
| QoLStress 2026 / SenseCobot | Additional recent domain leads; narrower physiology or overlapping stress/HRC role; not full finalist extraction | Revisit if final scope makes them central |
| Kaggle-only mood/mental-health tables | No verified original synchronized physiological acquisition or scientifically documented labels | Reject unverified provenance |
| Scientifically sourced rPPG/Kaggle resources | Potentially valid for pulse measurement; narrower target and physiology than the principal candidates | Measurement benchmark only |

## Literature leads deliberately not counted as verified reuse

- Citation to a descriptor without confirmation of recording use; mirrors, download counts and code forks.
- “Physiologically Guided Cross-Modal Fusion for Robust Vigilance Estimation” (2025): identity of MMV use requires full-method confirmation.
- Some ds003838 classifier papers describe the accession as “EEGMAT”; identity/protocol mismatch requires verification. They strengthen the need for caution about novelty but are not used as confirmed numerical counts.
- BBBD-related online/classroom studies with other participants are scientific precedent, not additional participants in the released dataset.
- NeurIPS/ACM/IEEE results inaccessible in full text are not treated as fully audited baselines.

No exclusions were erased because they were inconvenient to the preferred dataset. This log should receive a dated amendment if new data, rights or correction evidence changes a decision.
