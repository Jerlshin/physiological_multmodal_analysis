# Stage-0 evidence (outcome-free)

Every file here was produced **without reading any quiz outcome, item response or score**. The files hold:

- stimulus-level timing;
- item-level anchor proposals (item texts and spans only);
- aggregate signal statistics (per experiment × video unit, per fold, or overall).

Participant-level intermediate tables are kept git-ignored in `data/derived/cairn/`. File hashes are in `SHA256SUMS`.

| Files | Content | Produced by |
|---|---|---|
| `entry_sha256.txt`, `verify_freeze_entry.log`, `unittest_entry.log`, `incidents.log` | Entry state | Commands in [../entry_state.md](../entry_state.md) |
| `exit_checks.log` | Exit state: freeze, tests, access logs, frozen-path diff | Commands in [../README.md](../README.md#exit-checks) |
| `timeline_map_1hz.csv`, `timeline_segments.csv`, `timeline_audit_summary.json` | Candidate alignments and agreement | `scripts/timeline_audit.py` |
| `timeline_cut_locked_validation.csv` | Cut-locked saccade validator | `scripts/cut_locked_validation.py` |
| `timeline_pupil_luminance_validation.csv` | Pupillary light-response validator | `scripts/pupil_luminance_validation.py` |
| `timeline_table.csv`, `timeline_seconds.csv`, `timeline_gate_summary.json` | **Machine-readable timeline**, per-second G-TL status, verdicts | `scripts/timeline_gate.py` |
| `anchors_provisional.csv`, `anchors_provisional_by_video.csv`, `anchors_provisional_summary.json` | Provisional (machine / LLM-assisted) anchors on the recording clock | `scripts/anchors_build.py` |
| `signal/A_*`, `signal/B_*`, `signal/signal_feasibility_summary.json` | Variance structure, anchored moment terms, missingness, construct, identity, pupil | `scripts/signal_feasibility.py` |
| `signal/F_*`, `signal/G_*` | EEG CorrCA windowed ISC; HR | `scripts/eeg_hr_feasibility.py` |
| `signal/J_encoder_summary.json` | Label-free encoder validation | `scripts/encoder_stage0.py` |
| `literature_sources.json` | Provenance hashes of the literature sources read (copies git-ignored) | Stage 0d |

## Reproduce

From the repository root, using the frozen `.venv` (numpy/scipy/pandas only):

```sh
# 0. public media and captions (git-ignored); a current yt-dlp is needed for media
yt-dlp --skip-download --write-info-json --write-subs --write-auto-subs --sub-langs "en,en-US,en-GB,en-orig" --sub-format json3 -o "data/stimuli/youtube/%(id)s/%(id)s.%(ext)s" <12 URLs>
yt-dlp -f "18/134+140/133+140" --merge-output-format mp4 -o "data/stimuli/youtube/%(id)s/%(id)s.%(ext)s" <12 URLs>
# 1. 10 Hz series from the verified archives
PYTHONPATH=src .venv/bin/python -m cairn.extract --workers 5
# 2. Stage 0a
PYTHONPATH=src .venv/bin/python docs/research/novel_method/stage0/scripts/timeline_audit.py
PYTHONPATH=src .venv/bin/python docs/research/novel_method/stage0/scripts/cut_locked_validation.py
PYTHONPATH=src .venv/bin/python docs/research/novel_method/stage0/scripts/pupil_luminance_validation.py
PYTHONPATH=src .venv/bin/python docs/research/novel_method/stage0/scripts/timeline_gate.py
# 3. Stage 0b
PYTHONPATH=src .venv/bin/python -c "from cairn.transcripts import transcript; from cairn.paths import VIDEOS, SOURCES; [transcript(v, SOURCES[v]).to_csv(f'data/stimuli/transcripts/{v}.csv', index=False) for v in VIDEOS]"
PYTHONPATH=src .venv/bin/python docs/research/novel_method/stage0/scripts/anchors_build.py
PYTHONPATH=src .venv/bin/python docs/research/novel_method/stage0/scripts/make_annotation_package.py
# 4. Stage 0c
PYTHONPATH=src .venv/bin/python docs/research/novel_method/stage0/scripts/channels_build.py
PYTHONPATH=src .venv/bin/python docs/research/novel_method/stage0/scripts/signal_feasibility.py
PYTHONPATH=src .venv/bin/python docs/research/novel_method/stage0/scripts/eeg_hr_feasibility.py   # needs the G01-R EEG/HR cache
PYTHONPATH=src .venv/bin/python docs/research/novel_method/stage0/scripts/encoder_stage0.py
```

**Determinism.** `signal_feasibility.py` and `encoder_stage0.py` were re-run and reproduced their outputs bit-identically. Video sources may change on YouTube; the downloaded files' metadata (durations, upload dates) is recorded in [../timeline_audit.md](../timeline_audit.md) §2.
