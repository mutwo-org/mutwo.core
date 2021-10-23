import typing


from mutwo import converters
from mutwo import events
from mutwo import parameters

__all__ = ("ReaperMarkerConverter",)


class ReaperMarkerConverter(converters.abc.EventConverter):
    """Make Reaper Marker entries."""

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
    ) -> typing.Tuple[str, ...]:
        try:
            marker_name = self._simple_event_to_marker_name(simple_event)
            marker_color = self._simple_event_to_marker_color(simple_event)
        except AttributeError:
            return tuple([])

        return ("{} {} {}".format(absolute_entry_delay, marker_name, marker_color),)

    def convert(self, event_to_convert: events.abc.Event) -> str:
        reaper_marker = tuple(
            "MARKER {} {}".format(nth_marker, marker_data)
            for nth_marker, marker_data in enumerate(
                self._convert_event(event_to_convert, 0)
            )
        )
        return "\n".join(reaper_marker)
