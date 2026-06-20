import unittest
from datetime import datetime, timezone
from tally.ledger import Ledger
from tally.commands import ApplyExpenseCommand
from tally.models import Expense
from tally.splitting import EqualSplit

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

if __name__ == "__main__":
    unittest.main()
