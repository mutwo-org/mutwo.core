"""Constants to be used for and with :mod:`mutwo.converters.frontends.ekmelily`.

Some constants are also used as default values of
:class:`~mutwo.converters.frontends.abjad.MutwoPitchToHEJIAbjadPitchConverter`
__init__ method.
"""

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore


from mutwo.parameters import pitches
from mutwo.parameters import pitches_constants

DEFAULT_GLOBAL_SCALE = (
    fractions.Fraction(0),
    fractions.Fraction(1),
    fractions.Fraction(2),
    fractions.Fraction(5, 2),
    fractions.Fraction(7, 2),
    fractions.Fraction(9, 2),
    fractions.Fraction(11, 2),
)
"""Default value for
:class:`~mutwo.converters.frontends.ekmelily.EkmelilyTuningFileConverter`
argument `global_scale`."""


# TODO(find glyph names in 'EkmelosGlyphNames.nam' file, provided
#      by Ekmelos 3.5 (instead of hard coding hexacodes))
PRIME_AND_EXPONENT_AND_TRADITIONAL_ACCIDENTAL_TO_ACCIDENTAL_GLYPH = {
    (
        None,
        None,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(0, 1)
        ],
    ): (
        "#xE261"
    ),
    (
        None,
        None,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(1, 1)
        ],
    ): (
        "#xE262"
    ),
    (
        None,
        None,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(2, 1)
        ],
    ): (
        "#xE263"
    ),
    (
        None,
        None,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            -fractions.Fraction(1, 1)
        ],
    ): (
        "#xE260"
    ),
    (
        None,
        None,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            -fractions.Fraction(2, 1)
        ],
    ): (
        "#xE264"
    ),
    (
        5,
        1,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(0, 1)
        ],
    ): (
        "#xE2C2"
    ),
    (
        5,
        2,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(0, 1)
        ],
    ): (
        "#xE2C2"
    ),
    (
        5,
        3,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(0, 1)
        ],
    ): (
        "#xE2D6"
    ),
    (
        5,
        -1,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(0, 1)
        ],
    ): (
        "#xE2C7"
    ),
    (
        5,
        -2,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(0, 1)
        ],
    ): (
        "#xE2D1"
    ),
    (
        5,
        -3,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(0, 1)
        ],
    ): (
        "#xE2DB"
    ),
    (
        5,
        1,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(1, 1)
        ],
    ): (
        "#xE2C3"
    ),
    (
        5,
        2,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(1, 1)
        ],
    ): (
        "#xE2CD"
    ),
    (
        5,
        3,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(1, 1)
        ],
    ): (
        "#xE2D7"
    ),
    (
        5,
        -1,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(1, 1)
        ],
    ): (
        "#xE2C8"
    ),
    (
        5,
        -2,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(1, 1)
        ],
    ): (
        "#xE2D2"
    ),
    (
        5,
        -3,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(1, 1)
        ],
    ): (
        "#xE2DC"
    ),
    (
        5,
        1,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(2, 1)
        ],
    ): (
        "#xE2C4"
    ),
    (
        5,
        2,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(2, 1)
        ],
    ): (
        "#xE2CE"
    ),
    (
        5,
        3,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(2, 1)
        ],
    ): (
        "#xE2D8"
    ),
    (
        5,
        -1,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(2, 1)
        ],
    ): (
        "#xE2C9"
    ),
    (
        5,
        -2,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(2, 1)
        ],
    ): (
        "#xE2D3"
    ),
    (
        5,
        -3,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            fractions.Fraction(2, 1)
        ],
    ): (
        "#xE2DD"
    ),
    (
        5,
        1,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            -fractions.Fraction(1, 1)
        ],
    ): (
        "#xE2C1"
    ),
    (
        5,
        2,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            -fractions.Fraction(1, 1)
        ],
    ): (
        "#xE2CB"
    ),
    (
        5,
        3,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            -fractions.Fraction(1, 1)
        ],
    ): (
        "#xE2D5"
    ),
    (
        5,
        -1,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            -fractions.Fraction(1, 1)
        ],
    ): (
        "#xE2C6"
    ),
    (
        5,
        -2,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            -fractions.Fraction(1, 1)
        ],
    ): (
        "#xE2D0"
    ),
    (
        5,
        -3,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            -fractions.Fraction(1, 1)
        ],
    ): (
        "#xE2DA"
    ),
    (
        5,
        1,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            -fractions.Fraction(2, 1)
        ],
    ): (
        "#xE2C0"
    ),
    (
        5,
        2,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            -fractions.Fraction(2, 1)
        ],
    ): (
        "#xE2CA"
    ),
    (
        5,
        3,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            -fractions.Fraction(2, 1)
        ],
    ): (
        "#xE2D4"
    ),
    (
        5,
        -1,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            -fractions.Fraction(2, 1)
        ],
    ): (
        "#xE2C5"
    ),
    (
        5,
        -2,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            -fractions.Fraction(2, 1)
        ],
    ): (
        "#xE2CF"
    ),
    (
        5,
        -3,
        pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
            -fractions.Fraction(2, 1)
        ],
    ): (
        "#xE2D9"
    ),
    (7, 1, None): "#xE2DE",
    (7, 2, None): "#xE2E0",
    (7, -1, None): "#xE2DF",
    (7, -2, None): "#xE2E1",
    (11, 1, None): "#xE2E3",
    (11, -1, None): "#xE2E2",
    (13, 1, None): "#xE2E4",
    (13, -1, None): "#xE2E5",
    (17, 1, None): "#xE2E6",
    (17, -1, None): "#xE2E7",
    (19, 1, None): "#xE2E9",
    (19, -1, None): "#xE2E8",
    (23, 1, None): "#xE2EA",
    (23, -1, None): "#xE2EB",
}
"""Mapping of prime, exponent and pythagorean accidental to accidental
glyph name in Ekmelos."""


TEMPERED_ACCIDENTAL_TO_ACCIDENTAL_GLYPH = {
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        fractions.Fraction(0, 1)
    ]: (
        "#xE2F2"
    ),
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        fractions.Fraction(1, 1)
    ]: (
        "#xE2F3"
    ),
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        fractions.Fraction(2, 1)
    ]: (
        "#xE2F4"
    ),
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        -fractions.Fraction(1, 1)
    ]: (
        "#xE2F1"
    ),
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        -fractions.Fraction(2, 1)
    ]: (
        "#xE2F0"
    ),
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        fractions.Fraction(1, 2)
    ]: (
        "#xE2F6"
    ),
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        -fractions.Fraction(1, 2)
    ]: (
        "#xE2F5"
    ),
}
"""Mapping of tempered accidental name to glyph name in Ekmelos."""

TEMPERED_ACCIDENTAL_TO_CENT_DEVIATION = {
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        fractions.Fraction(0, 1)
    ]: 0,
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        fractions.Fraction(1, 1)
    ]: 100,
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        fractions.Fraction(2, 1)
    ]: 200,
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        -fractions.Fraction(1, 1)
    ]: -100,
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        -fractions.Fraction(2, 1)
    ]: -200,
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        fractions.Fraction(1, 2)
    ]: 50,
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        -fractions.Fraction(1, 2)
    ]: -50,
}
"""Mapping of tempered accidental name to cent deviation."""

DEFAULT_PRIME_TO_HEJI_ACCIDENTAL_NAME = {
    prime: accidental_name
    for prime, accidental_name in zip(
        (5, 7, 11, 13, 17, 19, 23), "a b c d e f g".split(" ")
    )
}
"""Default mapping for
:class:`~mutwo.converters.frontends.ekmelily.HEJIEkmelilyTuningFileConverter`
argument `prime_to_heji_accidental_name`."""

DEFAULT_PRIME_TO_HIGHEST_ALLOWED_EXPONENT = {
    prime: highest_allowed_comma
    # all potentially supported prime / max_exponent pairs:
    # (not used by default, because Lilypond would take too
    #  long for parsing)
    # for prime, highest_allowed_comma in zip(
    #     (5, 7, 11, 13, 17, 19, 23), (3, 2, 1, 1, 1, 1, 1),
    # )
    for prime, highest_allowed_comma in zip((5, 7, 11, 13, 17), (3, 2, 1, 1, 1),)
}
"""Default value for
:class:`~mutwo.converters.frontends.ekmelily.HEJIEkmelilyTuningFileConverter`
argument `prime_to_highest_allowed_exponent`."""

DEFAULT_TEMPERED_PITCH_INDICATOR = "t"
"""Default value for
:class:`~mutwo.converters.frontends.ekmelily.HEJIEkmelilyTuningFileConverter`
argument `tempered_pitch_indicator`."""

DEFAULT_OTONALITY_INDICATOR = "o"
"""Default value for
:class:`~mutwo.converters.frontends.ekmelily.HEJIEkmelilyTuningFileConverter`
argument `otonality_indicator`."""

DEFAULT_UTONALITY_INDICATOR = "u"
"""Default value for
:class:`~mutwo.converters.frontends.ekmelily.HEJIEkmelilyTuningFileConverter`
argument `utonality_indicator`."""

# solution from: https://stackoverflow.com/questions/23199733/convert-numbers-into-corresponding-letter-using-python
DEFAULT_EXPONENT_TO_EXPONENT_INDICATOR = lambda exponent: chr(ord("a") + exponent)
"""Default function for
:class:`~mutwo.converters.frontends.ekmelily.HEJIEkmelilyTuningFileConverter`
argument `exponent_to_exponent_indicator`."""

PYTHAGOREAN_ACCIDENTAL_CENT_DEVIATION_SIZE = round(
    (pitches.JustIntonationPitch((0, 7)).normalize(mutate=False).cents), 2  # type: ignore
)
"""Step in cents for one pythagorean accidental (# or b)."""

PYTHAGOREAN_ACCIDENTAL_TO_CENT_DEVIATIONS = {
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        fractions.Fraction(0, 1)
    ]: 0,
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        fractions.Fraction(1, 1)
    ]: PYTHAGOREAN_ACCIDENTAL_CENT_DEVIATION_SIZE,
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        fractions.Fraction(2, 1)
    ]: PYTHAGOREAN_ACCIDENTAL_CENT_DEVIATION_SIZE
    * 2,
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        -fractions.Fraction(1, 1)
    ]: -PYTHAGOREAN_ACCIDENTAL_CENT_DEVIATION_SIZE,
    pitches_constants.PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME[
        -fractions.Fraction(2, 1)
    ]: -2
    * PYTHAGOREAN_ACCIDENTAL_CENT_DEVIATION_SIZE,
}
"""Step in cents mapping for each pythagorean accidental (# or b)."""

DIFFERENCE_BETWEEN_PYTHAGOREAN_AND_TEMPERED_FIFTH = (
    pitches.JustIntonationPitch("3/2").cents - 700
)
"""The difference in cents between a just fifth (3/2) and
a 12-EDO fifth. This constant is used in
:class:`~mutwo.converters.frontends.ekmelily.HEJIEkmelilyTuningFileConverter`.
"""
