# Program charter (template with fictional numbers)

> This is a worked example of how a customer request becomes an execution plan.
> The customer and every number below are **invented** for practice.

## 1. Customer request (fictional)
"An AI lab asks for 500 original, verifiable physics and mathematics problems with exact reference answers,
to measure how well its model reasons. Delivery in 6 weeks."

## 2. Objective
Deliver 500 accepted tasks that a model can be graded on automatically, with no ambiguity and no wrong answers.

## 3. Scope
| In scope | Out of scope |
|---|---|
| Original problems with one numeric or closed-form answer | Multi-step proofs that need human grading |
| Two independent reference solutions per task | Tasks copied from textbooks or the web |
| Automatic grader with unit handling and tolerance | Training the customer's model |
| Weekly status report and final delivery report | Tasks needing special lab equipment |

Mix: 50% physics, 50% mathematics. Difficulty: 30% easy, 40% medium, 30% hard (hard = a strong model fails
more often than it succeeds).

## 4. Acceptance criteria (what "done" means)
1. Every delivered task has two independent solutions that agree (`python -m benchmark validate-tasks`).
2. Every task has a unit (or is dimensionless) and a stated tolerance.
3. Spot audit of 10% of tasks by a second reviewer finds fewer than 2% with an error.
4. Delivery report is attached (see `reports/delivery_report.md`).

## 5. Plan
| Week | Goal | Output |
|---|---|---|
| 1 | Kick-off, guidelines agreed, pilot of 20 tasks | Pilot review with the customer, feedback applied |
| 2-5 | Production, about 110 accepted tasks per week | Weekly report |
| 6 | Final audit, fixes, delivery | Delivery report, sign-off |

Capacity check: 110 per week at a 75% first-pass rate needs about 147 submissions per week, so about 8
contributors at roughly 18 tasks each, and reviewer capacity of 147 reviews per week.

## 6. Roles (RACI)
R = does the work, A = accountable, C = consulted, I = informed

| Activity | Program owner | Contributors | Reviewers | Customer |
|---|---|---|---|---|
| Agree scope and criteria | A/R | I | C | C |
| Write guidelines and rubric | A/R | C | C | I |
| Create tasks | A | R | I | I |
| Review tasks | A | I | R | I |
| Weekly report | A/R | I | C | I |
| Final delivery sign-off | R | I | I | A |

## 7. Cadence
Daily queue check (backlog, oldest unreviewed task). Weekly report and call with the customer.
Weekly calibration session for reviewers (see `03-reviewer-rubric.md`).

## 8. Change control
Any change to scope, difficulty mix, tolerance or deadline: written request, impact on plan and quality
stated, customer approves before work changes. Nothing changes by chat message alone.

## 9. Escalation
Metric is RED for two weeks, or a delivery date is at risk: owner informs the customer within one working
day with the cause, the options (more reviewers, fewer tasks, later date) and a recommendation.
