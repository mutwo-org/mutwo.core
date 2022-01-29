import typing
import unittest

import ranges

from mutwo import core_events
from mutwo import core_utilities


class SimpleEventTest(unittest.TestCase):
    def test_get_assigned_parameter(self):
        duration = 10
        self.assertEqual(
            core_events.SimpleEvent(duration).get_parameter("duration"), duration
        )

    def test_get_not_assigned_parameter(self):
        self.assertEqual(core_events.SimpleEvent(1).get_parameter("anyParameter"), None)

    def test_get_flat_assigned_parameter(self):
        duration = 10
        self.assertEqual(
            core_events.SimpleEvent(duration).get_parameter("duration", flat=True),
            (duration,),
        )

    def test_set_assigned_parameter_by_object(self):
        simple_event = core_events.SimpleEvent(1)
        new_duration = 10
        simple_event.set_parameter("duration", new_duration)
        self.assertEqual(simple_event.duration, new_duration)

    def test_set_assigned_parameter_by_function(self):
        old_duration = 1
        simple_event = core_events.SimpleEvent(old_duration)
        simple_event.set_parameter("duration", lambda old_duration: old_duration * 2)
        self.assertEqual(simple_event.duration, old_duration * 2)

    def test_set_not_assigned_parameter(self):
        simple_event = core_events.SimpleEvent(1)
        new_unknown_parameter = 10
        new_unknown_parameter_name = "new"
        simple_event.set_parameter(
            "new", new_unknown_parameter, set_unassigned_parameter=True
        )
        self.assertEqual(
            simple_event.get_parameter(new_unknown_parameter_name),
            new_unknown_parameter,
        )

    def test_parameter_to_compare_tuple(self):
        simple_event = core_events.SimpleEvent(1)
        expected_parameter_to_compare_tuple = ("duration",)
        self.assertEqual(
            simple_event._parameter_to_compare_tuple,
            expected_parameter_to_compare_tuple,
        )

    def test_equality_check(self):
        simple_event0 = core_events.SimpleEvent(2)
        simple_event1 = core_events.SimpleEvent(3)
        simple_event2 = core_events.SimpleEvent(2)
        simple_event3 = core_events.SimpleEvent(2.3)

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
        event0 = core_events.SimpleEvent(4)
        cut_up_event0 = core_events.SimpleEvent(2)

        event1 = core_events.SimpleEvent(10)
        cut_up_event1 = core_events.SimpleEvent(5)

        event2 = core_events.SimpleEvent(5)
        cut_up_event2 = core_events.SimpleEvent(1)

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
        event0 = core_events.SimpleEvent(4)
        cut_off_event0 = core_events.SimpleEvent(2)

        event1 = core_events.SimpleEvent(10)
        cut_off_event1 = core_events.SimpleEvent(5)

        self.assertEqual(event0.cut_off(0, 2, mutate=False), cut_off_event0)
        self.assertEqual(event0.cut_off(2, 5, mutate=False), cut_off_event0)

        event1.cut_off(0, 5)
        self.assertEqual(event1, cut_off_event1)

    def test_split_at(self):
        event = core_events.SimpleEvent(4)

        split0 = (core_events.SimpleEvent(1), core_events.SimpleEvent(3))
        split1 = (core_events.SimpleEvent(2), core_events.SimpleEvent(2))
        split2 = (core_events.SimpleEvent(3), core_events.SimpleEvent(1))

        self.assertEqual(event.split_at(1), split0)
        self.assertEqual(event.split_at(2), split1)
        self.assertEqual(event.split_at(3), split2)


class SequentialEventTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sequence: core_events.SequentialEvent[
            core_events.SimpleEvent
        ] = core_events.SequentialEvent(
            [
                core_events.SimpleEvent(1),
                core_events.SimpleEvent(2),
                core_events.SimpleEvent(3),
            ]
        )

    def test_magic_method_add(self):
        self.assertEqual(
            type(core_events.SequentialEvent([]) + core_events.SequentialEvent([])),
            core_events.SequentialEvent,
        )

    def test_magic_method_mul(self):
        self.assertEqual(
            type(core_events.SequentialEvent([]) * 5), core_events.SequentialEvent
        )

    def test_get_duration(self):
        self.assertEqual(self.sequence.duration, 6)

    def test_set_duration(self):
        self.sequence.duration = 3
        self.assertEqual(self.sequence[0].duration, 0.5)
        self.assertEqual(self.sequence[1].duration, 1)
        self.assertEqual(self.sequence[2].duration, 1.5)

    def test_get_absolute_time_tuple(self):
        result = tuple(self.sequence.absolute_time_tuple)
        self.assertEqual(result, (0, 1, 3))

    def test_get_event_at(self):
        result = self.sequence.get_event_at(1.5)
        self.assertEqual(result, self.sequence[1])

    def test_get_event_at_for_unavailable_event(self):
        result_for_unavailable_event = self.sequence.get_event_at(100)
        self.assertEqual(result_for_unavailable_event, None)

    def test_cut_up(self):
        result0 = core_events.SequentialEvent(
            [
                core_events.SimpleEvent(0.5),
                core_events.SimpleEvent(2),
                core_events.SimpleEvent(2),
            ]
        )
        result1 = core_events.SequentialEvent([core_events.SimpleEvent(1)])
        self.assertEqual(
            [event.duration for event in result0],
            [event.duration for event in self.sequence.cut_out(0.5, 5, mutate=False)],
        )
        self.assertEqual(
            [event.duration for event in result1],
            [event.duration for event in self.sequence.cut_out(1, 2, mutate=False)],
        )

    def test_cut_off(self):
        result0 = core_events.SequentialEvent(
            [
                core_events.SimpleEvent(0.5),
                core_events.SimpleEvent(2),
                core_events.SimpleEvent(3),
            ]
        )
        result1 = core_events.SequentialEvent([core_events.SimpleEvent(1)])
        result2 = core_events.SequentialEvent(
            [core_events.SimpleEvent(1), core_events.SimpleEvent(0.75)]
        )
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
            self.sequence.squash_in(0.5, core_events.SimpleEvent(1), mutate=False),
            core_events.SequentialEvent(
                [core_events.SimpleEvent(duration) for duration in (0.5, 1, 1.5, 3)]
            ),
        )
        self.assertEqual(
            self.sequence.squash_in(5, core_events.SimpleEvent(2), mutate=False),
            core_events.SequentialEvent(
                [core_events.SimpleEvent(duration) for duration in (1, 2, 2, 2)]
            ),
        )
        self.assertEqual(
            self.sequence.squash_in(0, core_events.SimpleEvent(1.5), mutate=False),
            core_events.SequentialEvent(
                [core_events.SimpleEvent(duration) for duration in (1.5, 1.5, 3)]
            ),
        )
        self.assertEqual(
            self.sequence.squash_in(6, core_events.SimpleEvent(1), mutate=False),
            core_events.SequentialEvent(
                [core_events.SimpleEvent(duration) for duration in (1, 2, 3, 1)]
            ),
        )
        self.assertEqual(
            self.sequence.squash_in(0.5, core_events.SimpleEvent(0.25), mutate=False),
            core_events.SequentialEvent(
                [
                    core_events.SimpleEvent(duration)
                    for duration in (0.5, 0.25, 0.25, 2, 3)
                ]
            ),
        )
        self.assertRaises(
            ValueError,
            lambda: self.sequence.squash_in(
                7, core_events.SimpleEvent(1.5), mutate=False
            ),
        )

    def test_squash_in_with_minor_differences(self):
        self.assertEqual(
            self.sequence.squash_in(6e-10, core_events.SimpleEvent(1), mutate=False),
            core_events.SequentialEvent(
                [
                    core_events.SimpleEvent(duration)
                    for duration in (6e-10, 1, 2 - 6e-10, 3)
                ]
            ),
        )

    def test_tie_by(self):
        self.assertEqual(
            self.sequence.tie_by(
                lambda event_left, event_right: event_left.duration + 1
                == event_right.duration,
                event_type_to_examine=core_events.SimpleEvent,
                mutate=False,
            ),
            core_events.SequentialEvent(
                [core_events.SimpleEvent(3), core_events.SimpleEvent(3)]
            ),
        )
        self.assertEqual(
            self.sequence.tie_by(
                lambda event_left, event_right: event_left.duration + 1
                == event_right.duration,
                lambda event_to_survive, event_to_remove: None,
                event_type_to_examine=core_events.SimpleEvent,
                event_to_remove=False,
                mutate=False,
            ),
            core_events.SequentialEvent([core_events.SimpleEvent(3)]),
        )
        self.assertEqual(
            self.sequence.tie_by(
                lambda event_left, event_right: event_left.duration + 1
                == event_right.duration,
                lambda event_to_survive, event_to_remove: None,
                event_type_to_examine=core_events.SimpleEvent,
                event_to_remove=True,
                mutate=False,
            ),
            core_events.SequentialEvent(
                [core_events.SimpleEvent(1), core_events.SimpleEvent(3)]
            ),
        )

    def test_tie_by_for_nested_events(self):
        nested_sequential_event0 = core_events.SequentialEvent(
            [
                core_events.SequentialEvent(
                    [core_events.SimpleEvent(3), core_events.SimpleEvent(2)]
                ),
                core_events.SequentialEvent(
                    [core_events.SimpleEvent(4), core_events.SimpleEvent(2)]
                ),
            ]
        )
        nested_sequential_event0.tie_by(
            lambda event_left, event_right: event_left.duration - 1
            == event_right.duration,
            event_type_to_examine=core_events.SimpleEvent,
            event_to_remove=True,
        )

        self.assertEqual(
            nested_sequential_event0,
            core_events.SequentialEvent(
                [
                    core_events.SequentialEvent([core_events.SimpleEvent(5)]),
                    core_events.SequentialEvent(
                        [core_events.SimpleEvent(4), core_events.SimpleEvent(2)]
                    ),
                ]
            ),
        )

        nested_sequential_event1 = core_events.SequentialEvent(
            [
                core_events.SequentialEvent(
                    [core_events.SimpleEvent(3), core_events.SimpleEvent(2)]
                ),
                core_events.SequentialEvent([core_events.SimpleEvent(5)]),
            ]
        )
        nested_sequential_event1.tie_by(
            lambda event_left, event_right: event_left.duration == event_right.duration,
            event_to_remove=True,
        )
        self.assertEqual(
            nested_sequential_event1,
            core_events.SequentialEvent(
                [
                    core_events.SequentialEvent(
                        [core_events.SimpleEvent(6), core_events.SimpleEvent(4)]
                    )
                ]
            ),
        )

    def test_split_child_at(self):
        sequential_event0 = core_events.SequentialEvent([core_events.SimpleEvent(3)])
        sequential_event0.split_child_at(1)
        sequential_event_to_compare0 = core_events.SequentialEvent(
            [core_events.SimpleEvent(1), core_events.SimpleEvent(2)]
        )
        self.assertEqual(sequential_event0, sequential_event_to_compare0)

        sequential_event1 = core_events.SequentialEvent(
            [core_events.SimpleEvent(4), core_events.SimpleEvent(1)]
        )
        sequential_event1.split_child_at(3)
        sequential_event_to_compare1 = core_events.SequentialEvent(
            [
                core_events.SimpleEvent(3),
                core_events.SimpleEvent(1),
                core_events.SimpleEvent(1),
            ]
        )
        self.assertEqual(sequential_event1, sequential_event_to_compare1)

        sequential_event2 = core_events.SequentialEvent(
            [core_events.SimpleEvent(3), core_events.SimpleEvent(2)]
        )
        sequential_event2_copy = sequential_event2.copy()
        sequential_event2.split_at(3)
        self.assertEqual(sequential_event2, sequential_event2_copy)

    def test_split_child_at_unavailable_time(self):
        self.assertRaises(
            core_utilities.exceptions.SplitUnavailableChildError,
            lambda: self.sequence.split_child_at(1000),
        )

    def test_start_and_end_time_per_event(self):
        self.assertEqual(
            self.sequence.start_and_end_time_per_event,
            (ranges.Range(0, 1), ranges.Range(1, 3), ranges.Range(3, 6)),
        )


class SimultaneousEventTest(unittest.TestCase):
    class DummyParameter(object):
        def __init__(self, value: float):
            self.value = value

        def double_value(self):
            self.value *= 2

        def __eq__(self, other: typing.Any) -> bool:
            try:
                return self.value == other.value
            except AttributeError:
                return False

    def setUp(self) -> None:
        self.sequence: core_events.SimultaneousEvent[
            core_events.SimpleEvent
        ] = core_events.SimultaneousEvent(
            [
                core_events.SimpleEvent(1),
                core_events.SimpleEvent(2),
                core_events.SimpleEvent(3),
            ]
        )
        self.nested_sequence: core_events.SimultaneousEvent[
            core_events.SequentialEvent[core_events.SimpleEvent]
        ] = core_events.SimultaneousEvent(
            [
                core_events.SequentialEvent(
                    [
                        core_events.SimpleEvent(1),
                        core_events.SimpleEvent(2),
                        core_events.SimpleEvent(3),
                    ]
                )
                for _ in range(2)
            ]
        )

    def test_get_event_from_index_sequence(self):
        self.assertEqual(
            self.sequence.get_event_from_index_sequence((0,)), self.sequence[0]
        )
        self.assertEqual(self.sequence.get_event_from_index_sequence([]), self.sequence)

    def test_get_duration(self):
        self.assertEqual(self.sequence.duration, 3)

    def test_set_duration(self):
        self.sequence.duration = 1.5
        self.assertEqual(self.sequence[0].duration, 0.5)
        self.assertEqual(self.sequence[1].duration, 1)
        self.assertEqual(self.sequence[2].duration, 1.5)

    def test_destructive_copy(self):
        simple_event = core_events.SimpleEvent(2)
        simultaneous_event = core_events.SimultaneousEvent([simple_event, simple_event])
        copied_simultaneous_event = simultaneous_event.destructive_copy()
        copied_simultaneous_event[0].duration = 10
        self.assertNotEqual(
            copied_simultaneous_event[0].duration, copied_simultaneous_event[1].duration
        )

    def test_get_parameter(self):
        result = self.sequence.get_parameter("duration")
        self.assertEqual(result, (1, 2, 3))

    def test_get_nested_parameter(self):
        result = self.nested_sequence.get_parameter("duration")
        self.assertEqual(result, ((1, 2, 3), (1, 2, 3)))

    def test_get_flat_parameter(self):
        result = self.nested_sequence.get_parameter("duration", flat=True)
        self.assertEqual(result, (1, 2, 3, 1, 2, 3))

    def test_set_parameter(self):
        self.sequence.set_parameter("duration", lambda x: 2 * x)
        self.assertEqual(self.sequence.get_parameter("duration"), (2, 4, 6))

    def test_mutate_parameter(self):
        dummy_parameter_tuple = (
            self.DummyParameter(1),
            self.DummyParameter(2),
            None,
        )
        simple_event_tuple = (
            core_events.SimpleEvent(1),
            core_events.SimpleEvent(1),
            core_events.SimpleEvent(2),
        )
        for simple_event, dummy_parameter in zip(
            simple_event_tuple, dummy_parameter_tuple
        ):
            if dummy_parameter is not None:
                simple_event.dummy_parameter = dummy_parameter  # type: ignore
        simultaneous_event = core_events.SimultaneousEvent(
            simple_event_tuple
        ).destructive_copy()
        simultaneous_event.mutate_parameter(
            "dummy_parameter",
            lambda dummy_parameter: dummy_parameter.double_value(),
        )
        for event, dummy_parameter in zip(simultaneous_event, dummy_parameter_tuple):
            if dummy_parameter is not None:
                expected_dummy_parameter = self.DummyParameter(
                    dummy_parameter.value * 2
                )
            else:
                expected_dummy_parameter = None

            self.assertEqual(
                event.get_parameter("dummy_parameter"), expected_dummy_parameter
            )

    def test_cut_up(self):
        result = core_events.SimultaneousEvent(
            [core_events.SimpleEvent(0.5) for _ in range(3)]
        )

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
        result0 = core_events.SimultaneousEvent(
            [core_events.SimpleEvent(duration) for duration in (0.5, 1.5, 2.5)]
        )
        result1 = core_events.SimultaneousEvent(
            [core_events.SimpleEvent(duration) for duration in (1, 2, 2.5)]
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
            lambda: self.sequence.squash_in(
                0, core_events.SimpleEvent(1.5), mutate=False
            ),
        )

        simultaneous_event_to_test = core_events.SimultaneousEvent(
            [
                core_events.SequentialEvent(
                    [core_events.SimpleEvent(duration) for duration in (2, 3)]
                ),
                core_events.SequentialEvent(
                    [core_events.SimpleEvent(duration) for duration in (1, 1, 1, 2)]
                ),
            ]
        )
        expected_simultaneous_event = core_events.SimultaneousEvent(
            [
                core_events.SequentialEvent(
                    [core_events.SimpleEvent(duration) for duration in (1, 1.5, 2.5)]
                ),
                core_events.SequentialEvent(
                    [core_events.SimpleEvent(duration) for duration in (1, 1.5, 0.5, 2)]
                ),
            ]
        )

        self.assertEqual(
            simultaneous_event_to_test.squash_in(
                1, core_events.SimpleEvent(1.5), mutate=False
            ),
            expected_simultaneous_event,
        )

    def test_split_child_at(self):
        simultaneous_event0 = core_events.SimultaneousEvent(
            [core_events.SequentialEvent([core_events.SimpleEvent(3)])]
        )
        simultaneous_event0.split_child_at(1)
        simultaneous_event_to_compare0 = core_events.SimultaneousEvent(
            [
                core_events.SequentialEvent(
                    [core_events.SimpleEvent(1), core_events.SimpleEvent(2)]
                )
            ]
        )
        self.assertEqual(simultaneous_event0, simultaneous_event_to_compare0)

    def test_filter(self):
        simultaneous_event_to_filter = core_events.SimultaneousEvent(
            [
                core_events.SimpleEvent(1),
                core_events.SimpleEvent(3),
                core_events.SimpleEvent(2),
            ]
        )
        simultaneous_event_to_filter.filter(lambda event: event.duration > 2)
        self.assertEqual(
            simultaneous_event_to_filter,
            core_events.SimultaneousEvent([core_events.SimpleEvent(3)]),
        )


if __name__ == "__main__":
    unittest.main()
