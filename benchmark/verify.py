"""Safe answer parsing, unit handling and grading.

Model answers are untrusted text. They are never passed to eval(); the parser below
walks a small whitelist of Python syntax nodes and computes the number itself.
"""
import ast
import math
import operator
import re
from dataclasses import dataclass

MAX_LENGTH = 120
MAX_EXPONENT = 100
MAX_BASE = 1e6

CORRECT = "correct"
INCORRECT = "incorrect"
UNIT_ERROR = "unit_error"
UNPARSEABLE = "unparseable"
MISSING = "missing"
OUTCOMES = (CORRECT, INCORRECT, UNIT_ERROR, UNPARSEABLE, MISSING)

_FUNCTIONS = {
    "sqrt": math.sqrt,
    "exp": math.exp,
    "log": math.log,
    "ln": math.log,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "abs": abs,
}
_CONSTANTS = {"pi": math.pi, "e": math.e}
_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


class ParseError(ValueError):
    """The text is not a number or a simple arithmetic expression."""


def evaluate_expression(text):
    """Evaluate a number or simple expression such as '3.2e3', '-1/6' or 'sqrt(2)*pi'."""
    cleaned = (
        text.strip()
        .replace("^", "**")
        .replace("×", "*")
        .replace("−", "-")
        .replace("π", "pi")
    )
    if not cleaned or len(cleaned) > MAX_LENGTH:
        raise ParseError("empty or too long")
    try:
        tree = ast.parse(cleaned, mode="eval")
        return float(_evaluate(tree.body))
    except (SyntaxError, ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ParseError(str(exc)) from exc


def _evaluate(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return float(node.value)
    if isinstance(node, ast.Name) and node.id in _CONSTANTS:
        return _CONSTANTS[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = _evaluate(node.operand)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.BinOp):
        left, right = _evaluate(node.left), _evaluate(node.right)
        if isinstance(node.op, ast.Pow):
            if abs(right) > MAX_EXPONENT or abs(left) > MAX_BASE:
                raise ParseError("exponent or base too large")
            return left ** right
        operation = _BINARY.get(type(node.op))
        if operation is None:
            raise ParseError("operator not allowed")
        return operation(left, right)
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in _FUNCTIONS
        and len(node.args) == 1
        and not node.keywords
    ):
        return _FUNCTIONS[node.func.id](_evaluate(node.args[0]))
    raise ParseError("syntax not allowed")


@dataclass
class Grade:
    outcome: str
    value: float = None
    detail: str = ""


def split_unit(text, accepted_units):
    """Return (number_text, unit_or_None). Raises ParseError for an unknown unit word."""
    stripped = text.strip()
    for unit in sorted(accepted_units, key=len, reverse=True):
        if stripped.endswith(unit):
            head = stripped[: -len(unit)].strip()
            if head:
                return head, unit
    match = re.search(r"\s+([A-Za-z][A-Za-z0-9/^*]*)$", stripped)
    if match and match.group(1) not in _CONSTANTS and match.group(1) not in _FUNCTIONS:
        raise ParseError("unknown unit: " + match.group(1))
    return stripped, None


def grade_answer(submitted, expected, accepted_units, rel_tol, abs_tol=1e-12):
    """Grade one submitted answer against the expected number (in the task's own unit)."""
    if submitted is None or not str(submitted).strip():
        return Grade(MISSING, detail="no answer given")
    text = str(submitted)
    try:
        number_text, unit = split_unit(text, accepted_units)
    except ParseError as exc:
        return Grade(UNIT_ERROR, detail=str(exc))
    try:
        value = evaluate_expression(number_text)
    except ParseError as exc:
        return Grade(UNPARSEABLE, detail=str(exc))
    if unit is not None:
        value *= accepted_units[unit]
    elif accepted_units:
        return Grade(UNIT_ERROR, value, "a unit is required")
    if math.isclose(value, expected, rel_tol=rel_tol, abs_tol=abs_tol):
        return Grade(CORRECT, value)
    return Grade(INCORRECT, value, f"expected about {expected:.6g}")
