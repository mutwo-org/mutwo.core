"""This module adds several constants that are used for the different volume classes.

"""

import numpy as np

MINIMUM_VELOCITY = 0
"""the lowest allowed midi velocity value"""

MAXIMUM_VELOCITY = 127
"""the highest allowed midi velocity value"""

# standard volume indicator
_dynamic_indicators = "ppppp pppp ppp pp p mp mf f ff fff ffff fffff".split(" ")
_min_decibel, _max_decibel = -52, 0
STANDARD_DYNAMIC_INDICATOR_TO_DECIBEL = {
    dynamic_indicator: decibel
    for dynamic_indicator, decibel in zip(
        _dynamic_indicators,
        np.linspace(_min_decibel, _max_decibel, len(_dynamic_indicators), dtype=float),
    )
}

# special volume indicator
SPECIAL_DYNAMIC_INDICATOR_TO_DECIBEL = {
    "fp": STANDARD_DYNAMIC_INDICATOR_TO_DECIBEL["mf"],
    "sf": STANDARD_DYNAMIC_INDICATOR_TO_DECIBEL["f"],
    "sff": STANDARD_DYNAMIC_INDICATOR_TO_DECIBEL["ff"],
    "sfz": STANDARD_DYNAMIC_INDICATOR_TO_DECIBEL["ff"],
    "sp": STANDARD_DYNAMIC_INDICATOR_TO_DECIBEL["p"],
    "spp": STANDARD_DYNAMIC_INDICATOR_TO_DECIBEL["pp"],
    "rfz": STANDARD_DYNAMIC_INDICATOR_TO_DECIBEL["f"],
}

DYNAMIC_INDICATOR_TO_DECIBEL = dict(**STANDARD_DYNAMIC_INDICATOR_TO_DECIBEL)
DYNAMIC_INDICATOR_TO_DECIBEL.update(SPECIAL_DYNAMIC_INDICATOR_TO_DECIBEL)

DECIBEL_TO_STANDARD_DYNAMIC_INDICATOR = {
    value: key for key, value in STANDARD_DYNAMIC_INDICATOR_TO_DECIBEL.items()
}

del _dynamic_indicators, np
