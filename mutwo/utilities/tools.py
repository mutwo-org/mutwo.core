import typing
import numbers


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
