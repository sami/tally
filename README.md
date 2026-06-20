# Tally

Tally is a small command-line library that splits shared expenses across a group, in the spirit of apps like Splitwise. The system records who paid for what, works out who owes whom, and raises alerts when a balance changes or a debt grows too large.

The core of Tally is designed to demonstrate classic Object-Oriented design patterns solving real needs in a coherent domain, developed using a strict test-first (TDD) approach with no third-party dependencies.

## Running the Application

Everything runs locally. You can see the system in action by executing the entry point composition root:

```bash
python3 main.py
```

This runs a realistic sequence showing expenses being applied with different splitting strategies, balance limits being crossed (triggering alerts), and settlements reconciling debts.

## Running the Tests

Tally was built test-first. You can run the entire suite using the standard library `unittest` module:

```bash
python3 -m unittest discover tests
```

## Directory Layout

```text
tally/
├── tally/                  # Core library package
│   ├── adapters.py         # Converts external shapes into internal domain models
│   ├── clock.py            # Interfaces and implementations for time access
│   ├── ledger.py           # The single source of truth for the group's balances
│   ├── models.py           # Pure data structures (e.g., Expense)
│   ├── money.py            # Deterministic, integer-math exact splitting and parsing rules
│   ├── notifier.py         # Interfaces for outputs (real and fakes)
│   ├── observers.py        # Listeners reacting to ledger state changes
│   └── splitting.py        # Polymorphic splitting strategies (Equal, Shares, Percentage, Exact)
├── tests/                  # Exhaustive behavior specification test suite
├── main.py                 # The composition root demonstrating integration
└── README.md
```

## Pattern Map Table

The project purposefully maps classic Object-Oriented design patterns to specific, practical domain needs.

| Pattern | Where it is used | Why it was used |
|---------|------------------|-----------------|
| **Singleton** | `tally.ledger.Ledger` | Ensures only one centralized ledger instance exists to maintain the zero-sum invariant across the entire system. |
| **Adapter** | `tally.adapters.adapt_external_record` | Translates external JSON-like structures with different field names and string currency values into the internal, sanitized `Expense` model. |
| **Strategy** | `tally.splitting.SplitStrategy` | Allows the Ledger to calculate splits for any expense polymorphically (Equal, Shares, Percentage, Exact) without writing conditional switch statements. |
| **Observer** | `tally.observers.Listener` | Enables decoupled, passive reactions (e.g., `BalanceReportListener`, `ThresholdAlertListener`) to changes in ledger balances without modifying the Ledger itself. |
| **Dependency Injection** | `tally.clock.Clock`, `tally.notifier.Output` | Offloads side effects (time, output generation) to interfaces, allowing real application paths and fake, perfectly deterministic test paths. |
| **Command** | `tally.commands.ApplyExpenseCommand` | Encapsulates the application of an expense as an object with `execute()` and `undo()`, allowing the ledger to safely execute and reverse changes dynamically without tracking complex state manually. |
| **Decorator** | `tally.commands.LoggingCommandDecorator` | Cleanly wraps any `Command` to dynamically attach cross-cutting concerns (like logging) before and after `execute()` and `undo()` without altering the command's core logic. |
| **Composition Root** | `main.py` | The absolute outer edge of the application where all dependencies, patterns, fakes, and real implementations are finally stitched together into a working whole. |
