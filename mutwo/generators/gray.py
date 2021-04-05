"""Algorithms which are related to US-American researcher Frank Gray."""

import typing

__all__ = ("reflected_binary_code",)


def reflected_binary_code(
    length: int, modulus: int
) -> typing.Tuple[typing.Tuple[int, ...], ...]:
    """Make gray code where each tuple has `length` items with `modulus` different numbers.

    :param length: how long one code is
    :param modulus: how many different numbers are included

    **Example:**

    >>> from mutwo.generators import gray
    >>> gray.reflected_binary_code(2, 2)
    ((0, 0), (0, 1), (1, 1), (1, 0))
    >>> gray.reflected_binary_code(3, 2)
    ((0, 0, 0),
    (0, 0, 1),
    (0, 1, 1),
    (0, 1, 0),
    (1, 1, 0),
    (1, 1, 1),
    (1, 0, 1),
    (1, 0, 0))
    >>> gray.reflected_binary_code(2, 3)
    ((0, 0), (0, 1), (0, 2), (1, 2), (1, 1), (1, 0), (2, 0), (2, 1), (2, 2))

    Basic code has been copied from:
        https://yetalengthothermodulusathblog.com/tag/gray-codes/
    """

    def _recursive_gray_code_maker(
        length: int, modulus: int
    ) -> typing.List[typing.List[int]]:
        F = range(modulus)
        if length == 1:
            return [[i] for i in F]
        L = _recursive_gray_code_maker(length - 1, modulus)
        M: typing.List[typing.List[int]] = []
        for j in F:
            M = M + [ll + [j] for ll in L]
        k = len(M)
        Mr: typing.List[typing.List[typing.List[int]]] = [[]] * modulus
        for i in range(modulus - 1):
            i1 = i * int(k / modulus)
            i2 = (i + 1) * int(k / modulus)
            Mr[i] = M[i1:i2]
        Mr[modulus - 1] = M[(modulus - 1) * int(k / modulus) :]  # type: ignore
        for i in range(modulus):
            if i % 2 != 0:
                Mr[i].reverse()
        M0: typing.List[typing.List[int]] = []
        for i in range(modulus):
            M0 = M0 + Mr[i]
        return M0

    return tuple(
        tuple(reversed(list_)) for list_ in _recursive_gray_code_maker(length, modulus)
    )
