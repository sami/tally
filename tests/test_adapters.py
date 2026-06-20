import unittest
from datetime import datetime, timezone
from tally.adapters import ExternalRecord, adapt_external_record
from tally.models import Expense, EntryType


class TestAdapters(unittest.TestCase):
    def test_adapter_normalises_money_date_and_field_names(self):
        # The external record has a different shape
        # Money is a string with a currency symbol
        # Date is an ISO 8601 string
        # Field names are different (e.g. 'paid_by' instead of 'payer')
        external_record = ExternalRecord(
            paid_by="Sami",
            for_whom=["Sami", "Mariam", "Yusuf"],
            cost_str="£60.00",
            occurred_at="2023-10-25T19:30:00Z",
            description="Dinner",
        )

        expense = adapt_external_record(external_record)

        self.assertIsInstance(expense, Expense)
        self.assertEqual(expense.payer, "Sami")
        self.assertEqual(expense.participants, ["Sami", "Mariam", "Yusuf"])
        # Money should be normalised to integer pence
        self.assertEqual(expense.amount_pence, 6000)
        # Date should be normalised to a datetime object
        expected_date = datetime(2023, 10, 25, 19, 30, tzinfo=timezone.utc)
        self.assertEqual(expense.date, expected_date)
        self.assertEqual(expense.description, "Dinner")

    def test_adapter_handles_money_without_pence(self):
        external_record = ExternalRecord(
            paid_by="Sami",
            for_whom=["Sami"],
            cost_str="£42",
            occurred_at="2023-10-25T19:30:00Z",
            description="Book",
        )
        expense = adapt_external_record(external_record)
        self.assertEqual(expense.amount_pence, 4200)


if __name__ == "__main__":
    unittest.main()
