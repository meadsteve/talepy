import asyncio
from typing import Iterable

from . import Step, StepLike, build_step_list


def _build_step_coroutine(state, step: Step):
    async def _runner():
        return step.execute(state)
    return _runner()


async def run_async_transaction(steps: Iterable[StepLike], starting_state=None):
    steps = build_step_list(steps)
    async_steps = [_build_step_coroutine(starting_state, step) for step in steps]

    try:
        results = await asyncio.gather(*async_steps, return_exceptions=True)
        return results
    except Exception as error:
        #_compensate_completed_steps(completed_steps)
        raise error