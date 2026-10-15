"""Outcome-free parsing of the EyeLink EDF files into compact per-person archives.

Uses the SR Research EDF Access API bundled with ``eyelinkio`` (run in ``.venv-ext``), but keeps
the **original EDF millisecond clock**: ``eyelinkio.read_edf`` re-times samples onto an index
grid, which would silently compress any recording gap. Events (blinks, saccades) and messages
keep their EDF timestamps too, so the video window is located on one clock.
"""
from __future__ import annotations

import importlib
import json
import re
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

from .paths import EDF_DIR, EVIDENCE, PARSED, VIDEO

MISSING = 1e8 - 1          # EyeLink MISSING_DATA sentinel (values at or above it are missing)


def participant_id(path) -> str:
    return re.match(r"LeVi_(.+)\.EDF$", path.name, re.I).group(1)


def read_raw(fname) -> dict:
    """Samples, events and messages of one EDF on the original EDF clock (ms)."""
    R = importlib.import_module("eyelinkio.edf.read_edf")
    from eyelinkio.edf._defines import event_constants

    done = event_constants.get("NO_PENDING_ITEMS")
    n_samps = {k: 0 for k in R._ets2pp.values()}
    with R._edf_open(str(fname)) as edf:
        et = None
        while et != done:
            et = R.edf_get_next_data(edf)
            if event_constants[et] in R._ets2pp:
                n_samps[R._ets2pp[event_constants[et]]] += 1
    with R._edf_open(str(fname)) as edf:
        info = R._parse_preamble(edf)
        res = dict(info=info, samples=None, n_samps=n_samps, offsets={k: 0 for k in n_samps},
                   edf_fields=dict(messages=["stime", "msg"]), discrete={}, eye_idx=None)
        res["discrete"]["messages"] = np.empty(n_samps["messages"], dtype=[("stime", np.float64), ("msg", "|S260")])
        et = None
        while et != done:
            et = R.edf_get_next_data(edf)
            R._element_handlers[event_constants[et]](edf, res)
        R._element_handlers["VERSION"](res)
    s = np.asarray(res["samples"], float)
    fields = info["sample_fields"][1:]
    data = s[1:].copy()
    data[data >= MISSING] = np.nan
    out = dict(info=info, time_ms=s[0], **{f: data[i] for i, f in enumerate(fields)})
    for key in ("blinks", "saccades"):
        d = res["discrete"].get(key)
        out[key] = np.column_stack([d["stime"], d["etime"]]) if d is not None and len(d) else np.zeros((0, 2))
    out["messages"] = [(float(m["stime"]), m["msg"].decode("ascii", "replace").strip()) for m in res["discrete"]["messages"]]
    return out


def _message_time(messages, text):
    times = [t for t, m in messages if m == text]
    return (times[0], len(times)) if times else (np.nan, 0)


def parse_one(path) -> dict:
    """Parse one EDF and store its archive; returns the outcome-free parse summary row."""
    pid = participant_id(path)
    raw = read_raw(path)
    msgs = raw["messages"]
    disp = [m for _, m in msgs if m.startswith("DISPLAY_COORDS")]
    coords = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", disp[0])] if disp else [np.nan] * 4
    t_rec, n_rec = _message_time(msgs, f"start_recording_{VIDEO}")
    t_on, n_on = _message_time(msgs, f"start_video_{VIDEO}")
    t_off, n_off = _message_time(msgs, f"stop_video_{VIDEO}")
    t_end, _ = _message_time(msgs, f"stop_recording_{VIDEO}")
    t = raw["time_ms"]
    dt = np.diff(t)
    PARSED.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(PARSED / f"{pid}.npz", time_ms=t, xpos=raw.get("xpos"), ypos=raw.get("ypos"),
                        ps=raw.get("ps"), blinks=raw["blinks"], saccades=raw["saccades"],
                        display=np.array(coords, float), video=np.array([t_on, t_off], float))
    return dict(participant=pid, file=path.name, sfreq=raw["info"].get("sfreq"), eye=raw["info"].get("eye"),
                sample_fields=",".join(raw["info"].get("sample_fields", [])), n_samples=len(t),
                first_ms=t[0], last_ms=t[-1], n_gaps=int((dt != dt.min()).sum()) if len(dt) else 0,
                max_gap_ms=float(dt.max()) if len(dt) else np.nan, display_coords=" ".join(f"{c:g}" for c in coords),
                start_recording_ms=t_rec, start_video_ms=t_on, stop_video_ms=t_off, stop_recording_ms=t_end,
                n_start_video_msgs=n_on, n_stop_video_msgs=n_off, n_start_recording_msgs=n_rec,
                onset_minus_recording_ms=t_on - t_rec, video_window_s=(t_off - t_on) / 1000.0,
                n_blinks=len(raw["blinks"]), n_saccades=len(raw["saccades"]), n_messages=len(msgs),
                recording_date=str(raw["info"].get("meas_date")))


def parse_all(workers: int = 4) -> pd.DataFrame:
    paths = sorted(EDF_DIR.glob("*.EDF"))
    with ProcessPoolExecutor(workers) as ex:
        rows = list(ex.map(parse_one, paths))
    table = pd.DataFrame(rows).sort_values("participant").reset_index(drop=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    table.to_csv(EVIDENCE / "edf_parse_summary.csv", index=False)
    (EVIDENCE / "edf_parse_meta.json").write_text(json.dumps(dict(
        reader="eyelinkio 0.3.0 with bundled SR Research EDF Access API; original EDF clock kept",
        files=len(paths)), indent=1) + "\n")
    return table
