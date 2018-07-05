import inspect
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Iterable, Tuple, TypeVar, Union

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


def _arity(func: Callable) -> int:
    return len(inspect.signature(func).parameters)


def _is_func_pair(step_definition: Any):
    return len(step_definition) == 2 \
       and callable(step_definition[0]) and _arity(step_definition[0]) == 1 \
       and callable(step_definition[1]) and _arity(step_definition[1]) == 1


class InvalidStepDefinition(Exception):
    pass


X = TypeVar('X')
FunctionPair = Tuple[Callable[[Any], X], Callable[[X], Any]]
PlainFunction = Callable[[Any], Any]
StepLike = Union[Step, FunctionPair, PlainFunction]


def build_step(step_definition: StepLike) -> Step:
    if isinstance(step_definition, Step):
        return step_definition
    if isinstance(step_definition, tuple) and _is_func_pair(step_definition):
        return LambdaStep(step_definition[0], step_definition[1])
    if callable(step_definition) and _arity(step_definition) == 1:
        return LambdaStep(step_definition)

    raise InvalidStepDefinition(f"Invalid step definition {step_definition}")


def build_step_list(step_definitions: Iterable[StepLike]) -> Iterable[Step]:
    return map(build_step, step_definitions)
