"""Convert mutwo or generic Python objects to other mutwo or generic Python objects."""

import functools
import math
import operator
import typing
import warnings

import expenvelope  # type: ignore

import mutwo_third_party

from mutwo import converters
from mutwo import events
from mutwo import parameters
from mutwo.utilities import constants
from mutwo.utilities import prime_factors

TempoPoint = typing.Union[parameters.tempos.TempoPoint, constants.Real]


__all__ = (
    "TempoConverter",
    "TempoPointConverter",
    "LoudnessToAmplitudeConverter",
    "RhythmicalStrataToIndispensabilityConverter",
)


class TempoPointConverter(converters.abc.Converter):
    """Convert a :class:`TempoPoint` with BPM to beat-length-in-seconds.

    A :class:`TempoPoint` is defined as an object that has a particular tempo in
    beats per seconds (BPM) and a reference value (1 for a quarter note, 4
    for a whole note, etc.). Besides elaborate :class:`mutwo.parameters.tempos.TempoPoint`
    objects, any number can also be interpreted as a `TempoPoint`. In this case
    the number simply represents the BPM number and the reference will be set to 1.
    The returned beat-length-in-seconds always indicates the length for one quarter
    note.

    **Example:**

    >>> from mutwo.converters import symmetrical
    >>> tempo_point_converter = symmetrical.TempoPointConverter()
    """

    @staticmethod
    def _beats_per_minute_to_seconds_per_beat(
        beats_per_minute: constants.Real,
    ) -> float:
        return float(60 / beats_per_minute)

    @staticmethod
    def _extract_beats_per_minute_and_reference_from_tempo_point(
        tempo_point: TempoPoint,
    ) -> typing.Tuple[constants.Real, constants.Real]:
        try:
            beats_per_minute = tempo_point.tempo_in_beats_per_minute  # type: ignore
        except AttributeError:
            beats_per_minute = float(tempo_point)  # type: ignore

        try:
            reference = tempo_point.reference  # type: ignore
        except AttributeError:
            message = (
                "Tempo point {} of type {} doesn't know attribute 'reference'.".format(
                    tempo_point, type(tempo_point)
                )
            )
            message += " Therefore reference has been set to 1."
            warnings.warn(message)
            reference = 1

        return beats_per_minute, reference

    def convert(self, tempo_point_to_convert: TempoPoint) -> float:
        """Converts a :class:`TempoPoint` to beat-length-in-seconds.

        :param tempo_point_to_convert: A tempo point defines the active tempo
            from which the beat-length-in-seconds shall be calculated. The argument
            can either be any number (which will be interpreted as beats per
            minute [BPM]) or a ``mutwo.parameters.tempos.TempoPoint`` object.
        :return: The duration of one beat in seconds within the passed tempo.

        **Example:**

        >>> from mutwo.converters import symmetrical
        >>> converter = symmetrical.TempoPointConverter()
        >>> converter.convert(60)  # one beat in tempo 60 bpm takes 1 second
        1
        >>> converter.convert(120)  # one beat in tempo 120 bpm takes 0.5 second
        0.5
        """

        (
            beats_per_minute,
            reference,
        ) = self._extract_beats_per_minute_and_reference_from_tempo_point(
            tempo_point_to_convert
        )
        return (
            TempoPointConverter._beats_per_minute_to_seconds_per_beat(beats_per_minute)
            / reference
        )


TempoEvents = expenvelope.Envelope


class TempoConverter(converters.abc.EventConverter):
    """Class for applying tempo curves on mutwo events.

    :param tempo_envelope: The tempo curve that shall be applied on the
        mutwo events. This is expected to be a :class:`expenvelope.Envelope`
        which levels arefilled with numbers that will be interpreted as BPM
        [beats per minute]) or with :class:`mutwo.parameters.tempos.TempoPoint`
        objects.

    **Example:**

    >>> import expenvelope
    >>> from mutwo.converters import symmetrical
    >>> from mutwo.parameters import tempos
    >>> tempo_envelope = expenvelope.Envelope.from_levels_and_durations(
    >>>     levels=[tempos.TempoPoint(60), 60, 30, 50],
    >>>     durations=[3, 0, 2],
    >>> )
    >>> my_tempo_converter = symmetrical.TempoConverter(tempo_events)
    """

    _tempo_point_converter = TempoPointConverter()

    def __init__(self, tempo_envelope: expenvelope.Envelope):
        self._envelope = TempoConverter._tempo_envelope_to_beat_length_in_seconds_envelope(
            tempo_envelope
        )

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _tempo_envelope_to_beat_length_in_seconds_envelope(
        tempo_envelope: expenvelope.Envelope,
    ) -> expenvelope.Envelope:
        """Convert bpm / TempoPoint based env to beat-length-in-seconds env."""

        levels: typing.List[float] = []
        for tempo_point in tempo_envelope.levels:
            beat_length_in_seconds = TempoConverter._tempo_point_converter.convert(
                tempo_point
            )
            levels.append(beat_length_in_seconds)

        print(levels, tempo_envelope.durations, tempo_envelope.curve_shapes)

        return expenvelope.Envelope.from_levels_and_durations(
            levels, tempo_envelope.durations, tempo_envelope.curve_shapes
        )

    # ###################################################################### #
    #                         private methods                                #
    # ###################################################################### #

    def _convert_simple_event(
        self,
        simple_event: events.basic.SimpleEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> typing.Tuple[typing.Any, ...]:
        simple_event.duration = self._envelope.integrate_interval(
            absolute_entry_delay, simple_event.duration + absolute_entry_delay
        )
        return tuple([])

    # ###################################################################### #
    #               public methods for interaction with the user             #
    # ###################################################################### #

    def convert(self, event_to_convert: events.abc.Event) -> events.abc.Event:
        """Apply tempo curve of the converter to the entered event.

        The method doesn't change the original event, but returns a copied
        version with different values for its duration attributes depending
        on the tempo curve.

        :param event_to_convert: The event to convert. Can be any object
            that inherits from ``mutwo.events.abc.Event``. If the event that
            shall be converted is longer than the tempo curve of the
            ``TempoConverter``, then the last tempo of the curve will be hold.
        :return: A new ``Event`` object which duration property has been adapted
            by the tempo curve of the ``TempoConverter``.

        **Example:**

        >>> from mutwo.events import basic
        >>> from mutwo.parameters import tempos
        >>> from mutwo.converters import symmetrical
        >>> tempo_events = basic.SequentialEvent(
        >>>     [basic.EnvelopeEvent(3, tempos.TempoPoint(60)),  # start with bpm = 60
        >>>      basic.EnvelopeEvent(2, 60, 120),                # acc. from 60 to 120
        >>>      basic.EnvelopeEvent(5, 120)]                    # stay on bpm = 120
        >>> )
        >>> my_tempo_converter = symmetrical.TempoConverter(tempo_events)
        >>> my_events = basic.SequentialEvent([basic.SimpleEvent(d) for d in (3, 2, 5)])
        >>> my_tempo_converter.convert(my_events)
        SequentialEvent([SimpleEvent(duration = 3.0), SimpleEvent(duration = 1.5), SimpleEvent(duration = 2.5)])
        """
        copied_event_to_convert = event_to_convert.destructive_copy()
        self._convert_event(copied_event_to_convert, 0)
        return copied_event_to_convert


class LoudnessToAmplitudeConverter(converters.abc.Converter):
    """Make an approximation of the needed amplitude for a perceived Loudness.

    :param perceived_loudness_in_sone: The subjectively perceived loudness that
        the resulting signal shall have (in the unit `Sone`).
    :param loudspeaker_frequency_response: Optionally the frequency response
        of the used loudspeaker can be added for balancing out uneven curves in
        the loudspeakers frequency response. The frequency response is defined
        with an ``expenvelope.Envelope`` object.
    :param interpolation_order: The interpolation order of the equal loudness
        contour interpolation.

    The converter works best with pure sine waves.
    """

    # roughly the sound of a mosquito flying 3 m away
    # (see https://en.wikipedia.org/wiki/Sound_pressure)
    _auditory_threshold_at_1khz = 0.00002

    def __init__(
        self,
        perceived_loudness_in_sone: constants.Real,
        loudspeaker_frequency_response: expenvelope.Envelope = expenvelope.Envelope.from_points(
            (0, 80), (2000, 80)
        ),
        interpolation_order: int = 4,
    ):
        perceived_loudness_in_phon = self._sone_to_phon(perceived_loudness_in_sone)
        self._equal_loudness_contour_interpolation = mutwo_third_party.pydsm.pydsm.iso226.iso226_spl_itpl(  # type: ignore
            perceived_loudness_in_phon, interpolation_order
        )
        self._loudspeaker_frequency_response = loudspeaker_frequency_response
        self._loudspeaker_frequency_response_average = (
            loudspeaker_frequency_response.average_level()
        )

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _decibel_to_amplitude_ratio(
        decibel: constants.Real, reference_amplitude: constants.Real = 1
    ) -> float:
        return float(reference_amplitude * (10 ** (decibel / 20)))

    @staticmethod
    def _decibel_to_power_ratio(decibel: constants.Real) -> float:
        return float(10 ** (decibel / 10))

    @staticmethod
    def _sone_to_phon(loudness_in_sone: constants.Real) -> constants.Real:
        # formula from http://www.sengpielaudio.com/calculatorSonephon.htm
        if loudness_in_sone >= 1:
            return 40 + (10 * math.log(loudness_in_sone, 2))
        else:
            return 40 * (loudness_in_sone + 0.0005) ** 0.35

    # ###################################################################### #
    #               public methods for interaction with the user             #
    # ###################################################################### #

    def convert(self, frequency: constants.Real) -> constants.Real:
        """Calculates the needed amplitude to reach a particular loudness for the entered frequency.

        :param frequency: A frequency in Hertz for which the necessary amplitude
            shall be calculated.
        :return: Return the amplitude for a sine tone to reach the converters
            loudness when played with the entered frequency.

        **Example:**

        >>> from mutwo.converters import symmetrical
        >>> loudness_converter = symmetrical.LoudnessToAmplitudeConverter(1)
        >>> loudness_converter.convert(200)
        0.009364120303317933
        >>> loudness_converter.convert(50)
        0.15497924558613232
        """

        # (1) calculates necessary sound pressure level depending on the frequency
        #     and loudness (to get the same loudness over all frequencies)
        sound_pressure_level_for_perceived_loudness_based_on_frequency = float(
            self._equal_loudness_contour_interpolation(frequency)
        )
        # (2) figure out the produced soundpressure of the loudspeaker depending
        #     on the frequency (for balancing uneven frequency responses of
        #     loudspeakers)
        produced_soundpressure_for_1_watt_1_meter_depending_on_loudspeaker = self._loudspeaker_frequency_response.value_at(
            frequency
        )
        difference_to_average = (
            self._loudspeaker_frequency_response_average
            - produced_soundpressure_for_1_watt_1_meter_depending_on_loudspeaker
        )
        sound_pressure_level_for_pereived_loudness_based_on_speaker = (
            sound_pressure_level_for_perceived_loudness_based_on_frequency
            + difference_to_average
        )
        amplitude_ratio = self._decibel_to_amplitude_ratio(
            sound_pressure_level_for_pereived_loudness_based_on_speaker,
            self._auditory_threshold_at_1khz,
        )
        return amplitude_ratio


class RhythmicalStrataToIndispensabilityConverter(converters.abc.Converter):
    """Builds metrical indispensability for a rhythmical strata.

    This technique has been described by Clarence Barlow in `On the Quantification
    of Harmony and Metre` (1992). The technique aims to model the weight
    of single beats in a particular metre. It allocates each beat of a metre
    to a specific value that describes the `indispensability` of a beat: the higher the
    assigned value, the more accented the beat.
    """

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _indispensability_of_nth_beat_for_simple_meter(
        beat_index: int, prime_number: int
    ) -> int:
        """Calculate indispensability for nth beat of a metre that is composed of a singular prime number."""

        if prime_number == 2:
            return prime_number - beat_index
        elif beat_index == prime_number - 1:
            return int(prime_number / 4)
        else:
            factorised = tuple(
                sorted(prime_factors.factorise(prime_number - 1), reverse=True)
            )
            q = RhythmicalStrataToIndispensabilityConverter._indispensability_of_nth_beat(
                beat_index - int(beat_index / prime_number), factorised
            )
            return int(q + (2 * math.sqrt((q + 1) / prime_number)))

    @staticmethod
    def _indispensability_of_nth_beat(
        beat_index: int, rhythmical_strata: typing.Tuple[int, ...]
    ) -> int:
        """Calculate indispensability for the nth beat of a metre.

        The metre is defined with the primes argument.
        """

        z = len(rhythmical_strata)
        rhythmical_strata = (1,) + rhythmical_strata + (1,)
        r_sum = []
        for r in range(0, z):
            up = (beat_index - 2) % functools.reduce(
                operator.mul, tuple(rhythmical_strata[j] for j in range(1, z + 1))
            )
            down = functools.reduce(
                operator.mul, tuple(rhythmical_strata[z + 1 - k] for k in range(r + 1))
            )
            local_result = 1 + (int(1 + (up / down)) % rhythmical_strata[z - r])
            base_indispensability = RhythmicalStrataToIndispensabilityConverter._indispensability_of_nth_beat_for_simple_meter(
                local_result, rhythmical_strata[z - r]
            )
            product = functools.reduce(
                operator.mul, tuple(rhythmical_strata[i] for i in range(0, z - r))
            )
            r_sum.append(product * base_indispensability)
        return sum(r_sum)

    # ###################################################################### #
    #               public methods for interaction with the user             #
    # ###################################################################### #

    def convert(
        self, rhythmical_strata_to_convert: typing.Sequence[int]
    ) -> typing.Tuple[int, ...]:
        """Convert indispensability for each beat of a particular metre.

        :param rhythmical_strata_to_convert: The rhythmical strata defines
            the metre for which the indispensability shall be calculated. The
            rhythmical strata is a list of prime numbers which product is the
            amount of available beats within the particular metre. Earlier
            prime numbers in the rhythmical strata are considered to be more
            important than later prime numbers.
        :return: A tuple of a integer for each beat of the respective metre where
            each integer describes how accented the particular beat is (the higher the
            number, the more important the beat).

        **Example:**

        >>> from mutwo.converters import symmetrical
        >>> metricity_converter = symmetrical.RhythmicalStrataToIndispensabilityConverter()
        >>> metricity_converter.convert((2, 3))  # time signature 3/4
        (5, 0, 3, 1, 4, 2)
        >>> metricity_converter.convert((3, 2))  # time signature 6/8
        (5, 0, 2, 4, 1, 3)
        """

        # inverse so that the first numbers are more important than the later numbers
        rhythmical_strata_to_convert = tuple(reversed(rhythmical_strata_to_convert))

        length = functools.reduce(operator.mul, rhythmical_strata_to_convert)
        return tuple(
            RhythmicalStrataToIndispensabilityConverter._indispensability_of_nth_beat(
                i + 1, rhythmical_strata_to_convert
            )
            for i in range(length)
        )
