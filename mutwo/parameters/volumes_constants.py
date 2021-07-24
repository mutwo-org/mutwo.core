"""This module adds several constants that are used for the different volume classes.

"""

MINIMUM_VELOCITY = 0
"""the lowest allowed midi velocity value"""

MAXIMUM_VELOCITY = 127
"""the highest allowed midi velocity value"""

# standard volume indicator
STANDARD_DYNAMIC_INDICATOR = tuple(
    "ppppp pppp ppp pp p mp mf f ff fff ffff fffff".split(" ")
)

DEFAULT_MINIMUM_DECIBEL_FOR_MIDI_VELOCITY_AND_STANDARD_DYNAMIC_INDICATOR: float = -40
"""Default value for ``minimum_decibel`` in
:class:`~mutwo.parameter.volumes.WesternVolume` and in
:method:`~mutwo.parameters.abc.Volume.decibel_to_midi_velocity`."""

DEFAULT_MAXIMUM_DECIBEL_FOR_MIDI_VELOCITY_AND_STANDARD_DYNAMIC_INDICATOR: float = 0
"""Default value for ``maximum_decibel`` in
:class:`~mutwo.parameter.volumes.WesternVolume` and in
:method:`~mutwo.parameters.abc.Volume.decibel_to_midi_velocity`."""


SPECIAL_DYNAMIC_INDICATOR_TO_STANDARD_DYNAMIC_INDICATOR_MAPPING = {
    "fp": "mf",
    "sf": "f",
    "sff": "ff",
    "sfz": "ff",
    "sp": "p",
    "spp": "pp",
    "rfz": "f",
}

DYNAMIC_INDICATOR = STANDARD_DYNAMIC_INDICATOR + tuple(
    SPECIAL_DYNAMIC_INDICATOR_TO_STANDARD_DYNAMIC_INDICATOR_MAPPING.keys()
)
"""all available dynamic indicator for :class:`WesternVolume`"""
