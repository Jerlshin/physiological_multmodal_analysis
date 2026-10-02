# Dataset-specific search and screening log

**Search date/cutoff:** 2026-10-01. This is an auditable, bounded evidence review, not a claim of complete citation indexing. The preceding [landscape search log](../../dataset_landscape/evidence/search_log.md), selection, comparison/risk/selection documents, dataset notes and evidence files were reviewed first. This stage pursued BBBD lineage and primary methods rather than reopening dataset selection.

## Search strategy and recorded query families

Web search was supplemented by the descriptor bibliography, original-paper references/methods, the author lab's publication list, NEMAR associated citations, Crossref publisher deposits, official GitHub code/API and OSF resource APIs. Queries used British/American spelling and antecedent titles, not just the final dataset name.

| Family | Representative executed queries / pathways | Screening result |
|---|---|---|
| Dataset identity | `"Brain, Body, and Behavior Dataset"`; `"Brain, Body, and Behaviour Dataset"`; `"BBBD" EEG`; `"bbbd.pythonanywhere.com"` | Descriptor/preprint, official site/repository, corrected release, mirrors, P04 and P05 lead |
| Eye antecedent | Exact PNAS 2021 title; author names plus synchrony/learning; original references and OSF m7gj4/fjxaq | P01 confirmed; classroom/home cohorts distinguished from released experiments |
| Cardiac antecedent | Exact Cell2021 title; `"osf.io/mhvy7" classification learning` | P02 full PDF/STAR Methods; only its Experiment 2 maps to BBBD |
| Multimodal antecedent | Exact PNASNexus2022 title; `"osf.io/d4k3q" EEG`; author publication list | P03 confirmed; code index and actual LOSO/video-holdout methods identified |
| State/trait outcome | BBBD+Madsen+learning/traits; lab publication list | P04 original2025 paper, code and 2026 poster; title variants deduplicated |
| Modern representations | BBBD / full name with `contrastive`, `self-supervised`, `foundation`, `distillation`, `fusion`, `model` | No confirmed modern-method reuse in inspected originals; acronym noise substantial. Negative evidence is provisional. |
| New classifier | Exact `EEG Based Classification of Attentive and Distracted States During Video Based Learning`; Rathnayake/Subasingha; DOI11499773 | P05 bibliographic identity verified in publisher-deposited Crossref; IEEE full text unavailable; secondary snippets not used for method/results extraction |
| Related collections | Exact2024 bidirectional brain–body title;2025 explanation-video study;2025 dynamics preprint;2026 auditory narrative preprint |2024 audio collection and 2025 classroom study distinct; inaccessible newer full preprints retained as adjacent-method leads |
| Independent replications | `Using synchronized eye movements to assess attentional engagement`; `Processing of the same narrative stimuli ...` | Original methods identify Zhejiang eye cohort and fMRI movie cohorts, not BBBD |
| Supplements | Exact DOI + supplement filename; PMC original links, PNAS publisher endpoint, web retrieval and public HTTP requests | P01/P03/P04 separate supplements not retrieved; no content inferred from filenames. P02 STAR Methods available within full PDF. |

## Screening disposition

**Confirmed same collection:** P01, P02(video subset), P03, P04. **Resource descriptor:** S01; bioRxiv2025 version deduplicated. **Duplicate dissemination:** P04 CNS 2026 poster/abstract. **Unresolved potential reuse:** P05. **Related independent studies:** R01, R04, R05 and Adler et al.2025. **Methodological ancestors, no established shared participants:** Cohen et al.2018, Ki et al.2016. Citations alone do not establish data reuse.

## Access and reproducibility checks

Public original article HTMLs and NSF-hosted original PDFs were read; a Cell PDF page was rendered to check extracted material visually. The GitHub archive resolved to commit 5109afa0fd70c407b869108106f5808c6b0cc33c. Source hashes and reference-table aggregates are retained. OSF P01/P02/P03/P04 top-level indexes were retrievable; P04 code listing explicitly included Figure_1.m, Figure_2.m, Figure_3.m and helpers. No scientific code was executed.

Separate PMC supplementary links returned HTML challenges masquerading as PDF downloads; web retrieval also failed. PNAS supplement publisher returned403. Newer bioRxiv full-text requests returned403/429; no automated retry loop was used. Author-hosted2026 dynamics talk was available and identifies adjacent temporal-modeling work, but is not a substitute for validating that preprint's full methods or cohort overlap. Original IEEE content was unavailable; Crossref supplied citation metadata, not an abstract or methods. Zenodo API returned403 in this stage; prior landscape release metadata is preserved and clearly distinguished from download verification.

## What would strengthen completeness

Obtain P05 and separate supplements; inspect forward citations through a bibliographic database with a dated export; check theses and newly indexed preprints; compare author OSF input hashes and corrected 1.1 IDs. This stage used search-engine/author/reference traversal rather than a complete Scopus/Web of Science/Semantic Scholar citation-graph export. Therefore “not found” means not verified in this bounded search, **never “has never been done.”** [INF-034]
