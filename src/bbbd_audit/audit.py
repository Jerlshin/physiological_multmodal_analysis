"""Full-file lightweight QC, canonical file manifest and event-boundary audit."""
import gzip
import hashlib
import io
import json
import re
import time
from pathlib import Path
import numpy as np
import pandas as pd
from .io import EVIDENCE, DATA, open_archive, write_json, storage_snapshot, now
from .qc import CONFIG, Stats, bdf_header, bdf_chunks, intervals_to_mask, longest_true, timestamp_metrics

QC_CODE_SHA256=hashlib.sha256(Path(__file__).read_bytes()+Path(__file__).with_name('qc.py').read_bytes()).hexdigest()

KEY_RE=re.compile(r"(sub-\d+)_(ses-\d+)_task-stim(\d+)")

def key(path):
    m=KEY_RE.search(path)
    return (m[1],int(m[2][4:]),int(m[3])) if m else None

def modality(path):
    if path.endswith('.bdf'):return 'eeg'
    for word in ['gaze','pupil','head']:
        if f'{word}_' in path:return word
    for word in ['ecg','eog','respiration']:
        if 'recording-'+word+'_' in path:return word
    if 'desc-filteredECG' in path:return 'ecg'
    if 'desc-heartrate.' in path:return 'heart_rate'
    if 'desc-breathrate.' in path:return 'breath_rate'
    return None

def frame(z,path,header='infer'):
    with z.open(path) as f:
        if path.endswith('.gz'):
            with gzip.GzipFile(fileobj=f) as g:return pd.read_csv(g,sep='\t',header=header)
        return pd.read_csv(f,sep='\t',header=header)

def tsv_chunks(z,path):
    with z.open(path) as f:
        with gzip.GzipFile(fileobj=f) as g:
            # Continuous derivatives are also headerless in actual release.
            yield from (x.to_numpy(dtype=float) for x in pd.read_csv(g,sep='\t',header=None,chunksize=CONFIG['tsv_chunk_rows']))

def exposure_condition(exp,session):
    if exp<=3:return 'intentional_attend' if session==1 and exp in [1,3] else 'incidental_attend' if session==1 else 'arithmetic_repeat'
    if exp==4:return 'attend_untested_content' if session==1 else 'attend_tested_content'
    return 'incidental_first' if session==1 else 'incentive_preview_repeat'

def qc_reasons(mod,rows,correction):
    c=CONFIG['basic_qc'];reasons=[]
    n=sum(r['samples'] for r in rows)
    if not n:return ['empty']
    if sum(r['nan_count']+r['inf_count'] for r in rows)/n>c['max_nonfinite_fraction']:reasons.append('nonfinite_gt_1pct')
    if sum(r['zero_count'] for r in rows)/n>c['max_exact_zero_fraction']:reasons.append('exact_zero_gt_95pct')
    flats=sum(r['flat'] for r in rows)
    if flats>c['max_eeg_flat_channels'] if mod=='eeg' else flats==len(rows):reasons.append('gross_flatness')
    if mod in ['gaze','pupil'] and correction is not None and correction>c['max_eye_correction_fraction']:reasons.append('correction_gt_50pct')
    return reasons

def run(experiments=(4,5,2,3,1)):
    mapping=pd.read_csv(EVIDENCE/'stimulus_map.csv')
    outcomes=pd.read_parquet(EVIDENCE/'quiz_video_outcomes.parquet').query("question_type=='memory'")
    traits=pd.read_parquet(EVIDENCE/'participant_traits.parquet')
    input_hash=hashlib.sha256(b''.join((EVIDENCE/n).read_bytes() for n in ['stimulus_map.csv','quiz_video_outcomes.parquet','participant_traits.parquet'])).hexdigest()
    for exp in experiments:
        target=EVIDENCE/f'files_exp{exp}.parquet'
        marker=EVIDENCE/f'audit_exp{exp}.json'
        if target.exists() and marker.exists():
            previous=json.loads(marker.read_text())
            config_hash=hashlib.sha256(json.dumps(CONFIG,sort_keys=True).encode()).hexdigest()
            if previous.get('code_sha256')==QC_CODE_SHA256 and previous.get('input_sha256')==input_hash and previous.get('config_sha256')==config_hash:
                print('Completed audit retained',exp,flush=True);continue
        print('Auditing experiment',exp,now(),flush=True)
        files=[];channels=[];discrete=[];timings=[];metadata=[];masks=[];errors=[]
        start=time.monotonic();last=start
        with open_archive(exp) as z:
            names=set(z.namelist())
            # Read all small raw sidecars once. Retain fingerprints and unique descriptions.
            sidecars={n:json.loads(z.read(n)) for n in names if n.endswith('.json')}
            event_paths={key(n):n for n in names if n.endswith('_events.tsv')}
            events={k:frame(z,n) for k,n in event_paths.items()}
            end_times={}
            for k,t in events.items():
                end=t[t.event=='end'] if 'event' in t else pd.DataFrame()
                # Export create_events writes end onset = n_samples / fs.
                # Its one-sample duration describes marker width, not one more signal sample.
                if len(end)==1:end_times[k]=float(end.onset.iloc[0])
                timings.append(dict(experiment=exp,participant_id=k[0],session=k[1],local_stimulus_id=k[2],path=event_paths[k],event_count=len(t),start_events=int(sum(t.event=='start')) if 'event' in t else 0,end_events=len(end),end_seconds=end_times.get(k),native_clock_residual_available=False,events_json=json.dumps(t.to_dict('records'))))
            meta_path=EVIDENCE/'release_metadata'/f'experiment{exp}'
            # Verify the range-read phenotype snapshots against the checksum-verified archive.
            for n in names:
                if '/' not in n or n.startswith('phenotype/'):
                    p=meta_path/n
                    if p.is_file() and p.read_bytes()!=z.read(n):raise ValueError('Metadata snapshot mismatch: '+n)
            for n,d in sidecars.items():
                metadata.append(dict(experiment=exp,path=n,sha256=hashlib.sha256(z.read(n)).hexdigest(),sampling_frequency=d.get('SamplingFrequency'),start_time=d.get('StartTime'),recording_duration=d.get('RecordingDuration'),task_name=d.get('TaskName'),task_description=d.get('TaskDescription'),software_filters=json.dumps(d.get('SoftwareFilters')),generated_by=json.dumps(d.get('GeneratedBy')),columns=json.dumps(d.get('Columns')),eeg_reference=d.get('EEGReference')))
            # Discrete peaks, correction masks and events are first-class data.
            for n in sorted(names):
                if not n.endswith('.tsv.gz') or not any(s in n for s in ['interpolation_timestamps','rpeak_timestamps','breath_peak_timestamps']):continue
                k=key(n);t=frame(z,n)
                base=dict(experiment=exp,participant_id=k[0],qualified_participant_id=f'exp-{exp}:{k[0]}',session=k[1],local_stimulus_id=k[2],path=n,bytes=z.getinfo(n).file_size)
                if 'interpolation' in n:
                    mod='gaze' if 'gaze_' in n else 'pupil'
                    vals=t.iloc[:,:2].to_numpy(float)
                    masks.append(base|dict(modality=mod,intervals=vals))
                else:
                    p=t.iloc[:,0].to_numpy(float)
                    event_type='rpeak' if 'rpeak' in n else 'breath_peak'
                    discrete.append(base|dict(event_type=event_type,header=t.columns[0],timestamp_unit='seconds; native-derived, stimulus-relative',**timestamp_metrics(p,event_type)))
            mask_lookup={(m['participant_id'],m['session'],m['local_stimulus_id'],m['modality']):m for m in masks}
            peak_lookup={key(r['path']):r for r in discrete if r['event_type']=='rpeak'}
            continuous=[n for n in sorted(names) if key(n) and modality(n) and n.endswith(('.bdf','.tsv.gz')) and 'interpolation' not in n]
            for i,n in enumerate(continuous):
                k=key(n);mod=modality(n);status='author_processed' if n.startswith('derivatives/') else 'aligned_release_raw'
                m=mapping[(mapping.experiment==exp)&(mapping.local_stimulus_id==k[2])]
                if len(m)!=1:raise ValueError('Unknown stimulus '+n)
                v=outcomes[(outcomes.experiment==exp)&(outcomes.participant_id==k[0])&(outcomes.local_stimulus_id==k[2])]
                direct=(k[1]==1 if exp<=3 else k[1]==2 and (exp==5 or k[2]<=3))
                valid_quiz=bool(direct and len(v)==1 and v.valid_outcome.iloc[0])
                scpath=n[:-7]+'.json' if n.endswith('.tsv.gz') else n[:-4]+'.json'
                sc=sidecars.get(scpath,{})
                if not sc:
                    # Find matching raw metadata by semantics, but do not claim derivative units/provenance verified.
                    sc=next((d for p,d in sidecars.items() if not p.startswith('derivatives/') and key(p)==k and modality(p.replace('.json','.tsv.gz'))==mod),{})
                fs=float(sc.get('SamplingFrequency',CONFIG['sampling_rate']))
                cr=None;mask_info=mask_lookup.get((*k,mod));mask_array=None;invalid_flags=[];wave=[]
                row=dict(experiment=exp,participant_id=k[0],qualified_participant_id=f'exp-{exp}:{k[0]}',session=k[1],block=k[1],local_stimulus_id=k[2],canonical_video_id=m.canonical_video_id.iloc[0],exposure_number=1 if exp==4 else k[1],condition=exposure_condition(exp,k[1]),modality=mod,path=f"experiment{exp}.zip::{n}",archive=f'experiment{exp}.zip',member_path=n,file_size=z.getinfo(n).file_size,status=status,nominal_sampling_rate=fs,sampling_rate_evidence='BDF header' if n.endswith('.bdf') else 'raw sidecar' if scpath in sidecars else 'raw counterpart / documented export grid; derivative sidecar absent',missing_file_status='present',interpolation_mask_available=mask_info is not None,event_available=k in events,quiz_available=len(v)==1,valid_quiz_outcome=valid_quiz,quiz_linkage='direct_final_test' if direct else 'earlier_or_later_exposure_same_video_only' if len(v)==1 else 'no_video_quiz',participant_metadata_available=k[0] in set(traits[traits.experiment==exp].participant_id),questionnaire_available=exp>1,preprocessing_provenance='raw aligned export; exact execution options unavailable' if status=='aligned_release_raw' else 'author derivative; no per-file GeneratedBy/options; upstream code pinned separately',start_time=sc.get('StartTime',0),sidecar_task_name=sc.get('TaskName'),sidecar_recording_duration=sc.get('RecordingDuration'))
                try:
                    if n.endswith('.bdf'):
                        with z.open(n) as f:
                            h=bdf_header(f);names_ch=h['labels'];units=h['units'];fs=float(h['samples_per_record'][0]/h['record_seconds'])
                            stats=Stats(h['channels'],fs);seen=0
                            observed=int(h['records']*h['samples_per_record'][0]);bound=min(observed,int(round(end_times[k]*fs))) if k in end_times else observed
                            digital_padding_nonzero=0;near_zero_padding=0;tail_max_abs=0.
                            for x,d in bdf_chunks(f,h):
                                take=max(0,min(len(x),bound-seen))
                                if take<len(x):
                                    digital_padding_nonzero+=int((d[take:]!=0).any(axis=1).sum())
                                    gain=(h['physical_max']-h['physical_min'])/(h['digital_max']-h['digital_min'])
                                    near_zero_padding+=int((np.abs(x[take:])<=gain).all(axis=1).sum())
                                    tail_max_abs=max(tail_max_abs,float(np.max(np.abs(x[take:]))))
                                if take:stats.update(x[:take],d[:take],h['digital_min'],h['digital_max'])
                                seen+=len(x)
                            row.update(nominal_sampling_rate=fs,observed_sample_count=observed,padding_samples=observed-bound,padding_tail_nonzero_digital_rows=digital_padding_nonzero,padding_tail_within_one_lsb_rows=near_zero_padding,padding_tail_max_abs=tail_max_abs,bdf_digital_range=json.dumps([h['digital_min'].tolist(),h['digital_max'].tolist()]),bdf_prefilter=h['prefilter'][0])
                    else:
                        stats=None;observed=0
                        for x in tsv_chunks(z,n):
                            if stats is None:stats=Stats(x.shape[1],fs)
                            stats.update(x);observed+=len(x)
                            bad=~np.isfinite(x).all(axis=1)
                            if mod=='pupil':bad|=(x[:,0]<=0)
                            if mod=='gaze' and x.shape[1]>=2:bad|=(x[:,0]<0)|(x[:,0]>1920)|(x[:,1]<0)|(x[:,1]>1080)
                            if mod=='head' and x.shape[1]>=3:bad|=(x[:,2]<=0)
                            invalid_flags.append(bad)
                            if mod=='ecg' and status=='author_processed':wave.append(x[:,0])
                        if stats is None:raise ValueError('Empty continuous stream')
                        names_ch=sc.get('Columns',[f'ch{c+1}' for c in range(stats.c)])
                        if len(names_ch)!=stats.c:names_ch=[f'ch{c+1}' for c in range(stats.c)]
                        units=[sc.get(c,{}).get('Units','unknown') for c in names_ch]
                        if status=='author_processed':units=['unverified derivative unit; raw counterpart '+u for u in units]
                        row.update(observed_sample_count=observed,padding_samples=0)
                    channel_rows=stats.result(names_ch)
                    bad=np.concatenate(invalid_flags) if invalid_flags else np.zeros(stats.n,bool)
                    if mask_info is not None:
                        mask_array,oob=intervals_to_mask(mask_info['intervals'],observed,fs)
                        cr=float(mask_array.mean())
                        row.update(correction_fraction=cr,correction_samples=int(mask_array.sum()),longest_correction_gap_seconds=longest_true(mask_array)/fs,correction_interval_count=len(mask_info['intervals']),correction_intervals_out_of_bounds=oob,mask_semantics='released seconds intervals; conservative floor/ceil conversion on 128 Hz grid')
                        if len(bad)==len(mask_array):bad|=mask_array
                    row.update(channel_count=stats.c,channel_names=json.dumps(names_ch),units=json.dumps(units),observed_duration=observed/fs,qc_sample_count=stats.n,nan_count=int(stats.nan.sum()),nan_fraction=float(stats.nan.sum()/max(1,stats.n*stats.c)),inf_count=int(stats.inf.sum()),exact_zero_count=int(stats.zero.sum()),exact_zero_fraction=float(stats.zero.sum()/max(1,stats.n*stats.c)),flat_channels=sum(r['flat'] for r in channel_rows),amplitude_min=min(r['minimum'] for r in channel_rows),amplitude_max=max(r['maximum'] for r in channel_rows),invalid_or_corrected_seconds=float(bad.sum()/fs),valid_duration=float((stats.n-bad.sum())/fs),valid_duration_definition='event-trimmed finite/range-valid, minus released eye correction-mask union; EEG corrected samples not recoverable',eeg_16hz_flagged_channels=sum(r.get('excess_16hz_db',0)>10 for r in channel_rows),eeg_16hz_median_db=float(np.median([r.get('excess_16hz_db',0) for r in channel_rows])) if mod=='eeg' else 0)
                    row['invalid_sample_bits']=np.packbits(bad,bitorder='little').tobytes()
                    if len(bad)!=stats.n:raise ValueError('Validity-mask length mismatch')
                    reasons=qc_reasons(mod,channel_rows,cr)
                    if mod in ['gaze','pupil'] and bad.mean()>.5 and 'correction_gt_50pct' not in reasons:reasons.append('range_or_nonfinite_or_correction_gt_50pct')
                    row['qc_status']='flagged_basic_screen' if reasons else 'passes_basic_screen'
                    row['qc_reasons']=json.dumps(reasons)
                    for r in channel_rows:channels.append({k2:row[k2] for k2 in ['experiment','participant_id','qualified_participant_id','session','local_stimulus_id','canonical_video_id','condition','status','modality','path']}|r)
                    if mod=='ecg' and wave and k in peak_lookup:
                        signal=np.concatenate(wave);p=frame(z,peak_lookup[k]['path']).iloc[:,0].to_numpy(float)
                        offsets=[];inbound=0;half=int(round(.1*fs))
                        for t in p:
                            ix=int(round(t*fs))
                            if half<=ix<len(signal)-half:
                                seg=signal[ix-half:ix+half+1];inbound+=1
                                if np.isfinite(seg).all():offsets.append((np.argmax(np.abs(seg-np.median(seg)))-half)/fs)
                        row.update(rpeak_waveform_checked=inbound,rpeak_local_abs_extremum_median_offset_seconds=float(np.median(offsets)) if offsets else None,rpeak_local_abs_extremum_median_abs_offset_seconds=float(np.median(np.abs(offsets))) if offsets else None,rpeak_out_of_waveform_count=int(((p<0)|(p>=len(signal)/fs)).sum()))
                except Exception as error:
                    row.update(qc_status='parse_error',qc_reasons=json.dumps([str(error)]));errors.append(dict(path=n,error=str(error)))
                files.append(row)
                if time.monotonic()-last>30:
                    print('Exp',exp,i+1,'/',len(continuous),'continuous files',flush=True);last=time.monotonic()
            for m in masks:m['intervals']=json.dumps(m['intervals'].tolist())
        pd.DataFrame(files).to_parquet(target,index=False,compression='zstd')
        pd.DataFrame(channels).to_parquet(EVIDENCE/f'channels_exp{exp}.parquet',index=False,compression='zstd')
        pd.DataFrame(discrete).to_parquet(EVIDENCE/f'peaks_exp{exp}.parquet',index=False,compression='zstd')
        pd.DataFrame(masks).to_parquet(EVIDENCE/f'masks_exp{exp}.parquet',index=False,compression='zstd')
        pd.DataFrame(timings).to_parquet(EVIDENCE/f'events_exp{exp}.parquet',index=False,compression='zstd')
        pd.DataFrame(metadata).to_parquet(EVIDENCE/f'metadata_exp{exp}.parquet',index=False,compression='zstd')
        write_json(EVIDENCE/f'audit_exp{exp}.json',dict(experiment=exp,completed_utc=now(),elapsed_seconds=time.monotonic()-start,continuous_files=len(files),channel_records=len(channels),errors=errors,config_sha256=hashlib.sha256(json.dumps(CONFIG,sort_keys=True).encode()).hexdigest(),code_sha256=QC_CODE_SHA256,input_sha256=input_hash,status='complete_lightweight_qc'))
        storage_snapshot(f'qc_exp{exp}_complete')
        print('QC completed',exp,'errors',len(errors),flush=True)
