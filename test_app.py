import unittest

from app import app
from calculator import CalculationError, evaluate_expression


class CalculatorLogicTests(unittest.TestCase):
    def test_basic_arithmetic_and_precedence(self):
        self.assertEqual(evaluate_expression("2 + 3 * 4"), "14")
        self.assertEqual(evaluate_expression("(2 + 3) * 4"), "20")
        self.assertEqual(evaluate_expression("10 ÷ 4"), "2.5")
        self.assertEqual(evaluate_expression("8 × 5 − 3"), "37")
        self.assertEqual(evaluate_expression("2 ** 10"), "1024")
        self.assertEqual(evaluate_expression("10 % 3"), "1")

    def test_unary_and_formatting(self):
        self.assertEqual(evaluate_expression("-5 + 12"), "7")
        self.assertEqual(evaluate_expression("4.0 + 2.0"), "6")
        self.assertEqual(evaluate_expression("0.1 + 0.2"), "0.3")

    def test_error_cases(self):
        with self.assertRaises(CalculationError):
            evaluate_expression("")
        with self.assertRaises(CalculationError):
            evaluate_expression("10 / 0")
        with self.assertRaises(CalculationError):
            evaluate_expression("(-1) ** 0.5")
        with self.assertRaises(CalculationError):
            evaluate_expression("2 ** 10000")
        with self.assertRaises(CalculationError):
            evaluate_expression("__import__('os').system('echo hi')")
        with self.assertRaises(CalculationError):
            evaluate_expression("2 + * 3")


class FlaskRoutesTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_page_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Flask Calculator", response.data)

    def test_calculate_endpoint_success(self):
        response = self.client.post("/api/calculate", json={"expression": "(12 + 8) ÷ 4"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"expression": "(12 + 8) ÷ 4", "result": "5"})

    def test_calculate_endpoint_error(self):
        response = self.client.post("/api/calculate", json={"expression": "5 / 0"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Cannot divide by zero."})


if __name__ == "__main__":
    unittest.main()
