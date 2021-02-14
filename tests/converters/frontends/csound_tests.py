import os
import unittest

from mutwo import converters
from mutwo import events
from mutwo import parameters


class SimpleEventWithPitchAndPathAttribute(events.basic.SimpleEvent):
    """SimpleEvent with additional pitch and path attributes.

    Only for testing purposes.
    """

    def __init__(
        self,
        pitch: parameters.abc.Pitch,
        duration: parameters.abc.DurationType,
        path: str,
    ):
        super().__init__(duration)
        self.pitch = pitch
        self.path = path


class CsoundScoreConverterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.converter = converters.frontends.csound.CsoundScoreConverter(
            "tests/converters/frontends/test.sco",
            p4=lambda event: event.pitch.frequency,
            p5=lambda event: event.path,
        )

    @classmethod
    def tearDownClass(cls):
        # remove score files
        os.remove(cls.converter.path)

    def test_convert_simple_event(self):
        duration = 2
        event_to_convert = SimpleEventWithPitchAndPathAttribute(
            parameters.pitches.JustIntonationPitch(), duration, "flute_sample.wav",
        )
        self.converter.convert(event_to_convert)
        expected_line = 'i 1 0 {} {} "{}"'.format(
            duration,
            float(parameters.pitches_constants.DEFAULT_CONCERT_PITCH),
            event_to_convert.path,
        )
        with open(self.converter.path, "r") as f:
            self.assertEqual(f.read(), expected_line)

    def test_convert_sequential_event(self):
        pitches = tuple(
            parameters.pitches.JustIntonationPitch(ratio)
            for ratio in ("3/2", "5/4", "1/2", "10/1", "8/1", "1/100")
        )
        durations = (2, 4, 3, 6.25, 8, 1)
        paths = tuple(
            "flute_sample{}.wav".format(nth_sample)
            for nth_sample, pitch in enumerate(pitches)
        )
        event_to_convert = events.basic.SequentialEvent(
            [
                SimpleEventWithPitchAndPathAttribute(pitch, duration, path)
                for pitch, duration, path in zip(pitches, durations, paths)
            ]
        )
        self.converter.convert(event_to_convert)

        expected_lines = "\n".join(
            [
                'i 1 {} {} {} "{}"'.format(
                    absolute_entry_delay, duration, pitch.frequency, path
                )
                for absolute_entry_delay, duration, pitch, path in zip(
                    event_to_convert.absolute_times, durations, pitches, paths
                )
            ]
        )
        with open(self.converter.path, "r") as f:
            self.assertEqual(f.read(), expected_lines)

    def test_convert_sequential_event_with_rests(self):
        path = "flute.wav"
        event_to_convert = events.basic.SequentialEvent(
            [
                SimpleEventWithPitchAndPathAttribute(
                    parameters.pitches.JustIntonationPitch(), 2, path
                ),
                events.basic.SimpleEvent(2),
                SimpleEventWithPitchAndPathAttribute(
                    parameters.pitches.JustIntonationPitch(), 1, path
                ),
                events.basic.SimpleEvent(3.5),
                SimpleEventWithPitchAndPathAttribute(
                    parameters.pitches.JustIntonationPitch(), 4, path
                ),
            ]
        )
        self.converter.convert(event_to_convert)

        expected_lines = "\n".join(
            [
                'i 1 {} {} {} "{}"'.format(
                    absolute_entry_delay, event.duration, event.pitch.frequency, path
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
        paths = tuple(
            "flute_sample{}.wav".format(nth_sample)
            for nth_sample, pitch in enumerate(pitches)
        )
        event_to_convert = events.basic.SimultaneousEvent(
            [
                SimpleEventWithPitchAndPathAttribute(pitch, duration, path)
                for pitch, duration, path in zip(pitches, durations, paths)
            ]
        )
        self.converter.convert(event_to_convert)

        expected_lines = "\n".join(
            [
                'i 1 0 {} {} "{}"'.format(duration, pitch.frequency, path)
                for duration, pitch, path in zip(durations, pitches, paths)
            ]
        )
        with open(self.converter.path, "r") as f:
            self.assertEqual(f.read(), expected_lines)

    def test_generate_p_field_mapping(self):
        pfield_key_to_function_mapping = {
            "p1": lambda event: 100,
            "p2": None,
            "p3": lambda event: event.duration,
            "p6": lambda event: event.duration / 2,
            "p5": lambda event: event.duration * 2,
        }
        pfields = self.converter._generate_pfield_mapping(
            pfield_key_to_function_mapping
        )
        self.assertEqual(len(pfields), len(pfield_key_to_function_mapping) + 1)

    def test_ignore_p_field_with_unsupported_type(self):
        # convert simple event with unsupported type (set) for path argument
        duration = 2
        event_to_convert = SimpleEventWithPitchAndPathAttribute(
            parameters.pitches.JustIntonationPitch(), duration, set([1, 2, 3]),
        )
        self.converter.convert(event_to_convert)
        expected_line = "i 1 0 {} {}".format(
            duration,
            float(parameters.pitches_constants.DEFAULT_CONCERT_PITCH),
        )
        with open(self.converter.path, "r") as f:
            self.assertEqual(f.read(), expected_line)


if __name__ == "__main__":
    unittest.main()
