import asyncio
from typing import Iterable

from talepy.exceptions import AsyncStepFailures
from . import Step, StepLike, build_step_list


def _build_step_coroutine(state, step: Step):
    async def _runner():
        return step.execute(state)
    return _runner()


async def run_async_transaction(steps: Iterable[StepLike], starting_state=None):
    async_steps = [_build_step_coroutine(starting_state, step) for step in build_step_list(steps)]

    results = await asyncio.gather(*async_steps, return_exceptions=True)
    executed_steps = zip(build_step_list(steps), results)
    successful_steps = [(step, result) for (step, result) in executed_steps if not isinstance(result, Exception)]
    if (len(successful_steps) != len(async_steps)):
        for (step, result) in successful_steps:
            step.compensate(result)
        raise AsyncStepFailures
    return results
