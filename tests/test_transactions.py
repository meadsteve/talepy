import typing

import pytest

from talepy import run_transaction
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


class AlwaysFailsStep(Step):

    actions_taken: typing.List[str]

    def __init__(self):
        self.actions_taken = []

    def compensate(self, counter_state):
        pass

    def execute(self, counter_state):
        raise Exception("oh no - How shocking")


def test_a_transaction_runs_a_step_it_wraps():
    mock_step = MockCountingStep()
    run_transaction(
        steps=[mock_step],
        starting_state=0
    )

    assert mock_step.actions_taken == ["run execute: 0"]


def test_a_transaction_runs_many_steps_it_wraps_and_passes_state():
    step_one = MockCountingStep()
    step_two = MockCountingStep()
    run_transaction(
        steps=[step_one, step_two],
        starting_state=0
    )

    assert step_one.actions_taken == ["run execute: 0"]
    assert step_two.actions_taken == ["run execute: 1"]


def test_final_state_is_returned():
    step_one = MockCountingStep()
    step_two = MockCountingStep()

    result = run_transaction(
        steps=[step_one, step_two],
        starting_state=0
    )

    assert result == 2


def test_if_a_transaction_fails_all_compensations_are_applied():
    step_one = MockCountingStep()
    step_two = MockCountingStep()
    failing_step = AlwaysFailsStep()

    with pytest.raises(Exception):
        run_transaction(
            steps=[step_one, step_two, failing_step],
            starting_state=0
        )

    assert step_one.actions_taken == ["run execute: 0", "run compensate: 1"]
    assert step_two.actions_taken == ["run execute: 1", "run compensate: 2"]


def test_if_a_transaction_fails_later_steps_are_ignored():
    step_one = MockCountingStep()
    step_two = MockCountingStep()
    failing_step = AlwaysFailsStep()
    never_executed_step = MockCountingStep()

    with pytest.raises(Exception):
        run_transaction(
            steps=[step_one, step_two, failing_step, never_executed_step],
            starting_state=0
        )

    assert never_executed_step.actions_taken == []


def test_exceptions_are_raised_eventually():
    with pytest.raises(Exception, message="oh no - How shocking"):
        run_transaction(
            steps=[MockCountingStep(), AlwaysFailsStep()],
            starting_state=0
        )


def test_single_lambdas_are_turned_into_steps():
    result = run_transaction(
        steps=[
            lambda x: x + 1,
            lambda x: x + 2,
        ],
        starting_state=0
    )

    assert result == 3


def test_pairs_of_lambdas_are_turned_into_a_step():
    result = run_transaction(
        steps=[
            (lambda x: x + 1, lambda y: None),
            (lambda x: x + 2, lambda y: None),
        ],
        starting_state=0
    )

    assert result == 3
