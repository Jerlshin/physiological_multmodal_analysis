# G01-R confirmatory H1/H2 baseline (first real-outcome run)

Tracking experiment `g01r-confirmatory`; 1 registry analyses collated.

Outcome source(s): real:authorized:0bd14a35f56734bb6c151f46c9fff9d23a532abac37348bccb6acd2bcacf3067

## H1

| people | cells | videos | skill | p_perm | B | ncv90_lo | ncv90_hi | futility_U3 | decision |
|---|---|---|---|---|---|---|---|---|---|
| 68 | 259 | 8 | 0.0206 | 0.0820 | 999 | -0.0332 | 0.0723 | 0.0786 | bounded_negative |

## H2

| test | base | full | p | p_holm | reject_holm | observed_skill_R10 |
|---|---|---|---|---|---|---|
| H2a | M3 | M5 | 0.0050 | 0.0200 | True | 0.0449 |
| H2b | M2 | M_EEG | 0.2280 | 0.4560 | False | -0.0023 |
| H2c | M2 | M_ECG | 0.8110 | 0.8110 | False | -0.0149 |
| H2d | M2 | M_GAZE | 0.0090 | 0.0270 | True | 0.0310 |

## models

| comparison | skill_person_balanced | skill_cell_weighted | delta_rmse_items | state_skill |
|---|---|---|---|---|
| M5_vs_M2 | 0.0206 | 0.0128 | 0.0221 | -0.0098 |
| M3_vs_M2 | -0.0276 | -0.0319 | -0.0293 | -0.0042 |
| M4_vs_M2 | 0.0386 | 0.0330 | 0.0417 | -0.0072 |
| M5_vs_M3 | 0.0469 | 0.0433 | 0.0514 | -0.0055 |
| M_EEG_vs_M2 | -0.0044 | -0.0040 | -0.0046 | -0.0074 |
| M_ECG_vs_M2 | -0.0105 | -0.0125 | -0.0112 | -0.0080 |
| M_GAZE_vs_M2 | 0.0307 | 0.0227 | 0.0330 | 0.0031 |
| M1_vs_M0 | 0.0355 | 0.0452 | 0.0401 | -0.0000 |
| M2_vs_M1 | 0.0517 | 0.0561 | 0.0574 | -0.0012 |
| SHORTCUT_i_M0Q_vs_M0 | 0.0694 | 0.0831 | 0.0789 | 0.0119 |
| SHORTCUT_iii_NOISE_vs_M2 | -0.0209 | -0.0250 | -0.0222 | -0.0237 |

## per_video

| unit | skill | people |
|---|---|---|
| 3:30o4omX5qfo | -0.0226 | 27 |
| 3:bYgV9nvgJ3E | 0.0037 | 25 |
| 3:e0NT9i4Qnak | -0.0245 | 26 |
| 3:lkRZKqDdwzU | 0.0087 | 24 |
| 3:mnYSMhR3jCI | 0.0180 | 24 |
| 3:rkntp3_cZl4 | -0.0006 | 22 |
| 4:VVAKFJ8VVp4 | 0.0261 | 38 |
| 4:mnYSMhR3jCI | 0.0599 | 37 |
| 4:zQGOcOUBi6s | -0.0155 | 36 |

## per_experiment

| experiment | skill | skill_over_reliable_share | reliable_share | people | cells |
|---|---|---|---|---|---|
| 3 | 0.0131 | 0.0277 | 0.4725 | 29 | 148 |
| 4 | 0.0257 | 0.0445 | 0.5774 | 39 | 111 |

## derived

| estimate | point | ncv90_lo | ncv90_hi |
|---|---|---|---|
| H3.7 cell-weighted | 0.0128 | -0.0455 | 0.0684 |
| state skill (exploratory) | -0.0098 | -0.0563 | 0.0348 |

## Runs

- `H1_H2`: run `20261005T104908Z_c57b28d6`, config `f34f1b03b657`, frozen=True, git `d02e477d62`
