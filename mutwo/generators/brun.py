"""Algorithms which are related to Norwegian mathematician V. Brun."""

import abc
import typing

import numpy as np

__all__ = ("make_bruns_euclidean_algorithm_generator",)


@typing.runtime_checkable
class _BrunEuclideanElement(typing.Protocol):
    """An ABC with abstract methods __sub__, __lt__ and __gt__."""

    __slots__ = ()

    @abc.abstractmethod
    def __sub__(self) -> typing.Any:
        pass

    @abc.abstractmethod
    def __lt__(self, other) -> bool:
        pass

    @abc.abstractmethod
    def __gt__(self, other) -> bool:
        pass


def make_bruns_euclidean_algorithm_generator(
    element_tuple: tuple[
        _BrunEuclideanElement, _BrunEuclideanElement, _BrunEuclideanElement
    ],
    matrix: np.array = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=int),
    subtraction_index: typing.Literal[1, 2] = 1,
) -> typing.Generator:
    """Make generator which runs Bruns adaption of the Euclidean algorithm.

    :param element_tuple: The initial elements which gets re-calculated
        after each step. Type doesn't matter; objects only need to have
        the following magic methods: __sub__, __lt__ and __gt__.
    :type element_tuple: tuple[_BrunEuclideanElement, _BrunEuclideanElement, _BrunEuclideanElement]
    :param matrix: The initial matrix.
    :type matrix: np.array
    :param subtraction_index: This parameter has been added for the adaption of the
        function in
        :func:`~mutwo.generators.wilson.make_wilsons_brun_euclidean_algorithm_generator`
        and is not part of Bruns original algorithm. It describes whether in each step
        the first element gets subtracted by the second (original) or by the third
        (Wilson adaption) element.
    :type subtraction_index: typing.Literal[1, 2]

    This algorithm has been described by V. Brun in his paper "EUCLIDEAN ALGORITHMS
    AND MUSICAL THEORY" (1964).

    **Example:**

    >>> import fractions
    >>> from mutwo.generators import brun
    >>> bruns_euclidean_algorithm_generator = brun.make_bruns_euclidean_algorithm_generator(
    >>>     (
    >>>         fractions.Fraction(2, 1),
    >>>         fractions.Fraction(3, 2),
    >>>         fractions.Fraction(5, 4),
    >>>     )
    >>> )
    >>> next(bruns_euclidean_algorithm_generator)
    """

    while True:
        sorted_element_tuple = tuple(sorted(element_tuple, reverse=True))
        indices = [element_tuple.index(element) for element in sorted_element_tuple]
        matrix = matrix[indices]
        yield sorted_element_tuple, matrix.copy(), element_tuple[0]
        element_tuple = (
            sorted_element_tuple[0] - sorted_element_tuple[subtraction_index],
        ) + sorted_element_tuple[1:]
        matrix[1] += matrix[0]
