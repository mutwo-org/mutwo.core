import numbers
import typing

from mutwo.parameters.pitches import abc as pitches_abc
from mutwo.parameters.pitches import constants as pitches_constants


ConcertPitch = typing.Union[numbers.Number, pitches_abc.Pitch]


class PitchWithConcertPitch(pitches_abc.Pitch):
    def __init__(
        self, concert_pitch: ConcertPitch = pitches_constants.DEFAULT_CONCERT_PITCH
    ):
        self.concert_pitch = concert_pitch
