import cmd
from datetime import datetime, timezone
from typing import List

from tally.ledger import Ledger
from tally.notifier import Output
from tally.models import Expense, Settlement, EntryType
from tally.splitting import EqualSplit, ExactSplit
from tally.commands import ApplyEntryCommand, LoggingCommandDecorator
from tally.money import parse_pounds_to_pence, format_pence_to_pounds
from tally.settlement import suggest_optimal_settlements
from tally.clock import Clock


class TallyCLI(cmd.Cmd):
    intro = "Welcome to Tally. Type help or ? to list commands.\n"
    prompt = "(tally) "

    def __init__(self, ledger: Ledger, output: Output, clock: Clock):
        super().__init__()
        self.ledger = ledger
        self.output = output
        self.clock = clock
        self.users: List[str] = []

    def precmd(self, line):
        # Allow passing custom commands during tests smoothly
        return line

    def do_add_user(self, arg):
        """Add a user to the current session: add_user <name>"""
        name = arg.strip()
        if not name:
            self.output.write("Error: Please provide a name.")
            return
        if name in self.users:
            self.output.write(f"Error: {name} is already registered.")
            return
        self.users.append(name)
        self.output.write(f"Added user: {name}")

    def do_expense(self, arg):
        """Add an expense split equally among all registered users: expense <payer> <amount> <description>
        Example: expense Sami £90.00 Dinner at Nandos"""
        if not self.users:
            self.output.write(
                "Error: No users registered. Use add_user first."
            )
            return

        try:
            # Easiest way: payer, amount, *desc
            parts = arg.split(maxsplit=2)
            if len(parts) < 3:
                self.output.write(
                    "Error: Expected format: expense <payer> <amount> <description>"
                )
                return

            payer, amount_str, description = parts[0], parts[1], parts[2]

            if payer not in self.users:
                self.output.write(f"Error: {payer} is not a registered user.")
                return

            amount_pence = parse_pounds_to_pence(amount_str)

            expense = Expense(
                description=description,
                amount_pence=amount_pence,
                payer=payer,
                participants=self.users.copy(),
                date=self.clock.now(),
                entry_type=EntryType.EXPENSE,
            )

            strategy = EqualSplit()
            command = ApplyEntryCommand(self.ledger, expense, strategy)
            decorated = LoggingCommandDecorator(
                command, f"Expense: {description}", self.output
            )

            self.ledger.execute(decorated)

        except ValueError as e:
            self.output.write(f"Error: {e}")
        except Exception as e:
            self.output.write(f"Unexpected Error: {e}")

    def do_settle(self, arg):
        """Settle a debt from one user to another: settle <payer> <payee> <amount>
        Example: settle Yusuf Mariam £100.00"""
        parts = arg.split(maxsplit=2)
        if len(parts) < 3:
            self.output.write(
                "Error: Expected format: settle <payer> <payee> <amount>"
            )
            return

        payer, payee, amount_str = parts[0], parts[1], parts[2]

        if payer not in self.users or payee not in self.users:
            self.output.write(
                "Error: Both payer and payee must be registered users."
            )
            return

        try:
            amount_pence = parse_pounds_to_pence(amount_str)

            settlement = Settlement(
                description="Settlement",
                amount_pence=amount_pence,
                payer=payer,
                participants=[payee],
                date=self.clock.now(),
                entry_type=EntryType.SETTLEMENT,
            )

            strategy = ExactSplit({payee: amount_pence})
            command = ApplyEntryCommand(self.ledger, settlement, strategy)
            decorated = LoggingCommandDecorator(
                command, f"Settlement from {payer} to {payee}", self.output
            )

            self.ledger.execute(decorated)

        except ValueError as e:
            self.output.write(f"Error: {e}")

    def do_balance(self, arg):
        """Print current balances of all registered users"""
        if not self.users:
            self.output.write("No users registered.")
            return

        self.output.write("--- Current Balances ---")
        for member in self.users:
            balance = self.ledger.get_balance(member)
            self.output.write(f"{member}: {format_pence_to_pounds(balance)}")

    def do_undo(self, arg):
        """Undo the last transaction"""
        self.output.write("--- Undoing last action ---")
        self.ledger.undo_last()

    def do_suggest_settlements(self, arg):
        """Suggest optimal settlements to perfectly clear all debts with minimum transactions."""
        if not self.users:
            self.output.write("No users registered.")
            return

        balances = {u: self.ledger.get_balance(u) for u in self.users}
        try:
            txs = suggest_optimal_settlements(balances)
            if not txs:
                self.output.write("All balances are settled! Nothing to do.")
                return

            self.output.write("--- Optimal Settlement Plan ---")
            for payer, payee, amt in txs:
                self.output.write(
                    f"{payer} should pay {payee} {format_pence_to_pounds(amt)}"
                )
        except ValueError as e:
            self.output.write(f"Error: {e}")

    def do_quit(self, arg):
        """Exit the application"""
        self.output.write("Goodbye!")
        return True

    def do_exit(self, arg):
        """Exit the application"""
        return self.do_quit(arg)
