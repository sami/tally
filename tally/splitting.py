from abc import ABC, abstractmethod
from typing import Dict, List
from dataclasses import dataclass
from decimal import Decimal
from tally.models import Expense
from tally.money import allocate_pennies


class SplitStrategy(ABC):
    """
    I used the Strategy Pattern here because there are many ways to split a bill
    (Equal, Exact, Percentage, Itemised). If I put all that maths inside
    `Ledger.execute()`, the Ledger class would become massive and hard to read.
    By defining an abstract base class (interface), I can pull the maths out into
    tiny, isolated, polymorphic classes. The Ledger just calls `.calculate_splits()`,
    oblivious to which strategy it's actually running!
    """

    @abstractmethod
    def calculate_splits(self, expense: Expense) -> Dict[str, int]:
        pass

    def _validate_participants(
        self, expense: Expense, configured_participants: set
    ):
        if set(expense.participants) != configured_participants:
            raise ValueError(
                "Split participants do not match expense participants"
            )


class EqualSplit(SplitStrategy):
    def calculate_splits(self, expense: Expense) -> Dict[str, int]:
        weights = {p: 1 for p in expense.participants}
        return allocate_pennies(
            expense.amount_pence, weights, expense.participants
        )


class SharesSplit(SplitStrategy):
    def __init__(self, shares: Dict[str, int]):
        self.shares = shares

    def calculate_splits(self, expense: Expense) -> Dict[str, int]:
        self._validate_participants(expense, set(self.shares.keys()))
        return allocate_pennies(
            expense.amount_pence, self.shares, expense.participants
        )


class PercentageSplit(SplitStrategy):
    def __init__(self, percentages: Dict[str, Decimal]):
        if sum(percentages.values()) != Decimal("100"):
            raise ValueError("Percentages must sum to 100")
        self.percentages = percentages

    def calculate_splits(self, expense: Expense) -> Dict[str, int]:
        self._validate_participants(expense, set(self.percentages.keys()))
        # Convert percentages to integer weights by multiplying by 100
        # Example: 33.33 -> 3333
        weights = {p: int(pct * 100) for p, pct in self.percentages.items()}
        return allocate_pennies(
            expense.amount_pence, weights, expense.participants
        )


class ExactSplit(SplitStrategy):
    def __init__(self, amounts: Dict[str, int]):
        self.amounts = amounts

    def calculate_splits(self, expense: Expense) -> Dict[str, int]:
        self._validate_participants(expense, set(self.amounts.keys()))
        if sum(self.amounts.values()) != expense.amount_pence:
            raise ValueError(
                "Exact split amounts must sum to the expense total"
            )
        return self.amounts.copy()


@dataclass(frozen=True)
class Item:
    description: str
    amount_pence: int
    participants: List[str]


class ItemisedSplit(SplitStrategy):
    def __init__(self, items: List[Item]):
        self.items = items

    def calculate_splits(self, expense: Expense) -> Dict[str, int]:
        total_items = sum(item.amount_pence for item in self.items)
        if total_items != expense.amount_pence:
            raise ValueError(
                f"Sum of items ({total_items}) must equal expense total ({expense.amount_pence})"
            )

        unique_participants = set()
        for item in self.items:
            unique_participants.update(item.participants)

        self._validate_participants(expense, unique_participants)

        final_splits = {p: 0 for p in expense.participants}
        for item in self.items:
            weights = {p: 1 for p in item.participants}
            splits = allocate_pennies(
                item.amount_pence, weights, item.participants
            )
            for p, amt in splits.items():
                final_splits[p] += amt

        return final_splits
