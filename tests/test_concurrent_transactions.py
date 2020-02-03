import pytest

from talepy import run_transaction
from talepy.exceptions import (
    AsyncStepFailures,
    AsyncStepUsedInSyncTransaction,
    RetriesCannotBeUsedInConcurrent,
)
from talepy.async_transactions import run_concurrent_transaction
from talepy.retries import attempt_retries
from tests.mocks import (
    MockCountingStep,
    MockAsyncExecuteStep,
    MockAsyncExecuteAndCompensateStep,
    MockAsyncCompensateStep,
    AlwaysFailsStep,
    SlowMoStep,
)


@pytest.mark.asyncio
async def test_a_transaction_runs_a_single_step_it_wraps():
    mock_step = MockCountingStep()
    await run_concurrent_transaction(steps=[mock_step], starting_state=0)

    assert mock_step.actions_taken == ["run execute: 0"]


@pytest.mark.asyncio
async def test_a_transaction_runs_many_steps_it_wraps():
    step_1 = MockCountingStep()
    step_2 = MockCountingStep()
    step_3 = MockCountingStep()
    await run_concurrent_transaction(steps=[step_1, step_2, step_3], starting_state=0)

    assert step_1.actions_taken == ["run execute: 0"]
    assert step_2.actions_taken == ["run execute: 0"]
    assert step_3.actions_taken == ["run execute: 0"]


@pytest.mark.asyncio
async def test_if_any_step_fails_they_all_get_rolled_back():
    step_1 = AlwaysFailsStep()
    step_2 = MockCountingStep()
    step_3 = MockCountingStep()

    try:
        await run_concurrent_transaction(
            steps=[step_1, step_2, step_3], starting_state=0
        )
    except AsyncStepFailures as _e:
        pass

    # Steps 2 and 3 have been run and then compensated
    assert step_2.actions_taken == ["run execute: 0", "run compensate: 1"]
    assert step_3.actions_taken == ["run execute: 0", "run compensate: 1"]


@pytest.mark.asyncio
async def test_all_exceptions_are_returned_to_the_user():
    step_1 = AlwaysFailsStep()
    step_2 = AlwaysFailsStep()

    with pytest.raises(AsyncStepFailures) as caught_error:
        await run_concurrent_transaction(steps=[step_1, step_2], starting_state=0)

    assert caught_error.value.inner_exceptions == [step_1.exception, step_2.exception]


@pytest.mark.asyncio
async def test_steps_may_be_async():
    step_1 = MockCountingStep()
    step_2 = MockAsyncExecuteStep()
    await run_concurrent_transaction(steps=[step_1, step_2], starting_state=0)

    assert step_1.actions_taken == ["run execute: 0"]
    assert step_2.actions_taken == ["run execute: 0"]


@pytest.mark.asyncio
async def test_compensate_funcs_can_be_async():
    step_1 = AlwaysFailsStep()
    step_2 = MockAsyncExecuteAndCompensateStep()
    step_3 = MockAsyncCompensateStep()

    try:
        await run_concurrent_transaction(
            steps=[step_1, step_2, step_3], starting_state=0
        )
    except AsyncStepFailures as _e:
        pass

    # Steps 2 and 3 have been run and then compensated
    assert step_2.actions_taken == ["run execute: 0", "run compensate: 1"]
    assert step_3.actions_taken == ["run execute: 0", "run compensate: 1"]


@pytest.mark.asyncio
async def test_regular_transactions_can_be_async():
    step_1 = MockAsyncExecuteAndCompensateStep()

    with pytest.raises(AsyncStepUsedInSyncTransaction):
        run_transaction(steps=[step_1], starting_state=0)


@pytest.mark.asyncio
async def test_currently_retries_cant_be_used_concurrently():
    # TODO: Implement this functionality
    step_1 = MockCountingStep()

    with pytest.raises(RetriesCannotBeUsedInConcurrent):
        await run_concurrent_transaction(
            steps=[attempt_retries(step_1, times=2)], starting_state=0
        )


@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_steps_are_treated_as_coroutines():
    # Each slowmo step does an asyncio.sleep for 1 second so 2000
    # of these can complete quickly if our async runner is working
    steps = [SlowMoStep() for _ in range(0, 2000)]
    results = await run_concurrent_transaction(steps=steps, starting_state=0)

    assert all([r == "okay" for r in results])
