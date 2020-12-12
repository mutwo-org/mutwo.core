import abc
import bisect
import functools
import math
import operator
import warnings

try:
    import quicktions as fractions
except ImportError:
    import fractions

from mutwo import parameters


@functools.total_ordering
class Pitch(parameters.abc.Parameter):
    """Abstract blueprint for any pitch class."""

    # constant used for cent calculation
    _cent_calculation_constant = 1200 / (math.log10(2))

    # constants used to generate sysex tuning messages
    # with the help of the 'get_midi_tuning' method.
    _midi_tuning_table0 = tuple(i * 0.78125 for i in range(128))
    _midi_tuning_table1 = tuple(i * 0.0061 for i in range(128))

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

    # properties
    @property
    @abc.abstractmethod
    def frequency(self) -> float:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def midi(self) -> float:
        raise NotImplementedError

    # comparison methods
    def __lt__(self, other: "Pitch") -> bool:
        return self.frequency < other.frequency

    def __eq__(self, other: "Pitch") -> bool:
        try:
            return self.frequency == other.frequency
        except AttributeError:
            return False

    # standard methods
    def get_midi_tuning(self) -> tuple:
        """calculates the MIDI Tuning Standard of the pitch (sysex message).

        (http://www.microtonal-synthesis.com/MIDItuning.html)
        """

        # TODO(make this method comprehensible)

        def find_lower_and_higher(table, element):
            closest = bisect.bisect_right(table, element)
            if closest < len(table):
                indices = (closest - 1, closest)
                differences = tuple(abs(element - table[idx]) for idx in indices)
            else:
                idx = closest - 1
                difference = abs(table[idx] - element)
                indices, differences = (idx, idx), (difference, difference)
            return tuple(zip(indices, differences))

        def detect_steps(difference):
            closest_s0 = find_lower_and_higher(Pitch._midi_tuning_table0, difference)
            closest_s1 = find_lower_and_higher(
                Pitch._midi_tuning_table1, closest_s0[0][1]
            )
            closest_s1 = min(closest_s1, key=operator.itemgetter(1))
            difference0 = closest_s1[1]
            difference1 = closest_s0[1][1]
            if difference0 <= difference1:
                return closest_s0[0][0], closest_s1[0], difference0
            else:
                return closest_s0[1][0], 0, difference1

        frequency = self.frequency
        if frequency:
            closest = (
                bisect.bisect_right(
                    parameters.pitches.constants.MidiPitchFrequencies, frequency
                )
                - 1
            )
            diff = self.hertz_to_cents(
                parameters.pitches.constants.MidiPitchFrequencies[closest], frequency
            )
            steps0, steps1, diff = detect_steps(diff)
            if diff >= 5:
                msg = "Closest midi-pitch of {0} ({1} Hz) ".format(self, frequency)
                msg += "is still {} cents apart!".format(diff)
                warnings.warn(msg)
            return closest, steps0, steps1
        else:
            return tuple([])
