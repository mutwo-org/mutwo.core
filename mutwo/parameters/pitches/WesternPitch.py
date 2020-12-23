import numbers
import re
import typing

from mutwo.parameters import pitches
from mutwo.utilities import tools


ConcertPitch = typing.Union[numbers.Number, pitches.abc.Pitch]
PitchClassOrPitchClassName = typing.Union[numbers.Number, str]


# TODO(add support for quarter tones and more when initialising
# via pitch class number)
# TODO(use constants for accidentals)
# TODO(add something similar to scamps SpellingPolicy (don't hard code
# if mutwo shall write a flat or sharp)
# TODO(add translation from octave number to notated octave (4 -> ', 5 -> '', ..))
# TODO(just pass an EqualDividedOctave pitch with n_pitch_classes_per_octave=12 instead
# of passing pitch_class, octave and frequency independent from each other?)


class WesternPitch(pitches.EqualDividedOctavePitch):
    def __init__(
        self,
        pitch_class_or_pitch_class_name: PitchClassOrPitchClassName = 0,
        octave: int = 4,
        concert_pitch_pitch_class: numbers.Number = 9,  # a
        concert_pitch_octave: numbers.Number = 4,  # a'
        concert_pitch: ConcertPitch = pitches.constants.DEFAULT_CONCERT_PITCH,
    ):
        (
            pitch_class,
            pitch_class_name,
        ) = self._translate_pitch_class_or_pitch_class_name_to_pitch_class_and_pitch_class_name(
            pitch_class_or_pitch_class_name
        )
        super().__init__(
            12,
            pitch_class,
            octave,
            concert_pitch_pitch_class,
            concert_pitch_octave,
            concert_pitch,
        )

        self._pitch_class_name = pitch_class_name

    @staticmethod
    def _translate_pitch_class_or_pitch_class_name_to_pitch_class_and_pitch_class_name(
        pitch_class_or_pitch_class_name: PitchClassOrPitchClassName,
    ) -> tuple:
        if isinstance(pitch_class_or_pitch_class_name, numbers.Number):
            pitch_class = float(pitch_class_or_pitch_class_name)
            pitch_class_name = WesternPitch._translate_pitch_class_to_pitch_class_name(
                pitch_class_or_pitch_class_name
            )
        elif isinstance(pitch_class_or_pitch_class_name, str):
            pitch_class = WesternPitch._translate_pitch_class_name_to_pitch_class(
                pitch_class_or_pitch_class_name
            )
            pitch_class_name = pitch_class_or_pitch_class_name
        else:
            message = "Can't initalise pitch_class by '{}' of type '{}'.".format(
                pitch_class_or_pitch_class_name, type(pitch_class_or_pitch_class_name)
            )
            raise TypeError(message)

        return pitch_class, pitch_class_name

    @staticmethod
    def _translate_accidentals_to_pitch_class_modifications(
        accidentals: str,
    ) -> numbers.Number:
        found_accidentals = re.findall(
            pitches.constants.ACCIDENTALS_REGEX_PATTERN, accidentals
        )
        return sum(
            pitches.constants.ACCIDENTAL_NAME_TO_PITCH_CLASS_MODIFICATION[accidental]
            for accidental in found_accidentals
        )

    @staticmethod
    def _translate_pitch_class_name_to_pitch_class(
        pitch_class_name: str,
    ) -> numbers.Number:
        diatonic_pitch_class_name, accidentals = (
            pitch_class_name[0],
            pitch_class_name[1:],
        )
        diatonic_pitch_class = pitches.constants.DIATONIC_PITCH_NAME_TO_PITCH_CLASS[
            diatonic_pitch_class_name
        ]
        pitch_class_modification = WesternPitch._translate_accidentals_to_pitch_class_modifications(
            accidentals
        )
        return diatonic_pitch_class + pitch_class_modification

    @staticmethod
    def _translate_pitch_class_to_pitch_class_name(pitch_class: numbers.Number) -> str:
        diatonic_pitch_classes = tuple(
            pitches.constants.DIATONIC_PITCH_NAME_TO_PITCH_CLASS.values()
        )
        closest_diatonic_pitch_class_index = tools.find_closest_index(
            pitch_class, diatonic_pitch_classes
        )
        closest_diatonic_pitch_class = diatonic_pitch_classes[
            closest_diatonic_pitch_class_index
        ]
        closest_diatonic_pitch = tuple(
            pitches.constants.DIATONIC_PITCH_NAME_TO_PITCH_CLASS.keys()
        )[closest_diatonic_pitch_class_index]
        difference_to_closest_diatonic_pitch = (
            pitch_class - closest_diatonic_pitch_class
        )

        if difference_to_closest_diatonic_pitch > 0:
            accidental = "s"
        else:
            accidental = "f"

        pitch_class_name = "{}{}".format(
            closest_diatonic_pitch,
            "".join([accidental] * int(abs(difference_to_closest_diatonic_pitch))),
        )
        return pitch_class_name

    def __repr__(self) -> str:
        return "{}({})".format(type(self).__name__, self.name)

    @property
    def name(self) -> str:
        return "{}{}".format(self._pitch_class_name, self.octave)

    @property
    def pitch_class_name(self) -> str:
        return self._pitch_class_name

    @pitch_class_name.setter
    def pitch_class_name(self, pitch_class_name: str):
        self._pitch_class = self._translate_pitch_class_name_to_pitch_class(
            pitch_class_name
        )
        self._pitch_class_name = pitch_class_name

    @pitches.EqualDividedOctavePitch.pitch_class.setter
    def pitch_class(self, pitch_class: numbers.Number):
        self._pitch_class_name = self._translate_pitch_class_to_pitch_class_name(
            pitch_class
        )
        self._pitch_class = pitch_class
