import unittest
from tally.ledger import Ledger
from tally.notifier import FakeOutput
from tally.cli import TallyCLI


class TestTallyCLI(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger()
        self.output = FakeOutput()
        self.cli = TallyCLI(self.ledger, self.output)

    def tearDown(self):
        Ledger.reset()

    def test_add_user(self):
        self.cli.do_add_user("Sami")
        self.assertIn("Sami", self.cli.users)
        self.assertIn("Added user: Sami", self.output.messages)

    def test_expense_requires_users(self):
        self.cli.do_expense("Sami £90.00 Dinner")
        self.assertIn(
            "Error: No users registered. Use add_user first.",
            self.output.messages,
        )

    def test_expense_and_balance(self):
        self.cli.do_add_user("Sami")
        self.cli.do_add_user("Mariam")
        self.cli.do_expense("Sami £10.00 Lunch")

        # Sami pays £10. Sami's share is £5, Mariam's share is £5.
        # Sami net +£5, Mariam net -£5.
        self.cli.do_balance("")

        self.assertIn("Sami: £5.00", self.output.messages)
        self.assertIn("Mariam: -£5.00", self.output.messages)

    def test_settle(self):
        self.cli.do_add_user("Sami")
        self.cli.do_add_user("Mariam")

        self.cli.do_settle("Mariam Sami £5.00")

        # Mariam pays Sami £5.
        self.cli.do_balance("")
        self.assertIn("Mariam: £5.00", self.output.messages)
        self.assertIn("Sami: -£5.00", self.output.messages)

    def test_undo(self):
        self.cli.do_add_user("Sami")
        self.cli.do_add_user("Mariam")
        self.cli.do_expense("Sami £10.00 Lunch")

        self.cli.do_undo("")

        self.cli.do_balance("")
        self.assertIn("Sami: £0.00", self.output.messages)
        self.assertIn("Mariam: £0.00", self.output.messages)

    def test_suggest_settlements(self):
        self.cli.do_add_user("Sami")
        self.cli.do_add_user("Mariam")

        # Sami pays £10. Sami is owed £5, Mariam owes £5.
        self.cli.do_expense("Sami £10.00 Lunch")
        self.cli.do_suggest_settlements("")

        self.assertIn("Mariam should pay Sami £5.00", self.output.messages)


if __name__ == "__main__":
    unittest.main()
