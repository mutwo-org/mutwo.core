import typing

TempoInBeatsPerMinute = float
TempoRangeInBeatsPerMinute = tuple[TempoInBeatsPerMinute, TempoInBeatsPerMinute]
TempoOrTempoRangeInBeatsPerMinute = typing.Union[
    TempoInBeatsPerMinute, TempoRangeInBeatsPerMinute
]

del typing
