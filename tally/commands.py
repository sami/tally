from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, TYPE_CHECKING

from tally.models import Expense
from tally.splitting import SplitStrategy

if TYPE_CHECKING:
    from tally.ledger import Ledger

class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass

class ApplyExpenseCommand(Command):
    def __init__(self, ledger: Ledger, expense: Expense, strategy: SplitStrategy):
        self.ledger = ledger
        self.expense = expense
        self.strategy = strategy
        self.changes: Dict[str, int] = {}
        self.splits: Dict[str, int] = {}

    def execute(self) -> None:
        self.splits = self.strategy.calculate_splits(self.expense)
        
        self.changes = {p: -amount for p, amount in self.splits.items()}
        self.changes[self.expense.payer] = self.changes.get(self.expense.payer, 0) + self.expense.amount_pence

        for member, change in self.changes.items():
            self.ledger.change_balance(member, change)

    def undo(self) -> None:
        if not self.changes:
            return
        # Revert the balance changes
        for member, change in self.changes.items():
            self.ledger.change_balance(member, -change)
