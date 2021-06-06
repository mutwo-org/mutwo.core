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

PitchOrPitches = typing.Union[
    parameters.abc.Pitch, typing.Iterable, constants.Real, None
]

Volume = typing.Union[parameters.abc.Volume, constants.Real, str]


class NoteLike(events.basic.SimpleEvent):
    """NoteLike represents traditional discreet musical objects.

    :param pitch_or_pitches: The pitch or pitches of the event. This can
        be a pitch object (any class that inherits from ``mutwo.parameters.abc.Pitch``)
        or a list of pitch objects. Furthermore mutwo supports syntactic sugar
        to convert other objects on the fly to pitch objects: Atring can be
        read as pitch class names to build
        :class:`mutwo.parameters.pitches.WesternPitch` objects or as ratios to
        build :class:`mutwo.parameters.pitches.JustIntonationPitch` objects.
        Fraction will also build :class:`mutwo.parameters.pitches.JustIntonationPitch`
        objects. Other numbers (integer and float) will be read as pitch class numbers
        to make :class:`mutwo.parameters.pitches.WesternPitch` objects.
    :param new_duration: The duration of ``NoteLike``. This can be any number.
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
    :param playing_indicators:
    :param notation_indicators:

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
        pitch_or_pitches: PitchOrPitches = "c",
        duration: parameters.abc.DurationType = 1,
        volume: Volume = "mf",
        playing_indicators: parameters.playing_indicators.PlayingIndicatorCollection = None,
        notation_indicators: parameters.notation_indicators.NotationIndicatorCollection = None,
        # before_grace_notes  # TODO(add grace note container!)
        # after_grace_notes
    ):
        if playing_indicators is None:
            playing_indicators = (
                events.music_constants.DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS()
            )

        if notation_indicators is None:
            notation_indicators = (
                events.music_constants.DEFAULT_NOTATION_INDICATORS_COLLECTION_CLASS()
            )

        self.pitch_or_pitches = pitch_or_pitches
        self.volume = volume
        super().__init__(duration)
        self.playing_indicators = playing_indicators
        self.notation_indicators = notation_indicators

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
            in parameters.pitches_constants.DIATONIC_PITCH_NAME_TO_PITCH_CLASS.keys()
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
    ) -> typing.List[parameters.abc.Pitch]:
        if unknown_object is None:
            pitches = []

        elif isinstance(unknown_object, parameters.abc.Pitch):
            pitches = [unknown_object]

        elif isinstance(unknown_object, str):
            pitches = [
                NoteLike._convert_string_to_pitch(pitch_indication)
                for pitch_indication in unknown_object.split(" ")
            ]

        elif isinstance(unknown_object, fractions.Fraction):
            pitches = [NoteLike._convert_fraction_to_pitch(unknown_object)]

        elif isinstance(unknown_object, float) or isinstance(unknown_object, int):
            pitches = [NoteLike._convert_float_or_integer_to_pitch(unknown_object)]

        else:
            message = "Can't build pitch object from object '{}' of type '{}'.".format(
                unknown_object, type(unknown_object)
            )
            raise NotImplementedError(message)

        return pitches

    # ###################################################################### #
    #                            properties                                  #
    # ###################################################################### #

    @property
    def _parameters_to_print(self) -> typing.Tuple[str, ...]:
        """Return tuple of attribute names which shall be printed for repr.
        """
        return tuple(
            attribute
            for attribute in self._parameters_to_compare
            if attribute not in ("playing_indicators", "notation_indicators")
        )

    @property
    def pitch_or_pitches(self) -> typing.Any:
        """The pitch or pitches of the event."""

        return self._pitch_or_pitches

    @pitch_or_pitches.setter
    def pitch_or_pitches(self, pitch_or_pitches: typing.Any):
        # make sure pitch_or_pitches always become assigned to a list of pitches,
        # to be certain of the returned type
        if not isinstance(pitch_or_pitches, str) and isinstance(
            pitch_or_pitches, typing.Iterable
        ):
            # several pitches
            pitches_per_element = (
                NoteLike._convert_unknown_object_to_pitch(pitch)
                for pitch in pitch_or_pitches
            )
            pitch_or_pitches = []
            for pitches in pitches_per_element:
                pitch_or_pitches.extend(pitches)
        else:
            pitch_or_pitches = NoteLike._convert_unknown_object_to_pitch(
                pitch_or_pitches
            )

        self._pitch_or_pitches = pitch_or_pitches

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
