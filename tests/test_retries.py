import pytest

from talepy import run_transaction
from talepy.exceptions import FailuresAfterRetrying
from talepy.retries import attempt_retries
from tests.mocks import (
    MockRetryStep,
    MockRetryStepThatRetriesTwice,
    MockRetryStepThatRetriesTwiceThenGivesUp,
    RegularMockStep,
)


def test_the_retry_is_run():
    mock_step = MockRetryStep()
    run_transaction(steps=[mock_step], starting_state=0)

    assert mock_step.actions_taken == ["ran retry on state 0 after 1 failures"]


def test_a_second_retry_can_be_run():
    mock_step = MockRetryStepThatRetriesTwice()
    run_transaction(steps=[mock_step], starting_state=0)

    assert mock_step.actions_taken == [
        "ran retry on state 0 after 1 failures",
        "ran retry on state 0 after 2 failures",
    ]


def test_retries_can_be_stopped_by_raising_abort_retries():
    mock_step = MockRetryStepThatRetriesTwiceThenGivesUp()

    with pytest.raises(FailuresAfterRetrying) as e_info:
        run_transaction(steps=[mock_step], starting_state=0)

    assert mock_step.actions_taken == [
        "ran retry on state 0 after 1 failures",
        "ran retry on state 0 after 2 failures",
    ]

    assert str(e_info.value) == "Failed to apply step after 2 attempts"


def test_helper_method_runs_the_step_the_expected_number_of_times():
    mock_step = RegularMockStep()

    with pytest.raises(FailuresAfterRetrying) as e_info:
        run_transaction(steps=[attempt_retries(mock_step, times=2)], starting_state=0)

    assert mock_step.actions_taken == ["trying", "trying", "trying"]

    assert str(e_info.value) == "Failed to apply step after 3 attempts"
