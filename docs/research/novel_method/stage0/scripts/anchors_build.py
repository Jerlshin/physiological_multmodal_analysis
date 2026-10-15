"""Stage 0b - provisional (machine/LLM-assisted, NOT human) anchor table on the recording clock.

Combines the R2 LLM-assisted provisional annotation with the deterministic R1 lexical
retriever and the Stage-0a timeline. Outputs are labelled provisional; they are never frozen
(gate G-AN needs two independent human annotators; see ANNOTATION_PROTOCOL.md).
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from cairn.anchors import item_bank, items_sha256, provisional_table
from cairn.paths import STAGE0, STAGE0_EVIDENCE, sha256_file

DEV_VIDEOS = {"Mosquitoes", "Related", "Work-energy", "Capacitors", "Planets", "Enzymes", "Lightbulbs", "Internet", "Birth rate"}


def distinct_moments(c: np.ndarray, gap: float = 10.0) -> int:
    c = np.sort(c[np.isfinite(c)])
    return int(1 + np.sum(np.diff(c) > gap)) if len(c) else 0


def main():
    r2 = STAGE0 / "annotation" / "anchors_R2_llm_provisional.csv"
    t = provisional_table(r2)
    t["role"] = np.where(t.video.isin(DEV_VIDEOS), "development", "locked_or_reserved")
    t.to_csv(STAGE0_EVIDENCE / "anchors_provisional.csv", index=False, float_format="%.2f")
    per_video = t.groupby("video").apply(lambda g: pd.Series(dict(
        items=len(g), localized=int(g.localized.sum()), anchorable=int(g.anchorable.sum()),
        timeline_tier_A=int((g.anchorable & (g.timeline_tier == "A")).sum()),
        conf3=int((g.anchorable & (g.r2_confidence == 3)).sum()),
        recognition=int((g.anchorable & (g.category == "R")).sum()), comprehension=int((g.anchorable & (g.category == "C")).sum()),
        distinct_moments=distinct_moments(g[g.anchorable].rec_centre_s.to_numpy(float)),
        span_median_s=float((g[g.anchorable].rec_end_s - g[g.anchorable].rec_start_s).median()),
        centre_first_s=float(g[g.anchorable].rec_centre_s.min()), centre_last_s=float(g[g.anchorable].rec_centre_s.max()),
        role=g.role.iloc[0])), include_groups=False)
    per_video.to_csv(STAGE0_EVIDENCE / "anchors_provisional_by_video.csv")
    loc = t[t.localized]
    summary = dict(
        status="PROVISIONAL - machine/LLM-assisted; not human-annotated; not frozen; gate G-AN not evaluated",
        items=len(t), types=t.r2_type.value_counts().to_dict(), localized=int(t.localized.sum()), anchorable=int(t.anchorable.sum()),
        anchorable_development=int(t[t.role == "development"].anchorable.sum()), items_development=int((t.role == "development").sum()),
        not_anchorable_reasons=dict(
            not_localized=int((~t.localized).sum()),
            timeline_fail_or_not_shown=int((t.localized & (t.timeline_tier.isna() | (t.shown_fraction < 0.99))).sum()),
            key_inconsistent=int((t.localized & t.timeline_tier.notna() & (t.shown_fraction >= 0.99) & (t.r2_key_check == "inconsistent")).sum())),
        key_check=t.r2_key_check.value_counts().to_dict(), visual_check_needed=int((t.r2_visual_check == "yes").sum()),
        machine_agreement_R1_R2_localized=dict(median_centre_diff_s=float(np.median(loc.r1_r2_centre_diff_s)),
                                               median_iou=float(np.median(loc.r1_r2_iou)),
                                               frac_centre_within_10s=float((loc.r1_r2_centre_diff_s <= 10).mean()),
                                               note="R1 (lexical retriever) vs R2 (LLM-assisted): machine-machine; NOT gate G-AN"),
        inputs={"item_bank": items_sha256(), "R2": sha256_file(r2),
                "timeline_table": sha256_file(STAGE0_EVIDENCE / "timeline_table.csv")})
    (STAGE0_EVIDENCE / "anchors_provisional_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print(per_video.to_string())


if __name__ == "__main__":
    sys.exit(main())
