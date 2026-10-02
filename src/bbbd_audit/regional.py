"""Dataset-wide flat-run checks for physiological TSV channels."""
import numpy as np
import pandas as pd
from .io import EVIDENCE,open_archive
from .audit import tsv_chunks
from .qc import longest_true

def run():
    f=pd.read_parquet(EVIDENCE/'canonical_manifest.parquet')
    f=f[(f.missing_file_status=='present')&(f.status=='aligned_release_raw')&f.modality.isin(['ecg','eog','respiration','head'])]
    rows=[]
    for exp,g in f.groupby('experiment'):
        with open_archive(int(exp)) as z:
            for _,r in g.iterrows():
                last=None;longest=None;tail=None
                for x in tsv_chunks(z,r.member_path):
                    if longest is None:longest=np.ones(x.shape[1],int);tail=np.ones(x.shape[1],int)
                    for c in range(x.shape[1]):
                        same=np.isfinite(x[1:,c])&(x[1:,c]==x[:-1,c])
                        lead=int(np.argmax(~same)) if (~same).any() else len(same)
                        continuation=(tail[c]+lead+1) if last is not None and np.isfinite(x[0,c]) and x[0,c]==last[c] else lead+1
                        longest[c]=max(longest[c],longest_true(same)+1,continuation)
                        if (~same).any():tail[c]=int(np.argmax(~same[::-1]))+1
                        elif last is not None and x[0,c]==last[c]:tail[c]+=len(x)
                        else:tail[c]=len(x)
                    last=x[-1]
                if longest is not None:
                    for ch,n in enumerate(longest):rows.append(dict(experiment=int(exp),participant_id=r.participant_id,session=int(r.session),local_stimulus_id=int(r.local_stimulus_id),modality=r.modality,path=r.path,channel_index=ch+1,longest_exact_constant_seconds=float(n/128),flat_run_gt_one_second=bool(n>128),definition='exact equality of finite exported samples; native ADC saturation thresholds unavailable'))
        print('Regional flat-run QC completed',exp,flush=True)
    pd.DataFrame(rows).to_parquet(EVIDENCE/'physiology_flat_runs.parquet',index=False,compression='zstd')

if __name__=='__main__':run()
