"""Scientific invariants and parser tests; no predictive tests."""
import hashlib
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from bbbd_audit.qc import decode_bdf24, intervals_to_mask, longest_true, Stats, timestamp_metrics
from bbbd_audit.quiz import options, partial_score, video_map
from bbbd_audit.io import verify_file, verified_entry, release, EVIDENCE

class ScientificInvariants(unittest.TestCase):
    def test_bdf_signed24_extremes(self):
        values=np.array([-8388608,-32768,-1,0,1,32767,8388607],np.int32)
        u=values & 0xffffff
        data=np.stack([u&255,(u>>8)&255,(u>>16)&255],axis=1).astype(np.uint8).tobytes()
        np.testing.assert_array_equal(decode_bdf24(data),values)
    def test_mask_union_and_bounds(self):
        m,oob=intervals_to_mask([(0,1),(.5,1.5),(1.75,2.5)],256)
        self.assertEqual(m.sum(),224);self.assertEqual(oob,1)
        self.assertEqual(longest_true(m),192)
        with self.assertRaises(ValueError):intervals_to_mask([(2,1)],256)
    def test_chunk_statistics(self):
        x=np.column_stack([np.arange(1000,dtype=float),np.ones(1000)])
        x[11,0]=np.nan
        s=Stats(2)
        for a in np.array_split(x,7):s.update(a)
        r=s.result(['a','b'])
        self.assertAlmostEqual(r[0]['mean'],np.nanmean(x[:,0]))
        self.assertAlmostEqual(r[0]['std'],np.nanstd(x[:,0]))
        self.assertEqual(r[0]['nan_count'],1);self.assertTrue(r[1]['flat'])
    def test_rmssd_semantics(self):
        d=timestamp_metrics([0,1,2,3,4])
        self.assertEqual(d['rms_rr_seconds'],1)
        self.assertEqual(d['true_rmssd_seconds'],0)
        self.assertEqual(timestamp_metrics([0,1,1,2])['duplicate_peaks'],1)
    def test_breath_peak_semantics(self):
        d=timestamp_metrics([0,4,8,12], 'breath_peak')
        self.assertEqual(d['median_breaths_per_minute'],15)
        self.assertEqual(d['breath_interval_outside_4_60_bpm_fraction'],0)
        self.assertNotIn('median_hr_bpm',d)
        self.assertNotIn('rr_outside_30_200_fraction',d)
    def test_questionnaire_coverage(self):
        p=EVIDENCE/'canonical_manifest.parquet'
        if not p.exists():return
        t=pd.read_parquet(p).query("missing_file_status=='present'")
        people=t[['experiment','participant_id','asrs_questionnaire_available']].drop_duplicates()
        self.assertEqual(people.asrs_questionnaire_available.sum(),147)
        self.assertEqual(people.query('experiment==2').asrs_questionnaire_available.sum(),27)
    def test_all_missing_not_physiological_flat(self):
        s=Stats(1);s.update(np.full((32,1),np.nan));r=s.result(['ECG'])[0]
        self.assertEqual(r['nan_count'],32)
        self.assertTrue(np.isnan(r['mean']))
        self.assertFalse(r['flat'])
    def test_partial_credit_and_exact_match_distinct(self):
        self.assertEqual(options('3  1  2'),{1,2,3})
        self.assertEqual(partial_score({1,2,4},{1,2}),1)
        self.assertNotEqual({1,2,4},{1,2})
    def test_stale_release_rejected(self):
        self.assertEqual(release()['metadata']['version'],'1.1')
        from unittest.mock import patch
        with patch('bbbd_audit.io.json.loads',return_value={'id':19241964,'metadata':{'version':'1.0'}}):
            with self.assertRaises(ValueError):release()
    def test_cached_verification_requires_pinned_release(self):
        import json
        row=json.loads((EVIDENCE/'download_manifest.json').read_text())[0]
        expected=next(x for x in release()['files'] if x['key']==row['filename'])
        self.assertTrue(verified_entry(row,expected,row['local_bytes']))
        self.assertFalse(verified_entry(row|{'version':'1.0'},expected,row['local_bytes']))
        self.assertFalse(verified_entry(row|{'official_checksum':'md5:stale'},expected,row['local_bytes']))
    def test_checksum_failure(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'archive';p.write_bytes(b'correct source')
            f={'size':p.stat().st_size,'checksum':'md5:'+hashlib.md5(p.read_bytes()).hexdigest()}
            self.assertEqual(verify_file(p,f)[0],hashlib.sha256(p.read_bytes()).hexdigest())
            p.write_bytes(b'wrong content')
            with self.assertRaises(ValueError):verify_file(p,f)
    def test_video_identity_unique(self):
        for e in range(1,6):
            d=EVIDENCE/'release_metadata'/f'experiment{e}'/'README.md'
            if not d.exists():continue
            t=video_map(e,d.read_text())
            self.assertFalse(t.local_stimulus_id.duplicated().any())
    def test_canonical_manifest_invariants(self):
        p=EVIDENCE/'canonical_manifest.parquet'
        if not p.exists():return
        t=pd.read_parquet(p)
        self.assertFalse(t.path.dropna().duplicated().any())
        measured=t[t.missing_file_status=='present']
        self.assertTrue((measured.nominal_sampling_rate==128).all())
        self.assertTrue((measured.valid_duration<=measured.observed_duration+1e-6).all())
        self.assertFalse(measured.canonical_video_id.isna().any())
    def test_quiz_quarantine(self):
        p=EVIDENCE/'quiz_video_outcomes.parquet'
        if not p.exists():return
        t=pd.read_parquet(p)
        self.assertFalse(t.duplicated(['experiment','participant_id','local_stimulus_id','question_type']).any())
        self.assertTrue(t.normalized_partial_score.between(0,1).all())
        self.assertFalse(t[t.duplicate_items>0].valid_outcome.any())
        self.assertFalse(t[~t.signals_available|~t.metadata_available].valid_outcome.any())
    def test_intersection_units(self):
        p=EVIDENCE/'modality_intersections.csv'
        if not p.exists():return
        t=pd.read_csv(p)
        self.assertTrue((t.people<=t.person_video_exposures).all())
        self.assertTrue((t.unique_person_video_pairs<=t.person_video_exposures).all())
        self.assertTrue((t.valid_duration_seconds>=0).all())
    def test_missing_signals_preserve_outcome_linkage(self):
        p=EVIDENCE/'exposure_tensor.parquet'
        if not p.exists():return
        t=pd.read_parquet(p)
        self.assertEqual(t.valid_quiz_outcome.sum(),736)
        m=pd.read_parquet(EVIDENCE/'missing_files.parquet')
        self.assertTrue(m.participant_metadata_available.all())
        self.assertTrue(m[m.valid_quiz_outcome].outcome_id.notna().all())
    def test_exclusive_end_event(self):
        # Marker duration is width, not an additional data sample.
        from bbbd_audit.audit import frame
        from bbbd_audit.io import DATA,open_archive
        if not (DATA/'canonical_source/experiment4.zip').exists():return
        fpath=EVIDENCE/'files_exp4.parquet'
        if not fpath.exists():return
        t=pd.read_parquet(fpath);r=t.query("modality=='eeg' and status=='aligned_release_raw'").iloc[0]
        with open_archive(4) as z:
            event_path=r.member_path.replace('_eeg.bdf','_events.tsv')
            events=frame(z,event_path)
        exclusive=round(events[events.event=='end'].onset.iloc[0]*128)
        self.assertEqual(r.qc_sample_count,exclusive)
        self.assertEqual(r.padding_tail_within_one_lsb_rows,r.padding_samples)

if __name__=='__main__':unittest.main()
