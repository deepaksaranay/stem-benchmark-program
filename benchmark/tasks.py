"""Loading task specifications and the generated answer key."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_PATH = ROOT / "tasks" / "tasks.json"
KEY_PATH = ROOT / "tasks" / "answer_key.json"

REQUIRED_FIELDS = ("id", "domain", "topic", "difficulty", "prompt", "answer")
DIFFICULTIES = ("easy", "medium", "hard")


def load_tasks(path=TASKS_PATH):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def load_key(path=KEY_PATH):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)["tasks"]


def spec_problems(tasks):
    """Return a list of human-readable problems with the task specs (empty list = fine)."""
    problems = []
    seen = set()
    for task in tasks:
        task_id = task.get("id", "<missing id>")
        for field in REQUIRED_FIELDS:
            if field not in task:
                problems.append(f"{task_id}: missing field '{field}'")
        if task_id in seen:
            problems.append(f"{task_id}: duplicate id")
        seen.add(task_id)
        if task.get("difficulty") not in DIFFICULTIES:
            problems.append(f"{task_id}: difficulty must be one of {DIFFICULTIES}")
        answer = task.get("answer", {})
        if answer.get("unit") and answer["unit"] not in answer.get("accepted_units", {}):
            problems.append(f"{task_id}: the main unit must be in accepted_units")
        if not 0 < answer.get("rel_tol", 0) < 0.1:
            problems.append(f"{task_id}: rel_tol must be between 0 and 0.1")
    return problems
