"""Routines to convert time brackets to basic events."""

import typing

from mutwo.converters import abc as converters_abc
from mutwo.events import basic
from mutwo.events import time_brackets
from mutwo.utilities import constants
from mutwo.utilities import exceptions

__all__ = ("TimeBracketsToEventConverter",)


class TimeBracketsToEventConverter(converters_abc.Converter):
    """Convert time bracket to basic events.

    :param tag: Events with this tag will be extracted and converted.
    """

    def __init__(self, tag: str):
        self._tag = tag

    @staticmethod
    def _get_start_and_end_time(
        time_bracket: time_brackets.TimeBracket,
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
                basic.TaggedSimpleEvent,
                basic.TaggedSequentialEvent,
                basic.TaggedSimultaneousEvent,
            ]
        ],
    ) -> typing.Union[
        basic.TaggedSimpleEvent,
        basic.TaggedSequentialEvent,
        basic.TaggedSimultaneousEvent,
    ]:
        for tagged_event in events:
            if tagged_event.tag == self._tag:
                return tagged_event

        raise NotImplementedError(f"Couldn't find instrument '{self._tag}' in bracket.")

    def convert(
        self, time_brackets_to_convert: typing.Sequence[time_brackets.TimeBracket]
    ) -> typing.Tuple[
        typing.Union[
            basic.TaggedSimpleEvent,
            basic.TaggedSequentialEvent,
            basic.TaggedSimultaneousEvent,
        ],
        ...,
    ]:
        events = []
        previous_end_time = 0
        for time_bracket in time_brackets_to_convert:
            (
                start_time,
                end_time,
            ) = TimeBracketsToEventConverter._get_start_and_end_time(time_bracket)

            # add rest if there is time between last time bracket and current bracket
            if previous_end_time < start_time:
                events.append(
                    basic.TaggedSimpleEvent(
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
            events.append(tagged_event)

            previous_end_time = end_time

        return tuple(events)
