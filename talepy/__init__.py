from typing import Tuple, Any, List

from .steps import Step


def _compensate_completed_steps(completed_steps: List[Tuple[Step, Any]]):
    for (step, state) in completed_steps:
        step.compensate(state)


def run_transaction(steps: List[Step], starting_state=None):
    completed_steps: List[Tuple[Step, Any]] = []
    state = starting_state
    try:
        for step in steps:
            state = step.execute(state)
            completed_steps.append((step, state))
        return state

    except Exception as error:
        _compensate_completed_steps(completed_steps)
        return error
