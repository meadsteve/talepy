from talepy.steps import LambdaStep, Step


def test_execute_calls_the_first_lambda():
    step: Step[str, str] = LambdaStep(lambda x: f"hello {x}", lambda y: None)
    assert step.execute("world") == "hello world"


def test_compensate_calls_the_second_lambda_with_the_supplied_state():
    class Reverter:
        def lambda_func(self, state_given):
            self.reverted = state_given

    reverter = Reverter()
    step: Step[str, str] = LambdaStep(lambda x: f"hello {x}", reverter.lambda_func)

    step.compensate("world")
    assert reverter.reverted == "world"


def test_compensate_step_is_optional():
    step: Step[str, str] = LambdaStep(lambda x: f"hello {x}")
    assert step.execute("world") == "hello world"
    step.compensate("world")
