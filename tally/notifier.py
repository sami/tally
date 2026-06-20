from abc import ABC, abstractmethod

class Output(ABC):
    @abstractmethod
    def write(self, msg: str) -> None:
        pass

class RealOutput(Output):
    def write(self, msg: str) -> None:
        print(msg)
