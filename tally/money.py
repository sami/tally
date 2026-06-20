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
