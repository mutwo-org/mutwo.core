"""Module for mutwo specific exceptions."""

__all__ = (
    "ValueNotAssignedError",
    "OverlappingTimeBracketsError",
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
