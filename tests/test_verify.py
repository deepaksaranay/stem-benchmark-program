import math

import pytest

from benchmark.verify import (
    CORRECT, INCORRECT, MISSING, UNIT_ERROR, UNPARSEABLE,
    ParseError, evaluate_expression, grade_answer,
)

METRES = {"m": 1, "km": 1000, "cm": 0.01}


@pytest.mark.parametrize("text, expected", [
    ("3.5", 3.5),
    ("-1/6", -1 / 6),
    ("1.2e3", 1200.0),
    ("pi", math.pi),
    ("π", math.pi),
    ("pi^2/6", math.pi**2 / 6),
    ("2*sqrt(2)", 2 * math.sqrt(2)),
    ("exp(1)", math.e),
    ("(1+2)*3", 9.0),
])
def test_valid_expressions(text, expected):
    assert evaluate_expression(text) == pytest.approx(expected)


@pytest.mark.parametrize("text", [
    "",
    "   ",
    "__import__('os').system('echo hacked')",
    "open('secret.txt').read()",
    "().__class__",
    "[1, 2, 3]",
    "x + 1",
    "lambda: 1",
    "9**9**9",
    "10**1000",
    "1/0",
    "sqrt(-1)",
    "sin(1, 2)",
    "abs(x=1)",
    "1" * 500,
])
def test_dangerous_or_invalid_input_is_rejected(text):
    with pytest.raises(ParseError):
        evaluate_expression(text)


def test_correct_answer_with_unit():
    assert grade_answer("90.35 m", 90.3493, METRES, 1e-3).outcome == CORRECT


def test_unit_conversion_is_applied():
    assert grade_answer("0.09035 km", 90.3493, METRES, 1e-3).outcome == CORRECT
    assert grade_answer("9035 cm", 90.3493, METRES, 1e-3).outcome == CORRECT


def test_wrong_unit_is_a_unit_error_even_if_the_number_is_right():
    assert grade_answer("90.35 s", 90.3493, METRES, 1e-3).outcome == UNIT_ERROR


def test_missing_unit_is_a_unit_error():
    assert grade_answer("90.35", 90.3493, METRES, 1e-3).outcome == UNIT_ERROR


def test_wrong_number_is_incorrect():
    assert grade_answer("91.5 m", 90.3493, METRES, 1e-3).outcome == INCORRECT


def test_tolerance_boundary():
    assert grade_answer("90.40 m", 90.3493, METRES, 1e-3).outcome == CORRECT
    assert grade_answer("90.50 m", 90.3493, METRES, 1e-3).outcome == INCORRECT


@pytest.mark.parametrize("answer", [None, "", "   "])
def test_empty_answers_are_missing(answer):
    assert grade_answer(answer, 5.0, {}, 1e-3).outcome == MISSING


def test_prose_is_unparseable():
    assert grade_answer("approximately -0.1667", -1 / 6, {}, 1e-3).outcome == UNPARSEABLE


def test_dimensionless_task_accepts_expressions():
    assert grade_answer("pi^2/6", math.pi**2 / 6, {}, 1e-3).outcome == CORRECT


def test_dimensionless_task_with_a_unit_word_is_flagged():
    assert grade_answer("14 apples", 14.0, {}, 1e-3).outcome == UNIT_ERROR


def test_zero_expected_value_uses_absolute_tolerance():
    assert grade_answer("0", 0.0, {}, 1e-3).outcome == CORRECT
