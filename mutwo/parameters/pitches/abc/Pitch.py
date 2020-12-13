import abc
import functools
import math

try:
    import quicktions as fractions
except ImportError:
    import fractions

from mutwo import parameters
from mutwo.utilities import tools


@functools.total_ordering
class Pitch(parameters.abc.Parameter):
    """Abstract blueprint for any pitch class."""

    # constant used for cent calculation
    _cent_calculation_constant = 1200 / (math.log10(2))

    # conversion methods between different pitch describing units
    @staticmethod
    def hertz_to_cents(frequency0: float, frequency1: float) -> float:
        """Calculates the difference in cents between to frequencies."""
        return 1200 * math.log(frequency1 / frequency0, 2)

    @staticmethod
    def ratio_to_cents(ratio: fractions.Fraction) -> float:
        """Converts a frequency ratio to its respective cent value."""
        return Pitch._cent_calculation_constant * math.log10(ratio)

    @staticmethod
    def cents_to_ratio(cents: float) -> fractions.Fraction:
        """Converts a cent value to its respective frequency ratio."""
        return fractions.Fraction(10 ** (cents / Pitch._cent_calculation_constant))

    @staticmethod
    def hertz_to_midi_pitch_number(frequency: float) -> float:
        closest_frequency_index = tools.find_closest_index(
            frequency, parameters.pitches.constants.MidiPitchFrequencies
        )
        closest_frequency = parameters.pitches.constants.MidiPitchFrequencies[
            closest_frequency_index
        ]
        closest_midi_pitch_number = parameters.pitches.constants.MidiPitchNumbers[
            closest_frequency_index
        ]
        difference_in_cents = Pitch.hertz_to_cents(frequency, closest_frequency)
        return closest_midi_pitch_number + (difference_in_cents / 100)

    # properties
    @property
    @abc.abstractmethod
    def frequency(self) -> float:
        raise NotImplementedError

    @property
    def midi_pitch_number(self) -> float:
        return self.hertz_to_midi_pitch_number(self.frequency)

    # comparison methods
    def __lt__(self, other: "Pitch") -> bool:
        return self.frequency < other.frequency

    def __eq__(self, other: "Pitch") -> bool:
        try:
            return self.frequency == other.frequency
        except AttributeError:
            return False
