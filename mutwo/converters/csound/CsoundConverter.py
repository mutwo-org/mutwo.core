import os
import typing

from mutwo import converters
from mutwo import events

from .CsoundScoreConverter import CsoundScoreConverter

ConvertableEvent = typing.Union[
    events.basic.SimpleEvent,
    events.basic.SequentialEvent,
    events.basic.SimultaneousEvent,
]


class CsoundConverter(converters.abc.FileConverter):
    """Simple converter that helps generating audio files with Csound.

    """

    def __init__(
        self,
        path: str,
        csound_orchestra_path: str,
        csound_score_converter: CsoundScoreConverter,
        *flag: str
    ):
        self.flags = flag
        self.path = path
        self.csound_orchestra_path = csound_orchestra_path
        self.csound_score_converter = csound_score_converter

    def convert(self, event_to_convert: ConvertableEvent) -> None:
        self.csound_score_converter.convert(event_to_convert)
        command = "csound -o {}".format(self.path)
        for flag in self.flags:
            command += " {} ".format(flag)
        command += " {} {}".format(
            self.csound_orchestra_path, self.csound_score_converter.path
        )

        os.system(command)
