"""Generic algorithms which are designed by mutwo authors."""

import numbers
import typing

import expenvelope  # type: ignore
import numpy as np  # type: ignore

from mutwo import utilities


class DynamicChoice(object):
    """Weighted random choices with dynamically changing weights.

    :param values: The items to choose from.
    :type values: typing.Iterable[typing.Any]
    :param curves: The dynamically changing weight for each value.
    :type curves: typing.Iterable[expenvelope.Envelope]
    :param random_seed: The seed which shall be set at class initialisation.
    :type random_seed: int
    """

    def __init__(
        self,
        values: typing.Iterable[typing.Any],
        curves: typing.Iterable[expenvelope.Envelope],
        random_seed: int = 100,
    ):

        assert len(values) == len(curves)

        self._values = values
        self._curves = curves
        self._random = np.random.default_rng(random_seed)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._values})"

    def items(self) -> typing.Tuple[typing.Tuple[typing.Any, expenvelope.Envelope]]:
        return tuple(zip(self._values, self._curves))

    def gamble_at(self, time: numbers.Real) -> typing.Any:
        """Return value at requested time.

        :param time: At which position on the x-Axis shall be gambled.
        :type time: numbers.Real
        """
        weights = [curve.value_at(time) for curve in self._curves]
        return self._random.choice(
            self._values, p=utilities.tools.scale_sequence_to_sum(weights, 1)
        )
