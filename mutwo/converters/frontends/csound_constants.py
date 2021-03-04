"""Constants to be used for and with :mod:`mutwo.converters.frontends.csound`.

The file mostly contains different flags for running Csound.
The flag definitions are documented
`here <https://csound.com/docs/manual/CommandFlags.html>`_.
"""

SILENT_FLAG = "-O null"
"""Flag for preventing Csound from printing any information
while rendering."""

FORMAT_IRCAM = "--format=ircam"
"""Flag for rendering sound files in IRCAM format."""

FORMAT_24BIT = "--format=24bit"
"""Flag for rendering sound files in 24bit."""

FORMAT_64BIT = "--format=double"
"""Flag for rendering sound files in 64bit floating point."""

FORMAT_8BIT = "--format=uchar"
"""Flag for rendering sound files in 8bit."""

FORMAT_FLOAT = "--format=float"
"""Flag for rendering sound files in single-format float audio samples."""

FORMAT_WAV = "--format=wav"
"""Flag for rendering sound files in wav file format."""

SEQUENTIAL_EVENT_ANNOTATION = ";; NEW SEQUENTIAL EVENT\n;;"
"""Annotation in Csound Score files when a new :class:`SequentialEvent` starts."""

SIMULTANEOUS_EVENT_ANNOTATION = ";; NEW SIMULTANEOUS EVENT\n;;"
"""Annotation in Csound Score files when a new :class:`SimultaneousEvent` starts."""

N_EMPTY_LINES_AFTER_COMPLEX_EVENT = 1
"""How many empty lines shall be written to a Csound Score file after a :class:`ComplexEvent`."""
