from abc import ABC, abstractmethod
from typing import List, TypeVar

from .exceptions import AbortRetries, FailuresAfterRetrying
from .steps import Step


InputState = TypeVar("InputState")
OutputState = TypeVar("OutputState")


class StepWithRetries(Step[InputState, OutputState], ABC):
    @abstractmethod
    def retry(self, state: InputState, failures: List[Exception]) -> OutputState:
        pass


def execute_step_retry(state, step: StepWithRetries, previous_errors: List[Exception]):
    try:
        return step.retry(state, previous_errors)
    except AbortRetries as _give_up:
        raise FailuresAfterRetrying(previous_errors)
    except Exception as e:
        return execute_step_retry(state, step, previous_errors + [e])
