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

