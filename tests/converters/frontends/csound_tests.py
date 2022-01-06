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
    test_path = "tests/converters/frontends/test.sco"

    @classmethod
    def setUpClass(cls):
        cls.converter = converters.frontends.csound.CsoundScoreConverter(
            p4=lambda event: event.pitch.frequency,
            p5=lambda event: event.path,
        )

    @classmethod
    def tearDownClass(cls):
        # remove score files
        os.remove(cls.test_path)

    def test_convert_simple_event(self):
        duration = 2
        event_to_convert = SimpleEventWithPitchAndPathAttribute(
            parameters.pitches.JustIntonationPitch(),
            duration,
            "flute_sample.wav",
        )
        self.converter.convert(event_to_convert, self.test_path)
        expected_line = 'i 1 0 {} {} "{}"'.format(
            duration,
            float(parameters.pitches_constants.DEFAULT_CONCERT_PITCH),
            event_to_convert.path,
        )
        with open(self.test_path, "r") as f:
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
        self.converter.convert(event_to_convert, self.test_path)

        expected_lines = [
            converters.frontends.csound_constants.SEQUENTIAL_EVENT_ANNOTATION
        ]

        expected_lines.extend(
            [
                'i 1 {} {} {} "{}"'.format(
                    absolute_entry_delay, duration, pitch.frequency, path
                )
                for absolute_entry_delay, duration, pitch, path in zip(
                    event_to_convert.absolute_time_tuple, durations, pitches, paths
                )
            ]
        )
        expected_lines.extend(
            [
                ""
                for _ in range(
                    converters.frontends.csound_constants.N_EMPTY_LINES_AFTER_COMPLEX_EVENT
                )
            ]
        )
        expected_lines = "\n".join(expected_lines)

        with open(self.test_path, "r") as f:
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
        self.converter.convert(event_to_convert, self.test_path)

        expected_lines = [
            converters.frontends.csound_constants.SEQUENTIAL_EVENT_ANNOTATION
        ]
        expected_lines.extend(
            [
                'i 1 {} {} {} "{}"'.format(
                    absolute_entry_delay, event.duration, event.pitch.frequency, path
                )
                for absolute_entry_delay, event in zip(
                    event_to_convert.absolute_time_tuple, event_to_convert
                )
                if hasattr(event, "pitch")
            ]
        )
        expected_lines.extend(
            [
                ""
                for _ in range(
                    converters.frontends.csound_constants.N_EMPTY_LINES_AFTER_COMPLEX_EVENT
                )
            ]
        )
        expected_lines = "\n".join(expected_lines)

        with open(self.test_path, "r") as f:
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
        self.converter.convert(event_to_convert, self.test_path)

        expected_lines = [
            converters.frontends.csound_constants.SIMULTANEOUS_EVENT_ANNOTATION
        ]
        expected_lines.extend(
            [
                'i 1 0 {} {} "{}"'.format(duration, pitch.frequency, path)
                for duration, pitch, path in zip(durations, pitches, paths)
            ]
        )
        expected_lines.extend(
            [
                ""
                for _ in range(
                    converters.frontends.csound_constants.N_EMPTY_LINES_AFTER_COMPLEX_EVENT
                )
            ]
        )
        expected_lines = "\n".join(expected_lines)

        with open(self.test_path, "r") as f:
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
            parameters.pitches.JustIntonationPitch(),
            duration,
            set([1, 2, 3]),
        )
        self.converter.convert(event_to_convert, self.test_path)
        expected_line = "i 1 0 {} {}".format(
            duration,
            float(parameters.pitches_constants.DEFAULT_CONCERT_PITCH),
        )
        with open(self.test_path, "r") as f:
            self.assertEqual(f.read(), expected_line)


class CsoundConverterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        common_path = "tests/converters/frontends"
        cls.orchestra_path = "{}/test.orc".format(common_path)
        cls.score_path = "{}/test.sco".format(common_path)
        cls.soundfile_path = "{}/test.wav".format(common_path)
        with open(cls.orchestra_path, "w") as f:
            f.write(
                "sr=44100\nksmps=1\n0dbfs=1\nnchnls=1\ninstr 1\nasig poscil3 p5,"
                " p4\nout asig\nendin"
            )
        cls.score_converter = converters.frontends.csound.CsoundScoreConverter(
            p4=lambda event: event.pitch_list[0].frequency,
            p5=lambda event: event.volume.amplitude,
        )
        cls.converter = converters.frontends.csound.CsoundConverter(
            cls.orchestra_path, cls.score_converter
        )

        cls.event_to_convert = events.music.NoteLike(
            parameters.pitches.WesternPitch("d"),
            2,
            parameters.volumes.DirectVolume(0.85),
        )

    @classmethod
    def tearDownClass(cls):
        # remove csound and sound files
        os.remove(cls.orchestra_path)
        os.remove(cls.score_path)
        os.remove(cls.soundfile_path)

    def test_convert(self):
        # make sure conversion method run without any errors
        # (and sound file exists)

        self.converter.convert(
            self.event_to_convert, self.soundfile_path, self.score_path
        )
        self.assertTrue(os.path.isfile(self.soundfile_path))

    def test_convert_with_remove_score_file(self):
        # make sure csound converter removes / maintains score file

        self.converter.remove_score_file = True
        self.converter.convert(
            self.event_to_convert, self.soundfile_path, self.score_path
        )
        self.assertFalse(os.path.isfile(self.score_path))

        self.converter.remove_score_file = False
        self.converter.convert(
            self.event_to_convert, self.soundfile_path, self.score_path
        )
        self.assertTrue(os.path.isfile(self.score_path))


if __name__ == "__main__":
    unittest.main()
