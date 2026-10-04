# Raw audit notes from the delegated M07/M05 checks (2026-10-04)

Verbatim working notes saved by the delegated investigations. Key items were re-verified by the lead investigator; see external_validation.md and novelty_closeout.md. Notes are data, not conclusions.

## M07 — John 2025
# John et al. 2025 Sci Rep 15:20291 doi:10.1038/s41598-025-06654-x PMC12198398
OSF 4rn5q: public, CC-BY 4.0 (license id 563c1cf88c5e4a3877f9e96a), 0 children, osfstorage only; 516 files, 6029 MB.
Contributors: Nathalie John, Sebastian Peter Korinth, Mareike Kunter, Franziska Baier-Mosch (DIPF/Goethe Frankfurt).
/Mine/Mine_Eye/edf 118 EDF (1475.7MB, ~12.3-12.7MB each) LeVi_<ID>.EDF ; 117 IDs link to Quest, 1 (A020523) not.
/Mine/Mine_EEG/Mine_raw 121 fif (2589.2MB) <ID>_003_TR4_raw.fif; all 121 link to Quest; 4 files <5MB (A160323 0.57MB, A200123 0.055MB, A200423 0.075MB, A250123 3.76MB).
/Bang/... 121 EDF (579MB), 121 fif (1251MB).
ScriptVariables.xlsx sheet Quest: 121 rows x 35 cols: participants, condition (0/1 utility value; 60/61), age, sex_n, comfortEEG, exert_*, mentalEffort, knowPre_1..8 (7 items), knowPre_sum, knowPost_1..14 (13 items), knowPost_sum. No missing.
sheet POIs: 76 annotated segments (code_explain, provide_summary, code_type, code_executed, game_explain).
EEG = 2 cEEGrids (L1-L10, R1-R8 used) SMARTING 250Hz; Eye = EyeLink 1000 right eye 500Hz; no ECG reported.
Paper: 121 recruited; Mine eye N=105 after QC; pretest ~10 min before video; posttest immediately after (~20 min).
codebook.Rmd imports ../all/data_mine_agg.rda (not present in /all listing).

## M07 — Bühler 2024
# Bühler et al. 2024 ETRA / PACM HCI 8(ETRA):230 doi:10.1145/3655604 arXiv 2404.00333
N=96 collected -> 88 -> 84 quality-retained; Tübingen (ethics A2.5.4-210_ns); SMI RED 250Hz no chinrest; one ~60-min prerecorded Zoom stats lecture (linear regression); 15 thought probes; pretest 8 items before; posttest 14 items (7 fact, 7 inference) after.
arXiv version: no data availability statement found.
Same cohort: ICMI'24 doi:10.1145/3678957.3685710 (eye+facial video+Empatica E4 EDA/BVP, N=87); J Educ Psychol 117(1):38-62 doi:10.1037/edu0000903.
Dissertation (Tübingen 10900/155225) Transparency: "We plan to make the survey and sensor data ... openly available at a later point in time. Supplemental materials are available at https://osf.io/4qkvx/?view_only=..."
OSF 4qkvx (public, node_license null) on 2026-10-04: /Code/ (empty), /Supplemental Materials/Pre-Post-Knowledge_Tests_en.pdf 392641 B, Supplemental_Materials.pdf 457911 B. No data.

## M07 — other leads
# Lallé et al. AIED 2025 (doi 10.1007/978-3-031-98417-4_10; HAL hal-05134575v2) green chemistry
GitLab https://gitlab.lip6.fr/mocah-public/eye_tracking_green_chem_video (project id 2304, public), LICENCE.md = BSD 3-Clause (copyright "XXX"); Readme.md empty.
Data/Data2023.zip 82,025,452 B; Data/Data2024.zip 85,762,303 B (NOTE: server ignored HTTP Range; both zips were fully downloaded by accident, listed, then deleted).
Data2023: 27 Tobii TSV exports (97 cols incl gaze L/R, pupil L/R, validity, eye position, events), Forms/Form_pre_study.csv (27x8), QCM_Labels.csv (348 rows, 25 participants, 15 segments, answer 0/0.33/0.5/0.66/1), SelfReport_Labels.csv, Logs/panopto_logs_filtered.csv, pupiltime.txt. Uncompressed 703 MB.
Data2024: 28 TSV, pre_survey.csv (28x8), QCM_Labels.csv (420 rows, 28 participants, 15 segs), SelfReports_Labels.csv, panopto log, Tobii MouseKeyboard Events. Uncompressed 662 MB.
Sampling ~60 Hz (median dt 16.655 ms). Paper: N=54 Sorbonne chem undergrads, one 7:30 video, self-paced (pause/seek, notes allowed), 15-item immediate retention MCQ each mapped to a video segment, per-item "already knew" flag; 3 pre-knowledge questions; 18-item retrospective attention survey.
# IMPROVE (Daza et al., arXiv 2412.14195; UAM BiDA lab) GitHub BiDAlab/IMPROVE README: access via signed license agreement emailed to atvs@uam.es; ScienceDB doi 10.57760/sciencedb.14565. 120 learners, Tobii Pro Fusion 120Hz, NeuroSky (band power ~1Hz), smartwatch HR/EDA, webcams; HTML MOOC session ~30 min, 2 short videos (20 s + 1:48) + reading; 8-item pre and 8-item post test. 2.83 TB.
# Adler et al. 2025 EAIT: DAS verbatim "not publicly available due to privacy and ethical considerations but are available from the corresponding author de-identified on reasonable request." WebGazer; CCNY Parra lab; 139 in-class + 215 online; 4 videos; 12-item pre/post quizzes.
# Liu et al. 2023 Psych Res (PMC9844199): DAS "All data, models, and code generated or used during the study appear in the submitted article." EyeLink 1000 500Hz; 24+26 students Zhejiang Univ of Tech.
# Davidesco et al. 2023 Psych Sci 34(5):633-643: live teachers, Enobio 32 500Hz, 31 students, 4 lectures, 10 MCQ per lecture pre(1wk)/immediate/delayed; no DAS found in bioRxiv v2; APS page shows no badges; OSF users 3758f/gtypd have no matching public project.
# Bühler-adjacent TUM dataset (arXiv 2604.09569) "Zenodo 14097753" -> Zenodo API 404 "The persistent identifier is not registered."
# Bodonhelyi et al. 2026 arXiv 2604.09569 (TUM/IWM/Tübingen) own dataset
Author-published preview link in PDF: zenodo.org/records/14097753?preview=1&token=... -> HTML: is_draft true, is_published false, access files "restricted", record "public"; license cc-by-4.0; creators "Anonymous"; files database_documentation.md 9,490 B, dataset.db 6,789,455,872 B (SQL). Description: N=56, sequence of three videos (derivatives), 10-item exam pre/post + 1-week retention; MW self-caught keypress; EyeLink 1000 Plus 1000 Hz. Public API /api/records/14097753 -> 404 not registered.
# Madsen et al. 2021 PNAS OSF m7gj4 (GUID fjxaq is file /data/Education_questions.xlsx): public, node_license None; 161 files, 4000 MB; Experiment_1..3 lab (BBBD 1-3 lineage), Experiment_4 (35 files) / Experiment_5 (41 files) webcam per-video: videos 1,3,5,7,11; *_data_eye.mat (~46 MB), *_T_answers.mat, *_T_demographics.mat, ISC_eye; Exp5 also data_eye_1000Hz.mat (~906 MB) and T_answers_baseline. Contributor: Jens Madsen.
# Sauter et al. 2022 ETRA: Ulm; Prolific + Labvanced webcam; 27 participants; 6 videos (2 from Madsen 2021: enzymes, planet measurement); no data statement found in PDF.
# Kok et al. 2023 Cogn Sci PMC10078589: SMI RED 250Hz; no data availability statement found in EuropePMC full text.
# AttentivU (Kosmyna & Maes 2019 Sensors PMC6929136): BrainCo Focus 1 consumer EEG; 48 adults; no data statement.
# Confused-student EEG (Kaggle wanghaohan/confused-eeg): 10 students, NeuroSky single channel, self-reported confusion; no objective test.
# MEMA (arXiv 2411.09879): EEG attention states; no knowledge test.
# Chen et al. 2026 NeuroImage (PMID 42302884, Tsinghua): EEG, online physics video learning, event-level outcomes; data availability UNRESOLVED.

## M05 — novelty closeout notes
# M05 scratch notes (2026-10-04)
## T1 Chen 2026
- PubMed efetch 42302884: abstract+keywords (EEG; Individual differences; IS-RSA; Learning; Prior knowledge profile); NeuroImage 338:122062, Sep 2026; online 2026-06-16 (OpenAlex/Crossref); OA CC BY-NC-ND (Unpaywall GOLD); 78 refs; NSFC funded.
- Full text: ScienceDirect 403/CAPTCHA (direct, pdfft, reader proxy); Elsevier API returns coredata only w/o key; EuropePMC no full text; no preprint found (OpenAlex, web search). => FT NA, AB only.
## T4 P01 verbatim (PMC7865179 HTML, Materials and Methods > Procedure > Laboratory experiments)
- "In experiment 1 (intentional learning), subjects watched a video and answered afterward a short four-alternative forced-choice questionnaire."
- "In experiment 2 (incidental learning) subjects were not aware that they would be tested or asked questions regarding the material. They first watched all five videos and subsequently answered all of the questions (59 questions in total)."
- "In experiment 3, subjects were informed that questions regarding the material would be presented after each video and followed the procedure of experiment 1, using a different set of stimuli with six videos."
- "Common for experiments 1 to 3, after subjects had watched all video stimuli and answered questions, they watched all of the videos again in a distracted condition using the same order as the attend condition."
- LOO CV (Methods, online): "Testing how well eye-movement ISC can predict the performance of students on tests regarding the material in the online setting, we use leave-one-out cross-validation." Results: "prediction error ... 14.6 ± 16.9% ... equivalent to 1.75 of 12 questions, and outperforms a naïve predictor based on mean performance"
## T4 P03 verbatim (PMC9802497 JATS via EuropePMC, Materials and methods > Procedure)
- "After they had watched the videos, subjects were given a 4-alternative forced-choice questionnaire covering factual information imparted during the video (11–12 recognition questions per video; ...)"
- "In Experiment 1, subjects were not aware that they would be tested on the material, whereas in Experiments 2 and 3 the test was anticipated."
- "After answering questions, in Experiments 2 and 3 subjects were asked to watch the videos again, but this time to silently count..."
- Results: "(these data were available for 43 of the 92 subjects)"; no mention of intervention/reward/preview in P03 text (grep: 'reward','preview','incentive' absent).
- Discrepancy: Results "total duration of 10 minutes" vs Methods "total duration 15.5 minutes" for Exp1 3 videos.
## T2 P05 (abstract via Semantic Scholar API + OpenAlex abstract_inverted_index; identical text)
- BBBD Experiment 2, 30 participants, common stimulus stim01, attentive vs distracted; 4 s windows/2 s overlap; 5278 windows (2730 A, 2548 D); 15 band-power features; SVM/RF/GB/XGBoost; LOSO CV; SVM acc 0.6027, weighted F1 0.5669.
- Target: attention condition, NOT quiz. Abstract states quiz scores "do not directly reflect whether learners remain attentive".
## T3 sweep leads (abstract-level unless noted)
- OpenAlex cites: S01 cited by NEMAR E1/E4 re-releases (2026-07/09), R03 review, P05; P04 cited by 1 (Chinese review). No 2025-10/2026 paper using BBBD for quiz prediction found.
- NEMAR nm000147 (E4) metadata: "Session 1 was an attentive condition with factual multiple-choice questions after each video. Session 2 was a distracted condition..." (conflicts w/ S01 two-attentive-block reconstruction)
- NEMAR nm000150 (E1): "attentive condition, in which participants were tested afterward with multiple-choice questions, and a distracted condition"
- Silvan Ortubay, Parra, Madsen arXiv 2409.13084 / EMBC 2025 doi 10.1109/embc58623.2025.11254013: reference-free face-video model predicting eye ISC; unseen subjects R2 .26-.30; target ISC not test score; quote "without needing reference data from an attentive group".
- Peng, Nastase,... Li, Neuron 2026 doi 10.1016/j.neuron.2026.04.005: fMRI+eye, n=57, alignment "jointly mediated learning gains" (explanatory)
- Adler, Steinberg, Parra JSET 2026-10-03 doi 10.1007/s10956-026-10360-2: classroom intervention; no physiology in abstract
- Madsen et al bioRxiv 2025.12.22.696055 brain-body dynamics narratives (not learning)
- Lambrechts et al bioRxiv 2026.08.06.743268 interpersonal sync tracks attention/engagement (auditory; no learning outcome)
- Levy..Zion Golumbic npj SoL 2025 (EEG/SCR, interest/noise); Cetron et al npj SoL 2026 fMRI concept knowledge
- Liu, Lin, Zhang 2025 BMC Psychol meta-analysis ISC-attention r=.65 (14 studies)
- EduGage arXiv 2605.01238 (engagement self-report, participant CV); SAVVY 2607.29413; Bodonhelyi et al 2604.09569 MW benchmark
## T4 S01 (PMC13284221 JATS) verbatim
- "For experiment 4, participants watched 6 videos in an attentive condition. They were tested on the last 3 videos they watched. Participants were not informed they would be tested on the content"
- "Between the two conditions there was an intervention - participants were incentivised with money for every question they got right at the test that was given to them at the end of the second condition. They were also shown what questions were going to be asked, and were made to watch the same videos again."
- Exp 2: "not knowing they would be questioned about the content of each video all together at the end of the video-watching" ; domain-knowledge questionnaire before stimuli.
## T5/T6 anchors: metadata verified via OpenAlex/Crossref; abstracts read (AB) for Hedge18, Yarkoni&Westfall17, Poldrack20, Funder&Ozer19, Marek22, Varoquaux18 (arXiv), Hunsley&Meyer03, Bates (JASA 2024 119(546):1434-45), Judd12, Westfall14, Cameron08, MacKinnon&Webb17. Gignac&Szodorai abstract NA -> dropped.
