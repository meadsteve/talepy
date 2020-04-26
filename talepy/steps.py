from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Iterable, TypeVar, Union, Awaitable, runtime_checkable, Protocol

from .exceptions import InvalidStepDefinition
from .functional import (
    FunctionPair,
    PlainStateChangingFunction,
    arity,
    is_arity_one_pair,
)

InputState = TypeVar("InputState", contravariant=True)
OutputState = TypeVar("OutputState")


@runtime_checkable
class StepProtocol(Protocol[InputState, OutputState]):
    def execute(self, state: InputState) -> Union[OutputState, Awaitable[OutputState]]: ...
    def compensate(self, state: OutputState) -> Union[None, Awaitable[Any]]: ...


class Step(ABC, StepProtocol, Generic[InputState, OutputState]):
    @abstractmethod
    def execute(self, state: InputState) -> Union[OutputState, Awaitable[OutputState]]:
        pass

    @abstractmethod
    def compensate(self, state: OutputState) -> Union[None, Awaitable[Any]]:
        pass


X = TypeVar("X")
Y = TypeVar("Y")


class LambdaStep(StepProtocol[X, Y]):
    def __init__(
        self,
        execute_lambda: Callable[[X], Y],
        compensate_lambda: Callable[[Y], Any] = None,
    ) -> None:
        self.execute_lambda = execute_lambda
        self.compensate_lambda = compensate_lambda or (lambda _x: None)

    def execute(self, state):
        return self.execute_lambda(state)

    def compensate(self, state) -> None:
        self.compensate_lambda(state)


StepLike = Union[StepProtocol, FunctionPair, PlainStateChangingFunction]


def build_step(definition: StepLike) -> StepProtocol:
    if isinstance(definition, Step):
        return definition
    if isinstance(definition, tuple) and is_arity_one_pair(definition):
        return LambdaStep(definition[0], definition[1])
    if callable(definition) and arity(definition) == 1:
        return LambdaStep(definition)

    raise InvalidStepDefinition(definition)


def build_step_list(step_definitions: Iterable[StepLike]) -> Iterable[StepProtocol]:
    return map(build_step, step_definitions)
