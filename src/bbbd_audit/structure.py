"""EXPLORATORY summary relationships, selection diagnostics and leakage ledger."""
import json
import numpy as np
import pandas as pd
from .io import EVIDENCE, write_json

def run():
    ex=pd.read_parquet(EVIDENCE/'exposure_tensor.parquet')
    f=pd.read_parquet(EVIDENCE/'canonical_manifest.parquet')
    f=f[f.missing_file_status=='present']
    c=pd.read_parquet(EVIDENCE/'channel_qc.parquet')
    p=pd.read_parquet(EVIDENCE/'peak_qc.parquet')
    q=pd.read_parquet(EVIDENCE/'quiz_video_outcomes.parquet').query("question_type=='memory' and valid_outcome")
    keys=['experiment','participant_id','session','local_stimulus_id']
    feat=ex.copy()
    eeg=c[(c.modality=='eeg')&(c.status=='author_processed')]
    eg=eeg.groupby(keys).agg(eeg_alpha_median=('power_alpha','median'),eeg_beta_median=('power_beta','median'),eeg_std_median=('std','median'),eeg_16hz_db_median=('excess_16hz_db','median')).reset_index()
    feat=feat.merge(eg,on=keys,how='left',validate='one_to_one')
    if not p.empty:
        cardiac=p[p.event_type=='rpeak'][keys+['median_hr_bpm','true_rmssd_seconds','rms_rr_seconds','rr_outside_30_200_fraction']]
        feat=feat.merge(cardiac,on=keys,how='left',validate='one_to_one')
    for mod in ['gaze','pupil']:
        eye=f[(f.modality==mod)&(f.status=='author_processed')][keys+['correction_fraction','longest_correction_gap_seconds']]
        eye=eye.rename(columns={x:mod+'_'+x for x in ['correction_fraction','longest_correction_gap_seconds']})
        feat=feat.merge(eye,on=keys,how='left',validate='one_to_one')
    for mod in ['pupil','respiration','head']:
        s=c[(c.modality==mod)&(c.status==('aligned_release_raw' if mod=='respiration' else 'author_processed'))]
        if s.empty:continue
        agg=s.groupby(keys).agg(**{mod+'_std_median':('std','median'),mod+'_mean_median':('mean','median'),mod+'_dominant_low_hz':('low_frequency_dominant_hz','median')}).reset_index()
        feat=feat.merge(agg,on=keys,how='left',validate='one_to_one')
    feat=feat.merge(q[['experiment','participant_id','local_stimulus_id','normalized_partial_score','normalized_exact_score']],on=['experiment','participant_id','local_stimulus_id'],how='left',validate='many_to_one')
    # Keep only directly linked final outcomes in outcome diagnostics.
    feat.loc[~feat.valid_quiz_outcome,['normalized_partial_score','normalized_exact_score']]=np.nan
    feat.to_parquet(EVIDENCE/'exploratory_exposure_summaries.parquet',index=False,compression='zstd')
    variables=['eeg_alpha_median','eeg_beta_median','eeg_std_median','eeg_16hz_db_median','median_hr_bpm','true_rmssd_seconds','gaze_correction_fraction','pupil_correction_fraction','pupil_std_median','respiration_std_median']
    correlations=[]
    for exp,g in feat.groupby('experiment'):
        # Collapse repeated videos within participant for person-level quality relationships.
        person=g.groupby('qualified_participant_id')[variables].mean(numeric_only=True)
        for ai,a in enumerate(variables):
            for b in variables[ai+1:]:
                s=person[[a,b]].dropna()
                if len(s)>=5 and s[a].nunique()>1 and s[b].nunique()>1:
                    correlations.append(dict(experiment=exp,level='participant mean across observed exposures',variable_a=a,variable_b=b,people=len(s),spearman_rho=float(s[a].corr(s[b],method='spearman')),status='EXPLORATORY; no significance testing, no outcome-driven feature selection'))
    pd.DataFrame(correlations).to_csv(EVIDENCE/'exploratory_quality_correlations.csv',index=False)
    effects=[]
    for exp,g in feat.groupby('experiment'):
        for variable in variables:
            for grouping in ['qualified_participant_id','canonical_video_id','condition']:
                s=g[[grouping,variable]].dropna()
                if len(s)<2:continue
                total=float(s[variable].var(ddof=0))
                means=s.groupby(grouping)[variable].mean();sizes=s.groupby(grouping).size()
                between=float(np.average((means-s[variable].mean())**2,weights=sizes))
                effects.append(dict(experiment=exp,variable=variable,grouping=grouping,observations=len(s),groups=len(means),total_variance=total,weighted_between_group_variance=between,fraction_between=between/total if total>0 else None,status='EXPLORATORY descriptive marginal variance, not adjusted causal effect or random-effects estimate'))
    pd.DataFrame(effects).to_csv(EVIDENCE/'exploratory_group_structure.csv',index=False)
    # Missingness by traits; no imputation or clinical interpretation.
    traits=pd.read_parquet(EVIDENCE/'participant_traits.parquet')
    availability=ex.groupby(['experiment','participant_id','qualified_participant_id']).agg(eye_pass_fraction=('eye_basic_qc','mean'),eeg_pass_fraction=('eeg_basic_qc','mean'),ecg_pass_fraction=('ecg_basic_qc','mean')).reset_index()
    t=availability.merge(traits,on=['experiment','participant_id','qualified_participant_id'],validate='one_to_one')
    traits_to_check=['Age','GPA_numeric','digit_span','asrs_recomputed_inattention_0_4','asrs_recomputed_hyperactivity_0_4']
    relations=[]
    for exp,g in t.groupby('experiment'):
        for quality in ['eye_pass_fraction','eeg_pass_fraction','ecg_pass_fraction']:
            for trait in traits_to_check:
                s=g[[quality,trait]].dropna()
                if len(s)>=5 and s[quality].nunique()>1 and s[trait].nunique()>1:
                    relations.append(dict(experiment=exp,quality=quality,trait=trait,people=len(s),spearman_rho=float(s[quality].corr(s[trait],method='spearman')),status='EXPLORATORY selection diagnostic only; GPA coding unresolved'))
    pd.DataFrame(relations).to_csv(EVIDENCE/'missingness_trait_diagnostics.csv',index=False)
    # Direct quiz outcomes versus availability: one score per person/video, no repeat duplication.
    direct=feat[feat.valid_quiz_outcome]
    direct.groupby(['experiment','eye_basic_qc']).agg(people=('qualified_participant_id','nunique'),person_video_observations=('normalized_partial_score','count'),mean_partial_score=('normalized_partial_score','mean'),mean_exact_score=('normalized_exact_score','mean')).reset_index().to_csv(EVIDENCE/'outcome_selection_diagnostics.csv',index=False)
    risk=[
      ('participant_overlap','experiment-qualified ID; cross-experiment same-human identity unknown','Group all exposures from a verified person together; obtain privacy-preserving cross-cohort identity statement'),
      ('canonical_video_overlap','11 canonical URLs; local stimulus IDs reused','Hold out canonical identities across every experiment; acquired trims/hashes unavailable'),
      ('repeated_exposure','sessions 1/2 repeat in 1–3 and 5; 4 uses different videos','Group both exposures for a person/video; name exposure-history estimand'),
      ('experiment_overlap','4/5 partition a shared upstream collection; protocol-specific outcomes','Experiment holdout also needs person and shared-video audit'),
      ('adjacent_windows','within-video autocorrelation and noncausal processing','Split independent groups before windowing; buffer filter/interpolation contexts'),
      ('global_preprocessing','author RPCA/interpolation fit scope and options not release-traced','Do not assume train-only preprocessing; disclose acquisition preprocessing and fit future learned transforms on training groups only'),
      ('isc_corrca_pca_reference','cohort-derived references and components','Declare inductive versus transductive reference availability; training-only references/components unless explicitly justified'),
      ('imputation_scaling','traits have missingness/offsets; future transforms could use all records','Fit imputation/scaling and feature selection inside training folds; use item-derived ASRS coding'),
      ('outcome_window_duplication','one quiz outcome replicated across many possible windows','Score uncertainty at person/video level; windows do not increase independent outcome N'),
      ('quality_shortcuts','eye masks, EEG 16 Hz, design missingness vary by experiment','Use nuisance controls and selection analyses; separate natural failure from synthetic ablations'),
      ('post_exposure_information','5 final quiz follows preview/review/incentive','Do not claim first-exposure learning forecast without specifying the intervening learning opportunity'),
      ('audit_adaptivity','full-release descriptive outcomes examined for integrity and feasibility','All outputs here exploratory; reserve a later locked protocol/untouched evaluation or external data for confirmatory claims')]
    write_json(EVIDENCE/'leakage_risk_register.json',[dict(channel=a,observed_basis=b,future_control=d,evidence_category='OUR INFERENCE grounded in audited manifest / retained documentation') for a,b,d in risk])
    graph=[]
    for vid,g in ex.groupby('canonical_video_id'):
        graph.append(dict(canonical_video_id=vid,experiments=sorted(g.experiment.unique().tolist()),qualified_participants=g.qualified_participant_id.nunique(),exposures=len(g),quiz_observations=int(g.valid_quiz_outcome.sum())))
    write_json(EVIDENCE/'independence_graph.json',dict(video_nodes=graph,person_nodes=ex.qualified_participant_id.nunique(),person_identity_limit='experiment-qualified cohort records; unique humans across experiments not independently certified',session_limit='viewing blocks, not longitudinal days',no_split_frozen=True))

if __name__=='__main__':run()
