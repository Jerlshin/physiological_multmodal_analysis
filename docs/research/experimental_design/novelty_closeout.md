# M05 — Novelty closeout for G01-R

2026-10-04. A targeted search was delegated to a parallel investigation. The lead investigator then re-checked the items this document relies on against saved source text: the P01 quotes, the S01 E4 quote, the P03 43/92 statement, the P05 abstract and the Chen 2026 abstract quote. Notes are in [delegated audit notes](evidence/external/delegated_audit_notes.md).

Access tiers: **FT** = relevant full-text sections read; **AB** = abstract or index only; **NA** = not accessible. This is a targeted closeout, not a systematic review. "Not found" does not mean "does not exist".

## Verdict

**No retrieved work answers G01-R's estimand.** That estimand has three parts:

1. Held-out **incremental** skill over content, permissible traits and measurement quality.
2. For new learners, with person-grouped evaluation.
3. Decomposed into reference-free and synchrony information, content transfer, and stable versus video-specific information, against a criterion with stated reliability.

The novelty is a **specific empirical-measurement result**, not a method. Two items narrow it further, and one supplies chronology.

| Item | What it establishes (tier) | Consequence for G01-R |
|---|---|---|
| **P01 at-home webcam cohort** (Madsen 2021, PNAS) | Held-out quiz prediction already exists. LOO-CV eye-ISC predicts test score with "14.6 ± 16.9% … equivalent to 1.75 of 12 questions, and outperforms a naïve predictor based on mean performance" (FT). Separate webcam cohort, not BBBD | **Narrows.** We may not claim "first held-out physiological prediction of quiz performance". What remains open: incremental over content, traits and quality; sensor decomposition; content transfer; criterion reliability; reference-free versus synchrony |
| **Chen et al. 2026**, NeuroImage 338:122062 | EEG IS-RSA in online physics learning: frontal theta similarity relates to between-person outcome differences; event-level alpha similarity relates negatively to event outcomes only for low prior knowledge (AB; full text NA after publisher 403/CAPTCHA) | **Narrows.** The between-person versus event-level contrast and prior-knowledge moderation are occupied. G01-R's state/person decomposition must be framed as a *predictive-validity* decomposition and cite Chen. BBBD cannot address prior knowledge. Full methods remain a **U** risk |
| **P05** Rathnayake et al., IEEE SCSE 2026 | Confirmed BBBD reuse: E2 EEG, stim01, attentive versus distracted, 4 s windows, LOSO, SVM accuracy 0.60 (AB, verified) | No collision: the target is an order-confounded condition, not the quiz |
| **Silvan Ortubay, Parra & Madsen**, EMBC 2025 | Face video predicts eye-movement ISC in unseen subjects "without needing reference data from an attentive group" (AB) | Occupies the *motivation* for reference-free attention measurement. Its target is ISC, not quiz score. Cite in the H2a framing |
| P03 (FT) | Quiz data "available for 43 of the 92 subjects", i.e. E4. The paper does not mention the E5 intervention; its quiz analyses are in-sample correlations | Unchanged: held-out incremental evaluation is absent |
| Peng et al. 2026, Neuron (AB) | fMRI + eye; neural alignment "jointly mediated learning gains"; explanatory | Context only |
| OpenAlex 2025+ citers of S01/P01–P04 | Only NEMAR re-releases, P05 and a review reuse BBBD | No newer BBBD quiz-prediction study found. The NEMAR E4 metadata repeats the "session 2 distracted" README error |

## Methodological anchors adopted (L, AB unless noted)

- **Bates, Hastie & Tibshirani**, JASA 2024: CV estimates the average error of the procedure, and naive CV intervals can undercover. Nested CV is proposed; its algorithm and bias correction were read in full text (FT) and implemented in the [simulation](evidence/precision_simulation.py).
- **Varoquaux**, NeuroImage 2018: CV error bars are large at n ≈ 100.
- **Poldrack, Huckins & Varoquaux**, JAMA Psychiatry 2020: no in-sample fit as evidence of prediction; prefer MAE; caution below several hundred observations. → MAE is a reported metric, and the claim is framed as bounded.
- **Judd, Westfall & Kenny** 2012; **Westfall, Kenny & Judd** 2014: stimuli as a random factor. Power for content generalization plateaus with the number of stimuli. → B is not confirmatory.
- **Cameron, Gelbach & Miller** 2008; **MacKinnon & Webb** 2017: over-rejection with few clusters. → No content-level cluster inference with 8 videos.
- **Hedge, Powell & Sumner** 2018: robust group effects do not imply reliable individual differences. → Criterion reliability is reported. **Funder & Ozer** 2019: effect-size interpretation for r.

## Residual novelty risks (U)

1. Chen 2026 full methods are unread. The authors are reachable; contacting them requires user authorization.
2. A conference paper or preprint outside the indexed sources may already report incremental held-out quiz validity on BBBD.
3. A reviewer may judge a careful bounded estimate, especially a null, as insufficient for a Q1 venue without external replication ([external validation](external_validation.md)).

None of these blocks baseline implementation. Risk 3 shapes the publication route.
