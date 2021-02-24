"""This module contains Event classes which are designated for musical usage."""

import numbers
import typing

from mutwo import events
from mutwo import parameters

__all__ = ("NoteLike",)

PitchOrPitches = typing.Union[
    parameters.abc.Pitch, typing.Iterable, numbers.Number, None
]


class NoteLike(events.basic.SimpleEvent):
    """NoteLike represents a traditional discreet musical object.

    :param pitch_or_pitches: The pitch or pitches of the event. This can
        be a pitch object (any class that inherits from ``mutwo.parameters.abc.Pitch``)
        or a list of pitch objects.
    :param new_duration: The duration of ``NoteLike``. This can be any number.
        The unit of the duration is up to the interpretation of the user and the
        respective converter routine that will be used.
    :param volume: The volume of the event.

    By default mutwo doesn't differentiate between Tones, Chords and
    Rests, but rather simply implements one general class which can
    represent any of the mentioned definitions (e.g. a NoteLike object
    with several pitches may be called a 'Chord' and a NoteLike object
    with only one pitch may be called a 'Tone').

    **Example:**

    >>> from mutwo.parameters import pitches
    >>> from mutwo.events import music
    >>> tone = music.NoteLike(pitches.WesternPitch('a'), 1, 1)
    >>> chord = music.NoteLike([pitches.WesternPitch('a'), pitches.JustIntonationPitch('3/2')], 1, 1)
    """

    def __init__(
        self,
        pitch_or_pitches: PitchOrPitches,
        duration: parameters.abc.DurationType,
        volume: numbers.Number,
    ):
        self.pitch_or_pitches = pitch_or_pitches
        self.volume = volume
        super().__init__(duration)

    @property
    def pitch_or_pitches(self) -> list:
        """The pitch or pitches of the event."""

        return self._pitch_or_pitches

    @pitch_or_pitches.setter
    def pitch_or_pitches(self, pitch_or_pitches: PitchOrPitches) -> None:
        # make sure pitch_or_pitches always become assigned to a list of pitches,
        # to be certain of the returned type
        if not isinstance(pitch_or_pitches, typing.Iterable):
            if pitch_or_pitches is not None:
                # only one pitch
                pitch_or_pitches = [pitch_or_pitches]
            else:
                # no pitches
                pitch_or_pitches = []
        else:
            # several pitches
            pitch_or_pitches = list(pitch_or_pitches)

        self._pitch_or_pitches = pitch_or_pitches
