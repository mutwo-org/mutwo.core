import typing

import rpp  # type: ignore

from mutwo.converters.frontends import reaper_constants

from mutwo import converters
from mutwo import events
from mutwo import parameters
from mutwo.utilities import tools

__all__ = ("ReaperFileConverter", "ReaperMarkerConverter")


class ReaperFileConverter(converters.abc.Converter):
    def __init__(self):
        self.reaper_project = self.create_reaper_project()

    @staticmethod
    def create_reaper_project() -> rpp.Element:
        return rpp.Element(
            tag="REAPER_PROJECT",
            attrib=["0.1", "6.16/linux-x86_64", "1607708341"],
            children=[],
        )

    def add_track(self, name: str = "") -> rpp.Element:
        track = rpp.Element(
            tag="TRACK",
            children=[["NAME", name], rpp.Element(tag="FXCHAIN", children=[],),],
        )
        self.reaper_project.append(track)
        return track

    def get_track(self, name: str) -> rpp.Element:
        for track in self.reaper_project.findall(".//TRACK"):
            current_trackname = track.find(".//NAME")
            if current_trackname[1] == name:
                return track

    @staticmethod
    def add_fx(
        track: rpp.Element, fx_info: reaper_constants.VstInfo, name: str = ""
    ) -> rpp.Element:
        fx = rpp.Element(
            tag="VST", attrib=[name, fx_info.filename], children=fx_info.binary
        )
        fxchain = track.find(".//FXCHAIN")
        fxchain.append(fx)
        return fx

    @staticmethod
    def get_all_fx(track) -> typing.List[rpp.Element]:
        fxchain = track.find(".//FXCHAIN")
        return fxchain.findall(".//VST")

    @staticmethod
    def add_parameter_envelope(
        track: rpp.Element,
        fx: rpp.Element,
        parameter_name: str,
        envelope_events: events.basic.SequentialEvent,
    ) -> rpp.Element:
        """events need a value attribute"""
        envelope = rpp.Element(
            tag="PARMENV",
            attrib=[parameter_name, "0", "1", "0.5"],
            children=[
                ["ACT", "1", "-1"],
                ["VIS", "1", "1", "1"],
                ["DEFSHAPE", "0", "-1", "-1"],
            ],
        )
        envelope_points = [
            ["PT", time, event.value, 0]
            for time, event in zip(envelope_events.absolute_times, envelope_events)
        ]
        envelope.extend(envelope_points)
        fxchain = track.find(".//FXCHAIN")
        tools.insert_next_to(fxchain, fx, 1, envelope)
        return envelope

    def convert(self, event: events.abc.Event):
        with open(self.path, "w") as file:
            rpp.dump(self.reaper_project, file)


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
