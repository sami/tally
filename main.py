from tally.adapters import ExternalRecord, adapt_external_record
from tally.ledger import Ledger
from tally.commands import ApplyExpenseCommand
from tally.notifier import RealOutput
from tally.observers import BalanceReportListener, ThresholdAlertListener
from tally.splitting import EqualSplit, SharesSplit, ExactSplit
from tally.money import format_pence_to_pounds


def main():
    # 1. Composition Root Setup
    ledger = Ledger()
    output = RealOutput()

    # Register listeners
    ledger.add_listener(BalanceReportListener(output))
    # Alert threshold is £50 (5000 pence)
    ledger.add_listener(
        ThresholdAlertListener(threshold_pence=5000, output=output)
    )

    output.write("--- Starting Tally ---\n")

    # 2. Realistic Sequence

    # Expense 1: Sami pays for dinner for Sami, Mariam, Yusuf
    record1 = ExternalRecord(
        paid_by="Sami",
        for_whom=["Sami", "Mariam", "Yusuf"],
        cost_str="£90.00",
        occurred_at="2023-10-25T19:30:00Z",
        description="Dinner at Nando's",
    )
    expense1 = adapt_external_record(record1)
    strategy1 = EqualSplit()
    output.write(
        f"--- [Expense] {expense1.payer} paid {record1.cost_str} for {expense1.description} ---"
    )
    ledger.execute(ApplyExpenseCommand(ledger, expense1, strategy1))

    # Expense 2: Mariam pays for hotel for Mariam and Yusuf
    record2 = ExternalRecord(
        paid_by="Mariam",
        for_whom=["Mariam", "Yusuf"],
        cost_str="£150.00",
        occurred_at="2023-10-26T10:00:00Z",
        description="Hotel booking",
    )
    expense2 = adapt_external_record(record2)
    # Yusuf gets 2 shares, Mariam gets 1 share
    strategy2 = SharesSplit({"Mariam": 1, "Yusuf": 2})
    output.write(
        f"\n--- [Expense] {expense2.payer} paid {record2.cost_str} for {expense2.description} ---"
    )
    ledger.execute(ApplyExpenseCommand(ledger, expense2, strategy2))
    # Yusuf's share of £150 is £100. He already owed £30. Total debt = £130.
    # This will trigger the alert since threshold is £50!

    # Expense 3: Settlement - Yusuf pays Mariam £100
    record3 = ExternalRecord(
        paid_by="Yusuf",
        for_whom=["Mariam"],
        cost_str="£100.00",
        occurred_at="2023-10-27T09:00:00Z",
        description="Settlement",
    )
    expense3 = adapt_external_record(record3)
    # Yusuf fronts £100, Mariam's share of this "expense" is £100
    strategy3 = ExactSplit({"Mariam": 10000})
    output.write(
        f"\n--- [Settlement] {expense3.payer} pays {record3.cost_str} to {expense3.participants[0]} ---"
    )
    ledger.execute(ApplyExpenseCommand(ledger, expense3, strategy3))

    output.write("\n--- Current Balances ---")
    for member in ["Sami", "Mariam", "Yusuf"]:
        balance = ledger.get_balance(member)
        output.write(f"{member}: {format_pence_to_pounds(balance)}")
        
    # Expense 4: Intentional Mistake
    record4 = ExternalRecord(
        paid_by="Yusuf",
        for_whom=["Sami", "Mariam", "Yusuf"],
        cost_str="£300.00",
        occurred_at="2023-10-28T12:00:00Z",
        description="Mistake Expense"
    )
    expense4 = adapt_external_record(record4)
    strategy4 = EqualSplit()
    output.write(
        f"\n--- [Expense] {expense4.payer} paid {record4.cost_str} for {expense4.description} ---"
    )
    ledger.execute(ApplyExpenseCommand(ledger, expense4, strategy4))
    
    # Oh no, we didn't mean to do that! Let's undo.
    output.write("\n--- [Undo] Reverting the last expense ---")
    ledger.undo_last()
    
    output.write("\n--- Final Balances ---")
    for member in ["Sami", "Mariam", "Yusuf"]:
        balance = ledger.get_balance(member)
        output.write(f"{member}: {format_pence_to_pounds(balance)}")


if __name__ == "__main__":
    main()
