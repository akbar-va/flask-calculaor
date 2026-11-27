import ast
import math
import operator
from typing import Union

Number = Union[int, float]

_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_MAX_EXPRESSION_LENGTH = 200
_MAX_EXPONENT = 1000


class CalculationError(ValueError):
    """Raised when an expression cannot be safely evaluated."""


def _eval_node(node: ast.AST) -> Number:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise CalculationError("Only numeric values are allowed.")
        return node.value

    if isinstance(node, ast.UnaryOp):
        op_func = _UNARY_OPS.get(type(node.op))
        if op_func is None:
            raise CalculationError("Unsupported unary operator.")
        return op_func(_eval_node(node.operand))

    if isinstance(node, ast.BinOp):
        op_func = _BINARY_OPS.get(type(node.op))
        if op_func is None:
            raise CalculationError("Unsupported operator.")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > _MAX_EXPONENT:
            raise CalculationError("Exponent is too large.")
        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)) and right == 0:
            raise CalculationError("Cannot divide by zero.")
        result = op_func(left, right)
        if isinstance(result, complex):
            raise CalculationError("Result is not a real number.")
        return result

    raise CalculationError("Invalid expression.")


def format_result(value: Number) -> str:
    """Format numeric results cleanly without trailing .0 or float noise."""
    if isinstance(value, complex):
        raise CalculationError("Result is not a real number.")
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            raise CalculationError("Result is out of range.")
        if value.is_integer():
            return str(int(value))
        return f"{value:.12g}"
    return str(value)


def evaluate_expression(expression: str) -> str:
    """Safely parse and evaluate a mathematical expression string."""
    if not isinstance(expression, str):
        raise CalculationError("Expression must be a string.")

    cleaned = (
        expression.strip()
        .replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
    )

    if not cleaned:
        raise CalculationError("Please enter an expression.")
    if len(cleaned) > _MAX_EXPRESSION_LENGTH:
        raise CalculationError("Expression is too long.")

    try:
        tree = ast.parse(cleaned, mode="eval")
    except SyntaxError as exc:
        raise CalculationError("Invalid syntax.") from exc

    try:
        result = _eval_node(tree)
        return format_result(result)
    except OverflowError as exc:
        raise CalculationError("Result is too large.") from exc
