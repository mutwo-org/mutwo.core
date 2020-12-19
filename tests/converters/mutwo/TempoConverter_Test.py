import unittest

import expenvelope

from mutwo import converters
from mutwo.events import basic


class TempoConverterTest(unittest.TestCase):
    def test_make_envelope(self):
        tempo_events = basic.SequentialEvent(
            [basic.EnvelopeEvent(4, 60), basic.EnvelopeEvent(3, 50, 60, curve_shape=1)]
        )
        envelope = converters.mutwo.TempoConverter.make_envelope_from_tempo_events(
            tempo_events
        )
        expected_envelope = expenvelope.Envelope.from_levels_and_durations(
            (1, 1, 1.2, 1), (4, 1e-100, 3 - 1e-100), (0, 0, 1)
        )
        self.assertEqual(envelope, expected_envelope)

    def test_convert_beats_per_minute_to_seconds_per_beat(self):
        self.assertEqual(
            converters.mutwo.TempoConverter.beats_per_minute_to_seconds_per_beat(60), 1
        )
        self.assertEqual(
            converters.mutwo.TempoConverter.beats_per_minute_to_seconds_per_beat(30), 2
        )
        self.assertEqual(
            converters.mutwo.TempoConverter.beats_per_minute_to_seconds_per_beat(120),
            0.5,
        )

    def test_convert_simple_event(self):
        tempo_events = basic.SequentialEvent([basic.EnvelopeEvent(4, 30, 60)])
        simple_event = basic.SimpleEvent(4)
        converter = converters.mutwo.TempoConverter(tempo_events)
        converted_simple_event = converter.convert(simple_event)
        expected_duration = 6
        self.assertEqual(converted_simple_event.duration, expected_duration)

    def test_convert_sequential_event(self):
        sequential_event = basic.SequentialEvent(
            [basic.SimpleEvent(2) for _ in range(5)]
        )
        tempo_events = basic.SequentialEvent(
            [
                basic.EnvelopeEvent(2, 30),
                basic.EnvelopeEvent(1, 60),
                basic.EnvelopeEvent(1, 30),
                basic.EnvelopeEvent(2, 30, 60),
                basic.EnvelopeEvent(2, 30, 60, curve_shape=10),
                basic.EnvelopeEvent(2, 30, 60, curve_shape=-10),
            ]
        )
        converter = converters.mutwo.TempoConverter(tempo_events)
        converted_sequential_event = converter.convert(sequential_event)
        expected_durations = (4, 3, 3, 3.8000908039820196, 2.1999091960179804)
        self.assertEqual(
            converted_sequential_event.get_parameter("duration"), expected_durations
        )

    def test_convert_simultaneous_event(self):
        tempo_events = basic.SequentialEvent([basic.EnvelopeEvent(4, 30, 60)])
        simple_event0 = basic.SimpleEvent(4)
        simple_event1 = basic.SimpleEvent(8)
        simultaneous_event = basic.SimultaneousEvent(
            [simple_event0, simple_event0, simple_event1]
        )
        converter = converters.mutwo.TempoConverter(tempo_events)
        converted_simultaneous_event = converter.convert(simultaneous_event)
        expected_duration0 = simultaneous_event[0].duration * 1.5
        expected_duration1 = 10
        self.assertEqual(converted_simultaneous_event[0].duration, expected_duration0)
        self.assertEqual(converted_simultaneous_event[1].duration, expected_duration0)
        self.assertEqual(converted_simultaneous_event[2].duration, expected_duration1)


if __name__ == "__main__":
    unittest.main()
