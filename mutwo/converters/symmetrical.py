"""Module for routines that convert mutwo objects to other mutwo objects."""

import math
import numbers
import typing
import warnings

import expenvelope

import mutwo_third_party

from mutwo import converters
from mutwo import events
from mutwo import parameters

TempoPoint = typing.Union[parameters.tempos.TempoPoint, numbers.Number]


__all__ = ("TempoConverter", "TempoPointConverter", "LoudnessToAmplitudeConverter")


class TempoPointConverter(converters.abc.Converter):
    """Simple class to convert a TempoPoint to beat-length-in-seconds.

    A TempoPoint is defined as an object that has a particular tempo in
    beats per seconds (BPM) and a reference value (1 for a quarter note, 4
    for a whole note, etc.). Besides elaborate mutwo.parameters.tempo.TempoPoint
    objects, any number can also be interpreted as a TempoPoint. In this case
    the number simply represents the BPM number and the reference will be set to 1.
    The returned beat-length-in-seconds always indicates the length for one quarter
    note.
    """

    @staticmethod
    def beats_per_minute_to_seconds_per_beat(beats_per_minute: numbers.Number) -> float:
        return 60 / beats_per_minute

    @staticmethod
    def extract_beats_per_minute_and_reference_from_tempo_point(
        tempo_point: TempoPoint,
    ) -> typing.Tuple[numbers.Number]:
        try:
            beats_per_minute = tempo_point.tempo_in_beats_per_minute
        except AttributeError:
            beats_per_minute = float(tempo_point)

        try:
            reference = tempo_point.reference
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
        """Converts a TempoPoint to beat-length-in-seconds."""

        (
            beats_per_minute,
            reference,
        ) = self.extract_beats_per_minute_and_reference_from_tempo_point(
            tempo_point_to_convert
        )
        return (
            TempoPointConverter.beats_per_minute_to_seconds_per_beat(beats_per_minute)
            / reference
        )


TempoEvents = events.basic.SequentialEvent[events.basic.EnvelopeEvent]


class TempoConverter(converters.abc.Converter):
    """Class for applying tempo curves on mutwo events.

    :param tempo_events: The tempo curve that shall be applied on the
        mutwo events. This is expected to be a SequentialEvent that is filled
        with EnvelopeEvent objects. Each EnvelopeEvent can either be initialised
        via numbers for start and end attributes (the numbers will be interpreted
        as BPM [beats per minute]) or via mutwo.parameters.tempo.TempoPoint objects.

    Example:
        >>> from mutwo.converters import symmetrical
        >>> from mutwo.events import basic
        >>> from mutwo.parameters import tempos
        >>> tempo_events = basic.SequentialEvent(
        >>>     [basic.EnvelopeEvent(3, tempos.TempoPoint(60)),  # start with bpm = 60
        >>>      basic.EnvelopeEvent(2, 30, 50),                 # acc. from 30 to 50
        >>>      basic.EnvelopeEvent(5, 50)]                     # stay on bpm = 50
        >>> )
        >>> my_tempo_converter = symmetrical.TempoConverter(tempo_events)
    """

    _tempo_point_converter = TempoPointConverter()

    def __init__(self, tempo_events: TempoEvents):
        self.tempo_events = tempo_events

    @staticmethod
    def _find_beat_length_at_start_and_end(
        tempo_event: events.basic.EnvelopeEvent,
    ) -> typing.Tuple[float]:
        """Extracts the beat-length-in-seconds at start and end of a TempoEvent."""
        beat_length_at_start_and_end = []
        for tempo_point in (tempo_event.object_start, tempo_event.object_stop):
            beat_length_at_start_and_end.append(
                TempoConverter._tempo_point_converter.convert(tempo_point)
            )

        return beat_length_at_start_and_end

    @staticmethod
    def make_envelope_from_tempo_events(
        tempo_events: TempoEvents,
    ) -> expenvelope.Envelope:
        """Convert a list of TempoEvents to an Envelope."""

        levels = []
        durations = []
        curve_shapes = []
        is_first = True
        for tempo_event in tempo_events:
            if is_first:
                is_first = False
            else:
                durations.append(1e-100)
                curve_shapes.append(0)

            beat_length_at_start_and_end = TempoConverter._find_beat_length_at_start_and_end(
                tempo_event
            )
            levels.extend(beat_length_at_start_and_end)
            durations.append(tempo_event.duration - 1e-100)
            curve_shapes.append(tempo_event.curve_shape)

        return expenvelope.Envelope.from_levels_and_durations(
            levels, durations, curve_shapes
        )

    @property
    def tempo_events(self) -> events.basic.SequentialEvent:
        return self._tempo_events

    @tempo_events.setter
    def tempo_events(self, tempo_events: TempoEvents):
        self._tempo_events = events.basic.SequentialEvent(tempo_events)
        self._envelope = self.make_envelope_from_tempo_events(self.tempo_events)

    @property
    def envelope(self) -> expenvelope.Envelope:
        return self._envelope

    def _apply_tempo_envelope_on_event(
        self,
        event_to_process: events.abc.Event,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> None:
        """Applies tempo envelope on any object that inherits from events.abc.Event.

        Make type checks to differentiate between different timing structures
        of SequentialEvent, SimultaneousEvent and SimpleEvent.
        """
        if isinstance(event_to_process, events.basic.SequentialEvent):
            self._apply_tempo_envelope_on_sequential_event(
                event_to_process, absolute_entry_delay
            )

        elif isinstance(event_to_process, events.basic.SimultaneousEvent,):
            self._apply_tempo_envelope_on_simultaneous_event(
                event_to_process, absolute_entry_delay
            )

        elif isinstance(event_to_process, events.basic.SimpleEvent,):
            self._apply_tempo_envelope_on_simple_event(
                event_to_process, absolute_entry_delay
            )

        else:
            msg = "Can't apply tempo curve on object '{}' of type '{}'.".format(
                event_to_process, type(event_to_process)
            )
            raise TypeError(msg)

    def _apply_tempo_envelope_on_sequential_event(
        self,
        sequential_event: events.basic.SequentialEvent[events.abc.Event],
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> None:
        for event_index, additional_delay in enumerate(sequential_event.absolute_times):
            self._apply_tempo_envelope_on_event(
                sequential_event[event_index], absolute_entry_delay + additional_delay
            )

    def _apply_tempo_envelope_on_simple_event(
        self,
        simple_event: events.basic.SimpleEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> None:
        simple_event.duration = self.envelope.integrate_interval(
            absolute_entry_delay, simple_event.duration + absolute_entry_delay
        )

    def _apply_tempo_envelope_on_simultaneous_event(
        self,
        simultaneous_event: events.basic.SimultaneousEvent[events.abc.Event],
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> None:
        [
            self._apply_tempo_envelope_on_event(event, absolute_entry_delay)
            for event in simultaneous_event
        ]

    def convert(self, event_to_convert: events.abc.Event) -> events.abc.Event:
        """Apply tempo curve of the converter to the entered event.

        The method doesn't change the original event, but returns a copied
        version with different values for its duration attributes depending
        on the tempo curve.

        :param event_to_convert: The event to convert. Can be any object
            that inherits from mutwo.events.abc.Event. If the event to convert
            is longer than tempo curve of the TempoConverter, the last tempo
            of the curve will be hold.
        """
        copied_event_to_convert = event_to_convert.destructive_copy()
        self._apply_tempo_envelope_on_event(copied_event_to_convert, 0)
        return copied_event_to_convert


class LoudnessToAmplitudeConverter(converters.abc.Converter):
    """Make an approximation of the needed amplitude for a perceived Loudness.

    The converter works best with pure sine waves.
    The formula takes into account the frequency of the output signal and the
    frequency response of the loudspeaker. The frequency response is defined
    with an expenvelope.Envelope object.
    """

    # roughly the sound of a mosquito flying 3 m away
    # (see https://en.wikipedia.org/wiki/Sound_pressure)
    _auditory_threshold_at_1khz = 0.00002

    def __init__(
        self,
        perceived_loudness_in_sone: numbers.Number,
        loudspeaker_frequency_response: expenvelope.Envelope = expenvelope.Envelope.from_points(
            (0, 80), (2000, 80)
        ),
        interpolation_order: int = 4,
    ):
        perceived_loudness_in_phon = self.sone_to_phon(perceived_loudness_in_sone)
        self._equal_loudness_contour_interpolation = mutwo_third_party.pydsm.pydsm.iso226.iso226_spl_itpl(
            perceived_loudness_in_phon, interpolation_order
        )
        self._loudspeaker_frequency_response = loudspeaker_frequency_response
        self._loudspeaker_frequency_response_maxima = (
            loudspeaker_frequency_response.max_level()
        )

    @staticmethod
    def decibel_to_amplitude_ratio(
        decibel: numbers.Number, reference_amplitude: numbers.Number = 1
    ) -> float:
        return float(reference_amplitude * (10 ** (decibel / 20)))

    @staticmethod
    def decibel_to_power_ratio(decibel: numbers.Number) -> float:
        return float(10 ** (decibel / 10))

    @staticmethod
    def sone_to_phon(loudness_in_sone: numbers.Number) -> numbers.Number:
        # formula from http://www.sengpielaudio.com/calculatorSonephon.htm
        if loudness_in_sone >= 1:
            return 40 + (10 * math.log(loudness_in_sone, 2))
        else:
            return 40 * (loudness_in_sone + 0.0005) ** 0.35

    def convert(self, frequency: numbers.Number) -> numbers.Number:
        # (1) calculates necessary sound pressure level depending on the frequency
        #     and loudness (to get the same loudness over all frequencies)
        sound_pressure_level_for_perceived_loudness_based_on_frequency = float(
            self._equal_loudness_contour_interpolation(frequency)
        )
        # (2) figure out the produced soundpressure of the loudspeaker depending
        #     on the frequency
        produced_soundpressure_for_1_watt_1_meter_depending_on_loudspeaker = self._loudspeaker_frequency_response.value_at(
            frequency
        )
        difference_to_maxima = (
            self._loudspeaker_frequency_response_maxima
            - produced_soundpressure_for_1_watt_1_meter_depending_on_loudspeaker
        )
        sound_pressure_level_for_pereived_loudness_based_on_speaker = (
            sound_pressure_level_for_perceived_loudness_based_on_frequency
            + difference_to_maxima
        )
        amplitude_ratio = self.decibel_to_amplitude_ratio(
            sound_pressure_level_for_pereived_loudness_based_on_speaker,
            self._auditory_threshold_at_1khz,
        )
        return amplitude_ratio
