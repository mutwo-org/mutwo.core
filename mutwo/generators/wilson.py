"""Algorithms which are related to US-American theorist Erv Wilson."""

import functools
import operator
import itertools
import typing

from mutwo.parameters import pitches


def make_product_pitch(
    numbers: typing.Sequence[int], tonality: bool, normalize: bool = False,
) -> pitches.JustIntonationPitch:
    """Make :class:`~mutwo.parameters.pitches.JustIntonationPitch` from the product of one, two or more numbers.

    :param numbers: The number which shall be multiplied to make a new pitch.
    :type numbers: typing.Sequence[int]
    :param tonality: ``True`` for putting the resulting product to the numerator of the
        frequency ratio and ``False`` for putting the resulting product to the
        denominator.
    :type tonality: bool
    :param normalize: ``True`` to normalize the new pitch to the middle octave.
        Default to ``False``.
    :type normalize: bool, optional
    """

    product = functools.reduce(operator.mul, numbers)
    if tonality:
        ratio = f"{product}/1"
    else:
        ratio = f"1/{product}"

    pitch = pitches.JustIntonationPitch(ratio)
    if normalize:
        pitch.normalize()
    return pitch


def make_common_product_set_scale(
    numbers: typing.Sequence[int],
    n_combinations: int,
    tonality: bool,
    normalize: bool = False,
) -> typing.Tuple[pitches.JustIntonationPitch, ...]:
    """Make common product set scale as described in Wilsons letter to Fokker.

    :param numbers: The numbers which will be combined to single pitches.
    :type numbers: typing.Sequence[int]
    :param n_combinations: How many numbers will be combined for each pitch.
    :type n_combinations: int
    :param tonality: ``True`` for otonality and ``False`` for utonality.
    :type tonality: bool
    :param normalize: ``True`` if pitches shall become normalized to the same octave.
    :type normalize: bool

    **Example:**

    >>> from mutwo.generators import wilson
    >>> wilson.make_common_product_set_scale((3, 5, 7, 9), 2, True)
    (JustIntonationPitch(15),
     JustIntonationPitch(21),
     JustIntonationPitch(27),
     JustIntonationPitch(35),
     JustIntonationPitch(45),
     JustIntonationPitch(63))
    >>> wilson.make_common_product_set_scale((3, 5, 7, 9), 2, False)
    (JustIntonationPitch(1/15),
     JustIntonationPitch(1/21),
     JustIntonationPitch(1/27),
     JustIntonationPitch(1/35),
     JustIntonationPitch(1/45),
     JustIntonationPitch(1/63))
    """

    common_product_set_scale = []
    for combined_numbers in itertools.combinations(numbers, n_combinations):
        common_product_set_scale.append(
            make_product_pitch(combined_numbers, tonality, normalize)
        )

    return tuple(common_product_set_scale)
