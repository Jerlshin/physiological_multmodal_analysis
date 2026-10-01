# A Multimodal Dataset for Mixed Emotion Recognition

**Disposition: valuable affect-specific alternative; access and short trials reduce its default priority.**

Sources: [Yang et al., Scientific Data, 5 August 2024](https://doi.org/10.1038/s41597-024-03676-4); [Zenodo record](https://zenodo.org/records/11194571). Archive metadata labels publication year 2023, whereas descriptor is 2024; retain both dates.

| Item | Evidence / limitation |
|---|---|
| Cohort | 80 recruited (48 women/32 men), 18–35, mean 23.06 ± 3.37; 73 retained after 7 physiological-data exclusions. Final demographics/intersection NV. |
| Protocol/duration | 32 clips, 20–30 s each: 8 positive, 8 negative, 16 mixed; four blocks with Latin-square order, baseline and arithmetic washouts. Approx. 13.0–19.5 h stimulus exposure if all 73 × 32 trials retained; actual usable duration NV. |
| Modalities/rates | DSI-24 EEG: 21 recorded channels at 300 Hz, 18 used in analysis; GSR 4 Hz, PPG 100 Hz, face video 30 fps. |
| Data/sync/IDs | Raw and time-aligned archives; EEG/peripheral/camera triggers/timestamps, no quantified residual alignment. Subject and trial IDs, one session/person, no BIDS verified. |
| Outcomes | Separate positive/negative PANAS and VAD, amusement/disgust ratings after clips. Mixed affect is assessed rather than presumed from clip labels. |
| Artifacts/controls | Physiological exclusions, headset/contact artifacts, short autonomic windows; clip/valence blocks and arithmetic washouts confound temporal dynamics. Residual missingness inventory NV. |
| Access/license/size/code | Restricted Zenodo request; no files/bytes exposed in public API, license not supplied there. Detailed descriptor; complete executable preprocessing package NV. |

Supports co-occurring positive/negative self-reports and relationships with physiology/face. This is more distinctive than ordinary positive/negative valence decoding. Cannot infer second-by-second mixed emotion or general psychopathology from post-clip ratings, nor establish universal emotional categories.

At least one descriptor with multimodal/SVM mixed-emotion classification verified; no additional independent empirical reuse verified. The obvious three-class benchmark already exists. Opportunities include label disagreement, person-and-stimulus transfer and modality reliability; no guarantee of first-of-kind novelty. Subject-independent testing is feasible at N=73 before quality loss; clip-held-out testing is required to distinguish person-specific affect from stimulus recognition. Access, released raw coverage, synchronization and the original baseline split remain verification items.

