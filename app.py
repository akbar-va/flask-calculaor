from flask import Flask, jsonify, render_template, request

from calculator import CalculationError, evaluate_expression

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.post("/api/calculate")
def calculate():
    data = request.get_json(silent=True) or {}
    expression = data.get("expression", "")

    try:
        result = evaluate_expression(expression)
    except CalculationError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"expression": expression, "result": result})


if __name__ == "__main__":
    app.run(debug=True)
