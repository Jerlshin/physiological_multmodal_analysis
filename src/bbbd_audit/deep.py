"""QC-directed deep inspection, chosen by declared metrics, not outcomes."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .io import EVIDENCE,open_archive,write_json
from .qc import Stats,bdf_header,bdf_chunks
from .figures import save

def run():
    c=pd.read_parquet(EVIDENCE/'channel_qc.parquet');e=c[c.modality=='eeg']
    selected=[]
    for status in ['aligned_release_raw','author_processed']:
        g=e[e.status==status]
        r=g.loc[g.excess_16hz_db.idxmax()];selected.append((status,r))
    fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained');ledger=[]
    for ax,(status,r) in zip(axs,selected):
        member=r.path.split('::',1)[1]
        with open_archive(int(r.experiment)) as z:
            with z.open(member) as stream:
                h=bdf_header(stream);channel=h['labels'].index(r.channel)
                fs=h['samples_per_record'][channel]/h['record_seconds'];stats=Stats(1,fs)
                for x,_ in bdf_chunks(stream,h):stats.update(x[:,channel:channel+1])
        ax.semilogy(stats.freqs,stats.psd[:,0]/stats.psd_weight,color='#23577a');ax.axvline(16,color='#ad3d32',ls='--')
        ax.set_xlim(0,64);ax.set_xlabel('Frequency (Hz)');ax.set_ylabel('Released voltage PSD (µV²/Hz)')
        ax.set_title(f"E{int(r.experiment)} {r.participant_id}, session {int(r.session)}, stim {int(r.local_stimulus_id)}, {r.channel}\n{status}; excess={r.excess_16hz_db:.1f} dB")
        nearby=(stats.freqs>=47.5)&(stats.freqs<=48.5)
        local=stats.psd[:,0]/stats.psd_weight
        harmonic_hz=float(stats.freqs[nearby][np.argmax(local[nearby])])
        ledger.append(dict(selection='maximum full-QC channel excess at 16 Hz within representation; outcome-independent',experiment=int(r.experiment),path=r.path,channel=r.channel,excess_16hz_db=float(r.excess_16hz_db),targeted_peak_near_48hz=harmonic_hz,note='Deep PSD includes padded BDF tail; lightweight QC map uses exclusive event trim. The approximately 48 Hz peak is targeted evidence only; no dataset-wide harmonic magnitude claim.'))
    fig.suptitle('BBBD v1.1 — EXPLORATORY targeted spectrum inspection');save(fig,'targeted_eeg_spectra')
    write_json(EVIDENCE/'targeted_inspection_ledger.json',ledger)

if __name__=='__main__':run()
