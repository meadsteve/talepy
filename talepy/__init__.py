from typing import Tuple, Any, List, Iterable

from .steps import Step, build_step_list, StepLike


def _compensate_completed_steps(completed_steps: List[Tuple[Step, Any]]):
    for (step, state) in completed_steps:
        step.compensate(state)


def run_transaction(steps: Iterable[StepLike], starting_state=None):
    steps = build_step_list(steps)
    completed_steps: List[Tuple[Step, Any]] = []
    state = starting_state
    try:
        for step in steps:
            state = step.execute(state)
            completed_steps.append((step, state))
        return state

    except Exception as error:
        _compensate_completed_steps(completed_steps)
        raise error
