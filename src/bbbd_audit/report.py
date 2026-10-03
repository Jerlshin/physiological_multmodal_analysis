"""Render the audit evidence as publication-oriented research documentation."""
import json
import re
from pathlib import Path
import numpy as np
import pandas as pd
from .io import EVIDENCE,ROOT,write_json

DOC=EVIDENCE.parent
def md(t,cols=None):
    if cols:t=t[cols]
    if t.empty:return 'No records in this scope.\n'
    def cell(x):
        if isinstance(x,(float,np.floating)):return '' if pd.isna(x) else f'{x:,.3f}'
        return str(x).replace('|','/').replace('\n',' ')
    return '| '+' | '.join(t.columns)+' |\n| '+' | '.join(['---']*len(t.columns))+' |\n'+'\n'.join('| '+' | '.join(cell(x) for x in row)+' |' for row in t.itertuples(index=False,name=None))+'\n'
def write(name,text):
    # Normalize prose spacing without altering paths, keys, hashes or code blocks.
    lines=[];fenced=False
    for line in text.splitlines():
        if line.startswith('```'):fenced=not fenced
        if not fenced and not line.startswith(('|','```')):
            for a,b in {'BBBD1.1':'BBBD 1.1','Zenodo22968459':'Zenodo record 22968459','released2026':'released 2026','Embedded1.0.0':'Embedded 1.0.0','Only11':'Only 11','only3':'only 3','Figure6':'Figure 6','full16 Hz':'full 16 Hz','labelsmV':'labels mV','isEurope/Berlin':'is Europe/Berlin','use2026':'use 2026','high-pass0.05':'high-pass 0.05','approximately0.':'approximately 0.','the0.25':'the 0.25','above4':'above 4','declared3–7':'declared 3–7'}.items():line=line.replace(a,b)
            line=re.sub(r'\b(experiments|in|for|across|at|with|before|plus)(?=\d)',r'\1 ',line)
            line=re.sub(r'([;:])(?=\d)',r'\1 ',line)
        lines.append(line)
    (DOC/name).write_text('\n'.join(lines).rstrip()+'\n')

def run():
    downloads=json.loads((EVIDENCE/'download_manifest.json').read_text())
    if len(downloads)!=5 or any(r['status']!='verified' for r in downloads):raise ValueError('Report requires all five checksum-verified archives')
    manifest=pd.read_parquet(EVIDENCE/'canonical_manifest.parquet');f=manifest[manifest.missing_file_status=='present']
    if set(f.experiment)!=set(range(1,6)):raise ValueError('Report requires full five-experiment QC')
    ex=pd.read_parquet(EVIDENCE/'exposure_tensor.parquet');c=pd.read_parquet(EVIDENCE/'channel_qc.parquet');peaks=pd.read_parquet(EVIDENCE/'peak_qc.parquet')
    inv=pd.read_parquet(EVIDENCE/'archive_members.parquet');q=pd.read_parquet(EVIDENCE/'quiz_video_outcomes.parquet');items=pd.read_parquet(EVIDENCE/'quiz_items.parquet');traits=pd.read_parquet(EVIDENCE/'participant_traits.parquet');joins=pd.read_csv(EVIDENCE/'participant_quiz_join_ledger.csv')
    ints=pd.read_csv(EVIDENCE/'modality_intersections.csv');timing=pd.read_parquet(EVIDENCE/'timing_boundaries.parquet');co=pd.read_parquet(EVIDENCE/'eeg_contamination_map.parquet');ag=pd.read_parquet(EVIDENCE/'quiz_aggregate_comparison.parquet')
    memory=q.query("question_type=='memory' and valid_outcome")
    coverage=f.groupby(['experiment','status','modality']).agg(files=('path','count'),people=('qualified_participant_id','nunique'),hours=('observed_duration',lambda x:x.sum()/3600),basic_QC_flags=('qc_status',lambda x:sum(x!='passes_basic_screen'))).reset_index()
    coverage.to_csv(EVIDENCE/'physical_coverage.csv',index=False)
    total=sum(r['local_bytes'] for r in downloads)
    archive=inv.groupby('archive').agg(members=('path','count'),member_bytes=('bytes','sum')).reset_index()
    archive=archive.merge(pd.DataFrame(downloads).rename(columns={'filename':'archive'}),on='archive',validate='one_to_one')
    table=md(archive,['archive','local_bytes','members','member_bytes','official_checksum','sha256'])
    overview=ex.groupby('experiment').agg(people=('qualified_participant_id','nunique'),design_exposures=('session','count'),videos=('canonical_video_id','nunique')).reset_index()
    overview=overview.merge(memory.groupby('experiment').agg(valid_quiz_person_video_pairs=('participant_id','count')).reset_index(),validate='one_to_one')
    allints=ints[ints.experiment=='ALL'].copy();allints['valid_hours']=allints.valid_duration_seconds/3600
    compact=allints[['modalities','stage','requires_valid_quiz','people','person_video_exposures','videos','valid_hours']]
    core=ints[(ints.stage=='basic_qc')&ints.requires_valid_quiz&(ints.modalities=='eeg+ecg+eye')].copy();core['valid_hours']=core.valid_duration_seconds/3600
    eye=f[(f.status=='author_processed')&f.modality.isin(['gaze','pupil'])]
    eyes=eye.groupby(['experiment','modality']).agg(files=('path','count'),mean_correction=('correction_fraction','mean'),median_correction=('correction_fraction','median'),max_correction=('correction_fraction','max'),max_gap_seconds=('longest_correction_gap_seconds','max'),basic_QC_flags=('qc_status',lambda x:sum(x!='passes_basic_screen'))).reset_index()
    eeg=co.groupby(['experiment','status']).agg(channels=('channel','count'),flagged_10dB=('flag_10db','sum'),max_excess_dB=('excess_16hz_db','max'),median_excess_dB=('excess_16hz_db','median'),extreme_variance_flags=('extreme_variance_flag','sum'),line_60Hz_flags=('line_noise_60hz_flag','sum')).reset_index()
    eeg['flag_fraction']=eeg.flagged_10dB/eeg.channels
    localized=co[co.flag_10db].groupby(['experiment','status']).agg(flagged_people=('qualified_participant_id','nunique'),flagged_recordings=('path','nunique')).reset_index()
    eeg=eeg.merge(localized,on=['experiment','status'],how='left',validate='one_to_one').fillna({'flagged_people':0,'flagged_recordings':0})
    powers=co.groupby(['experiment','status']).fraction_16hz.max().rename('max_16Hz_power_fraction').reset_index()
    eeg=eeg.merge(powers,on=['experiment','status'],validate='one_to_one')
    rp=peaks[peaks.event_type=='rpeak']
    heart=rp.groupby('experiment').agg(files=('path','count'),people=('qualified_participant_id','nunique'),peak_count=('peak_count','sum'),duplicates=('duplicate_peaks','sum'),nonmonotonic=('nonmonotonic_peaks','sum'),median_file_HR_bpm=('median_hr_bpm','median'),median_RMS_RR_seconds=('rms_rr_seconds','median'),median_RMSSD_seconds=('true_rmssd_seconds','median'),max_broad_RR_failure_fraction=('rr_outside_30_200_fraction','max')).reset_index()
    rp[rp.rpeak_out_of_waveform_count>0].to_csv(EVIDENCE/'rpeak_boundary_exceptions.csv',index=False)
    person_hrv=rp.groupby(['experiment','participant_id','session'])[['rms_rr_seconds','true_rmssd_seconds','median_hr_bpm']].mean().reset_index()
    person_hrv.to_csv(EVIDENCE/'hrv_person_session_comparison.csv',index=False)
    bp=peaks[peaks.event_type=='breath_peak']
    breathing=bp.groupby('experiment').agg(files=('path','count'),peak_count=('peak_count','sum'),duplicates=('duplicate_peaks','sum'),median_file_breaths_per_minute=('median_breaths_per_minute','median'),min_file_breaths_per_minute=('median_breaths_per_minute','min'),max_file_breaths_per_minute=('median_breaths_per_minute','max'),max_broad_interval_failure_fraction=('breath_interval_outside_4_60_bpm_fraction','max')).reset_index()
    breathing.to_csv(EVIDENCE/'respiration_peak_summary.csv',index=False)
    traits_rows=[]
    for e,g in traits.groupby('experiment'):
        traits_rows.append(dict(experiment=e,people=len(g),female=int((g.Sex=='Female').sum()),male=int((g.Sex=='Male').sum()),ASRS_complete=int(g.asrs_q1.notna().sum()),digit_span_nonmissing=int(g.digit_span.notna().sum()),digit_span_outside_declared_3_7=int(((g.digit_span<3)|(g.digit_span>7)).sum()),GPA_numeric=int(g.GPA_numeric.notna().sum()),GPA_zero=int((g.GPA_numeric==0).sum()),GPA_gt_4=int((g.GPA_numeric>4).sum())))
    traits_table=pd.DataFrame(traits_rows);traits_table.to_csv(EVIDENCE/'traits_summary.csv',index=False)
    outcome=memory.groupby('experiment').agg(people=('qualified_participant_id','nunique'),videos=('canonical_video_id','nunique'),person_video_pairs=('participant_id','count'),mean_partial=('normalized_partial_score','mean'),SD_partial=('normalized_partial_score','std'),floor_pairs=('normalized_partial_score',lambda x:sum(x==0)),ceiling_pairs=('normalized_partial_score',lambda x:sum(np.isclose(x,1))),min_items=('unique_items','min'),max_items=('unique_items','max')).reset_index()
    outcome.to_csv(EVIDENCE/'outcome_summary.csv',index=False)
    gates=pd.DataFrame([
      ('OQ-01','RESOLVED','All five files match official size and MD5; SHA-256 retained. Embedded 1.0.0 names are stale export metadata.'),
      ('OQ-02','RESOLVED FOR RELEASE KEYS / BOUNDED','Keyed participant/stimulus joins and unmatched ledger; surplus IDs excluded. Original randomized answer logs and cross-person identity not independently validated.'),
      ('OQ-03','RESOLVED WITH QUARANTINE','All item scores reconstruct; partial versus exact correctness distinguished; one Exp.3 person/video duplicate quarantined; aggregate rounding explained.'),
      ('OQ-04','RESOLVED FOR PROVISIONAL QC','Exact counts and released-grid validity unions computed. Basic QC is not full artifact certification or a final inclusion protocol.'),
      ('OQ-05','RESOLVED FOR RELEASE IDENTITY / BOUNDED','11 URL identities, local-task/session/exposure/condition map; Exp.4 different videos. Acquired clip hashes/order logs unavailable.'),
      ('OQ-06','BLOCKING / PARTIAL','Raw sidecars declare 0.3 Hz, descriptor/prior papers differ; derivatives have no per-file execution provenance. Native clock mappings, exact options, annotations and physical scaling remain unverified.'),
      ('OQ-07','RESOLVED METRIC SEMANTICS / BOUNDED','R-peaks are ordered stimulus-relative seconds with plausible RR and ECG correspondence; notebook formula is RMS RR, not RMSSD. Original executed figure inputs remain unavailable.')],columns=['gate','status','evidence_or_limit'])
    gates.to_csv(EVIDENCE/'p0_gate_status.csv',index=False)
    write('download_and_version_audit.md',f'''# Download and version audit — 2026-10-02

**EMPIRICALLY VERIFIED IN THIS AUDIT.** All five archives from [Zenodo record 22968459](https://zenodo.org/records/22968459), DOI 10.5281/zenodo.22968459, version 1.1, publication date 2026-09-25, were downloaded, streamed through MD5 and SHA-256, and atomically promoted from resumable `.part` files. Total verified canonical bytes: **{total:,}**. Official license metadata says CC BY 4.0.

{table}

Sources and UTC start/completion timestamps: [download_manifest.json](evidence/download_manifest.json). [Exact API snapshot](evidence/zenodo_record_22968459.json); [official correction changelog snapshot](evidence/official_changelog.html). The API's five objects establish independent per-experiment acquisition. One MiB/64 KiB range probes inspected the ZIP directories and small metadata before full transfers. Sequential transfer was replaced by six bounded 16 MiB range workers, reusing the completed prefix. Each worker writes into a single archive, syncs it, and records a local chunk hash. Retried 429 responses did not invalidate final official checksum matches. There are no duplicate full-data transfers or extracted waveform trees.

Canonical ZIPs are read-only under `data/bbbd/canonical_source/` and excluded from Git. Source files were never edited. Inner `dataset_description.json` names retain “1.0.0”; that is an **empirically observed contradiction**, not grounds to relabel checksum-matched 1.1 bytes as an older download. [Release versus pinned code fingerprints](evidence/release_vs_code_quiz_fingerprints.json) show exact Exp.4/5 quiz byte identity; Exp.1–3 differ in serialization but match after parsing and key sorting. A code commit date alone does not prove correction absence.
''')
    write('archive_manifest.md',f'''# Archive inventory

**EMPIRICALLY VERIFIED IN THIS AUDIT.** {len(inv):,} ZIP members, {inv.bytes.sum():,} member bytes. Outer ZIP entries use stored compression; many TSV members already contain gzip data. A complete second extracted tree would add approximately {inv.bytes.sum()/1024**3:.2f} GiB.

{md(archive,['archive','members','member_bytes','local_bytes'])}

[archive_members.parquet](evidence/archive_members.parquet) retains member path, bytes, compressed bytes, CRC32, method, directory indicator and offset. `CRC32` is an official member-integrity field, not a cryptographic identity. Archive cryptographic verification is in [download audit](download_and_version_audit.md). Archive roots are separate datasets; never flatten them into a shared `sub-XX` tree.
''')
    write('preprocessing_provenance.md','''# Released preprocessing provenance — bounded trace

**VERIFIED FACT** below means a documented method or inspected upstream implementation. **EMPIRICALLY VERIFIED IN THIS AUDIT** means a declaration, format or numerical property actually read from the five verified ZIPs. Neither a declaration nor a plausible spectrum proves execution of a particular filter.

| Stream | Native acquisition — documentary | Synchronization/export | Filtering/artifact handling — documentary | Actual release evidence | Unresolved execution link |
| --- | --- | --- | --- | --- | --- |
| EEG | BioSemi, 64 scalp channels, 2048 Hz | Documented shared triggers/clock correction, low-pass/downsample to 128 Hz | Descriptor/P03 0.05 Hz high-pass; public function 0.3 Hz; P04 0.5 Hz; 60 Hz notch, optional RPCA/EOG regression, interpolation | BDF headers: 64 channels, 128 Hz, uV; raw JSON declares 0.3 Hz fifth-order Butterworth and 60 Hz notch, reference “none”; binary events delimit padded export | Exact derivative high-pass/reference/options, fit scope and interpolation annotations absent; raw declaration is not an executed derivative recipe |
| ECG / R-peaks / HR | BioSemi electrical waveform, 2048 Hz | Released raw/filtered waveforms 128 Hz; peaks retain fractional seconds | Descriptor high-pass/notch/manual peak review; public code 0.5–25 Hz band-pass, thresholds/annotation options and rate rejection | Waveforms, ordered peak timestamps and derived HR actually present; waveform/peak consistency quantified; raw JSON says mV | Filter/manual choices, original annotations, physical scaling and derived HR implementation lineage unavailable |
| EOG | Six BioSemi auxiliary channels, 2048 Hz | Raw export 128 Hz | May enter EEG least-squares nuisance regression | Six numbered exported channels and numerical distributions checked | Participant-specific anatomical montage and exact EEG regression fit scope absent |
| Gaze / pupil | EyeLink, 500 Hz, calibrated screen gaze/tracker pupil units | Released raw/processed arrays 128 Hz | Outlier/blink-buffer interpolation; public code pupil/head regression and normalization, coordinate variants | Gzip headerless arrays and seconds correction intervals present; original intervals and invalidity unions retained | Exact buffer/options/coordinate or pupil-transform variant and original native observations not independently traced |
| Respiration / breath rate | BioSemi chest-tension belt, 2048 Hz | Raw belt and derived rate on 128 Hz grid | Public code polarity choice, 0.05–25 Hz peak-detection filter, rate eligibility/interpolation, Hilbert amplitude proxy | 546 waveforms/peak sequences; broad 4–60/min interval checks and coarse low-frequency PSD; raw JSON says mV | Scaling/calibration, executed polarity/filter/peak options and native saturation bounds absent |
| Head / eye events | EyeLink target geometry, 500 Hz; tracker-detected events | Exported head coordinates and event tables | Code includes transformed motion/rate proxies | Head X/Y tracker pixels, Z camera distance in mm; no Exp.1 head file; event presence inventoried | No calibrated orientation/full pose; exact exported transformations and independent event-detector validation absent |

The complete raw sidecar declarations/fingerprints are in `metadata_expN.parquet`; [pinned upstream code](evidence/upstream_code_5109afa.zip) is separate from [the exact audit execution source](evidence/audit_execution_code.zip). Reviewed methods and locators remain in [selected-dataset modalities](../selected_dataset/modalities.md) and [code audit](../selected_dataset/evidence/code_audit.md). There are no per-file derivative JSON sidecars or execution logs establishing the missing edges.

**OPEN QUESTION / blocking OQ-06:** establish the exact executed v1.1 recipe and scaling, or a scientifically adequate documented and explicitly authorized reconstruction route. No source was re-filtered, re-referenced, corrected or silently repaired in this pass. The release is verified as bytes, while physiological interpretation and globally fitted preprocessing remain conditional.
''')
    write('dataset_manifest.md',f'''# Canonical dataset manifest

**EMPIRICALLY VERIFIED IN THIS AUDIT.** [canonical_manifest.parquet](evidence/canonical_manifest.parquet) contains {len(f):,} physical continuous-signal records and {len(manifest)-len(f):,} explicit absent-modality/derivative placeholders. [exposure_tensor.parquet](evidence/exposure_tensor.parquet) contains {len(ex):,} design-expected person/video exposures. [stimulus_map.csv](evidence/stimulus_map.csv) maps local task IDs to 11 canonical YouTube identities.

{md(overview)}

Identifiers use `exp-N:sub-XX`. The record key is experiment + participant + session + local stimulus + representation + modality/member path. Each physical record includes canonical video, exposure number, condition, file bytes, rate evidence, sample counts, observed/QC/valid durations, channel names, units, NaN/Inf/zero counts, padding, correction/event/quiz/metadata availability, QC reasons, and keyed outcome reference/values. `outcome_id` joins the separate [quiz_video_outcomes.parquet](evidence/quiz_video_outcomes.parquet). Traits remain a keyed participant table. This normalized relation prevents duplicating quiz items across modality rows while preserving outcome availability.

Sampling is 128 Hz in inspected BDF headers/raw sidecars. Derivative TSV rates inherit the documented export grid and counterpart timing; absent derivative sidecars are recorded, not invented. Units for derivatives are explicitly unverified. All continuous raw/author-processed streams for EEG, ECG, EOG, gaze, pupil, head, respiration and HR/breath rates were streamed. Blink/saccade/fixation presence is inventoried; those event detectors were not independently validated.

`data_role` separates aligned raw signals, author-processed signals and derived HR/breath-rate features. Questionnaire availability is resolved from observed participant/video rows: complete ASRS item coverage, nonmissing digit-span score or at least one observed video-feedback field. These three fields are also separate; availability does not establish pre-exposure chronology. Final `peak_qc.parquet` uses distinct respiratory interval/rate fields; old experiment peak checkpoints are intermediate input, not the canonical semantic table.

`invalid_sample_bits` is a compact, little-endian packed Boolean invalid/correction union, with length `qc_sample_count`. [masks_expN.parquet](evidence/masks_exp4.parquet) preserve original correction intervals as seconds, not discarded labels. Valid durations count finite/range-valid samples minus released eye-mask unions. EEG's unreleased correction history is unknown. Whole-video usability is provisional; a pass does not certify a neural or clinical measurement.

No native 2048/500 Hz arrays, original clock-fit logs, acquired stimulus movies/hashes or independent acquired-video order log were found in the archives. Canonical URL identity is stronger than local stimulus numbering but does not establish byte-identical acquired trims.
''')
    quiz_summary=pd.DataFrame(json.loads((EVIDENCE/'quiz_audit.json').read_text()))
    un=joins[joins.status=='unmatched']
    write('quiz_integrity.md',f'''# Quiz integrity

**EMPIRICALLY VERIFIED IN THIS AUDIT.** All {len(items):,} item-row scores reconstruct from the supplied answer selections and answer keys with absolute tolerance 1e-8. Experiments 1–2 use equality of single answer/key. Experiments 3–5 use `number of selected correct options / number of correct options`. Extra wrong selections do **not** lower that partial score. In 4–5, `is_correct` requires exact selected/key set equality. Partial and exact outcomes must remain separate; fractional credit is not automatically a binomial count.

{md(quiz_summary.drop(columns=['scoring']))}

There are {len(un)} unmatched participant-level phenotype records: [complete ledger](evidence/participant_quiz_join_ledger.csv). They are surplus relative to the release participant/signal keys, not reassigned by row order. Signal-participant to metadata and participant to aggregate quiz are one-to-one at person/video scope; person/video to item responses is one-to-many. Repeated viewing creates one outcome potentially linked to two exposures, not two independent outcomes. Exact join validations reject ambiguous video mappings.

**Quarantine:** Exp.3 `sub-01`, stim03, question11 occurs twice with different answers/scores, while question12 is absent. The complete 12-row aggregate sums correctly but has only 11 distinct question numbers. Its person/video outcome is excluded from valid-outcome counts. Neither row was silently relabeled or removed from source. Exp.5 sub-09 is absent from corrected participant and quiz source keys; no local renumbering was attempted.

Video totals reconstruct. Exp.4/5 aggregate partial totals have {int(ag[ag.experiment>=4].aggregate_total_mismatch.sum())} differences above 1e-8, all no greater than {ag.aggregate_absolute_error.max():.8f}, consistent with four-decimal serialization; none exceed 0.000051. Exact totals match supplied `total_correct`. Exp.1–3 aggregates match at numerical precision. [Aggregate comparison](evidence/quiz_aggregate_comparison.parquet).

**OPEN QUESTION:** supplied key consistency is not an independent reconstruction from original randomized-option response logs. Original publications' internally used labels cannot be inferred from the current release. The release's no-penalty partial-score rule contradicts the penalty description retained in the historical review/P01 methods; neither is silently made consistent with the other.
''')
    write('modality_coverage.md',f'''# Modality coverage and provisional usability

**EMPIRICALLY VERIFIED IN THIS AUDIT.** Counts are experiment-qualified people and person/video exposures, never windows. `eye` requires both author-processed gaze and pupil. EEG/ECG/head use author-processed files; EOG/respiration use released raw files because corresponding cleaned waveform derivatives are not supplied. Raw and processed coverage are also retained separately.

{md(compact)}

Valid hours are exact sample-mask unions over the common **released** 128 Hz grid, including event-trimmed EEG bounds; this does not establish latent cross-device synchronization precision. Counts with valid quiz include direct test chronology only: session1 in 1–3, session2 stim01–03 in 4, session2 in 5. Exp.5 first viewing has the later final outcome as an explicitly indirect relation and is not counted twice.

Per-experiment complete EEG+ECG+eye+quiz after provisional QC:

{md(core,['experiment','people','person_video_exposures','videos','valid_hours'])}

[All combinations and experiments](evidence/modality_intersections.csv); [physical raw/processed coverage](evidence/physical_coverage.csv); [missing-file placeholders](evidence/missing_files.parquet). Presence, intrinsic numerical validity, correction burden and eligibility are distinct. Current QC thresholds were set for this audit, not tuned against outcomes; they are candidates for later sensitivity analysis, not a frozen paper inclusion policy.
''')
    write('signal_quality.md',f'''# Dataset-wide signal QC

**EMPIRICALLY VERIFIED IN THIS AUDIT.** Streamed all {len(f):,} relevant continuous files, yielding {len(c):,} recording/channel summaries. Parser failures: {int(sum(f.qc_status=='parse_error'))}. Gzip/ZIP members were read to completion; BDF24 calibration, record lengths and channel rates were checked. One EEG recording is at most a bounded series of 32-second chunks; TSV parsing uses 8192-row chunks. No signal-format copy was created.

{md(coverage)}

The [deterministic config](../../../audit_config.json) defines basic screening: >1% nonfinite values, >95% exact zeros, whole-file flatness (more than eight EEG channels or all channels of another modality), and >50% eye invalid/corrected samples. The 16 Hz threshold is **flag only**. Saturation at export digital limits is tabulated but must not be equated with native ADC saturation: BDF exporters choose a per-file physical range. EEG amplitude/variance and PSD bands, 60 Hz and 16 Hz excess, channel availability and extreme variance ratios are retained.

These thresholds do not detect every artifact, guarantee neural origin, or certify clinical-grade ECG. [Channel tables](evidence/channel_qc.parquet), [numeric summary](evidence/modality_qc_summary.csv), [regional finite constant runs](evidence/physiology_flat_runs.parquet). EOG numbering is ch1–ch6, with no verified participant-specific anatomical montage; missing/flat channels can be counted, but their anatomical equivalence cannot be assumed. Head X/Y are tracker pixels and Z is camera distance in mm; this is not full calibrated 3-D pose. Exp.1 contains no head stream in the verified ZIP.

## Remaining measurement limits

NaNs cannot survive a BDF integer representation; zero NaN count in BDF does not prove acquisition/processing had no missing samples. Exact physical zeros may become one-LSB values during export. Native ADC clipping limits and EEG correction masks are not released. Canonical ECG/respiration sidecars declare mV while numerical excursions reach thousands of declared units; physical voltage scaling needs upstream confirmation. Do not silently convert units or infer cardiac morphology from an unverified scale.
''')
    write('eeg_quality.md',f'''# EEG quality and 16 Hz characterization

**EMPIRICALLY VERIFIED IN THIS AUDIT.** The full channel map is [eeg_contamination_map.parquet](evidence/eeg_contamination_map.parquet): experiment × participant × session × canonical video × channel × raw/processed status. Every analyzed BDF has 64 exported channels at 128 Hz; labels/units are read from the binary header. Sidecars' fixed `RecordingDuration=0.5` contradict actual minutes-long recordings and are not used as duration evidence.

{md(eeg)}

PSD uses 8-second Hann/Welch segments (0.125 Hz bins) inside bounded chunks, with segment-count weighting. 16 Hz excess is 10log10(mean PSD15.75–16.25 / mean PSD14.5–15.5 and16.5–17.5). Sensitivity flags at 3/6/10/20 dB, fraction of 0.5–45 Hz power at the peak, 60 Hz excess and band powers are retained. A >10 dB peak is a screening flag, not proof of instrumental origin. The authors' instrument warning is an **AUTHOR-REPORTED LIMITATION**; measured peak magnitudes are **EMPIRICALLY VERIFIED IN THIS AUDIT**. Negative and unaffected recordings remain in the map.

![16 Hz distribution](figures/eeg_16hz.png)

![Participant/channel contamination map](figures/eeg_contamination_map.png)

![QC-directed deep spectra](figures/targeted_eeg_spectra.png)

[Target selection ledger](evidence/targeted_inspection_ledger.json) chooses the greatest excess in each representation without using quiz outcomes. Exp.5 raw peaks can be strong while processed counterparts lack a >10 dB narrow peak; this does not prove the exact cleaning operation or its neural-information consequences. A 48 Hz peak is also visible in both targeted spectra; its possible relation to the third harmonic of 16 Hz is **OUR INFERENCE**, not source attribution. The 48 Hz magnitude was not quantified dataset-wide in this pass. Exp.4 residual peaks require recording/channel-specific sensitivity analysis. Do not reject an experiment or interpret beta-band/coupling content automatically from these flags.

Extreme variance flags are a descriptive >100 ratio to the record's median channel variance. Flatness and band anomalies should guide additional artifact assessment and alternative preprocessing once provenance is resolved. No re-referencing, filtering, rejection or source modification was performed.
''')
    write('ecg_quality.md',f'''# ECG, R-peaks and HRV semantics

**EMPIRICALLY VERIFIED IN THIS AUDIT.** R-peak files have a `timestamp` header and fractional stimulus-relative seconds; RR magnitudes and corresponding waveform extrema support that interpretation. Native detection timestamps are not restricted to the 128 Hz waveform grid.

{md(heart)}

Timestamp order, duplicate/nonmonotonic peaks, broad RR bounds (0.3–2 s), author-range bounds (40–160 bpm), waveform bounds and local ±100 ms extrema were checked. Per-record peak failures are retained in [peak_qc.parquet](evidence/peak_qc.parquet). Local extrema agreement is a waveform/peak consistency diagnostic; a median offset of zero on a sampled ECG is not device synchronization accuracy or independently adjudicated detection sensitivity.

**Boundary exceptions:** five final R-peaks fall 0.00127–0.00649 seconds beyond their released filtered-waveform exclusive end, all less than one 128 Hz sample. The [exact exception ledger](evidence/rpeak_boundary_exceptions.csv) retains the timestamps and durations. This is compatible with export-grid quantization, but it is not independent proof of the native-clock transformation. No peaks were moved or removed. Median absolute local-extremum offset across files has overall median 0 and maximum file median 0.0234375 seconds; this supports local temporal correspondence rather than adjudicated detector accuracy.

**Metric definition resolved:** notebook `sqrt(mean(diff(peak_times)**2))` computes RMS RR. Successive-RR RMSSD is `sqrt(mean(diff(diff(peak_times))**2))`. Both were computed from the same released timestamps without changing supplied peaks. [Person/session comparison](evidence/hrv_person_session_comparison.csv) averages file metrics like the notebook; experiment4 combines attentive blocks only when explicitly described. The manuscript's executed input/version and exact Figure6 numerical reproduction remain open; the mathematical definition mismatch is now demonstrated with actual release inputs.

![HRV statistic comparison](figures/hrv_semantics.png)

No silent peak correction, ectopic removal, clinical interpretation or replacement of upstream HR values was made. RMS RR largely reflects mean interval and cannot be treated as beat-to-beat variability. A valid future HRV analysis must define beat editing, finite intervals, duration eligibility, units and the chosen metric.
''')
    write('eye_quality.md',f'''# Eye and pupil quality

**EMPIRICALLY VERIFIED IN THIS AUDIT.** Both raw and processed continuous eye files in this release are gzip-compressed and headerless. Correction interval files have `start_time/end_time` headers in seconds. Original masks remain first-class evidence, alongside conservative floor/ceil mapping to the 128 Hz released grid. No masks were replaced by a smooth signal's apparent completeness.

{md(eyes)}

![Correction burdens](figures/eye_correction.png)

Masks are unioned with nonfinite samples, nonpositive pupil values and off-screen gaze coordinates (1920×1080) for provisional validity. Off-screen gaze may include meaningful looking-away behavior, so this is a measurement eligibility flag, not an inattentive label. Reported correction gaps include grid quantization of at most approximately two samples per interval; exact original intervals are retained for alternative rules.

[Condition/video summaries](evidence/eye_quality_by_condition_video.csv); [missingness map](evidence/missingness_map.parquet). Masks encode upstream correction intentions; absent originals/native logs prevent independently proving that every interpolated sample or every bad observation was marked. Missing processed files are distinct from a large correction burden in an existing file. Whole-file pupil IQR/variation cannot automatically be called dilation; head-regression and normalization provenance remain unresolved for exported variants.
''')
    resp=f[f.modality.isin(['respiration','breath_rate'])]
    write('respiration_quality.md',f'''# Respiration and auxiliary streams

**EMPIRICALLY VERIFIED IN THIS AUDIT.** Respiration is confined to experiments4–5. Raw belt-waveform and derived breath-rate presence, amplitude ranges, whole-file variance, finite/zero values, exact constant runs and low-frequency PSD were audited. [Respiration/channel summaries](evidence/channel_qc.parquet), [regional flat runs](evidence/physiology_flat_runs.parquet), [breath peak timestamps](evidence/peak_qc.parquet).

{md(coverage[coverage.modality.isin(['respiration','breath_rate'])])}

{md(breathing)}

The 8-second PSD estimator provides only coarse respiration-frequency characterization: its 0.125 Hz resolution limits slow-rate discrimination. Derived breath-peak intervals provide a separate author-processed rate proxy. The exporter/pipeline uses a chest-tension belt and Hilbert-envelope “volume”; neither is calibrated tidal volume. Do not apply ECG plausibility thresholds to breath peaks merely because both are stored in the same peak table. Native belt saturation limits and exactly executed peak/filter options remain unknown.

EOG and head coverage is in [signal QC](signal_quality.md). EOG six-channel numbering does not supply an anatomical montage. Head position is tracker target geometry, not orientation/pose; transformed “velocity” semantics in the pinned code are unconventional and were not treated as ordinary derivatives of 3-D displacement.
''')
    spread=timing.raw_duration_spread_seconds.dropna();eegdiff=timing.eeg_vs_other_duration_seconds.dropna()
    write('synchronization_audit.md',f'''# Synchronization and timing audit

**EMPIRICALLY VERIFIED IN THIS AUDIT.** Raw non-EEG modality boundary spread has median {spread.median():.6f}s, 95th percentile {spread.quantile(.95):.6f}s and maximum {spread.max():.6f}s across {len(spread)} exposures. Event-trimmed EEG minus median other raw duration has median {eegdiff.median():.6f}s, 95th absolute percentile {eegdiff.abs().quantile(.95):.6f}s and maximum absolute {eegdiff.abs().max():.6f}s. [Per-exposure boundaries](evidence/timing_boundaries.parquet).

The exported events contain start/end markers generated from array length. End onset = n_samples/128 is an **exclusive** boundary; its one-sample marker duration is not an additional recorded sample. BDF records extend to whole seconds; all inferred padded rows are checked against one export-calibration LSB. `[RecordingDuration=0.5]` is stale/malformed metadata and not an actual recording length. Finite sample-count mismatch is retained, not rounded away.

**OPEN QUESTION.** Native shared flash/beep trigger sequences, clock-fit coefficients and residuals are not present in these event files. Two synthetic array-boundary markers do not permit dropped-native-trigger, clock-drift or residual-latency estimation. ECG/R-peak agreement verifies those two related derivatives, not EEG–eye device alignment. No millisecond precision is inferred from a common 128 Hz grid.

**OUR INFERENCE — recommendation:** whole-video aggregation is the safest supported analysis, after excluding absent/invalid regions. Multi-second windows may be explored with boundary/mask sensitivity and explicit unmeasured alignment uncertainty; exact safe window length cannot be certified. Sub-second coupling, phase, directional or lag claims are insufficiently verified. Reliable item-to-content timestamps are also absent, constraining C05 independently of alignment.
''')
    selection=pd.read_csv(EVIDENCE/'outcome_selection_diagnostics.csv')
    write('missingness.md',f'''# Missingness and selection

**EMPIRICALLY VERIFIED IN THIS AUDIT.** [missingness_map.parquet](evidence/missingness_map.parquet) separates design absence, expected file absence and provisional QC flags. Raw-versus-processed absence remains explicit in the canonical manifest; a processed file is never silently replaced by a raw waveform in complete-case counts. Exp.1 electrical streams and pre-4 respiration are absent by design. Exp.1 head is not released despite conflicting documentation. Partial invalidity and heavy interpolation are sample/file-level states, distinct from absent streams.

Directly linked quiz outcomes by processed-eye basic-QC status:

{md(selection)}

These are **EXPLORATORY selection diagnostics**, not causal evidence or significant outcome differences. People contribute multiple video observations and the group-specific person counts can overlap. [Trait diagnostics](evidence/missingness_trait_diagnostics.csv) use person-level availability fractions and observed traits without imputation. [Experiment/condition counts](evidence/missingness_by_condition.csv) and [video/correction burdens](evidence/eye_quality_by_condition_video.csv) expose protocol/content dependence. Score references across repeat exposures in the condition table are explicitly descriptive; the direct-outcome table does not duplicate outcomes across sessions.

**OUR INFERENCE.** Complete-case filtering changes the cohort and can select viewing behavior/trait profiles; missing-at-random is not established. Uniform random modality masking is not a validated model of these failure mechanisms. Preserve masks and failure ledgers; a future protocol must report excluded people, videos and durations and assess sensitivity at predefined correction thresholds.
''')
    write('outcome_characterization.md',f'''# Outcome and participant characterization

**EMPIRICALLY VERIFIED IN THIS AUDIT.** {len(memory)} unambiguous, keyed memory person/video outcomes for {memory.qualified_participant_id.nunique()} experiment-qualified participants across {memory.canonical_video_id.nunique()} videos. These are phenotype outcomes; direct usable signal/outcome counts can be smaller.

{md(outcome)}

[Item difficulty](evidence/item_difficulty.csv), [video summaries](evidence/outcome_by_video.csv), [within-person variation](evidence/outcome_person_variation.csv). Fractional versus exact-set correctness produce different distributions; denominators and item counts are retained. Recognition/comprehension tags are not released as a validated taxonomy. Experiments1–2 distinguish domain/memory; chronology of Exp.1 domain rows still conflicts with the protocol emphasis. Experiments3–5 contain memory questions without those semantic subtype labels.

**Negative finding requiring review:** Exp.2's mean video score is approximately0.257, near the0.25 benchmark for uniform four-option single-response guessing, versus approximately0.650 in Exp.1. This descriptive comparison does not identify a protocol effect or demonstrate erroneous labels. The supplied Exp.1/2 correct option codes are uniformly1, so original randomized-option canonicalization should be verified before strong behavioral claims or pooled outcome use. Key-consistent scoring alone cannot independently certify that transformation. For3–5, selecting every option can receive full partial credit even when exact-set correctness is zero;98 released rows have full partial credit plus an extra wrong selection. Original scores are retained without silently imposing a penalty.

{md(traits_table)}

ASRS items are 0–4 and supplied Likert totals reconstruct for matched rows. Author-defined inattention/hyperactivity groupings have ten/eight items. Supplied subscales in2–4 equal item sums +10/+8, while5 has offsets0/0. Item-derived 0–4 sums are retained alongside supplied values; no instrument is redefined or screening result converted into diagnosis. Digit-span files exist more often than their scores are nonmissing; Exp.3 has zero values outside the declared3–7 range, with semantics unresolved. The weighted formula cannot be reconstructed without trial data. GPA contains zeros, values above4 and text missing codes; no clipping/imputation or assumed institutional scale was performed.

Feedback tables are actually released for2–5, partially resolving OQ-24. Exp.2/3 have engaging/enjoyable/educational;4/5 have watched-before/question-difficulty/prior-knowledge/educational. These are distinct schemas and are not a universal engagement variable. Missingness/coding remains in [phenotype coverage](evidence/phenotype_coverage.json) and keyed raw metadata evidence.

First-exposure versus repeat exposure is identified in the manifest. Exp.5 has a final test after repeat/preview/incentive, not separate first/repeat tests; no empirical learning-gain outcome can be created from that final score alone. No delayed-retention or clinical diagnosis outcome is supplied.
''')
    write('leakage_and_independence.md',f'''# Independence and leakage map

**EMPIRICALLY VERIFIED IN THIS AUDIT.** {ex.qualified_participant_id.nunique()} experiment-qualified participant records, {ex.canonical_video_id.nunique()} canonical videos, {len(ex)} design-expected exposures; independent outcome counts appear in [outcomes](outcome_characterization.md). Blocks are not independent longitudinal visits. Experiments1–3 and5 repeat videos;4 changes content by block. Person/video exposures are nested in people and crossed with shared videos, not independent windows.

[Formal leakage risk register](evidence/leakage_risk_register.json); [person/video/experiment graph](evidence/independence_graph.json). Cross-experiment same-human identity is unresolved; do not claim independently certified178 unique humans or infer identity from similar traits. The descriptor's participant count remains documentary recruitment evidence.

| Evaluation unit | Feasibility and limits |
| --- | --- |
| Unseen participant | Feasible within cohorts after grouping all blocks/videos by qualified participant; references/scaling/imputation must respect held-out groups. Cross-cohort same-human overlap needs an author statement. |
| Unseen canonical video | Mechanically feasible at11 identities overall, but only3–6 per experiment; item/content/difficulty and audiovisual covariates differ. Local stimulus holdout is insufficient. |
| Unseen participant + unseen video | A crossed holdout is mechanically possible; small independent video N limits precision. Disjoint person and video axes must be enforced simultaneously. |
| Cross-experiment | Protocol/preprocessing/availability shifts and shared videos are substantial; holding out an experiment does not hold out content. 4/5 share one upstream collection. |
| Cross-condition | In1–3 attention/arithmetic/order/repetition are inseparable; within-person condition contrasts do not establish a transferable latent-attention label. |
| Across exposure settings | First/repeat and incidental/intentional/incentive transport is possible descriptively with shared-video controls; not an isolated causal reward effect. |

Adjacent windows, future imputation/scaling, globally fitted artifact transforms, ISC templates, CorrCA/PCA references and repeated quiz targets all have explicit controls in the register. Fit scope of author preprocessing is not fully known; this cannot be retrospectively fixed by a final train/test split. No split was frozen or held-out predictive outcome inspected. This full-release integrity/distribution audit is **EXPLORATORY**; hypotheses chosen using it require a later locked protocol and untouched evaluation/external validation for confirmatory claims.
''')
    write('exploratory_multimodal_structure.md','''# EXPLORATORY multimodal structure

[Exposure summaries](evidence/exploratory_exposure_summaries.parquet) combine median EEG channel bands/variance, R-peak heart-rate/RMSSD, gaze/pupil correction burden, pupil variation, head summaries and belt variation using validated keys. No predictive model is fit. [Person-mean quality correlations](evidence/exploratory_quality_correlations.csv) are experiment-specific Spearman coefficients; no p-values or significance selection were performed. [Marginal group structure](evidence/exploratory_group_structure.csv) partitions descriptive variance by person, video or condition separately, without claiming adjusted causal effects.

Measures are scientifically interpretable only within their provenance limits. EEG spectral quantities can include ocular/cardiac/16 Hz artifacts; pupil/head dependence can arise from processing; respiration amplitude is uncalibrated. Between-modality quality association is not neural/autonomic coupling. No ISC/CorrCA/PCA or temporal lag estimator was fitted, since reference leakage and native timing have not been resolved. These tables support future design and selection analysis, not claims of multimodal predictive benefit.
''')
    candidates=[]
    for cid,title,level,mods,confound,timing_limit,occupied,second in [
      ('C01','Incremental behavioral information','MEDIUM','eeg+ecg+eye','Only11 videos; heterogeneous quiz scoring/chronology; selection and globally processed EEG','Whole-video plausible; derivative provenance unresolved','P03 multimodal quiz association and P04 EEG+trait models','Likely useful for external validation; labels must retain domain semantics'),
      ('C02','Reliability under observed sensor failure','MEDIUM','eeg+ecg+eye','Natural failure varies by experiment/person/video; quality-based selection','Whole-video quality/outcome analysis plausible; fine timing unsupported','P03 complete-case exclusions; explicit robustness occupancy not verified','Useful to test new sensor/population failures'),
      ('C03','Transport across experimental settings','MEDIUM','eeg+ecg+eye','4/5 share3 canonical videos; outcome after different exposure histories; cohort identity unknown','Aggregate transport only until clocks/provenance clarified','P03 replication/P04 spatial-filter transfer','Likely needed for genuinely external transport'),
      ('C04','Reduced-sensor outcome measurement','MEDIUM','ecg+eye','EEG teacher fit/reference scope; mixed labels; small independent content','Aggregate feasible; no lag-based teacher claim','P03 EEG-to-body linear prediction and P01 webcam precedent','Useful for an operational low-cost measurement claim'),
      ('C05','Temporal item-linked evidence','LOW','eeg+ecg+eye','No reliable item-content timestamps or device residuals; interpolation can span minutes','Insufficient for proposed fine timing/directional analysis','P02 frequency work and P03 10s temporal work','A dataset with native triggers/item timestamps likely necessary'),
      ('C06','Falsifiable representation benefit','LOW','eeg+ecg+eye','Small independent N;11 videos; P05/pretraining lineage unknown; stimulus shortcuts','Aggregate representations possible after provenance gate','CorrCA/PCA strong precedent; modern competitors not fully accessed','Likely necessary for robust representation/transfer claims'),
      ('C07','Reproducibility and measurement validity','HIGH','eeg','Current metric/key defects demonstrable; original executed inputs still missing','Released aggregate definitions auditable; exact original reproduction conditional','All P01–P04/descriptor predate or differ from current release','Not necessary to demonstrate release integrity; helpful for measurement generality')]:
        r=ints[(ints.experiment=='ALL')&(ints.modalities==mods)&(ints.stage=='basic_qc')&ints.requires_valid_quiz].iloc[0]
        candidates.append(dict(candidate=cid,direction=title,feasibility=level,usable_people=int(r.people),usable_videos=int(r.videos),usable_person_video_observations=int(r.person_video_exposures),modalities=mods,valid_outcome='keyed final memory quiz; score definitions separate',confounds=confound,generalization_unit='person + canonical video; protocol-specific estimates',independent_observations='people reasonable for simple analyses; content N small; no power guarantee',missingness='material, preserve masks and selection diagnostics',timing=timing_limit,prior_occupancy=occupied,second_dataset=second,evidence='modality_intersections.csv; quiz_items.parquet; channel_qc.parquet; p0_gate_status.csv; retained prior_work_matrix'))
    cf=pd.DataFrame(candidates);cf.to_csv(EVIDENCE/'research_feasibility.csv',index=False)
    write('research_feasibility.md',f'''# Research-question feasibility — no final question selected

**OUR INFERENCE** grounded in audited files. Counts below are the provisional basic-QC, directly linkable memory-outcome subset for the indicated sensor combination. A direction can need a smaller cohort once traits/reference/timing eligibility is imposed. These are ceilings for candidate design, not a power analysis or promised predictive accuracy.

{md(cf,['candidate','direction','feasibility','usable_people','usable_videos','usable_person_video_observations','modalities'])}

{md(cf,['candidate','confounds','timing','prior_occupancy','second_dataset'])}

[Complete feasibility matrix](evidence/research_feasibility.csv) also records generalization unit, independent-observation limits, outcomes, missingness and evidence paths. C07 HIGH refers to released measurement/integrity auditing; exact published-analysis reproduction remains MEDIUM/conditional on original inputs. C02's measured masks are valuable but are not proof that robustness/calibration can be evaluated without selection bias.

Reframe C01/C04 as incremental, independently evaluated behavioral information rather than generic physiology-to-learning novelty. Reframe C03 as protocol/exposure transport, not isolated reward causality. Abandon sub-second/directional C05 claims on the current release until native timing and item alignment exist; multi-second descriptive alternatives would still need sensitivity controls. Defer architecture-led C06/foundation-model work until the competitor/pretraining and sample-size gates are resolved. Long-term learning gain, clinical diagnosis and a pure attention biomarker are unsupported outcome interpretations. No candidate is chosen.
''')
    write('open_questions_resolved.md',f'''# P0 gate disposition and bounded resolutions

{md(gates)}

Resolved or substantially bounded additional issues: OQ-09 now has a full16 Hz channel map; OQ-11 has preserved correction intervals and invalidity unions; OQ-12 has binary rates/scaling, exclusive event bounds and verified one-LSB padding; OQ-21 has deidentified phenotype coverage/coding checks; OQ-22 has observed per-modality hours rather than website totals; OQ-23 confirms no Exp.1 head files; OQ-24 verifies feedback table presence and distinct schemas. These do not imply that native annotations, physiological units or historical score provenance were recovered.

Evidence categories are scoped: numerical file checks are **EMPIRICALLY VERIFIED IN THIS AUDIT**; author caveats stay **AUTHOR-REPORTED LIMITATION**; judgments about safe analyses/novelty stay **OUR INFERENCE**; missing execution/identity/timing information stays **OPEN QUESTION**. Historical inference IDs are preserved with explicit new amendments.
''')
    write('open_questions_remaining.md','''# Remaining issues before Research Gap & Problem Formulation

1. **Blocking OQ-06:** obtain the exact v1.1 processing execution/configuration per representation (EEG high-pass0.05/0.3/0.5, reference, RPCA/EOG/interpolation scope/options, ECG filter/peak correction choices, resampling kernels/clock transforms, physical ECG/respiration units). Raw sidecars and a pinned MATLAB function do not establish the executed derivative pipeline. Either obtain execution provenance or establish an explicitly authorized reproducible processing route from a sufficiently documented source; do not silently retrofit the release.
2. **OQ-02/03 bounded integrity exceptions:** confirm surplus phenotype IDs and the Exp.3 sub-01/stim03 duplicated q11/missing q12; quarantine is usable now, original identity/response logs are not reconstructed. Clarify no-penalty release scoring versus historical penalty prose.
   Verify Exp.2 original answer-order canonicalization or an authoritative mapping audit before treating its near-chance aggregate scores as established behavioral performance differences; this is a consequential outcome-encoding review, not proof that its labels are wrong.
3. **OQ-07/08/15 reproduction limits:** original Figure6 inputs/execution and original paper cohort/label maps are unavailable. Current RMS-RR and true RMSSD are computed, but historical numerical effects are not attributed without those inputs. Pupil caption/statistic distinctions remain.
4. **OQ-10/14/16:** native timing residuals, allocation/exposure chronology and privacy-preserving cross-experiment person-overlap certification are absent. Aggregate video analysis is safer; timing/causal/person-independence claims need these checks.
5. **OQ-19/24:** digit-span zero/weighted-score semantics, GPA zero/above4 coding, item recognition/comprehension labels and item-content timestamps remain incomplete. ASRS subscale offsets are empirically resolved from items without clinical interpretation.
6. **OQ-17/18/26/27:** P05/full supplements, code/video reuse licensing details and future pretrained-model manifests remain outside this waveform audit. Retain the prior bounded search; no invented novelty or licensing clearance.

[Concrete author-query draft](evidence/author_query_draft.md) is prepared but not sent. No authors, collaborators or external recipients were contacted.

## NEXT_STAGE_RECOMMENDATION

**Resolve OQ-06's derivative execution/scaling provenance first, and review Exp.2 answer-order canonicalization before behavioral pooling.** The acquisition, release-key scoring, coverage and lightweight QC substrate now support focused scientific feasibility discussion, but the critical preprocessing gate is not sufficiently resolved for an unconditional transition. After recording a satisfactory provenance resolution and maintaining the stated outcome/quarantine/timing boundaries, proceed to **Research Gap & Problem Formulation**. Do not start model development or select the final problem in this pass.
''')
    write('README.md',f'''# Dataset Exploration & Empirical Readiness Report

Audit date: **2026-10-02**. Selected source: **BBBD v1.1, Zenodo22968459, released2026-09-25**. All five archives acquired and checksum-verified; all relevant continuous streams received dataset-wide lightweight QC. No predictive model, architecture search, performance optimization, final paper question or final split was developed.

The result is a queryable, reproducible release audit with a remaining **blocking preprocessing-provenance gate (OQ-06)**. The archive/scoring/intersection questions are substantially resolved; native timing, original execution logs and historical published-input lineage remain unavailable. Passing basic QC is a provisional numerical screen, not final scientific certification.

## Evidence and report index

- [Download/version](download_and_version_audit.md), [archive inventory](archive_manifest.md), [canonical manifest](dataset_manifest.md), [quiz integrity](quiz_integrity.md).
- [Modality intersections](modality_coverage.md), [all-signal QC](signal_quality.md), [EEG/16 Hz](eeg_quality.md), [ECG/HRV](ecg_quality.md), [eye/pupil](eye_quality.md), [respiration/auxiliary streams](respiration_quality.md).
- [Preprocessing trace](preprocessing_provenance.md), [timing](synchronization_audit.md), [missingness/selection](missingness.md), [outcomes/traits](outcome_characterization.md), [leakage/independence](leakage_and_independence.md), [EXPLORATORY multimodal structure](exploratory_multimodal_structure.md).
- [Candidate feasibility](research_feasibility.md), [P0 disposition](open_questions_resolved.md), [remaining gates](open_questions_remaining.md), [storage/retention](storage_and_retention.md), [machine-readable evidence](evidence/README.md).

## Answers to the readiness questions

1. **Correct release? Yes.** All five official file sizes/MD5s match; local SHA-256s and timestamps are retained. Embedded1.0.0 naming is stale metadata, explicitly recorded. Canonical total **{total:,} bytes**.
2. **What is on disk?** Five immutable ZIPs containing {len(inv):,} members, small source-metadata snapshots, {len(f):,} physical continuous-file manifest rows, compact validity masks, channel/peak/QC tables, seven scientific figures and reproducible modules/tests. No second full signal tree or converted full-dataset copy exists.
3. **Usable independent units?** {ex.qualified_participant_id.nunique()} experiment-qualified participants, {ex.canonical_video_id.nunique()} canonical videos, {len(ex)} design-expected exposures and {len(memory)} unambiguous phenotype memory outcomes. Scientific usable counts depend on modality, chronology and QC; the exact table follows. Cross-experiment unique-human identity is not independently certified.

{md(overview)}

4. **Exact modality intersections?** Full presence/QC/outcome counts and exact released-grid valid durations are in [modality_coverage.md](modality_coverage.md) and [CSV](evidence/modality_intersections.csv). Eye requires gaze+pupil, no raw fallback is disguised as processed data, and repeated outcomes are not counted as new tests.
5. **Correctly linkable outcomes?** Keyed video memory outcomes reconstruct;1–2 also include domain scores. Exp.3 sub-01/stim03 is quarantined. Extra phenotype IDs in1–3 remain unmatched. Partial credit in3–5 omits wrong-choice penalties;4–5 exact-set correctness is a different variable. Original answer-order logs remain unavailable.
6. **Strongest experiments?** **OUR INFERENCE:**2–3 support multimodal first-view quiz and qualified repeated arithmetic contrasts, within small cohorts;4 gives a single-exposure tested-video subset with respiration, but only3 tested videos;5 supports repeat/preview/incentive transport, not isolated reward or first-view learning.1 offers eye-only context. The exact complete-case table changes the headline cohort, so no experiment is chosen for a paper.
7. **Important QC problems?** Eye correction dominates attrition; some expected raw/processed streams are absent; integer EEG export loses original NaN semantics; EOG anatomical numbering and voltage scaling are not fully verified. Per-record reasons, absent-file placeholders and flat-run evidence remain queryable.
8. **16 Hz severity?** Quantified for every EEG channel/record and both representations, with3/6/10/20 dB flags and relative power. Peaks are localized rather than universal; processed/raw differences exist. No automatic rejection or neural/artifact attribution is made from a frequency peak alone.
9. **Eye interpolation?** Exact masks are preserved. Means, maxima and longest gaps by experiment/modality appear below. Some corrected spans last minutes; complete processed files are not equivalent to wholly observed samples.

{md(eyes)}

10. **Synchronization?** Boundary/sample-count agreement and padding are empirically checked. Synthetic array-boundary events contain no native clock-fit residuals. Whole-video aggregation is safest; multi-second windows are conditional exploratory analyses; sub-second/directional/lag claims are insufficiently verified.
11. **Leakage channels?** Participant/content repetition, adjacent windows, global preprocessing, ISC/CorrCA/PCA references, scaling/imputation, outcome duplication, quality/protocol shortcuts and post-exposure information are formally registered. Future controls must precede windowing/reference fitting.
12. **True experimental units?** People and canonical videos, with nested viewing blocks and crossed person/video exposures; repeated quizzes/targets are not independent windows. Experiment-qualified identifiers do not prove different humans across experiments. Only11 videos limits content-level uncertainty regardless of hours.
13. **Empirically feasible questions?** Whole-video incremental information, observed-failure reliability, reduced-sensor measurement and explicit protocol transport remain conditional MEDIUM candidates; release measurement/reproducibility auditing is HIGH for demonstrable definitions, conditional for original-paper replication. Exact counts/evidence are in the [feasibility matrix](research_feasibility.md).
14. **Abandon/reframe?** Abandon current-release millisecond/directional/item-timed C05 claims until timing/item alignment exists. Reframe generic fusion/quiz novelty around incremental independent information; reward around bundled transport; defer architecture-led C06. Long-term gain and diagnostic outcomes are unsupported.
15. **Unresolved before formulation?** OQ-06's actual derivative configuration/scaling is blocking. Surplus IDs/duplicate item are safely quarantined but not explained; original response/published-input lineage, unique-human overlap, allocation, native timing and weighted trait coding remain bounded open questions.
16. **Another dataset later?** **OUR INFERENCE:** likely useful for external validation of transport, robustness or content-independent physiological relationships. Antecedent BBBD subsets are not external validation. A second dataset needs compatible measurement semantics and separate outcome definitions; no indiscriminate pooling is proposed.
17. **Retained/deleted?** Canonical ZIPs, checksum ledgers, small/medium scientific evidence and generating code/config are retained. No full waveform derivative was generated or deleted. Verified temporary probes/font caches were deleted after evidence validation; superseded checkpoints were retained as history. Exact categories, bytes and recreation commands are in [retention report](storage_and_retention.md).

## Reproduction

The executed environment uses Python 3.14 on macOS; [locked dependencies](../../../requirements-audit.lock) record the exact library versions. Create an isolated environment and install the package to expose the `bbbd-audit` entry point, then run from repository root:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-audit.lock
.venv/bin/python -m pip install --no-deps -e .
```

```sh
PYTHONPATH=src .venv/bin/python -m bbbd_audit.cli inventory
PYTHONPATH=src .venv/bin/python -m bbbd_audit.cli download
PYTHONPATH=src .venv/bin/python -m bbbd_audit.quiz
PYTHONPATH=src .venv/bin/python -m bbbd_audit.cli audit
PYTHONPATH=src .venv/bin/python -m bbbd_audit.cli summarize
PYTHONPATH=src .venv/bin/python -m bbbd_audit.structure
PYTHONPATH=src .venv/bin/python -m bbbd_audit.regional
MPLCONFIGDIR=data/bbbd/temporary_cache/matplotlib PYTHONPATH=src .venv/bin/python -m bbbd_audit.figures
MPLCONFIGDIR=data/bbbd/temporary_cache/matplotlib PYTHONPATH=src .venv/bin/python -m bbbd_audit.deep
PYTHONPATH=src .venv/bin/python -m bbbd_audit.report
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python -m bbbd_audit.cli validate
```

`inventory` uses remote ranges only when a canonical ZIP is absent; verified downloads are skipped. `audit` checkpoints per experiment and automatically invalidates a cache when QC code, input tables or config changes. The exact source of the full signal pass is retained in [audit_execution_code.zip](evidence/audit_execution_code.zip); later metadata and breath-peak semantic corrections are deterministically applied by `summarize` without another full signal pass. The current source/config is fingerprinted by `validate`. Source archives remain untouched. [Evidence index](evidence/README.md) documents schema, validity semantics and limitations. All exploratory statistics use descriptive summaries, no p-value search or predictive fitting. No confirmatory test set was declared or evaluated; future hypotheses formed using this audit need a locked/untouched evaluation or external data.

## NEXT_STAGE_RECOMMENDATION

**Resolve the blocking OQ-06 preprocessing execution/scaling provenance, and verify Exp.2 answer-order canonicalization before behavioral pooling.** After that closure, retain the duplicate-item quarantine and explicit timing/identity boundaries and proceed to **Research Gap & Problem Formulation**. No final question is selected here.
''')
    write('evidence/README.md','''# Machine-readable evidence

Evidence is generated from checksum-verified BBBD1.1 ZIPs by `src/bbbd_audit/`, using `audit_config.json`. Raw source snapshots and author-code ZIP are attributed to the official dataset/code sources. No model or evaluation split exists.

| Artifact | Scientific role |
| --- | --- |
| download_manifest.json / zenodo_record_22968459.json | Official identity/sizes/MD5; local SHA-256 and download timestamps |
| archive_members.parquet | Complete canonical ZIP directory, file sizes/CRC/offsets |
| canonical_manifest.parquet / missing_files.parquet | Physical files plus explicit design/unexpected absent records, modality/outcome joins and validity masks |
| exposure_tensor.parquet / modality_intersections.csv | Grouping units, coverage, provisional QC and exact common-grid valid durations |
| quiz_items.parquet / quiz_video_outcomes.parquet / quiz_aggregate_comparison.parquet | Independent score reconstruction, duplicate quarantine, partial/exact denominators and rounding |
| participant_quiz_join_ledger.csv / participant_traits.parquet / phenotype_coverage.json | Cardinalities, unmatched IDs, observed traits and raw/item-derived coding |
| channel_qc.parquet / eeg_contamination_map.parquet / peak_qc.parquet | Channel statistics, PSD/band/line summaries, RR/RMSSD and peak anomalies |
| files/channels/peaks/masks/events/metadata_expN.parquet | Resumable experiment QC shards; masks keep original seconds intervals; metadata preserves contradictions |
| physiology_flat_runs.parquet | Dataset-wide finite exact-constant regions in raw ECG/EOG/respiration/head |
| timing_boundaries.parquet | Sample-count agreement; does not estimate native clock residuals |
| missingness_map.parquet / *_diagnostics.csv | Design versus loss versus QC, descriptive selection checks |
| exploratory_*.csv/parquet | EXPLORATORY modality/person/video summaries; no significance or performance optimization |
| leakage_risk_register.json / independence_graph.json / research_feasibility.csv / p0_gate_status.csv | Formal future-design constraints and bounded scientific judgments |
| disk_usage.jsonl / retention_manifest.json / validation.json | Allocated versus logical disk accounting, retention and verification |
| audit_execution_code.zip / audit_pipeline_source.zip / generating_source_fingerprints.json | Exact full-signal execution source, final deterministic pipeline source snapshot and per-file SHA-256 fingerprints |

Parquet uses Zstandard compression. Exact values are retained in tables; report decimals are rounded for readability. Binary validity masks use `numpy.packbits(..., bitorder='little')`; truncate unpacked masks to `qc_sample_count`. True means invalid/corrected, false means eligible under the audit definition. Exact intersection durations OR all selected modality masks over the shortest common released-grid length. This does not recover unreleased artifact masks or alignment residuals.

The full archive is immutable, while derived evidence is reproducible. Metadata descriptions and upstream code are evidence of declarations/possible operations, not proof that all options were executed. Scientific classifications are explicit in the reports. Date/timestamp values use2026-10-02 audit date and UTC machine timestamps; user-facing local timezone isEurope/Berlin.
''')
    write('evidence/author_query_draft.md','''# Prepared author query — NOT SENT

We have verified all five BBBD1.1 Zenodo22968459 archives against official MD5 and retained SHA-256s. Could you supply or confirm:

1. Exact per-experiment/per-representation EEG execution options (0.05/0.3/0.5 Hz discrepancy, reference, RPCA/EOG fitting scope, interpolation masks), ECG filter/peak/manual-edit options and resampling/synchronization kernels/software versions for these bytes?
2. Physical ECG/respiration scaling: raw JSON labelsmV, with numerical ranges in thousands; derivatives lack unit sidecars. Are values originally BioSemi microvolts or another representation?
3. Original device trigger/clock-fit mappings and residual uncertainty, and acquired-video trim hashes/order logs; released start/end events appear generated from array lengths.
4. Exp.3 sub-01 stim03 duplicated q11 (different answers) and missing q12; surplus quiz IDs1–3; no-penalty partial scoring versus published penalty prose; historical analysis label/cohort maps and Figure6 executed inputs.
5. Privacy-preserving statement of person overlap across experiments,4/5 allocation/chronology, digit-span zeros/weighted formula and GPA coding/institutional scales.
6. Original answer-order canonicalization in Exp.2: supplied correct-option codes are uniformly 1 and its mean score is near the uniform four-option chance benchmark. We have reconstructed the supplied scores but cannot independently verify the original response transformation.

This is a local evidence request draft. No message or email has been sent; sending requires a separate explicit user instruction.
''')
    if (EVIDENCE/'gate_closure_ecg_all_pairs.csv').exists() and (EVIDENCE/'gate_closure_historical_quiz_comparison.json').exists():
        from .gate_closure import apply_document_status
        apply_document_status()
    print('Research reports generated',flush=True)

if __name__=='__main__':run()
