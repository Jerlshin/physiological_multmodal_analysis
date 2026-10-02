"""Response-based scoring and cardinality audits; never row-position joins."""
import json
import re
import hashlib
import numpy as np
import pandas as pd
from .io import EVIDENCE, write_json

def options(value):
    if pd.isna(value): return set()
    return set(map(int,re.findall(r"\d+",str(value))))

def partial_score(selected, correct):
    if not correct: return np.nan
    return len(selected & correct)/len(correct)

def video_map(exp, readme):
    result=[]
    for line in readme.splitlines():
        m=re.search(r"\|\s*Stim-(\d+)\s*\|\s*(.*?)\s*\|.*?youtube.com/embed/([\w-]+)",line)
        if m: result.append(dict(experiment=exp,local_stimulus_id=int(m[1]),canonical_video_id=m[3],title=m[2],identity_evidence="archive README URL; acquired clip hash unavailable"))
    frame=pd.DataFrame(result)
    if frame.empty or frame.local_stimulus_id.duplicated().any(): raise ValueError("Missing/ambiguous stimulus map")
    return frame

def run():
    inv=pd.read_parquet(EVIDENCE/"archive_members.parquet")
    items=[];videos=[];joins=[];maps=[];traits=[];score_checks=[];phenotype_coverage=[]
    for exp in range(1,6):
        root=EVIDENCE/"release_metadata"/f"experiment{exp}"
        mapping=video_map(exp,(root/"README.md").read_text());maps.append(mapping)
        p=pd.read_csv(root/"participants.tsv",sep="\t",dtype={"participant_id":str})
        ids=set(p.participant_id)
        signal_ids=set(inv[inv.archive==f"experiment{exp}.zip"].path.str.extract(r"(?:^|/)(sub-\d+)/")[0].dropna())
        q=pd.read_csv(root/"phenotype/stimuli_questionnaire.tsv",sep="\t")
        q=q.rename(columns={"stimulus_id":"local_stimulus_id","stim_no":"local_stimulus_id","question_number":"question_no","correctanswer":"correct_answer"})
        q["experiment"]=exp;q["qualified_participant_id"]=f"exp-{exp}:"+q.participant_id
        q["question_type"]=q.get("question_type",pd.Series("memory",index=q.index))
        key=["experiment","participant_id","local_stimulus_id","question_type","question_no"]
        q["duplicate_item_key"]=q.duplicated(key,keep=False)
        if exp<=2:
            q["recomputed_score"]=(q.answer==q.correct_answer).astype(float)
            q["recomputed_exact_correct"]=q.recomputed_score.astype(int)
            q["supplied_score"]=q.is_correct
            q["selected_wrong_option_count"]=(q.answer!=q.correct_answer).astype(int)
            q["correct_option_denominator"]=1
        else:
            a=q.answers.map(options);c=q.correct_answers.map(options)
            q["recomputed_score"]=[partial_score(x,y) for x,y in zip(a,c)]
            q["recomputed_exact_correct"]=[int(x==y) for x,y in zip(a,c)]
            q["supplied_score"]=q.score
            q["selected_wrong_option_count"]=[len(x-y) for x,y in zip(a,c)]
            q["correct_option_denominator"]=c.map(len)
            q["option_out_of_range"]=[bool((x|y)-{1,2,3,4}) for x,y in zip(a,c)]
            q["denominator_mismatch"]=q.numberofanswers!=q.correct_option_denominator
        q["score_mismatch"]=~np.isclose(q.recomputed_score,q.supplied_score,atol=1e-8,rtol=0)
        q["correctness_mismatch"]=False if "is_correct" not in q else q.recomputed_exact_correct!=q.is_correct
        q["participant_metadata_available"]=q.participant_id.isin(ids)
        q["signal_participant_available"]=q.participant_id.isin(signal_ids)
        q=q.merge(mapping[["local_stimulus_id","canonical_video_id"]],on="local_stimulus_id",how="left",validate="many_to_one")
        for (pid,stim,qt),g in q.groupby(["participant_id","local_stimulus_id","question_type"]):
            videos.append(dict(experiment=exp,participant_id=pid,qualified_participant_id=f"exp-{exp}:{pid}",local_stimulus_id=int(stim),question_type=qt,canonical_video_id=g.canonical_video_id.iloc[0],item_rows=len(g),unique_items=g.question_no.nunique(),supplied_total=float(g.supplied_score.sum()),recomputed_total=float(g.recomputed_score.sum()),exact_correct_total=int(g.recomputed_exact_correct.sum()),normalized_partial_score=float(g.recomputed_score.mean()),normalized_exact_score=float(g.recomputed_exact_correct.mean()),duplicate_items=int(g.duplicate_item_key.sum()),score_mismatches=int(g.score_mismatch.sum()),correctness_mismatches=int(g.correctness_mismatch.sum()),metadata_available=pid in ids,signals_available=pid in signal_ids,valid_outcome=bool(pid in ids and pid in signal_ids and not g.duplicate_item_key.any() and not g.score_mismatch.any() and not g.correctness_mismatch.any() and g.canonical_video_id.notna().all())))
        for pid in sorted(ids|signal_ids|set(q.participant_id)):
            joins.append(dict(experiment=exp,participant_id=pid,qualified_participant_id=f"exp-{exp}:{pid}",metadata=pid in ids,signals=pid in signal_ids,quiz=pid in set(q.participant_id),quiz_rows=int(sum(q.participant_id==pid)),status="matched_keys_only_identity_not_independently_revalidated" if pid in ids&signal_ids&set(q.participant_id) else "unmatched",reason="" if pid in ids&signal_ids&set(q.participant_id) else "surplus phenotype or missing source; no positional reassignment"))
        score_checks.append(dict(experiment=exp,rows=len(q),quiz_people=q.participant_id.nunique(),duplicate_item_rows=int(q.duplicate_item_key.sum()),score_mismatches=int(q.score_mismatch.sum()),correctness_mismatches=int(q.correctness_mismatch.sum()),score_one_with_wrong_selection=int(((q.recomputed_score==1)&(q.selected_wrong_option_count>0)).sum()),scoring="single-selection equality" if exp<=2 else "selected correct options / all correct options; no wrong-option penalty in supplied score"))
        items.append(q)
        # Retain normalized traits separately; expose heterogeneous offsets.
        p["experiment"]=exp;p["qualified_participant_id"]=f"exp-{exp}:"+p.participant_id
        for name in ["asrs_questionnaire","digit_span_scores","stimuli_feedback_meta"]:
            path=root/"phenotype"/(name+".tsv")
            if not path.exists(): continue
            t=pd.read_csv(path,sep="\t")
            phenotype_coverage.append(dict(experiment=exp,phenotype=name,rows=len(t),people=t.participant_id.nunique(),matched_people=len(set(t.participant_id)&ids&signal_ids),surplus_ids=sorted(set(t.participant_id)-ids),missing_metadata_ids=sorted(ids-set(t.participant_id)),nonmissing={c:int(t[c].notna().sum()) for c in t if c!="participant_id"}))
            if name=="asrs_questionnaire":
                qs=[f"q{i}" for i in range(1,19)]
                t["asrs_item_invalid_count"]=((t[qs]<0)|(t[qs]>4)|t[qs].isna()).sum(axis=1)
                t["recomputed_likert_screener"]=t[qs[:6]].sum(axis=1)
                t["recomputed_likert_full"]=t[qs].sum(axis=1)
                ia=[1,2,3,4,7,8,9,10,11,12];hy=[5,6,13,14,15,16,17,18]
                t["recomputed_inattention_0_4"]=t[[f"q{i}" for i in ia]].sum(axis=1)
                t["recomputed_hyperactivity_0_4"]=t[[f"q{i}" for i in hy]].sum(axis=1)
                t["inattention_offset"]=t.inattention_subscore-t.recomputed_inattention_0_4
                t["hyperactivity_offset"]=t.hyperactivity_subscore-t.recomputed_hyperactivity_0_4
                t["likert_full_mismatch"]=t.likert_full_score!=t.recomputed_likert_full
                t=t.rename(columns={c:"asrs_"+c for c in t if c!="participant_id"})
                p=p.merge(t,on="participant_id",how="left",validate="one_to_one")
            elif name=="digit_span_scores":
                t=t.rename(columns={"score":"digit_span","weighted_score":"digit_span_weighted"})
                p=p.merge(t,on="participant_id",how="left",validate="one_to_one")
        traits.append(p)
    pd.concat(maps).to_csv(EVIDENCE/"stimulus_map.csv",index=False)
    pd.concat(items).to_parquet(EVIDENCE/"quiz_items.parquet",index=False,compression="zstd")
    v=pd.DataFrame(videos)
    srows=[]
    for exp in range(1,6):
        s=pd.read_csv(EVIDENCE/"release_metadata"/f"experiment{exp}/phenotype/stimuli_questionnaire_scores.tsv",sep="\t")
        s=s.rename(columns={"stimulus_id":"local_stimulus_id","stim_no":"local_stimulus_id","stimulus_no":"local_stimulus_id"})
        m=v[v.experiment==exp].query("question_type=='memory'").merge(s,on=["participant_id","local_stimulus_id"],how="outer",validate="one_to_one",indicator=True)
        total_col="memory_score" if exp<=2 else "score" if exp==3 else "total_score"
        m["aggregate_absolute_error"]=(m.recomputed_total-m[total_col]).abs()
        m["aggregate_total_mismatch"]=~np.isclose(m.recomputed_total,m[total_col],atol=1e-8,rtol=0)
        m["aggregate_exceeds_rounding_tolerance"]=m.aggregate_absolute_error>5.1e-5
        if exp>=4:m["aggregate_exact_mismatch"]=m.exact_correct_total!=m.total_correct
        srows.append(m)
    pd.concat(srows).to_parquet(EVIDENCE/"quiz_aggregate_comparison.parquet",index=False,compression="zstd")
    v.to_parquet(EVIDENCE/"quiz_video_outcomes.parquet",index=False,compression="zstd")
    pd.DataFrame(joins).to_csv(EVIDENCE/"participant_quiz_join_ledger.csv",index=False)
    t=pd.concat(traits)
    for col in ["Tired","Study_time","Caffeine","GPA"]: t[col]=t[col].astype("string")
    t["GPA_numeric"]=pd.to_numeric(t.GPA,errors="coerce")
    t.to_parquet(EVIDENCE/"participant_traits.parquet",index=False,compression="zstd")
    write_json(EVIDENCE/"quiz_audit.json",score_checks)
    write_json(EVIDENCE/"phenotype_coverage.json",phenotype_coverage)
    print("Quiz audit complete:",score_checks,flush=True)

if __name__=="__main__":run()
