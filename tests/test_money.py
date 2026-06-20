import unittest
from tally.money import parse_pounds_to_pence, format_pence_to_pounds

class TestMoney(unittest.TestCase):
    def test_parse_pounds_to_pence(self):
        self.assertEqual(parse_pounds_to_pence("£60.00"), 6000)
        self.assertEqual(parse_pounds_to_pence("£42"), 4200)
        self.assertEqual(parse_pounds_to_pence("1.50"), 150)
        
    def test_format_pence_to_pounds(self):
        self.assertEqual(format_pence_to_pounds(6000), "£60.00")
        self.assertEqual(format_pence_to_pounds(4200), "£42.00")
        self.assertEqual(format_pence_to_pounds(-150), "-£1.50")
        self.assertEqual(format_pence_to_pounds(5), "£0.05")

if __name__ == '__main__':
    unittest.main()
