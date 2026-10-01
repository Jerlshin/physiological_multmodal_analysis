# WEMAC

**Disposition: valuable women-focused affect resource; does not provide simultaneous brain/eye/body breadth.**

Sources: [Scientific Data 2024 descriptor](https://doi.org/10.1038/s41597-024-04002-8); [official physiological data DOI](https://doi.org/10.21950/FNUHKE); [labels](https://doi.org/10.21950/RYUCLV); [author processing repository](https://github.com/BINDI-UC3M/wemac_dataset_signal_processing). The repository cites a 2022 preprint/release; the 2024 descriptor does not establish a wholly new cohort.

| Item | Evidence / limitation |
|---|---|
| Cohort | 144 women initially selected, 100 retained after VR sickness, discomfort and technical problems; Spanish-speaking, ages 20–77, mean 39.92 ± 14.26. Attrition is a substantive selection mechanism. |
| Protocol/duration | Two batches, 14 selected clips each; approximately 1–1.5 h protocol/person, not audited retained waveform hours. VR viewing then spoken report/annotation; one session/person. |
| Signals/rates | BVP, GSR and skin temperature plus speech. Native acquisition rates require official files/table audit; no EEG/ECG/eye recording established. Speech occurs **after** stimuli, so it is not a fully simultaneous stream with viewing physiology. |
| Labels/controls | Twelve categorical emotions, modified SAM dimensions, liking/familiarity; fear/non-fear emphasis. Stimulus validation is not validation of real violence detection. |
| Raw/sync/IDs | Raw/derived physiology, speech features and questionnaires described; subject/clip/batch IDs. **Raw audio is explicitly withheld** for privacy; audio features are released, additional embeddings requestable. Cross-phase alignment is semantic rather than moment-to-moment. Full missing-data map and BIDS status not established. |
| Access/license/size/code | Official Dataverse DOIs found, but repository access was denied to the retrieval tool; file license/bytes not verified. Author speech-processing code verified on GitHub; full physiological processing reproducibility not audited. Treat acquisition readiness as unresolved. |

Supports affect/fear elicitation and cross-phase physiology–speech relationships over a wider adult age range. Cannot support detecting actual gender-based violence, identify victim status, or infer deployment safety from laboratory clips. Neither all-female recruitment nor a stated application makes labels a real-world violence reference.

At least descriptor verified; related BINDI fear/affective sensing work predates it, but exact cohort overlap/reuse count remains unverified. Potential concerns age, individual variation and nonresponse; obvious fear classification is already an explicit motivation. Retain as a domain comparator, not a reason to infer a sensitive clinical/social outcome.
