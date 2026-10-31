import json

import pytest

from benchmark.key import CrossCheckError, build_key, cross_check, key_is_current
from benchmark.reference import REGISTRY
from benchmark.tasks import KEY_PATH, load_key, load_tasks, spec_problems


def test_every_task_has_a_reference_and_vice_versa():
    assert {t["id"] for t in load_tasks()} == set(REGISTRY)


def test_specs_are_valid():
    assert spec_problems(load_tasks()) == []


@pytest.mark.parametrize("task_id", sorted(REGISTRY))
def test_two_independent_solutions_agree(task_id):
    (row,) = cross_check({task_id})
    assert row[4], f"{task_id}: A={row[1]} B={row[2]} diff={row[3]}"


def test_stored_key_matches_the_reference_solutions():
    assert key_is_current()


def test_key_covers_every_task():
    assert set(load_key()) == {t["id"] for t in load_tasks()}


def test_key_file_says_it_is_generated():
    assert "Do not edit by hand" in json.loads(KEY_PATH.read_text())["note"]


def test_a_wrong_reference_is_caught(monkeypatch):
    broken = REGISTRY["M-003"].__class__(
        solution_a=lambda: 5.0, solution_b=lambda: 4.0
    )
    monkeypatch.setitem(REGISTRY, "M-003", broken)
    with pytest.raises(CrossCheckError):
        build_key()


def test_spec_problems_are_reported():
    bad = [{"id": "X-1", "difficulty": "impossible", "answer": {"rel_tol": 0.5}}]
    problems = spec_problems(bad)
    assert any("missing field" in p for p in problems)
    assert any("difficulty" in p for p in problems)
    assert any("rel_tol" in p for p in problems)
