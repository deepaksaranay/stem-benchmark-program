# Contributor guidelines

## What a good task looks like
- **Original.** Not copied from a book, website or past exam. Change the numbers and the situation.
- **One answer.** A number, a unit, or a closed form such as `pi^2/6`. No "show that" and no essays.
- **Unambiguous.** Every constant is given in the prompt (for example `g = 9.81 m/s^2`). Another expert
  reading it gets the same answer.
- **Verifiable.** You provide two independent solution methods that agree (an analytic one and a numeric one).
- **Honest difficulty.** Easy: one idea. Medium: two or three steps. Hard: a trap or a non-obvious method,
  such as using the exact pendulum period instead of the small-angle formula.

## Units and precision
State the unit in the prompt. Say how many significant figures to give ("at least 4"). The grader accepts
equivalent units (m, km, cm) but not a wrong dimension.

## Checklist before you submit
- [ ] I solved it two different ways and the answers match.
- [ ] All constants and assumptions are in the prompt.
- [ ] The unit and the tolerance are set in the task file.
- [ ] I read the prompt once more as someone who has never seen it.
- [ ] The task passes `python -m benchmark validate-tasks`.

## Common reasons for rework
1. Missing constant or assumption (most frequent).
2. Two valid readings of the question.
3. Only one solution method, or the methods differ in the 3rd digit.
4. The answer depends on rounding in an intermediate step.
5. Too easy for the difficulty label.
