from benchmark import cli
from benchmark.report import build_report


def test_report_has_all_sections_and_the_synthetic_warning():
    text = build_report(cli.ROOT, cli.SUBMISSION_FILES, cli.LOG_PATH, cli.CONFIG_PATH)
    for heading in ("## 1. Task quality gate", "## 2. Model evaluation",
                    "## 3. Production metrics", "## 4. Actions a program owner would take"):
        assert heading in text
    assert "SYNTHETIC DEMO DATA" in text
    assert "12/12" in text


def test_committed_report_is_current():
    expected = build_report(cli.ROOT, cli.SUBMISSION_FILES, cli.LOG_PATH, cli.CONFIG_PATH)
    assert (cli.ROOT / "reports" / "delivery_report.md").read_text(encoding="utf-8") == expected


def test_validate_tasks_command_passes():
    assert cli.main(["validate-tasks"]) == 0


def test_build_key_check_passes():
    assert cli.main(["build-key", "--check"]) == 0


def test_evaluate_command(capsys):
    assert cli.main(["evaluate", str(cli.SUBMISSION_FILES[0])]) == 0
    assert "accuracy: 66.7%" in capsys.readouterr().out


def test_metrics_command(capsys):
    assert cli.main(["metrics"]) == 0
    assert "first_pass_rate" in capsys.readouterr().out
