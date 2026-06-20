from typing import Dict, List, Tuple


def suggest_optimal_settlements(
    balances: Dict[str, int],
) -> List[Tuple[str, str, int]]:
    """
    I used a Dynamic Programming approach here because a naive "greedy" algorithm
    (largest debtor pays largest creditor) works to clear debts, but often results
    in unnecessary extra transactions.
    If I want to PROVABLY minimise the number of transactions, it's equivalent to
    finding the maximum number of disjoint subsets that sum to exactly £0.00.
    This is an NP-hard problem. I used "Bitmask Dynamic Programming over Subsets"
    ($O(3^N)$) to find all perfect zero-sum partitions. Inside those partitions,
    greedy matching is mathematically guaranteed to be perfectly optimal!
    """
    # 1. Filter out users with £0.00 balances
    items = [(u, b) for u, b in balances.items() if b != 0]
    n = len(items)
    if n == 0:
        return []

    if sum(b for u, b in items) != 0:
        raise ValueError("Balances do not sum to exactly 0.")

    # 2. DP to find maximum disjoint zero-sum subsets
    sum_mask = [0] * (1 << n)
    dp = [0] * (1 << n)
    prev = [-1] * (1 << n)

    for mask in range(1, 1 << n):
        # Calculate sum for the mask efficiently
        lsb = mask & -mask
        lsb_idx = lsb.bit_length() - 1
        sum_mask[mask] = sum_mask[mask ^ lsb] + items[lsb_idx][1]

        if sum_mask[mask] == 0:
            best_val = 0
            best_sub = -1

            # Iterate through all submasks
            sub = (mask - 1) & mask
            while sub > 0:
                if sum_mask[sub] == 0:
                    val = dp[sub] + dp[mask ^ sub]
                    if val > best_val:
                        best_val = val
                        best_sub = sub
                sub = (sub - 1) & mask

            if best_sub == -1:
                # Cannot be split into smaller zero-sum subsets
                dp[mask] = 1
                prev[mask] = mask
            else:
                dp[mask] = best_val
                prev[mask] = best_sub

    # 3. Reconstruct optimal partitions
    partitions = []

    def reconstruct(mask):
        if mask == 0:
            return
        if prev[mask] == mask:
            partitions.append(mask)
        else:
            reconstruct(prev[mask])
            reconstruct(mask ^ prev[mask])

    reconstruct((1 << n) - 1)

    # 4. Greedily settle within each minimal zero-sum partition
    transactions = []
    for part in partitions:
        debtors = []
        creditors = []
        for i in range(n):
            if part & (1 << i):
                u, b = items[i]
                if b < 0:
                    # debtors owe money
                    debtors.append([u, -b])
                elif b > 0:
                    # creditors are owed money
                    creditors.append([u, b])

        d_idx, c_idx = 0, 0
        while d_idx < len(debtors) and c_idx < len(creditors):
            d_u, d_amt = debtors[d_idx]
            c_u, c_amt = creditors[c_idx]

            settled = min(d_amt, c_amt)
            transactions.append((d_u, c_u, settled))

            debtors[d_idx][1] -= settled
            creditors[c_idx][1] -= settled

            if debtors[d_idx][1] == 0:
                d_idx += 1
            if creditors[c_idx][1] == 0:
                c_idx += 1

    return transactions
