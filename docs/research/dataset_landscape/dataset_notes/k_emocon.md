# K-EmoCon

**Disposition: naturalistic social-affect comparator, with dyadic dependence and access limits.**

Sources: [Park et al., Scientific Data 2020](https://doi.org/10.1038/s41597-020-00630-y); [Zenodo](https://zenodo.org/records/3931963); [author code](https://github.com/Kaist-ICLab/K-EmoCon_SupplementaryCodes).

| Item | Evidence / limitation |
|---|---|
| Cohort/protocol/duration | 32 participants in 16 paired debates, 172.92 min dyadic interaction (~5.76 participant-hours if both people counted). Exact age/sex composition NV in this pass. Debates induce spontaneous social behavior; one visit/person. |
| Modalities/rates | Single-channel consumer EEG, E4 physiological streams, cardiac measures and audiovisual recordings. E4 native BVP 64/EDA 4/temperature 4/acceleration 32 Hz; EEG/cardiac per-device rates require original headers. |
| Labels | Self, partner and external-observer emotion annotations at 5 s intervals after reviewing recordings. Multiple perspectives are a distinctive asset; they measure different judgments rather than interchangeable ground truth. |
| Raw/sync/IDs | Raw sensor/audio/video plus annotations and processing utilities; timestamp alignment, quantified residuals NV. Person/dyad IDs; no BIDS verified. |
| Missing/artifacts/controls | Speech, movement and social roles strongly affect signals; sensor dropouts/usable overlap require inventory. Conversational interaction is not controlled video elicitation. |
| Access/license/size/code | Restricted/request Zenodo route; exact current data license and bytes NV. Official supplementary code supports annotation/sensor processing. |

Supports interpersonal affect, disagreement among raters and social physiological associations. Cannot claim independent evidence of emotion from mutually dependent partner labels or generalize to population-wide affect decoding. Dyad is a minimum evaluation grouping; cross-person splitting alone may leak a partner's conversation.

At least the descriptor and one independent 2026 empirical reuse verified. [Alkhodari et al., Frontiers in Systems Neuroscience](https://doi.org/10.3389/fnsys.2026.1802891) already analyzes cardiac/HRV synchrony, speaker–listener phases and self/partner emotion associations in these 32 individuals. Full reuse count remains unresolved. Naturalistic multi-perspective affect and interpersonal synchrony are therefore occupied topics. Potential remains in annotator uncertainty and robust dyad-held-out evaluation, not simply asserting that multiple raters or modalities are novel. Small number of independent conversations and short duration weaken primary selection.
