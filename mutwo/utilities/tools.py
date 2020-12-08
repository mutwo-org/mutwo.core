import itertools
import numbers
import typing


def scale(
    value: numbers.Number,
    old_min: numbers.Number,
    old_max: numbers.Number,
    new_min: numbers.Number,
    new_max: numbers.Number,
) -> numbers.Number:
    """Scale a value from one range to another range."""
    assert old_min <= value <= old_max
    return (((value - old_min) / (old_max - old_min)) * (new_max - new_min)) + new_min


def accumulate_from_n(iterable: typing.Iterable, n: numbers.Number) -> typing.Iterator:
    """Accumulates iterable starting with value n."""
    return itertools.accumulate(itertools.chain((n,), iterable))


def accumulate_from_zero(iterable: typing.Iterable) -> typing.Iterator:
    """Accumulates iterable starting from 0."""
    return accumulate_from_n(iterable, 0)
