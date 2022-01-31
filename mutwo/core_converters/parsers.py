"""Standardised way to extract data from simple events."""

import typing

from mutwo import core_converters
from mutwo import core_events
from mutwo import core_utilities


__all__ = ("SimpleEventToAttribute",)


class SimpleEventToAttribute(core_converters.abc.Converter):
    """Extract from a simple event an attribute.

    :param attribute_name: The name of the attribute which is fetched
        from a :class:`mutwo.core_events.SimpleEvent`.
    :param exception_value: This value is returned in case an `AttributeError`
        raises .
    """

    def __init__(self, attribute_name: str, exception_value: typing.Any):
        self._attribute_name = attribute_name
        self._exception_value = exception_value

    def convert(self, simple_event_to_convert: core_events.SimpleEvent) -> typing.Any:
        return core_utilities.call_function_except_attribute_error(
            lambda simple_event: getattr(simple_event, self._attribute_name),
            simple_event_to_convert,
            self._exception_value,
        )
