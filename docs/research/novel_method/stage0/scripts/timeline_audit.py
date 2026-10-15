"""Stage 0a - stimulus timeline recovery and gate G-TL (outcome-free).

For every canonical video, the BBBD recording clock is aligned to its public YouTube source(s)
with the peer gaze of all released viewings (cairn.timeline). Decision rule, fixed before any
anchor was built (stage0/timeline_audit.md §3):

1. Three signal configurations are fitted: ``temporal`` (hard cuts vs peer saccade rate),
   ``spatial`` (location of visual change vs peer-median gaze) and ``combined`` (their mean).
2. For each, a monotone alignment path (removals only; sources in a fixed order; edit penalty
   0.5 correlation units) is fitted to the pooled score matrix and, independently, to every
   viewing group: each experiment (disjoint learners), each session, and two random halves of
   the learners.
3. A configuration is *admissible* if its pooled path is physically plausible: video time
   >= -1 s at the recording start and inside every source.
4. A recording second is *defended* by a configuration if its pooled mapping (same source,
   |offset difference| <= 2 s) is reproduced by >= 2 independent experiments - or, for videos
   shown in one experiment only, by both learner halves and both sessions.
5. The final mapping is the admissible configuration defending the most seconds. A second
   passes G-TL if it is defended by the final configuration and not contradicted by another
   admissible configuration that defends a different mapping there (> 2 s apart).
6. Video verdict: PASS if >= 90 % of seconds pass and the duration accounting closes;
   PARTIAL if 50-90 % pass (only items whose evidence lies in passing seconds may be used);
   FAIL otherwise.

Inputs: data/stimuli (public videos; git-ignored), data/derived/cairn/series10 (10 Hz
ocular series). No quiz outcome, item response or score is read.

Usage (repo root): PYTHONPATH=src python docs/research/novel_method/stage0/scripts/timeline_audit.py
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

import cairn.timeline as tl
from cairn.paths import BIN_HZ, DERIVED, SOURCES, STAGE0_EVIDENCE, VIDEOS

WIN_S, STEP_S, JUMP, DRIFT = 30.0, 5.0, 0.5, 1
TOL_S = 2.0
SEED = 20261013
CONFIGS = {"combined": ("sacc", "spatial"), "spatial": ("spatial",), "temporal": ("sacc",)}


def scores(peer, vids, use):
    n = len(peer)
    starts = np.arange(0, max(1, n - int(WIN_S * BIN_HZ)) + 1, int(STEP_S * BIN_HZ))
    states, blocks = [], []
    for src, vid in vids.items():
        lags = np.arange(-n, len(vid) + 1)
        S = np.vstack([tl.score_curve(peer, vid, k0, k0 + int(WIN_S * BIN_HZ), lags, 0, use)[0] for k0 in starts])
        states += [(src, int(L)) for L in lags]
        blocks.append(S)
    return starts, states, np.hstack(blocks)


def best_path(S, states, sources):
    orders = [sources] if len(sources) == 1 else [sources, sources[::-1]]
    fits = [(*tl.monotone_viterbi(S, states, list(o), JUMP, DRIFT), list(o)) for o in orders]
    return max(fits, key=lambda f: f[1])


def per_second(starts, states, path, n_bins):
    centres = (starts + WIN_S * BIN_HZ / 2) / BIN_HZ
    secs = np.arange(int(n_bins / BIN_HZ))
    nearest = np.abs(secs[:, None] + 0.5 - centres[None, :]).argmin(1)
    return pd.DataFrame(dict(rec_s=secs, source=[states[path[i]][0] for i in nearest],
                             offset_s=np.array([states[path[i]][1] / BIN_HZ for i in nearest])))


def agree(a, b):
    n = min(len(a), len(b))
    return (a.source.to_numpy()[:n] == b.source.to_numpy()[:n]) & (np.abs(a.offset_s.to_numpy()[:n] - b.offset_s.to_numpy()[:n]) <= TOL_S)


def segments(mp):
    out, cur = [], None
    for r in mp.itertuples():
        if cur and r.source == cur["source"] and abs(r.offset_s - cur["o"][-1]) <= 0.35:
            cur["end"] = r.rec_s + 1
            cur["o"].append(r.offset_s)
        else:
            if cur:
                out.append(cur)
            cur = dict(start=r.rec_s, end=r.rec_s + 1, source=r.source, o=[r.offset_s])
    out.append(cur)
    return [dict(rec_start_s=int(s["start"]), rec_end_s=int(s["end"]), source=s["source"],
                 offset_s=round(float(np.median(s["o"])), 2), offset_min_s=float(min(s["o"])), offset_max_s=float(max(s["o"])),
                 video_start_s=round(float(s["start"] + s["o"][0]), 2), video_end_s=round(float(s["end"] + s["o"][-1]), 2))
            for s in out]


def plausible(mp, vids):
    first = mp.iloc[0]
    if first.offset_s < -1.0:
        return False
    vt = mp.rec_s + mp.offset_s
    lens = mp.source.map({s: len(v) / BIN_HZ for s, v in vids.items()})
    return bool(((vt >= -1.0) & (vt <= lens + 1.0)).all())


def main():
    m = pd.read_parquet(DERIVED / "series10_manifest.parquet")
    m = m[m.status == "ok"]
    rng = np.random.default_rng(SEED)
    STAGE0_EVIDENCE.mkdir(parents=True, exist_ok=True)
    maps, seg_rows, summary = [], [], {}
    for vid, name in VIDEOS.items():
        vids = {s: tl.video_features(s) for s in SOURCES[vid]}
        mv = m[m.canonical_video_id == vid]
        n_bins = int(mv.n_bins.min())
        people = np.array(sorted(mv.qualified_participant_id.dropna().unique()))
        rng.shuffle(people)
        halves = {f"half_{h}": set(hp) for h, hp in enumerate((people[: len(people) // 2], people[len(people) // 2:]))}
        groups = {f"E{e}s{s}": list(g.uid) for (e, s), g in mv.groupby(["experiment", "session"]) if len(g) >= 8}
        exps = sorted({g[:2] for g in groups})
        single = len(exps) == 1

        def peer(uids):
            return tl.peer_courses(mv, uids).iloc[:n_bins].reset_index(drop=True)

        per_cfg = {}
        for cname, use in CONFIGS.items():
            Sg = {}
            for g, u in groups.items():
                starts, states, Sg[g] = scores(peer(u), vids, use)
            wt = {g: np.sqrt(len(u)) for g, u in groups.items()}
            pooled = sum(Sg[g] * wt[g] for g in Sg) / sum(wt.values())
            path, total, order = best_path(pooled, states, SOURCES[vid])
            ref = per_second(starts, states, path, n_bins)
            indep = {}
            for e in exps:
                ge = [g for g in groups if g.startswith(e)]
                Se = sum(Sg[g] * wt[g] for g in ge) / sum(wt[g] for g in ge)
                indep[f"exp_{e}"] = per_second(starts, states, best_path(Se, states, SOURCES[vid])[0], n_bins)
            for g in groups:
                indep[f"grp_{g}"] = per_second(starts, states, best_path(Sg[g], states, SOURCES[vid])[0], n_bins)
            for h, hp in halves.items():
                _, _, Sh = scores(peer(list(mv[mv.qualified_participant_id.isin(hp)].uid)), vids, use)
                indep[h] = per_second(starts, states, best_path(Sh, states, SOURCES[vid])[0], n_bins)
            A = {k: agree(ref, v) for k, v in indep.items()}
            if single:
                defended = A["half_0"] & A["half_1"] & np.all([A[k] for k in A if k.startswith("grp_")], axis=0)
            else:
                defended = np.sum([A[k] for k in A if k.startswith("exp_")], axis=0) >= 2
            per_cfg[cname] = dict(ref=ref, defended=defended, admissible=plausible(ref, vids), order=order,
                                  agree={k: float(v.mean()) for k, v in A.items()}, indep=indep)
        adm = [c for c in CONFIGS if per_cfg[c]["admissible"]]
        if adm:
            final = max(adm, key=lambda c: (per_cfg[c]["defended"].sum(), c == "combined"))
            ref = per_cfg[final]["ref"].copy()
            ok = per_cfg[final]["defended"].copy()
            for c in adm:
                if c == final:
                    continue
                conflict = per_cfg[c]["defended"] & ~agree(ref, per_cfg[c]["ref"])
                ok &= ~conflict
        else:
            final, ref, ok = None, per_cfg["combined"]["ref"].copy(), np.zeros(len(per_cfg["combined"]["ref"]), bool)
        frac = float(ok.mean())
        segs = segments(ref)
        kept = sum(s["rec_end_s"] - s["rec_start_s"] for s in segs)
        src_len = sum(len(v) / BIN_HZ for v in vids.values())
        verdict = "PASS" if frac >= 0.90 else ("PARTIAL" if frac >= 0.50 else "FAIL")
        ref.insert(0, "canonical_video_id", vid)
        ref.insert(1, "video", name)
        ref["video_s"] = ref.rec_s + ref.offset_s
        ref["gtl_pass"] = ok
        for c in CONFIGS:
            ref[f"defended_{c}"] = per_cfg[c]["defended"]
            ref[f"offset_{c}"] = per_cfg[c]["ref"].offset_s.to_numpy()
            ref[f"source_{c}"] = per_cfg[c]["ref"].source.to_numpy()
        ref["final_config"] = final
        maps.append(ref)
        for s in segs:
            s.update(canonical_video_id=vid, video=name, config=final)
        seg_rows += segs
        summary[name] = dict(
            canonical_video_id=vid, sources=SOURCES[vid], recording_s=n_bins / BIN_HZ,
            source_s={s: len(v) / BIN_HZ for s, v in vids.items()},
            groups={g: len(u) for g, u in groups.items()}, experiments=exps, single_experiment=single,
            final_config=final, admissible=adm, verdict=verdict, frac_seconds_pass=round(frac, 3),
            segments=[(s["rec_start_s"], s["rec_end_s"], s["source"], s["offset_s"]) for s in segs],
            removed_s=round(src_len - kept, 1),
            per_config={c: dict(admissible=per_cfg[c]["admissible"], frac_defended=round(float(per_cfg[c]["defended"].mean()), 3),
                                agreement={k: round(v, 3) for k, v in per_cfg[c]["agree"].items()},
                                segments=[(s["rec_start_s"], s["rec_end_s"], s["source"], s["offset_s"]) for s in segments(per_cfg[c]["ref"])])
                        for c in CONFIGS})
        print(name, verdict, final, round(frac, 3), summary[name]["segments"], flush=True)
    pd.concat(maps).to_csv(STAGE0_EVIDENCE / "timeline_map_1hz.csv", index=False, float_format="%.3f")
    pd.DataFrame(seg_rows).to_csv(STAGE0_EVIDENCE / "timeline_segments.csv", index=False)
    (STAGE0_EVIDENCE / "timeline_audit_summary.json").write_text(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    sys.exit(main())
