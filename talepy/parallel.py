import asyncio
import inspect
from typing import Iterable, Any, Tuple

from .retries import StepWithRetries
from .exceptions import AsyncStepFailures, RetriesCannotBeUsedInAsync
from .functional import partition
from .steps import Step, StepLike, build_step_list


def _build_step_coroutine(state, step: Step):
    if isinstance(step, StepWithRetries):
        raise RetriesCannotBeUsedInAsync

    async def _runner():
        if has_async_execute(step):
            return await step.execute(state)
        else:
            return step.execute(state)

    return _runner()


def _build_compensation_coroutine(state, step: Step):
    async def _runner():
        if has_async_compensate(step):
            return await step.compensate(state)  # type: ignore
        else:
            return step.compensate(state)

    return _runner()


async def _raise_on_any_failures(steps: Iterable[StepLike], results: Tuple[Any, ...]):
    executed_steps = zip(build_step_list(steps), results)
    successful_steps, failing_steps = partition(
        executed_steps, lambda i: not isinstance(i[1], Exception)
    )
    if len(failing_steps) != 0:
        async_compensations = [
            _build_compensation_coroutine(state, step)
            for (step, state) in successful_steps
        ]
        _compensations = await asyncio.gather(
            *async_compensations, return_exceptions=True
        )
        exceptions = [error for (_step, error) in failing_steps]
        raise AsyncStepFailures(exceptions)


def has_async_execute(step: Step) -> bool:
    return inspect.iscoroutinefunction(step.execute)


def has_async_compensate(step: Step) -> bool:
    return inspect.iscoroutinefunction(step.compensate)


async def run_async_transaction(
    steps: Iterable[StepLike], starting_state=None
) -> Tuple[Any, ...]:
    async_steps = [
        _build_step_coroutine(starting_state, step) for step in build_step_list(steps)
    ]

    results = await asyncio.gather(*async_steps, return_exceptions=True)
    await _raise_on_any_failures(steps, results)
    return results
