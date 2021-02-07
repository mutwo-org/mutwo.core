"""This module contains Event classes which are accounted for musical usage."""

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

    :param pitch_or_pitches:
    :param duration:
    :param volume:

    By default mutwo doesn't differentiate between Tones, Chords and
    Rests, but rather simply implements one general class which can
    represent any of the mentioned definitions (e.g. a NoteLike object
    with several pitches may be called a 'Chord' and a NoteLike object
    with only one pitch may be called a 'Tone').
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
