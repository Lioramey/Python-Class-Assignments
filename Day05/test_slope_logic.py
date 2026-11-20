import pytest
import numpy as np
import sympy as sp

from slope_logic import (
    parse_expression,
    evaluate_slope,
    integrate_solution,
    create_slope_field
)


def test_parse_expression():
    x, y = sp.symbols("x y")
    result = parse_expression("x + y")
    assert result == x + y


def test_parse_sine():
    x = sp.Symbol("x")
    result = parse_expression("sin(x)")
    assert result == sp.sin(x)


def test_invalid_expression():
    with pytest.raises(ValueError):
        parse_expression("hello")


def test_evaluate_slope():
    def slope_function(x, y):
        return x + y

    result = evaluate_slope(slope_function, 2, 3)
    assert result == 5


def test_integrate_solution():
    def slope_function(x, y):
        return 1

    x_values, y_values = integrate_solution(
        slope_function,
        y_start=0,
        end_x=2
    )

    assert np.isclose(y_values[-1], 2, atol=0.001)


def test_create_slope_field():
    graph = create_slope_field("x - y", 2)

    assert isinstance(graph, str)
    assert len(graph) > 0


def test_invalid_graph():
    with pytest.raises(ValueError):
        create_slope_field("invalid_equation")
        