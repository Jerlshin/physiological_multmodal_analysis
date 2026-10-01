# AMIGOS

**Disposition: established affect/social-context comparator.**

Sources: [Miranda-Correa et al., IEEE TAFFC, online 2018 / issue 2021](https://doi.org/10.1109/TAFFC.2018.2884461); [official QMUL project](https://eecs.qmul.ac.uk/mmv/datasets/amigos/); [author preprint](https://arxiv.org/abs/1702.02510). Official server intermittently inaccessible; acquisitions/terms not confirmed by a live download.

| Item | Evidence / limitation |
|---|---|
| Cohort | 40 adults, 27 men/13 women, 21–40, mean 28.3; smaller usable subsets for some streams/experiments. |
| Protocol/duration/repeats | 16 short videos and four longer films, alone and in groups; long-film participation differs from short-video cohort. Total raw/complete-case hours NV. Subject, video and social-group IDs are needed together. |
| Signals/rates | Emotiv 14-channel EEG 128 Hz, ECG and GSR from Shimmer (256 Hz in original methods), face/full-body video. Beware secondary sources that report different rates or participant counts. |
| Labels/controls | VAD, liking/familiarity, discrete emotions, personality/mood and external annotations over intervals. Social context is useful but also creates group-level dependence. |
| Data/sync/artifacts | Raw and processed physiological data/video; task alignment, exact residual sync NV. Several participant/trial losses are reported in reuse literature, with inconsistent exclusion lists; official inventory must determine exclusions. Not BIDS. |
| Access/license/size/code | Research agreement/request route; exact current license and full bytes NV. Original processing plus extensive community code; no universal standard pipeline. |

Supports affect/personality associations and differences across individual/group viewing. Unusual social context is scientifically useful. Cannot establish stable personality diagnosis, causal group effects without allocation audit, or independent generalization when group members/video segments cross splits.

The original paper already studies multimodal affect, personality, mood and social context. Reuse includes [self-supervised ECG emotion learning, ICASSP 2020](https://dihana.cps.unizar.es/proceedings/ICASSP/2020/pdfs/0003217.pdf) and [EEG authentication, 2023](https://doi.org/10.1016/j.jksuci.2023.03.019): at least three distinct empirical works including original, not a census. Generic fusion and self-supervision are occupied. Group-aware transfer, disagreement among annotation perspectives and robustness could remain useful, with a focused novelty review. Test groups and people must be genuinely unseen.

