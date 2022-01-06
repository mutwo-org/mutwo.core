"""Event classes which are designated for musical usage."""

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

import numbers
import typing

from mutwo import events
from mutwo import parameters
from mutwo.utilities import constants

__all__ = ("NoteLike",)

PitchOrPitchSequence = typing.Union[
    parameters.abc.Pitch, typing.Sequence, constants.Real, None
]

Volume = typing.Union[parameters.abc.Volume, constants.Real, str]
GraceNotes = events.basic.SequentialEvent[events.basic.SimpleEvent]


class NoteLike(events.basic.SimpleEvent):
    """NoteLike represents traditional discreet musical objects.

    :param pitch_list: The pitch or pitches of the event. This can
        be a pitch object (any class that inherits from ``mutwo.parameters.abc.Pitch``)
        or a list of pitch objects. Furthermore mutwo supports syntactic sugar
        to convert other objects on the fly to pitch objects: Atring can be
        read as pitch class names to build
        :class:`mutwo.parameters.pitches.WesternPitch` objects or as ratios to
        build :class:`mutwo.parameters.pitches.JustIntonationPitch` objects.
        Fraction will also build :class:`mutwo.parameters.pitches.JustIntonationPitch`
        objects. Other numbers (integer and float) will be read as pitch class numbers
        to make :class:`mutwo.parameters.pitches.WesternPitch` objects.
    :param duration: The duration of ``NoteLike``. This can be any number.
        The unit of the duration is up to the interpretation of the user and the
        respective converter routine that will be used.
    :param volume: The volume of the event. Can either be a object of
        :mod:`mutwo.parameters.volumes`, a number or a string. If the number
        ranges from 0 to 1, mutwo automatically generates a
        :class:`mutwo.parameters.volumes.DirectVolume` object (and the number
        will be interpreted as the amplitude). If the
        number is smaller than 0, automatically generates a
        :class:`mutwo.parameters.volumes.DecibelVolume` object (and the number
        will be interpreted as decibel). If the argument is a string,
        `mutwo` will try to initialise a :class:`mutwo.parameters.volumes.WesternVolume`
        object.
    :param grace_note_sequential_event:
    :type grace_note_sequential_event: events.basic.SequentialEvent[NoteLike]
    :param after_grace_note_sequential_event:
    :type after_grace_note_sequential_event: events.basic.SequentialEvent[NoteLike]
    :param playing_indicator_collection: A :class:`~mutwo.parameters.playing_indicator_collection.PlayingIndicatorCollection`.
        Playing indicators alter the sound of :class:`NoteLike` (e.g.
        tremolo, fermata, pizzicato).
    :type playing_indicator_collection: parameters.playing_indicator_collection.PlayingIndicatorCollection
    :param notation_indicator_collection: A :class:`~mutwo.parameters.notation_indicator_collection.NotationIndicatorCollection`.
        Notation indicators alter the visual representation of :class:`NoteLike`
        (e.g. ottava, clefs) without affecting the resulting sound.
    :type notation_indicator_collection: parameters.notation_indicator_collection.NotationIndicatorCollection

    By default mutwo doesn't differentiate between Tones, Chords and
    Rests, but rather simply implements one general class which can
    represent any of the mentioned definitions (e.g. a NoteLike object
    with several pitches may be called a 'Chord' and a NoteLike object
    with only one pitch may be called a 'Tone').

    **Example:**

    >>> from mutwo.parameters import pitches
    >>> from mutwo.events import music
    >>> tone = music.NoteLike(pitches.WesternPitch('a'), 1, 1)
    >>> other_tone = music.NoteLike('3/2', 1, 0.5)
    >>> chord = music.NoteLike(
        [pitches.WesternPitch('a'), pitches.JustIntonationPitch('3/2')], 1, 1
    )
    >>> other_chord = music.NoteLike('c4 dqs3 10/7', 1, 3)
    """

    def __init__(
        self,
        pitch_list: PitchOrPitchSequence = "c",
        duration: parameters.abc.DurationType = 1,
        volume: Volume = "mf",
        grace_note_sequential_event: typing.Optional[GraceNotes] = None,
        after_grace_note_sequential_event: typing.Optional[GraceNotes] = None,
        playing_indicator_collection: parameters.playing_indicators.PlayingIndicatorCollection = None,
        notation_indicator_collection: parameters.notation_indicators.NotationIndicatorCollection = None,
    ):
        if playing_indicator_collection is None:
            playing_indicator_collection = (
                events.music_constants.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS()
            )
        if notation_indicator_collection is None:
            notation_indicator_collection = (
                events.music_constants.DEFAULT_NOTATION_INDICATORS_COLLECTION_CLASS()
            )
        if grace_note_sequential_event is None:
            grace_note_sequential_event = events.basic.SequentialEvent([])
        if after_grace_note_sequential_event is None:
            after_grace_note_sequential_event = events.basic.SequentialEvent([])

        self.pitch_list = pitch_list
        self.volume = volume
        super().__init__(duration)
        self.grace_note_sequential_event = grace_note_sequential_event
        self.after_grace_note_sequential_event = after_grace_note_sequential_event
        self.playing_indicator_collection = playing_indicator_collection
        self.notation_indicator_collection = notation_indicator_collection

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _convert_string_to_pitch(pitch_indication: str) -> parameters.abc.Pitch:
        # assumes it is a ratio
        if "/" in pitch_indication:
            return parameters.pitches.JustIntonationPitch(pitch_indication)

        # assumes it is a WesternPitch name
        elif (
            pitch_indication[0]
            in parameters.pitches_constants.DIATONIC_PITCH_NAME_TO_PITCH_CLASS_DICT.keys()
        ):
            if pitch_indication[-1].isdigit():
                pitch_name, octave = pitch_indication[:-1], int(pitch_indication[-1])
                pitch = parameters.pitches.WesternPitch(pitch_name, octave)
            else:
                pitch = parameters.pitches.WesternPitch(pitch_indication)

            return pitch

        else:
            message = (
                "Can't build pitch from pitch_indication '{}'. Supported string formats"
                " are (1) ratios divided by a forward slash (for instance '3/2' or"
                " '4/3') and (2) names of western pitch classes with an optional number"
                " to indicate the octave (for instance 'c4', 'as' or 'fqs2')."
            )
            raise NotImplementedError(message)

    @staticmethod
    def _convert_fraction_to_pitch(
        pitch_indication: fractions.Fraction,
    ) -> parameters.abc.Pitch:
        return parameters.pitches.JustIntonationPitch(pitch_indication)

    @staticmethod
    def _convert_float_or_integer_to_pitch(
        pitch_indication: float,
    ) -> parameters.abc.Pitch:
        return parameters.pitches.WesternPitch(pitch_indication)

    @staticmethod
    def _convert_unknown_object_to_pitch(
        unknown_object: typing.Any,
    ) -> list[parameters.abc.Pitch]:
        if unknown_object is None:
            pitch_list = []

        elif isinstance(unknown_object, parameters.abc.Pitch):
            pitch_list = [unknown_object]

        elif isinstance(unknown_object, str):
            pitch_list = [
                NoteLike._convert_string_to_pitch(pitch_indication)
                for pitch_indication in unknown_object.split(" ")
            ]

        elif isinstance(unknown_object, fractions.Fraction):
            pitch_list = [NoteLike._convert_fraction_to_pitch(unknown_object)]

        elif isinstance(unknown_object, float) or isinstance(unknown_object, int):
            pitch_list = [NoteLike._convert_float_or_integer_to_pitch(unknown_object)]

        else:
            message = "Can't build pitch object from object '{}' of type '{}'.".format(
                unknown_object, type(unknown_object)
            )
            raise NotImplementedError(message)

        return pitch_list

    @staticmethod
    def _convert_unknown_object_to_grace_note_sequential_event(
        unknown_object: typing.Union[GraceNotes, events.basic.SimpleEvent]
    ) -> GraceNotes:
        if isinstance(unknown_object, events.basic.SimpleEvent):
            return events.basic.SequentialEvent([unknown_object])
        elif isinstance(unknown_object, events.basic.SequentialEvent):
            return unknown_object
        else:
            raise TypeError(f"Can't set grace notes to {unknown_object}")

    # ###################################################################### #
    #                            properties                                  #
    # ###################################################################### #

    @property
    def _parameter_to_print_tuple(self) -> tuple[str, ...]:
        """Return tuple of attribute names which shall be printed for repr."""
        return tuple(
            attribute
            for attribute in self._parameter_to_compare_tuple
            if attribute
            # Avoid too verbose and long attributes
            not in (
                "playing_indicator_collection",
                "notation_indicator_collection",
                "grace_note_sequential_event",
                "after_grace_note_sequential_event",
            )
        )

    @property
    def pitch_list(self) -> typing.Any:
        """The pitch or pitches of the event."""

        return self._pitch_list

    @pitch_list.setter
    def pitch_list(self, pitch_list: typing.Any):
        # make sure pitch_list always become assigned to a list of pitches,
        # to be certain of the returned type
        if not isinstance(pitch_list, str) and isinstance(pitch_list, typing.Iterable):
            # several pitches
            pitches_per_element = (
                NoteLike._convert_unknown_object_to_pitch(pitch) for pitch in pitch_list
            )
            pitch_list = []
            for pitches in pitches_per_element:
                pitch_list.extend(pitches)
        else:
            pitch_list = NoteLike._convert_unknown_object_to_pitch(pitch_list)

        self._pitch_list = pitch_list

    @property
    def volume(self) -> typing.Any:
        """The volume of the event."""

        return self._volume

    @volume.setter
    def volume(self, volume: typing.Any):
        if isinstance(volume, numbers.Real):
            if volume >= 0:  # type: ignore
                volume = parameters.volumes.DirectVolume(volume)  # type: ignore
            else:
                volume = parameters.volumes.DecibelVolume(volume)  # type: ignore

        elif isinstance(volume, str):
            volume = parameters.volumes.WesternVolume(volume)

        elif not isinstance(volume, parameters.abc.Volume):
            message = (
                "Can't initialise '{}' with value '{}' of type '{}' for argument"
                " 'volume'. The type for 'volume' should be '{}'.".format(
                    type(self).__name__, volume, type(volume), Volume
                )
            )
            raise TypeError(message)
        self._volume = volume

    @property
    def grace_note_sequential_event(self) -> GraceNotes:
        """Fast NoteLikes before the actual :class:`NoteLike`"""

        return self._grace_note_sequential_event

    @grace_note_sequential_event.setter
    def grace_note_sequential_event(
        self,
        grace_note_sequential_event: typing.Union[GraceNotes, events.basic.SimpleEvent],
    ):
        self._grace_note_sequential_event = (
            NoteLike._convert_unknown_object_to_grace_note_sequential_event(
                grace_note_sequential_event
            )
        )

    @property
    def after_grace_note_sequential_event(self) -> GraceNotes:
        """Fast NoteLikes after the actual :class:`NoteLike`"""

        return self._after_grace_note_sequential_event

    @after_grace_note_sequential_event.setter
    def after_grace_note_sequential_event(
        self,
        after_grace_note_sequential_event: typing.Union[
            GraceNotes, events.basic.SimpleEvent
        ],
    ):
        self._after_grace_note_sequential_event = (
            NoteLike._convert_unknown_object_to_grace_note_sequential_event(
                after_grace_note_sequential_event
            )
        )
