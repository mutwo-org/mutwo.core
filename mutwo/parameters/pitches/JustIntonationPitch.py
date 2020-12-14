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
from mutwo.utilities import prime_factors

ConcertPitch = typing.Union[numbers.Number, pitches.abc.Pitch]


class JustIntonationPitch(pitches.abc.Pitch):
    def __init__(
        self,
        ratio_or_exponents: typing.Union[
            str, fractions.Fraction, typing.Iterable[int]
        ] = "1/1",
        concert_pitch: ConcertPitch = 440,
    ):
        self.exponents = ratio_or_exponents
        self.concert_pitch = concert_pitch

    # properties
    @property
    def exponents(self) -> tuple:
        return self._exponents

    @exponents.setter
    def exponents(
        self,
        ratio_or_exponents: typing.Union[str, fractions.Fraction, typing.Iterable[int]],
    ) -> None:
        if isinstance(ratio_or_exponents, str):
            numerator, denominator = ratio_or_exponents.split("/")
            exponents = self.ratio_to_exponents(
                fractions.Fraction(int(numerator), int(denominator))
            )
        elif isinstance(ratio_or_exponents, typing.Iterable):
            exponents = tuple(ratio_or_exponents)
        elif isinstance(ratio_or_exponents, fractions.Fraction):
            exponents = self.ratio_to_exponents(
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

        self._exponents = self.discard_nulls(exponents)

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

        >>> m0 = JustIntonationPitch((0, 0, 1,))
        >>> m0.ratio
        fractions.Fraction(5, 4)
        >>> m0 = JustIntonationPitch.from_ratio(3, 2)
        >>> m0.ratio
        fractions.Fraction(3, 2)
        """

        return JustIntonationPitch.exponents_to_ratio(self.exponents, self.primes)

    @property
    def numerator(self) -> int:
        """Return the numerator of a JustIntonationPitch or JIPitch - object.

        >>> m0 = JustIntonationPitch((0, -1,))
        >>> m0.numerator
        1
        """

        numerator = 1
        for number, exponent in zip(self.primes, self):
            if exponent > 0:
                numerator *= pow(number, exponent)
        return numerator

    @property
    def denominator(self) -> int:
        """Return the denominator of a JustIntonationPitch or JIPitch - object.

        >>> m0 = JustIntonationPitch((0, 1,))
        >>> m0.denominator
        1
        """

        denominator = 1
        for number, exponent in zip(self.primes, self):
            if exponent < 0:
                denominator *= pow(number, -exponent)
        return denominator

    @property
    def cents(self) -> float:
        return self.ratio_to_cents(self.ratio)

    @property
    def factorised(self) -> tuple:
        """Return factorised / decomposed version of itsef.

        >>> m0 = JustIntonationPitch((0, 0, 1,))
        >>> m0.factorised
        (2, 2, 5)
        >>> m1 = JustIntonationPitch.from_ratio(7, 6)
        >>> m1.factorised
        (2, 3, 7)
        """

        vec = self._vec
        primes = self.primes
        border = self.border
        vec_adjusted, primes_adjusted = type(self).adjust_exponents(vec, primes, border)
        decomposed = ([p] * abs(e) for p, e in zip(primes_adjusted, vec_adjusted))
        return tuple(functools.reduce(operator.add, decomposed))

    @property
    def factorised_numerator_and_denominator(self) -> tuple:
        vec = self._vec
        primes = self.primes
        border = self.border
        vec_adjusted, primes_adjusted = type(self).adjust_exponents(vec, primes, border)
        num_den = [[[]], [[]]]
        for p, e in zip(primes_adjusted, vec_adjusted):
            if e > 0:
                idx = 0
            else:
                idx = 1
            num_den[idx].append([p] * abs(e))
        return tuple(
            functools.reduce(operator.add, decomposed) for decomposed in num_den
        )

    @property
    def blueprint(self, ignore: tuple = (2,)) -> tuple:
        blueprint = []
        for factorised in self.factorised_numerator_and_denominator:
            factorised = tuple(fac for fac in factorised if fac not in ignore)
            counter = collections.Counter(collections.Counter(factorised).primesues())
            if counter:
                maxima = max(counter.keys())
                blueprint.append(tuple(counter[idx + 1] for idx in range(maxima)))
            else:
                blueprint.append(tuple([]))
        return tuple(blueprint)

    def __float__(self) -> float:
        """Return the float of a JustIntonationPitch or JIPitch - object.

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

        return self.exponents_to_float(self, self.primes, self.primes_shift)

    def __repr__(self) -> str:
        return "JustIntonationPitch({})".format(self.ratio)

    @staticmethod
    def adjust_exponent_lengths(exponents0: tuple, exponents1: tuple) -> tuple:
        r"""Adjust two exponents, e.g. make their length equal.

        The length of the longer JustIntonationPitch is the reference.

        Arguments:
            * exponents0: first exponents to adjust
            * exponents1: second exponents to adjust
        >>> v0 = (1, 0, -1)
        >>> v1 = (1,)
        >>> v0_adjusted, v1_adjusted = JustIntonationPitch.adjust_exponent_lengths(v0, v1)
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
    def adjust_ratio(ratio: fractions.Fraction, border: int) -> fractions.Fraction:
        r"""Multiply or divide a fractions.Fraction - Object with the border,

        until it is equal or bigger than 1 and smaller than border.

        Arguments:
            * rratio: The Ratio, which shall be adjusted
            * border
        >>> ratio0 = fractions.Fraction(1, 3)
        >>> ratio1 = fractions.Fraction(8, 3)
        >>> border = 2
        >>> JustIntonationPitch.adjust_ratio(ratio0, border)
        fractions.Fraction(4, 3)
        >>> JustIntonationPitch.adjust_ratio(ratio1, border)
        fractions.Fraction(4, 3)

        """

        if border > 1:
            while ratio >= border:
                ratio /= border
            while ratio < 1:
                ratio *= border
        return ratio

    @staticmethod
    def adjust_float(float_: float, border: int) -> float:
        r"""Multiply float with border, until it is <= 1 and > than border.

        Arguments:
            * r: The Ratio, which shall be adjusted
            * border
        >>> float0 = 0.5
        >>> float1 = 2
        >>> border = 2
        >>> JustIntonationPitch.adjust_ratio(float0, border)
        1
        >>> JustIntonationPitch.adjust_ratio(float1, border)
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
    def adjust_exponents(exponents: tuple, primes: tuple, border: int) -> tuple:
        r"""Adjust a exponents and its primes depending on the border.

        Arguments:
            * exponents: The exponents, which shall be adjusted
            * primes: Its corresponding primes
            * border
        >>> exponents0 = (1,)
        >>> primes0 = (3,)
        >>> border = 2
        >>> JustIntonationPitch.adjust_exponents(exponents0, primes0, border)
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
    def discard_nulls(iterable: typing.Iterable) -> tuple:
        r"""Discard all zeros after the last not 0 - element of an arbitary iterable.

        Return a tuple.
        Arguments:
            * iterable: the iterable, whose 0 - elements shall
              be discarded
        >>> tuple0 = (1, 0, 2, 3, 0, 0, 0)
        >>> ls = [1, 3, 5, 0, 0, 0, 2, 0]
        >>> JustIntonationPitch.discard_nulls(tuple0)
        (1, 0, 2, 3)
        >>> JustIntonationPitch.discard_nulls(ls)
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
    def exponents_to_pair(exponents: tuple, primes: tuple) -> tuple:
        r"""Transform a JustIntonationPitch to a (numerator, denominator) - pair.

        Arguments are:
            * JustIntonationPitch -> The exponents of prime numbers
            * primes -> the referring prime numbers
        >>> myJustIntonationPitch0 = (1, 0, -1)
        >>> myJustIntonationPitch1 = (0, 2, 0)
        >>> myVal0 = (2, 3, 5)
        >>> myVal1 = (3, 5, 7)
        >>> JustIntonationPitch.exponents_to_pair(myJustIntonationPitch0, myVal0)
        (2, 5)
        >>> JustIntonationPitch.exponents_to_pair(myJustIntonationPitch0, myVal1)
        (3, 7)
        >>> JustIntonationPitch.exponents_to_pair(myJustIntonationPitch1, myVal1)
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
    def exponents_to_ratio(exponents: tuple, primes: tuple) -> fractions.Fraction:
        r"""Transform a JustIntonationPitch to a fractions.Fraction - Object

        (if installed to a quicktions.fractions.Fraction - Object,
        otherwise to a fractions.fractions.Fraction - Object).

        Arguments are:
            * JustIntonationPitch -> The exponents of prime numbers
            * primes -> the referring prime numbers for the underlying
                      ._exponents - Argument (see JustIntonationPitch._exponents).
        >>> myJustIntonationPitch0 = (1, 0, -1)
        >>> myPrimes= (2, 3, 5)
        >>> JustIntonationPitch.exponents_to_ratio(myJustIntonationPitch0, myPrimes)
        2/5
        """

        numerator, denominator = JustIntonationPitch.exponents_to_pair(
            exponents, primes
        )
        return JustIntonationPitch.adjust_ratio(
            fractions.Fraction(numerator, denominator), 1
        )

    @staticmethod
    def exponents_to_float(exponents: tuple, primes: tuple) -> float:
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
        >>> JustIntonationPitch.exponents_to_ratio(myJustIntonationPitch0, myPrimes)
        0.4
        """

        numerator, denominator = JustIntonationPitch.exponents_to_pair(
            exponents, primes
        )
        try:
            return numerator / denominator
        except OverflowError:
            return numerator // denominator

    @staticmethod
    def ratio_to_exponents(ratio: fractions.Fraction) -> ["JustIntonationPitch"]:
        r"""Transform a fractions.Fraction - Object to a vector of exponents.

        Arguments are:
            * ratio -> The fractions.Fraction, which shall be transformed
        >>> try:
        >>>     from quicktions import fractions.Fraction
        >>> except ImportError:
        >>>     from fractions import fractions.Fraction
        >>> myRatio0 = fractions.Fraction(3, 2)
        >>> JustIntonationPitch.ratio_to_exponents(myRatio0)
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

        return exponents

    @staticmethod
    def indigestibility(num: int) -> float:
        """Calculate indigestibility of a number

        The implementation follows Clarence Barlows definition
        given in 'The Ratio Book' (1992).
        Arguments:
            * num -> integer, whose indigestibility primesue shall be calculated

        >>> JustIntonationPitch.indigestibility(1)
        0
        >>> JustIntonationPitch.indigestibility(2)
        1
        >>> JustIntonationPitch.indigestibility(3)
        2.6666666666666665
        """

        decomposed = prime_factors.factorise(num)
        return JustIntonationPitch.indigestibility_of_factorised(decomposed)

    @staticmethod
    def indigestibility_of_factorised(decomposed):
        decomposed = collections.Counter(decomposed)
        decomposed = zip(decomposed.primesues(), decomposed.keys())
        summed = ((power * pow(prime - 1, 2)) / prime for power, prime in decomposed)
        return 2 * sum(summed)

    def register(self, octave: int) -> "JustIntonationPitch":
        n = self.normalize()
        factor = 2 ** abs(octave)
        if octave < 1:
            added = type(self).from_ratio(1, factor)
        else:
            added = type(self).from_ratio(factor, 1)
        p = n + added
        p.concert_pitch = self.concert_pitch
        return p

    def move_to_closest_register(
        self, reference: "JustIntonationPitch"
    ) -> "JustIntonationPitch":
        reference_register = reference.octave

        best = None
        for adaption in range(-1, 2):
            candidate = self.register(reference_register + adaption)
            difference = abs((candidate - reference).cents)
            set_best = True
            if best and difference > best[1]:
                set_best = False

            if set_best:
                best = (candidate, difference)

        best[0].concert_pitch = self.concert_pitch
        return best[0]

    @property
    def tonality(self) -> bool:
        """Return the tonality (bool) of a JustIntonationPitch or JIPitch - object.

        The tonality of a JustIntonationPitch or JIPitch - may be True (otonality) if
        the exponent of the highest occurring prime number is a
        positive number and False if the exponent is a
        negative number (utonality).

        >>> m0 = JustIntonationPitch((-2. 1))
        >>> m0.tonality
        True
        >>> m1 = JustIntonationPitch((-2, -1))
        >>> m1.tonality
        False
        >>> m2 = JustIntonationPitch([])
        >>> m2.tonality
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
        subharmonic pitches. If the return - primesue is 0,
        the interval may occur neither between the first harmonic
        and any other pitch of the harmonic scale nor
        between the first subharmonic in the and any other
        pitch of the subharmonic scale.

        >>> m0 = JustIntonationPitch((0, 1))
        >>> m0.ratio
        fractions.Fraction(3, 2)
        >>> m0.harmonic
        3
        >>> m1 = JustIntonationPitch((-1,), 2)
        >>> m1.harmonic
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
        >>> m0 = JustIntonationPitch((0, 1,))
        >>> m1 = JustIntonationPitch()
        >>> m2 = JustIntonationPitch((0, 0, 1,))
        >>> m3 = JustIntonationPitch((0, 0, -1,))
        >>> m0.harmonicity_euler
        4
        >>> m1.harmonicity_euler
        1
        >>> m2.harmonicity_euler
        7
        >>> m3.harmonicity_euler
        8
        """

        decomposed = self.factorised
        return 1 + sum(x - 1 for x in decomposed)

    @property
    def harmonicity_barlow(self) -> float:
        r"""Calculate the barlow-harmonicity of an interval.

        This implementation follows Clarence Barlows definition, given
        in 'The Ratio Book' (1992).

        A higher number means a more consonant interval / a less
        complicated harmony.

        barlow(1/1) is definied as infinite.

        >>> m0 = JustIntonationPitch((0, 1,))
        >>> m1 = JustIntonationPitch()
        >>> m2 = JustIntonationPitch((0, 0, 1,))
        >>> m3 = JustIntonationPitch((0, 0, -1,))
        >>> m0.harmonicity_barlow
        0.27272727272727276
        >>> m1.harmonicity_barlow # 1/1 is infinite harmonic
        inf
        >>> m2.harmonicity_barlow
        0.11904761904761904
        >>> m3.harmonicity_barlow
        -0.10638297872340426
        """

        def sign(x):
            return (1, -1)[x < 0]

        num_den_decomposed = self.factorised_numerator_and_denominator
        ind_num = JustIntonationPitch.indigestibility_of_factorised(
            num_den_decomposed[0]
        )
        ind_de = JustIntonationPitch.indigestibility_of_factorised(
            num_den_decomposed[1]
        )
        if ind_num == 0 and ind_de == 0:
            return float("inf")
        return sign(ind_num - ind_de) / (ind_num + ind_de)

    @property
    def harmonicity_simplified_barlow(self) -> float:
        r"""Calculate a simplified barlow-harmonicity of an interval.

        This implementation follows Clarence Barlows definition, given
        in 'The Ratio Book' (1992), with the difference that
        only positive numbers are returned and that (1/1) is
        defined as 1 instead of infinite.

        >>> m0 = JustIntonationPitch((0, 1,))
        >>> m1 = JustIntonationPitch()
        >>> m2 = JustIntonationPitch((0, 0, 1,))
        >>> m3 = JustIntonationPitch((0, 0, -1,))
        >>> m0.harmonicity_simplified_barlow
        0.27272727272727276
        >>> m1.harmonicity_simplified_barlow # 1/1 is not infinite but 1
        1
        >>> m2.harmonicity_simplified_barlow
        0.11904761904761904
        >>> m3.harmonicity_simplified_barlow # positive return primesue
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

        >>> m0 = JustIntonationPitch((0, 1,))
        >>> m1 = JustIntonationPitch()
        >>> m2 = JustIntonationPitch((0, 0, 1,))
        >>> m3 = JustIntonationPitch((0, 0, -1,))
        >>> m0.harmonicity_tenney
        2.584962500721156
        >>> m1.harmonicity_tenney
        0.0
        >>> m2.harmonicity_tenney
        4.321928094887363
        >>> m3.harmonicity_tenney
        -0.10638297872340426
        """

        ratio = self.ratio
        num = ratio.numerator
        de = ratio.denominator
        return math.log(num * de, 2)

    @property
    def lv(self) -> int:
        if self.primes:
            return abs(
                functools.reduce(math.gcd, tuple(filter(lambda x: x != 0, self)))
            )
        else:
            return 1

    def normalize(self, prime: int = 2) -> "JustIntonationPitch":
        ratio = self.ratio
        adjusted = type(self).adjust_ratio(ratio, prime)
        return type(self).from_ratio(
            adjusted.numerator, adjusted.denominator, concert_pitch=self.concert_pitch
        )

    def _math(
        self, other: "JustIntonationPitch", operation: typing.Callable
    ) -> "JustIntonationPitch":
        exponents0, exponents1 = JustIntonationPitch.adjust_exponent_lengths(
            self.exponents, other.exponents
        )
        return JustIntonationPitch(
            (operation for x, y in zip(exponents0, exponents1)), self.concert_pitch
        )

    def __add__(self, other: "JustIntonationPitch") -> "JustIntonationPitch":
        return self._math(other, operator.add)

    def __sub__(self, other: "JustIntonationPitch") -> "JustIntonationPitch":
        return self._math(other, operator.sub)

    def __mul__(self, other) -> "JustIntonationPitch":
        return self._math(other, operator.mul)

    def __div__(self, other) -> "JustIntonationPitch":
        return self._math(other, operator.div)

    def __pow__(self, other) -> "JustIntonationPitch":
        return self._math(other, lambda x, y: x ** y)

    def __abs__(self):
        if self.numerator > self.denominator:
            return copy.deepcopy(self)
        else:
            exponents = tuple(-v for v in iter(self))
            return type(self)(exponents, self.concert_pitch)

    def inverse(self, axis=None) -> "JustIntonationPitch":
        if axis is None:
            return type(self)(list(map(lambda x: -x, self)), self.concert_pitch)
        else:
            distance = self - axis
            return axis - distance
