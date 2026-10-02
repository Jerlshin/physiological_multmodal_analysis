"""Strict final evidence checks, source fingerprints and local-link verification."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from .io import ROOT, DATA, EVIDENCE, now, release, verified_entry, write_json

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        while b:=f.read(8*1024*1024):h.update(b)
    return h.hexdigest()

def run(phase='final'):
    checks=[]
    def check(name, passed, detail=''):
        checks.append(dict(name=name,passed=bool(passed),detail=detail))
    manifest=json.loads((EVIDENCE/'download_manifest.json').read_text())
    check('all five canonical files pinned and immutable',len(manifest)==5)
    for official in release()['files']:
        p=DATA/'canonical_source'/official['key']
        rows=[r for r in manifest if r['filename']==p.name]
        check(p.name+' cached official checksum identity',p.is_file() and len(rows)==1 and verified_entry(rows[0],official,p.stat().st_size))
        check(p.name+' read-only mode',p.stat().st_mode&0o222==0)
    inventory=pd.read_parquet(EVIDENCE/'archive_members.parquet')
    check('unique ZIP-member keys',not inventory.duplicated(['archive','path']).any())
    check('full inventory',len(inventory)==41251)
    files=pd.read_parquet(EVIDENCE/'canonical_manifest.parquet')
    physical=files[files.missing_file_status=='present']
    check('unique canonical record keys',not files.path.duplicated().any())
    check('full signal audit',len(physical)==16038 and set(physical.experiment)=={1,2,3,4,5})
    check('no parse errors',not physical.qc_status.eq('parse_error').any())
    check('verified released grid',(physical.nominal_sampling_rate==128).all())
    official_members=inventory.set_index(['archive','path']).bytes.to_dict()
    check('all physical members and sizes match ZIP inventory',all(official_members.get((r.archive,r.member_path))==r.file_size for r in physical.itertuples()))
    check('valid duration never exceeds observation',physical.valid_duration.between(0,physical.observed_duration+1e-8).all())
    mask_ok=True
    for r in physical.itertuples():
        bits=np.unpackbits(np.frombuffer(r.invalid_sample_bits,np.uint8),bitorder='little')[:int(r.qc_sample_count)]
        mask_ok &= len(bits)==r.qc_sample_count and abs((len(bits)-bits.sum())/128-r.valid_duration)<1e-8
    check('all compact masks agree with exact valid duration',mask_ok)
    eeg=physical[physical.modality=='eeg']
    check('EEG padding is within one calibration LSB',(eeg.padding_samples==eeg.padding_tail_within_one_lsb_rows).all())
    traits=pd.read_parquet(EVIDENCE/'participant_traits.parquet')
    check('unique experiment-qualified person keys',len(traits)==178 and not traits.qualified_participant_id.duplicated().any())
    people=physical[['experiment','participant_id','asrs_questionnaire_available']].drop_duplicates()
    check('observed ASRS coverage',people.asrs_questionnaire_available.sum()==147)
    q=pd.read_parquet(EVIDENCE/'quiz_video_outcomes.parquet')
    check('unique outcome join keys',not q.duplicated(['experiment','participant_id','local_stimulus_id','question_type']).any())
    memory=q.query("question_type=='memory' and valid_outcome")
    check('valid memory outcomes after quarantine',len(memory)==736)
    items=pd.read_parquet(EVIDENCE/'quiz_items.parquet')
    check('all supplied item scores reconstructed',len(items)==12470 and not items.score_mismatch.any() and not items.correctness_mismatch.any())
    single=items[items.experiment<=2];multiple=items[items.experiment>=3]
    check('answer-option ranges and denominators',single.answer.isin([1,2,3,4]).all() and single.correct_answer.isin([1,2,3,4]).all() and not multiple.option_out_of_range.any() and not multiple.denominator_mismatch.any())
    check('duplicate outcome quarantine',not q[q.duplicate_items>0].valid_outcome.any())
    check('score ranges',q.normalized_partial_score.between(0,1).all())
    aggregates=pd.read_parquet(EVIDENCE/'quiz_aggregate_comparison.parquet')
    check('aggregates within declared rounding tolerance',not aggregates.aggregate_exceeds_rounding_tolerance.any() and aggregates['_merge'].eq('both').all())
    stimulus=pd.read_csv(EVIDENCE/'stimulus_map.csv')
    check('unambiguous local/video mapping',not stimulus.duplicated(['experiment','local_stimulus_id']).any() and stimulus.canonical_video_id.nunique()==11)
    exposures=pd.read_parquet(EVIDENCE/'exposure_tensor.parquet')
    check('unambiguous exposure keys',len(exposures)==1474 and not exposures.duplicated(['experiment','participant_id','session','local_stimulus_id']).any())
    check('missing signals do not erase available outcomes',exposures.valid_quiz_outcome.sum()==736 and files[files.missing_file_status!='present'].participant_metadata_available.all())
    ints=pd.read_csv(EVIDENCE/'modality_intersections.csv')
    core=ints.query("experiment=='ALL' and stage=='basic_qc' and requires_valid_quiz and modalities=='eeg+ecg+eye'").iloc[0]
    check('core independent-unit counts',core.people==120 and core.person_video_exposures==444 and core.videos==11)
    check('core validity union duration',abs(core.valid_duration_seconds-103100.5625)<1e-8)
    peaks=pd.read_parquet(EVIDENCE/'peak_qc.parquet')
    breathing=peaks[peaks.event_type=='breath_peak']
    check('breath metrics use respiratory semantics',len(breathing)==546 and breathing.median_hr_bpm.isna().all() and breathing.median_breaths_per_minute.notna().all())
    check('all discrete timestamps finite',peaks.nonfinite_peak_count.sum()==0)
    cardiac=peaks[peaks.event_type=='rpeak']
    check('cardiac ordering and documented edge exceptions',cardiac.duplicate_peaks.sum()==0 and cardiac.nonmonotonic_peaks.sum()==0 and cardiac.rpeak_out_of_waveform_count.sum()==5 and cardiac.rpeak_max_after_end_seconds.max()<1/128)
    with zipfile.ZipFile(EVIDENCE/'audit_execution_code.zip') as z:
        executed_hash=hashlib.sha256(z.read('src/bbbd_audit/audit.py')+z.read('src/bbbd_audit/qc.py')).hexdigest()
    qc_markers=[json.loads((EVIDENCE/f'audit_exp{e}.json').read_text()) for e in range(1,6)]
    check('exact full-QC source snapshot matches execution markers',all(m['code_sha256']==executed_hash for m in qc_markers))
    check('all experiment checkpoints completed',all(m['status']=='complete_lightweight_qc' and not m['errors'] for m in qc_markers))
    cfg=json.loads((ROOT/'audit_config.json').read_text())
    cfg_hash=hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
    check('execution configuration matches retained configuration',all(m['config_sha256']==cfg_hash for m in qc_markers))
    tests=(EVIDENCE/'tests.log').read_text()
    check('scientific unit tests passed','\nOK\n' in tests and 'FAILED' not in tests)
    if phase=='final':
        broken=[]
        amended=[ROOT/'docs/research'/n for n in ['README.md','inference_register.md','decision_log.md','selected_dataset/README.md','selected_dataset/research_readiness.md','selected_dataset/open_questions.md']]
        for p in list(EVIDENCE.parent.rglob('*.md'))+amended:
            for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text()):
                if '://' in target or target.startswith('#'):continue
                dest=(p.parent/target.split('#')[0].strip('<>')).resolve()
                if not dest.exists():broken.append(f'{p.relative_to(ROOT)} -> {target}')
        check('all report links and figures resolve',not broken,broken)
        for name in ['retention_manifest.json','storage_and_retention.md']:
            p=EVIDENCE/name if name.endswith('.json') else EVIDENCE.parent/name
            check(name+' retained',p.is_file())
    sources=sorted(list((ROOT/'src/bbbd_audit').glob('*.py'))+list((ROOT/'tests').glob('*.py'))+list((ROOT/'scripts').glob('*.py'))+[ROOT/n for n in ['audit_config.json','pyproject.toml','requirements-audit.lock','.gitignore']])
    write_json(EVIDENCE/'generating_source_fingerprints.json',[dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=sha(p)) for p in sources])
    result=dict(phase=phase,validated_utc=now(),status='passed' if all(c['passed'] for c in checks) else 'failed',checks=checks,canonical_hashes_reused='Previously computed full MD5/SHA-256; readonly modes, exact official identity and byte sizes checked here. CLI verify independently rehashes.',full_QC_execution_code_sha256=executed_hash,postprocess='Canonical questionnaire fields and separate respiratory peak metrics rebuilt by summary.py from original small keyed metadata/timestamp members; full channel/signal QC unchanged.')
    write_json(EVIDENCE/('validation.json' if phase=='final' else 'validation_pre_cleanup.json'),result)
    print(result['status'],len(checks),'checks',flush=True)
    if result['status']!='passed':raise ValueError([c for c in checks if not c['passed']])
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['pre-cleanup','final'],default='final');args=parser.parse_args();run(args.phase)
