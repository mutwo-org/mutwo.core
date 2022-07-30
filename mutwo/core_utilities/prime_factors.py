"""Prime number calculations.

The functions "factorise" and "factors" are copied from the `pyprimes
library <https://github.com/uzumaxy/pyprimes/blob/master/src/pyprimes/factors.py>`_.
In mutwo the function :func:`pyprimes.primes` has been replaced by
:class:`primesieve.Iterator()`, which improves speed by a factor of 10.
"""

import typing

import primesieve  # type: ignore

__all__ = ("factorise", "factors", "is_prime")


class PrimeGenerator(object):
    """Generator that yields the rising series of primes starting from 2."""

    def __init__(self):
        self.iterator = primesieve.Iterator()

    def __next__(self) -> int:
        return self.iterator.next_prime()

    def __iter__(self) -> typing.Iterator:
        return self


def factorise(number_to_factorise: int) -> list[int]:
    """factorise(integer) -> [list of factors]

    :param number_to_factorise: The number which shall be factorised.
    :return: Returns a list of the (mostly) prime factors of integer n. For negative
        integers, -1 is included as a factor. If n is 0, 1 or -1, [n] is
        returned as the only factor. Otherwise all the factors will be prime.

    **Example:**

    >>> factorise(-693)
    [-1, 3, 3, 7, 11]
    >>> factorise(55614)
    [2, 3, 13, 23, 31]
    """
    result_list = []
    for prime_number, prime_number_count in factors(number_to_factorise):
        result_list.extend([prime_number] * prime_number_count)
    return result_list


def factors(number: int) -> typing.Generator:
    """Get factor generator

    :param number: The number from which to yield factors.

    Yields tuples of (factor, count) where each factor is unique and usually
    prime, and count is an integer 1 or larger.
    The factors are prime, except under the following circumstances: if the
    argument n is negative, -1 is included as a factor; if n is 0 or 1, it
    is given as the only factor. For all other integer n, all of the factors
    returned are prime.

    **Example:**

    >>> list(factors(3*7*7*7*11))
    [(3, 1), (7, 3), (11, 1)]
    """
    if number in (0, 1, -1):
        yield (number, 1)
        return
    elif number < 0:
        yield (-1, 1)
        number = -number
    assert number >= 2
    for prime_number in PrimeGenerator():
        if prime_number * prime_number > number:
            break
        count = 0
        while number % prime_number == 0:
            count += 1
            number //= prime_number
        if count:
            yield (prime_number, count)
    if number != 1:
        yield (number, 1)


def is_prime(number_to_test: int) -> bool:
    """Test if number is prime or not.

    :param number_to_test: The number which shall be tested.
    :return: True if number is prime and False if number isn't a Prime.

    (`has been copied from here
    <https://www.geeksforgeeks.org/python-program-to-check-
    whether-a-number-is-prime-or-not/>`_)
    """

    # Corner cases
    if number_to_test <= 1:
        return False
    if number_to_test <= 3:
        return True

    # This is checked so that we can skip
    # middle five numbers in below loop
    if number_to_test % 2 == 0 or number_to_test % 3 == 0:
        return False

    i = 5
    while i * i <= number_to_test:
        if number_to_test % i == 0 or number_to_test % (i + 2) == 0:
            return False
        i = i + 6

    return True
