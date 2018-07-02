import typing

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


def test_if_a_transaction_fails_all_compensations_are_applied():
    step_one = MockCountingStep()
    step_two = MockCountingStep()
    failing_step = AlwaysFailsStep()
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
    run_transaction(
        steps=[step_one, step_two, failing_step, never_executed_step],
        starting_state=0
    )

    assert never_executed_step.actions_taken == []
