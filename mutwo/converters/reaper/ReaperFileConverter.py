import typing

import rpp

from mutwo import events
from mutwo.converters import abc
from mutwo.converters.reaper import constants
from mutwo.utilities import tools


class ReaperFileConverter(abc.FileConverter):
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
            children=[
                ["NAME", name],
                rpp.Element(
                    tag="FXCHAIN",
                    children=[],
                ),
            ],
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
        track: rpp.Element, fx_info: constants.VstInfo, name: str = ""
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
        with open(self.path) as file:
            rpp.dump(self.reaper_project, file)
