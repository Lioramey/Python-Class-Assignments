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

x_values = np.linspace(-5, 5, 20)
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

plt.quiver(x_grid, y_grid, horizontal, vertical, pivot="mid")
plt.xlabel("x")
plt.ylabel("y")
plt.title(f"Slope field for dy/dx = {sp.sstr(slope_expression)}")
plt.xlim(-5, 5)
plt.ylim(-5, 5)
plt.grid(True)
plt.show()
