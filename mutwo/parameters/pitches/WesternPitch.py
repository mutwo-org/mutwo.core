import numbers
import re
import typing

from mutwo.parameters import pitches
from mutwo.utilities import tools


ConcertPitch = typing.Union[numbers.Number, pitches.abc.Pitch]
PitchClassOrPitchClassName = typing.Union[numbers.Number, str]


# TODO(add something similar to scamps SpellingPolicy (don't hard code
# if mutwo shall write a flat or sharp)
# TODO(add translation from octave number to notated octave (4 -> ', 5 -> '', ..))


class WesternPitch(pitches.EqualDividedOctavePitch):
    """A WesternPitch is a Pitch with traditional Western nomenclature.

    It uses an equal divided octave system in 12 chromatic steps.
    The nomenclature is English (c, d, e, f, g, a, b).
    Accidentals are indicated by (s = sharp) and (f = flat) and can be
    stacked. Further microtonal accidentals are supported (see
    mutwo.parameters.pitches.constants.ACCIDENTAL_NAME_TO_PITCH_CLASS_MODIFICATION
    for all supported accidentals). Indications for the specific octave
    follow the MIDI Standard where 4 is defined as one line.
    """

    def __init__(
        self,
        pitch_class_or_pitch_class_name: PitchClassOrPitchClassName = 0,
        octave: int = 4,
        concert_pitch_pitch_class: numbers.Number = None,
        concert_pitch_octave: numbers.Number = None,
        concert_pitch: ConcertPitch = None,
    ):
        if concert_pitch_pitch_class is None:
            concert_pitch_pitch_class = (
                pitches.constants.DEFAULT_CONCERT_PITCH_PITCH_CLASS_FOR_WESTERN_PITCH
            )

        if concert_pitch_octave is None:
            concert_pitch_octave = (
                pitches.constants.DEFAULT_CONCERT_PITCH_OCTAVE_FOR_WESTERN_PITCH
            )

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

        # test if any accidentals are unknown
        unknown_accidentals = tuple(
            filter(
                lambda string: bool(string),
                re.split(pitches.constants.ACCIDENTALS_REGEX_PATTERN, accidentals),
            )
        )
        if unknown_accidentals:
            message = "Found unknown accidentals {}! Can't initialise".format(
                unknown_accidentals
            )
            message += " WesternPitch with accidental {}.".format(accidentals)
            raise ValueError(message)

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
    def _translate_difference_to_closest_diatonic_pitch_to_accidental(
        difference_to_closest_diatonic_pitch: numbers.Number,
    ) -> str:
        # TODO(add support for microtones)
        if difference_to_closest_diatonic_pitch > 0:
            accidental = "s"
        else:
            accidental = "f"

        return "".join([accidental] * int(abs(difference_to_closest_diatonic_pitch)))

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

        accidental = WesternPitch._translate_difference_to_closest_diatonic_pitch_to_accidental(
            difference_to_closest_diatonic_pitch
        )

        pitch_class_name = "{}{}".format(closest_diatonic_pitch, accidental)
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
