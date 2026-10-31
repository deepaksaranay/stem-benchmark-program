import pytest

from benchmark.metrics import AMBER, GREEN, RED, compute, percentile, rag

CONFIG = {
    "weekly_accepted_target": 2,
    "first_pass_target": 0.75,
    "turnaround_p90_sla_hours": 10,
    "amber_margin": 0.10,
}


def row(task, contributor, submitted, reviewed, first, cycles, final, accepted="", reviewer="R1"):
    return {
        "task_id": task, "contributor": contributor, "reviewer": reviewer, "domain": "physics",
        "submitted_at": submitted, "first_review_at": reviewed, "first_review_outcome": first,
        "rework_cycles": cycles, "final_outcome": final, "accepted_at": accepted,
    }


LOG = [
    row("T1", "C01", "2026-09-07 09:00", "2026-09-07 15:00", "accepted", 0, "accepted", "2026-09-07 15:00"),
    row("T2", "C01", "2026-09-07 10:00", "2026-09-07 20:00", "accepted", 0, "accepted", "2026-09-07 20:00"),
    row("T3", "C02", "2026-09-08 09:00", "2026-09-08 11:00", "rework", 1, "accepted", "2026-09-14 09:00"),
    row("T4", "C02", "2026-09-08 09:00", "2026-09-09 09:00", "rejected", 0, "rejected"),
    row("T5", "C02", "2026-09-09 09:00", "", "", 0, "in_review"),
]


def test_counts():
    metrics = compute(LOG, CONFIG)
    assert metrics["submitted"] == 5
    assert metrics["reviewed"] == 4
    assert metrics["in_review"] == 1
    assert metrics["accepted"] == 3
    assert metrics["rejected"] == 1


def test_first_pass_and_rework_rates():
    metrics = compute(LOG, CONFIG)
    assert metrics["first_pass_rate"] == pytest.approx(2 / 4)
    assert metrics["rework_rate"] == pytest.approx(1 / 4)
    assert metrics["first_pass_status"] == RED


def test_turnaround():
    metrics = compute(LOG, CONFIG)
    assert metrics["turnaround_median_hours"] == pytest.approx(8.0)  # waits: 6, 10, 2, 24
    assert metrics["turnaround_p90_hours"] == 24.0
    assert metrics["turnaround_status"] == RED


def test_weekly_accepted_uses_the_acceptance_date():
    metrics = compute(LOG, CONFIG)
    assert metrics["weekly_accepted"] == {"2026-W37": 2, "2026-W38": 1}
    assert metrics["weekly_status"] == {"2026-W37": GREEN}  # the last week is partial


def test_contributors_are_sorted_worst_first():
    metrics = compute(LOG, CONFIG)
    assert [c["contributor"] for c in metrics["contributors"]] == ["C02", "C01"]
    assert metrics["contributors"][0]["first_pass_rate"] == pytest.approx(0.0)


def test_reviewer_speed():
    assert compute(LOG, CONFIG)["reviewer_median_hours"] == {"R1": 8.0}


def test_percentile_nearest_rank():
    assert percentile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 0.9) == 9
    assert percentile([], 0.9) == 0.0


@pytest.mark.parametrize("value, higher, expected", [
    (30, True, GREEN), (28, True, AMBER), (20, True, RED),
    (36, False, GREEN), (39, False, AMBER), (50, False, RED),
])
def test_rag(value, higher, expected):
    target = 30 if higher else 36
    assert rag(value, target, higher, 0.10) == expected


def test_empty_log_does_not_crash():
    metrics = compute([], CONFIG)
    assert metrics["submitted"] == 0
    assert metrics["first_pass_rate"] == 0.0
