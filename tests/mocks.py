import asyncio
import typing
from typing import List

from talepy import StepWithRetries, Step
from talepy.exceptions import AbortRetries


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


class MockAsyncExecuteAndCompensateStep(Step[int, int]):

    actions_taken: typing.List[str]

    def __init__(self):
        self.actions_taken = []

    async def compensate(self, counter_state):
        self.actions_taken.append(f"run compensate: {counter_state}")

    async def execute(self, counter_state):
        self.actions_taken.append(f"run execute: {counter_state}")
        return counter_state + 1


class MockAsyncCompensateStep(Step[int, int]):

    actions_taken: typing.List[str]

    def __init__(self):
        self.actions_taken = []

    async def compensate(self, counter_state):
        self.actions_taken.append(f"run compensate: {counter_state}")

    def execute(self, counter_state):
        self.actions_taken.append(f"run execute: {counter_state}")
        return counter_state + 1


class AlwaysFailException(Exception):
    pass


class AlwaysFailsStep(Step):

    actions_taken: typing.List[str]

    def __init__(self):
        self.actions_taken = []
        self.exception = AlwaysFailException("oh no - How shocking")

    def compensate(self, counter_state):
        pass

    def execute(self, counter_state):
        raise self.exception


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


class RegularMockStep(Step):
    actions_taken: typing.List[str]

    def __init__(self):
        self.actions_taken = []

    def compensate(self, counter_state):
        self.actions_taken.append(f"run compensate: {counter_state}")

    def execute(self, counter_state):
        self.actions_taken.append("trying")
        raise FirstFail("this step will never succeed")


class FirstFail(Exception):
    pass


class SubsequentFailure(Exception):
    pass


class SlowMoStep(Step):
    def compensate(self, state):
        pass

    async def execute(self, state):
        await asyncio.sleep(1)
        return "okay"
