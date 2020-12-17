import unittest

from mutwo.events import basic
from mutwo.events import music

from mutwo import parameters


class SimultaneousEventTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sequence = basic.SimultaneousEvent(
            [basic.SimpleEvent(1), basic.SimpleEvent(2), basic.SimpleEvent(3)]
        )

    def test_get_duration(self):
        self.assertEqual(self.sequence.duration, 3)

    def test_set_duration(self):
        self.sequence.duration = 1.5
        self.assertEqual(self.sequence[0].duration, 0.5)
        self.assertEqual(self.sequence[1].duration, 1)
        self.assertEqual(self.sequence[2].duration, 1.5)

    def test_destructive_copy(self):
        simple_event = basic.SimpleEvent(2)
        simultaneous_event = basic.SimultaneousEvent([simple_event, simple_event])
        copied_simultaneous_event = simultaneous_event.destructive_copy()
        copied_simultaneous_event[0].duration = 10
        self.assertNotEqual(
            copied_simultaneous_event[0].duration, copied_simultaneous_event[1].duration
        )

    def test_get_parameter(self):
        result = self.sequence.get_parameter("duration")
        self.assertEqual(result, (1, 2, 3))

    def test_set_parameter(self):
        self.sequence.set_parameter("duration", lambda x: 2 * x)
        self.assertEqual(self.sequence.get_parameter("duration"), (2, 4, 6))

    def test_mutate_parameter(self):
        pitches = (
            parameters.pitches.JustIntonationPitch("1/1"),
            parameters.pitches.JustIntonationPitch("5/4"),
            None,
        )
        simultaneous_event = basic.SimultaneousEvent(
            [
                music.NoteLike(pitches[0], 1, 1),
                music.NoteLike(pitches[1], 1, 1),
                basic.SimpleEvent(2),
            ]
        ).destructive_copy()
        interval = parameters.pitches.JustIntonationPitch("2/1")
        simultaneous_event.mutate_parameter(
            "pitch_or_pitches",
            lambda just_intonation_pitches: just_intonation_pitches[0].add(interval),
        )
        for event, pitch in zip(simultaneous_event, pitches):
            if pitch is not None:
                expected_pitch = [pitch + interval]
            else:
                expected_pitch = None

            self.assertEqual(event.get_parameter("pitch_or_pitches"), expected_pitch)


if __name__ == "__main__":
    unittest.main()
