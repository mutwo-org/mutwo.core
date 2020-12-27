import bisect
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
    try:
        assert old_min <= value <= old_max
    except AssertionError:
        msg = "Input value '{}' has to be in the range of (old_min = {}, old_max = {}).".format(
            value, old_min, old_max
        )
        raise ValueError(msg)
    return (((value - old_min) / (old_max - old_min)) * (new_max - new_min)) + new_min


def accumulate_from_n(iterable: typing.Iterable, n: numbers.Number) -> typing.Iterator:
    """Accumulates iterable starting with value n."""
    return itertools.accumulate(itertools.chain((n,), iterable))


def accumulate_from_zero(iterable: typing.Iterable) -> typing.Iterator:
    """Accumulates iterable starting from 0."""
    return accumulate_from_n(iterable, 0)


def insert_next_to(
    sequence: typing.MutableSequence,
    item_to_find: typing.Any,
    distance: int,
    item_to_insert: typing.Any,
):
    """Insert an item into a list relative to the first item equal to a certain value."""
    index = list(sequence).index(item_to_find)
    if distance == 0:
        sequence[index] = item_to_insert
    else:
        real_distance = distance + 1 if distance < 0 else distance
        sequence.insert(index + real_distance, item_to_insert)


def find_closest_index(item: float, data: tuple, key: typing.Callable = None) -> int:
    """Return index of element in data with smallest difference to item"""

    if key is not None:
        research_data = tuple(map(key, data))

    else:
        research_data = tuple(data)

    sorted_research_data = sorted(research_data)

    solution = bisect.bisect_left(sorted_research_data, item)
    if solution == len(data):
        index = solution - 1

    elif solution == 0:
        index = solution

    else:
        indices = (solution, solution - 1)
        differences = tuple(abs(item - research_data[n]) for n in indices)
        index = indices[differences.index(min(differences))]

    return research_data.index(sorted_research_data[index])


def find_closest_item(item: float, data: tuple, key: typing.Callable = None) -> float:
    """Return element in data with smallest difference to item"""
    return data[find_closest_index(item, data, key=key)]
