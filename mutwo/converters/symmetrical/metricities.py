"""Calculate metricity of a bar"""

import functools
import math
import operator
import typing

from mutwo import converters
from mutwo.utilities import prime_factors

__all__ = ("RhythmicalStrataToIndispensabilityConverter",)


class RhythmicalStrataToIndispensabilityConverter(converters.abc.Converter):
    """Builds metrical indispensability for a rhythmical strata.

    This technique has been described by Clarence Barlow in `On the Quantification
    of Harmony and Metre` (1992). The technique aims to model the weight
    of single beats in a particular metre. It allocates each beat of a metre
    to a specific value that describes the `indispensability` of a beat: the higher the
    assigned value, the more accented the beat.
    """

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _indispensability_of_nth_beat_for_simple_meter(
        beat_index: int, prime_number: int
    ) -> int:
        """Calculate indispensability for nth beat of a metre that is composed of a singular prime number."""

        if prime_number == 2:
            return prime_number - beat_index
        elif beat_index == prime_number - 1:
            return int(prime_number / 4)
        else:
            factorised = tuple(
                sorted(prime_factors.factorise(prime_number - 1), reverse=True)
            )
            q = RhythmicalStrataToIndispensabilityConverter._indispensability_of_nth_beat(
                beat_index - int(beat_index / prime_number), factorised
            )
            return int(q + (2 * math.sqrt((q + 1) / prime_number)))

    @staticmethod
    def _indispensability_of_nth_beat(
        beat_index: int, rhythmical_strata: typing.Tuple[int, ...]
    ) -> int:
        """Calculate indispensability for the nth beat of a metre.

        The metre is defined with the primes argument.
        """

        z = len(rhythmical_strata)
        rhythmical_strata = (1,) + rhythmical_strata + (1,)
        r_sum = []
        for r in range(0, z):
            up = (beat_index - 2) % functools.reduce(
                operator.mul, tuple(rhythmical_strata[j] for j in range(1, z + 1))
            )
            down = functools.reduce(
                operator.mul, tuple(rhythmical_strata[z + 1 - k] for k in range(r + 1))
            )
            local_result = 1 + (int(1 + (up / down)) % rhythmical_strata[z - r])
            base_indispensability = RhythmicalStrataToIndispensabilityConverter._indispensability_of_nth_beat_for_simple_meter(
                local_result, rhythmical_strata[z - r]
            )
            product = functools.reduce(
                operator.mul, tuple(rhythmical_strata[i] for i in range(0, z - r))
            )
            r_sum.append(product * base_indispensability)
        return sum(r_sum)

    # ###################################################################### #
    #               public methods for interaction with the user             #
    # ###################################################################### #

    def convert(
        self, rhythmical_strata_to_convert: typing.Sequence[int]
    ) -> typing.Tuple[int, ...]:
        """Convert indispensability for each beat of a particular metre.

        :param rhythmical_strata_to_convert: The rhythmical strata defines
            the metre for which the indispensability shall be calculated. The
            rhythmical strata is a list of prime numbers which product is the
            amount of available beats within the particular metre. Earlier
            prime numbers in the rhythmical strata are considered to be more
            important than later prime numbers.
        :return: A tuple of a integer for each beat of the respective metre where
            each integer describes how accented the particular beat is (the higher the
            number, the more important the beat).

        **Example:**

        >>> from mutwo.converters import symmetrical
        >>> metricity_converter = symmetrical.metricities.RhythmicalStrataToIndispensabilityConverter()
        >>> metricity_converter.convert((2, 3))  # time signature 3/4
        (5, 0, 3, 1, 4, 2)
        >>> metricity_converter.convert((3, 2))  # time signature 6/8
        (5, 0, 2, 4, 1, 3)
        """

        # inverse so that the first numbers are more important than the later numbers
        rhythmical_strata_to_convert = tuple(reversed(rhythmical_strata_to_convert))

        length = functools.reduce(operator.mul, rhythmical_strata_to_convert)
        return tuple(
            RhythmicalStrataToIndispensabilityConverter._indispensability_of_nth_beat(
                i + 1, rhythmical_strata_to_convert
            )
            for i in range(length)
        )
