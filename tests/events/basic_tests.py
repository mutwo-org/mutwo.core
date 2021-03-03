import unittest

from mutwo.events import basic
from mutwo.events import music


from mutwo import parameters


class SimpleEventTest(unittest.TestCase):
    def test_get_assigned_parameter(self):
        duration = 10
        self.assertEqual(
            basic.SimpleEvent(duration).get_parameter("duration"), duration
        )

    def test_get_not_assigned_parameter(self):
        self.assertEqual(basic.SimpleEvent(1).get_parameter("anyParameter"), None)

    def test_set_assigned_parameter_by_object(self):
        simple_event = basic.SimpleEvent(1)
        new_duration = 10
        simple_event.set_parameter("duration", new_duration)
        self.assertEqual(simple_event.duration, new_duration)

    def test_set_assigned_parameter_by_function(self):
        old_duration = 1
        simple_event = basic.SimpleEvent(old_duration)
        simple_event.set_parameter("duration", lambda old_duration: old_duration * 2)
        self.assertEqual(simple_event.duration, old_duration * 2)

    def test_set_not_assigned_parameter(self):
        simple_event = basic.SimpleEvent(1)
        new_unknown_parameter = 10
        new_unknown_parameter_name = "new"
        simple_event.set_parameter(
            "new", new_unknown_parameter, set_unassigned_parameter=True
        )
        self.assertEqual(
            simple_event.get_parameter(new_unknown_parameter_name),
            new_unknown_parameter,
        )

    def test_parameters_to_compare(self):
        simple_event = basic.SimpleEvent(1)
        expected_parameters_to_compare = ("duration",)
        self.assertEqual(
            simple_event._parameters_to_compare, expected_parameters_to_compare
        )

    def test_equality_check(self):
        simple_event0 = basic.SimpleEvent(2)
        simple_event1 = basic.SimpleEvent(3)
        simple_event2 = basic.SimpleEvent(2)
        simple_event3 = basic.SimpleEvent(2.3)

        self.assertEqual(simple_event0, simple_event2)
        self.assertEqual(simple_event2, simple_event0)  # different order
        self.assertEqual(simple_event0, simple_event0)
        self.assertEqual(simple_event2, simple_event2)

        self.assertNotEqual(simple_event0, simple_event1)
        self.assertNotEqual(simple_event1, simple_event0)  # different order
        self.assertNotEqual(simple_event0, simple_event3)
        self.assertNotEqual(simple_event2, simple_event3)
        self.assertNotEqual(simple_event2, simple_event2.duration)
        self.assertNotEqual(simple_event0, [1, 2, 3])

    def test_cut_up(self):
        event0 = basic.SimpleEvent(4)
        cut_up_event0 = basic.SimpleEvent(2)

        event1 = basic.SimpleEvent(10)
        cut_up_event1 = basic.SimpleEvent(5)

        event2 = basic.SimpleEvent(5)
        cut_up_event2 = basic.SimpleEvent(1)

        event2.cut_out(2, 3)

        self.assertEqual(
            event0.cut_out(2, 4, mutate=False).duration, cut_up_event0.duration
        )
        self.assertEqual(
            event1.cut_out(0, 5, mutate=False).duration, cut_up_event1.duration
        )
        self.assertEqual(event2.duration, cut_up_event2.duration)

        # this will raise an error because the simple event isn't within the
        # asked range.
        self.assertRaises(ValueError, lambda: event0.cut_out(4, 5))
        self.assertRaises(ValueError, lambda: event0.cut_out(-2, -1))

    def test_cut_off(self):
        event0 = basic.SimpleEvent(4)
        cut_off_event0 = basic.SimpleEvent(2)

        event1 = basic.SimpleEvent(10)
        cut_off_event1 = basic.SimpleEvent(5)

        self.assertEqual(event0.cut_off(0, 2, mutate=False), cut_off_event0)
        self.assertEqual(event0.cut_off(2, 5, mutate=False), cut_off_event0)

        event1.cut_off(0, 5)
        self.assertEqual(event1, cut_off_event1)


class SequentialEventTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sequence = basic.SequentialEvent(
            [basic.SimpleEvent(1), basic.SimpleEvent(2), basic.SimpleEvent(3)]
        )

    def test_get_duration(self):
        self.assertEqual(self.sequence.duration, 6)

    def test_set_duration(self):
        self.sequence.duration = 3
        self.assertEqual(self.sequence[0].duration, 0.5)
        self.assertEqual(self.sequence[1].duration, 1)
        self.assertEqual(self.sequence[2].duration, 1.5)

    def test_get_absolute_times(self):
        result = tuple(self.sequence.absolute_times)
        self.assertEqual(result, (0, 1, 3))

    def test_get_event_at(self):
        result = self.sequence.get_event_at(1.5)
        self.assertEqual(result, self.sequence[1])

    def test_cut_up(self):
        result0 = basic.SequentialEvent(
            [basic.SimpleEvent(0.5), basic.SimpleEvent(2), basic.SimpleEvent(2)]
        )
        result1 = basic.SequentialEvent([basic.SimpleEvent(1)])
        self.assertEqual(
            [event.duration for event in result0],
            [event.duration for event in self.sequence.cut_out(0.5, 5, mutate=False)],
        )
        self.assertEqual(
            [event.duration for event in result1],
            [event.duration for event in self.sequence.cut_out(1, 2, mutate=False)],
        )

    def test_cut_off(self):
        result0 = basic.SequentialEvent(
            [basic.SimpleEvent(0.5), basic.SimpleEvent(2), basic.SimpleEvent(3)]
        )
        result1 = basic.SequentialEvent([basic.SimpleEvent(1)])
        result2 = basic.SequentialEvent([basic.SimpleEvent(1), basic.SimpleEvent(0.75)])
        self.assertEqual(
            [event.duration for event in result0],
            [event.duration for event in self.sequence.cut_off(0.5, 1, mutate=False)],
        )
        self.assertEqual(
            [event.duration for event in result1],
            [event.duration for event in self.sequence.cut_off(1, 6, mutate=False)],
        )
        self.assertEqual(
            [event.duration for event in result1],
            [event.duration for event in self.sequence.cut_off(1, 7, mutate=False)],
        )
        self.assertEqual(
            [event.duration for event in result2],
            [event.duration for event in self.sequence.cut_off(1.75, 7, mutate=False)],
        )

    def test_squash_in(self):
        self.assertEqual(
            self.sequence.squash_in(0.5, basic.SimpleEvent(1), mutate=False),
            basic.SequentialEvent(
                [basic.SimpleEvent(duration) for duration in (0.5, 1, 1.5, 3)]
            ),
        )
        self.assertEqual(
            self.sequence.squash_in(5, basic.SimpleEvent(2), mutate=False),
            basic.SequentialEvent(
                [basic.SimpleEvent(duration) for duration in (1, 2, 2, 2)]
            ),
        )
        self.assertEqual(
            self.sequence.squash_in(0, basic.SimpleEvent(1.5), mutate=False),
            basic.SequentialEvent(
                [basic.SimpleEvent(duration) for duration in (1.5, 1.5, 3)]
            ),
        )
        self.assertEqual(
            self.sequence.squash_in(6, basic.SimpleEvent(1), mutate=False),
            basic.SequentialEvent(
                [basic.SimpleEvent(duration) for duration in (1, 2, 3, 1)]
            ),
        )
        self.assertRaises(
            ValueError,
            lambda: self.sequence.squash_in(7, basic.SimpleEvent(1.5), mutate=False),
        )


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

    def test_cut_up(self):
        result = basic.SimultaneousEvent([basic.SimpleEvent(0.5) for _ in range(3)])

        self.assertEqual(
            [event.duration for event in result],
            [event.duration for event in self.sequence.cut_out(0.5, 1, mutate=False)],
        )
        self.assertEqual(
            [event.duration for event in result],
            [event.duration for event in self.sequence.cut_out(0, 0.5, mutate=False)],
        )
        self.assertEqual(
            [event.duration for event in result],
            [
                event.duration
                for event in self.sequence.cut_out(0.25, 0.75, mutate=False)
            ],
        )

        # this will raise an error because the simultaneous event contains simple events
        # where some simple event aren't long enough for the following cut up arguments.
        self.assertRaises(ValueError, lambda: self.sequence.cut_out(2, 3))

    def test_cut_off(self):
        result0 = basic.SimultaneousEvent(
            [basic.SimpleEvent(duration) for duration in (0.5, 1.5, 2.5)]
        )
        result1 = basic.SimultaneousEvent(
            [basic.SimpleEvent(duration) for duration in (1, 2, 2.5)]
        )

        self.assertEqual(
            [event.duration for event in result0],
            [event.duration for event in self.sequence.cut_off(0, 0.5, mutate=False)],
        )
        self.assertEqual(
            [event.duration for event in result1],
            [event.duration for event in self.sequence.cut_off(2.5, 3, mutate=False)],
        )

    def test_squash_in(self):
        self.assertRaises(
            TypeError,
            lambda: self.sequence.squash_in(0, basic.SimpleEvent(1.5), mutate=False),
        )

        simultaneous_event_to_test = basic.SimultaneousEvent(
            [
                basic.SequentialEvent(
                    [basic.SimpleEvent(duration) for duration in (2, 3)]
                ),
                basic.SequentialEvent(
                    [basic.SimpleEvent(duration) for duration in (1, 1, 1, 2)]
                ),
            ]
        )
        expected_simultaneous_event = basic.SimultaneousEvent(
            [
                basic.SequentialEvent(
                    [basic.SimpleEvent(duration) for duration in (1, 1.5, 2.5)]
                ),
                basic.SequentialEvent(
                    [basic.SimpleEvent(duration) for duration in (1, 1.5, 0.5, 2)]
                ),
            ]
        )

        self.assertEqual(
            simultaneous_event_to_test.squash_in(
                1, basic.SimpleEvent(1.5), mutate=False
            ),
            expected_simultaneous_event,
        )


if __name__ == "__main__":
    unittest.main()
