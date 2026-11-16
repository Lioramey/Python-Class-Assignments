import ast
import operator
import io
import base64

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp


# Mathematical symbols

x, y = sp.symbols("x y")

functions = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "exp": sp.exp,
    "log": sp.log,
    "sqrt": sp.sqrt,
}

constants = {
    "pi": sp.pi,
    "E": sp.E
}

binary_operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}

unary_operators = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg
}


# Interpret the user's equation

def parse_expression(expression):

    if not expression or len(expression) > 100:
        raise ValueError("Please enter an equation of at most 100 characters.")

    try:
        tree = ast.parse(expression, mode="eval")

    except SyntaxError:
        raise ValueError("Please enter a valid mathematical expression.")

    if sum(1 for _ in ast.walk(tree)) > 60:
        raise ValueError("This expression is too complicated.")

    def convert(node):

        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if abs(node.value) > 10000:
                raise ValueError("Please use smaller numbers.")
            return sp.sympify(node.value)

        if isinstance(node, ast.Name):

            if node.id == "x":
                return x

            if node.id == "y":
                return y

            if node.id in constants:
                return constants[node.id]

            raise ValueError(f"Unknown variable: {node.id}")

        if isinstance(node, ast.BinOp) and type(node.op) in binary_operators:

            if isinstance(node.op, ast.Pow):
                if (
                    not isinstance(node.right, ast.Constant)
                    or type(node.right.value) not in (int, float)
                    or abs(node.right.value) > 10
                ):
                    raise ValueError(
                        "Powers must be numbers between -10 and 10."
                    )

            return binary_operators[type(node.op)](
                convert(node.left),
                convert(node.right)
            )

        if isinstance(node, ast.UnaryOp) and type(node.op) in unary_operators:

            return unary_operators[type(node.op)](
                convert(node.operand)
            )

        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in functions
            and not node.keywords
            and len(node.args) == 1
        ):

            return functions[node.func.id](
                convert(node.args[0])
            )

        raise ValueError(
            "Use x, y, numbers, +, -, *, /, **, "
            "sin, cos, tan, exp, log, or sqrt."
        )

    result = convert(tree.body)

    if sp.count_ops(result) > 100:
        raise ValueError("This expression is too complicated.")

    return result


# Evaluate the slope

def evaluate_slope(slope_function, x_value, y_value):

    with np.errstate(all="ignore"):
        slope = np.asarray(
            slope_function(x_value, y_value),
            dtype=float
        ).item()

    if not np.isfinite(slope):
        raise ValueError(
            "The slope became undefined while calculating the solution."
        )

    return slope


# Runge-Kutta method (RK4)

def integrate_solution(
    slope_function,
    y_start,
    end_x,
    x_start=0
):

    direction = 1 if end_x > x_start else -1

    step_size = 0.02

    solution_x = [x_start]
    solution_y = [y_start]

    while direction * (end_x - solution_x[-1]) > 1e-12:

        current_x = solution_x[-1]
        current_y = solution_y[-1]

        step = direction * min(
            step_size,
            abs(end_x - current_x)
        )

        k1 = evaluate_slope(
            slope_function,
            current_x,
            current_y
        )

        k2 = evaluate_slope(
            slope_function,
            current_x + step / 2,
            current_y + step * k1 / 2
        )

        k3 = evaluate_slope(
            slope_function,
            current_x + step / 2,
            current_y + step * k2 / 2
        )

        k4 = evaluate_slope(
            slope_function,
            current_x + step,
            current_y + step * k3
        )

        next_y = current_y + step * (
            k1 + 2*k2 + 2*k3 + k4
        ) / 6

        if not np.isfinite(next_y) or abs(next_y) > 1e8:
            raise ValueError(
                "The solution became too large or undefined."
            )

        solution_x.append(current_x + step)
        solution_y.append(next_y)

    return solution_x, solution_y


# Generate the slope-field graph

def create_slope_field(equation, initial_value=None):

    slope_expression = parse_expression(equation)

    slope_function = sp.lambdify(
        (x, y),
        slope_expression,
        modules="numpy"
    )

    x_min, x_max = -5, 5
    x_start = 0

    x_values = np.linspace(x_min, x_max, 20)
    y_values = np.linspace(-5, 5, 20)

    x_grid, y_grid = np.meshgrid(
        x_values,
        y_values
    )

    with np.errstate(all="ignore"):

        slopes = np.broadcast_to(
            np.asarray(
                slope_function(x_grid, y_grid),
                dtype=float
            ),
            x_grid.shape
        )

        lengths = np.sqrt(1 + slopes**2)

        horizontal = 1 / lengths
        vertical = slopes / lengths

    valid = (
        np.isfinite(horizontal)
        & np.isfinite(vertical)
    )

    horizontal = np.where(
        valid,
        horizontal,
        np.nan
    )

    vertical = np.where(
        valid,
        vertical,
        np.nan
    )

    fig, ax = plt.subplots(figsize=(9, 6))

    try:
        ax.quiver(
            x_grid,
            y_grid,
            horizontal,
            vertical,
            pivot="mid",
            color="#765a9b"
        )

        if initial_value is not None:

            if not np.isfinite(initial_value) or abs(initial_value) > 5:
                raise ValueError(
                    "Please choose an initial value between -5 and 5."
                )

            left_x, left_y = integrate_solution(
                slope_function,
                initial_value,
                x_min
            )

            right_x, right_y = integrate_solution(
                slope_function,
                initial_value,
                x_max
            )

            solution_x = left_x[::-1][:-1] + right_x
            solution_y = left_y[::-1][:-1] + right_y

            ax.plot(
                solution_x,
                solution_y,
                color="#dd728c",
                linewidth=2.5,
                label="Solution curve"
            )

            ax.plot(
                x_start,
                initial_value,
                "o",
                color="#dd728c",
                label="Initial condition"
            )

            ax.legend()

        ax.set_xlabel("x")
        ax.set_ylabel("y")

        ax.set_title(
            f"Slope field for dy/dx = {sp.sstr(slope_expression)}"
        )

        ax.set_xlim(x_min, x_max)
        ax.set_ylim(-5, 5)
        ax.grid(True, alpha=0.3)

        # Convert graph into an image for Flask

        image_buffer = io.BytesIO()

        try:
            fig.savefig(
                image_buffer,
                format="png",
                bbox_inches="tight",
                dpi=120
            )

            image_buffer.seek(0)

            image_base64 = base64.b64encode(
                image_buffer.getvalue()
            ).decode("utf-8")

        finally:
            image_buffer.close()

        return image_base64

    finally:
        plt.close(fig)