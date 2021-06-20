"""Apply tempo curve on any :class:`~mutwo.events.abc.Event` and convert :class:`~mutwo.parameters.tempos.TempoPoint` to beat-length-in-seconds.

"""

import typing
import warnings

import expenvelope  # type: ignore

from mutwo import converters, events, parameters
from mutwo.utilities import constants


TempoEvents = expenvelope.Envelope
TempoPoint = typing.Union[parameters.tempos.TempoPoint, constants.Real]


__all__ = ("TempoPointConverter", "TempoConverter",)


class TempoPointConverter(converters.abc.Converter):
    """Convert a :class:`~mutwo.parameters.tempos.TempoPoint` with BPM to beat-length-in-seconds.

    A :class:`TempoPoint` is defined as an object that has a particular tempo in
    beats per seconds (BPM) and a reference value (1 for a quarter note, 4
    for a whole note, etc.). Besides elaborate :class:`mutwo.parameters.tempos.TempoPoint`
    objects, any number can also be interpreted as a `TempoPoint`. In this case
    the number simply represents the BPM number and the reference will be set to 1.
    The returned beat-length-in-seconds always indicates the length for one quarter
    note.

    **Example:**

    >>> from mutwo.converters import symmetrical
    >>> tempo_point_converter = symmetrical.tempos.TempoPointConverter()
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
        >>> converter = symmetrical.tempos.TempoPointConverter()
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
    >>> my_tempo_converter = symmetrical.tempos.TempoConverter(tempo_envelope)
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

        >>> import expenvelope
        >>> from mutwo.events import basic
        >>> from mutwo.parameters import tempos
        >>> from mutwo.converters import symmetrical
        >>> tempo_envelope = expenvelope.Envelope.from_levels_and_durations(
        >>>     levels=[tempos.TempoPoint(60), 60, 120, 120],
        >>>     durations=[3, 2, 5],
        >>> )
        >>> my_tempo_converter = symmetrical.tempos.TempoConverter(tempo_envelope)
        >>> my_events = basic.SequentialEvent([basic.SimpleEvent(d) for d in (3, 2, 5)])
        >>> my_tempo_converter.convert(my_events)
        SequentialEvent([SimpleEvent(duration = 3.0), SimpleEvent(duration = 1.5), SimpleEvent(duration = 2.5)])
        """
        copied_event_to_convert = event_to_convert.destructive_copy()
        self._convert_event(copied_event_to_convert, 0)
        return copied_event_to_convert
