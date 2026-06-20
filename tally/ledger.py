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

    @classmethod
    def reset(cls):
        if cls._instance is not None:
            cls._instance._init()
