"""Module for algorithms which are related to the Canadian computer scientist Godfried Toussaint."""

import itertools
import typing

from mutwo.utilities import tools


def euclidean(size: int, distribution: int) -> typing.Tuple[int]:
    """Return euclidean rhythm as described in a 2005 paper by Godfried Toussaint.

    :param size: how many beats the rhythm contains
    :param distribution: how many beats are played

    The title of Toussaints paper is
    "The Euclidean Algorithm Generates Traditional Musical Rhythms".
    """

    standard_size = size // distribution
    rest = size % distribution
    data = (standard_size for _ in range(distribution))
    if rest:
        added = tuple(tools.accumulate_from_zero(euclidean(distribution, rest)))
        return tuple(s + 1 if idx in added else s for idx, s in enumerate(data))
    else:
        return tuple(data)


def _mirror(pattern: typing.Tuple[bool]) -> typing.Tuple[bool]:
    """Inverse every boolean value inside the tuple.

    Helper function for other functions.
    """
    return tuple(False if item else True for item in pattern)


def paradiddle(size: int) -> typing.Tuple[typing.Tuple[int]]:
    """Generates rhythm using the paraddidle method described by G. T. Toussaint.

    :param size: how many beats the resulting rhythm shall last. 'Size' has to be
        divisible by 2 because of the symmetrical structure of the generated rhythm.

    :return: Return nested tuple that contains two tuple where each tuple represents
        one rhythm (both rhythms are complementary to each other). The rhythms are
        encoded in absolute time values.

    The paradiddle algorithm has been described by Godfried T. Toussaint
    in his paper 'Generating “Good” Musical Rhythms Algorithmically'.
    """

    def convert_to_right_left_pattern(pattern: tuple) -> tuple:
        right = []
        left = []
        for idx, item in enumerate(pattern):
            if item:
                right.append(idx)
            else:
                left.append(idx)
        return tuple(right), tuple(left)

    # check for correct size value
    try:
        assert size % 2 == 0 and size > 2
    except AssertionError:
        message = (
            "Invalid value '{}' for argument 'size'. 'Size' has to be divisible by 2"
            " and has to be bigger than 2.".format(size)
        )
        raise ValueError(message)

    cycle = itertools.cycle((True, False))
    pattern = list(next(cycle) for n in range(size // 2))
    pattern[-1] = pattern[-2]
    return convert_to_right_left_pattern(tuple(pattern) + _mirror(pattern))


def alternating_hands(
    seed_rhythm: typing.Tuple[int],
) -> typing.Tuple[typing.Tuple[int]]:
    """Generates rhythm using the alternating hands method described by G. T. Toussaint.

    :param seed_rhythm: rhythm that shall be distributed on two hands.

    :return: Return nested tuple that contains two tuple where each tuple represents
        one rhythm (both rhythms are complementary to each other). The rhythms are
        encoded in absolute time values.

    The alternating hands algorithm has been described by Godfried T. Toussaint
    in his paper 'Generating “Good” Musical Rhythms Algorithmically'.
    """

    n_elements = len(seed_rhythm)
    absolute_rhythm = tuple(tools.accumulate_from_zero(seed_rhythm + seed_rhythm))
    cycle = itertools.cycle((True, False))
    distribution = tuple(next(cycle) for n in range(n_elements))
    distribution += _mirror(distribution)
    right, left = [], []
    for idx, dis in enumerate(distribution):
        item = absolute_rhythm[idx]
        if dis:
            right.append(item)
        else:
            left.append(item)
    return tuple(right), tuple(left)
