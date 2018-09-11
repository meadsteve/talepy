from typing import Tuple, Any, List, Iterable

from .exceptions import CompensationFailure
from .retries import StepWithRetries, execute_step_retry
from .steps import Step, build_step_list, StepLike


def _compensate_completed_steps(completed_steps: List[Tuple[Step, Any]]):
    failures = []
    for (step, state) in reversed(completed_steps):
        try:
            step.compensate(state)
        except Exception as failure:
            failures.append(failure)
    if failures != []:
        raise CompensationFailure(failures)


def _execute_step(state, step: Step):
    try:
        return step.execute(state)
    except Exception as e:
        if isinstance(step, StepWithRetries):
            return execute_step_retry(state, step, [e])
        raise e


def run_transaction(steps: Iterable[StepLike], starting_state=None):
    steps = build_step_list(steps)
    completed_steps: List[Tuple[Step, Any]] = []
    state = starting_state
    try:
        for step in steps:
            state = _execute_step(state, step)
            completed_steps.append((step, state))
        return state

    except Exception as error:
        _compensate_completed_steps(completed_steps)
        raise error
