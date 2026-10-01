# CASE

**Disposition: older reference for continuous affect annotation; not selected as primary.**

Sources: [Sharma et al., Scientific Data 2019](https://doi.org/10.1038/s41597-019-0209-0); [official Figshare](https://springernature.figshare.com/articles/dataset/CASE_Dataset-full/8869157).

| Item | Evidence / limitation |
|---|---|
| Cohort | 30 adults, 15 men/15 women, ages 22–37; male mean 28.6 ± 4.8, female 25.7 ± 3.1. |
| Protocol/duration/IDs | Eight affective videos, two per amusement/boredom/relaxation/fear category; trained simultaneous 2-D joystick ratings. About 40 min/person (~20 h nominal), pseudorandom order and blue-screen intervals. Subject/trial identifiers, one visit. |
| Signals/rates | ECG, BVP, EDA/GSR, respiration, temperature and three EMG sites, 1000 Hz; valence/arousal annotation 20 Hz. EMG sensor output processing must be checked before treating it as unfiltered muscle potential. No EEG/eye tracking. |
| Raw/sync/standards | Raw and interpolated files, common acquisition-PC timestamps. Different annotation and physiology rates handled explicitly; residual lag not externally certified. CSV/MAT-style organization, not BIDS. |
| Labels/artifacts | Dense self-reported affect is unusually valuable, but joystick movement, reporting delay, cognitive interference and video identity affect signals. Clean-looking traces do not eliminate movement/physiological noise; complete missingness audit NV. |
| Access/license/size/code | Public Figshare, CC0 metadata, approximately 4.24 GB listed. Detailed protocol and MATLAB processing documentation/code. |

Supports time-varying self-reported affect, annotation-lag analysis and peripheral fusion. Cannot establish objective emotions or brain–body mechanisms without EEG; continuous annotations are not independent of the act of rating.

At least descriptor plus downstream affect comparisons were identified; a comprehensive count was not attempted. Continuous valence/arousal prediction and feature fusion are established uses. A useful secondary benchmark for robustness/label-lag work, but its 30 people and older, familiar protocol are weaker foundations than recent larger cohorts. Subject and video holdouts, temporal separation and lag estimation inside training folds are needed. Cross-modal learning among peripheral signals is feasible; educational/clinical transfer remains unproven.

