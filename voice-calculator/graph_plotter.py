from __future__ import annotations

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

from config import PLOT_RANGE, PLOT_POINTS
from math_engine import parse_expression


def plot_expression(expression: str, variable: str = "x") -> Optional[str]:
    try:
        var = sp.Symbol(variable)
        expr = parse_expression(expression)
        func = sp.lambdify(var, expr, modules=["numpy"])

        xs = np.linspace(PLOT_RANGE[0], PLOT_RANGE[1], PLOT_POINTS)
        ys = func(xs)

        plt.figure(figsize=(8, 4.5))
        plt.plot(xs, ys)
        plt.title(f"Plot of {expression}")
        plt.xlabel(variable)
        plt.ylabel("y")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        return None
    except Exception as exc:
        return str(exc)
