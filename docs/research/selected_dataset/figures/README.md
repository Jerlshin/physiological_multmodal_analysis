# Scientific figures

Each figure answers a concrete reconstruction question; none encodes measured waveform quality.

| Figure | Question answered | Evidence / limitation |
|---|---|---|
| [Experiment structure](experiment_structure.svg) | Which protocols and signals belong to each experiment? | S01–S06; design-level availability, not complete cases |
| [Prior-work coverage](prior_work_coverage.svg) | Which modalities/tasks/validation types already have published evidence? | P01–P05; explicit unknowns, no novelty proof from empty cells |
| [Signal provenance](protocol_and_signal_provenance.md) | Which transformations separate native signals, processed signals, features and outcomes? | S01/S06; conceptual order, actual execution provenance unresolved |
| [Dataset organization](dataset_organization.md) | What are the nested units and historical/release/reference evidence objects? | S01–S06/P01–P04; participant mappings still need archive audit |

SVGs are standalone editable vector artifacts. Mermaid source is retained for the two structural diagrams. The [stimulus table](../evidence/stimuli.csv) supports canonical video identity and overlap checks. Both SVGs were XML-validated and their full raster previews were visually inspected. Quick Look cropped the initial wide thumbnails; temporary square-canvas previews confirmed the complete layout without changing the delivered SVG geometry.
