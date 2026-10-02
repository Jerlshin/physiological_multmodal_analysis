"""Canonical exposure tensor, intersections and descriptive evidence tables."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .io import EVIDENCE, ROOT, write_json, open_archive
from .audit import exposure_condition, frame
from .qc import timestamp_metrics

GROUP=['experiment','participant_id','qualified_participant_id','session','local_stimulus_id','canonical_video_id','exposure_number','condition']
MODALITIES=['eeg','ecg','gaze','pupil','eog','respiration','head']

def read_parts(prefix):
    parts=[pd.read_parquet(p) for p in sorted(EVIDENCE.glob(prefix+'_exp*.parquet'))]
    return pd.concat(parts,ignore_index=True) if parts else pd.DataFrame()

def summarize_stats(frame,groupby,cols):
    rows=[]
    for key,g in frame.groupby(groupby,dropna=False):
        key=key if isinstance(key,tuple) else (key,)
        r=dict(zip(groupby,key));r['records']=len(g)
        for col in cols:
            if col not in g:continue
            s=pd.to_numeric(g[col],errors='coerce').replace([np.inf,-np.inf],np.nan).dropna()
            if len(s):r.update({col+'_mean':float(s.mean()),col+'_median':float(s.median()),col+'_q05':float(s.quantile(.05)),col+'_q95':float(s.quantile(.95)),col+'_min':float(s.min()),col+'_max':float(s.max())})
        rows.append(r)
    return pd.DataFrame(rows)

def run():
    f=read_parts('files');c=read_parts('channels');p=read_parts('peaks');meta=read_parts('metadata')
    if f.empty:raise ValueError('No verified file audits')
    if f.path.duplicated().any():raise ValueError('Duplicate canonical file keys')
    # Earlier checkpoint schema represented all-nonfinite extrema as infinities.
    # Normalize derived summaries only; preserve counts and original source bytes.
    nofinite=c.finite_samples==0
    c.loc[nofinite,['mean','std','minimum','maximum']]=np.nan
    c.loc[nofinite,'flat']=False
    f['amplitude_min']=f.amplitude_min.replace([np.inf,-np.inf],np.nan)
    f['amplitude_max']=f.amplitude_max.replace([np.inf,-np.inf],np.nan)
    outcomes=pd.read_parquet(EVIDENCE/'quiz_video_outcomes.parquet').query("question_type=='memory'")
    # Resolve observed questionnaire coverage from keyed rows, not experiment design.
    traits=pd.read_parquet(EVIDENCE/'participant_traits.parquet')
    asrs=[f'asrs_q{i}' for i in range(1,19)]
    traits['asrs_questionnaire_available']=traits[asrs].notna().all(axis=1)
    traits['digit_span_score_available']=traits.digit_span.notna()
    f=f.drop(columns=['questionnaire_available']).merge(traits[['experiment','participant_id','asrs_questionnaire_available','digit_span_score_available']],on=['experiment','participant_id'],how='left',validate='many_to_one')
    feedback=[]
    for exp in range(2,6):
        t=pd.read_csv(EVIDENCE/f'release_metadata/experiment{exp}/phenotype/stimuli_feedback_meta.tsv',sep='\t')
        col='stimulus' if 'stimulus' in t else 'stim_id'
        t['local_stimulus_id']=t[col].str.extract(r'(\d+)')[0].astype(int)
        t['experiment']=exp;t['video_feedback_available']=t.drop(columns=['participant_id',col,'local_stimulus_id','experiment']).notna().any(axis=1)
        feedback.append(t[['experiment','participant_id','local_stimulus_id','video_feedback_available']])
    f=f.merge(pd.concat(feedback),on=['experiment','participant_id','local_stimulus_id'],how='left',validate='many_to_one')
    f['video_feedback_available']=f.video_feedback_available.fillna(False).astype(bool)
    f['questionnaire_available']=f.asrs_questionnaire_available|f.digit_span_score_available|f.video_feedback_available
    f['data_role']=np.where(f.modality.isin(['heart_rate','breath_rate']),'derived_feature',np.where(f.status=='author_processed','author_processed_signal','aligned_release_raw_signal'))
    # These small timestamp members can be re-read without signal deserialization.
    # Breath intervals have their own units/ranges; cardiac plausibility never applies.
    corrected=[]
    ecg_waveforms=f[(f.modality=='ecg')&(f.status=='author_processed')].set_index(['experiment','participant_id','session','local_stimulus_id'])
    for exp,g in p.groupby('experiment'):
        with open_archive(exp) as z:
            for row in g.to_dict('records'):
                values=frame(z,row['path']).iloc[:,0].to_numpy(float)
                base={k:row[k] for k in ['experiment','participant_id','qualified_participant_id','session','local_stimulus_id','path','bytes','event_type','header','timestamp_unit']}
                if row['event_type']=='rpeak':
                    key=tuple(row[k] for k in ['experiment','participant_id','session','local_stimulus_id'])
                    wave=ecg_waveforms.loc[key]
                    outside=values[(values<0)|(values>=wave.observed_duration)]
                    base.update(ecg_duration_seconds=float(wave.observed_duration),rpeak_out_of_waveform_count=len(outside),rpeak_out_of_waveform_timestamps_seconds=json.dumps(outside.tolist()),rpeak_max_after_end_seconds=float(np.max(outside-wave.observed_duration)) if len(outside) else 0.)
                    for name in ['rpeak_waveform_checked','rpeak_local_abs_extremum_median_offset_seconds','rpeak_local_abs_extremum_median_abs_offset_seconds']:base[name]=wave[name]
                corrected.append(base|timestamp_metrics(values,row['event_type'])|{'nonfinite_peak_count':int((~np.isfinite(values)).sum())})
    p=pd.DataFrame(corrected)
    f=f.merge(outcomes[['experiment','participant_id','local_stimulus_id','normalized_partial_score','normalized_exact_score','unique_items','valid_outcome']],on=['experiment','participant_id','local_stimulus_id'],how='left',validate='many_to_one')
    f['outcome_id']=np.where(f.quiz_available,f.apply(lambda r:f"exp-{r.experiment}:{r.participant_id}:stim-{r.local_stimulus_id}:memory",axis=1),None)
    f['outcome_value_role']=np.where(f.valid_quiz_outcome,'direct final-test outcome',np.where(f.quiz_available,'same-video outcome with different exposure chronology or quarantined key','no link'))
    c.to_parquet(EVIDENCE/'channel_qc.parquet',index=False,compression='zstd')
    p.to_parquet(EVIDENCE/'peak_qc.parquet',index=False,compression='zstd')
    observed=[];validity={}
    for key,g in f.groupby(GROUP,dropna=False):
        row=dict(zip(GROUP,key));row['valid_quiz_outcome']=bool(g.valid_quiz_outcome.any());row['any_quiz']=bool(g.quiz_available.any())
        for mod in MODALITIES:
            mg=g[g.modality==mod];raw=mg[mg.status=='aligned_release_raw'];proc=mg[mg.status=='author_processed']
            selected=proc if mod in ['eeg','ecg','gaze','pupil','head'] else raw
            # Processed and raw completeness remain separate; no raw fallback disguised as cleaned data.
            row[mod+'_raw_present']=not raw.empty;row[mod+'_processed_present']=not proc.empty
            row[mod+'_present']=not selected.empty
            row[mod+'_basic_qc']=bool(len(selected)==1 and selected.qc_status.iloc[0]=='passes_basic_screen')
            row[mod+'_valid_duration']=float(selected.valid_duration.iloc[0]) if len(selected)==1 and pd.notna(selected.valid_duration.iloc[0]) else 0.
            row[mod+'_qc_reasons']=selected.qc_reasons.iloc[0] if len(selected)==1 else 'missing' if len(selected)==0 else 'ambiguous_multiple_variants'
            if len(selected)==1:
                r=selected.iloc[0]
                bits=np.unpackbits(np.frombuffer(r.invalid_sample_bits,dtype=np.uint8),bitorder='little')[:int(r.qc_sample_count)].astype(bool)
                validity[(*key[:5],mod)]=bits
        row['eye_present']=row['gaze_present'] and row['pupil_present']
        row['eye_basic_qc']=row['gaze_basic_qc'] and row['pupil_basic_qc']
        row['eye_valid_duration']=min(row['gaze_valid_duration'],row['pupil_valid_duration'])
        observed.append(row)
    ex=pd.DataFrame(observed)
    # Expected design grid over archive signal participants, with absent exposures explicit.
    sm=pd.read_csv(EVIDENCE/'stimulus_map.csv');missing=[]
    for exp,g in ex.groupby('experiment'):
        for pid in sorted(g.participant_id.unique()):
            for ses in [1,2]:
                stims=range(1,6) if exp<=2 else range(1,7) if exp==3 else range(4,7) if exp==4 and ses==1 else range(1,4)
                for stim in stims:
                    if not ((g.participant_id==pid)&(g.session==ses)&(g.local_stimulus_id==stim)).any():
                        video=sm[(sm.experiment==exp)&(sm.local_stimulus_id==stim)].canonical_video_id.iloc[0]
                        v=outcomes[(outcomes.experiment==exp)&(outcomes.participant_id==pid)&(outcomes.local_stimulus_id==stim)]
                        direct=ses==1 if exp<=3 else ses==2 and (exp==5 or stim<=3)
                        row=dict(experiment=exp,participant_id=pid,qualified_participant_id=f'exp-{exp}:{pid}',session=ses,local_stimulus_id=stim,canonical_video_id=video,exposure_number=1 if exp==4 else ses,condition=exposure_condition(exp,ses),valid_quiz_outcome=bool(direct and len(v)==1 and v.valid_outcome.iloc[0]),any_quiz=len(v)==1)
                        for mod in MODALITIES+['eye']:
                            for suffix in ['present','basic_qc','raw_present','processed_present']:row[mod+'_'+suffix]=False
                            row[mod+'_valid_duration']=0.;row[mod+'_qc_reasons']='entire_exposure_absent'
                        missing.append(row)
    if missing:ex=pd.concat([ex,pd.DataFrame(missing)],ignore_index=True)
    ex.to_parquet(EVIDENCE/'exposure_tensor.parquet',index=False,compression='zstd')
    missing_modalities=[]
    for _,r in ex.iterrows():
        for mod in MODALITIES:
            statuses=['aligned_release_raw','author_processed'] if mod in ['eeg','ecg','gaze','pupil','head'] else ['aligned_release_raw']
            for status in statuses:
                is_present=r[mod+('_raw_present' if status=='aligned_release_raw' else '_processed_present')]
                if is_present:continue
                bydesign=(r.experiment==1 and mod in ['eeg','ecg','eog']) or (r.experiment<4 and mod=='respiration')
                kind='absent_by_design' if bydesign else 'not_released_exp1_head' if r.experiment==1 and mod=='head' else 'expected_file_absent'
                v=outcomes[(outcomes.experiment==r.experiment)&(outcomes.participant_id==r.participant_id)&(outcomes.local_stimulus_id==r.local_stimulus_id)]
                trait=traits[(traits.experiment==r.experiment)&(traits.participant_id==r.participant_id)].iloc[0]
                fb=pd.concat(feedback);fb=fb[(fb.experiment==r.experiment)&(fb.participant_id==r.participant_id)&(fb.local_stimulus_id==r.local_stimulus_id)]
                feedback_available=bool(len(fb)==1 and fb.video_feedback_available.iloc[0])
                extra=dict(quiz_available=len(v)==1,participant_metadata_available=True,asrs_questionnaire_available=bool(trait.asrs_questionnaire_available),digit_span_score_available=bool(trait.digit_span_score_available),video_feedback_available=feedback_available,questionnaire_available=bool(trait.asrs_questionnaire_available or trait.digit_span_score_available or feedback_available))
                if len(v)==1:
                    extra.update(outcome_id=f"exp-{r.experiment}:{r.participant_id}:stim-{r.local_stimulus_id}:memory",normalized_partial_score=float(v.normalized_partial_score.iloc[0]),normalized_exact_score=float(v.normalized_exact_score.iloc[0]),unique_items=int(v.unique_items.iloc[0]),valid_outcome=bool(v.valid_outcome.iloc[0]),outcome_value_role='direct final-test outcome; signal file absent' if r.valid_quiz_outcome else 'same-video outcome with different exposure chronology or quarantined key')
                missing_modalities.append({x:r[x] for x in GROUP}|dict(modality=mod,status=status,path=f"missing::exp-{r.experiment}:{r.participant_id}:ses-{r.session}:stim-{r.local_stimulus_id}:{mod}:{status}",missing_file_status=kind,file_size=0,observed_sample_count=0,observed_duration=0,valid_duration=0,qc_status='absent',qc_reasons=json.dumps([kind]),valid_quiz_outcome=r.valid_quiz_outcome)|extra)
    pd.DataFrame(missing_modalities).to_parquet(EVIDENCE/'missing_files.parquet',index=False,compression='zstd')
    pd.concat([f,pd.DataFrame(missing_modalities)],ignore_index=True).to_parquet(EVIDENCE/'canonical_manifest.parquet',index=False,compression='zstd')
    combinations=[['eeg'],['ecg'],['eye'],['eeg','ecg'],['eeg','eye'],['ecg','eye'],['eeg','ecg','eye'],['eeg','ecg','eye','respiration']]
    intersections=[]
    for exp in [0]+sorted(ex.experiment.unique().tolist()):
        g=ex if exp==0 else ex[ex.experiment==exp]
        for mods in combinations:
            for stage in ['present','basic_qc']:
                for quiz in [False,True]:
                    mask=np.logical_and.reduce([g[m+'_'+stage].fillna(False).to_numpy(bool) for m in mods])
                    if quiz:mask&=g.valid_quiz_outcome.to_numpy(bool)
                    s=g[mask]
                    valid=0.
                    for _,r in s.iterrows():
                        k=tuple(r[x] for x in GROUP[:5]);use=[m2 for m in mods for m2 in (['gaze','pupil'] if m=='eye' else [m])]
                        masks=[validity[(*k,m)] for m in use]
                        n=min(map(len,masks));bad=np.logical_or.reduce([b[:n] for b in masks])
                        valid+=float((n-bad.sum())/128)
                    intersections.append(dict(experiment='ALL' if exp==0 else str(exp),modalities='+'.join(mods),stage=stage,requires_valid_quiz=quiz,people=s.qualified_participant_id.nunique(),person_video_exposures=len(s),unique_person_video_pairs=len(s[['qualified_participant_id','canonical_video_id']].drop_duplicates()),videos=s.canonical_video_id.nunique(),experiments=s.experiment.nunique(),valid_duration_seconds=float(valid),duration_semantics='exact union of audited invalid/correction masks within common released-grid span; residual synchronization and unreleased EEG corrections unknown'))
    ints=pd.DataFrame(intersections);ints.to_csv(EVIDENCE/'modality_intersections.csv',index=False)
    # Selection and signal quality evidence.
    summarize_stats(f,['experiment','status','modality'],['observed_duration','valid_duration','nan_fraction','exact_zero_fraction','flat_channels','correction_fraction','longest_correction_gap_seconds','amplitude_min','amplitude_max','eeg_16hz_median_db','rpeak_local_abs_extremum_median_abs_offset_seconds']).to_csv(EVIDENCE/'modality_qc_summary.csv',index=False)
    summarize_stats(f[f.modality.isin(['gaze','pupil'])],['experiment','status','modality','condition','canonical_video_id'],['correction_fraction','longest_correction_gap_seconds','valid_duration']).to_csv(EVIDENCE/'eye_quality_by_condition_video.csv',index=False)
    summarize_stats(c[c.modality=='eeg'],['experiment','status'],['std','excess_16hz_db','fraction_16hz','excess_60hz_db','power_alpha','power_beta']).to_csv(EVIDENCE/'eeg_quality_summary.csv',index=False)
    contamination=c[c.modality=='eeg'].copy()
    med=contamination.groupby('path')['std'].transform('median')
    contamination['variance_ratio_to_record_median']=contamination['std']**2/(med**2+1e-30)
    contamination['extreme_variance_flag']=contamination.variance_ratio_to_record_median>100
    contamination['line_noise_60hz_flag']=contamination.excess_60hz_db>10
    contamination['dominant_16hz_fraction_flag']=contamination.fraction_16hz>.1
    for threshold in [3,6,10,20]:contamination['flag_'+str(threshold)+'db']=contamination.excess_16hz_db>threshold
    contamination.to_parquet(EVIDENCE/'eeg_contamination_map.parquet',index=False,compression='zstd')
    summarize_stats(p[p.event_type=='rpeak'] if not p.empty else p,['experiment'],['peak_count','rr_median_seconds','median_hr_bpm','rms_rr_seconds','true_rmssd_seconds','rr_outside_40_160_fraction','rr_outside_30_200_fraction','duplicate_peaks','nonmonotonic_peaks']).to_csv(EVIDENCE/'ecg_peak_summary.csv',index=False)
    # Boundary agreement is not synchronization residual accuracy.
    timing=[]
    for key,g in f.groupby(GROUP):
        raw=g[g.status=='aligned_release_raw'];non_eeg=raw[raw.modality!='eeg']
        row=dict(zip(GROUP,key));row.update(modalities=raw.modality.nunique(),raw_duration_spread_seconds=float(non_eeg.observed_duration.max()-non_eeg.observed_duration.min()) if len(non_eeg) else None,eeg_vs_other_duration_seconds=float(raw[raw.modality=='eeg'].qc_sample_count.iloc[0]/128-non_eeg.observed_duration.median()) if len(raw[raw.modality=='eeg']) and len(non_eeg) else None,native_trigger_residual_available=False)
        timing.append(row)
    pd.DataFrame(timing).to_parquet(EVIDENCE/'timing_boundaries.parquet',index=False,compression='zstd')
    # Outcome-only descriptive summaries: no hypotheses, p-values or predictive selection.
    q=pd.read_parquet(EVIDENCE/'quiz_video_outcomes.parquet');i=pd.read_parquet(EVIDENCE/'quiz_items.parquet')
    q=q[(q.question_type=='memory')&q.valid_outcome]
    summarize_stats(q,['experiment','canonical_video_id'],['normalized_partial_score','normalized_exact_score','unique_items']).to_csv(EVIDENCE/'outcome_by_video.csv',index=False)
    iq=i[(i.question_type=='memory')&i.signal_participant_available&i.participant_metadata_available&~i.duplicate_item_key]
    iq.groupby(['experiment','canonical_video_id','question_no']).agg(people=('participant_id','nunique'),partial_difficulty=('recomputed_score','mean'),exact_difficulty=('recomputed_exact_correct','mean')).reset_index().to_csv(EVIDENCE/'item_difficulty.csv',index=False)
    participant_variation=q.groupby(['experiment','qualified_participant_id']).agg(video_observations=('canonical_video_id','count'),mean_partial=('normalized_partial_score','mean'),within_person_sd=('normalized_partial_score','std')).reset_index()
    participant_variation.to_csv(EVIDENCE/'outcome_person_variation.csv',index=False)
    selection=ex.merge(q[['experiment','participant_id','local_stimulus_id','normalized_partial_score']],on=['experiment','participant_id','local_stimulus_id'],how='left',validate='many_to_one')
    for mod in MODALITIES+['eye']:
        selection[mod+'_missingness_kind']=np.where((selection.experiment==1)&(mod in ['eeg','ecg','eog','head']), 'absent_by_design_or_unestablished_head',np.where((selection.experiment<4)&(mod=='respiration'),'absent_by_design',np.where(~selection[mod+'_present'],'expected_file_absent',np.where(~selection[mod+'_basic_qc'],'flagged_basic_qc','available_passes_basic_qc'))))
    selection.to_parquet(EVIDENCE/'missingness_map.parquet',index=False,compression='zstd')
    missing_rows=[]
    for mod in MODALITIES+['eye']:
        for keys,g in selection.groupby(['experiment','condition',mod+'_missingness_kind']):
            missing_rows.append(dict(experiment=keys[0],condition=keys[1],modality=mod,status=keys[2],exposures=len(g),people=g.qualified_participant_id.nunique(),mean_quiz_partial=float(g.normalized_partial_score.mean()) if g.normalized_partial_score.notna().any() else None,score_note='same score may be referenced across repeated exposures; descriptive selection diagnostic only'))
    pd.DataFrame(missing_rows).to_csv(EVIDENCE/'missingness_by_condition.csv',index=False)
    write_json(EVIDENCE/'summary_status.json',dict(audited_experiments=sorted(f.experiment.unique().tolist()),physical_continuous_files=len(f),channel_records=len(c),observed_exposures=len(observed),design_expected_exposures=len(ex),whole_exposure_missing=len(missing),people=ex.qualified_participant_id.nunique(),videos=ex.canonical_video_id.nunique(),parse_errors=int(sum(f.qc_status=='parse_error')),classification='EMPIRICALLY VERIFIED IN THIS AUDIT; quality thresholds and interpretation are OUR INFERENCE'))
    print(ints.query("experiment=='ALL'").to_string(index=False),flush=True)
