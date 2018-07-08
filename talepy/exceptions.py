from typing import Any


class TalepyException(Exception):
    pass


class InvalidStepDefinition(TalepyException):
    def __init__(self, invalid_definition: Any) -> None:
        super().__init__(f"Invalid step definition: `{invalid_definition}`")
