import abc
import numbers
import typing

import mido

from mutwo.converters.frontends import abc as converters_frontends_abc
from mutwo import events
from mutwo import parameters

Cents = typing.NewType("Cents", numbers.Number)

ConvertableEvents = typing.Union[
    events.music.NoteLike,
    events.basic.SequentialEvent[events.music.NoteLike],
    events.basic.SimultaneousEvent[events.basic.SequentialEvent[events.music.NoteLike]],
]


class MidiFileConverter(converters_frontends_abc.FileConverter):
    # those constants are defined by midi standard
    _maximum_pitch_bend_in_midi = 16382
    _maximum_microseconds_per_beats = 16777215

    def __init__(
        self,
        path: str,
        available_midi_channels: typing.Iterable[int] = tuple(range(16)),
        tempo_events: typing.Union[
            events.basic.SequentialEvent[events.basic.EnvelopeEvent], None
        ] = None,
        maximum_pitch_bend_deviation: Cents = 200,
        ticks_per_beat: int = 700,
        instrument_name: str = "Acoustic Grand Piano",
    ):
        super().__init__(path)

        if tempo_events is None:
            tempo_events = events.basic.SequentialEvent(
                [events.basic.TempoEvent(1, 60)]
            )

        self._available_midi_channels = available_midi_channels
        self._tempo_events = tempo_events
        self._maximum_pitch_bend_deviation = maximum_pitch_bend_deviation
        self._ticks_per_beat = ticks_per_beat
        self._tick_size = 1 / self._ticks_per_second
        self._instrument_name = instrument_name

    @abc.abstractmethod
    def _tune_pitch(self, pitch: parameters.pitches.abc.Pitch):
        raise NotImplementedError

    def _convert_seconds_to_ticks(self, n_seconds: numbers.Number) -> int:
        return int(n_seconds // self._tick_size)

    def _convert_sequential_event_to_midi_track(
        self, sequential_event: events.basic.SequentialEvent[events.basic.SimpleEvent]
    ) -> mido.MidiTrack:
        track = mido.MidiTrack([])
        track.append(mido.MetaMessage("instrument_name", name=self._instrument_name))
        track.append(mido.MetaMessage("end_of_track"))
        return track

    def convert(self, event_to_convert: ConvertableEvents) -> None:
        midi_file = mido.MidiFile([], ticks_per_beat=self._ticks_per_beat)
        midi_file.play
        midi_file.save(filename=self.path)


""""
    self.filename = filename
    self.midifile = MidiFile()
    self.miditrack = MidiTrack()
    self.midifile.tracks.append(self.miditrack)
    self.time = 0
    self.last_event_time = 0
"""
