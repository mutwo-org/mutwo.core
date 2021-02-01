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
