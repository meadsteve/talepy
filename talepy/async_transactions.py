import asyncio
import inspect
from typing import Iterable, Any, Tuple, List

from .retries import StepWithRetries
from .exceptions import AsyncStepFailures, RetriesCannotBeUsedInConcurrent
from .functional import partition
from .steps import Step, StepLike, build_step_list


class _WrappedAsyncStep(Step):
    _wrapped_step: Step

    def __init__(self, wrapped_step: Step):
        if isinstance(wrapped_step, StepWithRetries):
            raise RetriesCannotBeUsedInConcurrent
        self._wrapped_step = wrapped_step

    async def compensate(self, state):
        if has_async_compensate(self._wrapped_step):
            return await self._wrapped_step.compensate(state)  # type: ignore
        else:
            return self._wrapped_step.compensate(state)

    async def execute(self, state):
        if has_async_execute(self._wrapped_step):
            return await self._wrapped_step.execute(state)
        else:
            return self._wrapped_step.execute(state)


async def _raise_on_any_failures(
    steps: List[_WrappedAsyncStep], results: Tuple[Any, ...]
):
    executed_steps = zip(steps, results)
    successful_steps, failing_steps = partition(
        executed_steps, lambda i: not isinstance(i[1], Exception)
    )
    if len(failing_steps) != 0:
        async_compensations = [
            step.compensate(state) for (step, state) in successful_steps
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


async def run_concurrent_transaction(
    step_defs: Iterable[StepLike], starting_state=None
) -> Tuple[Any, ...]:
    steps = [_WrappedAsyncStep(step) for step in build_step_list(step_defs)]
    executions = [step.execute(starting_state) for step in steps]
    results = await asyncio.gather(*executions, return_exceptions=True)
    await _raise_on_any_failures(steps, results)
    return results


async def run_transaction(step_defs: Iterable[StepLike], starting_state=None):
    completed_steps: List[Tuple[_WrappedAsyncStep, Any]] = []
    steps = [_WrappedAsyncStep(step) for step in build_step_list(step_defs)]
    state = starting_state
    try:
        for step in steps:
            state = await step.execute(state)
            completed_steps.append((step, state))
        return state

    except Exception as error:
        async_compensations = [
            step.compensate(state) for (step, state) in completed_steps
        ]
        await asyncio.gather(*async_compensations, return_exceptions=True)
        raise error
