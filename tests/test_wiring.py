import unittest
from datetime import datetime, timezone

from tally.adapters import ExternalRecord, adapt_external_record
from tally.clock import FakeClock
from tally.ledger import Ledger
from tally.notifier import FakeOutput
from tally.observers import BalanceReportListener, ThresholdAlertListener
from tally.splitting import EqualSplit, SharesSplit

class TestWiring(unittest.TestCase):
    def setUp(self):
        Ledger.reset()
        self.ledger = Ledger()
        self.output = FakeOutput()
        self.clock = FakeClock(datetime(2023, 1, 1, tzinfo=timezone.utc))
        
        # Wire up listeners
        self.ledger.add_listener(BalanceReportListener(self.output))
        self.ledger.add_listener(ThresholdAlertListener(threshold_pence=5000, output=self.output))

    def test_end_to_end_shared_expense_workflow(self):
        # 1. External system provides a record
        record1 = ExternalRecord(
            paid_by="Sami",
            for_whom=["Sami", "Mariam", "Yusuf"],
            cost_str="£60.00",
            occurred_at="2023-10-25T19:30:00Z",
            description="Dinner"
        )
        
        # 2. Adapter converts to internal Expense
        expense1 = adapt_external_record(record1)
        
        # 3. Strategy is chosen
        strategy1 = EqualSplit()
        
        # 4. Ledger applies it
        self.ledger.apply_expense(expense1, strategy1)
        
        # 5. Verify Ledger balances
        # Sami paid 6000. Share is 2000. Net +4000.
        # Mariam share 2000. Net -2000.
        # Yusuf share 2000. Net -2000.
        self.assertEqual(self.ledger.get_balance("Sami"), 4000)
        self.assertEqual(self.ledger.get_balance("Mariam"), -2000)
        self.assertEqual(self.ledger.get_balance("Yusuf"), -2000)
        
        # 6. Verify Listeners triggered correctly (2000 pence is under the £50 alert threshold)
        output_text = "\n".join(self.output.messages)
        self.assertIn("Balance Report: Sami is now at £40.00", output_text)
        self.assertIn("Balance Report: Mariam is now at -£20.00", output_text)
        self.assertIn("Balance Report: Yusuf is now at -£20.00", output_text)
        self.assertNotIn("ALERT", output_text)
        
        # Clear output to test next step cleanly
        self.output.messages.clear()
        
        # Next Expense: Mariam pays for a hotel, Yusuf gets 2 shares, Mariam 1 share, Sami 0
        record2 = ExternalRecord(
            paid_by="Mariam",
            for_whom=["Mariam", "Yusuf"],
            cost_str="£120.00",
            occurred_at="2023-10-26T10:00:00Z",
            description="Hotel"
        )
        expense2 = adapt_external_record(record2)
        strategy2 = SharesSplit({"Mariam": 1, "Yusuf": 2})
        self.ledger.apply_expense(expense2, strategy2)
        
        # Mariam paid 12000. Her share is 4000. Net from this: +8000.
        # Previous balance: -2000. New balance: +6000.
        # Yusuf paid 0. His share is 8000. Net from this: -8000.
        # Previous balance: -2000. New balance: -10000.
        # Sami is unaffected. Balance remains +4000.
        self.assertEqual(self.ledger.get_balance("Sami"), 4000)
        self.assertEqual(self.ledger.get_balance("Mariam"), 6000)
        self.assertEqual(self.ledger.get_balance("Yusuf"), -10000)
        
        # Yusuf is now at -£100.00, which exceeds the £50 threshold!
        output_text2 = "\n".join(self.output.messages)
        self.assertIn("Balance Report: Mariam is now at £60.00", output_text2)
        self.assertIn("Balance Report: Yusuf is now at -£100.00", output_text2)
        self.assertIn("ALERT: Yusuf owes £100.00, exceeding the limit.", output_text2)

if __name__ == '__main__':
    unittest.main()
