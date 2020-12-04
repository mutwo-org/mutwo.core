from collections import abc
import numbers


def scale_sum(iterable: abc.Iterable, new_sum: numbers.Number) -> abc.Iterable:
    old_sum = sum(iterable)
    return type(iterable)((i / old_sum) * new_sum for i in iterable)
