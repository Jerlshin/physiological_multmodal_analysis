"""Stage 0a - final per-second gate G-TL, edit-point refinement and the machine-readable timeline.

Reads the alignment audit (timeline_map_1hz.csv, timeline_audit_summary.json) and the
independent validators, then assigns each recording second a status:

* PASS-A  replicated (final mapping reproduced by >= 2 independent experiments, or - one
          experiment only - by both learner halves and both sessions), no conflict with another
          admissible configuration, and validated in its 60 s block by an independent signal:
          pupillary light response p < 0.05, or (unless the final configuration is the
          cut-based one, which would be circular) cut-locked saccade response p < 0.05;
* PASS-B  replicated and conflict-free, and no validator supports *any* candidate mapping in that
          block (validators uninformative, e.g. constant luminance, no cuts);
* FAIL    otherwise (not replicated, in conflict, or a validator supports another candidate
          while the final mapping is unsupported).

Video verdict: PASS if >= 90 % of seconds pass, PARTIAL if 50-90 %, FAIL below 50 %.
Edit points (segment boundaries) are re-localized at 1 s resolution with 10 s windows by a
change-point search between the two adjacent mappings, with a 200-draw viewer bootstrap.

Outputs: timeline_table.csv (segments, offsets, edit-point CIs, uncertainty, status shares),
timeline_seconds.csv (per second: video time, status), timeline_gate_summary.json.
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

import cairn.timeline as tl
from cairn.paths import BIN_HZ, DERIVED, SOURCES, STAGE0_EVIDENCE, VIDEOS

sys.path.insert(0, str(STAGE0_EVIDENCE.parent / "scripts"))
from cut_locked_validation import frame_cuts, map_to_recording, response  # noqa: E402

SEED = 2026
ALPHA = 0.05
ALPHA_CONTRADICT = 0.01   # v2: an admissible alternative contradicts only with p < 0.01 and stronger support
BLOCK_S = 60
LATENCY_S = 0.25          # gaze response latency absorbed in the spatial/temporal offsets (Stars, Light bulbs, Birth rate)


def block_of(sec: int, n_s: int) -> str:
    a = (sec // BLOCK_S) * BLOCK_S
    return f"{a}-{min(a + BLOCK_S, n_s)}s"


def cut_block_p(sacc, cuts, mapping, lo, hi, rng, n_bins):
    t = map_to_recording(cuts, mapping)
    t = t[(t >= lo) & (t < hi)]
    if len(t) < 3:
        return np.nan, np.nan
    obs = response(sacc, t)
    null = np.array([response(sacc, np.sort(rng.uniform(max(2, lo), min(hi, n_bins / BIN_HZ - 2), len(t)))) for _ in range(500)])
    return obs, float((np.sum(null >= obs) + 1) / (np.sum(np.isfinite(null)) + 1))


def refine_edit(peer_fn, uids, vids, a, b, rng, search_s=20, win_s=10):
    """Change point between mapping a=(source, offset) and b on [boundary-search, boundary+search]."""
    def local(u):
        p = peer_fn(u)
        sc = {}
        for key, (src, off) in (("a", a[:2]), ("b", b[:2])):
            lags = np.array([int(round(off * BIN_HZ))])
            r = []
            for t in range(a[2] - search_s, a[2] + search_s + 1):
                k0 = int((t - win_s / 2) * BIN_HZ)
                if k0 < 0 or k0 + win_s * BIN_HZ > len(p):
                    r.append(np.nan)
                    continue
                r.append(tl.score_curve(p, vids[src], k0, k0 + int(win_s * BIN_HZ), lags)[0][0])
            sc[key] = np.nan_to_num(np.array(r), nan=0.0)
        cs = [sc["a"][:i].sum() + sc["b"][i:].sum() for i in range(len(sc["a"]) + 1)]
        return a[2] - search_s + int(np.argmax(cs))

    est = local(uids)
    boots = [local(list(rng.choice(uids, len(uids), replace=True))) for _ in range(200)]
    return est, float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def main():
    rng = np.random.default_rng(SEED)
    m = pd.read_parquet(DERIVED / "series10_manifest.parquet")
    m = m[m.status == "ok"]
    mp = pd.read_csv(STAGE0_EVIDENCE / "timeline_map_1hz.csv")
    summ = json.loads((STAGE0_EVIDENCE / "timeline_audit_summary.json").read_text())
    pl = pd.read_csv(STAGE0_EVIDENCE / "timeline_pupil_luminance_validation.csv")
    seconds, table, verdicts = [], [], {}
    for vid, name in VIDEOS.items():
        s = summ[name]
        d = mp[mp.video == name].reset_index(drop=True)
        n_s = len(d)
        mv = m[m.canonical_video_id == vid]
        n_bins = int(mv.n_bins.min())
        vids = {src: tl.video_features(src) for src in SOURCES[vid]}
        final = s["final_config"]
        adm = s["admissible"]
        # replication and conflicts (from the audit)
        replicated = d[f"defended_{final}"].to_numpy(bool) if final else np.zeros(n_s, bool)
        conflict = np.zeros(n_s, bool)
        for c in adm:
            if c != final:
                diff = (d[f"source_{c}"] != d["source"]) | (np.abs(d[f"offset_{c}"] - d["offset_s"]) > 2.0)
                conflict |= d[f"defended_{c}"].to_numpy(bool) & diff.to_numpy()
        # validators per 60 s block
        sacc = tl.peer_courses(mv, list(mv.uid)).sacc.to_numpy()[:n_bins]
        cuts = {src: frame_cuts(src) for src in SOURCES[vid]}
        cands = {"final": d[["rec_s", "source", "offset_s"]]}
        for c in ("combined", "spatial", "temporal"):
            cands[c] = d[["rec_s", f"source_{c}", f"offset_{c}"]].rename(columns={f"source_{c}": "source", f"offset_{c}": "offset_s"})
        blocks = sorted({block_of(t, n_s) for t in range(n_s)}, key=lambda b: int(b.split("-")[0]))
        val = {}
        for b in blocks:
            lo, hi = (int(x) for x in b[:-1].split("-"))
            plb = pl[(pl.video == name) & (pl.region == b)]
            lum_p = {r.mapping: r.p_null for r in plb.itertuples()}
            lum_r = {r.mapping: r.r for r in plb.itertuples()}
            cut = {c: cut_block_p(sacc, cuts, mpg, lo, hi, rng, n_bins) for c, mpg in cands.items()}
            cut_r = {c: v[0] for c, v in cut.items()}
            cut_p = {c: v[1] for c, v in cut.items()}
            final_ok = (lum_p.get("final", np.nan) < ALPHA) or (final != "temporal" and cut_p["final"] < ALPHA)

            def differs(c):
                return not (np.allclose(cands[c].offset_s.to_numpy()[lo:hi], d.offset_s.to_numpy()[lo:hi], atol=2.0)
                            and (cands[c].source.to_numpy()[lo:hi] == d.source.to_numpy()[lo:hi]).all())
            # v1 (as first run): any differing configuration validated at p < 0.05 counts against the final
            alt_v1 = any((lum_p.get(c, np.nan) < ALPHA or (c != "temporal" and cut_p[c] < ALPHA))
                         for c in ("combined", "spatial", "temporal") if differs(c))
            # v2 (primary): only admissible alternatives; p < 0.01 and stronger than the final mapping
            def stronger(c):
                lum = lum_p.get(c, np.nan) < ALPHA_CONTRADICT and lum_r.get(c, -np.inf) > np.nan_to_num(lum_r.get("final", -np.inf), nan=-np.inf)
                cutc = (c != "temporal" and cut_p[c] < ALPHA_CONTRADICT
                        and cut_r[c] > np.nan_to_num(cut_r["final"], nan=-np.inf))
                return lum or cutc
            alt_v2 = any(stronger(c) for c in adm if c != final and differs(c))
            any_valid_v1 = final_ok or alt_v1
            val[b] = dict(final_validated=bool(final_ok), alternative_validated_v1=bool(alt_v1), informative_v1=bool(any_valid_v1),
                          contradicted_v2=bool(alt_v2), lum_r_final=lum_r.get("final"), lum_p_final=lum_p.get("final"),
                          cut_r_final=cut_r["final"], cut_p_final=cut_p["final"])
        # edit-point refinement
        segs = s["segments"]
        edits = []
        def peer_fn(u):
            return tl.peer_courses(mv, u).iloc[:n_bins].reset_index(drop=True)
        for (a0, a1, asrc, aoff), (b0, b1, bsrc, boff) in zip(segs[:-1], segs[1:]):
            est, lo95, hi95 = refine_edit(peer_fn, list(mv.uid), vids, (asrc, aoff, a1), (bsrc, boff, b0), rng)
            edits.append(dict(window_boundary_s=a1, refined_s=est, ci95=(lo95, hi95)))
        in_edit_ci = np.zeros(n_s, bool)
        for e in edits:
            in_edit_ci[int(np.floor(e["ci95"][0])): int(np.ceil(e["ci95"][1])) + 1] = True
        status, status_v1 = [], []
        for t in range(n_s):
            v = val[block_of(t, n_s)]
            base_fail = not replicated[t] or conflict[t]
            # v1
            if base_fail:
                status_v1.append("FAIL")
            elif v["final_validated"]:
                status_v1.append("PASS-A")
            elif not v["informative_v1"]:
                status_v1.append("PASS-B")
            else:
                status_v1.append("FAIL")
            # v2 (primary)
            if base_fail or v["contradicted_v2"] or in_edit_ci[t]:
                status.append("FAIL")
            elif v["final_validated"]:
                status.append("PASS-A")
            else:
                status.append("PASS-B")
        d["status"] = status
        d["status_v1"] = status_v1
        frac = float(np.isin(status, ["PASS-A", "PASS-B"]).mean())
        frac_v1 = float(np.isin(status_v1, ["PASS-A", "PASS-B"]).mean())
        verdict = "PASS" if frac >= 0.9 else ("PARTIAL" if frac >= 0.5 else "FAIL")
        verdict_v1 = "PASS" if frac_v1 >= 0.9 else ("PARTIAL" if frac_v1 >= 0.5 else "FAIL")
        # per-second output (latency-corrected video time)
        d["video_s"] = d.rec_s + d.offset_s + LATENCY_S
        d["edit_ci_width_s"] = 0.0
        for e in edits:
            near = (d.rec_s >= e["ci95"][0] - 1) & (d.rec_s <= e["ci95"][1] + 1)
            d.loc[near, "edit_ci_width_s"] = e["ci95"][1] - e["ci95"][0]
        seconds.append(d[["canonical_video_id", "video", "rec_s", "source", "offset_s", "video_s", "status", "status_v1", "edit_ci_width_s"]])
        # segment table with refined boundaries
        bounds = [0] + [e["refined_s"] for e in edits] + [n_s]
        for i, (a0, a1, src, off) in enumerate(segs):
            r0, r1 = bounds[i], bounds[i + 1]
            st = np.array(status[r0:r1])
            grp_off = [d[f"offset_{c}"].to_numpy()[r0:r1] for c in ("combined", "spatial", "temporal") if c in adm]
            spread = float(np.nanmax(np.abs(np.vstack(grp_off) - off))) if grp_off else np.nan
            table.append(dict(canonical_video_id=vid, video=name, segment=i + 1, source=src,
                              rec_start_s=r0, rec_end_s=r1, offset_s=off, latency_corrected_offset_s=round(off + LATENCY_S, 2),
                              video_start_s=round(r0 + off + LATENCY_S, 2), video_end_s=round(r1 + off + LATENCY_S, 2),
                              start_edit_ci95=None if i == 0 else edits[i - 1]["ci95"],
                              end_edit_ci95=None if i == len(segs) - 1 else edits[i]["ci95"],
                              admissible_config_spread_s=spread, final_config=final,
                              frac_pass_A=float((st == "PASS-A").mean()), frac_pass_B=float((st == "PASS-B").mean()),
                              frac_fail=float((st == "FAIL").mean())))
        verdicts[name] = dict(canonical_video_id=vid, verdict=verdict, frac_pass=round(frac, 3),
                              verdict_v1=verdict_v1, frac_pass_v1=round(frac_v1, 3),
                              frac_pass_A=round(float(np.mean(np.array(status) == "PASS-A")), 3),
                              frac_pass_B=round(float(np.mean(np.array(status) == "PASS-B")), 3),
                              final_config=final, single_experiment=s["single_experiment"], experiments=s["experiments"],
                              n_segments=len(segs), edits=edits, blocks=val, removed_s=s["removed_s"])
        print(name, verdict, round(frac, 3), "(v1", verdict_v1, round(frac_v1, 3), ") A", verdicts[name]["frac_pass_A"], "B", verdicts[name]["frac_pass_B"], "edits", edits, flush=True)
    pd.concat(seconds).to_csv(STAGE0_EVIDENCE / "timeline_seconds.csv", index=False, float_format="%.2f")
    pd.DataFrame(table).to_csv(STAGE0_EVIDENCE / "timeline_table.csv", index=False)
    (STAGE0_EVIDENCE / "timeline_gate_summary.json").write_text(json.dumps(verdicts, indent=2, default=str))


if __name__ == "__main__":
    sys.exit(main())
