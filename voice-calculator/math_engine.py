from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import sympy as sp
from sympy.parsing.sympy_parser import (
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
    parse_expr,
)


_TRANSFORMS = standard_transformations + (implicit_multiplication_application, convert_xor)


@dataclass
class MathResult:
    value: Any
    ok: bool
    error: str | None = None


def parse_expression(expression: str) -> sp.Expr:
    allowed = {
        "sqrt": sp.sqrt,
        "log": sp.log,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
        "factorial": sp.factorial,
        "pi": sp.pi,
        "e": sp.E,
        "x": sp.Symbol("x"),
    }
    return parse_expr(expression, local_dict=allowed, transformations=_TRANSFORMS)


def calculate(expression: str) -> MathResult:
    try:
        expr = parse_expression(expression)
        value = expr.evalf()
        return MathResult(value=float(value) if value.is_number else value, ok=True)
    except Exception as exc:
        return MathResult(value=None, ok=False, error=str(exc))


def solve_equation(equation: str) -> MathResult:
    try:
        if "=" not in equation:
            return MathResult(value=None, ok=False, error="No equals sign")

        left, right = equation.split("=", 1)
        left_expr = parse_expression(left)
        right_expr = parse_expression(right)
        equation_expr = sp.Eq(left_expr, right_expr)

        symbols: Iterable[sp.Symbol] = list(equation_expr.free_symbols)
        if not symbols:
            return MathResult(value="No variables to solve", ok=False)

        target = sorted(symbols, key=lambda s: s.name)[0]
        solution = sp.solve(equation_expr, target)
        return MathResult(value=solution, ok=True)
    except Exception as exc:
        return MathResult(value=None, ok=False, error=str(exc))


def differentiate(expression: str, variable: str = "x") -> MathResult:
    try:
        expr = parse_expression(expression)
        var = sp.Symbol(variable)
        result = sp.diff(expr, var)
        return MathResult(value=result, ok=True)
    except Exception as exc:
        return MathResult(value=None, ok=False, error=str(exc))


def integrate(expression: str, variable: str = "x") -> MathResult:
    try:
        expr = parse_expression(expression)
        var = sp.Symbol(variable)
        result = sp.integrate(expr, var)
        return MathResult(value=result, ok=True)
    except Exception as exc:
        return MathResult(value=None, ok=False, error=str(exc))
