import functools
import operator
import unittest

from mutwo import core_utilities


class PrimeFactorsTest(unittest.TestCase):
    def test_is_prime(self):
        self.assertEqual(core_utilities.is_prime(4), False)
        self.assertEqual(core_utilities.is_prime(3), True)
        self.assertEqual(core_utilities.is_prime(100), False)
        self.assertEqual(core_utilities.is_prime(23), True)
        self.assertEqual(core_utilities.is_prime(19), True)
        self.assertEqual(core_utilities.is_prime(18), False)

    def test_factorise(self):
        factorised_numbers = ([2, 2], [2, 3, 13, 23, 31], [3, 5, 7], [11, 11, 11])
        for factorised_number in factorised_numbers:
            self.assertEqual(
                core_utilities.factorise(
                    functools.reduce(operator.mul, factorised_number)
                ),
                factorised_number,
            )

    def test_factors(self):
        factors = ([(2, 1), (3, 4), (5, 1), (11, 1)], [(5, 10)])
        for primes_and_exponents in factors:
            number = functools.reduce(
                operator.mul,
                [
                    operator.pow(*prime_and_exponent)
                    for prime_and_exponent in primes_and_exponents
                ],
            )
            self.assertEqual(
                list(core_utilities.factors(number)),
                primes_and_exponents,
            )


if __name__ == "__main__":
    unittest.main()
