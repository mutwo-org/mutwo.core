"""Module for mutwo specific exceptions."""

from mutwo import parameters

__all__ = (
    "ValueNotAssignedError",
    "OverlappingTimeBracketsError",
    "SplitUnavailableChildError",
)


class ValueNotAssignedError(Exception):
    def __init__(self):
        super().__init__(
            "TimeBracket values haven't been assigned yet, run"
            " 'assign_concrete_times' method first"
        )


class OverlappingTimeBracketsError(Exception):
    def __init__(self):
        super().__init__("Found overlapping time brackets!")


class SplitUnavailableChildError(Exception):
    def __init__(self, absolute_time: parameters.abc.DurationType):
        super().__init__(
            f"Can't split child at absolute time '{absolute_time}'. There is no child"
            " event available at the requested time."
        )
