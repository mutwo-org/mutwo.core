import numbers
import typing

from mutwo import events
from mutwo import parameters

PitchOrPitches = typing.Union[parameters.pitches.abc.Pitch, typing.Iterable, numbers.Number, None]

class NoteLike(events.basic.SimpleEvent):
    """NoteLike represents a traditional discreet musical object."""

    def __init__(self, pitch_or_pitches: PitchOrPitches, duration: numbers.Number, dynamic: numbers.Number):
        self.pitch_or_pitches = pitch_or_pitches
        super().__init__(duration)

    @property
    def pitch_or_pitches(self) -> list:
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