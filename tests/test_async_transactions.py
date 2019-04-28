import typing

import pytest

from talepy.exceptions import AsyncStepFailures
from talepy.parallel import run_async_transaction
from talepy.steps import Step


class MockCountingStep(Step[int, int]):

    actions_taken: typing.List[str]

    def __init__(self):
        self.actions_taken = []

    def compensate(self, counter_state):
        self.actions_taken.append(f"run compensate: {counter_state}")

    def execute(self, counter_state):
        self.actions_taken.append(f"run execute: {counter_state}")
        return counter_state + 1


class MockAsyncExecuteStep(Step[int, int]):

    actions_taken: typing.List[str]

    def __init__(self):
        self.actions_taken = []

    def compensate(self, counter_state):
        self.actions_taken.append(f"run compensate: {counter_state}")

    async def execute(self, counter_state):
        self.actions_taken.append(f"run execute: {counter_state}")
        return counter_state + 1


class AlwaysFailException(Exception):
    pass


class AlwaysFailsStep(Step):

    actions_taken: typing.List[str]

    def __init__(self):
        self.actions_taken = []

    def compensate(self, counter_state):
        pass

    def execute(self, counter_state):
        raise AlwaysFailException("oh no - How shocking")


@pytest.mark.asyncio
async def test_a_transaction_runs_a_single_step_it_wraps():
    mock_step = MockCountingStep()
    await run_async_transaction(steps=[mock_step], starting_state=0)

    assert mock_step.actions_taken == ["run execute: 0"]

@pytest.mark.asyncio
async def test_a_transaction_runs_many_steps_it_wraps():
    step_1 = MockCountingStep()
    step_2 = MockCountingStep()
    step_3 = MockCountingStep()
    await run_async_transaction(steps=[step_1, step_2, step_3], starting_state=0)

    assert step_1.actions_taken == ["run execute: 0"]
    assert step_2.actions_taken == ["run execute: 0"]
    assert step_3.actions_taken == ["run execute: 0"]

@pytest.mark.asyncio
async def test_if_any_step_fails_they_all_get_rolled_back():
    step_1 = AlwaysFailsStep()
    step_2 = MockCountingStep()
    step_3 = MockCountingStep()

    try:
        await run_async_transaction(steps=[step_1, step_2, step_3], starting_state=0)
    except AsyncStepFailures as _e:
        pass

    # Steps 2 and 3 have been run and then compensated
    assert step_2.actions_taken == ["run execute: 0", "run compensate: 1"]
    assert step_3.actions_taken == ["run execute: 0", "run compensate: 1"]


@pytest.mark.asyncio
async def test_steps_may_be_async():
    step_1 = MockCountingStep()
    step_2 = MockAsyncExecuteStep()
    await run_async_transaction(steps=[step_1, step_2], starting_state=0)

    assert step_1.actions_taken == ["run execute: 0"]
    assert step_2.actions_taken == ["run execute: 0"]
