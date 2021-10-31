"""Events which are defined by absolute start and end times.

Time brackets are events which are defined by their absolute start-
and end time. Furthermore start and end times don't have to be fixed
points but can also be ranges. In this way it is possible to model
Cage-like time brackets like in his late number pieces.
"""

import bisect
import statistics
import typing

import numpy as np  # type: ignore

from mutwo.events import abc as events_abc
from mutwo.events import basic
from mutwo.parameters import tempos
from mutwo.utilities import constants
from mutwo.utilities import exceptions

__all__ = (
    "TimeBracket",
    "TempoBasedTimeBracket",
    "TimeBracketContainer",
)


TimeRange = tuple[constants.Real, constants.Real]
TimeOrTimeRange = typing.Union[constants.Real, TimeRange]

T = typing.TypeVar("T", bound=events_abc.Event)


class TimeBracket(basic.SimultaneousEvent):
    """:class:`SimultaneousEvent` with a specified start and end point.

    :param tagged_event_or_tagged_events:
    :param start_or_start_range:
    :param end_or_end_range:
    :param seed:
    :param force_spanning_of_end_or_end_range:
    """

    _class_specific_side_attributes = (
        "start_or_start_range",
        "end_or_end_range",
        "seed",
        "force_spanning_of_end_or_end_range",
    )

    def __init__(
        self,
        tagged_event_or_tagged_events: typing.Sequence[
            typing.Union[
                basic.TaggedSimpleEvent,
                basic.TaggedSequentialEvent,
                basic.TaggedSimultaneousEvent,
            ]
        ],
        start_or_start_range: TimeOrTimeRange,
        end_or_end_range: TimeOrTimeRange,
        seed: typing.Optional[int] = None,
        force_spanning_of_end_or_end_range: bool = True,
    ):
        super().__init__(tagged_event_or_tagged_events)
        self.start_or_start_range = start_or_start_range
        self.end_or_end_range = end_or_end_range

        time_bracket_random = np.random.default_rng(seed)
        self.force_spanning_of_end_or_end_range = force_spanning_of_end_or_end_range

        self._seed = seed
        self._time_bracket_random = time_bracket_random

    # ###################################################################### #
    #                           static methods                               #
    # ###################################################################### #

    @staticmethod
    def _get_mean_of_value_or_value_range(
        value_or_value_range: typing.Union[
            constants.Real, tuple[constants.Real, constants.Real]
        ],
    ) -> constants.Real:
        if isinstance(value_or_value_range, typing.Sequence):
            return statistics.mean(value_or_value_range)
        else:
            return value_or_value_range

    @staticmethod
    def _get_extrema_of_value_or_value_range(
        value_or_value_range: TimeOrTimeRange,
        operation: typing.Callable[[typing.Sequence], constants.Real],
    ):
        if isinstance(value_or_value_range, typing.Sequence):
            return operation(value_or_value_range)
        else:
            return value_or_value_range

    @staticmethod
    def _get_flexible_range_of_value_or_value_range(
        value_or_value_range: TimeOrTimeRange,
    ) -> float:
        if isinstance(value_or_value_range, typing.Sequence):
            return value_or_value_range[1] - value_or_value_range[0]
        else:
            return 0

    @staticmethod
    def _delay_value_or_value_range(
        value_or_value_range: TimeOrTimeRange, delay: constants.Real
    ) -> TimeOrTimeRange:
        if isinstance(value_or_value_range, typing.Sequence):
            return tuple(map(lambda value: value + delay, value_or_value_range))
        else:
            return value_or_value_range + delay

    @staticmethod
    def _extend_or_shrink_value_or_value_range(
        value_or_value_range: TimeOrTimeRange,
        difference: float,
        direction: typing.Literal["right", "left"],
    ) -> TimeOrTimeRange:
        if not isinstance(value_or_value_range, typing.Sequence):
            value_or_value_range = (value_or_value_range, value_or_value_range)

        new_value_or_value_range = list(value_or_value_range)
        if direction == "right":
            index = 1
        elif direction == "left":
            index = 0
        else:
            raise NotImplementedError(f"Unknown direction {direction}!")

        new_value_or_value_range[index] += difference

        if new_value_or_value_range[0] == new_value_or_value_range[1]:
            new_value_or_value_range = new_value_or_value_range[0]
        else:
            new_value_or_value_range = tuple(new_value_or_value_range)

        return new_value_or_value_range

    # ###################################################################### #
    #                           private methods                              #
    # ###################################################################### #

    def _assign_concrete_time(
        self, time_or_time_range: TimeOrTimeRange
    ) -> constants.Real:
        if hasattr(time_or_time_range, "__getitem__"):
            return self._time_bracket_random.uniform(*time_or_time_range)
        else:
            return time_or_time_range

    # ###################################################################### #
    #                         public properties                              #
    # ###################################################################### #

    @property
    def start_or_start_range(self) -> TimeOrTimeRange:
        return self._start_or_start_range

    @start_or_start_range.setter
    def start_or_start_range(self, start_or_start_range: TimeOrTimeRange):
        self._start_or_start_range = start_or_start_range
        if hasattr(self, "_assigned_start_time"):
            self.assign_concrete_times()

    @property
    def end_or_end_range(self) -> TimeOrTimeRange:
        return self._end_or_end_range

    @end_or_end_range.setter
    def end_or_end_range(self, end_or_end_range: TimeOrTimeRange):
        self._end_or_end_range = end_or_end_range
        if hasattr(self, "_assigned_end_time"):
            self.assign_concrete_times()

    @property
    def mean_start(self) -> constants.Real:
        return TimeBracket._get_mean_of_value_or_value_range(self.start_or_start_range)

    @property
    def mean_end(self) -> constants.Real:
        return TimeBracket._get_mean_of_value_or_value_range(self.end_or_end_range)

    @property
    def minimal_start(self) -> constants.Real:
        return TimeBracket._get_extrema_of_value_or_value_range(
            self.start_or_start_range, min
        )

    @property
    def maximum_end(self) -> constants.Real:
        return TimeBracket._get_extrema_of_value_or_value_range(
            self.end_or_end_range, max
        )

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

    @property
    def seed(self) -> typing.Optional[int]:
        return self._seed

    @property
    def as_active_event(self) -> basic.SequentialEvent[basic.SimpleEvent]:
        as_active_event = basic.SequentialEvent([])
        start, end = self.minimal_start, self.maximum_end
        if start > 0:
            inactive_event = basic.SimpleEvent(start)
            inactive_event.is_active = False
            as_active_event.append(inactive_event)
        active_event = basic.SimpleEvent(end - start)
        active_event.is_active = True
        as_active_event.append(active_event)
        return as_active_event

    @property
    def flexible_start_range(self) -> float:
        return TimeBracket._get_flexible_range_of_value_or_value_range(
            self.start_or_start_range
        )

    @flexible_start_range.setter
    def flexible_start_range(self, new_flexible_start_range: float):
        assert new_flexible_start_range >= 0
        difference = new_flexible_start_range - self.flexible_start_range
        self.start_or_start_range = self._extend_or_shrink_value_or_value_range(
            self.start_or_start_range, difference, "right"
        )

    @property
    def flexible_end_range(self) -> float:
        return TimeBracket._get_flexible_range_of_value_or_value_range(
            self.end_or_end_range
        )

    @flexible_end_range.setter
    def flexible_end_range(self, new_flexible_end_range: float):
        assert new_flexible_end_range >= 0
        difference = self.flexible_end_range - new_flexible_end_range
        self.end_or_end_range = self._extend_or_shrink_value_or_value_range(
            self.end_or_end_range, difference, "left"
        )

    # ###################################################################### #
    #                          public methods                                #
    # ###################################################################### #

    def assign_concrete_times(self):
        """Assign concrete values for start and end time"""

        self._assigned_start_time = self._assign_concrete_time(
            self.start_or_start_range
        )
        self._assigned_end_time = self._assign_concrete_time(self.end_or_end_range)

    def is_overlapping_with_other(self, other: "TimeBracket") -> bool:
        as_active_event = self.as_active_event
        as_active_event.cut_out(other.minimal_start, other.maximum_end)
        if as_active_event:
            for event in as_active_event:
                if event.is_active:
                    return True
        return False

    def delay(self, value: constants.Real):
        self._start_or_start_range = self._delay_value_or_value_range(
            self.start_or_start_range, value
        )
        self._end_or_end_range = self._delay_value_or_value_range(
            self.end_or_end_range, value
        )


class TempoBasedTimeBracket(TimeBracket, typing.Generic[T]):
    _class_specific_side_attributes = TimeBracket._class_specific_side_attributes + (
        "tempo",
    )

    def __init__(
        self,
        tagged_event_or_tagged_events: typing.Sequence[
            typing.Union[
                basic.TaggedSimpleEvent,
                basic.TaggedSequentialEvent,
                basic.TaggedSimultaneousEvent,
            ]
        ],
        start_or_start_range: TimeOrTimeRange,
        end_or_end_range: TimeOrTimeRange,
        tempo: typing.Union[constants.Real, tempos.TempoPoint],
        seed: typing.Optional[int] = None,
        force_spanning_of_end_or_end_range: bool = False,
    ):
        self.tempo = tempo
        super().__init__(
            tagged_event_or_tagged_events,
            start_or_start_range,
            end_or_end_range,
            seed,
            force_spanning_of_end_or_end_range,
        )


class TimeBracketContainer(object):
    def __init__(self, time_brackets: typing.Sequence[TimeBracket]):
        self._time_brackets = basic.SequentialEvent(time_brackets)
        self._resort()

    def _resort(self):
        self._time_brackets.sort(key=lambda bracket: bracket.mean_start)

    def __repr__(self) -> str:
        return "BracketContainer({})".format(tuple(self._time_brackets))

    def __iter__(self):
        return iter(self._time_brackets)

    def __getitem__(self, index: int) -> TimeBracket:
        return self._time_brackets[index]

    def _test_for_overlaying_brackets(
        self,
        time_bracket_to_test: TimeBracket,
        tags_to_analyse: typing.Optional[tuple[str, ...]],
    ):
        def get_tags_of_bracket(
            bracket_from_which_to_extract_tags: TimeBracket,
        ) -> tuple[str, ...]:
            return tuple(
                tagged_event.tag for tagged_event in bracket_from_which_to_extract_tags
            )

        # check for overlapping brackets before registering the new one
        if not tags_to_analyse:
            tags_to_analyse = get_tags_of_bracket(time_bracket_to_test)
        for registered_bracket in self._time_brackets:
            registered_bracket_tags = get_tags_of_bracket(registered_bracket)
            is_tag_in_other_tags = tuple(
                tag in tags_to_analyse for tag in registered_bracket_tags
            )
            if any(is_tag_in_other_tags):
                if registered_bracket.is_overlapping_with_other(time_bracket_to_test):
                    raise exceptions.OverlappingTimeBracketsError()

    def register(
        self,
        time_bracket_to_register: TimeBracket,
        test_for_overlapping_brackets: bool = True,
        tags_to_analyse: typing.Optional[tuple[str, ...]] = None,
    ):
        """Add new bracket to :class`TimeBracketContainer`.

        :param time_bracket_to_register: The :class:`TimeBracket`
            which shall be added.
        :type time_bracket_to_register: TimeBracket
        :param test_for_overlapping_brackets: Set to ``True``
            if mutwo shall check if the new :class:`TimeBracket`
            overlaps with any :class:`TimeBracket` in the
            :class:`TimeBracketContainer`.
        :type test_for_overlapping_brackets: bool
        :param tags_to_analyse:
        :type tags_to_analyse:
        """

        if test_for_overlapping_brackets:
            self._test_for_overlaying_brackets(
                time_bracket_to_register, tags_to_analyse
            )

        start_of_brackets = tuple(bracket.mean_start for bracket in self._time_brackets)
        index = bisect.bisect_left(
            start_of_brackets, time_bracket_to_register.mean_start
        )
        self._time_brackets.insert(index, time_bracket_to_register)

    def filter(self, tag: str) -> tuple[TimeBracket, ...]:
        """Filter and return all brackets which contain events with the requested tag

        :param tag: The tag which shall be investigated.
        :type tag: str
        """

        filtered_brackets = []
        for bracket in self._time_brackets:
            for tagged_event in bracket:
                if tagged_event.tag == tag:
                    filtered_brackets.append(bracket)
                    break

        return tuple(filtered_brackets)

    def delay(
        self,
        value: constants.Real,
        start: typing.Optional[constants.Real] = None,
        end: typing.Optional[constants.Real] = None,
        time_bracket_to_time_bracket_time: typing.Callable[
            [TimeBracket], constants.Real
        ] = lambda time_bracket: time_bracket.minimal_start,
    ):
        """Delay all time brackets in area from start to end by value.

        :param value:
        :type value:
        :param start:
        :type start:
        :param end:
        :type end:
        :param time_bracket_to_time_bracket_time:
        :type time_bracket_to_time_bracket_time:

        **WARNING**: This function is not safe (wrong usage could create
            overlapping time brackets with the same tags).
        """

        if not start:
            start = 0

        if not end:
            end = self[-1].maximum_end

        for time_bracket in self:
            time_bracket_time = time_bracket_to_time_bracket_time(time_bracket)
            if time_bracket_time >= start and time_bracket_time <= end:
                time_bracket.delay(value)

        self._resort()
