from flask import Flask, render_template, request
from slope_logic import create_slope_field

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():

    graph = None
    error = None

    equation = "x - y"
    initial_value = ""

    if request.method == "POST":

        equation = request.form.get("equation", "").strip()
        initial_value = request.form.get("initial_value", "").strip()

        try:

            if not equation:
                raise ValueError("Please enter a differential equation.")

            if initial_value:
                y0 = float(initial_value)
            else:
                y0 = None

            graph = create_slope_field(
                equation,
                y0
            )

        except (ValueError, TypeError, ArithmeticError) as exc:
            error = str(exc)

    return render_template(
        "index.html",
        graph=graph,
        error=error,
        equation=equation,
        initial_value=initial_value
    )


if __name__ == "__main__":
    app.run(debug=True)