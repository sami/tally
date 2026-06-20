import unittest
from tally.money import parse_pounds_to_pence, format_pence_to_pounds


class TestMoney(unittest.TestCase):
    def test_parse_pounds_to_pence(self):
        self.assertEqual(parse_pounds_to_pence("£60.00"), 6000)
        self.assertEqual(parse_pounds_to_pence("£42"), 4200)
        self.assertEqual(parse_pounds_to_pence("1.50"), 150)
        self.assertEqual(parse_pounds_to_pence("-£1.50"), -150)
        self.assertEqual(parse_pounds_to_pence("-5.00"), -500)

    def test_allocate_pennies_zero_weight(self):
        from tally.money import allocate_pennies
        weights = {"A": 0, "B": 0}
        order = ["A", "B"]
        result = allocate_pennies(1000, weights, order)
        self.assertEqual(result, {"A": 0, "B": 0})

    def test_format_pence_to_pounds(self):
        self.assertEqual(format_pence_to_pounds(6000), "£60.00")
        self.assertEqual(format_pence_to_pounds(4200), "£42.00")
        self.assertEqual(format_pence_to_pounds(-150), "-£1.50")
        self.assertEqual(format_pence_to_pounds(5), "£0.05")


if __name__ == "__main__":
    unittest.main()
