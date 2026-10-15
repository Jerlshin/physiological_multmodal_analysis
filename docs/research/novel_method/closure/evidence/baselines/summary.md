# Baseline validation summary (synthetic outcomes; rule R-K)

Mean held-out S_item over IRT-M2:

| model | development/ALT3 | development/N0 | locked_pooled/ALT3 | locked_pooled/N0 | locked_pooled/N2 | locked_pooled/N2s |
|---|---|---|---|---|---|---|
| B3-catboost | -0.0002 | -0.0003 | -0.0014 | -0.0000 | 0.0035 | 0.0133 |
| B3-elastic-net | 0.0009 | -0.0025 | -0.0008 | -0.0006 | -0.0021 | 0.0141 |
| B3-gpboost | -0.0015 | 0.0002 | -0.0003 | 0.0003 | -0.0000 | 0.0022 |
| B3-item-gpboost-crossed-RE | 0.0195 | 0.0024 | 0.0176 | 0.0011 | 0.0033 | nan |
| B3-item-lightgbm-residual | 0.0163 | -0.0023 | 0.0174 | -0.0122 | 0.0047 | nan |
| B3-lightgbm | -0.0013 | -0.0010 | -0.0010 | -0.0006 | 0.0034 | 0.0063 |
| B3-random-forest | -0.0003 | -0.0012 | -0.0013 | -0.0016 | 0.0040 | 0.0088 |
| B3-tabpfn-v2 | -0.0022 | -0.0027 | -0.0004 | -0.0007 | -0.0013 | 0.0078 |
| B4a-mantis8m-anchored (A4-FM) | 0.0221 | -0.0077 | 0.0276 | -0.0064 | -0.0007 | nan |
| B4a-mantisv2-anchored (A4-FM) | 0.0226 | -0.0067 | 0.0249 | -0.0098 | 0.0017 | nan |
| B4a-mantisv2-video | 0.0014 | 0.0001 | -0.0015 | 0.0011 | -0.0009 | 0.0049 |
| B4a-moment-anchored (A4-FM) | 0.0003 | -0.0104 | 0.0116 | -0.0058 | -0.0029 | nan |
| B4a-moment-video | 0.0007 | -0.0008 | -0.0019 | -0.0001 | -0.0026 | 0.0028 |
| B4b-attention-MIL | 0.0001 | 0.0000 | 0.0001 | -0.0001 | 0.0040 | 0.0097 |
| B4b-item-text-attention-MIL | 0.0147 | -0.0029 | 0.0157 | -0.0124 | 0.0021 | nan |
| B4b-item-text-attention-linear | 0.0166 | 0.0003 | 0.0199 | -0.0019 | 0.0106 | nan |
| B7-TCN-encoder (A4) | 0.0329 | 0.0002 | 0.0376 | -0.0075 | 0.0045 | nan |
| B9-Lalle | -0.0261 | -0.0690 | -0.0643 | -0.0829 | -0.0960 | nan |
| CAIRN-linear-dt (B6) | 0.0420 | -0.0047 | 0.0463 | -0.0084 | 0.0032 | nan |
| IRT-whole (B5) | -0.0026 | 0.0001 | -0.0020 | -0.0083 | 0.0139 | 0.0092 |


Verdicts:

| index | kind | negative_control | positive_control_scenario | positive_control | deterministic | fold_safe |
|---|---|---|---|---|---|---|
| B3-catboost | whole-video | True | N2 | False | True | True |
| B3-elastic-net | whole-video | True | N2 | False | True | True |
| B3-gpboost | whole-video | True | N2 | False | True | True |
| B3-item-gpboost-crossed-RE | anchored/item-level | True | ALT3 | True | True | True |
| B3-item-lightgbm-residual | anchored/item-level | True | ALT3 | True | True | True |
| B3-lightgbm | whole-video | True | N2 | False | True | True |
| B3-random-forest | whole-video | True | N2 | False | True | True |
| B3-tabpfn-v2 | whole-video | True | N2 | False | True | True |
| B4a-mantis8m-anchored (A4-FM) | anchored/item-level | True | ALT3 | True | True | True |
| B4a-mantisv2-anchored (A4-FM) | anchored/item-level | True | ALT3 | True | True | True |
| B4a-mantisv2-video | whole-video | True | N2 | False | True | True |
| B4a-moment-anchored (A4-FM) | anchored/item-level | True | ALT3 | True | True | True |
| B4a-moment-video | whole-video | True | N2 | False | True | True |
| B4b-attention-MIL | whole-video | True | N2 | False | True | True |
| B4b-item-text-attention-MIL | anchored/item-level | True | ALT3 | True | True | True |
| B4b-item-text-attention-linear | anchored/item-level | True | ALT3 | True | True | True |
| B7-TCN-encoder (A4) | anchored/item-level | True | ALT3 | True | True | True |
| B9-Lalle | anchored/item-level | True | ALT3 | False | nan | nan |
| CAIRN-linear-dt (B6) | anchored/item-level | True | ALT3 | True | nan | nan |
| IRT-whole (B5) | whole-video | True | N2 | True | nan | nan |