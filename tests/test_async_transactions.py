import pytest

from talepy.async_transactions import run_transaction
from talepy.exceptions import (
    AsyncStepFailures,
    AsyncStepUsedInSyncTransaction,
    RetriesCannotBeUsedInConcurrent,
)
from talepy.retries import attempt_retries
from tests.mocks import (
    MockCountingStep,
    MockAsyncExecuteStep,
    MockAsyncExecuteAndCompensateStep,
    MockAsyncCompensateStep,
    AlwaysFailsStep,
    SlowMoStep,
    AlwaysFailException,
)


@pytest.mark.asyncio
async def test_a_transaction_runs_a_single_step_it_wraps():
    mock_step = MockCountingStep()
    await run_transaction(steps=[mock_step], starting_state=0)

    assert mock_step.actions_taken == ["run execute: 0"]


@pytest.mark.asyncio
async def test_exceptions_are_raised_eventually():
    with pytest.raises(AlwaysFailException, match="oh no - How shocking"):
        await run_transaction(
            steps=[MockCountingStep(), AlwaysFailsStep()], starting_state=0
        )


@pytest.mark.asyncio
async def test_a_transaction_runs_many_steps_it_wraps_and_passes_state():
    step_one = MockCountingStep()
    step_two = MockCountingStep()
    await run_transaction(steps=[step_one, step_two], starting_state=0)

    assert step_one.actions_taken == ["run execute: 0"]
    assert step_two.actions_taken == ["run execute: 1"]


@pytest.mark.asyncio
async def test_if_a_transaction_fails_all_compensations_are_applied():
    step_one = MockCountingStep()
    step_two = MockCountingStep()
    failing_step = AlwaysFailsStep()

    with pytest.raises(AlwaysFailException):
        await run_transaction(
            steps=[step_one, step_two, failing_step], starting_state=0
        )

    assert step_one.actions_taken == ["run execute: 0", "run compensate: 1"]
    assert step_two.actions_taken == ["run execute: 1", "run compensate: 2"]
