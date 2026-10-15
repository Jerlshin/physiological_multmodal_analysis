"""Stage 0c - per-second channels for every in-scope exposure (outcome-free).

Scope (decisions in Stage 0 use development and label-free data only): every released
exposure except the tested exposures of the locked cohorts (E4 session 2, E5 session 2).
Reference for each exposure: the attentive viewings of the same video in scope by *other*
learners (leave-learner-out; regime-A-like). One common reference definition lets attentive
and distracted viewings be compared on the same scale (construct check).

Output: data/derived/cairn/channels_1hz.parquet (uid x second x channel); git-ignored.
"""
from __future__ import annotations

import sys
import time

import numpy as np
import pandas as pd

from cairn.channels import ALL_CHANNELS, channels, reference_stats
from cairn.paths import BIN_HZ, DERIVED

ATTENTIVE = {"intentional_attend", "incidental_attend", "attend_untested_content", "incidental_first"}


def scope(m: pd.DataFrame) -> pd.DataFrame:
    locked_tested = ((m.experiment == 4) & (m.session == 2)) | ((m.experiment == 5) & (m.session == 2))
    return m[(m.status == "ok") & ~locked_tested].copy()


def main():
    m = scope(pd.read_parquet(DERIVED / "series10_manifest.parquet"))
    people = dict(zip(m.uid, m.qualified_participant_id))
    t0, out = time.time(), []
    for vid, mv in m.groupby("canonical_video_id"):
        n_s = int(mv.n_bins.min()) // BIN_HZ
        pool = mv[mv.condition.isin(ATTENTIVE)]
        for r in mv.itertuples():
            ref_uids = list(pool[pool.qualified_participant_id != r.qualified_participant_id].uid)
            ref = reference_stats(ref_uids, people, n_s, exclude_person=r.qualified_participant_id)
            c = channels(r.uid, ref, n_s)
            c.insert(0, "uid", r.uid)
            c["n_ref"] = len(ref_uids)
            out.append(c)
        print(vid, len(mv), "exposures", n_s, "s", round(time.time() - t0, 1), flush=True)
    df = pd.concat(out, ignore_index=True)
    df[list(ALL_CHANNELS)] = df[list(ALL_CHANNELS)].astype("float32")
    df.to_parquet(DERIVED / "channels_1hz.parquet", index=False)
    m.to_parquet(DERIVED / "channels_scope.parquet", index=False)
    print(df.shape, round(time.time() - t0, 1))


if __name__ == "__main__":
    sys.exit(main())
