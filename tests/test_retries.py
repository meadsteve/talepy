import typing
from typing import List

import pytest

from talepy import run_transaction
from talepy.exceptions import AbortRetries, FailuresAfterRetrying
from talepy.retries import StepWithRetries


class MockRetryStep(StepWithRetries):
    actions_taken: typing.List[str]

    def __init__(self):
        self.actions_taken = []

    def compensate(self, counter_state):
        self.actions_taken.append(f"run compensate: {counter_state}")

    def execute(self, counter_state):
        raise FirstFail("this step will never succeed")

    def retry(self, state: int, failures: List[Exception]) -> int:
        self.actions_taken.append(
            f"ran retry on state {state} after {len(failures)} failures"
        )
        return state + 1


class MockRetryStepThatRetriesTwice(StepWithRetries):
    actions_taken: typing.List[str]

    def __init__(self):
        self.actions_taken = []

    def compensate(self, counter_state):
        self.actions_taken.append(f"run compensate: {counter_state}")

    def execute(self, counter_state):
        raise FirstFail("this step will never succeed")

    def retry(self, state: int, failures: List[Exception]) -> int:
        self.actions_taken.append(
            f"ran retry on state {state} after {len(failures)} failures"
        )
        if len(failures) < 2:
            raise FirstFail("still failing")
        return state + 1


class MockRetryStepThatRetriesTwiceThenGivesUp(StepWithRetries):
    actions_taken: typing.List[str]

    def __init__(self):
        self.actions_taken = []

    def compensate(self, counter_state):
        self.actions_taken.append(f"run compensate: {counter_state}")

    def execute(self, counter_state):
        raise FirstFail("this step will never succeed")

    def retry(self, state: int, failures: List[Exception]) -> int:
        self.actions_taken.append(
            f"ran retry on state {state} after {len(failures)} failures"
        )
        if len(failures) < 2:
            raise FirstFail("still failing")

        raise AbortRetries("This isn't going to work")


class FirstFail(Exception):
    pass


class SubsequentFailure(Exception):
    pass


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
