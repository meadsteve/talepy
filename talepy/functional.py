import inspect
from typing import Any, Callable, Tuple, TypeVar

X = TypeVar("X")
FunctionPair = Tuple[Callable[[Any], X], Callable[[X], Any]]
PlainStateChangingFunction = Callable[[Any], Any]


def arity(func: Callable) -> int:
    return len(inspect.signature(func).parameters)


def is_pair_of_funcs(thing: Any) -> bool:
    return (
        len(thing) == 2
        and callable(thing[0])
        and arity(thing[0]) == 1
        and callable(thing[1])
        and arity(thing[1]) == 1
    )