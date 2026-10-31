# Reviewer rubric

Score each dimension 0 (fails), 1 (needs work) or 2 (good).

| Dimension | Question |
|---|---|
| Correctness | Is the reference answer right? Did you re-derive it independently? |
| Unambiguity | Could a careful expert reasonably read the question differently? |
| Verifiability | Are both solutions present, independent and in agreement? Unit and tolerance set? |
| Difficulty fit | Does the difficulty label match what a strong solver would experience? |
| Originality | Is it clearly not a copy of a known problem? |

## Decision
| Result | Rule |
|---|---|
| **Accept** | No 0, and total at least 8 of 10 |
| **Rework** | Any 1 that can be fixed, or total 5 to 7. Write what to change, as a specific instruction |
| **Reject** | Correctness 0 that cannot be fixed, or not original |

A wrong answer key is never "good enough". If Correctness is 0, the task does not ship.

## Giving feedback
- Say what is wrong, why, and what a fix looks like.
- One clear instruction per point. Avoid "make it better".
- Same standard for everyone. Praise specific things that were done well.

## Calibration (weekly, 30 minutes)
Reviewers all score the same 3 tasks, compare, and discuss every difference. Record any new rule in the
guidelines. If two reviewers differ by more than one point on the same dimension often, the rubric is unclear.

## Spot audit
A second reviewer re-checks a random 10% of accepted tasks. Errors found feed back into coaching and
into the risk register.
