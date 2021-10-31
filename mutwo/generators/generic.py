"""Generic algorithms which are designed by mutwo authors."""

import numbers
import typing

import expenvelope  # type: ignore
import numpy as np  # type: ignore

from mutwo import utilities

__all__ = ("DynamicChoice",)


class DynamicChoice(object):
    """Weighted random choices with dynamically changing weights.

    :param values: The items to choose from.
    :type values: typing.Sequence[typing.Any]
    :param curves: The dynamically changing weight for each value.
    :type curves: typing.Sequence[expenvelope.Envelope]
    :param random_seed: The seed which shall be set at class initialisation.
    :type random_seed: int

    **Example:**

    >>> import expenvelope
    >>> from mutwo.generators import generic
    >>> dynamic_choice = generic.DynamicChoice(
    >>>    [0, 1, 2],
    >>>    [
    >>>        expenvelope.Envelope.from_points((0, 0), (0.5, 1), (1, 0)),
    >>>        expenvelope.Envelope.from_points((0, 0.5), (0.5, 0), (1, 0.5)),
    >>>        expenvelope.Envelope.from_points((0, 0.5), (1, 1)),
    >>>    ],
    >>> )
    >>> dynamic_choice.gamble_at(0.3)
    2
    >>> dynamic_choice.gamble_at(0.3)
    2
    >>> dynamic_choice.gamble_at(0.3)
    0
    """

    def __init__(
        self,
        values: typing.Sequence[typing.Any],
        curves: typing.Sequence[expenvelope.Envelope],
        random_seed: int = 100,
    ):

        assert len(values) == len(curves)

        self._values = values
        self._curves = curves
        self._random = np.random.default_rng(random_seed)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._values})"

    def items(self) -> tuple[tuple[typing.Any, expenvelope.Envelope]]:
        return tuple(zip(self._values, self._curves))

    def gamble_at(self, time: numbers.Real) -> typing.Any:
        """Return value at requested time.

        :param time: At which position on the x-Axis shall be gambled.
        :type time: numbers.Real
        :return: The chosen value.
        """
        weights = [curve.value_at(time) for curve in self._curves]
        return self._random.choice(
            self._values, p=utilities.tools.scale_sequence_to_sum(weights, 1)
        )
