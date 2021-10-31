"""Convert mutwo data to data readable by the `Reaper DAW <reaper.fm/>`_."""

import typing


from mutwo import converters
from mutwo import events
from mutwo import parameters

__all__ = ("ReaperMarkerConverter",)


class ReaperMarkerConverter(converters.abc.EventConverter):
    """Make Reaper Marker entries.

    :param simple_event_to_marker_name: A function which converts a
        :class:`~mutwo.events.basic.SimpleEvent` to the marker
        name. By default the function will ask the event for its
        `name` property. If the event doesn't know the `name`
        property (and the function call will result in an ``AttributeError``)
        mutwo will ignore the current event.
    :type simple_event_to_marker_name: typing.Callable[[events.basic.SimpleEvent], str]
    :param simple_event_to_marker_color: A function which converts a
        :class:`~mutwo.events.basic.SimpleEvent` to the marker
        color. By default the function will ask the event for its
        `color` property. If the event doesn't know the `color`
        property (and the function call will result in an ``AttributeError``)
        mutwo will ignore the current event.
    :type simple_event_to_marker_color: typing.Callable[[events.basic.SimpleEvent], str]

    The resulting string can be copied into the respective reaper
    project file one line before the '<PROJBAY' tag.

    **Example:**

    >>> from mutwo.converters.frontends import reaper
    >>> from mutwo.events import basic
    >>> marker_converter = reaper.ReaperMarkerConverter()
    >>> events = basic.SequentialEvent([basic.SimpleEvent(2), basic.SimpleEvent(3)])
    >>> events[0].name = 'beginning'
    >>> events[0].color = r'0 16797088 1 B {A4376701-5AA5-246B-900B-28ABC969123A}'
    >>> events[1].name = 'center'
    >>> events[1].color = r'0 18849803 1 B {E4DD7D23-98F4-CA97-8587-F4259A9498F7}'
    >>> marker_converter.convert(events)
    'MARKER 0 0 beginning 0 16797088 1 B {A4376701-5AA5-246B-900B-28ABC969123A}\nMARKER 1 2 center 0 18849803 1 B {E4DD7D23-98F4-CA97-8587-F4259A9498F7}'
    """

    def __init__(
        self,
        simple_event_to_marker_name: typing.Callable[
            [events.basic.SimpleEvent], str
        ] = lambda simple_event: simple_event.name,  # type: ignore
        simple_event_to_marker_color: typing.Callable[
            [events.basic.SimpleEvent], str
        ] = lambda simple_event: simple_event.color,  # type: ignore
    ):
        self._simple_event_to_marker_name = simple_event_to_marker_name
        self._simple_event_to_marker_color = simple_event_to_marker_color

    def _convert_simple_event(
        self,
        simple_event: events.basic.SimpleEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> tuple[str, ...]:
        try:
            marker_name = self._simple_event_to_marker_name(simple_event)
            marker_color = self._simple_event_to_marker_color(simple_event)
        except AttributeError:
            return tuple([])

        return ("{} {} {}".format(absolute_entry_delay, marker_name, marker_color),)

    def convert(self, event_to_convert: events.abc.Event) -> str:
        """Convert event to reaper markers (as plain string).

        :param event_to_convert: The event which shall be
            converted to reaper marker entries.
        :type event_to_convert: events.abc.Event
        :return: The reaper marker entries as plain strings.
            Copy them to your reaper project file one line
            before the '<PROJBAY' tag and the next time when
            you open the project they will appear.
        :return type: str
        """

        reaper_marker = tuple(
            "MARKER {} {}".format(nth_marker, marker_data)
            for nth_marker, marker_data in enumerate(
                self._convert_event(event_to_convert, 0)
            )
        )
        return "\n".join(reaper_marker)
