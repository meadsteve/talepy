from typing import Any, List


class TalepyException(Exception):
    pass


class InvalidStepDefinition(TalepyException):
    def __init__(self, invalid_definition: Any) -> None:
        super().__init__(f"Invalid step definition: `{invalid_definition}`")


class CompensationFailure(TalepyException):
    inner_exceptions: List[Exception]

    def __init__(self, failures: List[Exception]) -> None:
        self.inner_exceptions = failures
        super().__init__(f"Failed to apply compensation of {len(failures)} steps")


class AbortRetries(TalepyException):
    pass


class FailuresAfterRetrying(TalepyException):
    inner_exceptions: List[Exception]

    def __init__(self, failures: List[Exception]) -> None:
        self.inner_exceptions = failures
        super().__init__(f"Failed to apply step after {len(failures)} attempts")
