from dataclasses import dataclass
from typing import List
from datetime import datetime
from tally.models import Expense
from tally.money import parse_pounds_to_pence


@dataclass(frozen=True)
class ExternalRecord:
    paid_by: str
    for_whom: List[str]
    cost_str: str
    occurred_at: str
    description: str


def adapt_external_record(record: ExternalRecord) -> Expense:
    amount_pence = parse_pounds_to_pence(record.cost_str)
    # Parse ISO 8601 string. Python 3.11 natively handles 'Z',
    # but for Python 3.8+ compatibility, replace 'Z' with '+00:00'
    date_str = record.occurred_at.replace("Z", "+00:00")
    date_obj = datetime.fromisoformat(date_str)

    return Expense(
        description=record.description,
        amount_pence=amount_pence,
        payer=record.paid_by,
        participants=record.for_whom,
        date=date_obj,
    )
