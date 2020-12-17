import abc
import numbers
import typing

import mido

from mutwo import converters
from mutwo import events
from mutwo import parameters


Cents = typing.NewType("Cents", numbers.Number)


class MidiFileConverter(converters.abc.FileConverter):
    _maximum_pitch_bend_in_midi = 16382

    def __init__(
        self,
        path: str,
        available_midi_channels: typing.Iterable[int] = tuple(range(16)),
        tempo_events: typing.Union[
            typing.Iterable[events.basic.TempoEvent], None
        ] = None,
        maximum_pitch_bend_deviation: Cents = 200,
        ticks_per_second: int = 1000,
        instrument_name: str = "Acoustic Grand Piano",
    ):
        super().__init__(path)

        self._available_midi_channels = available_midi_channels
        self._tempo_events = tempo_events
        self._maximum_pitch_bend_deviation = maximum_pitch_bend_deviation
        self._ticks_per_second = ticks_per_second
        self._tick_size = 1 / self._ticks_per_second
        self._instrument_name = instrument_name

    @abc.abstractmethod
    def _tune_pitch(self, pitch: parameters.pitches.abc.Pitch):
        raise NotImplementedError

    def _convert_seconds_to_ticks(self, n_seconds: float) -> int:
        return int(n_seconds // self._tick_size)

    def convert(self, event_to_convert: events.abc.Event) -> None:
        track = mido.MidiTrack([])
        track.append(mido.MetaMessage("instrument_name", name=self._instrument_name))


""""
    self.filename = filename
    self.midifile = MidiFile()
    self.miditrack = MidiTrack()
    self.midifile.tracks.append(self.miditrack)
    self.time = 0
    self.last_event_time = 0
"""
