# Which units are nested, and which evidence objects must stay separate?

```mermaid
flowchart TD
    C[Underlying experimental collection] --> E123[BBBD experiments 1 / 2 / 3]
    C --> C45[Shared upstream collection
doIntervention partition]
    C45 --> E4[BBBD 4: attentive different-video blocks]
    C45 --> E5[BBBD 5: repeated-video incentive setting]
    E123 --> Person[Experiment-qualified participant ID]
    E4 --> Person
    E5 --> Person
    Person --> Ses[Viewing block / ses]
    Ses --> Vid[Local stimulus ID → canonical video identity]
    Vid --> Mod[Modality file + sidecar + valid mask]
    Mod --> Win[Dependent samples / possible windows
NOT independent participants]
    C --> Hist[Historical paper cohorts
P01–P04, overlapping and differently numbered]
    C --> Rel[Corrected Zenodo 1.1 release
178 documented retained participants]
    C --> Ref[Repository reference assets
commit 5109afa, not proven ZIP-identical]
```

Sources: S01/S02/S04/S06; P01–P04. The three bottom evidence objects require explicit mappings. A paper's cohort, a reference TSV's distinct IDs and a release's usable signal subjects need not coincide. Unknown cross-experiment repeated participation is not resolved by local IDs.
