"""Submodule for the parameter pitch.

'Pitch' is defined as any object that knows a 'frequency' attribute.
The two major modern tuning systems Just intonation and Equal-divided-octave
are supported by the JustIntonationPitch and EqualDividedOctavePitch classes.
For using Western nomenclature (e.g. c, d, e, f, ...) mutwo offers the
WesternPitch class (which inherits from EqualDividedOctavePitch).
For a straight frequency-based approach one may use the DirectPitch class.

If desired the default concert pitch can be adjusted after importing mutwo:

    >>> from mutwo.parameters import pitches_constants
    >>> pitches_constants.DEFAULT_CONCERT_PITCH = 443

All pitch objects with a concert pitch attribute that become initialised after
overriding the default concert pitch value will by default use the new
overriden default concert pitch value.
"""

import collections
import copy
import functools
import math
import numbers
import operator
import typing

import primesieve
from primesieve import numpy as primesieve_numpy

try:
    import quicktions as fractions
except ImportError:
    import fractions

from mutwo.utilities import decorators
from mutwo.utilities import prime_factors
from mutwo.utilities import tools

from mutwo import parameters

__all__ = (
    "DirectPitch",
    "JustIntonationPitch",
    "EqualDividedOctavePitch",
    "WesternPitch",
)

ConcertPitch = typing.Union[numbers.Number, parameters.abc.Pitch]
PitchClassOrPitchClassName = typing.Union[numbers.Number, str]


class DirectPitch(parameters.abc.Pitch):
    """A simple pitch class that gets directly initialised by its frequency.

    May be used when a converter class needs a pitch object, but there is
    no need or desire for a complex abstraction of the respective pitch
    (that classes like JustIntonationPitch or WesternPitch offer).
    """

    def __init__(self, frequency: float):
        self._frequency = frequency

    @property
    def frequency(self) -> float:
        return self._frequency

    def __repr__(self) -> str:
        return "DirectPitch(frequency = {})".format(self.frequency)


class JustIntonationPitch(parameters.abc.Pitch):
    """A JustIntonationPitch is defined by a frequency ratio and a reference pitch.

    The resulting frequency is calculated by multiplying the frequency ratio
    with the respective reference pitch.

    JustIntonationPitch objects can be initialised by either
        (1) a string that indicates the frequency ratio
            for instance: "1/1", "3/2", "9/2", etc.
        (2) a fractions.Fraction (or quicktions.Fraction) object that
            indicates the frequency ratio for instance:
            fractions.Fraction(3, 2), fractions.Fraction(7, 4), etc.
        (3) an Iterable that is filled with integer that represents the exponents
            of the respective prime numbers of the decomposed frequency ratio.
            The prime numbers are rising and start with 2. Therefore the tuple
            (2, 0, -1) would return the frequency ratio 4/5 because
            (2 ** 2) * (3 ** 0) * (5 ** -1) = 4/5.

    Furthermore the concert_pitch argument can either be another Pitch object or
    a number to indicate a particular frequency in Hertz.
    """

    def __init__(
        self,
        ratio_or_exponents: typing.Union[
            str, fractions.Fraction, typing.Iterable[int]
        ] = "1/1",
        concert_pitch: ConcertPitch = None,
    ):
        if concert_pitch is None:
            concert_pitch = parameters.pitches_constants.DEFAULT_CONCERT_PITCH

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
        elif hasattr(ratio_or_exponents, "numerator") and hasattr(
            ratio_or_exponents, "denominator"
        ):
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

        return self._exponents_to_float(self.exponents, self.primes)

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
    def concert_pitch(self) -> parameters.abc.Pitch:
        return self._concert_pitch

    @concert_pitch.setter
    def concert_pitch(self, concert_pitch: ConcertPitch) -> None:
        if not isinstance(concert_pitch, parameters.abc.Pitch):
            concert_pitch = DirectPitch(concert_pitch)

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


class EqualDividedOctavePitch(parameters.abc.Pitch):
    """Class for representing pitches tuned to an Equal divided octave tuning system."""

    def __init__(
        self,
        n_pitch_classes_per_octave: int,
        pitch_class: numbers.Number,
        octave: int,
        concert_pitch_pitch_class: numbers.Number,
        concert_pitch_octave: int,
        concert_pitch: ConcertPitch = None,
    ):
        if concert_pitch is None:
            concert_pitch = parameters.pitches_constants.DEFAULT_CONCERT_PITCH

        self._n_pitch_classes_per_octave = n_pitch_classes_per_octave
        self.pitch_class = pitch_class
        self.octave = octave
        self.concert_pitch_pitch_class = concert_pitch_pitch_class
        self.concert_pitch_octave = concert_pitch_octave
        self.concert_pitch = concert_pitch

    def _assert_correct_pitch_class(self, pitch_class: numbers.Number) -> None:
        """Makes sure the respective pitch_class is within the allowed range."""

        try:
            assert all(
                (pitch_class <= self.n_pitch_classes_per_octave - 1, pitch_class >= 0)
            )
        except AssertionError:
            message = (
                "Invalid pitch class {}!. Pitch_class has to be in range (min = 0, max"
                " = {}).".format(pitch_class, self.n_pitch_classes_per_octave - 1)
            )
            raise ValueError(message)

    @property
    def n_pitch_classes_per_octave(self) -> int:
        return self._n_pitch_classes_per_octave

    @property
    def concert_pitch(self) -> parameters.abc.Pitch:
        return self._concert_pitch

    @concert_pitch.setter
    def concert_pitch(self, concert_pitch: ConcertPitch) -> None:
        if not isinstance(concert_pitch, parameters.abc.Pitch):
            concert_pitch = DirectPitch(concert_pitch)

        self._concert_pitch = concert_pitch

    @property
    def concert_pitch_pitch_class(self) -> numbers.Number:
        return self._concert_pitch_pitch_class

    @concert_pitch_pitch_class.setter
    def concert_pitch_pitch_class(self, pitch_class: numbers.Number) -> numbers.Number:
        self._assert_correct_pitch_class(pitch_class)
        self._concert_pitch_pitch_class = pitch_class

    @property
    def pitch_class(self) -> numbers.Number:
        return self._pitch_class

    @pitch_class.setter
    def pitch_class(self, pitch_class: numbers.Number) -> numbers.Number:
        self._assert_correct_pitch_class(pitch_class)
        self._pitch_class = pitch_class

    @property
    def step_factor(self):
        return pow(2, 1 / self.n_pitch_classes_per_octave)

    @property
    def n_cents_per_step(self) -> float:
        return self.ratio_to_cents(self.step_factor)

    @property
    def frequency(self) -> float:
        n_octaves_distant_to_concert_pitch = self.octave - self.concert_pitch_octave
        n_pitch_classes_distant_to_concert_pitch = (
            self.pitch_class - self.concert_pitch_pitch_class
        )
        distance_to_concert_pitch_in_cents = (
            n_octaves_distant_to_concert_pitch * 1200
        ) + (self.n_cents_per_step * n_pitch_classes_distant_to_concert_pitch)
        distance_to_concert_pitch_as_factor = self.cents_to_ratio(
            distance_to_concert_pitch_in_cents
        )
        return float(self.concert_pitch.frequency * distance_to_concert_pitch_as_factor)

    def __sub__(self, other: "EqualDividedOctavePitch") -> "EqualDividedOctavePitch":
        """Calculates the interval between two EqualDividedOctave pitches."""

        try:
            assert self.n_pitch_classes_per_octave == other.n_pitch_classes_per_octave
        except AssertionError:
            message = (
                "Can't calculate the interval between to different"
                " EqualDividedOctavePitch objects with different value for"
                " 'n_pitch_classes_per_octave'."
            )
            raise ValueError(message)

        n_pitch_classes_difference = self.pitch_class - other.pitch_class
        n_octaves_difference = self.octave - other.octave
        return n_pitch_classes_difference + (
            n_octaves_difference * self.n_pitch_classes_per_octave
        )

    def _math(
        self,
        n_pitch_classes_difference: numbers.Number,
        operator: typing.Callable[[numbers.Number, numbers.Number], numbers.Number],
    ) -> None:
        new_pitch_class = operator(self.pitch_class, n_pitch_classes_difference)
        n_octaves_difference = new_pitch_class // self.n_pitch_classes_per_octave
        new_pitch_class = new_pitch_class % self.n_pitch_classes_per_octave
        new_octave = self.octave + n_octaves_difference
        self.pitch_class = new_pitch_class
        self.octave = new_octave

    @decorators.add_return_option
    def add(
        self, n_pitch_classes_difference: numbers.Number
    ) -> typing.Union[None, "EqualDividedOctavePitch"]:
        """Transposes the EqualDividedOctavePitch by n_pitch_classes_difference."""

        self._math(n_pitch_classes_difference, operator.add)

    @decorators.add_return_option
    def subtract(
        self, n_pitch_classes_difference: numbers.Number
    ) -> typing.Union[None, "EqualDividedOctavePitch"]:
        """Transposes the EqualDividedOctavePitch by n_pitch_classes_difference."""

        self._math(n_pitch_classes_difference, operator.sub)


# TODO(add something similar to scamps SpellingPolicy (don't hard code
# if mutwo shall write a flat or sharp)
# TODO(add translation from octave number to notated octave (4 -> ', 5 -> '', ..))


class WesternPitch(EqualDividedOctavePitch):
    """A WesternPitch is a Pitch with traditional Western nomenclature.

    It uses an equal divided octave system in 12 chromatic steps.
    The nomenclature is English (c, d, e, f, g, a, b).
    Accidentals are indicated by (s = sharp) and (f = flat).
    Further microtonal accidentals are supported (see
    mutwo.parameters.parameters.parameters.pitches_constants.ACCIDENTAL_NAME_TO_PITCH_CLASS_MODIFICATION
    for all supported accidentals). Indications for the specific octave
    follow the MIDI Standard where 4 is defined as one line.
    """

    def __init__(
        self,
        pitch_class_or_pitch_class_name: PitchClassOrPitchClassName = 0,
        octave: int = 4,
        concert_pitch_pitch_class: numbers.Number = None,
        concert_pitch_octave: numbers.Number = None,
        concert_pitch: ConcertPitch = None,
    ):
        if concert_pitch_pitch_class is None:
            concert_pitch_pitch_class = (
                parameters.pitches_constants.DEFAULT_CONCERT_PITCH_PITCH_CLASS_FOR_WESTERN_PITCH
            )

        if concert_pitch_octave is None:
            concert_pitch_octave = (
                parameters.pitches_constants.DEFAULT_CONCERT_PITCH_OCTAVE_FOR_WESTERN_PITCH
            )

        (
            pitch_class,
            pitch_class_name,
        ) = self._translate_pitch_class_or_pitch_class_name_to_pitch_class_and_pitch_class_name(
            pitch_class_or_pitch_class_name
        )
        super().__init__(
            12,
            pitch_class,
            octave,
            concert_pitch_pitch_class,
            concert_pitch_octave,
            concert_pitch,
        )

        self._pitch_class_name = pitch_class_name

    @staticmethod
    def _translate_pitch_class_or_pitch_class_name_to_pitch_class_and_pitch_class_name(
        pitch_class_or_pitch_class_name: PitchClassOrPitchClassName,
    ) -> tuple:
        """Helper function to initialise a WesternPitch from a number or a string.

        A number has to represent the pitch class while the name has to use
        the Western English nomenclature with the form
        DIATONICPITCHCLASSNAME-ACCIDENTAL (e.g. "cs" for c-sharp,
        "gqf" for g-quarter-flat, "b" for b)
        """
        if isinstance(pitch_class_or_pitch_class_name, numbers.Number):
            pitch_class = float(pitch_class_or_pitch_class_name)
            pitch_class_name = WesternPitch._translate_pitch_class_to_pitch_class_name(
                pitch_class_or_pitch_class_name
            )
        elif isinstance(pitch_class_or_pitch_class_name, str):
            pitch_class = WesternPitch._translate_pitch_class_name_to_pitch_class(
                pitch_class_or_pitch_class_name
            )
            pitch_class_name = pitch_class_or_pitch_class_name
        else:
            message = "Can't initalise pitch_class by '{}' of type '{}'.".format(
                pitch_class_or_pitch_class_name, type(pitch_class_or_pitch_class_name)
            )
            raise TypeError(message)

        return pitch_class, pitch_class_name

    @staticmethod
    def _translate_accidental_to_pitch_class_modifications(
        accidental: str,
    ) -> numbers.Number:
        """Helper function to translate an accidental to its pitch class modification.

        Raises an error if the accidental hasn't been defined yet in
        mutwo.parameters.parameters.parameters.pitches_constants.ACCIDENTAL_NAME_TO_PITCH_CLASS_MODIFICATION.
        """
        try:
            return parameters.pitches_constants.ACCIDENTAL_NAME_TO_PITCH_CLASS_MODIFICATION[
                accidental
            ]
        except KeyError:
            message = (
                "Can't initialise WesternPitch with unknown accidental {}!".format(
                    accidental
                )
            )
            raise NotImplementedError(message)

    @staticmethod
    def _translate_pitch_class_name_to_pitch_class(
        pitch_class_name: str,
    ) -> numbers.Number:
        """Helper function to translate a pitch class name to its respective number.

        +/-1 is defined as one chromatic step. Smaller floating point numbers
        represent microtonal inflections..
        """
        diatonic_pitch_class_name, accidental = (
            pitch_class_name[0],
            pitch_class_name[1:],
        )
        diatonic_pitch_class = parameters.pitches_constants.DIATONIC_PITCH_NAME_TO_PITCH_CLASS[
            diatonic_pitch_class_name
        ]
        pitch_class_modification = WesternPitch._translate_accidental_to_pitch_class_modifications(
            accidental
        )
        return diatonic_pitch_class + pitch_class_modification

    @staticmethod
    def _translate_difference_to_closest_diatonic_pitch_to_accidental(
        difference_to_closest_diatonic_pitch: numbers.Number,
    ) -> str:
        """Helper function to translate a number to the closest known accidental."""
        closest_accidental = parameters.pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            tools.find_closest_item(
                difference_to_closest_diatonic_pitch,
                tuple(
                    parameters.pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME.keys()
                ),
            )
        ]
        return closest_accidental

    @staticmethod
    def _translate_pitch_class_to_pitch_class_name(pitch_class: numbers.Number) -> str:
        """Helper function to translate a pitch class in number to a string.

        The returned pitch class name uses a Western nomenclature of English
        diatonic note names. Accidental names are defined in
        mutwo.parameters.pitches_constants.ACCIDENTAL_NAME_TO_PITCH_CLASS_MODIFICATION.
        For floating point numbers the closest accidental will be chosen.
        """

        diatonic_pitch_classes = tuple(
            parameters.pitches_constants.DIATONIC_PITCH_NAME_TO_PITCH_CLASS.values()
        )
        closest_diatonic_pitch_class_index = tools.find_closest_index(
            pitch_class, diatonic_pitch_classes
        )
        closest_diatonic_pitch_class = diatonic_pitch_classes[
            closest_diatonic_pitch_class_index
        ]
        closest_diatonic_pitch = tuple(
            parameters.pitches_constants.DIATONIC_PITCH_NAME_TO_PITCH_CLASS.keys()
        )[closest_diatonic_pitch_class_index]
        difference_to_closest_diatonic_pitch = (
            pitch_class - closest_diatonic_pitch_class
        )

        accidental = WesternPitch._translate_difference_to_closest_diatonic_pitch_to_accidental(
            difference_to_closest_diatonic_pitch
        )

        pitch_class_name = "{}{}".format(closest_diatonic_pitch, accidental)
        return pitch_class_name

    def __repr__(self) -> str:
        return "{}({})".format(type(self).__name__, self.name)

    @property
    def name(self) -> str:
        return "{}{}".format(self._pitch_class_name, self.octave)

    @property
    def pitch_class_name(self) -> str:
        return self._pitch_class_name

    @pitch_class_name.setter
    def pitch_class_name(self, pitch_class_name: str):
        self._pitch_class = self._translate_pitch_class_name_to_pitch_class(
            pitch_class_name
        )
        self._pitch_class_name = pitch_class_name

    @EqualDividedOctavePitch.pitch_class.setter
    def pitch_class(self, pitch_class: numbers.Number):
        self._pitch_class_name = self._translate_pitch_class_to_pitch_class_name(
            pitch_class
        )
        self._pitch_class = pitch_class
