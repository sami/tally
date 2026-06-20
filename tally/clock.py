from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta

class Clock(ABC):
    @abstractmethod
    def now(self) -> datetime:
        pass

class RealClock(Clock):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)

class FakeClock(Clock):
    def __init__(self, current_time: datetime):
        self._current_time = current_time

    def now(self) -> datetime:
        return self._current_time
    
    def advance(self, td: timedelta) -> None:
        self._current_time += td
