import unittest
from tally.ledger import Ledger
from tally.notifier import FakeOutput
from tally.cli import TallyCLI
from tally.clock import FakeClock
from datetime import datetime, timezone


class TestTallyCLI(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger()
        self.output = FakeOutput()
        self.clock = FakeClock(datetime(2023, 1, 1, tzinfo=timezone.utc))
        self.cli = TallyCLI(self.ledger, self.output, self.clock)

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

    def test_clock_wiring(self):
        # We want to verify that the CLI uses the injected clock
        self.cli.do_add_user("Sami")
        self.cli.do_expense("Sami £10.00 Lunch")
        
        # Access the history in ledger to inspect the command and its entry
        last_command = self.ledger._history[-1]
        entry = last_command._wrapped.entry if hasattr(last_command, "_wrapped") else last_command.entry
        self.assertEqual(entry.date, datetime(2023, 1, 1, tzinfo=timezone.utc))

    def test_cli_add_user_errors(self):
        self.cli.do_add_user("")
        self.assertIn("Error: Please provide a name.", self.output.messages)

        self.cli.do_add_user("Sami")
        self.cli.do_add_user("Sami")
        self.assertIn("Error: Sami is already registered.", self.output.messages)

    def test_cli_expense_format_and_unregistered(self):
        self.cli.do_add_user("Sami")
        self.cli.do_expense("Sami")
        self.assertIn("Error: Expected format: expense <payer> <amount> <description>", self.output.messages)

        self.cli.do_expense("Mariam £10.00 Lunch")
        self.assertIn("Error: Mariam is not a registered user.", self.output.messages)

        self.cli.do_expense("Sami invalid_amount Lunch")
        self.assertIn("Error: invalid literal for int() with base 10: 'invalid_amount'", self.output.messages)

    def test_cli_settle_errors(self):
        self.cli.do_add_user("Sami")
        self.cli.do_settle("Sami")
        self.assertIn("Error: Expected format: settle <payer> <payee> <amount>", self.output.messages)

        self.cli.do_settle("Sami Mariam £10.00")
        self.assertIn("Error: Both payer and payee must be registered users.", self.output.messages)

    def test_cli_no_users_balance_and_suggest(self):
        self.cli.do_balance("")
        self.assertIn("No users registered.", self.output.messages)

        self.cli.do_suggest_settlements("")
        self.assertIn("No users registered.", self.output.messages)

    def test_suggest_settlements_already_settled(self):
        self.cli.do_add_user("Sami")
        self.cli.do_suggest_settlements("")
        self.assertIn("All balances are settled! Nothing to do.", self.output.messages)

    def test_suggest_settlements_value_error(self):
        self.cli.do_add_user("Sami")
        # Forcing an imbalance to trigger ValueError
        self.ledger._balances["Sami"] = 100
        self.cli.do_suggest_settlements("")
        self.assertTrue(any("Balances do not sum to exactly 0" in msg for msg in self.output.messages))

    def test_cli_quit_and_exit(self):
        self.assertTrue(self.cli.do_quit(""))
        self.assertIn("Goodbye!", self.output.messages)
        self.assertTrue(self.cli.do_exit(""))

    def test_expense_broad_exception(self):
        self.cli.do_add_user("Sami")
        # trigger unexpected exception in execute
        original_execute = self.ledger.execute
        self.ledger.execute = None  # break the ledger to raise TypeError
        try:
            self.cli.do_expense("Sami £10.00 Lunch")
            self.assertTrue(any("Unexpected Error:" in msg for msg in self.output.messages))
        finally:
            self.ledger.execute = original_execute

    def test_settle_value_error(self):
        self.cli.do_add_user("Sami")
        self.cli.do_add_user("Mariam")
        self.cli.do_settle("Sami Mariam invalid_amount")
        self.assertIn("Error: invalid literal for int() with base 10: 'invalid_amount'", self.output.messages)


if __name__ == "__main__":
    unittest.main()
