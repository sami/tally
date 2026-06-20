from abc import ABC, abstractmethod
from typing import List

class Output(ABC):
    @abstractmethod
    def write(self, msg: str) -> None:
        pass

class RealOutput(Output):
    def write(self, msg: str) -> None:
        print(msg)

class FakeOutput(Output):
    def __init__(self):
        self.messages: List[str] = []

    def write(self, msg: str) -> None:
        self.messages.append(msg)
