"""Module for mutwo specific exceptions."""

from mutwo import core_constants

__all__ = (
    "AlreadyDefinedValueNameError",
    "InvalidAverageValueStartAndEndWarning",
    "InvalidStartValueError",
    "InvalidPointError",
    "ImpossibleToSquashInError",
    "InvalidStartAndEndValueError",
    "InvalidCutOutStartAndEndValuesError",
    "SplitUnavailableChildError",
    "NoSolutionFoundError",
)


class AlreadyDefinedValueNameError(Exception):
    def __init__(self, cls):
        super().__init__(
            f"Confusing setup in class '{cls}' which inherits from "
            "'SingleValueParameter'. Found already a defined value for"
            " 'value_name'. SingleValueParameter instances can only "
            "have one value!"
        )


class InvalidStartValueError(Exception):
    def __init__(
        self,
        start,
        duration,
    ):
        super().__init__(
            f"Invalid value for start = '{start}' in 'squash_in' call "
            f"for event with duration = '{duration}'!"
            " Start has to be equal or smaller than the events duration."
        )


class InvalidAverageValueStartAndEndWarning(RuntimeWarning):
    def __init__(self):
        super().__init__(
            "Average value for range where start == end is equal to"
            " envelope.value_at(start)!"
        )


class InvalidPointError(Exception):
    def __init__(self, point, point_count):
        super().__init__(
            f"Found invalid point: '{point}' with {point_count} "
            "items! Points should have two or three items."
        )


class ImpossibleToSquashInError(TypeError):
    def __init__(self, event_to_be_squashed_into, event_to_squash_in):
        super().__init__(
            f"Can't squash '{event_to_squash_in}' in '{event_to_be_squashed_into}'. "
            "Does the SimultaneousEvent contain SimpleEvents or events that inherit"
            " from SimpleEvent? For being able to squash in, the"
            " SimultaneousEvent needs to only contain SequentialEvents or"
            " SimultaneousEvents."
        )


class InvalidStartAndEndValueError(Exception):
    def __init__(self, start, end):
        super().__init__(
            f"Invalid values for start and end property (start = '{start}' "
            f"and end = '{end}')!"
            " Value for 'end' has to be bigger than value for 'start'."
        )


class InvalidCutOutStartAndEndValuesError(Exception):
    def __init__(self, start, end, simple_event, duration):
        super().__init__(
            f"Can't cut out SimpleEvent '{simple_event}' with "
            f"duration '{duration}' from"
            f" (start = {start} to end = {end})."
        )


class SplitUnavailableChildError(Exception):
    def __init__(self, absolute_time: core_constants.DurationType):
        super().__init__(
            f"Can't split child at absolute time '{absolute_time}'. There is no child"
            " event available at the requested time."
        )


class NoSolutionFoundError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
