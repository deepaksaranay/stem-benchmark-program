"""Grades a model's answers against the answer key."""
import json
from collections import Counter, defaultdict

from .verify import CORRECT, MISSING, OUTCOMES, grade_answer


def load_submissions(path):
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    answers = {}
    for entry in data["submissions"]:
        answers[entry["task_id"]] = entry.get("answer")  # if a task appears twice, the last wins
    return data.get("model", "unknown-model"), answers


def evaluate(answers, tasks, key):
    """Return one result row per task, in task order."""
    rows = []
    for task in tasks:
        spec = task["answer"]
        grade = grade_answer(
            answers.get(task["id"]),
            key[task["id"]]["value"],
            spec["accepted_units"],
            spec["rel_tol"],
        )
        rows.append({
            "task_id": task["id"],
            "domain": task["domain"],
            "difficulty": task["difficulty"],
            "outcome": grade.outcome,
            "detail": grade.detail,
        })
    return rows


def summarize(rows):
    total = len(rows)
    outcomes = Counter(row["outcome"] for row in rows)

    def accuracy(selected):
        return sum(1 for r in selected if r["outcome"] == CORRECT) / len(selected) if selected else 0.0

    groups = {}
    for field in ("domain", "difficulty"):
        buckets = defaultdict(list)
        for row in rows:
            buckets[row[field]].append(row)
        groups[field] = {name: (accuracy(items), len(items)) for name, items in sorted(buckets.items())}
    return {
        "total": total,
        "accuracy": accuracy(rows),
        "outcomes": {name: outcomes.get(name, 0) for name in OUTCOMES},
        "by_domain": groups["domain"],
        "by_difficulty": groups["difficulty"],
        "answered": total - outcomes.get(MISSING, 0),
    }
