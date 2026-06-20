import unittest
from tally.settlement import suggest_optimal_settlements


class TestSettlement(unittest.TestCase):
    def test_basic_greedy(self):
        # A simple case where greedy and optimal are the same
        balances = {"A": -10, "B": -20, "C": 30}
        txs = suggest_optimal_settlements(balances)
        # N=3, K=1 subset. Min txs = 3 - 1 = 2
        self.assertEqual(len(txs), 2)

        # Verify the debts are cleared
        b_copy = balances.copy()
        for payer, payee, amt in txs:
            b_copy[payer] += amt
            b_copy[payee] -= amt

        for v in b_copy.values():
            self.assertEqual(v, 0)

    def test_optimal_beats_greedy(self):
        # A case where naive greedy (largest debtor to largest creditor) fails.
        # Balances: A:-10, B:-10, C:-5, D:15, E:10
        # If naive greedy:
        # D(15) gets 10 from A. D now 5.
        # D(5) gets 5 from B. D now 0, B now -5.
        # E(10) gets 5 from B. B now 0, E now 5.
        # E(5) gets 5 from C.
        # Total naive greedy transactions: 4.

        # But notice: A(-10) + E(10) = 0. B(-10) + C(-5) + D(15) = 0.
        # K = 2 subsets. N = 5.
        # Optimal transactions = 5 - 2 = 3.

        balances = {"A": -10, "B": -10, "C": -5, "D": 15, "E": 10}
        txs = suggest_optimal_settlements(balances)
        self.assertEqual(len(txs), 3)

        # Verify debts cleared
        b_copy = balances.copy()
        for payer, payee, amt in txs:
            b_copy[payer] += amt
            b_copy[payee] -= amt

        for v in b_copy.values():
            self.assertEqual(v, 0)

    def test_ignore_zeros(self):
        balances = {"A": -10, "B": 10, "C": 0}
        txs = suggest_optimal_settlements(balances)
        self.assertEqual(len(txs), 1)

    def test_no_transactions_needed(self):
        balances = {"A": 0, "B": 0}
        txs = suggest_optimal_settlements(balances)
        self.assertEqual(len(txs), 0)

    def test_throws_if_not_zero_sum(self):
        balances = {"A": -10, "B": 15}
        with self.assertRaises(ValueError):
            suggest_optimal_settlements(balances)


if __name__ == "__main__":
    unittest.main()
