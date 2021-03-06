from typing import Any, List


class TalepyException(Exception):
    pass


class InvalidStepDefinition(ValueError, TalepyException):
    def __init__(self, invalid_definition: Any) -> None:
        super().__init__(f"Invalid step definition: `{invalid_definition}`")


class CompensationFailure(RuntimeError, TalepyException):
    inner_exceptions: List[Exception]

    def __init__(self, failures: List[Exception]) -> None:
        self.inner_exceptions = failures
        super().__init__(f"Failed to apply compensation of {len(failures)} steps")


class AbortRetries(RuntimeError, TalepyException):
    pass


class FailuresAfterRetrying(RuntimeError, TalepyException):
    inner_exceptions: List[Exception]

    def __init__(self, failures: List[Exception]) -> None:
        self.inner_exceptions = failures
        super().__init__(f"Failed to apply step after {len(failures)} attempts")


class AsyncStepFailures(RuntimeError, TalepyException):
    inner_exceptions: List[Exception]

    def __init__(self, exceptions: List[Exception]) -> None:
        self.inner_exceptions = exceptions


class AsyncStepUsedInSyncTransaction(ValueError, TalepyException):
    def __init__(self) -> None:
        super().__init__(
            f"Async step cannot be called synchronously"
            f" - try importing from `talepy.async_transactions` instead"
        )


class RetriesCannotBeUsedInConcurrent(ValueError, TalepyException):
    def __init__(self) -> None:
        super().__init__(
            f"Retries cannot currently be used in `run_concurrent_transaction`"
        )
