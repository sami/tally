import unittest
from datetime import datetime, timezone
from tally.ledger import Ledger
from tally.commands import (
    ApplyExpenseCommand,
    Command,
    LoggingCommandDecorator,
)
from tally.models import Expense
from tally.splitting import EqualSplit
from tally.notifier import FakeOutput


class TestApplyExpenseCommand(unittest.TestCase):
    def test_execute_alters_balances_and_undo_reverts_them(self):
        ledger = Ledger()
        expense = Expense(
            description="Lunch",
            amount_pence=3000,
            payer="Sami",
            participants=["Sami", "Mariam", "Yusuf"],
            date=datetime.now(timezone.utc),
        )
        strategy = EqualSplit()
        command = ApplyExpenseCommand(ledger, expense, strategy)

        # Pre-execution: Everyone is at 0
        self.assertEqual(ledger.get_balance("Sami"), 0)

        # Execute
        ledger.execute(command)

        # Post-execution: Sami paid 3000, his share is 1000. Net +2000.
        # Mariam and Yusuf each share 1000. Net -1000.
        self.assertEqual(ledger.get_balance("Sami"), 2000)
        self.assertEqual(ledger.get_balance("Mariam"), -1000)
        self.assertEqual(ledger.get_balance("Yusuf"), -1000)

        # Undo
        ledger.undo_last()

        # Reverted back to 0
        self.assertEqual(ledger.get_balance("Sami"), 0)
        self.assertEqual(ledger.get_balance("Mariam"), 0)
        self.assertEqual(ledger.get_balance("Yusuf"), 0)


class DummyCommand(Command):
    def __init__(self):
        self.executed = False
        self.undone = False

    def execute(self) -> None:
        self.executed = True

    def undo(self) -> None:
        self.undone = True


class TestLoggingCommandDecorator(unittest.TestCase):
    def test_decorator_logs_and_delegates(self):
        cmd = DummyCommand()
        output = FakeOutput()
        decorated = LoggingCommandDecorator(cmd, "TestCmd", output)

        decorated.execute()
        self.assertTrue(cmd.executed)
        self.assertIn("[Log] Executing: TestCmd", output.messages)
        self.assertIn("[Log] Execution successful: TestCmd", output.messages)

        decorated.undo()
        self.assertTrue(cmd.undone)
        self.assertIn("[Log] Undoing: TestCmd", output.messages)
        self.assertIn("[Log] Undo successful: TestCmd", output.messages)


if __name__ == "__main__":
    unittest.main()
