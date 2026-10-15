"""Build the human annotation package (ANNOTATION_PROTOCOL.md §1) - outcome-free.

Writes, per video, an item sheet (question, options, keyed options, category) and the timed
transcripts of its public source(s) to data/stimuli/annotation_package/ (git-ignored: transcripts
are not redistributed). Machine proposals (R1, R2) are deliberately NOT included. A manifest
with file hashes is written to the repository so the package can be verified.
"""
from __future__ import annotations

import json
import sys

import pandas as pd

from cairn.anchors import item_bank, load_transcript
from cairn.paths import SOURCES, STAGE0, STIMULI, VIDEOS, sha256_file

OUT = STIMULI / "annotation_package"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bank = item_bank()
    manifest = {}
    for order, (vid, name) in enumerate(VIDEOS.items(), start=1):
        b = bank[bank.canonical_video_id == vid].sort_values("item")
        sheet = pd.DataFrame(dict(video=name, item=b.item, category=b.category, question=b.question,
                                  option_1=[o[0] for o in b.options], option_2=[o[1] for o in b.options],
                                  option_3=[o[2] for o in b.options], option_4=[o[3] for o in b.options],
                                  keyed_options=[", ".join(f"option_{i + 1}" for i in range(k)) for k in b.k_keyed],
                                  graph_supplied=b.has_graph))
        f_items = OUT / f"{order:02d}_{name.replace(' ', '_')}_items.csv"
        sheet.to_csv(f_items, index=False)
        tr = load_transcript(vid)
        tr = tr[["source", "src_start_s", "src_end_s", "shown", "text"]].rename(columns={"src_start_s": "start_s", "src_end_s": "end_s"})
        tr["shown"] = tr.shown.map({True: "", False: "NOT SHOWN"})
        f_tr = OUT / f"{order:02d}_{name.replace(' ', '_')}_transcript.csv"
        tr.sort_values(["source", "start_s"]).to_csv(f_tr, index=False)
        manifest[name] = dict(sources=[f"https://www.youtube.com/watch?v={s}" for s in SOURCES[vid]],
                              items_sha256=sha256_file(f_items), transcript_sha256=sha256_file(f_tr), n_items=len(sheet))
    (STAGE0 / "annotation" / "package_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps({k: v["n_items"] for k, v in manifest.items()}))


if __name__ == "__main__":
    sys.exit(main())
