# Research inference register

Opened/updated: 2026-10-01. Scope: dataset selection only. **F** = observed/reported fact; **D** = derived metadata fact; **I** = interpretation; **H** = untested research opportunity; **U** = unresolved. Confidence describes evidence, not a statistical posterior. Facts can still require file-level confirmation.

| ID | Type / confidence | Statement | Basis and implication / verification |
|---|---|---|---|
| F01 | F / high | BBBD descriptor reports 178 released people from 186 recruited | [BBBD note](dataset_landscape/dataset_notes/bbbd.md); not all have every modality |
| F02 | F / high | BBBD Zenodo 1.1 was released 2026-09-25 with quiz mapping/correctness changes | [Changelog](https://bbbd.pythonanywhere.com/changelog); pin version and verify label joins |
| F03 | F / high | BBBD native acquisition rates differ from released 128 Hz aligned files | Descriptor signal-acquisition section; “raw” does not establish native fidelity |
| F04 | F / high | BBBD gaze/pupil interpolation is substantial and 16 Hz electrical contamination is documented | Descriptor preprocessing; clean derivatives cannot be assumed artifact-free |
| U01 | U | BBBD all-modality/outcome cohort and valid hours unknown | Need actual manifests, masks and corrected outcome joins |
| U02 | U | BBBD Exp. 2 website/paper counts and Exp. 5 allocation descriptions differ | Preserve discrepancy; do not silently pick whichever supports a desired conclusion |
| U03 | U | BBBD reported parenthetical counts are not sufficiently defined to label them by sex | Recalculate from archived participant metadata |
| I01 | I / high | BBBD attention-condition prediction can exploit arithmetic, order, repetition or video identity | Fixed order/shared stimuli; association is not a specific latent-state or causal claim |
| I02 | I / high | Window count and modality-hours overstate independent sample size | Dependence within people/videos/sessions applies to all candidates |
| D01 | D / high for inspected file | ds003838 metadata gives 86 people, 65 EEG, 83 ECG/PPG, 84 pupil, 64 all-availability flags clear | [Aggregate audit](dataset_landscape/evidence/digit_span_metadata_audit.json); mutable master source hashed; no waveform QC |
| D02 | D / high for inspected file | ds003838 has 74 female/12 male, age mean 20.53, range 18–44 | Same audit; availability counts do not equal quality-approved counts |
| U04 | U | ds003838 exclusion-reason arithmetic is inconsistent with paper total | Metadata has 21 EEG exclusions; paper describes 3 + 19. Reasons remain unresolved |
| I03 | I / high | Digit span offers stronger sensory/memory control than naturalistic video | Fixed visual scene, passive auditory control and scored recall; control-block placement still confounds |
| F05 | F / high | BBBD synchrony/attention/memory and digit-span EEG/pupil/PPG load analyses already exist | [Bibliography](literature/bibliography.md); low recent dataset-name reuse is not an unoccupied topic |
| F06 | F / high | A 2026 ds003838 thesis already studies pupil–ECG cognitive-load fusion | [UPM](https://oa.upm.es/97820/); thesis is prior work, not peer-reviewed journal evidence |
| F07 | F / high | DREAMT 2.2 includes PSG and fixes acceleration alignment | [PhysioNet](https://physionet.org/content/dreamt/2.2.0/); older wearable-only descriptions are stale |
| I04 | I / high | DREAMT is a stronger clinical wearable reference than BBBD | Expert PSG scoring and patient cohort; does not establish home/multi-night utility |
| I05 | I / high | MMV eye-derived PERCLOS with eye/EOG predictors and MPD-DF EEG-based labels with EEG predictors require restricted interpretation | [MMV](dataset_landscape/dataset_notes/mmv.md), [MPD-DF](dataset_landscape/dataset_notes/mpd_df.md); agreement with constructed labels is not independent latent-state validation |
| I06 | I / high | BALLADEER diagnosis can be confounded by age/sex/device/task and recruitment | Coverage/diagnosis tables; require matching and independent external validation |
| I07 | I / high | IMPROVE gaze/head-refined interruption labels can reward reproducing the annotation rule | Preserve original labels and audit refinement provenance |
| I08 | I / high | A shared logging clock does not prove sample-level device synchronization | Particularly relevant to LLaMAC/software-only systems; measure latency and drift |
| U05 | U | I DARE's reported PPG low-pass specification may remove pulse information | Inspect unprocessed signals/code; do not repair publication text by assumption |
| I09 | I / high | Public-exhibit nominal visitors and complete physiological cases are different populations | 21,539 ≥1 signal versus 7,646 all 3; persistent visitor identity not established |
| U06 | U | SENSE-42 actual released ECG/webcam counts and prior CHI analysis footprint remain incomplete | Consent statements differ; restricted files/full text not audited |
| U07 | U | EMBRACE visible small archive does not establish full raw-signal access | 36 dyads include recurrent people; TDF proprietary; unique N/rates/bytes need inspection |
| D03 | D / high | BBBD corrected ZIPs sum to 26,973,110,601 bytes | [Manifest](dataset_landscape/evidence/bbbd_release_manifest.md); metadata sum, not downloaded checksum verification |
| I10 | I / high | New archive date or 97% newly public duration does not imply new experiments or untouched scientific questions | BBBD antecedents, ds003838 mirror and original benchmarks illustrate distinction |
| I11 | I / medium | BBBD offers the best balance under the present broad scope | [Decision](dataset_landscape/selection_decision.md); contingent on trustworthy labels/coverage and future novelty review |
| H01 | H / untested | BBBD may permit individual behavioral prediction beyond shared stimulus/trait effects | Must survive person/stimulus holdouts and simple behavioral/stimulus controls; not a chosen problem |
| H02 | H / untested | Real missing-modality patterns may support useful reliability research | Need masks, failure mechanisms and nonselective evaluation; not assume missing-at-random |
| H03 | H / untested | Cross-dataset comparison may test robustness of shared physiological relationships | Preserve incompatible labels; harmonize sensors/licensing; separate rather than blindly pool domains |
| U08 | U | Most candidate reuse counts are lower bounds | No comprehensive citation database export; inaccessible methods and indexing lag prevent census claims |

Amend entries when evidence changes; retain the superseded interpretation and reason rather than silently rewriting history. No H entry authorizes modelling or establishes novelty.
