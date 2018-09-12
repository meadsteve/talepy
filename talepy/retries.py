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


def attempt_retries(step: Step, times: int) -> StepWithRetries:
    class AutoRetryStep(StepWithRetries):
        def __init__(self, wrapped_step: Step, max_tries: int) -> None:
            self.wrapped_step = wrapped_step
            self.attempts_made = 0
            self.max_tries = max_tries

        def compensate(self, state) -> None:
            self.wrapped_step.compensate(state)

        def execute(self, state):
            self.attempts_made += 1
            return self.wrapped_step.execute(state)

        def retry(self, state, _failures):
            if self.attempts_made > self.max_tries:
                raise AbortRetries("Maximum number of retries hit")
            return self.execute(state)

    return AutoRetryStep(step, times)


def execute_step_retry(state, step: StepWithRetries, previous_errors: List[Exception]):
    try:
        return step.retry(state, previous_errors)
    except AbortRetries as _give_up:
        raise FailuresAfterRetrying(previous_errors)
    except Exception as e:
        return execute_step_retry(state, step, previous_errors + [e])
