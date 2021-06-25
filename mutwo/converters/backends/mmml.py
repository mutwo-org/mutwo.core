"""Module for converting MMML text to Mutwo objects.

MMML is an abbreviation for 'Mutwos Music Markup Language'.
Similarly to `Music Macro Language <https://en.wikipedia.org/wiki/Music_Macro_Language>`_
it is intended to be a easy human readable and writeable plain text encoding
for musical data. The language is inspired by Lilypond, ABC Notation, Guido and Alda.
It differs from the former insofar as that the render engine (frontend) is
unspecified. Furthermore MMML is quite open to different notation specifications for
pitch, dynamics and rhythm as long as predefined identifier won't get overridden.
"""

import typing

from mutwo.converters import abc
from mutwo.converters.backends import mmml_constants
from mutwo import parameters

___all___ = (
    "MMMLSinglePitchConverter",
    "MMMLSingleJIPitchConverter",
    "MMMLPitchesConverter",
)


class MMMLSinglePitchConverter(abc.Converter):
    """Convert a single MMML pitch string to a mutwo pitch object."""

    def __init__(
        self,
        decodex_or_decodex_function: typing.Union[
            typing.Dict[str, parameters.abc.Pitch],
            typing.Callable[[str], parameters.abc.Pitch],
        ],
        octave_mark_processor: typing.Callable[
            [parameters.abc.Pitch, typing.Optional[str]], parameters.abc.Pitch
        ] = lambda pitch, _: pitch,
    ):
        self._decodex_or_decodex_function = decodex_or_decodex_function
        self._octave_mark_processor = octave_mark_processor

    def convert(
        self, mmml_pitch_to_convert: str
    ) -> typing.Optional[parameters.abc.Pitch]:
        mmml_pitch_class, *mmml_octave_mark = mmml_pitch_to_convert.split(
            mmml_constants.OCTAVE_IDENTIFIER
        )

        if mmml_pitch_class == mmml_constants.REST_IDENTIFIER:
            return None

        if mmml_octave_mark:
            mmml_octave_mark = mmml_octave_mark[0]

        if hasattr(self._decodex_or_decodex_function, "__call__"):
            mutwo_pitch = self._decodex_or_decodex_function(mmml_pitch_class)
        else:
            mutwo_pitch = self._decodex_or_decodex_function[mmml_pitch_class]

        mutwo_pitch = self._octave_mark_processor(mutwo_pitch, mmml_octave_mark)
        return mutwo_pitch


class MMMLSingleJIPitchConverter(MMMLSinglePitchConverter):
    def __init__(self):
        super().__init__(self._decodex_function, self._octave_mark_processor)

    @staticmethod
    def _get_and_add_prime_and_exponent_pair(
        prime_to_exponent: typing.Dict[int, int],
        element: str,
        current_base: str,
        current_exponent: int,
    ) -> typing.Tuple[str, int]:
        base = int(current_base)
        if base in prime_to_exponent:
            message = f"Found duplicate base {base}!"
            raise ValueError(message)
        prime_to_exponent.update({base: current_exponent})
        current_base = element
        current_exponent = 0
        is_separating = False
        return current_base, current_exponent, is_separating

    @staticmethod
    def _split_to_prime_and_exponent_pairs(
        mmml_pitch_class_to_convert: str,
    ) -> typing.Tuple[str, ...]:
        is_separating = False
        current_base = ""
        current_exponent = 0
        prime_to_exponent = {}
        for element in mmml_pitch_class_to_convert:
            if element.isdigit():
                if is_separating:
                    (
                        current_base,
                        current_exponent,
                        is_separating,
                    ) = MMMLSingleJIPitchConverter._get_and_add_prime_and_exponent_pair(
                        prime_to_exponent, element, current_base, current_exponent
                    )
                else:
                    current_base += element
            elif element == mmml_constants.JUST_INTONATION_POSITIVE_EXPONENT_IDENTIFIER:
                is_separating = True
                current_exponent += 1
            elif element == mmml_constants.JUST_INTONATION_NEGATIVE_EXPONENT_IDENTIFIER:
                is_separating = True
                current_exponent -= 1
            else:
                message = (
                    f"Found undefined sign {element} in {mmml_pitch_class_to_convert}!"
                )
                raise NotImplementedError(message)

        return prime_to_exponent

    @staticmethod
    def _decodex_function(
        mmml_pitch_class_to_convert: str,
    ) -> parameters.pitches.JustIntonationPitch:
        prime_to_exponent = MMMLSingleJIPitchConverter._split_to_prime_and_exponent_pairs(
            mmml_pitch_class_to_convert
        )
        numerator = 1
        denominator = 1

        for prime, exponent in prime_to_exponent.items():
            multiplied = prime ** abs(exponent)
            if exponent > 0:
                numerator *= multiplied
            else:
                denominator *= multiplied

        pitch = parameters.pitches.JustIntonationPitch(f"{numerator}/{denominator}")
        return pitch

    @staticmethod
    def _octave_mark_processor(
        just_intonation_pitch: parameters.pitches.JustIntonationPitch,
        mmml_octave_mark_to_apply: typing.Optional[str],
    ) -> parameters.pitches.JustIntonationPitch:
        if mmml_octave_mark_to_apply:
            octave = int(mmml_octave_mark_to_apply)
        else:
            octave = 0
        just_intonation_pitch.register(octave)
        return just_intonation_pitch


class MMMLPitchesConverter(abc.Converter):
    """Convert one or multiple MMML pitches to mutwo pitch objects."""

    def __init__(
        self,
        mmml_single_pitch_converter: MMMLSinglePitchConverter = MMMLSinglePitchConverter(
            lambda frequency: parameters.pitches.DirectPitch(float(frequency)),
            lambda pitch, octave: parameters.pitches.DirectPitch(
                pitch.frequency * (2 ** int(octave))
            )
            if octave
            else pitch,
        ),
        default_pitch: parameters.abc.Pitch = parameters.pitches.DirectPitch(440),
        default_octave_mark: str = "0",
    ):
        self._mmml_single_pitch_converter = mmml_single_pitch_converter
        self._default_pitch = default_pitch
        self._default_octave_mark = default_octave_mark

    @staticmethod
    def _get_octave_mark(mmml_pitch: str) -> typing.Optional[str]:
        _, *mmml_octave_mark = mmml_pitch.split(mmml_constants.OCTAVE_IDENTIFIER)
        if mmml_octave_mark:
            return mmml_octave_mark[0]
        return None

    def _convert_mmml_pitch_or_pitches_to_mutwo_pitch_or_pitches(
        self, mmml_pitch_or_pitches_to_convert: str, previous_octave_mark: str,
    ) -> typing.Tuple[typing.Tuple[parameters.abc.Pitch, ...], str]:
        converted_chord = []
        for mmml_pitch_to_convert in mmml_pitch_or_pitches_to_convert.split(
            mmml_constants.MULTIPLE_PITCHES_IDENTIFIER
        ):
            current_octave_mark = self._get_octave_mark(mmml_pitch_to_convert)
            if current_octave_mark:
                previous_octave_mark = current_octave_mark
            else:
                mmml_pitch_to_convert = (
                    f"{mmml_pitch_to_convert}:{previous_octave_mark}"
                )
            converted_pitch = self._mmml_single_pitch_converter.convert(
                mmml_pitch_to_convert
            )
            if converted_pitch:
                converted_chord.append(converted_pitch)
        converted_chord = tuple(converted_chord)
        return converted_chord, previous_octave_mark

    def convert(
        self,
        mmml_pitches_to_convert: typing.Union[
            str, typing.Sequence[typing.Optional[str]]
        ],
    ) -> typing.Tuple[typing.Tuple[parameters.abc.Pitch, ...], ...]:
        previous_chord = (self._default_pitch,)
        previous_octave_mark = self._default_octave_mark

        mmml_pitch_events_to_iterate = (
            mmml_pitches_to_convert.split(mmml_constants.EVENT_IDENTIFIER)
            if hasattr(mmml_pitches_to_convert, "split")
            else mmml_pitches_to_convert
        )

        converted_pitches = []
        for mmml_pitch_or_pitches_to_convert in mmml_pitch_events_to_iterate:
            if mmml_pitch_or_pitches_to_convert:
                (
                    converted_chord,
                    previous_octave_mark,
                ) = self._convert_mmml_pitch_or_pitches_to_mutwo_pitch_or_pitches(
                    mmml_pitch_or_pitches_to_convert, previous_octave_mark
                )
                previous_chord = converted_chord
            else:
                converted_chord = previous_chord
            converted_pitches.append(converted_chord)
        return tuple(converted_pitches)
