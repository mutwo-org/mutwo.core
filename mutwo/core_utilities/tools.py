"""Generic utility functions."""

import bisect
import copy
import functools
import itertools
import logging
import math
import operator
import types
import typing

from mutwo import core_configurations
from mutwo import core_constants


__all__ = (
    "scale",
    "scale_sequence_to_sum",
    "accumulate_from_n",
    "accumulate_from_zero",
    "insert_next_to",
    "uniqify_sequence",
    "cyclic_permutations",
    "find_closest_index",
    "find_closest_item",
    "get_nested_item_from_index_sequence",
    "set_nested_item_from_index_sequence",
    "find_numbers_which_sums_up_to",
    "call_function_except_attribute_error",
    "round_floats",
    "camel_case_to_snake_case",
    "test_if_objects_are_equal_by_parameter_tuple",
    "get_all",
    "get_cls_logger",
)


def scale(
    value: core_constants.Real,
    old_min: core_constants.Real,
    old_max: core_constants.Real,
    new_min: core_constants.Real,
    new_max: core_constants.Real,
    translation_shape: core_constants.Real = 0,
) -> core_constants.Real:
    """Scale a value from one range to another range.

    :param value: The value that shall be scaled.
    :param old_min: The minima of the old range.
    :param old_max: The maxima of the old range.
    :param new_min: The minima of the new range.
    :param new_max: The maxima of the new range.
    :param translation_shape: 0 for a linear translation,
        values > 0 for a slower change at the beginning,
        values < 0 for a faster change at the beginning.

    The algorithmic to change the translation with the
    `translation_shape` has been copied from
    `expenvelope <https://git.sr.ht/~marcevanstein/expenvelope/tree/master/item/expenvelope/envelope_segment.py#L206>`_
    by M. Evanstein.

    **Example:**

    >>> from mutwo import core_utilities
    >>> core_utilities.scale(1, 0, 1, 0, 100)
    100.0
    >>> core_utilities.scale(0.5, 0, 1, 0, 100)
    50.0
    >>> core_utilities.scale(0.2, 0, 1, 0, 100)
    20.0
    >>> core_utilities.scale(0.2, 0, 1, 0, 100, 1)
    12.885124808584155
    >>> core_utilities.scale(0.2, 0, 1, 0, 100, -1)
    28.67637263023771
    """

    try:
        assert old_min <= value <= old_max
    except AssertionError:
        raise ValueError(
            f"Input value '{value}' has to be in the range of "
            f"(old_min = {old_min}, old_max = {old_max})."
        )

    old_span = old_max - old_min
    assert old_span != 0, "Can't scale if old span == 0"

    percentage = (value - old_min) / old_span
    new_range = new_max - new_min
    if translation_shape:
        value = (new_range / ((math.exp(translation_shape)) - 1)) * (
            math.exp(translation_shape * percentage) - 1
        )
    else:
        value = new_range * percentage
    return value + new_min


def scale_sequence_to_sum(
    sequence_to_scale: typing.Sequence[core_constants.Real],
    sum_to_scale_to: core_constants.Real,
) -> typing.Sequence[core_constants.Real]:
    """Scale numbers in a sequence so that the resulting sum fits to the given value.

    :param sequence_to_scale: The sequence filled with real numbers which sum should fit
        to the given `sum_to_scale_to` argument.
    :type sequence_to_scale: typing.Sequence[core_constants.Real]
    :param sum_to_scale_to: The resulting sum of the sequence.
    :type sum_to_scale_to: core_constants.Real

    **Example:**

    >>> from mutwo import core_utilities
    >>> sequence_to_scale = [1, 3, 2]
    >>> core_utilities.scale_sequence_to_sum(sequence_to_scale, 3)
    [0.5, 1.5, 1.0]
    """

    if sequence_to_scale:
        current_sum = sum(sequence_to_scale)
        if current_sum:
            factor = sum_to_scale_to / current_sum
            scaled_sequence = map(lambda number: number * factor, sequence_to_scale)
        else:
            item_to_scale_count = len(sequence_to_scale)
            size_per_item = sum_to_scale_to / item_to_scale_count
            scaled_sequence = (size_per_item for _ in sequence_to_scale)
        return type(sequence_to_scale)(scaled_sequence)
    else:
        return copy.copy(sequence_to_scale)


def accumulate_from_n(
    iterable: typing.Iterable[core_constants.Real], n: core_constants.Real
) -> typing.Iterator:
    """Accumulates iterable starting with value n.

    :param iterable: The iterable which values shall be accumulated.
    :param n: The start number from which shall be accumulated.

    **Example:**

    >>> from mutwo import core_utilities
    >>> tuple(core_utilities.accumulate_from_n((4, 2, 3), 0))
    (0, 4, 6, 9)
    >>> tuple(core_utilities.accumulate_from_n((4, 2, 3), 2))
    (2, 6, 8, 11)
    """
    return itertools.accumulate(itertools.chain((n,), iterable))


def accumulate_from_zero(
    iterable: typing.Iterable[core_constants.Real],
) -> typing.Iterator:
    """Accumulates iterable starting from 0.

    :param iterable: The iterable which values shall be accumulated.

    **Example:**

    >>> from mutwo import core_utilities
    >>> tuple(core_utilities.accumulate_from_zero((4, 2, 3)))
    (0, 4, 6, 9)
    """
    return accumulate_from_n(iterable, 0)


def insert_next_to(
    mutable_sequence: typing.MutableSequence,
    item_to_find: typing.Any,
    distance: int,
    item_to_insert: typing.Any,
):
    """Insert an item into a list relative to the first item equal to a certain value."""

    index = list(mutable_sequence).index(item_to_find)
    if distance == 0:
        mutable_sequence[index] = item_to_insert
    else:
        real_distance = distance + 1 if distance < 0 else distance
        mutable_sequence.insert(index + real_distance, item_to_insert)


T = typing.TypeVar("T", bound=core_constants.Real)


def find_closest_index(
    item: core_constants.Real,
    sequence: typing.Sequence,
    key: typing.Callable[[typing.Any], T] = lambda item: item,
) -> int:
    """Return index of element in ``data`` with smallest difference to ``item``.

    :param item: The item from which the closest item shall be found.
    :param sequence: The data to which the closest item shall be found.

    **Example:**

    >>> from mutwo import core_utilities
    >>> core_utilities.find_closest_index(2, (1, 4, 5))
    0
    >>> core_utilities.find_closest_index(127, (100, 4, 300, 53, 129))
    4
    >>> core_utilities.find_closest_index(127, (('hi', 100), ('hey', 4), ('hello', 300)), key=lambda item: item[1])
    0
    """

    research_data = tuple(map(key, sequence))
    sorted_research_data = sorted(research_data)

    solution = bisect.bisect_left(sorted_research_data, item)
    # make type ignore because data has been converted to tuple (which is sizeable)
    if solution == len(sequence):
        index = solution - 1

    elif solution == 0:
        index = solution

    else:
        index_tuple = (solution, solution - 1)
        difference_tuple = tuple(
            abs(-sorted_research_data[index] + item) for index in index_tuple
        )
        index = index_tuple[difference_tuple.index(min(difference_tuple))]

    return research_data.index(sorted_research_data[index])


def find_closest_item(
    item: core_constants.Real,
    sequence: typing.Sequence,
    key: typing.Callable[[typing.Any], T] = lambda item: item,
) -> T:
    """Return element in ``data`` with smallest difference to ``item``.

    :param item: The item from which the closest item shall be found.
    :param sequence: The data to which the closest item shall be found.
    :return: The closest number to ``item`` in ``data``.

    **Example:**

    >>> from mutwo import core_utilities
    >>> core_utilities.find_closest_item(2, (1, 4, 5))
    1
    >>> core_utilities.find_closest_item(127, (100, 4, 300, 53, 129))
    129
    >>> core_utilities.find_closest_item(
    ...     127,
    ...     (('hi', 100), ('hey', 4), ('hello', 300)),
    ...     key=lambda item: item[1]
    ... )
    ('hi', 100)
    """
    return sequence[find_closest_index(item, sequence, key=key)]


def uniqify_sequence(
    sequence: typing.Sequence,
    sort_key: typing.Callable[[typing.Any], core_constants.Real] = None,
    group_by_key: typing.Callable[[typing.Any], typing.Any] = None,
) -> typing.Iterable:
    """Not-Order preserving function to uniqify any iterable with non-hashable objects.

    :param sequence: The iterable which items shall be uniqified.
    :return: Return uniqified version of the entered iterable.
        The function will try to return the same type of the passed
        iterable. If Python raises an error during initialisation of
        the original iterable type, the function will simply return
        a tuple.

    **Example:**

    >>> from mutwo import core_utilities
    >>> core_utilities.uniqify_sequence([[1, 2], [1], [1]])
    [[1], [1, 2]]
    """

    sorted_iterable = sorted(sequence, key=sort_key)
    result = (key for key, _ in itertools.groupby(sorted_iterable, key=group_by_key))

    try:
        return type(sequence)(result)  # type: ignore

    except Exception:
        return tuple(result)


def cyclic_permutations(sequence: typing.Sequence[typing.Any]) -> typing.Generator:
    """Cyclic permutation of an iterable. Return a generator object.

    :param sequence: The sequence from which cyclic permutations shall be generated.

    **Example:**

    >>> from mutwo import core_utilities
    >>> permutations = core_utilities.cyclic_permutations((1, 2, 3, 4))
    >>> next(permutations)
    (1, 2, 3, 4)
    >>> next(permutations)
    (2, 3, 4, 1)

    `Adapted function from the reply of Paritosh Singh
    <https://stackoverflow.com/questions/56171246/cyclic-permutation-operators-in-python/56171531>`_
    """

    def reorder_from_index(index: int, sequence: tuple) -> tuple:
        return sequence[index:] + sequence[:index]

    return (
        functools.partial(reorder_from_index, i)(sequence) for i in range(len(sequence))
    )


def camel_case_to_snake_case(camel_case_string: str) -> str:
    """Transform camel case formatted string to snake case.

    :param camel_case_string: String which is formatted using
        camel case (no whitespace, but upper letters at
        new word start).
    :return: string formatted using snake case

    **Example:** MyClassName -> my_class_name
    """

    character_list = []

    is_first = True
    for character in camel_case_string:
        if character.isupper():
            character = character.lower()
            if not is_first:
                character = "_{}".format(character)

        if is_first:
            is_first = False

        character_list.append(character)

    return "".join(character_list)


def get_nested_item_from_index_sequence(
    index_sequence: typing.Sequence[int], sequence: typing.Sequence
) -> typing.Any:
    """Get item in nested Sequence.

    :param index_sequence: The indices of the nested item.
    :type index_sequence: typing.Sequence[int]
    :param sequence: A nested sequence.
    :type sequence: typing.Sequence[typing.Any]


    **Example:**

    >>> from mutwo import core_utilities
    >>> nested_sequence = (1, 2, (4, (5, 1), (9, (3,))))
    >>> core_utilities.get_nested_item_from_index_sequence((2, 2, 0), nested_sequence)
    9
    >>> nested_sequence[2][2][0]  # is equal
    9
    """

    for index in index_sequence:
        sequence = sequence[index]
    return sequence


def set_nested_item_from_index_sequence(
    index_sequence: typing.Sequence[int],
    sequence: typing.MutableSequence,
    item: typing.Any,
) -> None:
    """Set item in nested Sequence.

    :param index_sequence: The indices of the nested item which shall be set.
    :type index_sequence: typing.Sequence[int]
    :param sequence: A nested sequence.
    :type sequence: typing.MutableSequence[typing.Any]
    :param item: The new item value.
    :type item: typing.Any

    **Example:**

    >>> from mutwo import core_utilities
    >>> nested_sequence = [1, 2, [4, [5, 1], [9, [3]]]]
    >>> core_utilities.set_nested_item_from_index_sequence((2, 2, 0), nested_sequence, 100)
    >>> nested_sequence[2][2][0] = 100  # is equal
    """

    index_count = len(index_sequence)
    for index_index, index in enumerate(index_sequence):
        if index_count == index_index + 1:
            sequence.__setitem__(index, item)
        else:
            sequence = sequence[index]


def round_floats(
    number_to_round: core_constants.Real, n_digits: int
) -> core_constants.Real:
    """Round number if it is an instance of float, otherwise unaltered number.

    :param number_to_round: The number which shall be rounded.
    :type number_to_round: core_constants.Real
    :param n_digits: How many digits shall the number be rounded.
    :type n_digits: int
    """

    if isinstance(number_to_round, float):
        return round(number_to_round, n_digits)
    else:
        return number_to_round


def find_numbers_which_sums_up_to(
    given_sum: float,
    number_to_choose_from_sequence: typing.Optional[typing.Sequence[float]] = None,
    item_to_sum_up_count_set: typing.Optional[set[int]] = None,
) -> tuple[tuple[float, ...], ...]:
    """Find all combinations of numbers which sum is equal to the given sum.

    :param given_sum: The target sum for which different combinations shall
        be searched.
    :type given_sum: float
    :param number_to_choose_from_sequence: A sequence of numbers which shall be
        tried to combine to result in the :attr:`given_sum`. If the user
        doesn't specify this argument mutwo will use all natural numbers
        equal or smaller than the :attr:`given_sum`.
    :type number_to_choose_from_sequence: typing.Optional[typing.Sequence[float]]
    :param item_to_sum_up_count_set: How many numbers can be combined to result
        in the :attr:`given_sum`. If the user doesn't specify this argument
        mutwo will use all natural numbers equal or smaller than the
        :attr:`given_sum`.
    :type item_to_sum_up_count_set: typing.Optional[set[int]]

    **Example:**

    >>> from mutwo import core_utilities
    >>> core_utilities.find_numbers_which_sums_up_to(4)
    ((4,), (1, 3), (2, 2), (1, 1, 2), (1, 1, 1, 1))
    """

    if not number_to_choose_from_sequence:
        number_to_choose_from_sequence = tuple(range(1, int(given_sum) + 1))

    if not item_to_sum_up_count_set:
        item_to_sum_up_count_set = set(range(1, given_sum + 1))

    number_tuple_list = []
    for item_to_sum_up_count in item_to_sum_up_count_set:
        number_tuple_list.extend(
            [
                pair
                for pair in itertools.combinations_with_replacement(
                    number_to_choose_from_sequence, item_to_sum_up_count
                )
                if sum(pair) == given_sum
            ]
        )
    return tuple(number_tuple_list)


def call_function_except_attribute_error(
    function: typing.Callable[[typing.Any], typing.Any],
    argument: typing.Any,
    exception_value: typing.Any,
) -> typing.Any:
    """Run a function with argument as input

    :param function: The function to be called.
    :param argument: The argument with which the function shall be called.
    :param exception_value: The alternative value if the function call raises an
        `AttributeError`.
    :return: Return :obj:`exception_value` in case an attribute error occurs.
        In case the function call is successful the function return value will
        be returned.
    """

    try:
        value = function(argument)
    except AttributeError:
        value = exception_value

    return value


def test_if_objects_are_equal_by_parameter_tuple(
    object0: typing.Any,
    object1: typing.Any,
    parameter_to_compare_tuple: tuple[str, ...],
) -> bool:
    """Check if the parameters of two objects have equal values.

    :param object0: The first object which shall be compared.
    :param object1: The second object with which the first object shall be compared.
    :parameter_to_compare_tuple: A tuple of attribute names which shall be compared.
    :return: `True` if all values of all parameters of the objects are equal and `False`
        if not or if an `AttributeError` is raised.

    **Example:**

    >>> from mutwo import core_utilities
    >>> class A: pass
    >>> first_object = A()
    >>> first_object.a = 100
    >>> second_object = A()
    >>> second_object.a = 100
    >>> third_object = A()
    >>> third_object.a = 200
    >>> core_utilities.test_if_objects_are_equal_by_parameter_tuple(
    ...     first_object, second_object, ("a",)
    ... )
    True
    >>> core_utilities.test_if_objects_are_equal_by_parameter_tuple(
    ...     first_object, third_object, ("a",)
    ... )
    False
    """

    for parameter_to_compare in parameter_to_compare_tuple:
        try:
            # If the assigned values of the specific parameter aren't
            # equal, both objects can't be equal.
            if getattr(object0, parameter_to_compare) != getattr(
                object1, parameter_to_compare
            ):
                return False

        # If the other object doesn't know the essential parameter
        # mutwo assumes that both objects can't be equal.
        except AttributeError:
            return False

    # If all compared parameters are equal, return True.
    return True


def get_all(*submodule_tuple: types.ModuleType) -> tuple[str, ...]:
    """Fetch from all arguments their `__all__` attribute and combine them to one tuple

    :param submodule_tuple: Submodules which `__all__` attribute shall be fetched.

    This function is mostly useful in the `__init__` code of each :mod:`mutwo` module.
    """
    return functools.reduce(
        operator.add,
        map(
            lambda submodule: getattr(submodule, "__all__", tuple([])), submodule_tuple
        ),
    )


def get_cls_logger(
    cls: typing.Type, level: typing.Optional[int] = None
) -> logging.Logger:
    """Get the local logger of your class.

    :param cls: The class for which the logger should be returned. Simply call
        `type(o)` if you only have the instance.
    :type cls: typing.Type
    :param level: The logging level of the logger. If ``None`` the level
        defined in `mutwo.core_configurations.LOGGING_LEVEL` is used. Default
        to ``None``.
    :type level: int
    :return: A :class:`logging.Logger`.
    """
    if level is None:
        level = core_configurations.LOGGING_LEVEL
    logger = logging.getLogger(f"{cls.__module__}.{cls.__name__}")
    logger.setLevel(level)
    return logger
