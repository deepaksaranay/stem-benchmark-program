"""Command line: python -m benchmark <command>."""
import argparse
import sys

from . import demo_data
from .evaluate import evaluate, load_submissions, summarize
from .key import CrossCheckError, cross_check, key_is_current, write_key
from .metrics import compute, load_config, load_log
from .report import write_report
from .tasks import KEY_PATH, ROOT, load_key, load_tasks, spec_problems

DATA = ROOT / "data"
SUBMISSION_FILES = [DATA / "synthetic_submissions_model_a.json", DATA / "synthetic_submissions_model_b.json"]
LOG_PATH = DATA / "synthetic_workflow_log.csv"
CONFIG_PATH = DATA / "program_config.json"


def cmd_validate_tasks(_):
    failed = False
    problems = spec_problems(load_tasks())
    for problem in problems:
        print("SPEC  ", problem)
        failed = True
    for task_id, a, b, rel_diff, ok in cross_check():
        print(f"{'OK  ' if ok else 'FAIL'}  {task_id}  A={a:.8g}  B={b:.8g}  diff={rel_diff:.1e}")
        failed = failed or not ok
    try:
        current = key_is_current()
    except (CrossCheckError, FileNotFoundError) as exc:
        print("KEY    cannot check:", exc)
        current = False
    print("answer key is current:", current)
    return 1 if failed or not current else 0


def cmd_build_key(args):
    if args.check:
        current = key_is_current()
        print("answer key is current" if current else "answer key is OUT OF DATE: run build-key")
        return 0 if current else 1
    key = write_key()
    print(f"wrote {KEY_PATH} with {len(key)} answers")
    return 0


def cmd_evaluate(args):
    model, answers = load_submissions(args.submissions)
    rows = evaluate(answers, load_tasks(), load_key())
    summary = summarize(rows)
    print(f"model: {model}")
    for row in rows:
        print(f"  {row['task_id']}  {row['difficulty']:<7}  {row['outcome']:<11}  {row['detail']}")
    print(f"accuracy: {summary['accuracy'] * 100:.1f}%  outcomes: {summary['outcomes']}")
    return 0


def cmd_metrics(args):
    config = load_config(CONFIG_PATH)
    metrics = compute(load_log(args.log), config)
    for name in ("submitted", "reviewed", "in_review", "accepted", "rejected"):
        print(f"{name:<24}{metrics[name]}")
    print(f"{'first_pass_rate':<24}{metrics['first_pass_rate']:.3f}  {metrics['first_pass_status']}")
    p90, status = metrics["turnaround_p90_hours"], metrics["turnaround_status"]
    print(f"{'turnaround_p90_hours':<24}{p90:.1f}  {status}")
    print(f"{'weekly_accepted':<24}{metrics['weekly_accepted']}")
    return 0


def cmd_report(_):
    out = write_report(ROOT, SUBMISSION_FILES, LOG_PATH, CONFIG_PATH)
    print("wrote", out)
    return 0


def cmd_demo_data(_):
    key = load_key()
    demo_data.write_submissions(SUBMISSION_FILES[0], "model-a (synthetic)", demo_data.model_a_answers(key))
    demo_data.write_submissions(SUBMISSION_FILES[1], "model-b (synthetic)", demo_data.model_b_answers(key))
    rows = demo_data.write_workflow_log(LOG_PATH)
    print(f"wrote 2 submission files and a workflow log with {len(rows)} tasks (all synthetic)")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="python -m benchmark", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser(
        "validate-tasks", help="check specs, cross-check solutions, check the key")
    validate.set_defaults(run=cmd_validate_tasks)
    build = commands.add_parser("build-key", help="generate tasks/answer_key.json")
    build.add_argument("--check", action="store_true", help="only check that the key is current")
    build.set_defaults(run=cmd_build_key)
    ev = commands.add_parser("evaluate", help="grade a submissions file")
    ev.add_argument("submissions")
    ev.set_defaults(run=cmd_evaluate)
    metrics = commands.add_parser("metrics", help="production metrics from a workflow log")
    metrics.add_argument("log", nargs="?", default=str(LOG_PATH))
    metrics.set_defaults(run=cmd_metrics)
    report = commands.add_parser("report", help="write reports/delivery_report.md")
    report.set_defaults(run=cmd_report)
    demo = commands.add_parser("demo-data", help="regenerate the synthetic demo data")
    demo.set_defaults(run=cmd_demo_data)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
