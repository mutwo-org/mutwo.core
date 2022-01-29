"""Module for mutwo specific exceptions."""

import typing

from mutwo import core_constants

__all__ = (
    "ValueNotAssignedError",
    "OverlappingTimeBracketsError",
    "SplitUnavailableChildError",
    "NoSolutionFoundError",
)


class ValueNotAssignedError(Exception):
    def __init__(self):
        super().__init__(
            "TimeBracket values haven't been assigned yet, run"
            " 'assign_concrete_times' method first"
        )


class OverlappingTimeBracketsError(Exception):
    def __init__(
        self,
        previous_end_time: typing.Optional[float] = None,
        start_time: typing.Optional[float] = None,
        time_bracket=None,
    ):
        message = "Found overlapping time brackets!"
        if previous_end_time and start_time:
            previous_end_time = round(previous_end_time / 60, 2)
            start_time = round(previous_end_time / 60, 2)
            message += f"\nThe end time of the previous time bracket is {previous_end_time}. The start time of the current time bracket is {start_time}."
        if time_bracket:
            message += f"\nThe problematic candidate is:\n{repr(time_bracket)[:50]}."
        super().__init__(message)


class SplitUnavailableChildError(Exception):
    def __init__(self, absolute_time: core_constants.DurationType):
        super().__init__(
            f"Can't split child at absolute time '{absolute_time}'. There is no child"
            " event available at the requested time."
        )


class NoSolutionFoundError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
