from abc import ABC, abstractmethod
from tally.notifier import Output
from tally.money import format_pence_to_pounds


class Listener(ABC):
    """
    I used the Observer Pattern here because when a ledger balance changes, I might
    want to print a report, or check if the user went over their debt threshold.
    If I put `if new_balance < -5000: print("ALERT")` directly inside `Ledger.change_balance`,
    the Ledger becomes coupled to output formatting and business logic limits.
    Instead, the Ledger just announces "Balance Changed!" to its Observers (Listeners).
    These independent classes then react passively.
    """

    @abstractmethod
    def on_balance_change(self, member: str, new_balance: int) -> None:
        pass


class BalanceReportListener(Listener):
    def __init__(self, output: Output):
        self.output = output

    def on_balance_change(self, member: str, new_balance: int) -> None:
        formatted_balance = format_pence_to_pounds(new_balance)
        self.output.write(
            f"Balance Report: {member} is now at {formatted_balance}"
        )


class ThresholdAlertListener(Listener):
    def __init__(self, threshold_pence: int, output: Output):
        self.threshold_pence = threshold_pence
        self.output = output

    def on_balance_change(self, member: str, new_balance: int) -> None:
        if new_balance < -self.threshold_pence:
            owed = format_pence_to_pounds(-new_balance)
            self.output.write(
                f"ALERT: {member} owes {owed}, exceeding the limit."
            )
