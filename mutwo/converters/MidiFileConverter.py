from mutwo import converters
from mutwo import events


class MidiFileConverter(converters.Converter):
    def convert(self, events_to_convert: events.abc.Event):
        raise NotImplementedError


""""
    self.filename = filename
    self.midifile = MidiFile()
    self.miditrack = MidiTrack()
    self.midifile.tracks.append(self.miditrack)
    self.time = 0
    self.last_event_time = 0
"""
