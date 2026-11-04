import ast
import operator

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp


x, y = sp.symbols("x y")
functions = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "exp": sp.exp,
    "log": sp.log,
    "sqrt": sp.sqrt,
}
constants = {"pi": sp.pi, "E": sp.E}
binary_operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}
unary_operators = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def parse_expression(expression):
    """Convert a simple mathematical expression into a SymPy expression."""
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as error:
        raise ValueError("Enter a valid expression, such as x - y or x**2.") from error

    def convert(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return sp.sympify(node.value)
        if isinstance(node, ast.Name):
            if node.id == "x":
                return x
            if node.id == "y":
                return y
            if node.id in constants:
                return constants[node.id]
            raise ValueError(f"Unknown name: {node.id}")
        if isinstance(node, ast.BinOp) and type(node.op) in binary_operators:
            return binary_operators[type(node.op)](convert(node.left), convert(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in unary_operators:
            return unary_operators[type(node.op)](convert(node.operand))
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in functions
            and not node.keywords
        ):
            return functions[node.func.id](*(convert(arg) for arg in node.args))
        raise ValueError(
            "Use x, y, numbers, +, -, *, /, **, and functions such as sin(x), "
            "cos(y), exp(x), log(x), or sqrt(x)."
        )

    return convert(tree.body)


equation = input("dy/dx = ")
slope_expression = parse_expression(equation)
slope_function = sp.lambdify((x, y), slope_expression, modules="numpy")

x_min, x_max = -5, 5
x_start = 0
print("Assuming the initial x-value is x_0 = 0.")
y_start_text = input("y(0) = (press Enter to plot only the slope field): ").strip()
has_initial_value = bool(y_start_text)
if has_initial_value:
    y_start = float(y_start_text)

x_values = np.linspace(x_min, x_max, 20)
y_values = np.linspace(-5, 5, 20)
x_grid, y_grid = np.meshgrid(x_values, y_values)

with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
    slopes = np.broadcast_to(
        np.asarray(slope_function(x_grid, y_grid), dtype=float), x_grid.shape
    )
    lengths = np.sqrt(1 + slopes**2)
    horizontal = 1 / lengths
    vertical = slopes / lengths

valid = np.isfinite(horizontal) & np.isfinite(vertical)
horizontal = np.where(valid, horizontal, np.nan)
vertical = np.where(valid, vertical, np.nan)

def evaluate_slope(x_value, y_value):
    slope = np.asarray(slope_function(x_value, y_value), dtype=float).item()
    if not np.isfinite(slope):
        raise ValueError("The slope became undefined while calculating the solution.")
    return slope


def integrate_solution(end_x):
    direction = 1 if end_x > x_start else -1
    step_size = 0.02
    solution_x = [x_start]
    solution_y = [y_start]

    while direction * (end_x - solution_x[-1]) > 1e-12:
        current_x = solution_x[-1]
        current_y = solution_y[-1]
        step = direction * min(step_size, abs(end_x - current_x))
        k1 = evaluate_slope(current_x, current_y)
        k2 = evaluate_slope(current_x + step / 2, current_y + step * k1 / 2)
        k3 = evaluate_slope(current_x + step / 2, current_y + step * k2 / 2)
        k4 = evaluate_slope(current_x + step, current_y + step * k3)
        next_y = current_y + step * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        if not np.isfinite(next_y):
            raise ValueError("The solution became undefined while being calculated.")
        solution_x.append(current_x + step)
        solution_y.append(next_y)

    return solution_x, solution_y


if has_initial_value:
    left_x, left_y = integrate_solution(x_min)
    right_x, right_y = integrate_solution(x_max)
    solution_x = left_x[::-1][:-1] + right_x
    solution_y = left_y[::-1][:-1] + right_y

plt.quiver(x_grid, y_grid, horizontal, vertical, pivot="mid")
if has_initial_value:
    plt.plot(solution_x, solution_y, color="red", label="Solution curve")
    plt.plot(x_start, y_start, "ro", label="Initial condition")
plt.xlabel("x")
plt.ylabel("y")
if has_initial_value:
    plt.title(f"Slope field and solution for dy/dx = {sp.sstr(slope_expression)}")
    plt.legend()
else:
    plt.title(f"Slope field for dy/dx = {sp.sstr(slope_expression)}")
plt.xlim(x_min, x_max)
plt.ylim(-5, 5)
plt.grid(True)
plt.show()
