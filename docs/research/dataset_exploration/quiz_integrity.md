# Quiz integrity

**Gate follow-up — 2026-10-02:** All 12,470 rows still reconstruct against supplied keys. Exp.2 content mapping is verified, but response mapping is unverified and historical scores disagree. Its domain/memory targets are now quarantined from scientific behavioral use; this table remains an encoding audit. [Evidence and verdict](gate_closure.md).

**EMPIRICALLY VERIFIED IN THIS AUDIT.** All 12,470 item-row scores reconstruct from the supplied answer selections and answer keys with absolute tolerance 1e-8. Experiments 1–2 use equality of single answer/key. Experiments 3–5 use `number of selected correct options / number of correct options`. Extra wrong selections do **not** lower that partial score. In 4–5, `is_correct` requires exact selected/key set equality. Partial and exact outcomes must remain separate; fractional credit is not automatically a binomial count.

| experiment | rows | quiz_people | duplicate_item_rows | score_mismatches | correctness_mismatches | score_one_with_wrong_selection |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 3286 | 31 | 0 | 0 | 0 | 0 |
| 2 | 3604 | 34 | 0 | 0 | 0 | 0 |
| 3 | 2304 | 32 | 2 | 0 | 0 | 63 |
| 4 | 1548 | 43 | 0 | 0 | 0 | 16 |
| 5 | 1728 | 48 | 0 | 0 | 0 | 19 |

There are 10 unmatched participant-level phenotype records: [complete ledger](evidence/participant_quiz_join_ledger.csv). They are surplus relative to the release participant/signal keys, not reassigned by row order. Signal-participant to metadata and participant to aggregate quiz are one-to-one at person/video scope; person/video to item responses is one-to-many. Repeated viewing creates one outcome potentially linked to two exposures, not two independent outcomes. Exact join validations reject ambiguous video mappings.

**Quarantine:** Exp.3 `sub-01`, stim03, question11 occurs twice with different answers/scores, while question12 is absent. The complete 12-row aggregate sums correctly but has only 11 distinct question numbers. Its person/video outcome is excluded from valid-outcome counts. Neither row was silently relabeled or removed from source. Exp.5 sub-09 is absent from corrected participant and quiz source keys; no local renumbering was attempted.

Video totals reconstruct. Exp.4/5 aggregate partial totals have 66 differences above 1e-8, all no greater than 0.00003333, consistent with four-decimal serialization; none exceed 0.000051. Exact totals match supplied `total_correct`. Exp.1–3 aggregates match at numerical precision. [Aggregate comparison](evidence/quiz_aggregate_comparison.parquet).

**OPEN QUESTION:** supplied key consistency is not an independent reconstruction from original randomized-option response logs. Original publications' internally used labels cannot be inferred from the current release. The release's no-penalty partial-score rule contradicts the penalty description retained in the historical review/P01 methods; neither is silently made consistent with the other.
