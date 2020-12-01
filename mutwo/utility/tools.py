from collections.abc import Iterable

def scale_sum(iterable: Iterable, new_sum: float) -> Iterable:
    old_sum = sum(iterable)
    return type(iterable)((i / old_sum) * new_sum for i in iterable)

