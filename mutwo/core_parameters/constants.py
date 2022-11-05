import typing

import ranges

TempoInBeatsPerMinute = float
"""Type alias for `TempoInBeatsPerMinute`. Used in
`core_parameters.abc.TempoPoint`"""

TempoRangeInBeatsPerMinute = ranges.Range
"""Type alias for `TempoRangeInBeatsPerMinute`. Used in
`core_parameters.abc.TempoPoint`"""

TempoOrTempoRangeInBeatsPerMinute = typing.Union[
    TempoInBeatsPerMinute, TempoRangeInBeatsPerMinute
]
"""Type alias for `TempoOrTempoRangeInBeatsPerMinute`. Used in
`core_parameters.abc.TempoPoint`"""

# Cleanup
del ranges, typing
