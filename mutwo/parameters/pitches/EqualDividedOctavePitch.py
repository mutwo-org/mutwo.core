import numbers
import operator
import typing

from mutwo.parameters import pitches
from mutwo.utilities import decorators

ConcertPitch = typing.Union[numbers.Number, pitches.abc.Pitch]


class EqualDividedOctavePitch(pitches.abc.Pitch):
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
            concert_pitch = pitches.constants.DEFAULT_CONCERT_PITCH
        self._n_pitch_classes_per_octave = n_pitch_classes_per_octave
        self.pitch_class = pitch_class
        self.octave = octave
        self.concert_pitch_pitch_class = concert_pitch_pitch_class
        self.concert_pitch_octave = concert_pitch_octave
        self.concert_pitch = concert_pitch

    def _assert_correct_pitch_class(self, pitch_class: numbers.Number) -> None:
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
    def concert_pitch(self) -> pitches.abc.Pitch:
        return self._concert_pitch

    @concert_pitch.setter
    def concert_pitch(self, concert_pitch: ConcertPitch) -> None:
        if not isinstance(concert_pitch, pitches.abc.Pitch):
            concert_pitch = pitches.DirectPitch(concert_pitch)

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

    @decorators.add_return_option
    def _math(
        self,
        other: "EqualDividedOctavePitch",
        operator: typing.Callable[[numbers.Number, numbers.Number], numbers.Number],
    ) -> "EqualDividedOctavePitch":
        try:
            assert self.n_pitch_classes_per_octave == other.n_pitch_classes_per_octave
        except AssertionError:
            message = (
                "Can't apply mathematical operation on two EqualDividedOctavePitch"
                " objects with different value for 'n_pitch_classes_per_octave'."
            )
            raise ValueError(message)

        new_pitch_class = self.pitch_class + other.pitch_class
        n_octaves_difference = new_pitch_class // self.n_pitch_classes_per_octave
        new_pitch_class = new_pitch_class % self.n_pitch_classes_per_octave
        new_octave = self.octave + other.octave + n_octaves_difference
        self.pitch_class = new_pitch_class
        self.octave = new_octave

    def __add__(self, other: "EqualDividedOctavePitch") -> "EqualDividedOctavePitch":
        return self._math(self, other, operator.add, mutate=False)

    def __sub__(self, other: "EqualDividedOctavePitch") -> "EqualDividedOctavePitch":
        return self._math(self, other, operator.sub, mutate=False)

    @decorators.add_return_option
    def add(
        self, other: "EqualDividedOctavePitch"
    ) -> typing.Union[None, "EqualDividedOctavePitch"]:
        self._math(self, other, operator.add)

    @decorators.add_return_option
    def subtract(
        self, other: "EqualDividedOctavePitch"
    ) -> typing.Union[None, "EqualDividedOctavePitch"]:
        self._math(self, other, operator.sub)
