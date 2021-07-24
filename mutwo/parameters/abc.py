"""Abstract base classes for different parameters."""

import abc
import dataclasses
import functools
import math
import typing

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

from mutwo.parameters import pitches_constants
from mutwo.parameters import volumes_constants
from mutwo.utilities import constants
from mutwo.utilities import tools

__all__ = ("Pitch", "Volume", "PlayingIndicator", "NotationIndicator")


class Parameter(abc.ABC):
    """Abstract base class for any parameter class."""

    pass


ParameterType = object
DurationType = constants.Real


@functools.total_ordering  # type: ignore
class Pitch(Parameter):
    """Abstract base class for any pitch class.

    If the user wants to define a new pitch class, the abstract
    property :attr:`frequency` has to be overridden.
    """

    # conversion methods between different pitch describing units
    @staticmethod
    def hertz_to_cents(frequency0: constants.Real, frequency1: constants.Real) -> float:
        """Calculates the difference in cents between two frequencies.

        :param frequency0: The first frequency in Hertz.
        :param frequency1: The second frequency in Hertz.
        :return: The difference in cents between the first and the second
            frequency.

        **Example:**

        >>> from mutwo.parameters import abc
        >>> abc.Pitch.hertz_to_cents(200, 400)
        1200.0
        """
        return float(1200 * math.log(frequency1 / frequency0, 2))

    @staticmethod
    def ratio_to_cents(ratio: fractions.Fraction) -> float:
        """Converts a frequency ratio to its respective cent value.

        :param ratio: The frequency ratio which cent value shall be
            calculated.

        **Example:**

        >>> from mutwo.parameters import abc
        >>> abc.Pitch.ratio_to_cents(fractions.Fraction(3, 2))
        701.9550008653874
        """
        return pitches_constants.CENT_CALCULATION_CONSTANT * math.log10(ratio)

    @staticmethod
    def cents_to_ratio(cents: constants.Real) -> fractions.Fraction:
        """Converts a cent value to its respective frequency ratio.

        :param cents: Cents that shall be converted to a frequency ratio.

        **Example:**

        >>> from mutwo.parameters import abc
        >>> abc.Pitch.cents_to_ratio(1200)
        Fraction(2, 1)
        """
        return fractions.Fraction(
            10 ** (cents / pitches_constants.CENT_CALCULATION_CONSTANT)
        )

    @staticmethod
    def hertz_to_midi_pitch_number(frequency: constants.Real) -> float:
        """Converts a frequency in hertz to its respective midi pitch.

        :param frequency: The frequency that shall be translated to a midi pitch
            number.
        :return: The midi pitch number (potentially a floating point number if the
            entered frequency isn't on the grid of the equal divided octave tuning
            with a = 440 Hertz).

        **Example:**

        >>> from mutwo.parameters import abc
        >>> abc.Pitch.hertz_to_midi_pitch_number(440)
        69.0
        >>> abc.Pitch.hertz_to_midi_pitch_number(440 * 3 / 2)
        75.98044999134612
        """
        closest_frequency_index = tools.find_closest_index(
            frequency, pitches_constants.MIDI_PITCH_FREQUENCIES
        )
        closest_frequency = pitches_constants.MIDI_PITCH_FREQUENCIES[
            closest_frequency_index
        ]
        closest_midi_pitch_number = pitches_constants.MIDI_PITCH_NUMBERS[
            closest_frequency_index
        ]
        difference_in_cents = Pitch.hertz_to_cents(frequency, closest_frequency)
        return float(closest_midi_pitch_number + (difference_in_cents / 100))

    # properties
    @property
    @abc.abstractmethod
    def frequency(self) -> float:
        """The frequency in Hertz of the pitch."""
        raise NotImplementedError

    @property
    def midi_pitch_number(self) -> float:
        """The midi pitch number (from 0 to 127) of the pitch."""
        return self.hertz_to_midi_pitch_number(self.frequency)

    # comparison methods
    def __lt__(self, other: "Pitch") -> bool:
        return self.frequency < other.frequency

    def __eq__(self, other: object) -> bool:
        try:
            return self.frequency == other.frequency  # type: ignore
        except AttributeError:
            return False


@functools.total_ordering  # type: ignore
class Volume(Parameter):
    """Abstract base class for any volume class.

    If the user wants to define a new volume class, the abstract
    property :attr:`` has to be overridden.
    """

    @staticmethod
    def decibel_to_amplitude_ratio(
        decibel: constants.Real, reference_amplitude: constants.Real = 1
    ) -> float:
        """Convert decibel to amplitude ratio.

        :param decibel: The decibel number that shall be converted.
        :param reference_amplitude: The amplitude for decibel == 0.

        **Example:**

        >>> from mutwo.parameters import abc
        >>> abc.Volume.decibel_to_amplitude_ratio(0)
        1
        >>> abc.Volume.decibel_to_amplitude_ratio(-6)
        0.5011872336272722
        >>> abc.Volume.decibel_to_amplitude_ratio(0, reference_amplitude=0.25)
        0.25
        """
        return float(reference_amplitude * (10 ** (decibel / 20)))

    @staticmethod
    def decibel_to_power_ratio(
        decibel: constants.Real, reference_amplitude: constants.Real = 1
    ) -> float:
        """Convert decibel to power ratio.

        :param decibel: The decibel number that shall be converted.
        :param reference_amplitude: The amplitude for decibel == 0.

        **Example:**

        >>> from mutwo.parameters import abc
        >>> abc.Volume.decibel_to_power_ratio(0)
        1
        >>> abc.Volume.decibel_to_power_ratio(-6)
        0.251188643150958
        >>> abc.Volume.decibel_to_power_ratio(0, reference_amplitude=0.25)
        0.25
        """
        return float(reference_amplitude * (10 ** (decibel / 10)))

    @staticmethod
    def amplitude_ratio_to_decibel(
        amplitude: constants.Real, reference_amplitude: constants.Real = 1
    ) -> float:
        """Convert amplitude ratio to decibel.

        :param amplitude: The amplitude that shall be converted.
        :param reference_amplitude: The amplitude for decibel == 0.

        **Example:**

        >>> from mutwo.parameters import abc
        >>> abc.Volume.amplitude_ratio_to_decibel(1)
        0
        >>> abc.Volume.amplitude_ratio_to_decibel(0)
        inf
        >>> abc.Volume.amplitude_ratio_to_decibel(0.5)
        -6.020599913279624
        """
        if amplitude == 0:
            return float("-inf")
        else:
            return float(20 * math.log10(amplitude / reference_amplitude))

    @staticmethod
    def power_ratio_to_decibel(
        amplitude: constants.Real, reference_amplitude: constants.Real = 1
    ) -> float:
        """Convert power ratio to decibel.

        :param amplitude: The amplitude that shall be converted.
        :param reference_amplitude: The amplitude for decibel == 0.

        **Example:**

        >>> from mutwo.parameters import abc
        >>> abc.Volume.power_ratio_to_decibel(1)
        0
        >>> abc.Volume.power_ratio_to_decibel(0)
        inf
        >>> abc.Volume.power_ratio_to_decibel(0.5)
        -3.010299956639812
        """
        if amplitude == 0:
            return float("-inf")
        else:
            return float(10 * math.log10(amplitude / reference_amplitude))

    @staticmethod
    def amplitude_ratio_to_midi_velocity(
        amplitude: constants.Real, reference_amplitude: constants.Real = 1
    ) -> int:
        """Convert amplitude ratio to midi velocity.

        :param amplitude: The amplitude which shall be converted.
        :type amplitude: constants.Real
        :param reference_amplitude: The amplitude for decibel == 0.
        :return: The midi velocity.

        The method clips values that are higher than 1 / lower than 0.

        **Example:**

        >>> from mutwo.parameters import abc
        >>> abc.Volume.amplitude_ratio_to_midi_velocity(1)
        127
        >>> abc.Volume.amplitude_ratio_to_midi_velocity(0)
        0
        """

        return Volume.decibel_to_midi_velocity(
            Volume.amplitude_ratio_to_decibel(
                amplitude, reference_amplitude=reference_amplitude
            )
        )

    @staticmethod
    def decibel_to_midi_velocity(
        decibel_to_convert: constants.Real,
        minimum_decibel: typing.Optional[constants.Real] = None,
        maximum_decibel: typing.Optional[constants.Real] = None,
    ) -> int:
        """Convert decibel to midi velocity (0 to 127).

        :param decibel: The decibel value which shall be converted..
        :type decibel: constants.Real
        :param minimum_decibel: The decibel value which is equal to the lowest
            midi velocity (0).
        :type minimum_decibel: constants.Real, optional
        :param maximum_decibel: The decibel value which is equal to the highest
            midi velocity (127).
        :type maximum_decibel: constants.Real, optional
        :return: The midi velocity.

        The method clips values which are higher than 'maximum_decibel' and lower than
        'minimum_decibel'.

        **Example:**

        >>> from mutwo.parameters import abc
        >>> abc.Volume.decibel_to_midi_velocity(0)
        127
        >>> abc.Volume.decibel_to_midi_velocity(-40)
        0
        """

        if minimum_decibel is None:
            minimum_decibel = (
                volumes_constants.DEFAULT_MINIMUM_DECIBEL_FOR_MIDI_VELOCITY_AND_STANDARD_DYNAMIC_INDICATOR
            )

        if maximum_decibel is None:
            maximum_decibel = (
                volumes_constants.DEFAULT_MAXIMUM_DECIBEL_FOR_MIDI_VELOCITY_AND_STANDARD_DYNAMIC_INDICATOR
            )

        if decibel_to_convert > maximum_decibel:
            decibel_to_convert = maximum_decibel

        if decibel_to_convert < minimum_decibel:
            decibel_to_convert = minimum_decibel

        velocity = int(
            tools.scale(
                decibel_to_convert,
                minimum_decibel,
                maximum_decibel,
                volumes_constants.MINIMUM_VELOCITY,
                volumes_constants.MAXIMUM_VELOCITY,
            )
        )

        return velocity

    # properties
    @property
    @abc.abstractmethod
    def amplitude(self) -> constants.Real:
        """The amplitude of the Volume (a number from 0 to 1)."""
        raise NotImplementedError

    @property
    def decibel(self) -> constants.Real:
        """The decibel of the volume (from -120 to 0)"""
        return self.amplitude_ratio_to_decibel(self.amplitude)

    @property
    def midi_velocity(self) -> int:
        """The velocity of the volume (from 0 to 127)."""
        return self.decibel_to_midi_velocity(self.decibel)

    # comparison methods
    def __lt__(self, other: "Volume") -> bool:
        return self.amplitude < other.amplitude

    def __eq__(self, other: object) -> bool:
        try:
            return self.amplitude == other.amplitude  # type: ignore
        except AttributeError:
            return False


@dataclasses.dataclass()  # type: ignore
class Indicator(Parameter):
    @property
    @abc.abstractmethod
    def is_active(self) -> bool:
        raise NotImplementedError()

    def get_arguments_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            key: getattr(self, key) for key in self.__dataclass_fields__.keys()  # type: ignore
        }


class PlayingIndicator(Indicator):
    pass


class ExplicitPlayingIndicator(PlayingIndicator):
    def __init__(self, is_active: bool = False):
        self.is_active = is_active

    def __repr__(self):
        return "{}({})".format(type(self).__name__, self.is_active)

    def get_arguments_dict(self) -> typing.Dict[str, typing.Any]:
        return {"is_active": self.is_active}

    @property
    def is_active(self) -> bool:
        return self._is_active

    @is_active.setter
    def is_active(self, is_active: bool):
        self._is_active = is_active


@dataclasses.dataclass()
class ImplicitPlayingIndicator(PlayingIndicator):
    @property
    def is_active(self) -> bool:
        return all(
            tuple(
                argument is not None for argument in self.get_arguments_dict().values()
            )
        )


class NotationIndicator(Indicator):
    @property
    def is_active(self) -> bool:
        return all(
            tuple(
                argument is not None for argument in self.get_arguments_dict().values()
            )
        )


T = typing.TypeVar("T", PlayingIndicator, NotationIndicator)


@dataclasses.dataclass(frozen=True)
class IndicatorCollection(typing.Generic[T]):
    def get_all_indicator(self) -> typing.Tuple[T, ...]:
        return tuple(
            getattr(self, key)
            for key in self.__dataclass_fields__.keys()  # type: ignore
        )

    def get_indicator_dict(self) -> typing.Dict[str, Indicator]:
        return {key: getattr(self, key) for key in self.__dataclass_fields__.keys()}  # type: ignore
