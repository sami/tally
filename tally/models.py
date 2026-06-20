from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass(frozen=True)
class Expense:
    description: str
    amount_pence: int
    payer: str
    participants: List[str]
    date: datetime
