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

MINIMUM_DECIBEL_FOR_STANDARD_DYNAMIC_INDICATOR: float = -52
"""decibel value for lowest dynamic indicator ('ppppp')"""

MAXIMUM_DECIBEL_FOR_STANDARD_DYNAMIC_INDICATOR: float = 0
"""decibel value for highest dynamic indicator ('fffff')"""

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
