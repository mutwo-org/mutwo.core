import collections
import copy
import functools
import math
import numbers
import operator
import typing

try:
    import quicktions as fractions
except ImportError:
    import fractions

import primesieve
from primesieve import numpy as primesieve_numpy

from mutwo.parameters import pitches
from mutwo.utilities import decorators
from mutwo.utilities import prime_factors

ConcertPitch = typing.Union[numbers.Number, pitches.abc.Pitch]


class JustIntonationPitch(pitches.abc.Pitch):
    def __init__(
        self,
        ratio_or_exponents: typing.Union[
            str, fractions.Fraction, typing.Iterable[int]
        ] = "1/1",
        concert_pitch: ConcertPitch = pitches.constants.DEFAULT_CONCERT_PITCH,
    ):
        self.exponents = self._translate_ratio_or_fractions_argument_to_exponents(
            ratio_or_exponents
        )
        self.concert_pitch = concert_pitch

    # ###################################################################### #
    #                      static private methods                            #
    # ###################################################################### #
    @staticmethod
    def _adjust_exponent_lengths(exponents0: tuple, exponents1: tuple) -> tuple:
        r"""Adjust two exponents, e.g. make their length equal.

        The length of the longer JustIntonationPitch is the reference.

        Arguments:
            * exponents0: first exponents to adjust
            * exponents1: second exponents to adjust
        >>> v0 = (1, 0, -1)
        >>> v1 = (1,)
        >>> v0_adjusted, v1_adjusted = JustIntonationPitch._adjust_exponent_lengths(v0, v1)
        >>> v0_adjusted
        (1, 0, -1)
        >>> v1_adjusted
        (1, 0, 0)
        """

        length0 = len(exponents0)
        length1 = len(exponents1)
        if length0 > length1:
            return exponents0, exponents1 + (0,) * (length0 - length1)
        else:
            return exponents0 + (0,) * (length1 - length0), exponents1

    @staticmethod
    def _adjust_ratio(ratio: fractions.Fraction, border: int) -> fractions.Fraction:
        r"""Multiply or divide a fractions.Fraction - Object with the border,

        until it is equal or bigger than 1 and smaller than border.

        Arguments:
            * rratio: The Ratio, which shall be adjusted
            * border
        >>> ratio0 = fractions.Fraction(1, 3)
        >>> ratio1 = fractions.Fraction(8, 3)
        >>> border = 2
        >>> JustIntonationPitch._adjust_ratio(ratio0, border)
        fractions.Fraction(4, 3)
        >>> JustIntonationPitch._adjust_ratio(ratio1, border)
        fractions.Fraction(4, 3)

        """

        if border > 1:
            while ratio >= border:
                ratio /= border
            while ratio < 1:
                ratio *= border
        return ratio

    @staticmethod
    def _adjust_float(float_: float, border: int) -> float:
        r"""Multiply float with border, until it is <= 1 and > than border.

        Arguments:
            * float_: The float, which shall be adjusted
            * border
        >>> float0 = 0.5
        >>> float1 = 2
        >>> border = 2
        >>> JustIntonationPitch._adjust_float(float0, border)
        1
        >>> JustIntonationPitch._adjust_float(float1, border)
        1
        """

        if border > 1:
            while float_ > border:
                try:
                    float_ /= border
                except OverflowError:
                    float_ //= border
            while float_ < 1:
                float_ *= border
        return float_

    @staticmethod
    def _adjust_exponents(exponents: tuple, primes: tuple, border: int) -> tuple:
        r"""Adjust a exponents and its primes depending on the border.

        Arguments:
            * exponents: The exponents, which shall be adjusted
            * primes: Its corresponding primes
            * border
        >>> exponents0 = (1,)
        >>> primes0 = (3,)
        >>> border = 2
        >>> JustIntonationPitch._adjust_exponents(exponents0, primes0, border)
        ((-1, 1), (2, 3))

        """  # TODO(DOCSTRING) Make proper description what actually happens

        if exponents:
            if border > 1:
                multiplied = functools.reduce(
                    operator.mul, (p ** e for p, e in zip(primes, exponents))
                )
                res = math.log(border / multiplied, border)
                if res < 0:
                    res -= 1
                res = int(res)
                primes = (border,) + primes
                exponents = (res,) + exponents
            return exponents, primes
        return (1,), (1,)

    @staticmethod
    def _discard_nulls(iterable: typing.Iterable) -> tuple:
        r"""Discard all zeros after the last not 0 - element of an arbitary iterable.

        Return a tuple.
        Arguments:
            * iterable: the iterable, whose 0 - elements shall
              be discarded
        >>> tuple0 = (1, 0, 2, 3, 0, 0, 0)
        >>> ls = [1, 3, 5, 0, 0, 0, 2, 0]
        >>> JustIntonationPitch._discard_nulls(tuple0)
        (1, 0, 2, 3)
        >>> JustIntonationPitch._discard_nulls(ls)
        (1, 3, 5, 0, 0, 0, 2)
        """

        iterable = tuple(iterable)
        c = 0
        for i in reversed(iterable):
            if i != 0:
                break
            c += 1
        if c != 0:
            return iterable[:-c]
        return iterable

    @staticmethod
    def _exponents_to_pair(exponents: tuple, primes: tuple) -> tuple:
        r"""Transform a JustIntonationPitch to a (numerator, denominator) - pair.

        Arguments are:
            * JustIntonationPitch -> The exponents of prime numbers
            * primes -> the referring prime numbers
        >>> myJustIntonationPitch0 = (1, 0, -1)
        >>> myJustIntonationPitch1 = (0, 2, 0)
        >>> myVal0 = (2, 3, 5)
        >>> myVal1 = (3, 5, 7)
        >>> JustIntonationPitch._exponents_to_pair(myJustIntonationPitch0, myVal0)
        (2, 5)
        >>> JustIntonationPitch._exponents_to_pair(myJustIntonationPitch0, myVal1)
        (3, 7)
        >>> JustIntonationPitch._exponents_to_pair(myJustIntonationPitch1, myVal1)
        (25, 1)
        """

        numerator = 1
        denominator = 1
        for number, exponent in zip(primes, exponents):
            if exponent > 0:
                numerator *= pow(number, exponent)
            elif exponent < 0:
                denominator *= pow(number, -exponent)
        return numerator, denominator

    @staticmethod
    def _exponents_to_ratio(exponents: tuple, primes: tuple) -> fractions.Fraction:
        r"""Transform a JustIntonationPitch to a fractions.Fraction - Object

        (if installed to a quicktions.fractions.Fraction - Object,
        otherwise to a fractions.fractions.Fraction - Object).

        Arguments are:
            * JustIntonationPitch -> The exponents of prime numbers
            * primes -> the referring prime numbers for the underlying
                      ._exponents - Argument (see JustIntonationPitch._exponents).
        >>> myJustIntonationPitch0 = (1, 0, -1)
        >>> myPrimes= (2, 3, 5)
        >>> JustIntonationPitch._exponents_to_ratio(myJustIntonationPitch0, myPrimes)
        2/5
        """

        numerator, denominator = JustIntonationPitch._exponents_to_pair(
            exponents, primes
        )
        return JustIntonationPitch._adjust_ratio(
            fractions.Fraction(numerator, denominator), 1
        )

    @staticmethod
    def _exponents_to_float(exponents: tuple, primes: tuple) -> float:
        r"""Transform a JustIntonationPitch to a float.

        Arguments are:
            * JustIntonationPitch -> The exponents of prime numbers
            * primes -> the referring prime numbers for the underlying
                      ._exponents - Argument (see JustIntonationPitch._exponents).
            * primes-shift -> how many prime numbers shall be skipped
                            (see JustIntonationPitch.primes_shift)
        >>> myJustIntonationPitch0 = (1, 0, -1)
        >>> myJustIntonationPitch1 = (0, 2, 0)
        >>> myPrimes = (2, 3, 5)
        >>> JustIntonationPitch._exponents_to_float(myJustIntonationPitch0, myPrimes)
        0.4
        """

        numerator, denominator = JustIntonationPitch._exponents_to_pair(
            exponents, primes
        )
        try:
            return numerator / denominator
        except OverflowError:
            return numerator // denominator

    @staticmethod
    def _ratio_to_exponents(ratio: fractions.Fraction) -> tuple:
        r"""Transform a fractions.Fraction - Object to a vector of exponents.

        Arguments are:
            * ratio -> The fractions.Fraction, which shall be transformed
        >>> try:
        >>>     from quicktions import fractions.Fraction
        >>> except ImportError:
        >>>     from fractions import fractions.Fraction
        >>> myRatio0 = fractions.Fraction(3, 2)
        >>> JustIntonationPitch._ratio_to_exponents(myRatio0)
        (-1, 1)
        """

        factorised_numerator = prime_factors.factors(ratio.numerator)
        factorised_denominator = prime_factors.factors(ratio.denominator)

        factorised_num = prime_factors.factorise(ratio.numerator)
        factorised_den = prime_factors.factorise(ratio.denominator)

        biggest_prime = max(factorised_num + factorised_den)
        exponents = [0] * primesieve.count_primes(biggest_prime)

        for prime, fac in factorised_numerator:
            if prime > 1:
                exponents[primesieve.count_primes(prime) - 1] += fac

        for prime, fac in factorised_denominator:
            if prime > 1:
                exponents[primesieve.count_primes(prime) - 1] -= fac

        return tuple(exponents)

    @staticmethod
    def _indigestibility(num: int) -> float:
        """Calculate _indigestibility of a number

        The implementation follows Clarence Barlows definition
        given in 'The Ratio Book' (1992).
        Arguments:
            * num -> integer, whose _indigestibility value shall be calculated

        >>> JustIntonationPitch._indigestibility(1)
        0
        >>> JustIntonationPitch._indigestibility(2)
        1
        >>> JustIntonationPitch._indigestibility(3)
        2.6666666666666665
        """

        decomposed = prime_factors.factorise(num)
        return JustIntonationPitch._indigestibility_of_factorised(decomposed)

    @staticmethod
    def _indigestibility_of_factorised(decomposed):
        decomposed = collections.Counter(decomposed)
        decomposed = zip(decomposed.values(), decomposed.keys())
        summed = ((power * pow(prime - 1, 2)) / prime for power, prime in decomposed)
        return 2 * sum(summed)

    # ###################################################################### #
    #                            private methods                             #
    # ###################################################################### #

    def _translate_ratio_or_fractions_argument_to_exponents(
        self,
        ratio_or_exponents: typing.Union[str, fractions.Fraction, typing.Iterable[int]],
    ):
        if isinstance(ratio_or_exponents, str):
            numerator, denominator = ratio_or_exponents.split("/")
            exponents = self._ratio_to_exponents(
                fractions.Fraction(int(numerator), int(denominator))
            )
        elif isinstance(ratio_or_exponents, typing.Iterable):
            exponents = tuple(ratio_or_exponents)
        elif isinstance(ratio_or_exponents, fractions.Fraction):
            exponents = self._ratio_to_exponents(
                fractions.Fraction(
                    ratio_or_exponents.numerator, ratio_or_exponents.denominator
                )
            )
        else:
            message = (
                "Unknown type '{}' of object '{}' for 'ratio_or_exponents' argument."
                .format(type(ratio_or_exponents), ratio_or_exponents)
            )
            raise NotImplementedError(message)
        return exponents

    @decorators.add_return_option
    def _math(
        self, other: "JustIntonationPitch", operation: typing.Callable
    ) -> "JustIntonationPitch":
        exponents0, exponents1 = JustIntonationPitch._adjust_exponent_lengths(
            self.exponents, other.exponents
        )
        self.exponents = tuple(operation(x, y) for x, y in zip(exponents0, exponents1))

    # ###################################################################### #
    #                            magic methods                               #
    # ###################################################################### #

    def __float__(self) -> float:
        """Return the float of a JustIntonationPitch - object.

        These are the same:
            float(myJustIntonationPitch.ratio) == float(myJustIntonationPitch).
        Note the difference that the second version might be slightly
        more performant.

        >>> jip0 = JustIntonationPitch((-1, 1))
        >>> float(jip0)
        1.5
        >>> float(jip0.ratio)
        1.5
        """

        return self._exponents_to_float(self, self.primes)

    def __repr__(self) -> str:
        return "JustIntonationPitch({})".format(self.ratio)

    def __add__(self, other: "JustIntonationPitch") -> "JustIntonationPitch":
        return self._math(other, operator.add, mutate=False)

    def __sub__(self, other: "JustIntonationPitch") -> "JustIntonationPitch":
        return self._math(other, operator.sub, mutate=False)

    def __abs__(self):
        if self.numerator > self.denominator:
            return copy.deepcopy(self)
        else:
            exponents = tuple(-v for v in iter(self.exponents))
            return type(self)(exponents, self.concert_pitch)

    # ###################################################################### #
    #                            properties                                  #
    # ###################################################################### #

    @property
    def exponents(self) -> tuple:
        return self._exponents

    @exponents.setter
    def exponents(self, exponents: typing.Iterable[int],) -> None:
        self._exponents = self._discard_nulls(exponents)

    @property
    def primes(self) -> tuple:
        r"""Return ascending list of primes, until the highest contained Prime.

        >>> jip0 = JustIntonationPitch((0, 1, 2))
        >>> jip0.exponents
        (2, 3, 5)
        >>> jip1 = JustIntonationPitch((0, -1, 0, 0, 1), 1)
        >>> jip1.exponents
        (2, 3, 5, 7, 11)
        """

        return tuple(primesieve_numpy.n_primes(len(self.exponents)))

    @property
    def occupied_primes(self) -> tuple:
        """Return all occurring prime numbers of a JustIntonationPitch object."""

        return tuple(
            prime
            for prime, exponent in zip(self.primes, self.exponents)
            if exponent != 0
        )

    @property
    def concert_pitch(self) -> pitches.abc.Pitch:
        return self._concert_pitch

    @concert_pitch.setter
    def concert_pitch(self, concert_pitch: ConcertPitch) -> None:
        if not isinstance(concert_pitch, pitches.abc.Pitch):
            concert_pitch = pitches.DirectPitch(concert_pitch)

        self._concert_pitch = concert_pitch

    @property
    def frequency(self) -> float:
        return float(self.ratio * self.concert_pitch.frequency)

    @property
    def ratio(self) -> fractions.Fraction:
        """Return the JustIntonationPitch transformed to a Ratio.

        >>> jip0 = JustIntonationPitch((0, 0, 1,))
        >>> jip0.ratio
        fractions.Fraction(5, 4)
        >>> jip0 = JustIntonationPitch("3/2")
        >>> jip0.ratio
        fractions.Fraction(3, 2)
        """

        return JustIntonationPitch._exponents_to_ratio(self.exponents, self.primes)

    @property
    def numerator(self) -> int:
        """Return the numerator of a JustIntonationPitch - object.

        >>> jip0 = JustIntonationPitch((0, -1,))
        >>> jip0.numerator
        1
        """

        numerator = 1
        for number, exponent in zip(self.primes, self.exponents):
            if exponent > 0:
                numerator *= pow(number, exponent)
        return numerator

    @property
    def denominator(self) -> int:
        """Return the denominator of a JustIntonationPitch - object.

        >>> jip0 = JustIntonationPitch((0, 1,))
        >>> jip0.denominator
        1
        """

        denominator = 1
        for number, exponent in zip(self.primes, self.exponents):
            if exponent < 0:
                denominator *= pow(number, -exponent)
        return denominator

    @property
    def cents(self) -> float:
        return self.ratio_to_cents(self.ratio)

    @property
    def factorised(self) -> tuple:
        """Return factorised / decomposed version of itsef.

        >>> jip0 = JustIntonationPitch((0, 0, 1,))
        >>> jip0.factorised
        (2, 2, 5)
        >>> jip1 = JustIntonationPitch("7/6")
        >>> jip1.factorised
        (2, 3, 7)
        """

        exponents = self.exponents
        primes = self.primes
        exponents_adjusted, primes_adjusted = type(self)._adjust_exponents(
            exponents, primes, 1
        )
        decomposed = ([p] * abs(e) for p, e in zip(primes_adjusted, exponents_adjusted))
        return tuple(functools.reduce(operator.add, decomposed))

    @property
    def factorised_numerator_and_denominator(self) -> tuple:
        exponents = self.exponents
        primes = self.primes
        exponents_adjusted, primes_adjusted = type(self)._adjust_exponents(
            exponents, primes, 1
        )
        numerator_denominator = [[[]], [[]]]
        for prime, exponent in zip(primes_adjusted, exponents_adjusted):
            if exponent > 0:
                idx = 0
            else:
                idx = 1
            numerator_denominator[idx].append([prime] * abs(exponent))
        return tuple(
            functools.reduce(operator.add, decomposed)
            for decomposed in numerator_denominator
        )

    @property
    def octave(self) -> int:
        ct = self.cents
        ref, exp = 1200, 0
        while ref * exp <= ct:
            exp += 1
        while ref * exp > ct:
            exp -= 1
        return exp

    @property
    def blueprint(self, ignore: typing.Sequence[int] = (2,)) -> tuple:
        blueprint = []
        for factorised in self.factorised_numerator_and_denominator:
            factorised = tuple(fac for fac in factorised if fac not in ignore)
            counter = collections.Counter(collections.Counter(factorised).values())
            if counter:
                maxima = max(counter.keys())
                blueprint.append(tuple(counter[idx + 1] for idx in range(maxima)))
            else:
                blueprint.append(tuple([]))
        return tuple(blueprint)

    @property
    def tonality(self) -> bool:
        """Return the tonality (bool) of a JustIntonationPitch - object.

        The tonality of a JustIntonationPitch   - may be True (otonality) if
        the exponent of the highest occurring prime number is a
        positive number and False if the exponent is a
        negative number (utonality).

        >>> jip0 = JustIntonationPitch((-2. 1))
        >>> jip0.tonality
        True
        >>> jip1 = JustIntonationPitch((-2, -1))
        >>> jip1.tonality
        False
        >>> jip2 = JustIntonationPitch([])
        >>> jip2.tonality
        True
        """

        if self.exponents:
            maxima = max(self.exponents)
            minima = min(self.exponents)
            test = (
                maxima <= 0 and minima < 0,
                minima < 0
                and self.exponents.index(minima) > self.exponents.index(maxima),
            )
            if any(test):
                return False

        return True

    @property
    def harmonic(self) -> int:
        """Return the nth - harmonic / subharmonic the pitch may represent.

        May be positive for harmonic and negative for
        subharmonic pitches. If the return - value is 0,
        the interval may occur neither between the first harmonic
        and any other pitch of the harmonic scale nor
        between the first subharmonic in the and any other
        pitch of the subharmonic scale.

        >>> jip0 = JustIntonationPitch((0, 1))
        >>> jip0.ratio
        fractions.Fraction(3, 2)
        >>> jip0.harmonic
        3
        >>> jip1 = JustIntonationPitch((-1,), 2)
        >>> jip1.harmonic
        -3
        """

        ratio = self.ratio

        if ratio.denominator % 2 == 0:
            return ratio.numerator
        elif ratio.numerator % 2 == 0:
            return -ratio.denominator
        elif ratio == fractions.Fraction(1, 1):
            return 1
        else:
            return 0

    @property
    def primes_for_numerator_and_denominator(self) -> tuple:
        return tuple(
            tuple(sorted(set(prime_factors.factorise(n))))
            for n in (self.numerator, self.denominator)
        )

    @property
    def harmonicity_wilson(self) -> int:
        decomposed = self.factorised
        return int(sum(filter(lambda x: x != 2, decomposed)))

    @property
    def harmonicity_vogel(self) -> int:
        decomposed = self.factorised
        decomposed_filtered = tuple(filter(lambda x: x != 2, decomposed))
        am_2 = len(decomposed) - len(decomposed_filtered)
        return int(sum(decomposed_filtered) + am_2)

    @property
    def harmonicity_euler(self) -> int:
        """Return the 'gradus suavitatis' of euler.

        A higher number means a less consonant interval /
        a more complicated harmony.
        euler(1/1) is definied as 1.
        >>> jip0 = JustIntonationPitch((0, 1,))
        >>> jip1 = JustIntonationPitch()
        >>> jip2 = JustIntonationPitch((0, 0, 1,))
        >>> jip3 = JustIntonationPitch((0, 0, -1,))
        >>> jip0.harmonicity_euler
        4
        >>> jip1.harmonicity_euler
        1
        >>> jip2.harmonicity_euler
        7
        >>> jip3.harmonicity_euler
        8
        """

        decomposed = self.factorised
        return 1 + sum(x - 1 for x in decomposed)

    @property
    def harmonicity_barlow(self) -> float:
        r"""Calculate the barlow-harmonicity of an interval.

        This implementation follows Clarence Barlows definition, given
        in 'The Ratio Book' (1992).

        A higher number means a more harmonic interval / a less
        complex harmony.

        barlow(1/1) is definied as infinite.

        >>> jip0 = JustIntonationPitch((0, 1,))
        >>> jip1 = JustIntonationPitch()
        >>> jip2 = JustIntonationPitch((0, 0, 1,))
        >>> jip3 = JustIntonationPitch((0, 0, -1,))
        >>> jip0.harmonicity_barlow
        0.27272727272727276
        >>> jip1.harmonicity_barlow # 1/1 is infinite harmonic
        inf
        >>> jip2.harmonicity_barlow
        0.11904761904761904
        >>> jip3.harmonicity_barlow
        -0.10638297872340426
        """

        def sign(x):
            return (1, -1)[x < 0]

        numerator_denominator_decomposed = self.factorised_numerator_and_denominator
        indigestibility_numerator = JustIntonationPitch._indigestibility_of_factorised(
            numerator_denominator_decomposed[0]
        )
        indigestibility_denominator = JustIntonationPitch._indigestibility_of_factorised(
            numerator_denominator_decomposed[1]
        )
        if indigestibility_numerator == 0 and indigestibility_denominator == 0:
            return float("inf")
        return sign(indigestibility_numerator - indigestibility_denominator) / (
            indigestibility_numerator + indigestibility_denominator
        )

    @property
    def harmonicity_simplified_barlow(self) -> float:
        r"""Calculate a simplified barlow-harmonicity of an interval.

        This implementation follows Clarence Barlows definition, given
        in 'The Ratio Book' (1992), with the difference that
        only positive numbers are returned and that (1/1) is
        defined as 1 instead of infinite.

        >>> jip0 = JustIntonationPitch((0, 1,))
        >>> jip1 = JustIntonationPitch()
        >>> jip2 = JustIntonationPitch((0, 0, 1,))
        >>> jip3 = JustIntonationPitch((0, 0, -1,))
        >>> jip0.harmonicity_simplified_barlow
        0.27272727272727276
        >>> jip1.harmonicity_simplified_barlow # 1/1 is not infinite but 1
        1
        >>> jip2.harmonicity_simplified_barlow
        0.11904761904761904
        >>> jip3.harmonicity_simplified_barlow # positive return value
        0.10638297872340426
        """

        barlow = abs(self.harmonicity_barlow)
        if barlow == float("inf"):
            return 1
        return barlow

    @property
    def harmonicity_tenney(self) -> float:
        r"""Calculate Tenneys harmonic distance of an interval

        A higher number
        means a more consonant interval / a less
        complicated harmony.

        tenney(1/1) is definied as 0.

        >>> jip0 = JustIntonationPitch((0, 1,))
        >>> jip1 = JustIntonationPitch()
        >>> jip2 = JustIntonationPitch((0, 0, 1,))
        >>> jip3 = JustIntonationPitch((0, 0, -1,))
        >>> jip0.harmonicity_tenney
        2.584962500721156
        >>> jip1.harmonicity_tenney
        0.0
        >>> jip2.harmonicity_tenney
        4.321928094887363
        >>> jip3.harmonicity_tenney
        -0.10638297872340426
        """

        ratio = self.ratio
        num = ratio.numerator
        de = ratio.denominator
        return math.log(num * de, 2)

    @property
    def level(self) -> int:
        if self.primes:
            return abs(
                functools.reduce(
                    math.gcd, tuple(filter(lambda x: x != 0, self.exponents))
                )
            )
        else:
            return 1

    # ###################################################################### #
    #                            public methods                              #
    # ###################################################################### #

    @decorators.add_return_option
    def register(self, octave: int) -> typing.Union[None, "JustIntonationPitch"]:
        normalized_just_intonation_pitch = self.normalize(mutate=False)
        factor = 2 ** abs(octave)
        if octave < 1:
            added = type(self)(fractions.Fraction(1, factor))
        else:
            added = type(self)(fractions.Fraction(factor, 1))
        self.exponents = (normalized_just_intonation_pitch + added).exponents

    @decorators.add_return_option
    def move_to_closest_register(
        self, reference: "JustIntonationPitch"
    ) -> typing.Union[None, "JustIntonationPitch"]:
        reference_register = reference.octave

        best = None
        for adaption in range(-1, 2):
            candidate = self.register(reference_register + adaption, mutate=False)
            difference = abs((candidate - reference).cents)
            set_best = True
            if best and difference > best[1]:
                set_best = False

            if set_best:
                best = (candidate, difference)

        self.exponents = best[0].exponents

    @decorators.add_return_option
    def normalize(self, prime: int = 2) -> typing.Union[None, "JustIntonationPitch"]:
        """Normalize JustIntonationPitch."""
        ratio = self.ratio
        adjusted = type(self)._adjust_ratio(ratio, prime)
        self.exponents = self._translate_ratio_or_fractions_argument_to_exponents(
            adjusted
        )

    @decorators.add_return_option
    def inverse(
        self, axis: typing.Union[None, "JustIntonationPitch"] = None
    ) -> typing.Union[None, "JustIntonationPitch"]:
        if axis is None:
            exponents = list(map(lambda x: -x, self.exponents))
        else:
            distance = self - axis
            exponents = (axis - distance).exponents
        self.exponents = exponents

    @decorators.add_return_option
    def add(
        self, other: "JustIntonationPitch"
    ) -> typing.Union[None, "JustIntonationPitch"]:
        self._math(other, operator.add)

    @decorators.add_return_option
    def subtract(
        self, other: "JustIntonationPitch"
    ) -> typing.Union[None, "JustIntonationPitch"]:
        self._math(other, operator.sub)
