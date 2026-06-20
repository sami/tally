import unittest
from decimal import Decimal
from datetime import datetime, timezone
from tally.splitting import (
    EqualSplit,
    SharesSplit,
    PercentageSplit,
    ExactSplit,
    ItemisedSplit,
    Item,
)
from tally.models import Expense


class TestSplitting(unittest.TestCase):
    def test_equal_split_reconciles_exactly(self):
        expense = Expense(
            "Test", 1000, "Sami", ["Sami", "Mariam", "Yusuf"], None
        )
        strategy = EqualSplit()
        splits = strategy.calculate_splits(expense)
        self.assertEqual(sum(splits.values()), 1000)
        self.assertEqual(splits["Sami"], 334)
        self.assertEqual(splits["Mariam"], 333)
        self.assertEqual(splits["Yusuf"], 333)

    def test_shares_split(self):
        expense = Expense(
            "Test", 1000, "Sami", ["Sami", "Mariam", "Yusuf"], None
        )
        strategy = SharesSplit({"Sami": 2, "Mariam": 1, "Yusuf": 0})
        splits = strategy.calculate_splits(expense)
        self.assertEqual(sum(splits.values()), 1000)
        self.assertEqual(splits["Sami"], 667)
        self.assertEqual(splits["Mariam"], 333)
        self.assertEqual(splits["Yusuf"], 0)

    def test_percentage_split_rejects_invalid_sum(self):
        Expense("Test", 1000, "Sami", ["Sami", "Mariam"], None)
        with self.assertRaises(ValueError):
            PercentageSplit({"Sami": Decimal("50"), "Mariam": Decimal("40")})

    def test_percentage_split(self):
        expense = Expense(
            "Test", 1000, "Sami", ["Sami", "Mariam", "Yusuf"], None
        )
        strategy = PercentageSplit(
            {
                "Sami": Decimal("33.33"),
                "Mariam": Decimal("33.33"),
                "Yusuf": Decimal("33.34"),
            }
        )
        splits = strategy.calculate_splits(expense)
        self.assertEqual(sum(splits.values()), 1000)
        self.assertEqual(splits["Sami"], 333)
        self.assertEqual(splits["Mariam"], 333)
        self.assertEqual(splits["Yusuf"], 334)

    def test_exact_split_rejects_invalid_sum(self):
        expense = Expense("Test", 1000, "Sami", ["Sami", "Mariam"], None)
        with self.assertRaises(ValueError):
            ExactSplit({"Sami": 500, "Mariam": 400}).calculate_splits(expense)

    def test_exact_split(self):
        expense = Expense("Test", 1000, "Sami", ["Sami", "Mariam"], None)
        strategy = ExactSplit({"Sami": 600, "Mariam": 400})
        splits = strategy.calculate_splits(expense)
        self.assertEqual(sum(splits.values()), 1000)
        self.assertEqual(splits["Sami"], 600)
        self.assertEqual(splits["Mariam"], 400)

    def test_split_rejects_mismatched_participants(self):
        expense = Expense("Test", 1000, "Sami", ["Sami", "Mariam"], None)
        with self.assertRaises(ValueError):
            ExactSplit({"Sami": 1000}).calculate_splits(expense)

    def test_itemised_split(self):
        expense = Expense(
            description="Grocery receipt",
            amount_pence=4500,
            payer="Mariam",
            participants=["Mariam", "Sami"],
            date=datetime.now(timezone.utc),
        )
        # Mariam and Sami split bread (1000)
        # Sami exclusively pays for cheese (2000)
        # Mariam exclusively pays for apples (1500)
        items = [
            Item("Bread", 1000, ["Mariam", "Sami"]),
            Item("Cheese", 2000, ["Sami"]),
            Item("Apples", 1500, ["Mariam"]),
        ]
        strategy = ItemisedSplit(items)
        splits = strategy.calculate_splits(expense)
        
        # Sami's share: 500 (bread) + 2000 (cheese) = 2500
        # Mariam's share: 500 (bread) + 1500 (apples) = 2000
        self.assertEqual(splits["Sami"], 2500)
        self.assertEqual(splits["Mariam"], 2000)

    def test_itemised_split_validation(self):
        expense = Expense(
            description="Invalid receipt",
            amount_pence=1000,
            payer="Mariam",
            participants=["Mariam", "Sami"],
            date=datetime.now(timezone.utc),
        )
        # Total items don't match expense
        items = [Item("Bread", 500, ["Mariam", "Sami"])]
        strategy = ItemisedSplit(items)
        with self.assertRaises(ValueError):
            strategy.calculate_splits(expense)


if __name__ == "__main__":
    unittest.main()
