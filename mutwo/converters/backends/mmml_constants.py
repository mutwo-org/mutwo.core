"""Constants for :mod:`mutwo.converters.backends.mmml`."""

EVENT_IDENTIFIER = " "
"""Identifier for a new event."""

OCTAVE_IDENTIFIER = ":"
"""Identifier for indicating the octave."""

MULTIPLE_PITCHES_IDENTIFIER = ","
"""Identifier for multiple pitches (for writing chords)."""

RHYTHM_IDENTIFIER = "'"
"""Identifier for writing rhythms."""

DYNAMIC_IDENTIFIER = '"'
"""Identifier for writing dynamics."""

ATTRIBUTE_IDENTIFIER = r"/"
"""Identifier for setting attributes.
Inspired by Lilypond and Guido."""

ATTRIBUTE_ARGUMENT_START_IDENTIFIER = "<"
"""Identifier for setting arguments of attributes.
Inspired by Guido."""

ATTRIBUTE_ARGUMENT_END_IDENTIFIER = ">"
"""Identifier for setting arguments of attributes.
Inspired by Guido."""

VARIABLE_IDENTIFIER = "$"

REST_IDENTIFIER = "r"
"""Identifier for writing rests.
Inspired by Lilypond."""

COMMENT_IDENTIFIER = "#"
"""Identifier for writing comments.
Inspired by bash and scripting languages like Python, Perl, etc."""

JUST_INTONATION_POSITIVE_EXPONENT_IDENTIFIER = "+"
"""Identifier for positive exponent when using
:class:`mutwo.converters.backends.mmml.MMMLSingleJIPitchConverter`."""


JUST_INTONATION_NEGATIVE_EXPONENT_IDENTIFIER = "-"
"""Identifier for negative exponent when using
:class:`mutwo.converters.backends.mmml.MMMLSingleJIPitchConverter`."""
