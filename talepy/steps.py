from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar

InputState = TypeVar('InputState')
OutputState = TypeVar('OutputState')


class Step(ABC, Generic[InputState, OutputState]):

    @abstractmethod
    def execute(self, state: InputState) -> OutputState:
        pass

    @abstractmethod
    def compensate(self, state: OutputState) -> None:
        pass


Y = TypeVar('Y')


class LambdaStep(Step[Any, Y]):

    def __init__(
        self,
        execute_lambda: Callable[[Any], Y],
        compensate_lambda: Callable[[Y], Any] = None
    ) -> None:
        self.execute_lambda = execute_lambda
        self.compensate_lambda = compensate_lambda or (lambda _x: None)

    def execute(self, state):
        return self.execute_lambda(state)

    def compensate(self, state) -> None:
        self.compensate_lambda(state)
