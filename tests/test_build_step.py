import pytest

from talepy.steps import InputState, OutputState, Step, build_step


class StubStep(Step):

    def execute(self, state: InputState) -> OutputState:
        pass

    def compensate(self, state: OutputState) -> None:
        pass


step_like_objects = [
    StubStep(),
    (lambda x: x + 1, lambda y: y - 1),
    lambda x: x + 1
]


@pytest.mark.parametrize('step_like_object', step_like_objects)
def test_things_that_should_turn_into_steps(step_like_object):
    step = build_step(step_like_object)
    assert isinstance(step, Step)


non_step_like_objects = [
    {},
    "step",
    lambda x,y: x + y # arity 2 - should only take one state arg
]


@pytest.mark.parametrize('non_step_like_object', non_step_like_objects)
def test_things_that_should_not_turn_into_steps(non_step_like_object):
    with pytest.raises(Exception):
        build_step(non_step_like_object)
