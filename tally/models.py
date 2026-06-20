from dataclasses import dataclass
from typing import List
from datetime import datetime
from enum import Enum, auto


class EntryType(Enum):
    EXPENSE = auto()
    SETTLEMENT = auto()


@dataclass(frozen=True)
class Entry:
    description: str
    amount_pence: int
    payer: str
    participants: List[str]
    date: datetime
    entry_type: EntryType


@dataclass(frozen=True)
class Expense(Entry):
    pass


@dataclass(frozen=True)
class Settlement(Entry):
    pass
