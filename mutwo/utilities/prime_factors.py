"""
factorise and factors - function from the pyprimes - library.
(https://github.com/uzumaxy/pyprimes/blob/master/src/pyprimes/factors.py)
replaced pyprimes.primes by primesieve.Iterator(), which improves
speed about a factor of 10.
"""

import primesieve


class Prime_Generator(object):
    def __init__(self):
        self.it = primesieve.Iterator()

    def __next__(self):
        return self.it.next_prime()

    def __iter__(self):
        return self


def factorise(n: int) -> list:
    """factorise(integer) -> [list of factors]

    Returns a list of the (mostly) prime factors of integer n. For negative
    integers, -1 is included as a factor. If n is 0, 1 or -1, [n] is
    returned as the only factor. Otherwise all the factors will be prime.
    >>> factorise(-693)
    [-1, 3, 3, 7, 11]
    >>> factorise(55614)
    [2, 3, 13, 23, 31]
    """
    result = []
    for p, count in factors(n):
        result.extend([p] * count)
    return result


def factors(n: int):
    """factors(integer) -> yield factors of integer lazily

    >>> list(factors(3*7*7*7*11))
    [(3, 1), (7, 3), (11, 1)]
    Yields tuples of (factor, count) where each factor is unique and usually
    prime, and count is an integer 1 or larger.
    The factors are prime, except under the following circumstances: if the
    argument n is negative, -1 is included as a factor; if n is 0 or 1, it
    is given as the only factor. For all other integer n, all of the factors
    returned are prime.
    """
    # if n < 900000 - 1:
    if False:
        # pre = __PRECALCULATED_FACTORS[n]
        # for fac in pre:
        #     yield fac
        return
    else:
        if n in (0, 1, -1):
            yield (n, 1)
            return
        elif n < 0:
            yield (-1, 1)
            n = -n
        assert n >= 2
        for p in Prime_Generator():
            if p * p > n:
                break
            count = 0
            while n % p == 0:
                count += 1
                n //= p
            if count:
                yield (p, count)
        if n != 1:
            yield (n, 1)


def is_prime(n: int) -> bool:
    """Test if number is prime or not.

    from https://www.geeksforgeeks.org/python-program-to-check-
    whether-a-number-is-prime-or-not/
    """

    # Corner cases
    if n <= 1:
        return False
    if n <= 3:
        return True

    # This is checked so that we can skip
    # middle five numbers in below loop
    if n % 2 == 0 or n % 3 == 0:
        return False

    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i = i + 6

    return True
