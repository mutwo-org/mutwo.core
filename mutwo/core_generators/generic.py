"""Generic algorithms which are designed by mutwo authors."""

import numbers
import typing

import numpy as np  # type: ignore

from mutwo import core_events
from mutwo import core_utilities

__all__ = ("DynamicChoice",)


class DynamicChoice(object):
    """Weighted random choices with dynamically changing weights.

    :param value_sequence: The items to choose from.
    :type value_sequence: typing.Sequence[typing.Any]
    :param curve_sequence: The dynamically changing weight for each value.
    :type curve_sequence: typing.Sequence[core_events.Envelope]
    :param random_seed: The seed which shall be set at class initialisation.
    :type random_seed: int

    **Example:**

    >>> from mutwo import core_events
    >>> from mutwo import core_generators
    >>> dynamic_choice = core_generators.DynamicChoice(
    ...    [0, 1, 2],
    ...    [
    ...        core_events.Envelope([(0, 0), (0.5, 1), (1, 0)]),
    ...        core_events.Envelope([(0, 0.5), (0.5, 0), (1, 0.5)]),
    ...        core_events.Envelope([(0, 0.5), (1, 1)]),
    ...    ],
    ... )
    >>> dynamic_choice.gamble_at(0.3)
    2
    >>> dynamic_choice.gamble_at(0.3)
    2
    >>> dynamic_choice.gamble_at(0.3)
    0
    """

    def __init__(
        self,
        value_sequence: typing.Sequence[typing.Any],
        curve_sequence: typing.Sequence[core_events.Envelope],
        random_seed: int = 100,
    ):

        assert len(value_sequence) == len(curve_sequence)

        self._value_sequence = value_sequence
        self._curve_sequence = curve_sequence
        self._random = np.random.default_rng(random_seed)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._value_sequence})"

    def items(self) -> tuple[tuple[typing.Any, core_events.Envelope]]:
        return tuple(zip(self._value_sequence, self._curve_sequence))

    def gamble_at(self, time: numbers.Real) -> typing.Any:
        """Return value at requested time.

        :param time: At which position on the x-Axis shall be gambled.
        :type time: numbers.Real
        :return: The chosen value.
        """
        weight_list = [curve.value_at(time) for curve in self._curve_sequence]
        return self._random.choice(
            self._value_sequence, p=core_utilities.scale_sequence_to_sum(weight_list, 1)
        )
