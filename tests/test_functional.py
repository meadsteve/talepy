from talepy.functional import arity, is_arity_one_pair, partition
import pytest


@pytest.mark.parametrize(
    "test_func,expected_arity",
    [(lambda: 0, 0), (lambda x: x, 1), (lambda x, y: x + y, 2)],
)
def test_we_can_get_arity_from_functions(test_func, expected_arity: int):
    assert arity(test_func) == expected_arity


@pytest.mark.parametrize(
    "thing, expected_result",
    [
        ((lambda x: x, lambda y: y), True),
        (lambda: 0, False),
        (("steve", "b"), False),
        ((lambda x: x, "x"), False),
        ("steve", False),
        ((lambda x, z: x + z, lambda y: y), False),
        ((lambda x: x, lambda y, z: y + z), False),
        ((lambda: 0, lambda y: y), False),
        ((lambda x: x, lambda: 0), False),
        ((lambda x: x, lambda y: y, lambda z: z), False),
    ],
)
def test_we_can_tell_if_something_is_a_pair_of_functions(thing, expected_result):
    assert is_arity_one_pair(thing) == expected_result


def test_partition_splits_a_list():
    odd, even = partition([1, 2, 3, 4], lambda x: x % 2)
    assert odd == [1, 3]
    assert even == [2, 4]
