# G01-R baseline study results

Tracking experiment `g01r-confirmatory`; 15 registry analyses collated.

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

## robustness_and_descriptive_A

| analysis | comparison | people | cells | videos | skill | ncv90_lo | ncv90_hi |
|---|---|---|---|---|---|---|---|
| D_E1 | M5_E1_vs_M2 | 26 | 121 | 5 | 0.2605 | -0.1043 | 0.5839 |
| D_E5 | M5_vs_M2 | 46 | 128 | 3 | -0.0229 | -0.1412 | 0.0980 |
| H3_1_partial | M5_vs_M2 | 68 | 259 | 8 | 0.0190 | -0.0406 | 0.0788 |
| H3_2_eye30 | M5_vs_M2 | 65 | 223 | 8 | 0.0087 | -0.0205 | 0.0384 |
| H3_2_eye70 | M5_vs_M2 | 69 | 265 | 8 | 0.0170 | -0.0315 | 0.0583 |
| H3_3_four | M5_vs_M2 | 57 | 216 | 8 | 0.0185 | -0.0295 | 0.0725 |
| H3_3_four | M5_PUPIL_vs_M2 | 57 | 216 | 8 | 0.0316 | -0.0286 | 0.0999 |
| H3_4_raw | M5_vs_M2 | 68 | 259 | 8 | 0.0212 | -0.0405 | 0.0761 |
| H3_5_alpha | M5_vs_M2 | 68 | 234 | 7 | 0.0161 | -0.0380 | 0.0626 |
| H3_6_gpa | M5_vs_M2 | 68 | 259 | 8 | 0.0153 | -0.0349 | 0.0608 |

## BC

| regime | within_content_skill | absolute_skill | boot90_lo | boot90_hi |
|---|---|---|---|---|
| B | -0.0249 | -0.0140 | -0.0491 | -0.0062 |
| C | 0.0203 | 0.0099 | -0.0136 | 0.0445 |

## BC_per_video

| video | B | C | B_minus_C |
|---|---|---|---|
| 30o4omX5qfo | -0.0562 | -0.0359 | -0.0203 |
| VVAKFJ8VVp4 | -0.0188 | 0.0239 | -0.0427 |
| bYgV9nvgJ3E | -0.0025 | 0.0046 | -0.0070 |
| e0NT9i4Qnak | -0.0692 | -0.0185 | -0.0507 |
| lkRZKqDdwzU | -0.0523 | 0.0046 | -0.0570 |
| mnYSMhR3jCI | -0.0147 | 0.0514 | -0.0662 |
| rkntp3_cZl4 | -0.0573 | -0.0164 | -0.0409 |
| zQGOcOUBi6s | -0.0081 | -0.0017 | -0.0064 |

## CAS

| analysis | n_people | n_cells | n_core_cells | policy_vs_M2_skill_all_cells | policy_vs_M2_cell_weighted | skill_on_core_cells | skill_on_noncore_cells | label | elapsed_s |
|---|---|---|---|---|---|---|---|---|---|
| D_CAS | 72 | 302 | 259 | -0.0000 | -0.0101 | -0.0119 | 0.0000 | DESCRIPTIVE coverage-policy risk; selection report in analysis_population.md | 565.4292 |

## transport

| direction | variant | skill | loss_diff_lo | loss_diff_hi |
|---|---|---|---|---|
| E4_core->E5_core | source_offsets | -0.1426 | -0.0091 | -0.0012 |
| E4_core->E5_core | target_mean_recalibrated_USES_TARGET_LABELS | -0.0653 | -0.0054 | 0.0011 |
| E5_core->E4_core | source_offsets | 0.0180 | -0.0003 | 0.0015 |
| E5_core->E4_core | target_mean_recalibrated_USES_TARGET_LABELS | 0.0280 | -0.0000 | 0.0017 |

## explanatory

| name | estimate | se | wald_z | ci95 | p_wald |
|---|---|---|---|---|---|
| intercept | 0.4263 | 0.0432 | 9.8741 | [0.3416469504313475, 0.5108708136472933] | 0.0000 |
| experiment_E4 | 0.0942 | 0.0819 | 1.1498 | [-0.06637976507957172, 0.25479919899432735] | 0.2502 |
| C_age | -0.0158 | 0.0225 | -0.7023 | [-0.05994998802636996, 0.02832122208853434] | 0.4825 |
| C_sex_male | -0.0005 | 0.0181 | -0.0251 | [-0.036022459759954176, 0.0351115368244696] | 0.9800 |
| C_asrs_inattention | -0.0012 | 0.0175 | -0.0700 | [-0.0355809484346631, 0.03312776936258317] | 0.9442 |
| C_asrs_hyperactivity | 0.0123 | 0.0179 | 0.6870 | [-0.02276754980526485, 0.047338783463371226] | 0.4921 |
| C_digit_span | 0.0037 | 0.0152 | 0.2450 | [-0.026106246811315507, 0.033566053012593924] | 0.8064 |
| C_digit_span_missing | -0.0245 | 0.0209 | -1.1702 | [-0.06543121925023127, 0.01650910817053075] | 0.2419 |
| Q_gaze_correction | 0.0216 | 0.0147 | 1.4659 | [-0.007284671377673788, 0.05051380549016833] | 0.1427 |
| Q_pupil_correction | -0.0410 | 0.0177 | -2.3135 | [-0.07566035275846777, -0.006258980249079907] | 0.0207 |
| Q_eeg_zeroed | -0.0128 | 0.0110 | -1.1600 | [-0.03437811898084453, 0.008815457734130967] | 0.2461 |
| Q_eeg_16hz_excess | -0.0230 | 0.0141 | -1.6365 | [-0.050612967552627966, 0.004552388079444292] | 0.1017 |
| RF1_eeg_posterior_alpha | 0.0173 | 0.0150 | 1.1567 | [-0.012039833076362756, 0.04671292649986058] | 0.2474 |
| RF2_eeg_frontal_theta | -0.0020 | 0.0153 | -0.1298 | [-0.03191911275207714, 0.027953051106661315] | 0.8967 |
| RF3_heart_rate | -0.0161 | 0.0230 | -0.7027 | [-0.061167308156888305, 0.02888281348819021] | 0.4822 |
| RF4_ln_rmssd | -0.0085 | 0.0237 | -0.3575 | [-0.05485046825464874, 0.03792737938701773] | 0.7207 |
| RF5_gaze_dispersion | 0.0089 | 0.0267 | 0.3320 | [-0.043436849753736184, 0.061152848989548925] | 0.7399 |
| RF6_saccade_rate | -0.0043 | 0.0146 | -0.2921 | [-0.0329747534542604, 0.0244219472817354] | 0.7702 |
| SYN1_eeg_isc | 0.0283 | 0.0196 | 1.4406 | [-0.010206773417694045, 0.0668198266188622] | 0.1497 |
| SYN2_hr_isc | -0.0094 | 0.0122 | -0.7732 | [-0.033287703250849274, 0.014453587751307822] | 0.4394 |
| SYN3_gaze_isc | 0.0308 | 0.0167 | 1.8456 | [-0.0019099742932909072, 0.06355726923284483] | 0.0649 |

## identity_probe

| accuracy | majority_rate | chance_by_frequency | n_classes | splits | label | elapsed_s |
|---|---|---|---|---|---|---|
| 0.5019 | 0.1467 | 0.1159 | 9 | 100 | DIAGNOSTIC: accuracy well above the majority rate means features carry content identity | 0.6217 |

## Runs

- `D_BC`: run `20261007T165649Z_c945a3df`, config `f34f1b03b657`, frozen=True, git `d737ac162c`
- `D_CAS`: run `20261007T170301Z_6dbbf219`, config `f34f1b03b657`, frozen=True, git `d737ac162c`
- `D_E1`: run `20261007T182532Z_8e41b75d`, config `f34f1b03b657`, frozen=True, git `d737ac162c`
- `D_E5`: run `20261007T171226Z_99ee1196`, config `f34f1b03b657`, frozen=True, git `d737ac162c`
- `D_transport`: run `20261007T182520Z_c9759030`, config `f34f1b03b657`, frozen=True, git `d737ac162c`
- `H1_H2`: run `20261005T104908Z_c57b28d6`, config `f34f1b03b657`, frozen=True, git `d02e477d62`
- `H3_1_partial`: run `20261006T123221Z_a27a0b62`, config `f34f1b03b657`, frozen=True, git `d737ac162c`
- `H3_2_eye30`: run `20261006T123439Z_5a0263c2`, config `f34f1b03b657`, frozen=True, git `d737ac162c`
- `H3_2_eye70`: run `20261006T180824Z_85517ad2`, config `f34f1b03b657`, frozen=True, git `d737ac162c`
- `H3_3_four`: run `20261007T031645Z_20f139c0`, config `f34f1b03b657`, frozen=True, git `d737ac162c`
- `H3_4_raw`: run `20261007T084404Z_9117498b`, config `f34f1b03b657`, frozen=True, git `d737ac162c`
- `H3_5_alpha`: run `20261007T130648Z_ea387334`, config `f34f1b03b657`, frozen=True, git `d737ac162c`
- `H3_6_gpa`: run `20261006T123257Z_d1e38f11`, config `f34f1b03b657`, frozen=True, git `d737ac162c`
- `S_identity_probe`: run `20261007T183823Z_12d883ba`, config `f34f1b03b657`, frozen=True, git `d737ac162c`
- `X_explanatory`: run `20261007T183817Z_904fe9c0`, config `f34f1b03b657`, frozen=True, git `d737ac162c`
