import unittest

import expenvelope

from mutwo import converters
from mutwo.events import basic


class TempoConverterTest(unittest.TestCase):
    def test_make_envelope(self):
        tempo_events = basic.SequentialEvent(
            [basic.TempoEvent(4, 60), basic.TempoEvent(3, 50, 60, curve_shape=1)]
        )
        envelope = converters.TempoConverter.make_envelope_from_tempo_events(
            tempo_events
        )
        expected_envelope = expenvelope.Envelope.from_levels_and_durations(
            (1, 1, 1.2, 1), (4, 1e-100, 3 - 1e-100), (0, 0, 1)
        )
        self.assertEqual(envelope, expected_envelope)

    def test_convert_bpm_to_seconds_per_beat(self):
        self.assertEqual(converters.TempoConverter.bpm_to_seconds_per_beat(60), 1)
        self.assertEqual(converters.TempoConverter.bpm_to_seconds_per_beat(30), 2)
        self.assertEqual(converters.TempoConverter.bpm_to_seconds_per_beat(120), 0.5)

    def test_convert_simple_event(self):
        tempo_events = basic.SequentialEvent([basic.TempoEvent(4, 30, 60)])
        simple_event = basic.SimpleEvent(4)
        converter = converters.TempoConverter(tempo_events)
        converted_simple_event = converter.convert(simple_event)
        expected_duration = 6
        self.assertEqual(converted_simple_event.duration, expected_duration)

    def test_convert_sequential_event(self):
        sequential_event = basic.SequentialEvent(
            [basic.SimpleEvent(2) for _ in range(5)]
        )
        tempo_events = basic.SequentialEvent(
            [
                basic.TempoEvent(2, 30),
                basic.TempoEvent(1, 60),
                basic.TempoEvent(1, 30),
                basic.TempoEvent(2, 30, 60),
                basic.TempoEvent(2, 30, 60, curve_shape=10),
                basic.TempoEvent(2, 30, 60, curve_shape=-10),
            ]
        )
        converter = converters.TempoConverter(tempo_events)
        converted_sequential_event = converter.convert(sequential_event)
        expected_durations = (4, 3, 3, 3.8000908039820196, 2.1999091960179804)
        self.assertEqual(
            converted_sequential_event.get_parameter("duration"), expected_durations
        )


if __name__ == "__main__":
    unittest.main()
