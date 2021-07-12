"""Module for Cage-like time brackets.

Time brackets are events which are defined by unspecified start and end times.
"""

import typing

from mutwo.events import basic
from mutwo.events import brackets
from mutwo.utilities import constants
from mutwo.utilities import exceptions

__all__ = (
    "TimeBracket",
    "TimeBracketContainer",
)


TimeOrTimeRange = typing.Union[
    constants.Real, typing.Tuple[constants.Real, constants.Real]
]


class TimeBracket(brackets.Bracket):
    def __init__(
        self,
        tagged_events: typing.Sequence[
            typing.Union[
                basic.TaggedSimpleEvent,
                basic.TaggedSequentialEvent,
                basic.TaggedSimultaneousEvent,
            ]
        ],
        start_or_start_range: TimeOrTimeRange,
        end_or_end_range: TimeOrTimeRange,
        seed: typing.Optional[int] = None,
    ):
        super().__init__(tagged_events, start_or_start_range, end_or_end_range)

        import random as time_bracket_random

        if seed:
            time_bracket_random.seed(seed)
        self._time_bracket_random = time_bracket_random

    def _assign_concrete_time(
        self, time_or_time_range: TimeOrTimeRange
    ) -> constants.Real:
        if hasattr(time_or_time_range, "__getitem__"):
            return self._time_bracket_random.uniform(*time_or_time_range)
        else:
            return time_or_time_range

    @brackets.Bracket.start_or_start_range.setter
    def start_or_start_range(self, start_or_start_range: TimeOrTimeRange):
        self._start_or_start_range = start_or_start_range
        if hasattr(self, "_assigned_start_time"):
            self.assign_concrete_times()

    @brackets.Bracket.end_or_end_range.setter
    def end_or_end_range(self, end_or_end_range: TimeOrTimeRange):
        self._end_or_end_range = end_or_end_range
        if hasattr(self, "_assigned_end_time"):
            self.assign_concrete_times()

    @property
    def mean_start(self) -> constants.Real:
        return brackets.Bracket._get_mean_of_value_or_value_range(
            self.start_or_start_range
        )

    @property
    def mean_end(self) -> constants.Real:
        return TimeBracket._get_mean_of_value_or_value_range(self.end_or_end_range)

    @property
    def duration(self) -> constants.Real:
        return self.mean_end - self.mean_start

    @property
    def assigned_start_time(self) -> constants.Real:
        try:
            return self._assigned_start_time
        except AttributeError:
            raise exceptions.ValueNotAssignedError()

    @property
    def assigned_end_time(self) -> constants.Real:
        try:
            return self._assigned_end_time
        except AttributeError:
            raise exceptions.ValueNotAssignedError()

    def assign_concrete_times(self):
        """Assign concrete values for start and end time"""

        self._assigned_start_time = self._assign_concrete_time(
            self.start_or_start_range
        )
        self._assigned_end_time = self._assign_concrete_time(self.end_or_end_range)


class TimeBracketContainer(brackets.BracketContainer[TimeBracket]):
    pass
