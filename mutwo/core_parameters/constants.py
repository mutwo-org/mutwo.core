import typing

import ranges

TempoInBeatsPerMinute = float
TempoRangeInBeatsPerMinute = ranges.Range
TempoOrTempoRangeInBeatsPerMinute = typing.Union[
    TempoInBeatsPerMinute, TempoRangeInBeatsPerMinute
]

del ranges, typing
