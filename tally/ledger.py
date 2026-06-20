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

    def _notify_listeners(self, member: str, new_balance: int):
        for listener in self._listeners:
            listener.on_balance_change(member, new_balance)
