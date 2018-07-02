from abc import ABC, abstractmethod
from typing import Generic, TypeVar

InputState = TypeVar('InputState')
OutputState = TypeVar('OutputState')


class Step(ABC, Generic[InputState, OutputState]):

    @abstractmethod
    def execute(self, state: InputState) -> OutputState:
        pass

    @abstractmethod
    def compensate(self, state: OutputState) -> None:
        pass
