import pytest

from talepy import run_transaction
from talepy.exceptions import CompensationFailure
from tests.mocks import MockCountingStep, AlwaysFailsStep, AlwaysFailException


def test_a_transaction_runs_a_step_it_wraps():
    mock_step = MockCountingStep()
    run_transaction(steps=[mock_step], starting_state=0)

    assert mock_step.actions_taken == ["run execute: 0"]


def test_a_transaction_runs_many_steps_it_wraps_and_passes_state():
    step_one = MockCountingStep()
    step_two = MockCountingStep()
    run_transaction(steps=[step_one, step_two], starting_state=0)

    assert step_one.actions_taken == ["run execute: 0"]
    assert step_two.actions_taken == ["run execute: 1"]


def test_final_state_is_returned():
    step_one = MockCountingStep()
    step_two = MockCountingStep()

    result = run_transaction(steps=[step_one, step_two], starting_state=0)

    assert result == 2


def test_if_a_transaction_fails_all_compensations_are_applied():
    step_one = MockCountingStep()
    step_two = MockCountingStep()
    failing_step = AlwaysFailsStep()

    with pytest.raises(AlwaysFailException):
        run_transaction(steps=[step_one, step_two, failing_step], starting_state=0)

    assert step_one.actions_taken == ["run execute: 0", "run compensate: 1"]
    assert step_two.actions_taken == ["run execute: 1", "run compensate: 2"]


def test_if_a_transaction_fails_later_steps_are_ignored():
    step_one = MockCountingStep()
    step_two = MockCountingStep()
    failing_step = AlwaysFailsStep()
    never_executed_step = MockCountingStep()

    with pytest.raises(AlwaysFailException):
        run_transaction(
            steps=[step_one, step_two, failing_step, never_executed_step],
            starting_state=0,
        )

    assert never_executed_step.actions_taken == []


def test_exceptions_are_raised_eventually():
    with pytest.raises(AlwaysFailException, match="oh no - How shocking"):
        run_transaction(steps=[MockCountingStep(), AlwaysFailsStep()], starting_state=0)


def test_single_lambdas_are_turned_into_steps():
    result = run_transaction(steps=[lambda x: x + 1, lambda x: x + 2], starting_state=0)

    assert result == 3


def test_pairs_of_lambdas_are_turned_into_a_step():
    result = run_transaction(
        steps=[(lambda x: x + 1, lambda y: None), (lambda x: x + 2, lambda y: None)],
        starting_state=0,
    )

    assert result == 3


def test_failures_in_compensations_are_caught_and_bundled():
    def create_failure(message):
        def fail(s):
            raise Exception(message)

        return fail

    with pytest.raises(CompensationFailure) as e_info:
        run_transaction(
            steps=[
                (lambda x: x + 1, create_failure("reverting one")),
                (lambda x: x + 2, create_failure("reverting two")),
                (create_failure("STOP"), lambda x: x - 3),
            ],
            starting_state=0,
        )

    assert str(e_info.value) == f"Failed to apply compensation of 2 steps"
    error_messages = map(lambda e: str(e), e_info.value.inner_exceptions)
    assert list(error_messages) == ["reverting two", "reverting one"]
