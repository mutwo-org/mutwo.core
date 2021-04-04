"""Abstract base classes for different parameters."""

import abc
import functools
import math
import typing

try:
    import quicktions as fractions
except ImportError:
    import fractions

from mutwo.parameters import pitches_constants
from mutwo.parameters import volumes_constants
from mutwo.utilities import constants
from mutwo.utilities import tools

__all__ = ("Pitch", "Volume")


class Parameter(abc.ABC):
    """Abstract base class for any parameter class."""

    pass


class Duration(Parameter):
    """Abstract base class for any duration class."""

    pass


DurationType = typing.Union[constants.Real, Duration]


@functools.total_ordering
class Pitch(Parameter):
    """Abstract base class for any pitch class.

    If the user wants to define a new pitch class, the abstract
    property :attr:`frequency` has to be overridden.
    """

    # conversion methods between different pitch describing units
    @staticmethod
    def hertz_to_cents(frequency0: float, frequency1: float) -> float:
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
        return 1200 * math.log(frequency1 / frequency0, 2)

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
    def cents_to_ratio(cents: float) -> fractions.Fraction:
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
    def hertz_to_midi_pitch_number(frequency: float) -> float:
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
        return closest_midi_pitch_number + (difference_in_cents / 100)

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

    def __eq__(self, other: "Pitch") -> bool:
        try:
            return self.frequency == other.frequency
        except AttributeError:
            return False


@functools.total_ordering
class Volume(Parameter):
    """Abstract base class for any volume class.

    If the user wants to define a new volume class, the abstract
    property :attr:`volume` has to be overridden.
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
            return float("inf")
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
            return float("inf")
        else:
            return float(10 * math.log10(amplitude / reference_amplitude))

    @staticmethod
    def amplitude_to_midi_velocity(amplitude: constants.Real) -> int:
        """Convert volume (floating point number from 0 to 1) to midi velocity.

        :param amplitude: A value from 0 to 1 that shall be converted to midi
            velocity (0 to 127).
        :return: The midi velocity.

        The method clips values that are higher than 1 / lower than 0.

        **Example:**

        >>> from mutwo.parameters import abc
        >>> abc.Volume.amplitude_to_midi_velocity(1)
        127
        >>> abc.Volume.amplitude_to_midi_velocity(0)
        0
        """
        velocity = int(round(amplitude * volumes_constants.MAXIMUM_VELOCITY))

        # clip velocity
        if velocity < volumes_constants.MINIMUM_VELOCITY:
            velocity = volumes_constants.MINIMUM_VELOCITY
        if velocity > volumes_constants.MAXIMUM_VELOCITY:
            velocity = volumes_constants.MAXIMUM_VELOCITY

        return velocity

    # properties
    @property
    @abc.abstractmethod
    def amplitude(self) -> float:
        """The amplitude of the Volume (a number from 0 to 1)."""
        raise NotImplementedError

    @property
    def decibel(self) -> float:
        """The decibel of the volume (from -120 to 0)"""
        return self.amplitude_ratio_to_decibel(self.amplitude)

    @property
    def midi_velocity(self) -> int:
        """The velocity of the volume (from 0 to 1)."""
        return self.amplitude_to_midi_velocity(self.amplitude)

    # comparison methods
    def __lt__(self, other: "Volume") -> bool:
        return self.amplitude < other.amplitude

    def __eq__(self, other: "Volume") -> bool:
        try:
            return self.amplitude == other.amplitude
        except AttributeError:
            return False
