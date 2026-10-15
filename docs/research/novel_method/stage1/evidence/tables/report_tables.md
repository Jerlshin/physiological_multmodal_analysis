# Stage-1 simulation tables (generated)

Written by `stage1/scripts/report.py` from the stored replicates (synthetic outcomes only). Do not edit by hand.

## 1. False-detection rate at α = .05 (base nulls; N0–N3 500 replicates, N1q 500 E4/pooled after R-E, 200 development, E5 200)

### E4 (locked primary)

| model | test | N0 | N1 | N2 | N3 | N1q | max N0–N3 |
|---|---|---|---|---|---|---|---|
| CAIRN-linear-dt | T1 | 0.054 | 0.042 | 0.058 | 0.058 | 0.064 | 0.058 |
| CAIRN-linear-dt | T2 | 0.042 | 0.042 | 0.046 | 0.050 | 0.074 | 0.050 |
| CAIRN-linear-dt | T2c | 0.048 | 0.040 | — | — | 0.066 | 0.048 |
| CAIRN-linear-dt | NH1 | 0.038 | 0.030 | 0.040 | 0.042 | 0.056 | 0.042 |
| CAIRN-linear-dt | T1lr | 0.052 | 0.046 | 0.064 | 0.060 | 0.060 | 0.064 |
| CAIRN-linear-dt | T2lr | 0.044 | 0.038 | 0.064 | 0.056 | 0.066 | 0.064 |
| CAIRN-linear-dt | T2clr | 0.052 | 0.044 | — | — | 0.062 | 0.052 |
| CAIRN-linear-dt | NH1lr | 0.038 | 0.030 | 0.050 | 0.042 | 0.048 | 0.050 |
| dir | T1 | 0.046 | 0.036 | 0.054 | 0.062 | 0.070 | 0.062 |
| dir | T2 | 0.052 | 0.044 | 0.046 | 0.066 | 0.070 | 0.066 |
| dir | NH1 | 0.038 | 0.030 | 0.034 | 0.056 | 0.052 | 0.056 |
| dir | T1lr | 0.042 | 0.042 | 0.058 | 0.058 | 0.070 | 0.058 |
| dir | T2lr | 0.060 | 0.034 | 0.056 | 0.066 | 0.068 | 0.066 |
| dir | NH1lr | 0.032 | 0.026 | 0.036 | 0.050 | 0.050 | 0.050 |
| CAIRN-validity-dt | T2 | 0.036 | — | — | 0.050 | — | 0.050 |
| CAIRN-validity-dt | T2lr | 0.032 | — | — | 0.062 | — | 0.062 |
| full-data glmm Wald | one-sided z | 0.062 | 0.128 | 0.078 | 0.030 | 0.106 | 0.128 |
| full-data naive Wald | one-sided z | 0.056 | 0.124 | 0.076 | 0.028 | 0.106 | 0.124 |
| full-data robust Wald | one-sided z | 0.086 | 0.174 | 0.086 | 0.054 | 0.160 | 0.174 |
| full-data literal Wald | one-sided z | 0.052 | 0.136 | 0.068 | 0.040 | 0.074 | 0.136 |

### Development

| model | test | N0 | N1 | N2 | N3 | N1q | max N0–N3 |
|---|---|---|---|---|---|---|---|
| CAIRN-linear-dt | T1 | 0.032 | 0.060 | 0.054 | 0.040 | 0.050 | 0.060 |
| CAIRN-linear-dt | T2 | 0.040 | 0.048 | 0.048 | 0.038 | 0.055 | 0.048 |
| CAIRN-linear-dt | T2c | 0.046 | 0.044 | — | — | 0.060 | 0.046 |
| CAIRN-linear-dt | NH1 | 0.026 | 0.034 | 0.040 | 0.028 | 0.025 | 0.040 |
| CAIRN-linear-dt | T1lr | 0.046 | 0.058 | 0.054 | 0.046 | 0.035 | 0.058 |
| CAIRN-linear-dt | T2lr | 0.054 | 0.054 | 0.056 | 0.042 | 0.045 | 0.056 |
| CAIRN-linear-dt | T2clr | 0.048 | 0.062 | — | — | 0.040 | 0.062 |
| CAIRN-linear-dt | NH1lr | 0.032 | 0.036 | 0.036 | 0.022 | 0.030 | 0.036 |
| CAIRN-validity-dt | T2 | 0.058 | — | — | 0.036 | — | 0.058 |
| CAIRN-validity-dt | T2lr | 0.050 | — | — | 0.048 | — | 0.050 |
| stop-rule | go | 0.000 | 0.002 | 0.008 | 0.002 | 0.005 | 0.008 |
| full-data glmm Wald | one-sided z | 0.026 | 0.292 | 0.036 | 0.032 | 0.100 | 0.292 |
| full-data naive Wald | one-sided z | 0.028 | 0.284 | 0.036 | 0.032 | 0.100 | 0.284 |
| full-data robust Wald | one-sided z | 0.056 | 0.336 | 0.054 | 0.046 | 0.140 | 0.336 |
| full-data literal Wald | one-sided z | 0.050 | 0.344 | 0.026 | 0.036 | 0.135 | 0.344 |

### E4 + E5 pooled

| model | test | N0 | N1 | N2 | N3 | N1q | max N0–N3 |
|---|---|---|---|---|---|---|---|
| CAIRN-linear-dt | T1 | 0.054 | 0.050 | 0.058 | 0.054 | 0.066 | 0.058 |
| CAIRN-linear-dt | T2 | 0.066 | 0.064 | 0.044 | 0.050 | 0.070 | 0.066 |
| CAIRN-linear-dt | T2c | 0.066 | 0.060 | — | — | 0.072 | 0.066 |
| CAIRN-linear-dt | NH1 | 0.042 | 0.032 | 0.034 | 0.040 | 0.056 | 0.042 |
| CAIRN-linear-dt | T1lr | 0.024 | 0.066 | 0.048 | 0.042 | 0.082 | 0.066 |
| CAIRN-linear-dt | T2lr | 0.040 | 0.060 | 0.054 | 0.044 | 0.080 | 0.060 |
| CAIRN-linear-dt | T2clr | 0.038 | 0.068 | — | — | 0.070 | 0.068 |
| CAIRN-linear-dt | NH1lr | 0.020 | 0.052 | 0.038 | 0.032 | 0.068 | 0.052 |
| dir | T1 | 0.058 | 0.054 | 0.070 | 0.050 | 0.060 | 0.070 |
| dir | T2 | 0.062 | 0.052 | 0.068 | 0.054 | 0.068 | 0.068 |
| dir | NH1 | 0.040 | 0.042 | 0.050 | 0.030 | 0.050 | 0.050 |
| dir | T1lr | 0.032 | 0.040 | 0.076 | 0.052 | 0.076 | 0.076 |
| dir | T2lr | 0.046 | 0.046 | 0.078 | 0.036 | 0.068 | 0.078 |
| dir | NH1lr | 0.024 | 0.024 | 0.064 | 0.032 | 0.050 | 0.064 |
| CAIRN-validity-dt | T2 | 0.052 | — | — | 0.060 | — | 0.060 |
| CAIRN-validity-dt | T2lr | 0.048 | — | — | 0.068 | — | 0.068 |
| full-data glmm Wald | one-sided z | 0.036 | 0.174 | 0.038 | 0.060 | 0.166 | 0.174 |
| full-data naive Wald | one-sided z | 0.040 | 0.168 | 0.038 | 0.062 | 0.164 | 0.168 |
| full-data robust Wald | one-sided z | 0.056 | 0.194 | 0.046 | 0.078 | 0.198 | 0.194 |
| full-data literal Wald | one-sided z | 0.054 | 0.144 | 0.042 | 0.052 | 0.088 | 0.144 |

### E5 (locked secondary)

| model | test | N0 | N1 | N2 | N3 | N1q | max N0–N3 |
|---|---|---|---|---|---|---|---|
| CAIRN-linear-dt | T1 | 0.065 | 0.040 | — | — | — | 0.065 |
| CAIRN-linear-dt | T2 | 0.055 | 0.040 | — | — | — | 0.055 |
| CAIRN-linear-dt | T2c | — | 0.035 | — | — | — | 0.035 |
| CAIRN-linear-dt | NH1 | 0.035 | 0.020 | — | — | — | 0.035 |
| CAIRN-linear-dt | T1lr | 0.060 | 0.030 | — | — | — | 0.060 |
| CAIRN-linear-dt | T2lr | 0.050 | 0.040 | — | — | — | 0.050 |
| CAIRN-linear-dt | T2clr | — | 0.025 | — | — | — | 0.025 |
| CAIRN-linear-dt | NH1lr | 0.045 | 0.025 | — | — | — | 0.045 |
| dir | T1 | 0.035 | 0.035 | — | — | — | 0.035 |
| dir | T2 | 0.045 | 0.030 | — | — | — | 0.045 |
| dir | NH1 | 0.020 | 0.010 | — | — | — | 0.020 |
| dir | T1lr | 0.030 | 0.055 | — | — | — | 0.055 |
| dir | T2lr | 0.030 | 0.045 | — | — | — | 0.045 |
| dir | NH1lr | 0.010 | 0.025 | — | — | — | 0.025 |
| CAIRN-validity-dt | T2 | 0.070 | — | — | — | — | 0.070 |
| CAIRN-validity-dt | T2lr | 0.070 | — | — | — | — | 0.070 |
| full-data glmm Wald | one-sided z | 0.050 | 0.085 | — | — | — | 0.085 |
| full-data naive Wald | one-sided z | 0.050 | 0.085 | — | — | — | 0.085 |
| full-data robust Wald | one-sided z | 0.055 | 0.100 | — | — | — | 0.100 |
| full-data literal Wald | one-sided z | 0.055 | 0.080 | — | — | — | 0.080 |

## 2. Power (rejection rate) on the alternative grid, ρ = .4

| set | statistic | OR 1 | OR 1.15 | OR 1.25 | OR 1.35 | OR 1.5 | OR 1.75 | OR 2 | OR 2.5 | OR 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| E4 (locked primary) | NH1, CV (plan) | 0.04 | 0.08 | 0.12 | 0.32 | 0.51 | 0.84 | 0.95 | 1.00 | 1.00 |
| E4 (locked primary) | NH1, LR | 0.04 | 0.10 | 0.18 | 0.34 | 0.53 | 0.85 | 0.95 | 1.00 | 1.00 |
| E4 (locked primary) | NH1, CV, frozen direction | 0.04 | 0.09 | 0.15 | 0.40 | 0.65 | 0.91 | 0.99 | 1.00 | 1.00 |
| E4 (locked primary) | NH1, LR, frozen direction | 0.03 | 0.10 | 0.17 | 0.45 | 0.67 | 0.94 | 0.99 | 1.00 | 1.00 |
| E4 (locked primary) | T1 alone, CV | 0.05 | 0.11 | 0.16 | 0.39 | 0.54 | 0.87 | 0.97 | 1.00 | 1.00 |
| E4 (locked primary) | T2 alone, CV | 0.04 | 0.11 | 0.14 | 0.34 | 0.54 | 0.85 | 0.95 | 1.00 | 1.00 |
| E4 (locked primary) | oracle GLMM Wald (true composite) | 0.06 | 0.32 | 0.54 | 0.82 | 0.93 | 0.99 | 1.00 | 1.00 | 1.00 |
| E4 (locked primary) | oracle naive Wald (independent responses) | 0.06 | 0.30 | 0.51 | 0.80 | 0.92 | 0.99 | 1.00 | 1.00 | 1.00 |
| E4 + E5 pooled | NH1, CV (plan) | 0.04 | 0.12 | 0.33 | 0.51 | 0.85 | 0.99 | 1.00 | 1.00 | 1.00 |
| E4 + E5 pooled | NH1, LR | 0.02 | 0.14 | 0.36 | 0.66 | 0.93 | 1.00 | 1.00 | 1.00 | 1.00 |
| E4 + E5 pooled | NH1, CV, frozen direction | 0.04 | 0.10 | 0.34 | 0.60 | 0.92 | 0.99 | 1.00 | 1.00 | 1.00 |
| E4 + E5 pooled | NH1, LR, frozen direction | 0.02 | 0.13 | 0.43 | 0.74 | 0.96 | 1.00 | 1.00 | 1.00 | 1.00 |
| E4 + E5 pooled | T1 alone, CV | 0.05 | 0.15 | 0.38 | 0.56 | 0.90 | 0.99 | 1.00 | 1.00 | 1.00 |
| E4 + E5 pooled | T2 alone, CV | 0.07 | 0.14 | 0.36 | 0.58 | 0.89 | 0.99 | 1.00 | 1.00 | 1.00 |
| E4 + E5 pooled | oracle GLMM Wald (true composite) | 0.04 | 0.48 | 0.81 | 0.95 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| E4 + E5 pooled | oracle naive Wald (independent responses) | 0.04 | 0.47 | 0.80 | 0.95 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Development | NH1, CV (plan) | 0.03 | 0.09 | 0.26 | 0.49 | 0.83 | 0.99 | 1.00 | 1.00 | 1.00 |
| Development | NH1, LR | 0.03 | 0.10 | 0.26 | 0.64 | 0.91 | 1.00 | 1.00 | 1.00 | 1.00 |
| Development | T1 alone, CV | 0.03 | 0.11 | 0.32 | 0.55 | 0.85 | 0.99 | 1.00 | 1.00 | 1.00 |
| Development | T2 alone, CV | 0.04 | 0.14 | 0.35 | 0.58 | 0.87 | 0.99 | 1.00 | 1.00 | 1.00 |
| Development | oracle GLMM Wald (true composite) | 0.03 | 0.47 | 0.86 | 0.96 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Development | oracle naive Wald (independent responses) | 0.03 | 0.45 | 0.86 | 0.95 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |

ρ = 0.2 (OR 1 = pure null N0):

| set | statistic | OR 1 | OR 1.5 | OR 2 | OR 2.5 | OR 3 | OR 4 |
|---|---|---|---|---|---|---|---|
| E4 (locked primary) | NH1, CV | 0.04 | 0.28 | 0.52 | 0.89 | 1.00 | 1.00 |
| E4 (locked primary) | NH1, LR | 0.04 | 0.30 | 0.63 | 0.96 | 0.99 | 1.00 |
| E4 (locked primary) | NH1, LR, frozen direction | 0.03 | 0.46 | 0.75 | 0.97 | 1.00 | 1.00 |
| E4 + E5 pooled | NH1, CV | 0.04 | 0.56 | 0.92 | 1.00 | 1.00 | 1.00 |
| E4 + E5 pooled | NH1, LR | 0.02 | 0.63 | 0.97 | 1.00 | 1.00 | 1.00 |
| E4 + E5 pooled | NH1, LR, frozen direction | 0.02 | 0.74 | 0.99 | 1.00 | 1.00 | 1.00 |
| Development | NH1, CV | 0.03 | 0.48 | 0.96 | 0.98 | 1.00 | 1.00 |
| Development | NH1, LR | 0.03 | 0.62 | 0.99 | 0.98 | 1.00 | 1.00 |

ρ = 0.7 (OR 1 = pure null N0):

| set | statistic | OR 1 | OR 1.15 | OR 1.25 | OR 1.35 | OR 1.5 | OR 1.75 | OR 2 |
|---|---|---|---|---|---|---|---|---|
| E4 (locked primary) | NH1, CV | 0.04 | 0.07 | 0.30 | 0.54 | 0.87 | 0.97 | 1.00 |
| E4 (locked primary) | NH1, LR | 0.04 | 0.13 | 0.31 | 0.59 | 0.85 | 0.99 | 1.00 |
| E4 (locked primary) | NH1, LR, frozen direction | 0.03 | 0.15 | 0.34 | 0.69 | 0.94 | 0.99 | 1.00 |
| E4 + E5 pooled | NH1, CV | 0.04 | 0.21 | 0.45 | 0.81 | 0.98 | 1.00 | 1.00 |
| E4 + E5 pooled | NH1, LR | 0.02 | 0.28 | 0.65 | 0.88 | 1.00 | 1.00 | 1.00 |
| E4 + E5 pooled | NH1, LR, frozen direction | 0.02 | 0.34 | 0.67 | 0.95 | 1.00 | 1.00 | 1.00 |
| Development | NH1, CV | 0.03 | 0.20 | 0.52 | 0.88 | 0.98 | 1.00 | 1.00 |
| Development | NH1, LR | 0.03 | 0.21 | 0.59 | 0.93 | 1.00 | 1.00 | 1.00 |

## 3. Minimum detectable effect: OR per SD of the latent state at 80% power

| set | statistic | ρ = 0.2 | ρ = 0.4 | ρ = 0.7 |
|---|---|---|---|---|
| Development | CAIRN-linear-dt NH1 | 1.817 | 1.486 | 1.327 |
| Development | CAIRN-linear-dt NH1lr | 1.725 | 1.439 | 1.311 |
| Development | full-data glmm Wald z | 1.404 | 1.233 | 1.172 |
| Development | full-data naive Wald z | 1.409 | 1.234 | 1.175 |
| E4 + E5 pooled | CAIRN-linear-dt NH1 | 1.817 | 1.477 | 1.347 |
| E4 + E5 pooled | CAIRN-linear-dt NH1lr | 1.732 | 1.427 | 1.314 |
| E4 + E5 pooled | dir NH1 | 1.747 | 1.443 | 1.329 |
| E4 + E5 pooled | dir NH1lr | 1.607 | 1.387 | 1.295 |
| E4 + E5 pooled | full-data glmm Wald z | 1.393 | 1.248 | 1.175 |
| E4 + E5 pooled | full-data naive Wald z | 1.398 | 1.253 | 1.175 |
| E4 (locked primary) | CAIRN-linear-dt NH1 | 2.368 | 1.718 | 1.467 |
| E4 (locked primary) | CAIRN-linear-dt NH1lr | 2.244 | 1.705 | 1.470 |
| E4 (locked primary) | dir NH1 | 2.087 | 1.642 | 1.420 |
| E4 (locked primary) | dir NH1lr | 2.104 | 1.618 | 1.414 |
| E4 (locked primary) | full-data glmm Wald z | 1.583 | 1.341 | 1.257 |
| E4 (locked primary) | full-data naive Wald z | 1.583 | 1.356 | 1.274 |

At ρ = .4, in usefulness units (population metrics of the oracle predictor at the MDE; λ_obs = log OR · √ρ):

| set | statistic | mde_or | lambda_obs | s_item_pop_at_mde | d_auc_wp_pop_at_mde |
|---|---|---|---|---|---|
| Development | CAIRN-linear-dt NH1 | 1.4859 | 0.2505 | 0.0063 | 0.0066 |
| Development | CAIRN-linear-dt NH1lr | 1.4387 | 0.2300 | 0.0054 | 0.0058 |
| Development | full-data glmm Wald z | 1.2332 | 0.1326 | 0.0019 | 0.0022 |
| Development | full-data naive Wald z | 1.2338 | 0.1329 | 0.0019 | 0.0022 |
| E4 + E5 pooled | CAIRN-linear-dt NH1 | 1.4773 | 0.2468 | 0.0062 | 0.0065 |
| E4 + E5 pooled | CAIRN-linear-dt NH1lr | 1.4273 | 0.2250 | 0.0053 | 0.0056 |
| E4 + E5 pooled | dir NH1 | 1.4425 | 0.2317 | 0.0055 | 0.0059 |
| E4 + E5 pooled | dir NH1lr | 1.3869 | 0.2068 | 0.0045 | 0.0049 |
| E4 + E5 pooled | full-data glmm Wald z | 1.2484 | 0.1403 | 0.0021 | 0.0021 |
| E4 + E5 pooled | full-data naive Wald z | 1.2531 | 0.1427 | 0.0022 | 0.0021 |
| E4 (locked primary) | CAIRN-linear-dt NH1 | 1.7181 | 0.3423 | 0.0103 | 0.0103 |
| E4 (locked primary) | CAIRN-linear-dt NH1lr | 1.7049 | 0.3374 | 0.0100 | 0.0100 |
| E4 (locked primary) | dir NH1 | 1.6424 | 0.3138 | 0.0088 | 0.0086 |
| E4 (locked primary) | dir NH1lr | 1.6178 | 0.3043 | 0.0084 | 0.0081 |
| E4 (locked primary) | full-data glmm Wald z | 1.3409 | 0.1855 | 0.0032 | 0.0019 |
| E4 (locked primary) | full-data naive Wald z | 1.3557 | 0.1925 | 0.0035 | 0.0022 |

## 4. Candidate confirmatory designs (rule R-B2)

| design | set | statistic | moment | max_false_detection | admissible | power_or_1_35 | power_or_1_50 | mde80_or | or_useful_cv | power_at_useful_cv | or_useful_pop | power_at_useful_pop |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | locked_primary | CV log-loss | refitted | 0.058 | True | 0.320 | 0.505 | 1.718 | 2.565 | 1.000 | 2.162 | 0.967 |
| 2 | locked_primary | CV log-loss | frozen development direction | 0.066 | True | 0.395 | 0.650 | 1.642 | 2.264 | 0.998 | 2.162 | 0.997 |
| 3 | locked_primary | likelihood ratio | refitted | 0.064 | True | 0.335 | 0.530 | 1.705 | 2.565 | 1.000 | 2.162 | 0.971 |
| 4 | locked_primary | likelihood ratio | frozen development direction | 0.066 | True | 0.445 | 0.670 | 1.618 | 2.264 | 0.998 | 2.162 | 0.997 |
| 5 | locked_pooled | CV log-loss | refitted | 0.066 | True | 0.505 | 0.850 | 1.477 | 2.128 | 1.000 | 2.115 | 1.000 |
| 6 | locked_pooled | CV log-loss | frozen development direction | 0.070 | True | 0.605 | 0.915 | 1.443 | 2.119 | 1.000 | 2.115 | 1.000 |
| 7 | locked_pooled | likelihood ratio | refitted | 0.066 | True | 0.660 | 0.925 | 1.427 | 2.128 | 1.000 | 2.115 | 1.000 |
| 8 | locked_pooled | likelihood ratio | frozen development direction | 0.078 | False | 0.745 | 0.960 | 1.387 | 2.119 | 1.000 | 2.115 | 1.000 |

Recommended by the pre-declared choice rule: design 7.

## 5. Usefulness mapping: smallest OR whose mean metric meets S_item ≥ .01 and ΔAUC_wp ≥ .02

| set | variant | rho | or_s_item | or_d_auc | or_useful |
|---|---|---|---|---|---|
| Development | infinite-data | 0.200 | 2.099 | 2.946 | 2.946 |
| Development | infinite-data | 0.400 | 1.657 | 2.085 | 2.085 |
| Development | infinite-data | 0.700 | 1.459 | 1.740 | 1.740 |
| E4 + E5 pooled | infinite-data | 0.200 | 2.122 | 2.982 | 2.982 |
| E4 + E5 pooled | infinite-data | 0.400 | 1.657 | 2.115 | 2.115 |
| E4 + E5 pooled | infinite-data | 0.700 | 1.453 | 1.735 | 1.735 |
| E4 (locked primary) | infinite-data | 0.200 | 2.186 | 3.128 | 3.128 |
| E4 (locked primary) | infinite-data | 0.400 | 1.704 | 2.162 | 2.162 |
| E4 (locked primary) | infinite-data | 0.700 | 1.490 | 1.800 | 1.800 |
| Development | CAIRN-linear-dt | 0.200 | 3.384 | 3.004 | 3.384 |
| Development | CAIRN-linear-dt | 0.400 | 2.209 | 2.114 | 2.209 |
| Development | CAIRN-linear-dt | 0.700 | 1.795 | 1.771 | 1.795 |
| E4 + E5 pooled | CAIRN-linear-dt | 0.200 | 2.846 | 3.048 | 3.048 |
| E4 + E5 pooled | CAIRN-linear-dt | 0.400 | 2.012 | 2.128 | 2.128 |
| E4 + E5 pooled | CAIRN-linear-dt | 0.700 | 1.666 | 1.744 | 1.744 |
| E4 + E5 pooled | CAIRN-linear-dt-dir | 0.200 | 2.409 | 3.048 | 3.048 |
| E4 + E5 pooled | CAIRN-linear-dt-dir | 0.400 | 1.809 | 2.119 | 2.119 |
| E4 + E5 pooled | CAIRN-linear-dt-dir | 0.700 | 1.560 | 1.747 | 1.747 |
| E4 (locked primary) | CAIRN-linear-dt | 0.200 | > grid | 3.514 | > grid |
| E4 (locked primary) | CAIRN-linear-dt | 0.400 | 2.565 | 2.318 | 2.565 |
| E4 (locked primary) | CAIRN-linear-dt | 0.700 | 1.977 | 1.868 | 1.977 |
| E4 (locked primary) | CAIRN-linear-dt-dir | 0.200 | 2.995 | 3.362 | 3.362 |
| E4 (locked primary) | CAIRN-linear-dt-dir | 0.400 | 2.033 | 2.264 | 2.264 |
| E4 (locked primary) | CAIRN-linear-dt-dir | 0.700 | 1.679 | 1.822 | 1.822 |

Population (infinite-data) S_item and ΔAUC_wp of the oracle predictor, ρ = .4:

| set | metric | OR 1.15 | OR 1.25 | OR 1.35 | OR 1.5 | OR 1.75 | OR 2 | OR 2.5 | OR 3 |
|---|---|---|---|---|---|---|---|---|---|
| Development | s_item_pop | 0.0008 | 0.0021 | 0.0037 | 0.0066 | 0.0119 | 0.0173 | 0.0271 | 0.0355 |
| Development | d_auc_wp_pop | 0.0010 | 0.0024 | 0.0040 | 0.0069 | 0.0122 | 0.0182 | 0.0279 | 0.0358 |
| E4 + E5 pooled | s_item_pop | 0.0008 | 0.0021 | 0.0037 | 0.0066 | 0.0119 | 0.0171 | 0.0266 | 0.0345 |
| E4 + E5 pooled | d_auc_wp_pop | 0.0011 | 0.0021 | 0.0042 | 0.0069 | 0.0118 | 0.0179 | 0.0264 | 0.0334 |
| E4 (locked primary) | s_item_pop | 0.0008 | 0.0019 | 0.0034 | 0.0060 | 0.0108 | 0.0158 | 0.0248 | 0.0324 |
| E4 (locked primary) | d_auc_wp_pop | -0.0004 | 0.0003 | 0.0020 | 0.0053 | 0.0109 | 0.0164 | 0.0267 | 0.0341 |

Mean cross-validated estimate (planned procedure), ρ = .4:

| set | model | metric | OR 1.15 | OR 1.25 | OR 1.35 | OR 1.5 | OR 1.75 | OR 2.5 | OR 2 | OR 3 | OR 1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Development | CAIRN-linear-dt | s_item | -0.0078 | -0.0067 | -0.0050 | -0.0027 | 0.0025 | 0.0148 | 0.0062 | 0.0217 | -0.0077 |
| Development | CAIRN-linear-dt | d_auc_wp | -0.0009 | 0.0004 | 0.0032 | 0.0062 | 0.0116 | 0.0283 | 0.0172 | 0.0378 | -0.0014 |
| E4 + E5 pooled | CAIRN-linear-dt | s_item | -0.0047 | -0.0042 | -0.0029 | 0.0003 | 0.0048 | 0.0186 | 0.0098 | 0.0254 | -0.0057 |
| E4 + E5 pooled | CAIRN-linear-dt | d_auc_wp | -0.0006 | 0.0014 | 0.0022 | 0.0061 | 0.0130 | 0.0272 | 0.0172 | 0.0350 | -0.0013 |
| E4 + E5 pooled | dir | s_item | -0.0008 | -0.0001 | 0.0013 | 0.0039 | 0.0088 | 0.0225 | 0.0138 | 0.0290 | -0.0012 |
| E4 + E5 pooled | dir | d_auc_wp | -0.0003 | 0.0012 | 0.0022 | 0.0059 | 0.0127 | 0.0272 | 0.0175 | 0.0352 | -0.0004 |
| E4 (locked primary) | CAIRN-linear-dt | s_item | -0.0113 | -0.0099 | -0.0088 | -0.0069 | -0.0036 | 0.0091 | 0.0015 | 0.0154 | -0.0113 |
| E4 (locked primary) | CAIRN-linear-dt | d_auc_wp | -0.0005 | 0.0000 | 0.0021 | 0.0035 | 0.0096 | 0.0229 | 0.0144 | 0.0311 | -0.0019 |
| E4 (locked primary) | dir | s_item | -0.0026 | -0.0023 | -0.0009 | 0.0006 | 0.0052 | 0.0175 | 0.0094 | 0.0243 | -0.0025 |
| E4 (locked primary) | dir | d_auc_wp | -0.0004 | 0.0001 | 0.0024 | 0.0041 | 0.0097 | 0.0241 | 0.0149 | 0.0325 | -0.0008 |

## 6. Clustering versus the plan §20.3 analytic estimate (ρ = .4)

| set | anchorable responses | learners | moments | analytic SE (independent) | oracle GLMM SE (model) | oracle GLMM SD (empirical) | variance ratio | analytic MDE | oracle GLMM MDE | NH1 CV MDE | NH1 LR MDE |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E4 (locked primary) | 977 | 39 | 19 | 0.066 | 0.073 | 0.075 | 1.035 | 1.339 | 1.341 | 1.718 | 1.705 |
| E4 + E5 pooled | 2096 | 86 | 19 | 0.045 | 0.050 | 0.048 | 0.937 | 1.219 | 1.248 | 1.477 | 1.427 |
| Development | 2205 | 55 | 59 | 0.044 | 0.049 | 0.043 | 0.787 | 1.215 | 1.233 | 1.486 | 1.439 |

## 7. Joint behaviour of T1 and T2

| set | scenario | statistic | n | T1 | T2 | both | T1_only | T2_only | p_spearman | P_T2_given_T1 |
|---|---|---|---|---|---|---|---|---|---|---|
| Development | ALT_or1.35_rho0.4_q0.5 | CV | 200 | 0.545 | 0.585 | 0.495 | 0.050 | 0.090 | 0.879 | 0.908 |
| Development | ALT_or1.5_rho0.4_q0.5 | CV | 200 | 0.850 | 0.870 | 0.830 | 0.020 | 0.040 | 0.769 | 0.976 |
| Development | ALT_or2_rho0.4_q0.5 | CV | 200 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | — | 1.000 |
| Development | N0_or1_rho0.4_q0.5 | CV | 500 | 0.032 | 0.040 | 0.026 | 0.006 | 0.014 | 0.929 | 0.812 |
| Development | N1_or1_rho0.4_q0.5 | CV | 500 | 0.060 | 0.048 | 0.034 | 0.026 | 0.014 | 0.941 | 0.567 |
| Development | N1q_or1_rho0.4_q0.5 | CV | 200 | 0.050 | 0.055 | 0.025 | 0.025 | 0.030 | 0.946 | 0.500 |
| Development | N2_or1_rho0.4_q0.5 | CV | 500 | 0.054 | 0.048 | 0.040 | 0.014 | 0.008 | 0.932 | 0.741 |
| Development | N3_or1_rho0.4_q0.5 | CV | 500 | 0.040 | 0.038 | 0.028 | 0.012 | 0.010 | 0.934 | 0.700 |
| E4 + E5 pooled | ALT_or1.35_rho0.4_q0.5 | CV | 200 | 0.555 | 0.580 | 0.505 | 0.050 | 0.075 | 0.881 | 0.910 |
| E4 + E5 pooled | ALT_or1.5_rho0.4_q0.5 | CV | 200 | 0.895 | 0.885 | 0.850 | 0.045 | 0.035 | 0.674 | 0.950 |
| E4 + E5 pooled | ALT_or2_rho0.4_q0.5 | CV | 200 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.702 | 1.000 |
| E4 + E5 pooled | N0_or1_rho0.4_q0.5 | CV | 500 | 0.054 | 0.066 | 0.042 | 0.012 | 0.024 | 0.954 | 0.778 |
| E4 + E5 pooled | N1_or1_rho0.4_q0.5 | CV | 500 | 0.050 | 0.064 | 0.032 | 0.018 | 0.032 | 0.953 | 0.640 |
| E4 + E5 pooled | N1q_or1_rho0.4_q0.5 | CV | 500 | 0.066 | 0.070 | 0.056 | 0.010 | 0.014 | 0.961 | 0.848 |
| E4 + E5 pooled | N2_or1_rho0.4_q0.5 | CV | 500 | 0.058 | 0.044 | 0.034 | 0.024 | 0.010 | 0.955 | 0.586 |
| E4 + E5 pooled | N3_or1_rho0.4_q0.5 | CV | 500 | 0.054 | 0.050 | 0.040 | 0.014 | 0.010 | 0.952 | 0.741 |
| E4 (locked primary) | ALT_or1.35_rho0.4_q0.5 | CV | 200 | 0.390 | 0.345 | 0.320 | 0.070 | 0.025 | 0.941 | 0.821 |
| E4 (locked primary) | ALT_or1.5_rho0.4_q0.5 | CV | 200 | 0.540 | 0.540 | 0.505 | 0.035 | 0.035 | 0.926 | 0.935 |
| E4 (locked primary) | ALT_or2_rho0.4_q0.5 | CV | 200 | 0.970 | 0.955 | 0.950 | 0.020 | 0.005 | 0.632 | 0.979 |
| E4 (locked primary) | N0_or1_rho0.4_q0.5 | CV | 500 | 0.054 | 0.042 | 0.038 | 0.016 | 0.004 | 0.971 | 0.704 |
| E4 (locked primary) | N1_or1_rho0.4_q0.5 | CV | 500 | 0.042 | 0.042 | 0.030 | 0.012 | 0.012 | 0.967 | 0.714 |
| E4 (locked primary) | N1q_or1_rho0.4_q0.5 | CV | 500 | 0.064 | 0.074 | 0.056 | 0.008 | 0.018 | 0.974 | 0.875 |
| E4 (locked primary) | N2_or1_rho0.4_q0.5 | CV | 500 | 0.058 | 0.046 | 0.040 | 0.018 | 0.006 | 0.972 | 0.690 |
| E4 (locked primary) | N3_or1_rho0.4_q0.5 | CV | 500 | 0.058 | 0.050 | 0.042 | 0.016 | 0.008 | 0.969 | 0.724 |
| E5 (locked secondary) | N0_or1_rho0.4_q0.5 | CV | 200 | 0.065 | 0.055 | 0.035 | 0.030 | 0.020 | 0.941 | 0.538 |
| E5 (locked secondary) | N1_or1_rho0.4_q0.5 | CV | 200 | 0.040 | 0.040 | 0.020 | 0.020 | 0.020 | 0.919 | 0.500 |
| Development | ALT_or1.35_rho0.4_q0.5 | LR | 200 | 0.705 | 0.710 | 0.640 | 0.065 | 0.070 | 0.818 | 0.908 |
| Development | ALT_or1.5_rho0.4_q0.5 | LR | 200 | 0.930 | 0.925 | 0.905 | 0.025 | 0.020 | 0.718 | 0.973 |
| Development | ALT_or2_rho0.4_q0.5 | LR | 200 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | — | 1.000 |
| Development | N0_or1_rho0.4_q0.5 | LR | 500 | 0.046 | 0.054 | 0.032 | 0.014 | 0.022 | 0.942 | 0.696 |
| Development | N1_or1_rho0.4_q0.5 | LR | 500 | 0.058 | 0.054 | 0.036 | 0.022 | 0.018 | 0.948 | 0.621 |
| Development | N1q_or1_rho0.4_q0.5 | LR | 200 | 0.035 | 0.045 | 0.030 | 0.005 | 0.015 | 0.962 | 0.857 |
| Development | N2_or1_rho0.4_q0.5 | LR | 500 | 0.054 | 0.056 | 0.036 | 0.018 | 0.020 | 0.940 | 0.667 |
| Development | N3_or1_rho0.4_q0.5 | LR | 500 | 0.046 | 0.042 | 0.022 | 0.024 | 0.020 | 0.948 | 0.478 |
| E4 + E5 pooled | ALT_or1.35_rho0.4_q0.5 | LR | 200 | 0.730 | 0.720 | 0.660 | 0.070 | 0.060 | 0.842 | 0.904 |
| E4 + E5 pooled | ALT_or1.5_rho0.4_q0.5 | LR | 200 | 0.960 | 0.930 | 0.925 | 0.035 | 0.005 | 0.728 | 0.964 |
| E4 + E5 pooled | ALT_or2_rho0.4_q0.5 | LR | 200 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | — | 1.000 |
| E4 + E5 pooled | N0_or1_rho0.4_q0.5 | LR | 500 | 0.024 | 0.040 | 0.020 | 0.004 | 0.020 | 0.965 | 0.833 |
| E4 + E5 pooled | N1_or1_rho0.4_q0.5 | LR | 500 | 0.066 | 0.060 | 0.052 | 0.014 | 0.008 | 0.973 | 0.788 |
| E4 + E5 pooled | N1q_or1_rho0.4_q0.5 | LR | 500 | 0.082 | 0.080 | 0.068 | 0.014 | 0.012 | 0.971 | 0.829 |
| E4 + E5 pooled | N2_or1_rho0.4_q0.5 | LR | 500 | 0.048 | 0.054 | 0.038 | 0.010 | 0.016 | 0.978 | 0.792 |
| E4 + E5 pooled | N3_or1_rho0.4_q0.5 | LR | 500 | 0.042 | 0.044 | 0.032 | 0.010 | 0.012 | 0.967 | 0.762 |
| E4 (locked primary) | ALT_or1.35_rho0.4_q0.5 | LR | 200 | 0.380 | 0.395 | 0.335 | 0.045 | 0.060 | 0.922 | 0.882 |
| E4 (locked primary) | ALT_or1.5_rho0.4_q0.5 | LR | 200 | 0.620 | 0.570 | 0.530 | 0.090 | 0.040 | 0.891 | 0.855 |
| E4 (locked primary) | ALT_or2_rho0.4_q0.5 | LR | 200 | 0.970 | 0.970 | 0.955 | 0.015 | 0.015 | 0.557 | 0.985 |
| E4 (locked primary) | N0_or1_rho0.4_q0.5 | LR | 500 | 0.052 | 0.044 | 0.038 | 0.014 | 0.006 | 0.971 | 0.731 |
| E4 (locked primary) | N1_or1_rho0.4_q0.5 | LR | 500 | 0.046 | 0.038 | 0.030 | 0.016 | 0.008 | 0.975 | 0.652 |
| E4 (locked primary) | N1q_or1_rho0.4_q0.5 | LR | 500 | 0.060 | 0.066 | 0.048 | 0.012 | 0.018 | 0.974 | 0.800 |
| E4 (locked primary) | N2_or1_rho0.4_q0.5 | LR | 500 | 0.064 | 0.064 | 0.050 | 0.014 | 0.014 | 0.973 | 0.781 |
| E4 (locked primary) | N3_or1_rho0.4_q0.5 | LR | 500 | 0.060 | 0.056 | 0.042 | 0.018 | 0.014 | 0.970 | 0.700 |
| E5 (locked secondary) | N0_or1_rho0.4_q0.5 | LR | 200 | 0.060 | 0.050 | 0.045 | 0.015 | 0.005 | 0.966 | 0.750 |
| E5 (locked secondary) | N1_or1_rho0.4_q0.5 | LR | 200 | 0.030 | 0.040 | 0.025 | 0.005 | 0.015 | 0.951 | 0.833 |

## 8. N1 decision experiment (rule R-A)

| set | name | form | NH1 | T1 | T2 | T2c |
|---|---|---|---|---|---|---|
| Development | ALT | detrended | 0.860 | 0.880 | 0.900 | 0.890 |
| Development | ALT | raw (plan-literal) | 0.830 | 0.860 | 0.910 | 0.900 |
| Development | N0 | detrended | 0.020 | 0.040 | 0.025 | 0.030 |
| Development | N0 | raw (plan-literal) | 0.025 | 0.035 | 0.050 | 0.040 |
| Development | N1 | detrended | 0.045 | 0.055 | 0.070 | 0.065 |
| Development | N1 | raw (plan-literal) | 0.075 | 0.100 | 0.100 | 0.075 |
| E4 (locked primary) | ALT | detrended | 0.530 | 0.530 | 0.560 | 0.500 |
| E4 (locked primary) | ALT | raw (plan-literal) | 0.590 | 0.650 | 0.590 | 0.630 |
| E4 (locked primary) | N0 | detrended | 0.030 | 0.040 | 0.040 | 0.030 |
| E4 (locked primary) | N0 | raw (plan-literal) | 0.025 | 0.035 | 0.040 | 0.055 |
| E4 (locked primary) | N1 | detrended | 0.030 | 0.040 | 0.045 | 0.040 |
| E4 (locked primary) | N1 | raw (plan-literal) | 0.070 | 0.085 | 0.090 | 0.075 |

