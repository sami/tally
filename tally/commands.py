from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, TYPE_CHECKING

from tally.models import Expense
from tally.splitting import SplitStrategy

if TYPE_CHECKING:
    from tally.ledger import Ledger
    from tally.notifier import Output


class Command(ABC):
    """
    I used the Command Pattern here because if the Ledger simply added/subtracted
    balances instantly, I could never "Undo" without manually keeping track of
    exactly how much money moved where.
    By wrapping an entire action into a "Command" object with an `execute()` and
    `undo()` method, the Ledger can just keep a history stack of these objects.
    To undo, it just pops the last command and calls `.undo()`.
    """

    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass


class ApplyExpenseCommand(Command):
    def __init__(
        self, ledger: Ledger, expense: Expense, strategy: SplitStrategy
    ):
        self.ledger = ledger
        self.expense = expense
        self.strategy = strategy
        self.changes: Dict[str, int] = {}
        self.splits: Dict[str, int] = {}

    def execute(self) -> None:
        self.splits = self.strategy.calculate_splits(self.expense)

        self.changes = {p: -amount for p, amount in self.splits.items()}
        self.changes[self.expense.payer] = (
            self.changes.get(self.expense.payer, 0) + self.expense.amount_pence
        )

        for member, change in self.changes.items():
            self.ledger.change_balance(member, change)

    def undo(self) -> None:
        if not self.changes:
            return
        # Revert the balance changes
        for member, change in self.changes.items():
            self.ledger.change_balance(member, -change)


class CommandDecorator(Command):
    def __init__(self, wrapped: Command):
        self._wrapped = wrapped

    def execute(self) -> None:
        self._wrapped.execute()

    def undo(self) -> None:
        self._wrapped.undo()


class LoggingCommandDecorator(CommandDecorator):
    """
    I used the Decorator Pattern because I want to log whenever a command executes
    or undos. I COULD put `print("Logging...")` inside `ApplyExpenseCommand.execute()`,
    but that violates the Single Responsibility Principle (it shouldn't care about logging).
    Instead, I "wrap" the command in this Decorator. This decorator implements the
    exact same interface (`Command`), but intercepts the calls, logs what it needs to,
    and forwards the real work to the wrapped command.
    """

    def __init__(
        self, wrapped_command: Command, action_name: str, output: "Output"
    ):
        super().__init__(wrapped_command)
        self.name = action_name
        self.output = output

    def execute(self) -> None:
        self.output.write(f"[Log] Executing: {self.name}")
        super().execute()
        self.output.write(f"[Log] Execution successful: {self.name}")

    def undo(self) -> None:
        self.output.write(f"[Log] Undoing: {self.name}")
        super().undo()
        self.output.write(f"[Log] Undo successful: {self.name}")
