# Metrics and SLA

All formulas below are exactly what `benchmark/metrics.py` computes.

| Metric | Definition | Why it matters | Target (demo) |
|---|---|---|---|
| **First-pass acceptance rate** | Tasks accepted at the first review / tasks that had a first review | Quality at the source. Low = rework cost and slow delivery | 75% |
| **Rework rate** | Reviewed tasks that needed at least one rework cycle / reviewed tasks | Hidden cost of low quality | watch |
| **Review turnaround (median, p90)** | Hours from submission to first review. p90 = nearest-rank 90th percentile | Contributors wait. Long tails hide a bottleneck that the average hides | p90 <= 36 h |
| **Weekly accepted tasks** | Tasks with a final "accepted" status, grouped by ISO week of acceptance | Throughput against the plan | 30 per week |
| **Contributor first-pass rate** | First-pass rate for each contributor | Where to coach | 75% |
| **Reviewer median turnaround** | Median first-review time for each reviewer | Where the queue is stuck | watch |

Tasks still waiting for a first review are counted as "in review", not as failures. The final, partial
week is shown without a status.

## RAG status
- Higher is better (acceptance, throughput): GREEN at or above target, AMBER within 10% below, RED below that.
- Lower is better (turnaround): GREEN at or under target, AMBER within 10% above, RED above that.
- The 10% margin is `amber_margin` in `data/program_config.json`.

## Reporting
Weekly report to the customer: progress against plan, the metrics above, risks and the decisions needed.
Every RED metric comes with a cause and an action, never just the colour.

## Cautions
- Do not chase first-pass rate by lowering the bar. Pair it with the spot-audit error rate.
- Do not compare contributors on small samples: with fewer than 10 reviews, one task moves the rate a lot.
- Averages hide problems. Look at the median, the tail and the breakdown by person.
