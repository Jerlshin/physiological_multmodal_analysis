# Evidence — novel-method planning phase (outcome-free)

2026-10-08. Everything in this folder was computed **without reading any quiz outcome, item response or score**. The inputs are:

- the frozen analysis-set manifest: keys and set flags only;
- the outcome-free exposure feature table: EEG channel labels only;
- the G01-R 128 Hz signal cache. Gaze is stored in pixels, NaN outside the frozen valid mask. Pupil is z-scored within the recording. EEG is per-channel centred, with its valid mask.

No BBBD or John outcome-access log changed. The files contain aggregate variance components per experiment × video unit, with no participant-level values.

| File | Content |
|---|---|
| `temporal_structure_audit.py` | Gaze/pupil windowed decomposition (person / window / person × window) |
| `temporal_structure_w{5,10,20,30}.csv`, `*_summary.json`, `temporal_units_w*.csv` | Outputs for 5, 10, 20 and 30 s windows |
| `eeg_temporal_audit.py` | Windowed EEG (relative posterior alpha; filter-free EEG ISC proxy) and its coupling with gaze |
| `eeg_temporal_w10.csv`, `eeg_temporal_w10_summary.json` | Outputs for 10 s windows |
| `SHA256SUMS` | Hashes of the files above |

Reproduce from the repository root:

```sh
cd docs/research/novel_method/evidence
../../../../.venv/bin/python temporal_structure_audit.py --window 10   # also 5, 20, 30
../../../../.venv/bin/python eeg_temporal_audit.py --window 10
```

## What was asked

Do the whole-video summaries used in G01-R and in the John replication discard temporal structure that a time-resolved model could use? Each learner × video recording was cut into windows. Each windowed feature matrix F[p, w] was split additively into three parts:

- a **person level** a_p: what a whole-video feature keeps;
- a **window level** b_w: what all viewers share at that moment, i.e. stimulus-locked structure;
- a **person × window residual** e_pw: time-localized, idiosyncratic deviations. Whole-video averaging discards these.

## Results (variance shares; weighted over units)

**Gaze ISC** (Pearson r with the leave-one-out peer mean; x and y averaged):

| Set | Window | Person | Window (stimulus-locked) | Person × window | x/y residual agreement | Residual lag-1 autocorrelation |
|---|---|---|---|---|---|---|
| PAS-core (68 / 259 / 8) | 5 s | 0.05 | 0.41 | 0.54 | 0.18 | +0.04 |
| PAS-core | 10 s | 0.10 | 0.44 | 0.46 | 0.21 | +0.02 |
| PAS-core | 20 s | 0.19 | 0.40 | 0.41 | 0.24 | +0.03 |
| PAS-core | 30 s | 0.28 | 0.33 | 0.39 | 0.28 | −0.04 |
| E1-gaze (26 / 121 / 5) | 10 s | 0.22 | 0.37 | 0.40 | 0.22 | +0.07 |
| E5-core (46 / 128 / 3) | 10 s | 0.07 | 0.36 | 0.57 | 0.20 | +0.01 |

**Gaze validity** (fraction of valid, on-screen samples), PAS-core at 10 s:

- person 0.48;
- window 0.04;
- person × window 0.49, with residual lag-1 autocorrelation **+0.26**. E5 is +0.40 and E1 +0.23.

**Pupil ISC** (PAS-core, 10 s): person 0.07, window 0.24, residual 0.69.

**Coupling of residuals** (median over units, 10 s):

| Pair | PAS-core |
|---|---|
| Validity × gaze ISC | 0.05 |
| Dispersion × gaze ISC | 0.07 |

**EEG** (PAS-core, 10 s; [eeg_temporal_w10_summary.json](eeg_temporal_w10_summary.json)):

| Feature | Person | Window | Person × window |
|---|---|---|---|
| Relative posterior alpha | 0.64 | 0.25 | 0.10 |
| Filter-free EEG ISC proxy (mean over 64 channels) | 0.06 | 0.17 | 0.77 |

Coupling of EEG residuals with gaze residuals is small: EEG ISC × gaze ISC 0.06; EEG ISC × gaze validity 0.07; alpha × gaze validity −0.06. E5 is similar, with alpha × validity −0.19.

## Reading (interpretation, labelled as such)

1. **Whole-video features keep a small part of ocular engagement variance.** At 10 s the learner level is about 10% of windowed gaze-ISC variance in PAS-core and 22% in E1. The rest is either:
   - shared, stimulus-locked structure (about 40%), which a model can only use if it knows *what content* each moment carries; or
   - person × moment deviations (about 45–55%).
2. **A modest part of the person × moment component is reliable.**
   - The x- and y-axis residuals agree at r ≈ 0.18–0.28. The Spearman–Brown reliability of their average is about 0.31–0.44.
   - So about 16% of total windowed ISC variance is reliable, time-localized and idiosyncratic, at every window length from 5 to 30 s. For windows up to 20 s that exceeds the person-level share whole-video features keep (5–19%). At 30 s it is smaller (28%).
   - Shared measurement artifacts (head movement, drift) could also produce x/y agreement. This is an upper bound on attention-related reliability, not a measurement of it.
3. **Idiosyncratic ISC deviations are short-lived; data-loss episodes persist.**
   - ISC residuals have no autocorrelation beyond one window.
   - Validity residuals persist over 10–20 s (+0.17 to +0.40), consistent with looking-away or track-loss episodes.
   - The two are nearly uncorrelated (0.05). They are distinct channels, not one "attention" variable.
4. **EEG, on these simple proxies, shows little reliable time-localized structure.**
   - Alpha is mostly a stable learner trait.
   - The filter-free ISC proxy is mostly residual noise.
   - A CorrCA-filtered windowed EEG ISC was not computed here. It is a declared Stage-0 check ([research plan §7.4](../research_plan.md#74-modality-decisions-from-evidence)).

**What this does not show.** Nothing here relates any of this structure to learning. Whether time-localized engagement predicts *which* items a learner gets wrong is the new hypothesis (NH1), to be tested under the protocol in the [research plan](../research_plan.md).
