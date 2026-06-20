from typing import Dict, List

def parse_pounds_to_pence(pounds_str: str) -> int:
    """
    Parses a string representing pounds (e.g. '£60.00' or '£42') into integer pence.
    """
    cleaned = pounds_str.replace('£', '').replace(',', '').strip()
    if '.' in cleaned:
        pounds, pence = cleaned.split('.')
        # Pad pence with zeros if necessary (e.g., '60.5' -> '50')
        pence = pence.ljust(2, '0')[:2]
        return int(pounds) * 100 + int(pence)
    else:
        return int(cleaned) * 100

def format_pence_to_pounds(pence: int) -> str:
    """
    Formats integer pence into a pounds string (e.g. 6000 -> '£60.00', -150 -> '-£1.50').
    """
    sign = "-" if pence < 0 else ""
    abs_pence = abs(pence)
    pounds = abs_pence // 100
    remainder = abs_pence % 100
    return f"{sign}£{pounds}.{remainder:02d}"

def allocate_pennies(total_pence: int, weights: Dict[str, int], order: List[str]) -> Dict[str, int]:
    """
    Distributes total_pence across participants according to weights.
    Extra pennies are distributed one by one according to the provided order
    to participants who have a weight greater than 0.
    """
    total_weight = sum(weights.values())
    if total_weight == 0:
        return {p: 0 for p in order}

    splits = {}
    for p in order:
        splits[p] = (total_pence * weights.get(p, 0)) // total_weight

    allocated = sum(splits.values())
    remainder = total_pence - allocated

    # Distribute remainder starting with those who had the highest weight.
    # Because sort is stable, ties are broken by the original 'order' list.
    remainder_order = sorted(order, key=lambda p: weights.get(p, 0), reverse=True)

    for p in remainder_order:
        if remainder <= 0:
            break
        if weights.get(p, 0) > 0:
            splits[p] += 1
            remainder -= 1

    return splits

