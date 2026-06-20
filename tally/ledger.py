class Ledger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Ledger, cls).__new__(cls, *args, **kwargs)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self._balances = {}
        self._history = []
        self._listeners = []

    @classmethod
    def reset(cls):
        if cls._instance is not None:
            cls._instance._init()

    def add_listener(self, listener):
        self._listeners.append(listener)

    def get_balance(self, member: str) -> int:
        return self._balances.get(member, 0)

    def apply_expense(self, expense, strategy):
        splits = strategy.calculate_splits(expense)

        # Determine the net changes for each member
        changes = {p: -amount for p, amount in splits.items()}
        changes[expense.payer] = changes.get(expense.payer, 0) + expense.amount_pence

        for member, change in changes.items():
            if change == 0:
                continue
            new_balance = self.get_balance(member) + change
            self._balances[member] = new_balance
            self._notify_listeners(member, new_balance)

        self._history.append((expense, splits))

    def _notify_listeners(self, member: str, new_balance: int):
        for listener in self._listeners:
            listener.on_balance_change(member, new_balance)
