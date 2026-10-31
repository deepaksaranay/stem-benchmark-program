"""Builds and checks the answer key from the reference solutions."""
import json
import math

from .reference import REGISTRY
from .tasks import KEY_PATH, load_tasks


class CrossCheckError(Exception):
    """Solution A and solution B disagree for at least one task."""


def cross_check(task_ids=None):
    """Run both methods for every task. Returns rows of (task_id, a, b, rel_diff, ok)."""
    rows = []
    for task_id, reference in REGISTRY.items():
        if task_ids is not None and task_id not in task_ids:
            continue
        a, b = reference.solution_a(), reference.solution_b()
        rel_diff = abs(a - b) / max(abs(a), 1e-300)
        rows.append((task_id, a, b, rel_diff, rel_diff <= reference.cross_check_rel_tol))
    return rows


def build_key():
    """Compute the key. Fails if the two solutions of any task disagree."""
    tasks = {task["id"]: task for task in load_tasks()}
    missing = sorted(set(tasks) - set(REGISTRY))
    extra = sorted(set(REGISTRY) - set(tasks))
    if missing or extra:
        raise CrossCheckError(f"tasks without reference: {missing}; references without task: {extra}")
    rows = cross_check(set(tasks))
    bad = [row[0] for row in rows if not row[4]]
    if bad:
        raise CrossCheckError(f"solution A and B disagree for: {bad}")
    key = {}
    for task_id, a, _, _, _ in rows:
        key[task_id] = {"value": float(f"{a:.12g}"), "unit": tasks[task_id]["answer"]["unit"]}
    return key


def write_key(path=KEY_PATH):
    key = build_key()
    payload = {
        "generated_by": "python -m benchmark build-key",
        "note": "Generated from benchmark/reference.py. Do not edit by hand.",
        "tasks": key,
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    return key


def key_is_current(path=KEY_PATH):
    """True if the stored key still matches what the reference solutions compute now."""
    with open(path, encoding="utf-8") as handle:
        stored = json.load(handle)["tasks"]
    fresh = build_key()
    if set(stored) != set(fresh):
        return False
    return all(math.isclose(stored[k]["value"], fresh[k]["value"], rel_tol=1e-9) for k in fresh)
