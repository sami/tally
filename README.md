# Tally: A Software Design Project

Welcome to **Tally**! 

I built this repository from the ground up to practice clean architecture, strict Test-Driven Development (TDD), and the practical application of classical Object-Oriented (OO) design patterns. 

This guide explains exactly why the code is written the way it is.

---

## 1. Core Philosophy

**Zero Dependencies**  
This application relies on zero external libraries. I used nothing but the Python standard library. I did this because reaching for a framework often hides the complexity of architectural design. By writing everything from scratch, the design patterns, interfaces, and testing strategies are exposed cleanly.

**Strict Test-Driven Development (TDD)**  
I built the codebase test-first. I never wrote a class or a function before a failing test demanded it. TDD forces you to think about the API of your code before you write the implementation. It ensures that components are decoupled and easily testable.

**Type Hints & Strict Signatures**  
Python is dynamically typed, but I used strict type hints (`typing.Dict`, `typing.List`) throughout. Type hints serve as living documentation. When you see `def calculate_splits(expense: Expense) -> Dict[str, int]:`, you know exactly what goes in and what comes out without having to read the function body.

---

## 2. Data Integrity: Why Integer Maths?

If you look at `tally/money.py`, you'll notice I never use `float` to represent currency. Instead, I use integers to represent **pence** (e.g., £10.50 is stored as `1050`).

**Why not Floats?**  
Computers represent floating-point numbers in base-2, which means numbers like `0.1` cannot be represented perfectly. If you divide £10.00 by 3 people using floats, you might get `3.3333333333333335`. When you sum them back up, you might get `9.999999999999999`. 
By using integers, I maintain strict exactness. I created a deterministic `allocate_pennies` function that guarantees pennies are distributed deterministically by weight, and any remaining indivisible pennies are handed out sequentially so the sum perfectly matches the original expense.

---

## 3. The Design Patterns in Action

I built this project to show how "textbook" design patterns solve real problems. Here is a guided tour:

### A. Singleton (`tally.ledger.Ledger`)
**The Problem:** If two different parts of the application create their own "Ledger", the state of who owes who gets out of sync. We need one absolute source of truth.
**The Solution:** The Singleton pattern ensures that calling `Ledger()` always returns the exact same instance in memory. It guarantees the zero-sum invariant (if A owes B £10, B is owed £10 by A) is globally maintained.

### B. Strategy (`tally.splitting.SplitStrategy`)
**The Problem:** Expenses can be split equally, by exact amounts, by percentages, by shares, or itemised line-by-line. If I used an `if/elif/else` block, `ledger.py` would become massive and fragile every time I added a new splitting method.
**The Solution:** I defined a `SplitStrategy` interface. The `Ledger` doesn't care *how* the split is calculated; it just calls `.calculate_splits()`. You can plug in `EqualSplit` or `PercentageSplit` interchangeably.

### C. Observer (`tally.observers.Listener`)
**The Problem:** When a balance changes, we want to print a report, and maybe raise an alert if a user goes over a debt limit. Putting `print()` statements inside the `Ledger` tightly couples UI with business logic.
**The Solution:** The Observer pattern. The Ledger maintains a list of listeners. When a balance changes, it simply announces "Hey, the balance changed!" to its listeners. `BalanceReportListener` and `ThresholdAlertListener` listen and react independently.

### D. Command (`tally.commands.Command`)
**The Problem:** Users make mistakes and want to "Undo" an expense. To undo an expense, you have to remember exactly how much every person's balance changed and reverse it.
**The Solution:** Instead of directly executing maths on the ledger, I wrap the entire action in an `ApplyExpenseCommand`. This command object has an `execute()` method and an `undo()` method. The Ledger keeps a history stack of these objects. To undo, it just pops the last command and calls `.undo()`.

### E. Decorator (`tally.commands.LoggingCommandDecorator`)
**The Problem:** We want to log whenever a command is executed or undone. Modifying the `ApplyExpenseCommand` to include `print("Logging...")` violates the Single Responsibility Principle (it should only care about maths, not logging).
**The Solution:** The Decorator pattern lets us "wrap" the command. The `LoggingCommandDecorator` takes a command, prints a log, calls the command's real `execute()`, and then prints a success log. To the Ledger, the decorated command looks exactly like a normal command.

### F. Dependency Injection (`tally.notifier.Output`, `tally.clock.Clock`)
**The Problem:** How do you test a system that prints to the console or uses the current time? If a test runs on Tuesday, it might fail on Wednesday. If it prints to the real console, tests clutter your terminal.
**The Solution:** Dependency Injection. I created interfaces (`Output`, `Clock`). In `main.py` (the real app), I inject `RealOutput` which calls Python's `print()`. In `tests/`, I inject `FakeOutput` which just saves strings to an array so we can assert against them. The core logic doesn't know the difference.

### G. Adapter (`tally.adapters.ExternalRecord`)
**The Problem:** External APIs or legacy JSON files often use different naming conventions (e.g., `cost` instead of `amount_pence`, `payer_name` instead of `payer`).
**The Solution:** The Adapter pattern creates a protective barrier. I pass the messy `ExternalRecord` into an adapter, which translates and sanitises it into our pristine internal `Expense` domain model.

---

## 4. Algorithmic Complexity: Optimal Settlement

**The Problem:** When a group trip ends, people need to settle their debts. A naive "greedy" algorithm (largest debtor pays largest creditor) works, but can result in unnecessary transactions. For example, if A owes B £10, B owes C £10, and C owes A £10, a naive algorithm might issue 2 or 3 payments. The optimal answer is 0 payments (they cancel out).
**The Solution (`tally.settlement.py`):** Minimising the number of transactions is equivalent to finding the maximum number of zero-sum subsets within the group. I used **Bitmask Dynamic Programming (DP) over Subsets**. 
This is an NP-hard problem ($O(3^N)$ time complexity). While exponential, expense sharing groups rarely exceed 15-20 people, making this perfectly suitable. My DP algorithm finds all optimal disjoint partitions, and then safely applies a greedy settlement *within* those perfect boundaries, guaranteeing the absolute minimum number of payments mathematically possible.

---

## Running the Application

To drive the app interactively via the CLI, run:
```bash
python3 main.py
```
To run the automated test suite (currently 39 tests ensuring 100% logic coverage), run:
```bash
python3 -m unittest discover tests
```
