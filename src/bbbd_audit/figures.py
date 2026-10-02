"""Exportable scientific audit figures; all analyses exploratory."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from .io import EVIDENCE

def save(fig,name):
    out=EVIDENCE.parent/'figures';out.mkdir(exist_ok=True)
    fig.savefig(out/(name+'.png'),dpi=180,bbox_inches='tight')
    fig.savefig(out/(name+'.svg'),bbox_inches='tight');plt.close(fig)

def run():
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    ex=pd.read_parquet(EVIDENCE/'exposure_tensor.parquet')
    f=pd.read_parquet(EVIDENCE/'canonical_manifest.parquet');f=f[f.missing_file_status=='present']
    c=pd.read_parquet(EVIDENCE/'channel_qc.parquet')
    mods=['eeg','ecg','eye','respiration','head']
    a=ex.groupby('experiment')[[m+'_present' for m in mods]].mean()
    b=ex.groupby('experiment')[[m+'_basic_qc' for m in mods]].mean()
    fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for ax,t,title in zip(axs,[a,b],['Released modality availability','Passes provisional basic QC']):
        im=ax.imshow(t.to_numpy(),vmin=0,vmax=1,cmap='Blues',aspect='auto')
        ax.set_xticks(range(len(mods)),[m.upper() if m in ['eeg','ecg'] else m for m in mods]);ax.set_yticks(range(len(t)),[f'E{i}' for i in t.index]);ax.set_title(title)
        for y in range(len(t)):
            for x in range(len(mods)):ax.text(x,y,f'{100*t.iloc[y,x]:.0f}%',ha='center',va='center',color='white' if t.iloc[y,x]>.6 else 'black')
    fig.colorbar(im,ax=axs,label='Fraction of design-expected exposures',shrink=.8)
    fig.suptitle('BBBD v1.1 — EXPLORATORY coverage audit');save(fig,'modality_coverage')
    eye=f[(f.status=='author_processed')&f.modality.isin(['gaze','pupil'])]
    fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for ax,mod in zip(axs,['gaze','pupil']):
        gs=list(eye[eye.modality==mod].groupby('experiment'));ax.boxplot([g.correction_fraction.dropna() for _,g in gs],tick_labels=[f'E{e}\nn={len(g)}' for e,g in gs],showfliers=False)
        ax.axhline(.5,color='#9c3030',ls='--',lw=1);ax.set_ylim(0,1);ax.set_ylabel('Corrected fraction on released grid');ax.set_title(mod.capitalize()+' correction masks')
    fig.suptitle('BBBD v1.1 — EXPLORATORY eye quality (files, not independent people)');save(fig,'eye_correction')
    eeg=c[c.modality=='eeg']
    fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for ax,status in zip(axs,['aligned_release_raw','author_processed']):
        gs=list(eeg[eeg.status==status].groupby('experiment'));ax.boxplot([g.excess_16hz_db for _,g in gs],tick_labels=[f'E{e}' for e,_ in gs],showfliers=False)
        maxima=[g.excess_16hz_db.max() for _,g in gs]
        ax.scatter(range(1,len(gs)+1),maxima,marker='^',color='#9c3030',s=35,label='Maximum channel-record')
        ax.legend(fontsize=8,loc='upper left')
        ax.axhline(10,color='#9c3030',ls='--',lw=1);ax.set_ylabel('16 Hz excess versus neighboring PSD (dB)');ax.set_title(status.replace('_',' '))
    fig.suptitle('BBBD v1.1 — EXPLORATORY channel spectra; 10 dB flags do not reject data');save(fig,'eeg_16hz')
    q=pd.read_parquet(EVIDENCE/'quiz_video_outcomes.parquet').query("question_type=='memory' and valid_outcome")
    fig,ax=plt.subplots(figsize=(9,4),layout='constrained')
    gs=list(q.groupby('experiment'));ax.boxplot([g.normalized_partial_score for _,g in gs],tick_labels=[f'E{e}\nn={len(g)}' for e,g in gs],showfliers=True)
    ax.set_ylabel('Recomputed video partial score / item count');ax.set_ylim(-.04,1.04);ax.set_title('BBBD v1.1 — EXPLORATORY quiz distributions (person–video observations)');save(fig,'quiz_distributions')
    peaks=pd.read_parquet(EVIDENCE/'peak_qc.parquet');p=peaks[peaks.event_type=='rpeak']
    person=p.groupby(['experiment','participant_id'])[['rms_rr_seconds','true_rmssd_seconds']].mean().reset_index()
    fig,ax=plt.subplots(figsize=(7,4),layout='constrained')
    for e,g in person.groupby('experiment'):ax.scatter(g.rms_rr_seconds,g.true_rmssd_seconds,s=18,alpha=.6,label=f'E{e}')
    ax.set_xlabel('Notebook formula: RMS RR (seconds)');ax.set_ylabel('Successive-interval RMSSD (seconds)');ax.legend(ncol=2);ax.set_title('BBBD v1.1 — EXPLORATORY statistic-definition audit\nOne point per experiment-qualified participant');save(fig,'hrv_semantics')
    # A compact participant × exposure contamination map, preserving condition.
    s=eeg[eeg.status=='author_processed'].groupby(['experiment','participant_id','session','local_stimulus_id']).excess_16hz_db.apply(lambda x:float((x>10).mean())).reset_index(name='fraction_flagged')
    s['person']=s.apply(lambda r:f"E{r.experiment}:{r.participant_id}",axis=1);s['exposure']=s.apply(lambda r:f"s{r.session}/v{r.local_stimulus_id}",axis=1)
    pivot=s.pivot(index='person',columns='exposure',values='fraction_flagged')
    colors=matplotlib.colormaps['magma'].copy();colors.set_bad('#d9d9d9')
    fig,ax=plt.subplots(figsize=(9,10),layout='constrained');im=ax.imshow(pivot.to_numpy(),vmin=0,vmax=1,cmap=colors,aspect='auto')
    positions=[];labels=[]
    for experiment in ['E2','E3','E4','E5']:
        ix=np.flatnonzero(pivot.index.str.startswith(experiment+':'));positions.append(float(np.mean(ix)));labels.append(experiment)
        if ix[0]>0:ax.axhline(ix[0]-.5,color='#777777',lw=.8)
    flagged=s[s.fraction_flagged>0].person.unique()
    for person_id in flagged:
        positions.append(pivot.index.get_loc(person_id));labels.append(person_id)
    ax.set_xticks(range(len(pivot.columns)),pivot.columns,rotation=45,ha='right');ax.set_ylabel('Experiment-qualified participants (all recorded rows)');ax.set_yticks(positions,labels,fontsize=8)
    ax.legend(handles=[Patch(facecolor='#d9d9d9',label='Missing / design absent')],loc='upper right',fontsize=8)
    fig.colorbar(im,ax=ax,label='Fraction of channels >10 dB at 16 Hz',shrink=.65);ax.set_title('BBBD v1.1 — EXPLORATORY contamination map\nExact person × session × video × channel evidence retained in Parquet');save(fig,'eeg_contamination_map')

if __name__=='__main__':run()
