"""Builds SYNTHETIC demo data: fake model answers and a fake contributor/reviewer workflow log.

Nothing here comes from a real program or a real person. It exists so the metrics and reports
have something to run on. The generator is deterministic (fixed seed), so results are repeatable.
"""
import csv
import json
import random
from datetime import datetime, timedelta

LOG_COLUMNS = [
    "task_id", "contributor", "reviewer", "domain", "submitted_at", "first_review_at",
    "first_review_outcome", "rework_cycles", "final_outcome", "accepted_at",
]
CONTRIBUTORS = {  # chance that a task is accepted at the first review
    "C01": 0.90, "C02": 0.85, "C03": 0.80, "C04": 0.78,
    "C05": 0.72, "C06": 0.65, "C07": 0.55, "C08": 0.40,
}
REVIEWERS = {"R1": 12.0, "R2": 16.0, "R3": 30.0}  # average hours to a first review
START = datetime(2026, 9, 7, 9, 0)  # a Monday
DAYS = 28
TASK_COUNT = 160
STAMP = "%Y-%m-%d %H:%M"


def model_a_answers(key):
    """A model that is strong on easy tasks and makes realistic mistakes elsewhere."""
    def num(task_id, scale=1.0, digits=4):
        return f"{key[task_id]['value'] * scale:.{digits}g}"

    return [
        ("P-001", f"{num('P-001')} m"),
        ("P-002", "2.006 s"),  # the small-angle approximation: a classic wrong answer
        ("P-003", f"{num('P-003')} min"),
        ("P-004", num("P-004")),
        ("P-005", f"{num('P-005')} m"),  # right number, wrong unit (distance instead of speed)
        ("P-006", f"{num('P-006', 1000)} keV"),
        ("M-001", "pi"),
        ("M-002", "pi^2/6"),
        ("M-003", "5"),
        ("M-004", "14"),
        # M-005: no answer given
        ("M-006", "approximately -0.1667"),  # prose instead of a clean answer
    ]


def model_b_answers(key):
    """A model that is stronger on hard tasks but sloppy about units and arithmetic."""
    def num(task_id, scale=1.0, digits=4):
        return f"{key[task_id]['value'] * scale:.{digits}g}"

    return [
        ("P-001", num("P-001")),  # missing unit
        ("P-002", f"{num('P-002')} s"),
        ("P-003", f"{num('P-003', 60)} s"),
        ("P-004", "0.4"),  # rounded too much
        ("P-005", f"{num('P-005', 0.001)} km/s"),
        ("P-006", f"{num('P-006')} MeV"),
        ("M-001", "3.1416"),
        ("M-002", "1.6449"),
        ("M-003", "5"),
        ("M-004", "13"),  # arithmetic slip
        ("M-005", "6"),
        ("M-006", "-1/6"),
    ]


def write_submissions(path, model, answers):
    payload = {
        "synthetic": True,
        "model": model,
        "submissions": [{"task_id": task_id, "answer": answer} for task_id, answer in answers],
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def make_workflow_rows(seed=2026):
    rng = random.Random(seed)
    contributors = sorted(CONTRIBUTORS)
    reviewers = sorted(REVIEWERS)
    cutoff = START + timedelta(days=DAYS - 2)  # the last two days are still waiting for review
    rows = []
    for number in range(1, TASK_COUNT + 1):
        contributor = rng.choice(contributors)
        reviewer = rng.choice(reviewers)
        submitted = START + timedelta(minutes=rng.randint(0, DAYS * 24 * 60 - 1))
        domain = rng.choice(["physics", "mathematics"])
        row = {
            "task_id": f"T-{number:04d}", "contributor": contributor, "reviewer": reviewer,
            "domain": domain, "submitted_at": submitted.strftime(STAMP),
            "first_review_at": "", "first_review_outcome": "", "rework_cycles": 0,
            "final_outcome": "in_review", "accepted_at": "",
        }
        if submitted < cutoff:
            reviewed = submitted + timedelta(hours=2 + rng.expovariate(1 / REVIEWERS[reviewer]))
            row["first_review_at"] = reviewed.strftime(STAMP)
            if rng.random() < CONTRIBUTORS[contributor]:
                row["first_review_outcome"] = "accepted"
                row["final_outcome"] = "accepted"
                row["accepted_at"] = row["first_review_at"]
            elif rng.random() < 0.85:
                cycles = rng.choice([1, 1, 2])
                row["first_review_outcome"] = "rework"
                row["rework_cycles"] = cycles
                done = reviewed + timedelta(hours=sum(rng.uniform(6, 30) for _ in range(cycles)))
                if rng.random() < 0.9:
                    row["final_outcome"] = "accepted"
                    row["accepted_at"] = done.strftime(STAMP)
                else:
                    row["final_outcome"] = "rejected"
            else:
                row["first_review_outcome"] = "rejected"
                row["final_outcome"] = "rejected"
        rows.append(row)
    return rows


def write_workflow_log(path, seed=2026):
    rows = make_workflow_rows(seed)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LOG_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return rows
