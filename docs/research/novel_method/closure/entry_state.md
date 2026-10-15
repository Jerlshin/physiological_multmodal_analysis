# Closure-phase entry state (2026-10-14T06:01:57Z)

Recorded before any closure output was written. The logs are in [evidence/](evidence/): `entry_time.txt`, `verify_freeze_entry.log`, `unittest_entry.log`, `entry_sha256.txt`, `entry_git_status.txt`, `stage0_sha256_check_entry.log` and `stage1_sha256_check_entry.log`.

## 1. Instruction

The user accepted Stage 1 and asked for **the final outcome-free closure phase before Stage 2**:

- finalize the strongest calibrated confirmatory design and address temporal (fatigue) confounding;
- maximize power without compromising calibration;
- keep E4/E5 heterogeneity interpretable;
- complete and validate the strong modern baselines;
- finish infrastructure, leakage checks, reproducibility controls, manifests and gates;
- prepare the two-annotator G-AN process and the anchor freeze;
- update method and design if outcome-free evidence warrants it.

Hard limits: **no** development, E4, E5, John or external outcome or response data, and **no** Stage 2.

## 2. State at entry

| Check | Result |
|---|---|
| HEAD | `ade5102` (branch `main`). The planning, Stage-0 and Stage-1 work is uncommitted (a user act) |
| `PYTHONPATH=src .venv/bin/python -m g01r verify-freeze` | **VERIFIED** |
| Full test suite | **170 tests, OK** (2 skipped, pre-existing) |
| Stage-0 hash list (`stage0/SHA256SUMS`) | **64/64 OK** |
| Stage-1 hash list (`stage1/SHA256SUMS`) | **221/221 OK** |
| BBBD outcome-access log | 15 lines, SHA-256 `2ea691fa…` |
| John outcome-access log | 1 line, SHA-256 `766489e7…` |
| `analysis_freeze_cairn/` | **absent** (no CAIRN freeze, authorization or access log) |
| Provisional anchors | `69ce6c83…` (machine anchors, not frozen) |

## 3. What this phase may and may not read

The Stage-1 rules ([stage1/entry_state.md §3](../stage1/entry_state.md#3-what-stage-1-may-and-may-not-read)) apply unchanged:

- **Allowed:** per-second signals, availability flags, the item bank, the questionnaire sidecars, timelines and provisional anchors.
- **Never read:** any outcome, response, score or correctness value.

In addition, the closure phase reads:

- **public item texts and public transcripts**, for the text-conditioned baseline's item ↔ transcript relevance. This is outcome-free, and the same material the Stage-0 anchoring raters used;
- **pretrained model weights:** MantisV2, Mantis-8M, TabPFN v2 and all-MiniLM-L6-v2. They contain no BBBD data.
