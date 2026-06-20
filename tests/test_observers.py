import unittest
from tally.ledger import Ledger
from tally.observers import (
    Listener,
    BalanceReportListener,
    ThresholdAlertListener,
)
from tally.notifier import FakeOutput


class DummyListener(Listener):
    def __init__(self):
        self.notified_changes = []

    def on_balance_change(self, member: str, new_balance: int):
        self.notified_changes.append((member, new_balance))


class TestObservers(unittest.TestCase):
    def setUp(self):
        Ledger.reset()

    def test_ledger_registers_and_notifies_listeners(self):
        ledger = Ledger()
        listener = DummyListener()
        ledger.add_listener(listener)

        # We manually trigger _notify_listeners to simulate an announced change.
        ledger._notify_listeners("Sami", -2000)

        self.assertEqual(len(listener.notified_changes), 1)
        self.assertEqual(listener.notified_changes[0], ("Sami", -2000))

    def test_balance_report_listener(self):
        fake_output = FakeOutput()
        listener = BalanceReportListener(output=fake_output)

        listener.on_balance_change("Sami", -2000)

        # The balance report states each member's current position.
        self.assertEqual(len(fake_output.messages), 1)
        self.assertIn("Sami", fake_output.messages[0])
        self.assertIn("-£20.00", fake_output.messages[0])

    def test_threshold_alert_listener_fires_above_limit(self):
        fake_output = FakeOutput()
        # Limit of 5000 pence (£50)
        listener = ThresholdAlertListener(
            threshold_pence=5000, output=fake_output
        )

        # Owe more than £50 (balance < -5000)
        listener.on_balance_change("Sami", -6000)
        self.assertEqual(len(fake_output.messages), 1)
        self.assertIn("Sami owes", fake_output.messages[0])

    def test_threshold_alert_listener_stays_silent_below_limit(self):
        fake_output = FakeOutput()
        # Limit of 5000 pence (£50)
        listener = ThresholdAlertListener(
            threshold_pence=5000, output=fake_output
        )

        # Owe less than £50 (balance is -4000)
        listener.on_balance_change("Sami", -4000)
        self.assertEqual(len(fake_output.messages), 0)


if __name__ == "__main__":
    unittest.main()
