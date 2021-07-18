"""Convert :class:`mutwo.events.time_brackets.TimeBracket` to other data structures."""

import bisect
import itertools
import typing

import expenvelope  # type: ignore
import numpy as np  # type: ignore

from mutwo.converters import abc as converters_abc
from mutwo import events
from mutwo import parameters
from mutwo.utilities import constants
from mutwo.utilities import exceptions

__all__ = (
    "TimeBracketsToEventConverter",
    "EventToProbabilityCurveConverter",
)


class TimeBracketsToEventConverter(converters_abc.Converter):
    """Convert time bracket to events.basic.events.

    :param tag: Events with this tag will be extracted and converted.
    """

    def __init__(self, tag: str):
        self._tag = tag

    @staticmethod
    def _get_start_and_end_time(
        time_bracket: events.time_brackets.TimeBracket,
    ) -> typing.Tuple[constants.Real, constants.Real]:
        try:
            return (
                time_bracket.assigned_start_time,
                time_bracket.assigned_end_time,
            )
        except exceptions.ValueNotAssignedError:
            time_bracket.assign_concrete_times()
            return TimeBracketsToEventConverter._get_start_and_end_time(time_bracket)

    def _extract_tagged_event(
        self,
        events: typing.Sequence[
            typing.Union[
                events.basic.TaggedSimpleEvent,
                events.basic.TaggedSequentialEvent,
                events.basic.TaggedSimultaneousEvent,
            ]
        ],
    ) -> typing.Union[
        events.basic.TaggedSimpleEvent,
        events.basic.TaggedSequentialEvent,
        events.basic.TaggedSimultaneousEvent,
    ]:
        for tagged_event in events:
            if tagged_event.tag == self._tag:
                return tagged_event

        raise NotImplementedError(f"Couldn't find instrument '{self._tag}' in bracket.")

    def convert(
        self,
        time_brackets_to_convert: typing.Sequence[events.time_brackets.TimeBracket],
    ) -> typing.Tuple[
        typing.Union[
            events.basic.TaggedSimpleEvent,
            events.basic.TaggedSequentialEvent,
            events.basic.TaggedSimultaneousEvent,
        ],
        ...,
    ]:
        converted_events = []
        previous_end_time = 0
        for time_bracket in time_brackets_to_convert:
            (
                start_time,
                end_time,
            ) = TimeBracketsToEventConverter._get_start_and_end_time(time_bracket)

            # add rest if there is time between last time bracket and current bracket
            if previous_end_time < start_time:
                converted_events.append(
                    events.basic.TaggedSimpleEvent(
                        start_time - previous_end_time, tag=self._tag
                    )
                )
            # raise error if last bracket is still running while the current
            # time bracket already started
            elif previous_end_time > start_time:
                raise exceptions.OverlappingTimeBracketsError()

            duration_in_seconds = end_time - start_time
            tagged_event = self._extract_tagged_event(
                tuple(time_bracket)
            ).destructive_copy()
            tagged_event.duration = duration_in_seconds
            converted_events.append(tagged_event)

            previous_end_time = end_time

        return tuple(converted_events)


class EventToProbabilityCurveConverter(converters_abc.EventConverter):
    def __init__(
        self,
        start_or_start_range: events.time_brackets.TimeOrTimeRange,
        end_or_end_range: events.time_brackets.TimeOrTimeRange,
        time_grid: float = 0.5,
        precision: int = 45,
    ):
        self._time_grid = time_grid
        self._possible_start_times = EventToProbabilityCurveConverter._get_possible_times_range(
            precision, start_or_start_range
        )
        self._possible_end_times = EventToProbabilityCurveConverter._get_possible_times_range(
            precision, end_or_end_range
        )
        self._init_grid(start_or_start_range[0], end_or_end_range[1])

    def _init_grid(self, start, end):
        self._grid_size = int((end - start) // self._time_grid)
        self._grid = np.linspace(start, end, self._grid_size)

    @staticmethod
    def _get_possible_times_range(
        precision: int, time_or_time_range: events.time_brackets.TimeOrTimeRange
    ) -> typing.Tuple[float, ...]:
        try:
            possible_times = tuple(
                np.linspace(*time_or_time_range, num=precision, dtype=float)
            )
        except TypeError:
            possible_times = (time_or_time_range,)
        return possible_times

    def _get_probability_array_for_event(
        self,
        event_to_convert: events.basic.SimpleEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> typing.Tuple[
        typing.Tuple[parameters.abc.DurationType, parameters.abc.DurationType]
    ]:
        start_and_end_times = np.array(
            [absolute_entry_delay, absolute_entry_delay + event_to_convert.duration]
        )

        probability_array = np.zeros(self._grid_size)
        for start_time, end_time in itertools.product(
            self._possible_start_times, self._possible_end_times
        ):
            if start_time < end_time:
                start_of_event, end_of_event = np.interp(
                    start_and_end_times,
                    (0, self._duration_of_event_to_convert),
                    (start_time, end_time),
                )
                start_index, end_index = tuple(
                    bisect.bisect_left(self._grid, position_of_event)
                    for position_of_event in (start_of_event, end_of_event)
                )
                probability_array[start_index:end_index] += 1

        # scale probability array
        probability_array = np.interp(
            probability_array, (0, np.max(probability_array)), (0, 1)
        )
        return probability_array

    def _convert_simple_event(
        self,
        event_to_convert: events.basic.SimpleEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> typing.Sequence[typing.Any]:
        """Convert instance of :class:`mutwo.events.events.basic.SimpleEvent`.

        This method calculates the probability curve for a simple event. A higher number
        in the curve means that it is more likely that the converted event is active at
        the respective moment on the time line.
        """

        probability_array = self._get_probability_array_for_event(
            event_to_convert, absolute_entry_delay
        )

        probability_curve = expenvelope.Envelope.from_points(
            *tuple((time, value) for time, value in zip(self._grid, probability_array)),
        )
        return (probability_curve,)

    def convert(self, event_to_convert: events.abc.Event) -> typing.Any:
        self._duration_of_event_to_convert = event_to_convert.duration
        probability_curves = self._convert_event(event_to_convert, 0)
        return probability_curves
