from benchmark import cli, demo_data
from benchmark.evaluate import evaluate, load_submissions, summarize
from benchmark.tasks import load_key, load_tasks


def run(name):
    _, answers = load_submissions(cli.DATA / name)
    return evaluate(answers, load_tasks(), load_key())


def test_model_a_shows_every_kind_of_outcome():
    summary = summarize(run("synthetic_submissions_model_a.json"))
    assert summary["total"] == 12
    assert all(count >= 1 for count in summary["outcomes"].values())
    assert summary["outcomes"]["correct"] == 8


def test_model_b_summary():
    summary = summarize(run("synthetic_submissions_model_b.json"))
    assert summary["outcomes"]["correct"] == 9
    assert summary["accuracy"] == 0.75


def test_unanswered_tasks_count_as_missing():
    rows = evaluate({}, load_tasks(), load_key())
    assert {row["outcome"] for row in rows} == {"missing"}


def test_last_answer_wins_for_duplicates(tmp_path):
    path = tmp_path / "s.json"
    path.write_text(
        '{"model": "m", "submissions": [{"task_id": "M-003", "answer": "1"},'
        ' {"task_id": "M-003", "answer": "5"}]}'
    )
    _, answers = load_submissions(path)
    rows = evaluate(answers, load_tasks(), load_key())
    assert [r["outcome"] for r in rows if r["task_id"] == "M-003"] == ["correct"]


def test_stored_demo_files_are_current(tmp_path):
    """The files in data/ must be what the generator produces, so nobody edits them by hand."""
    key = load_key()
    out = tmp_path / "a.json"
    demo_data.write_submissions(out, "model-a (synthetic)", demo_data.model_a_answers(key))
    assert out.read_text() == (cli.DATA / "synthetic_submissions_model_a.json").read_text()
    log = tmp_path / "log.csv"
    demo_data.write_workflow_log(log)
    assert log.read_text() == (cli.LOG_PATH).read_text()
