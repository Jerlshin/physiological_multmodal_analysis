"""Read-only targeted provenance tests; no source repair or predictive fitting.

Run with PYTHONPATH=src .venv/bin/python -m bbbd_audit.gate_closure.
All signal probes use release keys and deterministic selection, never outcomes.
"""
import gzip
import hashlib
import io
import json
import zipfile
from importlib.metadata import version

import numpy as np
import pandas as pd
from scipy import signal
from scipy.interpolate import PchipInterpolator, interp1d

from .io import EVIDENCE, open_archive, write_json, now
from .qc import bdf_header, bdf_chunks, intervals_to_mask


def array(z, path):
    b = z.read(path)
    if path.endswith('.bdf'):
        f = io.BytesIO(b)
        h = bdf_header(f)
        return np.concatenate([x for x, _ in bdf_chunks(f, h)]), h
    return np.loadtxt(io.BytesIO(gzip.decompress(b)), ndmin=2), None


def spectral_candidates(x, y, stream):
    """Complex transfer response comparison, with signal-weighted residuals.

    Includes identity and competing frequencies, orders, design rates, phases.
    A winning candidate is consistency evidence, not historical execution proof.
    Native filtering may precede segmentation/resampling/nonlinear corrections.
    """
    n = min(len(x), len(y))
    x, y = x[:n], y[:n]
    if x.ndim == 1:
        x, y = x[:, None], y[:, None]
    ok = np.isfinite(x).all(axis=1) & np.isfinite(y).all(axis=1)
    if not ok.all() or n < 8192:
        return []
    f, px = signal.welch(x, 128, nperseg=8192, axis=0)
    _, py = signal.welch(y, 128, nperseg=8192, axis=0)
    _, cross = signal.csd(x, y, 128, nperseg=8192, axis=0)
    coherence = np.abs(cross)**2 / np.maximum(px*py, 1e-30)
    band = (f >= .0625) & (f <= (45 if stream == 'ecg' else 2))
    eligible = band[:, None] & (coherence >= .8) & (px > np.max(px, axis=0)*1e-7)
    if eligible.sum() == 0:
        return []
    observed = cross / np.maximum(px, 1e-30)
    w = np.where(eligible, px, 0)
    denom = np.sum(w*np.abs(observed)**2)
    configs = [('identity', np.ones(len(f), complex))]
    if stream == 'ecg':
        designs = [(hp, order, fs) for hp in [.05, .3, .5] for order in [1, 5] for fs in [128, 2048]]
    else:
        designs = [(hp, 5, fs) for hp in [.05, .3, .5] for fs in [128, 2048]]
    for hp, order, fs in designs:
        sos = signal.butter(order, hp, 'high', fs=fs, output='sos')
        _, h = signal.freqz_sos(sos, worN=f, fs=fs)
        if stream == 'ecg':
            lp = signal.butter(order, 25, 'low', fs=fs, output='sos')
            _, hl = signal.freqz_sos(lp, worN=f, fs=fs)
            h *= hl
        else:
            notch = signal.butter(5, [59, 61], 'bandstop', fs=fs, output='sos')
            _, hn = signal.freqz_sos(notch, worN=f, fs=fs)
            h *= hn
        for phase, hh in [('causal', h), ('forward_backward', np.abs(h)**2)]:
            configs.append((f'hp{hp}_order{order}_designfs{fs}_{phase}', hh))
    rows = []
    for name, h in configs:
        h = h[:, None]
        # Signed real gain and integer grid offsets are diagnostics, not repairs.
        choices = []
        for lag in range(-2, 3):
            v = h*np.exp(-2j*np.pi*f[:, None]*lag/128)
            gain = np.sum(w*np.real(np.conj(v)*observed))/max(np.sum(w*np.abs(v)**2), 1e-30)
            error = np.sqrt(np.sum(w*np.abs(observed-gain*v)**2)/max(denom, 1e-30))
            choices.append((float(error), int(lag), float(gain)))
        error, lag, gain = min(choices)
        rows.append(dict(candidate=name, relative_complex_transfer_error=error,
                         grid_lag_samples=lag, gain=gain, eligible_bins=int(eligible.sum()),
                         median_eligible_coherence=float(np.median(coherence[eligible]))))
    return sorted(rows, key=lambda r:r['relative_complex_transfer_error'])


def probes():
    manifest = pd.read_parquet(EVIDENCE/'canonical_manifest.parquet')
    manifest = manifest[manifest.missing_file_status == 'present']
    paired, candidates, selections = [], [], []
    for exp in range(1, 6):
        g = manifest[manifest.experiment == exp]
        keys = ['participant_id', 'session', 'local_stimulus_id']
        # First and median participant, both blocks, first available stimulus.
        people = sorted(g.participant_id.unique())
        ids = [people[0], people[len(people)//2]]
        units = g[g.participant_id.isin(ids)][keys].drop_duplicates().sort_values(keys)
        units = units.groupby(['participant_id','session'], as_index=False).first()
        with open_archive(exp) as z:
            for u in units.to_dict('records'):
                sub = g[(g.participant_id==u['participant_id']) & (g.session==u['session']) & (g.local_stimulus_id==u['local_stimulus_id'])]
                base = dict(experiment=exp, **u)
                selections.append(base)
                for modality in ['eeg','ecg','gaze','pupil','head','respiration']:
                    m = sub[sub.modality==modality]
                    raw = m[m.status=='aligned_release_raw']
                    proc = m[m.status=='author_processed']
                    if len(raw)!=1 or len(proc)!=1:
                        continue
                    r, p = raw.iloc[0], proc.iloc[0]
                    x, hx = array(z, r.member_path)
                    y, hy = array(z, p.member_path)
                    n = min(len(x), len(y), int(r.observed_sample_count), int(p.observed_sample_count))
                    x, y = x[:n], y[:n]
                    cols = min(x.shape[1], y.shape[1])
                    x, y = x[:, :cols], y[:, :cols]
                    valid = np.isfinite(x)&np.isfinite(y)
                    row = dict(**base, modality=modality, raw_path=r.member_path, processed_path=p.member_path,
                               raw_samples=int(r.observed_sample_count), processed_samples=int(p.observed_sample_count),
                               comparison_samples=n, columns=cols, finite_pair_fraction=float(valid.mean()))
                    if valid.any():
                        row.update(raw_q95=float(np.nanquantile(x,.95)), processed_q95=float(np.nanquantile(y,.95)),
                                   exact_equal_fraction=float(np.mean(x[valid]==y[valid])),
                                   difference_rms=float(np.sqrt(np.mean((x[valid]-y[valid])**2))),
                                   raw_std=float(np.std(x[valid])), processed_std=float(np.std(y[valid])))
                    if modality=='eeg':
                        row.update(raw_units=json.dumps(hx['units']), processed_units=json.dumps(hy['units']),
                                   raw_median_lsb=float(np.median((hx['physical_max']-hx['physical_min'])/(hx['digital_max']-hx['digital_min']))),
                                   processed_median_lsb=float(np.median((hy['physical_max']-hy['physical_min'])/(hy['digital_max']-hy['digital_min']))),
                                   processed_channel_mean_rms=float(np.sqrt(np.mean(np.mean(y,axis=1)**2))),
                                   processed_median_channel_rms=float(np.median(np.sqrt(np.mean(y*y,axis=0)))))
                    if modality in ['ecg','eeg']:
                        for c in spectral_candidates(x if modality=='ecg' else x[:,::8], y if modality=='ecg' else y[:,::8], modality):
                            candidates.append(dict(**base, modality=modality, **c))
                    if modality in ['gaze','pupil']:
                        name = str(p.member_path).split('_desc-')[0] + f'_desc-{modality}_interpolation_timestamps.tsv.gz'
                        if name in z.namelist():
                            intervals = pd.read_csv(io.BytesIO(gzip.decompress(z.read(name))), sep='\t').to_numpy(float)
                            mask, _ = intervals_to_mask(intervals, n)
                            good = valid & (~mask[:,None])
                            row['outside_correction_equal_fraction'] = float(np.mean(x[good]==y[good])) if good.any() else None
                            row['outside_correction_difference_rms'] = float(np.sqrt(np.mean((x[good]-y[good])**2))) if good.any() else None
                            row['correction_fraction'] = float(mask.mean())
                    paired.append(row)
        print('Targeted paired probes completed',exp,flush=True)
    pd.DataFrame(paired).to_csv(EVIDENCE/'gate_closure_signal_pairs.csv',index=False)
    pd.DataFrame(candidates).to_csv(EVIDENCE/'gate_closure_filter_candidates.csv',index=False)
    write_json(EVIDENCE/'gate_closure_probe_selection.json',dict(rule='first and median released participant; both sessions; first task in each session; no outcome selection',probes=selections))


def quiz_content():
    one = json.loads((EVIDENCE/'release_metadata/experiment1/phenotype/stimuli_questionnaire.json').read_text())
    two = json.loads((EVIDENCE/'release_metadata/experiment2/phenotype/stimuli_questionnaire.json').read_text())
    rows = []
    for qt in ['domain','memory']:
        global_q = 0
        for stim, questions in one['questions'][qt].items():
            for q, text in questions.items():
                global_q += 1
                k = f'q{global_q}'
                a = one['answers'][qt][stim][q]
                b = two['answers'][qt].get(k,{})
                rows.append(dict(question_type=qt,local_stimulus_id=int(stim[4:]),exp1_question=int(q[1:]),exp2_question=global_q,
                                 identical_question=text==two['questions'][qt].get(k),
                                 identical_option_order=list(a.values())==list(b.values()),question_sha256=hashlib.sha256(text.encode()).hexdigest()))
    pd.DataFrame(rows).to_csv(EVIDENCE/'gate_closure_quiz_content_map.csv',index=False)
    items = pd.read_parquet(EVIDENCE/'quiz_items.parquet')
    summaries = []
    for exp in [1,2]:
        g = items[(items.experiment==exp)&items.participant_metadata_available&items.signal_participant_available]
        for qt, h in g.groupby('question_type'):
            counts = h.answer.value_counts().reindex([1,2,3,4],fill_value=0)
            summaries.append(dict(experiment=exp,question_type=qt,rows=len(h),people=h.participant_id.nunique(),
                                  key_values=sorted(h.correct_answer.unique().tolist()),
                                  score=float(h.recomputed_score.mean()),answer_counts={str(k):int(v) for k,v in counts.items()}))
    write_json(EVIDENCE/'gate_closure_quiz_content_summary.json',dict(content_items=len(rows),identical_questions=sum(r['identical_question'] for r in rows),identical_option_orders=sum(r['identical_option_order'] for r in rows),response_distributions=summaries,
        interpretation='Content/order mapping is verified; the response code to presented-option permutation is not established by these content schemas. No majority-vote key or outcome-maximizing permutation is used.'))


def ecg_full():
    """All available ECG pairs, fixed shortlist established by targeted controls."""
    m = pd.read_parquet(EVIDENCE/'canonical_manifest.parquet')
    m = m[(m.modality=='ecg') & (m.missing_file_status=='present')]
    keys = ['experiment','participant_id','session','local_stimulus_id']
    raw = m[m.status=='aligned_release_raw']
    proc = m[m.status=='author_processed']
    pairs = raw.merge(proc,on=keys,validate='one_to_one',suffixes=('_raw','_processed'))
    rows = []
    for exp, g in pairs.groupby('experiment'):
        with open_archive(int(exp)) as z:
            for r in g.to_dict('records'):
                x, _ = array(z,r['member_path_raw']); y, _ = array(z,r['member_path_processed'])
                # Same competing shortlist at every record, never score-selected.
                c = spectral_candidates(x,y,'ecg')
                row = {k:r[k] for k in keys}
                row.update(raw_path=r['member_path_raw'],processed_path=r['member_path_processed'],
                           raw_samples=len(x),processed_samples=len(y),status='tested' if c else 'insufficient_finite_data_or_coherence')
                if c:
                    row.update(c[0])
                    target = next(v for v in c if v['candidate']=='hp0.5_order5_designfs2048_causal')
                    row.update(target_error=target['relative_complex_transfer_error'],target_gain=target['gain'],
                               target_grid_lag=target['grid_lag_samples'],
                               runner_up_error=c[1]['relative_complex_transfer_error'],
                               identity_error=next(v['relative_complex_transfer_error'] for v in c if v['candidate']=='identity'))
                rows.append(row)
        print('Dataset-wide ECG transfer completed',exp,len(g),flush=True)
    pd.DataFrame(rows).to_csv(EVIDENCE/'gate_closure_ecg_all_pairs.csv',index=False)


def historical_quiz():
    """Compare content and aggregate score distributions without inventing IDs."""
    from scipy.io import loadmat
    workbook = json.loads((EVIDENCE/'gate_closure_Education_questions.json').read_text())['Questions']
    headers = workbook[0]
    records = [dict(zip(headers,r)) for r in workbook[1:] if r and isinstance(r[0],(float,int))]
    schema = json.loads((EVIDENCE/'release_metadata/experiment1/phenotype/stimuli_questionnaire.json').read_text())
    content = []
    for r in records:
        if int(r['Video_no']) > 5: continue
        qt = 'memory' if r['Position']=='Post' else 'domain'
        stim,q = f"stim{int(r['Video_no'])}", f"q{int(r['Local_Question_no'])}"
        if stim not in schema['questions'][qt] or q not in schema['questions'][qt][stim]:
            continue
        text = schema['questions'][qt][stim][q]
        options = list(schema['answers'][qt][stim][q].values())
        normalized = lambda value: ' '.join(str(value).split())
        content.append(dict(question_type=qt,local_stimulus_id=int(r['Video_no']),question_no=int(r['Local_Question_no']),
                            workbook_row=records.index(r)+2,identical_question=r['Question']==text,
                            identical_option_order=[r[f'Option_{i}'] for i in range(1,5)]==options,
                            whitespace_normalized_question_equal=normalized(r['Question'])==normalized(text),
                            whitespace_normalized_options_equal=[normalized(r[f'Option_{i}']) for i in range(1,5)]==[normalized(v) for v in options],
                            no_correct_options=r['No_correct_options'],category=r['Category']))
    pd.DataFrame(content).to_csv(EVIDENCE/'gate_closure_original_workbook_mapping.csv',index=False)
    d = loadmat(EVIDENCE/'gate_closure_P01_Experiment_2_Points.mat',simplify_cells=True)
    demographics=pd.DataFrame(loadmat(EVIDENCE/'gate_closure_P01_Experiment_2_demographics.mat',simplify_cells=True)['demographicData'])
    demographics['participant_id']=demographics.no.map(lambda n:f'sub-{int(n):02d}')
    released_people=pd.read_csv(EVIDENCE/'release_metadata/experiment2/participants.tsv',sep='\t')
    joined=demographics.merge(released_people,on='participant_id',validate='one_to_one',suffixes=('_historical','_release'))
    trait_agreement={}
    trait_shared_missing={}
    for field in ['Age','Sex','Study_time','GPA']:
        a,b=joined[field+'_historical'],joined[field+'_release']
        if field=='Sex':matches=a.astype(str).str.casefold()==b.astype(str).str.casefold()
        else:matches=(pd.to_numeric(a,errors='coerce')==pd.to_numeric(b,errors='coerce')) | (a.isna()&b.isna())
        trait_agreement[field]=int(matches.sum())
        trait_shared_missing[field]=int((a.isna()&b.isna()).sum())
    order=np.asarray(loadmat(EVIDENCE/'gate_closure_P01_Experiment_2_stimuli_order.mat',simplify_cells=True)['stimuli_order'])
    cohort_trace=dict(historical_people=len(demographics),released_people=len(released_people),matched_ids=len(joined),
        identical_id_sets=set(demographics.participant_id)==set(released_people.participant_id),
        matching_companion_trait_counts=trait_agreement,
        shared_missing_companion_trait_counts=trait_shared_missing,
        stimulus_order_shape=list(order.shape),order_rows_are_permutations_of_1_5=bool(np.all(np.sort(order,axis=1)==np.arange(1,6))),
        boundary='The keyed companion strongly supports cohort correspondence; Points and order matrices themselves have no row IDs. No score-matrix row binding or response permutations are reconstructed.')
    outcomes = pd.read_parquet(EVIDENCE/'quiz_video_outcomes.parquet')
    summary = []
    for qt, name in [('domain','Npoints_stim_pre'),('memory','Npoints_stim_post')]:
        a = np.asarray(d[name],float)/100
        g = outcomes[(outcomes.experiment==2)&outcomes.valid_outcome&(outcomes.question_type==qt)]
        summary.append(dict(question_type=qt,historical_shape=list(a.shape),historical_mean=float(a.mean()),
                            released_pairs=len(g),released_mean=float(g.normalized_partial_score.mean()),
                            historical_sum=float(a.sum()),released_sum=float(g.normalized_partial_score.sum()),
                            scope='Unkeyed historical matrix; no participant-row reassignment. Mean/sum discrepancy cannot be explained by permuting these 31x5 cells.'))
    write_json(EVIDENCE/'gate_closure_historical_quiz_comparison.json',dict(workbook_mapped_items=len(content),
        identical_questions=sum(r['identical_question'] for r in content),identical_option_orders=sum(r['identical_option_order'] for r in content),
        whitespace_normalized_questions=sum(r['whitespace_normalized_question_equal'] for r in content),
        whitespace_normalized_options=sum(r['whitespace_normalized_options_equal'] for r in content),
        cohort_companion=cohort_trace,
        aggregate_comparison=summary,interpretation='Historical aggregates are evidence of non-equivalence, not a replacement target or an independent response-to-option mapping.'))


def eligibility():
    """Expose the conservative Exp.2 behavioral quarantine in a separate view."""
    outcomes = pd.read_parquet(EVIDENCE/'quiz_video_outcomes.parquet')
    outcomes['gate_behavior_eligible'] = outcomes.valid_outcome & (outcomes.experiment!=2)
    outcomes['gate_behavior_reason'] = np.where(outcomes.experiment==2,'unverified_response_option_mapping_and_historical_score_non_equivalence',
                                               np.where(outcomes.valid_outcome,'release_key_valid_bounded_provenance','preexisting_key_or_item_quarantine'))
    outcomes.to_parquet(EVIDENCE/'gate_closure_behavioral_eligibility.parquet',index=False,compression='zstd')
    tensor = pd.read_parquet(EVIDENCE/'exposure_tensor.parquet')
    # summary.py constructs valid_quiz_outcome at direct test/exposure scope:
    # session 1 for 1-3; session 2 tested tasks for 4-5.
    direct = tensor[tensor.valid_quiz_outcome].copy()
    rows=[]
    for label, g in [('release_key_audit_all',direct),('exclude_exp2_behavior',direct[direct.experiment!=2])]:
        for mods in [['eeg','ecg','eye'],['ecg','eye'],['eeg']]:
            mask=g.valid_quiz_outcome.copy()
            for mod in mods:mask &= g[mod+'_present'] & g[mod+'_basic_qc']
            s=g[mask]
            rows.append(dict(scope=label,modalities='+'.join(mods),people=s.qualified_participant_id.nunique(),
                             videos=s.canonical_video_id.nunique(),observations=len(s)))
    pd.DataFrame(rows).to_csv(EVIDENCE/'gate_closure_feasibility_counts.csv',index=False)


def sources():
    """Verify downloaded file bytes against OSF's own versioned metadata."""
    ledger_path=EVIDENCE/'gate_closure_sources.json'
    retained=json.loads(ledger_path.read_text())['sources'] if ledger_path.exists() else []
    pinned={r['path']:r for r in retained if r.get('official_sha256_match')}
    expected = {
        'gate_closure_Education_questions.xlsx':('gate_closure_osf_m7gj4_data.json','Education_questions.xlsx'),
        'gate_closure_P01_Experiment_2_Points.mat':('gate_closure_osf_m7gj4_exp2.json','Experiment_2_Points.mat'),
        'gate_closure_P01_Experiment_2_questionnaire.mat':('gate_closure_osf_m7gj4_exp2.json','Experiment_2_questionnaire.mat'),
        'gate_closure_P01_figure_1.m':('gate_closure_osf_m7gj4_code.json','figure_1.m'),
        'gate_closure_P01_figure_2.m':('gate_closure_osf_m7gj4_code.json','figure_2.m'),
        'gate_closure_P01_Experiment_2_demographics.mat':('gate_closure_osf_m7gj4_exp2.json','Experiment_2_demographics.mat'),
        'gate_closure_P01_Experiment_2_stimuli_order.mat':('gate_closure_osf_m7gj4_exp2.json','Experiment_2_stimuli_order.mat'),
        'gate_closure_p03_preprocessEEGdata.m':('gate_closure_osf_d4k3q_routines.json','preprocessEEGdata.m'),
    }
    rows=[]
    for local, (listing, name) in expected.items():
        entries=json.loads((EVIDENCE/listing).read_text())['data']
        r=next(x for x in entries if x['attributes'].get('name')==name)
        b=(EVIDENCE/local).read_bytes();h=hashlib.sha256(b).hexdigest()
        a=r['attributes']
        assert len(b)==a['size'] and h==a['extra']['hashes']['sha256'],local
        if local in pinned:
            assert h==pinned[local]['sha256'] and a.get('current_version')==pinned[local]['source_version'],f'Changed pinned OSF source: {local}'
        rows.append(dict(path=local,bytes=len(b),sha256=h,source_url=r['links']['download'],
                         metadata_listing=listing,osf_file_id=r['id'],source_version=a.get('current_version'),
                         source_modified=a.get('date_modified'),official_sha256_match=True))
    for p in sorted(EVIDENCE.glob('gate_closure_*')):
        retrieval = p.name.startswith('gate_closure_osf_') or p.name in {
            'gate_closure_upstream_main.json','gate_closure_official_experiments.html',
            'gate_closure_official_experiments.js','gate_closure_official_stars_quiz.tsv'}
        if p.name in expected or not retrieval:continue
        b=p.read_bytes();rows.append(dict(path=p.name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),
                                        kind='primary retrieval snapshot; see retrieval script for URL'))
    write_json(EVIDENCE/'gate_closure_sources.json',dict(verified_utc=now(),release_record=22968459,
        upstream_main=json.loads((EVIDENCE/'gate_closure_upstream_main.json').read_text())['sha'],
        sources=rows,access_limit='fjxaq is a file-download GUID, not an accessible project node; its workbook is discoverable and verified via m7gj4. Historical response permutations and executed release option logs were not found.',
        libraries={name:version(name) for name in ['numpy','scipy','pandas','pyarrow']}))


def apply_document_status():
    """Keep regenerated audit reports subordinate to the follow-up evidence."""
    from .report import md
    doc = EVIDENCE.parent
    counts = pd.read_csv(EVIDENCE/'gate_closure_feasibility_counts.csv')
    marker = '**Gate follow-up — 2026-10-02:** '
    def banner(name, message, link='gate_closure.md'):
        p = doc/name
        body = p.read_text()
        # Idempotent across report regeneration or independent status refreshes.
        lines = [line for line in body.splitlines() if not line.startswith(marker)]
        lines.insert(2,marker+message+f' [Evidence and verdict]({link}).')
        import re
        text='\n'.join(lines)
        text=text.replace(lines[2]+'\n',lines[2]+'\n\n',1)
        p.write_text(re.sub(r'\n{3,}','\n\n',text).rstrip()+'\n')
    gates = pd.read_csv(EVIDENCE/'p0_gate_status.csv')
    old = EVIDENCE/'superseded_checkpoints/p0_gate_status_before_gate_closure.csv'
    if not old.exists():gates.to_csv(old,index=False)
    gates.loc[gates.gate=='OQ-03',['status','evidence_or_limit']] = [
        'RELEASE SCORING VERIFIED / EXP2 BEHAVIOR QUARANTINED',
        'Content/order schemas match across 1-2, but Exp.2 response canonicalization is not verified and historical aggregates disagree. Exp.2 behavioral outcomes excluded; Exp.3 duplicate quarantine and partial/exact distinction remain.']
    gates.loc[gates.gate=='OQ-06',['status','evidence_or_limit']] = [
        'BLOCKING / EMPIRICALLY NARROWED',
        'All 1,140 testable ECG pairs favor causal fifth-order 0.5–25 Hz at design rate 2048 Hz with near-unit gain; 10 raw ECG files are all NaN. EEG/eye execution options, native transforms, annotations and absolute ECG/belt calibration remain unresolved.']
    gates.to_csv(EVIDENCE/'p0_gate_status.csv',index=False)
    p=doc/'open_questions_resolved.md'
    body=p.read_text();start=body.index('| gate |');end=body.index('\n\n',start)
    p.write_text(body[:start]+md(gates).rstrip()+body[end:])
    cf=pd.read_csv(EVIDENCE/'research_feasibility.csv')
    old=EVIDENCE/'superseded_checkpoints/research_feasibility_before_gate_closure.csv'
    if not old.exists():cf.to_csv(old,index=False)
    for i,r in cf.iterrows():
        before=counts[(counts.scope=='release_key_audit_all')&(counts.modalities==r.modalities)].iloc[0]
        after=counts[(counts.scope=='exclude_exp2_behavior')&(counts.modalities==r.modalities)].iloc[0]
        cf.loc[i,'release_key_audit_people']=int(before.people)
        cf.loc[i,'release_key_audit_videos']=int(before.videos)
        cf.loc[i,'release_key_audit_observations']=int(before.observations)
        for c,k in [('usable_people','people'),('usable_videos','videos'),('usable_person_video_observations','observations')]:
            cf.loc[i,c]=int(after[k])
        cf.loc[i,'valid_outcome']='Exp.2 behavior excluded; keyed memory outcomes 1,3-5; score definitions and exposure chronology separate'
        cf.loc[i,'evidence']='gate_closure.md; gate_closure_behavioral_eligibility.parquet; gate_closure_feasibility_counts.csv; existing modality/QC tables'
        cf.loc[i,'confounds']=str(r.confounds).replace('Only11 videos','Only 8 videos in the multimodal behavioral subset').replace('Only 11 videos','Only 8 videos in the multimodal behavioral subset').replace('N;11 videos','N; 8 videos').replace('N;8 videos','N; 8 videos')
        if r.candidate=='C03':
            cf.loc[i,'feasibility']='MEDIUM (3–5 only)'
            cf.loc[i,'confounds']='Exp.2 incidental-learning behavior excluded; 4/5 share 3 videos; different exposure histories; cross-experiment human overlap unresolved'
        if r.candidate=='C07':
            cf.loc[i,'confounds']='Release integrity includes all records; behavioral ceilings exclude Exp.2. P01 Exp.2 aggregate non-equivalence established; original response permutations and executed figure inputs unavailable'
    cf.to_csv(EVIDENCE/'research_feasibility.csv',index=False)
    (doc/'research_feasibility.md').write_text('''# Research-question feasibility — no final question selected

**OUR INFERENCE — updated 2026-10-02.** The current behavioral ceilings exclude Experiment 2. The original release-key ceilings remain in the CSV as historical audit fields; they do not certify response-option provenance. Counts below reuse exactly the prior direct-test/exposure rule and provisional QC. OQ-06 still blocks a full multimodal transition. [Gate findings](gate_closure.md).

'''+md(cf,['candidate','direction','feasibility','usable_people','usable_videos','usable_person_video_observations','modalities'])+'\n'+md(cf,['candidate','confounds','timing','prior_occupancy','second_dataset'])+'''
[Complete matrix](evidence/research_feasibility.csv); [exact before/after counts](evidence/gate_closure_feasibility_counts.csv). C01/C02/C04 remain conditional MEDIUM with smaller cohorts. C03 permits bounded 3–5 protocol comparisons; incidental-versus-intentional behavioral transport is ineligible. C05/C06 remain LOW. C07 HIGH concerns demonstrable release measurement/integrity, which may inspect all records; its table counts are the conservative behavioral subset, and exact historical-paper reproduction remains conditional.

Exp.3 is the strongest remaining first-view multimodal quiz cohort (24 people / 124 observations / 6 videos). Exp.4 contributes 33 / 92 / 3 single-exposure tested observations; Exp.5 contributes 37 / 108 / 3 repeat/preview/incentive observations. Exp.2 remains available for signal/condition measurement within provenance limits. None of these counts guarantees power, fixes selection bias or selects a final question. Preserve separate partial/exact outcomes, chronology, masks and people/video grouping. Absolute amplitude, fine timing/directional claims and unverifiable preprocessing invariance remain constrained. No model is developed.
''')
    (doc/'open_questions_remaining.md').write_text('''# Remaining material gates before Research Gap & Problem Formulation

**Verdict — 2026-10-02: NOT FULLY CLOSED.** The full multimodal transition remains blocked by OQ-06. [Executed follow-up and findings](gate_closure.md).

1. **OQ-06 / BLOCKING, empirically narrowed:** exact EEG high-pass/reference, RPCA/EOG/artifact/interpolation options and fit scope; eye correction/transform options; native resampling/clock lineage; and actual ECG/belt physical calibration remain unavailable. ECG's 0.5–25 Hz fifth-order causal configuration is strongly supported across 1,140 testable pairs, and numerical gain is preserved, but this does not establish physical units or other stream recipes. A source-backed execution record or a documented, scientifically adequate reconstruction route is still needed. Available aligned raw exports cannot recover discarded native observations/annotations.
2. **OQ-03 / behavioral mapping provenance unresolved, safety decision closed by exclusion:** Exp.2 content/option order is mapped, but participant response permutations are not. Historical original-source 31 × 5 score matrices disagree materially with the release, without participant keys permitting replacement. Exp.2 domain/memory targets are quarantined from performance comparison, pooling and physiology–quiz inference. This issue constrains incidental-learning and five-experiment behavioral comparisons; it does not block analysis of the remaining cohorts once OQ-06 is addressed.

After exclusion, direct basic-QC EEG+ECG+eye behavioral ceilings are 94 qualified people / 324 observations / 8 videos; ECG+eye 94 / 327 / 8. Scope boundaries remain: no certified sub-second/directional/item-timed analysis without native timing/item alignment; no isolated reward effect or certified cross-experiment unique-human generalization without allocation/identity evidence; preserve heterogeneous scoring/exposure definitions. These narrow candidate claims rather than creating new blanket gates. The older P05/supplement/trait/licensing questions stay in the historical queue and are relevant only when a candidate requires them.

The [author-query draft](evidence/author_query_draft.md) contains the now-specific missing evidence. It remains unsent. No final problem or model is selected. Focused gap mapping around verified measurement limitations is possible, but it does not close the full multimodal formulation gate.
''')
    banner('preprocessing_provenance.md','The table below records declarations and earlier documentary limits. The follow-up empirically identifies the ECG transfer configuration, rules out a simple normalized interpretation of probed pupil exports, and leaves OQ-06 blocking for actual EEG/eye options and absolute calibration.')
    banner('quiz_integrity.md','All 12,470 rows still reconstruct against supplied keys. Exp.2 content mapping is verified, but response mapping is unverified and historical scores disagree. Its domain/memory targets are now quarantined from scientific behavioral use; this table remains an encoding audit.')
    banner('outcome_characterization.md','The 736 outcomes and Exp.2 distributions below describe release-key reconstructions. Scientific behavioral eligibility now excludes 155 Exp.2 memory outcomes, leaving 581 for 147 qualified people. Exp.2 differences must not be interpreted as learning/protocol effects.')
    banner('missingness.md','Exp.2 score/quality entries below are retained as release-encoding diagnostics; they cannot establish behavioral selection or performance effects. Use the separate gate eligibility view for scientific targets.')
    banner('modality_coverage.md','The tables below remain physical/QC/release-key coverage. Current behavior-eligible EEG+ECG+eye coverage is 94 people / 324 observations / 8 videos after Exp.2 exclusion; ECG+eye is 94 / 327 / 8. These are eligibility counts, not new signal-QC exclusions.')
    banner('ecg_quality.md','All 1,140 testable raw/filtered pairs favor causal fifth-order 0.5–25 Hz at design fs 2048 and near-unit gain; ten all-NaN raw files remain untestable. Absolute units and manual peak history remain open; the earlier RR/RMSSD findings stand.')
    banner('eeg_quality.md','Paired low-frequency transfer tests do not distinguish an executed filter recipe. The final 64-channel derivative is not an exact common-average output; earlier references are still possible. No spectral/16 Hz result certifies the unknown cleaning options.')
    banner('eye_quality.md','Exporter column selection and 17 pupil probes exclude a simple 95th-percentile-normalized output interpretation. Head-regression history, buffers and kernels remain open; differences outside masks are not proof of unmarked native artifacts.')
    banner('open_questions_resolved.md','The immediate Exp.2 pooling/comparison decision is closed by behavioral quarantine; its original response provenance stays unresolved. OQ-06 remains blocking despite strong ECG narrowing.')
    banner('README.md','Current behavioral eligibility excludes Exp.2: 581 memory outcomes overall; multimodal QC ceiling 94 people / 324 observations / 8 videos. The full-release counts below remain forensic release-key/QC evidence. OQ-06 is empirically narrowed but still blocking; the full transition is not ready.')
    p=doc/'README.md';body=p.read_text().replace('| valid_quiz_person_video_pairs |','| release_key_memory_pairs |')
    # Override the old strongest-cohort conclusion without changing source counts.
    lines=body.splitlines()
    for i,line in enumerate(lines):
        if line.startswith('6. **Strongest experiments?**'):
            lines[i]='6. **Strongest experiments?** **OUR INFERENCE:** Exp.3 is the strongest remaining first-view multimodal quiz cohort; Exp.4 supports the single-exposure tested subset and Exp.5 bundled repeat/preview/incentive transport. Exp.2 remains a signal/condition cohort while its behavioral targets are quarantined. Exp.1 offers eye-only context. No experiment is selected for a paper.'
    p.write_text('\n'.join(lines)+'\n')
    body=p.read_text().replace('**Resolve the blocking OQ-06 preprocessing execution/scaling provenance, and verify Exp.2 answer-order canonicalization before behavioral pooling.** After that closure, retain the duplicate-item quarantine and explicit timing/identity boundaries and proceed to **Research Gap & Problem Formulation**. No final question is selected here.',
        '**Gate not fully closed:** resolve the remaining OQ-06 EEG/eye execution, native-lineage and physical-calibration provenance before the full multimodal transition. Exp.2 behavioral pooling is now disallowed, with its targets quarantined; original response mapping remains needed only to reinstate those targets. The revised multimodal behavioral ceiling is 94 people / 324 observations / 8 videos. [Follow-up findings and reproduction](gate_closure.md). No final question or model is selected.')
    p.write_text(body)
    banner('evidence/README.md','New gate_closure_* artifacts retain paired/all-ECG transfer tests, OSF hash-verified inputs, content maps, historical aggregate comparisons and an explicit behavioral eligibility view. The original quiz tables are unchanged. The generating module is bbbd_audit.gate_closure; report generation automatically reapplies this status.',link='../gate_closure.md')
    p=doc/'evidence/author_query_draft.md'
    body=p.read_text()
    detail='''
## Follow-up evidence for a focused query — 2026-10-02

ECG: all 1,140 testable release pairs favor causal fifth-order 0.5–25 Hz designed at 2048 Hz, with median gain 0.999975. Please confirm historical invocation, unit calibration and manual peak provenance rather than only function defaults. Ten Exp.2 sub-29 raw files contain all NaNs.

EEG/eye: the export runner loads preprocessed arrays and supplies no preprocessing option record. Please provide executed per-cohort EEG reference/high-pass/RPCA/EOG/artifact options and fit scope, plus eye buffers/transform variants and native resampling lineage. Exported pupil column 1 is not the separate postprocessing function's normalized column 3.

Exp.2: all 106 content/option-order entries match Exp.1, but P01 OSF Experiment_2_Points.mat has memory mean 0.545308 versus 0.257087 in v1.1 and domain mean 0.501790 versus 0.255293. Both have 31 × 5 cells; cell permutation cannot reconcile the means. The demographic companion matches all 31 local IDs and core trait coding/missingness. Please supply response-position to canonical-option permutations, explicit score-matrix row binding and the source scoring/export step. The historical aggregate matrix is not used to replace release labels.

This evidence is local and the draft remains unsent.
'''
    body=body.split('\n## Follow-up evidence for a focused query')[0]
    p.write_text(body.rstrip()+'\n'+detail)


def validate_followup():
    """Validate new scientific dispositions independently of the legacy QC view."""
    checks=[]
    def check(name, value, detail=''):
        checks.append(dict(name=name,passed=bool(value),detail=detail))
    ledger=json.loads((EVIDENCE/'gate_closure_sources.json').read_text())
    originals=[r for r in ledger['sources'] if r.get('official_sha256_match')]
    check('eight original files match retained official source hashes',len(originals)==8 and all(
        hashlib.sha256((EVIDENCE/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in originals))
    check('upstream main unchanged from pinned source',ledger['upstream_main']=='5109afa0fd70c407b869108106f5808c6b0cc33c')
    content=pd.read_csv(EVIDENCE/'gate_closure_quiz_content_map.csv')
    check('106 one-to-one content/order mappings',len(content)==106 and not content.duplicated(['question_type','exp2_question']).any()
          and content.identical_question.all() and content.identical_option_order.all())
    historical=json.loads((EVIDENCE/'gate_closure_historical_quiz_comparison.json').read_text())
    cohort=historical['cohort_companion']
    check('Exp.2 keyed companion matches all IDs and core traits',cohort['matched_ids']==31 and cohort['identical_id_sets']
          and all(v==31 for v in cohort['matching_companion_trait_counts'].values()))
    check('historical non-equivalence independently visible in both sums',len(historical['aggregate_comparison'])==2 and all(
        r['historical_shape']==[31,5] and r['released_pairs']==155 and abs(r['historical_sum']-r['released_sum'])>1 for r in historical['aggregate_comparison']))
    q=pd.read_parquet(EVIDENCE/'quiz_video_outcomes.parquet')
    e=pd.read_parquet(EVIDENCE/'gate_closure_behavioral_eligibility.parquet')
    check('original outcome columns preserved exactly',q.equals(e[q.columns]))
    check('eligibility excludes only Exp.2 beyond previous quarantines',np.array_equal(e.gate_behavior_eligible.to_numpy(),
        (q.valid_outcome & (q.experiment!=2)).to_numpy()))
    memory=e[(e.question_type=='memory')&e.gate_behavior_eligible]
    check('581 behavioral memory outcomes and 147 qualified people',len(memory)==581 and memory.qualified_participant_id.nunique()==147)
    f=pd.read_csv(EVIDENCE/'gate_closure_ecg_all_pairs.csv')
    tested=f[f.status=='tested'];skipped=f[f.status!='tested']
    check('all 1150 available ECG pairs accounted for',len(f)==1150 and not f.duplicated(['experiment','participant_id','session','local_stimulus_id']).any())
    check('all 1140 testable ECG pairs favor native-rate causal fifth-order response',len(tested)==1140 and
          tested.candidate.eq('hp0.5_order5_designfs2048_causal').all() and tested.target_grid_lag.eq(0).all() and
          (tested.target_error<tested.runner_up_error).all())
    qc=pd.read_parquet(EVIDENCE/'channel_qc.parquet')
    raw_invalid=qc[(qc.experiment==2)&(qc.participant_id=='sub-29')&(qc.modality=='ecg')&(qc.status=='aligned_release_raw')]
    check('ten untestable sources are all-NaN raw ECG, not hidden successes',len(skipped)==10 and skipped.participant_id.eq('sub-29').all()
          and skipped.experiment.eq(2).all() and len(raw_invalid)==10 and (raw_invalid.nan_count==raw_invalid.samples).all())
    counts=pd.read_csv(EVIDENCE/'gate_closure_feasibility_counts.csv')
    now_counts=counts[counts.scope=='exclude_exp2_behavior'].set_index('modalities')
    check('revised direct multimodal counts',[int(now_counts.loc['eeg+ecg+eye',k]) for k in ['people','observations','videos']]==[94,324,8])
    check('revised direct cardiac/eye counts',[int(now_counts.loc['ecg+eye',k]) for k in ['people','observations','videos']]==[94,327,8])
    candidates=pd.read_csv(EVIDENCE/'research_feasibility.csv')
    check('all candidate behavioral ceilings use the current view',all(int(r.usable_people)==int(now_counts.loc[r.modalities,'people'])
          and int(r.usable_person_video_observations)==int(now_counts.loc[r.modalities,'observations'])
          and int(r.usable_videos)==int(now_counts.loc[r.modalities,'videos']) for r in candidates.itertuples()))
    gates=pd.read_csv(EVIDENCE/'p0_gate_status.csv').set_index('gate')
    check('blocking and quarantine statuses are explicit',gates.loc['OQ-06','status'].startswith('BLOCKING') and 'QUARANTINED' in gates.loc['OQ-03','status'])
    tests=(EVIDENCE/'gate_closure_tests.log').read_text()
    check('20 tests including transfer negative controls passed','Ran 20 tests' in tests and '\nOK\n' in tests and 'FAILED' not in tests)
    result=dict(validated_utc=now(),status='passed' if all(r['passed'] for r in checks) else 'failed',checks=checks,
                scope='New gate findings and scientific eligibility; legacy full-release QC validation is separate.')
    write_json(EVIDENCE/'gate_closure_validation.json',result)
    if result['status']!='passed':raise ValueError([r for r in checks if not r['passed']])
    print(result['status'],len(checks),'follow-up checks',flush=True)
    return result


def main():
    quiz_content()
    probes()
    historical_quiz()
    eligibility()
    ecg_full()
    sources()
    if (EVIDENCE/'p0_gate_status.csv').exists():apply_document_status()


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--validate',action='store_true',help='Validate retained follow-up evidence without re-running signal probes')
    args=parser.parse_args()
    if args.validate:validate_followup()
    else:main()
