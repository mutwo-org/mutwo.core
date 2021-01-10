import os
import unittest

from mutwo import converters
from mutwo import events
from mutwo import parameters


class SimpleEventWithPitchAttribute(events.basic.SimpleEvent):
    """SimpleEvent with additional pitch attribute.

    Only for testing purposes.
    """

    def __init__(
        self,
        pitch: parameters.pitches.abc.Pitch,
        duration: parameters.durations.abc.DurationType,
    ):
        super().__init__(duration)
        self.pitch = pitch


class CsoundScoreConverterTest(unittest.TestCase):
    def setUp(self):
        self.converter = converters.frontends.csound.CsoundScoreConverter(
            "tests/converters/frontends/csound/test.sco", p4=lambda event: event.pitch.frequency
        )

    def tearDown(self):
        # remove score files
        os.remove(self.converter.path)

    def test_convert_simple_event(self):
        duration = 2
        event_to_convert = SimpleEventWithPitchAttribute(
            parameters.pitches.JustIntonationPitch(), duration
        )
        self.converter.convert(event_to_convert)
        expected_line = "i 1 0 {} {}".format(
            duration, float(parameters.pitches.constants.DEFAULT_CONCERT_PITCH)
        )
        with open(self.converter.path, "r") as f:
            self.assertEqual(f.read(), expected_line)

    def test_convert_sequential_event(self):
        pitches = tuple(
            parameters.pitches.JustIntonationPitch(ratio)
            for ratio in ("3/2", "5/4", "1/2", "10/1", "8/1", "1/100")
        )
        durations = (2, 4, 3, 6.25, 8, 1)
        event_to_convert = events.basic.SequentialEvent(
            [
                SimpleEventWithPitchAttribute(pitch, duration)
                for pitch, duration in zip(pitches, durations)
            ]
        )
        self.converter.convert(event_to_convert)

        expected_lines = "\n".join(
            [
                "i 1 {} {} {}".format(absolute_entry_delay, duration, pitch.frequency)
                for absolute_entry_delay, duration, pitch in zip(
                    event_to_convert.absolute_times, durations, pitches
                )
            ]
        )
        with open(self.converter.path, "r") as f:
            self.assertEqual(f.read(), expected_lines)

    def test_convert_sequential_event_with_rests(self):
        event_to_convert = events.basic.SequentialEvent(
            [
                SimpleEventWithPitchAttribute(
                    parameters.pitches.JustIntonationPitch(), 2
                ),
                events.basic.SimpleEvent(2),
                SimpleEventWithPitchAttribute(
                    parameters.pitches.JustIntonationPitch(), 1
                ),
                events.basic.SimpleEvent(3.5),
                SimpleEventWithPitchAttribute(
                    parameters.pitches.JustIntonationPitch(), 4
                ),
            ]
        )
        self.converter.convert(event_to_convert)

        expected_lines = "\n".join(
            [
                "i 1 {} {} {}".format(
                    absolute_entry_delay, event.duration, event.pitch.frequency
                )
                for absolute_entry_delay, event in zip(
                    event_to_convert.absolute_times, event_to_convert
                )
                if hasattr(event, "pitch")
            ]
        )
        with open(self.converter.path, "r") as f:
            self.assertEqual(f.read(), expected_lines)

    def test_convert_simultaneous_event(self):
        pitches = tuple(
            parameters.pitches.JustIntonationPitch(ratio)
            for ratio in ("3/2", "5/4", "1/2", "10/1", "8/1", "1/100")
        )
        durations = (2, 4, 3, 6.25, 8, 1)
        event_to_convert = events.basic.SimultaneousEvent(
            [
                SimpleEventWithPitchAttribute(pitch, duration)
                for pitch, duration in zip(pitches, durations)
            ]
        )
        self.converter.convert(event_to_convert)

        expected_lines = "\n".join(
            [
                "i 1 0 {} {}".format(duration, pitch.frequency)
                for duration, pitch in zip(durations, pitches)
            ]
        )
        with open(self.converter.path, "r") as f:
            self.assertEqual(f.read(), expected_lines)

    # def test_generate_p_field_mapping(self):
    #     pfield_key_to_function_mapping = {
    #         "p1": lambda event: 100,
    #         "p2": None,
    #         "p3": lambda event: event.duration,
    #         "p6": lambda event: event.duration / 2,
    #         "p5": lambda event: event.duration * 2,
    #     }
    #     pfields = converters.frontends.csound.CsoundScoreConverter._generate_pfield_mapping(
    #         pfield_key_to_function_mapping
    #     )
    #     self.assertEqual(len(pfields), len(pfield_key_to_function_mapping) + 1)


if __name__ == "__main__":
    unittest.main()
