"""This file contains several flags for running csound.

The flag definitions are documented in
https://csound.com/docs/manual/CommandFlags.html
"""

SILENT_FLAG = '--no-displays'
"""Flag for preventing Csound from printing any information
during rendering."""

FORMAT_IRCAM = '--format=ircam'
"""Flag for rendering sound files in IRCAM format."""

FORMAT_24BIT = '--format=24bit'
"""Flag for rendering sound files in 24bit."""

FORMAT_64BIT = '--format=double'
"""Flag for rendering sound files in 64bit floating point."""

FORMAT_8BIT = '--format=uchar'
"""Flag for rendering sound files in 8bit."""

FORMAT_FLOAT = '--format=float'
"""Flag for rendering sound files in 8bit."""

FORMAT_WAV = '--format=wav'
"""Flag for rendering sound files in wav file format."""
