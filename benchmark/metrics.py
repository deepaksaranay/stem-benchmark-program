"""Program metrics from the workflow log: quality, speed and throughput, with RAG status."""
import csv
import json
import math
from collections import defaultdict
from datetime import datetime
from statistics import median

from .demo_data import STAMP

GREEN, AMBER, RED = "GREEN", "AMBER", "RED"


def load_config(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_log(path):
    with open(path, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _time(text):
    return datetime.strptime(text, STAMP) if text else None


def percentile(values, fraction):
    """Nearest-rank percentile (the smallest value with at least `fraction` of the data below it)."""
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[max(0, math.ceil(fraction * len(ordered)) - 1)]


def rag(value, target, higher_is_better, margin):
    if higher_is_better:
        if value >= target:
            return GREEN
        return AMBER if value >= target * (1 - margin) else RED
    if value <= target:
        return GREEN
    return AMBER if value <= target * (1 + margin) else RED


def compute(rows, config):
    reviewed = [r for r in rows if r["first_review_at"]]
    first_pass = [r for r in reviewed if r["first_review_outcome"] == "accepted"]
    reworked = [r for r in reviewed if int(r["rework_cycles"]) > 0]
    rejected = [r for r in rows if r["final_outcome"] == "rejected"]
    accepted = [r for r in rows if r["final_outcome"] == "accepted"]
    waits = [
        (_time(r["first_review_at"]) - _time(r["submitted_at"])).total_seconds() / 3600
        for r in reviewed
    ]

    weekly = defaultdict(int)
    for row in accepted:
        iso = _time(row["accepted_at"]).isocalendar()
        weekly[f"{iso[0]}-W{iso[1]:02d}"] += 1

    by_contributor = defaultdict(list)
    by_reviewer = defaultdict(list)
    for row, wait in zip(reviewed, waits):
        by_contributor[row["contributor"]].append(row)
        by_reviewer[row["reviewer"]].append(wait)

    margin = config["amber_margin"]
    first_pass_rate = len(first_pass) / len(reviewed) if reviewed else 0.0
    p90 = percentile(waits, 0.9)
    contributors = []
    for name, items in sorted(by_contributor.items()):
        rate = sum(1 for r in items if r["first_review_outcome"] == "accepted") / len(items)
        contributors.append({
            "contributor": name,
            "reviewed": len(items),
            "first_pass_rate": rate,
            "status": rag(rate, config["first_pass_target"], True, margin),
        })
    contributors.sort(key=lambda c: c["first_pass_rate"])

    full_weeks = sorted(weekly)[:-1] if len(weekly) > 1 else sorted(weekly)
    return {
        "submitted": len(rows),
        "reviewed": len(reviewed),
        "in_review": len(rows) - len(reviewed),
        "accepted": len(accepted),
        "rejected": len(rejected),
        "first_pass_rate": first_pass_rate,
        "first_pass_status": rag(first_pass_rate, config["first_pass_target"], True, margin),
        "rework_rate": len(reworked) / len(reviewed) if reviewed else 0.0,
        "turnaround_median_hours": median(waits) if waits else 0.0,
        "turnaround_p90_hours": p90,
        "turnaround_status": rag(p90, config["turnaround_p90_sla_hours"], False, margin),
        "weekly_accepted": dict(sorted(weekly.items())),
        "weekly_status": {
            week: rag(weekly[week], config["weekly_accepted_target"], True, margin)
            for week in full_weeks
        },
        "contributors": contributors,
        "reviewer_median_hours": {k: median(v) for k, v in sorted(by_reviewer.items())},
    }
