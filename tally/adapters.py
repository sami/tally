from dataclasses import dataclass
from typing import List
from datetime import datetime
from tally.models import Expense, EntryType
from tally.money import parse_pounds_to_pence


@dataclass(frozen=True)
class ExternalRecord:
    paid_by: str
    for_whom: List[str]
    cost_str: str
    occurred_at: str
    description: str


def adapt_external_record(record: ExternalRecord) -> Expense:
    """
    I used the Adapter Pattern here because if I fetch expenses from an external API
    or legacy JSON file, they might use 'cost' instead of 'amount', or have weird
    string date formats.
    If I let `ExternalRecord` directly into the system, the entire codebase
    would become coupled to their messy format.
    The Adapter acts as a quarantine barrier. It translates the external shape
    into my pristine, sanitised `Expense` model right at the edge of the app.
    """
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
        entry_type=EntryType.EXPENSE,
    )
