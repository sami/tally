import unittest
from tally.ledger import Ledger

class TestLedgerSingleton(unittest.TestCase):
    def setUp(self):
        # Reset the ledger before each test to ensure test isolation
        Ledger.reset()

    def test_two_requests_return_same_instance(self):
        ledger1 = Ledger()
        ledger2 = Ledger()
        self.assertIs(ledger1, ledger2, "Multiple requests for Ledger should return the same instance")

    def test_reset_clears_balances_and_history(self):
        ledger = Ledger()
        # Manually inject dummy data to verify reset clears it
        ledger._balances["test_user"] = 100
        ledger._history.append("dummy_entry")
        
        Ledger.reset()
        
        ledger_after_reset = Ledger()
        self.assertEqual(len(ledger_after_reset._balances), 0, "Balances should be empty after reset")
        self.assertEqual(len(ledger_after_reset._history), 0, "History should be empty after reset")

    def test_initial_zero_sum_invariant(self):
        ledger = Ledger()
        # Since there are no balances, sum is 0. But let's check it.
        total = sum(ledger._balances.values())
        self.assertEqual(total, 0, "The zero-sum invariant must hold (initially 0)")

if __name__ == '__main__':
    unittest.main()
