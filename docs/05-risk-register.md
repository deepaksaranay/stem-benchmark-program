# Risk register

| # | Risk | Likelihood | Impact | Early signal | Mitigation | Owner |
|---|---|---|---|---|---|---|
| 1 | A wrong reference answer ships | Medium | Very high (the benchmark misleads the customer) | Two solutions disagree, or audit finds an error | Dual-solution gate in CI, independent review, 10% spot audit | Program owner |
| 2 | Ambiguous task wording | High | High | Strong models "fail" an easy task in different ways | Rubric "unambiguity" check, pilot of 20 tasks | Reviewers |
| 3 | Review bottleneck (one slow reviewer) | High | Medium | p90 turnaround RED, one reviewer far above the median | Rebalance the queue, add a reviewer, reviewer capacity in the plan | Program owner |
| 4 | Large quality gap between contributors | High | Medium | A contributor's first-pass rate is RED for 2 weeks | Coaching, pair with a strong contributor, review their next tasks more closely | Program owner |
| 5 | Scope or difficulty change mid-programme | Medium | High | Customer asks for "just a few more" hard tasks | Change control: written impact on plan and quality before agreeing | Program owner |
| 6 | Tasks leak into public data | Low | High | A task appears on the web | Originality check, restricted sharing, fresh variants | Program owner |
| 7 | Unit or tolerance disputes | Medium | Medium | Many `unit_error` outcomes in evaluation | Units set per task, accepted-unit table, examples in the guidelines | Reviewers |
| 8 | Schedule slip | Medium | High | Weekly accepted below target for 2 weeks | Capacity plan, early escalation with options | Program owner |
| 9 | Confidential data handled carelessly | Low | Very high | Files shared outside agreed tools | Access control, no real customer data in repositories | Program owner |

Review the register every week. Close a risk only when its signal has been gone for a while.
