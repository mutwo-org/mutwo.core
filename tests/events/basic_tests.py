import abc
import typing
import unittest

import ranges

try:
    import quicktions as fractions
except ImportError:
    import fractions

from mutwo import core_converters
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities


class EventTest(abc.ABC):
    """Define tests which should pass on various event classes"""

    @abc.abstractmethod
    def get_event_class(self) -> typing.Type:
        ...

    @abc.abstractmethod
    def get_event_instance(self) -> core_events.abc.Event:
        ...

    def test_tempo_envelope_auto_initialization(self):
        event = self.get_event_instance()
        self.assertTrue(bool(event.tempo_envelope))
        self.assertTrue(isinstance(event.tempo_envelope, core_events.TempoEnvelope))

    def test_tempo_envelope_auto_initialization_and_settable(self):
        self.event.tempo_envelope[0].duration = 100
        self.assertEqual(self.event.tempo_envelope[0].duration, 100)

    def test_split_at_start(self):
        self.assertEqual(self.event.split_at(0), (self.event,))

    def test_split_at_end(self):
        self.assertEqual(self.event.split_at(self.event.duration), (self.event,))

    def test_split_at_invalid_absolute_time(self):
        self.assertRaises(
            core_utilities.InvalidAbsoluteTime,
            self.event.split_at,
            -1,
        )

    def test_split_at_out_of_range_time(self):
        self.assertRaises(
            core_utilities.SplitError, self.event.split_at, self.event.duration + 1
        )

    def test_cut_off_invalid_absolute_time(self):
        self.assertRaises(
            core_utilities.InvalidAbsoluteTime,
            self.event.cut_off,
            -1,
            self.event.duration,
        )

    def test_cut_out_invalid_absolute_time(self):
        self.assertRaises(
            core_utilities.InvalidAbsoluteTime,
            self.event.cut_out,
            -1,
            self.event.duration,
        )


class ComplexEventTest(EventTest):
    def test_slide_in_invalid_absolute_time(self):
        self.assertRaises(
            core_utilities.InvalidAbsoluteTime,
            self.event.slide_in,
            -1,
            core_events.SimpleEvent(1),
        )

    def test_squash_in_invalid_absolute_time(self):
        self.assertRaises(
            core_utilities.InvalidAbsoluteTime,
            self.event.squash_in,
            -1,
            core_events.SimpleEvent(1),
        )

    def test_split_child_at(self):
        self.assertRaises(
            core_utilities.InvalidAbsoluteTime, self.event.split_child_at, -1
        )
>>>>>>> 3c74e35 (fixup! events/E.split_at: standardize exception)


class SimpleEventTest(unittest.TestCase, EventTest):
    def get_event_class(self) -> typing.Type:
        return core_events.SimpleEvent

    def get_event_instance(self) -> core_events.SimpleEvent:
        return self.get_event_class()(10)

    def test_copy(self):
        simple_event0 = core_events.SimpleEvent(20)
        simple_event1 = simple_event0.copy()
        simple_event1.duration = 300

        self.assertEqual(simple_event0.duration.duration, 20)
        self.assertEqual(simple_event1.duration.duration, 300)

    def test_set(self):
        simple_event = core_events.SimpleEvent(1)
        self.assertEqual(simple_event.duration, 1)

        simple_event.set("duration", 10)
        self.assertEqual(simple_event.duration, 10)

        simple_event.set("new_attribute", "hello world!")
        self.assertEqual(simple_event.new_attribute, "hello world!")

    def test_metrize(self):
        """Minimal test to ensure API keeps stable

        Please consult EventToMetrizedEventTest for tests of actual
        functionality.
        """

        simple_event = core_events.SimpleEvent(
            1, tempo_envelope=core_events.TempoEnvelope([[0, 30], [1, 120]])
        )
        self.assertEqual(
            simple_event.metrize(mutate=False),
            core_converters.EventToMetrizedEvent().convert(simple_event),
        )

    def test_reset_tempo_envelope(self):
        simple_event = self.get_event_instance()
        simple_event.tempo_envelope[0].value = 100
        self.assertEqual(simple_event.tempo_envelope[0].value, 100)
        simple_event.reset_tempo_envelope()
        self.assertEqual(simple_event.tempo_envelope.value_tuple[0], 60)

    def test_get_assigned_parameter(self):
        duration = core_parameters.DirectDuration(10)
        self.assertEqual(
            core_events.SimpleEvent(duration).get_parameter("duration"), duration
        )

    def test_get_not_assigned_parameter(self):
        self.assertEqual(core_events.SimpleEvent(1).get_parameter("anyParameter"), None)

    def test_get_flat_assigned_parameter(self):
        duration = core_parameters.DirectDuration(10)
        self.assertEqual(
            core_events.SimpleEvent(duration).get_parameter("duration", flat=True),
            duration,
        )

    def test_set_assigned_parameter_by_object(self):
        simple_event = core_events.SimpleEvent(1)
        duration = core_parameters.DirectDuration(10)
        simple_event.set_parameter("duration", duration)
        self.assertEqual(simple_event.duration, duration)

    def test_set_assigned_parameter_by_function(self):
        old_duration = 1
        simple_event = core_events.SimpleEvent(old_duration)
        simple_event.set_parameter("duration", lambda old_duration: old_duration * 2)
        self.assertEqual(
            simple_event.duration, core_parameters.DirectDuration(old_duration * 2)
        )

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
        expected_parameter_to_compare_tuple = ("duration", "tempo_envelope")
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

    def test_cut_out(self):
        event0 = core_events.SimpleEvent(4)
        cut_out_event0 = core_events.SimpleEvent(2)

        event1 = core_events.SimpleEvent(10)
        cut_out_event1 = core_events.SimpleEvent(5)

        event2 = core_events.SimpleEvent(5)
        cut_out_event2 = core_events.SimpleEvent(1)

        event2.cut_out(2, 3)

        self.assertEqual(
            event0.cut_out(2, 4, mutate=False).duration, cut_out_event0.duration
        )
        self.assertEqual(
            event1.cut_out(0, 5, mutate=False).duration, cut_out_event1.duration
        )
        self.assertEqual(event2.duration, cut_out_event2.duration)

        # this will raise an error because the simple event isn't within the
        # asked range.
        self.assertRaises(
            core_utilities.InvalidCutOutStartAndEndValuesError,
            lambda: event0.cut_out(4, 5),
        )
        self.assertRaises(
            core_utilities.InvalidCutOutStartAndEndValuesError,
            lambda: event0.cut_out(-2, -1),
        )

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


class SequentialEventTest(unittest.TestCase, EventTest):
    def setUp(self):
        self.simple_event0 = core_events.SimpleEvent(1)
        self.simple_event1 = core_events.SimpleEvent(2)
        self.simple_event2 = core_events.SimpleEvent(3)
        self.sequence: core_events.SequentialEvent[
            core_events.SimpleEvent
        ] = core_events.SequentialEvent(
            [
                self.simple_event0,
                self.simple_event1,
                self.simple_event2,
            ]
        )

    def tag_sequence(self) -> tuple[str, ...]:
        tag_sequence = "abc"
        for tag, item in zip(tag_sequence, self.sequence):
            item.tag = tag

        return tuple(tag_sequence)

    def get_event_class(self) -> typing.Type:
        return core_events.SequentialEvent

    def get_event_instance(self) -> core_events.SimpleEvent:
        return self.get_event_class()([])

    def test_getitem_index(self):
        self.assertEqual(self.simple_event0, self.sequence[0])
        self.assertEqual(self.simple_event1, self.sequence[1])
        self.assertEqual(self.simple_event2, self.sequence[2])

    def test_getitem_slice(self):
        self.assertEqual(
            core_events.SequentialEvent([self.simple_event0, self.simple_event1]),
            self.sequence[:2],
        )

    def test_getitem_tag(self):
        tag0, tag1, tag2 = self.tag_sequence()

        self.assertEqual(self.sequence[tag0], self.simple_event0)
        self.assertEqual(self.sequence[tag1], self.simple_event1)
        self.assertEqual(self.sequence[tag2], self.simple_event2)

    def test_setitem_index(self):
        simple_event = core_events.SimpleEvent(100).set("unique-id", 100)
        self.sequence[0] = simple_event
        self.assertEqual(self.sequence[0], simple_event)

    def test_setitem_tag(self):
        simple_event = core_events.SimpleEvent(100).set("unique-id", 100)
        tag0, tag1, tag2 = self.tag_sequence()
        self.sequence[tag1] = simple_event.set("tag", tag1)
        self.assertEqual(self.sequence[tag1], simple_event)

    def test_duration(self):
        self.assertEqual(self.sequence.duration, core_parameters.DirectDuration(6))

    def test_zero_duration(self):
        self.assertEqual(
            core_events.SequentialEvent().duration, core_parameters.DirectDuration(0)
        )

    def test_set(self):
        sequential_event = core_events.SequentialEvent(
            [core_events.SimpleEvent(1), core_events.SimpleEvent(1)]
        )
        self.assertEqual(sequential_event.duration, 2)

        sequential_event.set("duration", 10)
        self.assertEqual(sequential_event.duration, 10)
        self.assertEqual(sequential_event[0].duration, 5)
        self.assertEqual(sequential_event[1].duration, 5)

        sequential_event.set("new_attribute", "hello world!")
        self.assertEqual(sequential_event.new_attribute, "hello world!")

    def test_equal_with_different_side_attributes(self):
        """Ensure __eq__ takes _class_specific_side_attribute_tuple into account"""

        sequential_event0 = core_events.SequentialEvent([])
        sequential_event1 = core_events.SequentialEvent([])

        self.assertEqual(sequential_event0, sequential_event1)

        sequential_event0.tempo_envelope = core_events.TempoEnvelope(
            [[0, 100], [10, 100]]
        )

        self.assertNotEqual(
            sequential_event0.tempo_envelope, sequential_event1.tempo_envelope
        )
        self.assertNotEqual(sequential_event0, sequential_event1)
        self.assertTrue(list.__eq__(sequential_event0, sequential_event1))

    def test_metrize(self):
        """Minimal test to ensure API keeps stable

        Please consult EventToMetrizedEventTest for tests of actual
        functionality.
        """

        sequential_event = core_events.SequentialEvent(
            [
                core_events.SimpleEvent(
                    1, tempo_envelope=core_events.TempoEnvelope([[0, 120], [1, 120]])
                )
            ],
            tempo_envelope=core_events.TempoEnvelope([[0, 30], [1, 120]]),
        )
        self.assertEqual(
            sequential_event.metrize(mutate=False),
            core_converters.EventToMetrizedEvent().convert(sequential_event),
        )

    def test_concatenate_tempo_envelope(self):
        seq0 = self.get_event_class()(
            [core_events.SimpleEvent(1)],
            tempo_envelope=core_events.TempoEnvelope([[0, 20], [100, 30]]),
        )
        seq1 = self.get_event_class()(
            [core_events.SimpleEvent(2)],
            tempo_envelope=core_events.TempoEnvelope([[0, 50], [1, 10]]),
        )
        seq0._concatenate_tempo_envelope(seq1)
        self.assertEqual(seq0.tempo_envelope.value_tuple, (20, 30, 50, 10))
        self.assertEqual(
            seq0.tempo_envelope.absolute_time_in_floats_tuple, (0, 1, 1, 3)
        )

    def test_magic_method_add(self):
        self.assertEqual(
            type(core_events.SequentialEvent([]) + core_events.SequentialEvent([])),
            core_events.SequentialEvent,
        )

    def test_magic_method_add_children(self):
        """Ensure children and tempo envelope are concatenated"""
        seq, s = core_events.SequentialEvent, core_events.SimpleEvent
        seq0, seq1 = seq([s(1)]), seq([s(1), s(2)])
        seq_ok = seq(
            [s(1), s(1), s(2)],
            tempo_envelope=core_events.TempoEnvelope(
                [[0, 60], [1, 60], [1, 60], [4, 60]]
            ),
        )
        self.assertEqual(seq0 + seq1, seq_ok)

    def test_magic_method_mul(self):
        self.assertEqual(
            type(core_events.SequentialEvent([]) * 5), core_events.SequentialEvent
        )

    def test_magic_method_del_by_tag(self):
        s = core_events.SequentialEvent([core_events.TaggedSimpleEvent(1, tag="a")])
        del s["a"]
        self.assertEqual(s, core_events.SequentialEvent([]))

    def test_get_duration(self):
        self.assertEqual(self.sequence.duration, core_parameters.DirectDuration(6))

    def test_set_duration(self):
        self.sequence.duration = 3
        self.assertEqual(self.sequence[0].duration, core_parameters.DirectDuration(0.5))
        self.assertEqual(self.sequence[1].duration, core_parameters.DirectDuration(1))
        self.assertEqual(self.sequence[2].duration, core_parameters.DirectDuration(1.5))

    def test_set_duration_with_equal_event(self):
        simple_event = core_events.SimpleEvent(1)
        sequential_event = core_events.SequentialEvent([simple_event, simple_event])
        sequential_event.duration = 5
        self.assertEqual(sequential_event.duration, 5)
        self.assertEqual(sequential_event[0].duration, 2.5)
        self.assertEqual(sequential_event[1].duration, 2.5)

    def test_get_absolute_time_tuple(self):
        result = tuple(self.sequence.absolute_time_tuple)
        self.assertEqual(
            result,
            (
                core_parameters.DirectDuration(0),
                core_parameters.DirectDuration(1),
                core_parameters.DirectDuration(3),
            ),
        )

    def test_get_event_at(self):
        result = self.sequence.get_event_at(1.5)
        self.assertEqual(result, self.sequence[1])

    def test_get_event_at_for_unavailable_event(self):
        result_for_unavailable_event = self.sequence.get_event_at(100)
        self.assertEqual(result_for_unavailable_event, None)

    def test_get_event_at_for_unavailable_event_at_corner(self):
        self.assertEqual(self.sequence.get_event_at(6), None)

    def test_get_event_at_for_unavailable_event_before(self):
        self.assertEqual(self.sequence.get_event_at(-1), None)

    def test_cut_out(self):
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
            core_utilities.InvalidStartValueError,
            lambda: self.sequence.squash_in(
                7, core_events.SimpleEvent(1.5), mutate=False
            ),
        )

    def test_squash_in_with_minor_differences(self):
        minor_difference = fractions.Fraction(6e-10)
        self.assertEqual(
            self.sequence.squash_in(
                minor_difference, core_events.SimpleEvent(1), mutate=False
            ),
            core_events.SequentialEvent(
                [
                    core_events.SimpleEvent(duration)
                    for duration in (minor_difference, 1, 2 - minor_difference, 3)
                ]
            ),
        )

    def test_squash_in_event_with_0_duration(self):
        squashed_in_sequence = self.sequence.squash_in(
            1, core_events.SimpleEvent(0), mutate=False
        )
        self.assertEqual(
            squashed_in_sequence,
            core_events.SequentialEvent(
                [core_events.SimpleEvent(duration) for duration in (1, 0, 2, 3)]
            ),
        )

        # Now ensure that when we squash_in, we will always be
        # before the old event (just like index
        # based squash_in: insert).

        # This still raises an error because of the problematic
        # behaviour of "get_event_index_at" -> that it doesn't
        # return events with duration = 0.

        squashed_in_sequence.squash_in(1, core_events.SimpleEvent(0).set("test", 100))
        self.assertEqual(squashed_in_sequence[1].get_parameter("test"), 100)

    def test_slide_in(self):
        s, se = core_events.SimpleEvent, core_events.SequentialEvent
        f = fractions.Fraction

        for start, event_to_slide_in, expected_sequential_event in (
            (0, s(100), se([s(100), s(1), s(2), s(3)])),
            (1, s(100), se([s(1), s(100), s(2), s(3)])),
            (2, s(100), se([s(1), s(1), s(100), s(1), s(3)])),
            (3, s(100), se([s(1), s(2), s(100), s(3)])),
            (4, s(100), se([s(1), s(2), s(1), s(100), s(2)])),
            (
                f(6e-10),
                s(100),
                se(
                    [
                        # Strange number due to floating point error :)
                        s(f(6.000000496442226e-10)),
                        s(100),
                        s(1 - f(6.000000496442226e-10)),
                        s(2),
                        s(3),
                    ]
                ),
            ),
        ):
            with self.subTest(start=start):
                self.assertEqual(
                    self.sequence.slide_in(start, event_to_slide_in, mutate=False),
                    expected_sequential_event,
                )

    def test_slide_in_with_invalid_start(self):
        s = core_events.SimpleEvent(1)
        self.assertRaises(
            core_utilities.SplitError, self.sequence.slide_in, -1, s
        )
        self.assertRaises(
            core_utilities.InvalidStartValueError, self.sequence.slide_in, 100, s
        )

    def test_tie_by(self):
        # Ensure empty event can be tied without error
        self.assertEqual(
            core_events.SequentialEvent([]).tie_by(
                lambda event_left, event_right: True
            ),
            core_events.SequentialEvent([]),
        )
        # Ensure tie_by function as expected
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
            core_utilities.SplitUnavailableChildError,
            lambda: self.sequence.split_child_at(1000),
        )

    def test_start_and_end_time_per_event(self):
        self.assertEqual(
            self.sequence.start_and_end_time_per_event,
            (
                ranges.Range(
                    core_parameters.DirectDuration(0), core_parameters.DirectDuration(1)
                ),
                ranges.Range(
                    core_parameters.DirectDuration(1), core_parameters.DirectDuration(3)
                ),
                ranges.Range(
                    core_parameters.DirectDuration(3), core_parameters.DirectDuration(6)
                ),
            ),
        )

    def test_extend_until(self):
        s, se = core_events.SimpleEvent, core_events.SequentialEvent

        self.assertEqual(
            self.sequence.extend_until(100, mutate=False), se([s(1), s(2), s(3), s(94)])
        )

        # Do nothing if already long enough
        self.assertEqual(self.sequence.extend_until(6), se([s(1), s(2), s(3)]))

        # Change in place
        self.assertEqual(self.sequence.extend_until(7), se([s(1), s(2), s(3), s(1)]))
        self.assertEqual(self.sequence, se([s(1), s(2), s(3), s(1)]))

        # Do nothing if already longer
        self.assertEqual(self.sequence.extend_until(4), se([s(1), s(2), s(3), s(1)]))

        # Use custom event generator
        self.assertEqual(
            self.sequence.extend_until(8, duration_to_white_space=lambda d: se([s(d)])),
            se([s(1), s(2), s(3), s(1), se([s(1)])]),
        )


class SimultaneousEventTest(unittest.TestCase, EventTest):
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

    def get_event_class(self) -> typing.Type:
        return core_events.SimultaneousEvent

    def get_event_instance(self) -> core_events.SimpleEvent:
        return self.get_event_class()([])

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

    def test_duration(self):
        self.assertEqual(self.sequence.duration, core_parameters.DirectDuration(3))

    def test_nested_event_duration(self):
        self.assertEqual(
            self.nested_sequence.duration, core_parameters.DirectDuration(6)
        )

    def test_zero_duration(self):
        self.assertEqual(
            core_events.SimultaneousEvent().duration, core_parameters.DirectDuration(0)
        )

    def test_get_event_from_index_sequence(self):
        self.assertEqual(
            self.sequence.get_event_from_index_sequence((0,)), self.sequence[0]
        )
        self.assertEqual(self.sequence.get_event_from_index_sequence([]), self.sequence)

    def test_get_duration(self):
        self.assertEqual(self.sequence.duration, core_parameters.DirectDuration(3))

    def test_set_duration(self):
        self.sequence.duration = 1.5
        self.assertEqual(self.sequence[0].duration, core_parameters.DirectDuration(0.5))
        self.assertEqual(self.sequence[1].duration, core_parameters.DirectDuration(1))
        self.assertEqual(self.sequence[2].duration, core_parameters.DirectDuration(1.5))

        nested_sequence = self.nested_sequence.copy()

        nested_sequence.duration = 3

        self.assertEqual(nested_sequence[0].duration, 3)
        self.assertEqual(nested_sequence[1].duration, 3)

        for sequential_event in nested_sequence:
            self.assertEqual(sequential_event[0].duration, 0.5)
            self.assertEqual(sequential_event[1].duration, 1)
            self.assertEqual(sequential_event[2].duration, 1.5)

        nested_sequence.duration = 6
        self.assertEqual(nested_sequence, self.nested_sequence)

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
        self.assertEqual(
            result,
            (
                core_parameters.DirectDuration(1),
                core_parameters.DirectDuration(2),
                core_parameters.DirectDuration(3),
            ),
        )

    def test_get_nested_parameter(self):
        result = self.nested_sequence.get_parameter("duration")
        duration_tuple = (
            core_parameters.DirectDuration(1),
            core_parameters.DirectDuration(2),
            core_parameters.DirectDuration(3),
        )
        self.assertEqual(result, (duration_tuple, duration_tuple))

    def test_get_flat_parameter(self):
        result = self.nested_sequence.get_parameter("duration", flat=True)
        self.assertEqual(
            result,
            tuple(
                core_parameters.DirectDuration(duration)
                for duration in (1, 2, 3, 1, 2, 3)
            ),
        )

    def test_get_parameter_but_filter_undefined(self):
        sequential_event = core_events.SequentialEvent(
            [core_events.SimpleEvent(1), core_events.SimpleEvent(2)]
        )
        sequential_event[0].set("name", "event0")
        self.assertEqual(sequential_event.get_parameter("name"), ("event0", None))
        self.assertEqual(
            sequential_event.get_parameter("name", filter_undefined=True), ("event0",)
        )

    def test_set_parameter(self):
        self.sequence.set_parameter("duration", lambda x: x * 2)
        self.assertEqual(
            self.sequence.get_parameter("duration"),
            (
                core_parameters.DirectDuration(2),
                core_parameters.DirectDuration(4),
                core_parameters.DirectDuration(6),
            ),
        )

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

    def test_cut_out(self):
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
        self.assertRaises(
            core_utilities.InvalidCutOutStartAndEndValuesError,
            lambda: self.sequence.cut_out(2, 3),
        )

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
            core_utilities.ImpossibleToSquashInError,
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

    def test_slide_in(self):
        s, si, se = (
            core_events.SimpleEvent,
            core_events.SimultaneousEvent,
            core_events.SequentialEvent,
        )

        for start, event_to_slide_in, expected_simultaneous_event in (
            (0, s(100), si([se([s(100), s(1), s(2), s(3)])] * 2)),
            (1, s(100), si([se([s(1), s(100), s(2), s(3)])] * 2)),
            (2, s(100), si([se([s(1), s(1), s(100), s(1), s(3)])] * 2)),
        ):
            with self.subTest(start=start):
                self.assertEqual(
                    self.nested_sequence.slide_in(
                        start, event_to_slide_in, mutate=False
                    ),
                    expected_simultaneous_event,
                )

    def test_slide_in_exception(self):
        self.assertRaises(
            core_utilities.ImpossibleToSlideInError,
            self.sequence.slide_in,
            0,
            core_events.SimpleEvent(1),
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

    def test_remove_by(self):
        simultaneous_event_to_filter = core_events.SimultaneousEvent(
            [
                core_events.SimpleEvent(1),
                core_events.SimpleEvent(3),
                core_events.SimpleEvent(2),
            ]
        )
        simultaneous_event_to_filter.remove_by(
            lambda event: event.duration > core_parameters.DirectDuration(2)
        )
        self.assertEqual(
            simultaneous_event_to_filter,
            core_events.SimultaneousEvent([core_events.SimpleEvent(3)]),
        )

    def test_extend_until(self):
        s, se, si = (
            core_events.SimpleEvent,
            core_events.SequentialEvent,
            core_events.SimultaneousEvent,
        )

        # Extend simple events inside simultaneous event..
        self.assertEqual(
            self.sequence.extend_until(10, mutate=False), si([s(10), s(10), s(10)])
        )

        # ..should raise if flag is set to False
        self.assertRaises(
            core_utilities.ImpossibleToExtendUntilError,
            self.sequence.extend_until,
            10,
            prolong_simple_event=False,
        )

        # We can't call 'extend_until' on an empty SimultaneousEvent: this would
        # raise an error.
        self.assertRaises(
            core_utilities.IneffectiveExtendUntilError, si().extend_until, 10
        )

        # Extend sequential events inside simultaneous event..
        ese = se([s(1), s(2), s(3), s(4)])  # extended sequential event
        self.assertEqual(
            self.nested_sequence.extend_until(10, mutate=False), si([ese, ese])
        )

        # Nothing happens if already long enough
        self.assertEqual(
            self.nested_sequence.extend_until(4, mutate=False), self.nested_sequence
        )

        # Check default value for SimultaneousEvent
        self.assertEqual(si([s(1), s(3)]).extend_until(), si([s(3), s(3)]))

    def test_concatenate_by_index(self):
        # In this test we call 'metrize()' on each concatenated
        # event, so for each layer 'reset_tempo_envelope' is called
        # and we don't have to provide the concatenated tempo envelope
        # (which is != the default tempo envelope when constructing events).
        #
        # We already carefully test the tempo_envelope concatenation
        # feature of 'conatenate_by_tag' in
        # 'test_concatenate_by_index_persists_tempo_envelope'.
        s, se, si = (
            core_events.SimpleEvent,
            core_events.SequentialEvent,
            core_events.SimultaneousEvent,
        )

        # Equal size concatenation
        self.assertEqual(
            self.nested_sequence.concatenate_by_index(
                self.nested_sequence, mutate=False
            ).metrize(),
            si(
                [
                    se([s(1), s(2), s(3), s(1), s(2), s(3)]),
                    se([s(1), s(2), s(3), s(1), s(2), s(3)]),
                ]
            ),
        )

        # Smaller self
        si_test = si([se([s(1), s(1)])])
        si_ok = si(
            [
                se([s(1), s(1), s(1), s(2), s(3)]),
                se([s(2), s(1), s(2), s(3)]),
            ]
        )
        self.assertEqual(
            si_test.concatenate_by_index(self.nested_sequence).metrize(), si_ok
        )
        #   Mutate inplace!
        self.assertEqual(si_test, si_ok)

        # Smaller other
        si_test = si([se([s(1), s(1)]), se([s(0.5)]), se([s(2)])])
        si_ok = si(
            [
                se([s(1), s(1), s(1), s(2), s(3)]),
                se([s(0.5), s(1.5), s(1), s(2), s(3)]),
                se([s(2)]),
            ]
        )
        self.assertEqual(
            si_test.concatenate_by_index(self.nested_sequence).metrize(), si_ok
        )

    def test_concatenate_by_index_exception(self):
        self.assertRaises(
            core_utilities.ConcatenationError,
            self.sequence.concatenate_by_index,
            self.sequence,
        )

    def test_concatenate_by_index_to_empty_event(self):
        empty_se = core_events.SimultaneousEvent([])
        filled_se = core_events.SimultaneousEvent(
            [core_events.SequentialEvent([core_events.SimpleEvent(1)])]
        )
        empty_se.concatenate_by_index(filled_se)
        self.assertEqual(empty_se, filled_se)

    def test_concatenate_by_index_persists_tempo_envelope(self):
        """Verify that concatenation also concatenates the tempos"""
        sim0 = core_events.SimultaneousEvent(
            [
                core_events.SequentialEvent(
                    [core_events.SimpleEvent(1)],
                    tempo_envelope=core_events.TempoEnvelope([[0, 1], [10, 100]]),
                )
            ]
        )
        sim1 = core_events.SimultaneousEvent(
            [
                core_events.SequentialEvent(
                    [core_events.SimpleEvent(1)],
                    tempo_envelope=core_events.TempoEnvelope([[0, 1000], [1, 10]]),
                )
            ]
        )
        sim0.concatenate_by_index(sim1)
        self.assertEqual(sim0[0].tempo_envelope.value_tuple, (1, 100, 1000, 10))
        self.assertEqual(
            sim0[0].tempo_envelope.absolute_time_in_floats_tuple, (0, 1, 1, 2)
        )

    def test_concatenate_by_tag(self):
        s, tse, si, t = (
            core_events.SimpleEvent,
            core_events.TaggedSequentialEvent,
            core_events.SimultaneousEvent,
            core_events.TempoEnvelope,
        )

        s1 = si([tse([s(1), s(1)], tag="a")])
        s2 = si([tse([s(2), s(1)], tag="a"), tse([s(0.5)], tag="b")])

        # Concatenation tempo envelopes
        t0 = t([[0, 60], [2, 60], [2, 60], [4, 60]])
        t1 = t([[0, 60], [2, 60], [2, 60], [5, 60]])
        t2 = t([[0, 60], [3, 60], [3, 60], [5, 60]])

        # Equal size concatenation
        self.assertEqual(
            s1.concatenate_by_tag(s1, mutate=False),
            si([tse([s(1), s(1), s(1), s(1)], tag="a", tempo_envelope=t0)]),
        )

        # Smaller self
        s2.reverse()  # verify order doesn't matter
        self.assertEqual(
            s1.concatenate_by_tag(s2, mutate=False),
            si(
                [
                    tse([s(1), s(1), s(2), s(1)], tag="a", tempo_envelope=t1),
                    # Tempo envelope is default, because no ancestor existed
                    # (so '_concatenate_tempo_envelope' wasn't called)
                    tse([s(2), s(0.5)], tag="b"),
                ]
            ),
        )

        # Smaller other
        s2.reverse()  # reverse to original order
        self.assertEqual(
            s2.concatenate_by_tag(s1, mutate=False),
            si(
                [
                    tse([s(2), s(1), s(1), s(1)], tag="a", tempo_envelope=t2),
                    # Tempo envelope is default, because no successor existed
                    # (so '_concatenate_tempo_envelope' wasn't called)
                    tse([s(0.5), s(2.5)], tag="b"),
                ]
            ),
        )

    def test_concatenate_by_tag_exception(self):
        self.assertRaises(
            core_utilities.NoTagError,
            self.sequence.concatenate_by_tag,
            self.sequence,
        )

        s1 = core_events.SimultaneousEvent([core_events.TaggedSimpleEvent(1, tag="a")])
        self.assertRaises(
            core_utilities.ConcatenationError,
            s1.concatenate_by_tag,
            s1,
        )

    def test_concatenate_by_tag_to_empty_event(self):
        empty_se = core_events.SimultaneousEvent([])
        filled_se = core_events.SimultaneousEvent(
            [core_events.TaggedSequentialEvent([core_events.SimpleEvent(1)], tag="t")]
        )
        empty_se.concatenate_by_tag(filled_se)
        self.assertEqual(empty_se, filled_se)

    def test_sequentialize_empty_event(self):
        self.assertEqual(
            core_events.SimultaneousEvent([]).sequentialize(),
            core_events.SequentialEvent([]),
        )

    def test_sequentialize_simple_event(self):
        e = core_events.SimultaneousEvent(
            [core_events.SimpleEvent(3), core_events.SimpleEvent(1)]
        )
        e_sequentialized = core_events.SequentialEvent(
            [
                core_events.SimultaneousEvent(
                    [core_events.SimpleEvent(1), core_events.SimpleEvent(1)]
                ),
                core_events.SimultaneousEvent([core_events.SimpleEvent(2)]),
            ]
        )
        self.assertEqual(e.sequentialize(), e_sequentialized)

    def test_sequentialize_sequential_event(self):
        seq, sim, s = (
            core_events.SequentialEvent,
            core_events.SimultaneousEvent,
            core_events.SimpleEvent,
        )
        e = sim(
            [
                seq([s(2), s(1)]),
                seq([s(3)]),
            ]
        )
        e_sequentialized = seq(
            [
                sim([seq([s(2)]), seq([s(2)])]),
                sim([seq([s(1)]), seq([s(1)])]),
            ]
        )
        self.assertEqual(e.sequentialize(), e_sequentialized)

    def test_sequentialize_simultaneous_event(self):
        seq, sim, s = (
            core_events.SequentialEvent,
            core_events.SimultaneousEvent,
            core_events.SimpleEvent,
        )
        e = sim(
            [
                sim([s(3)]),
                sim([s(1)]),
            ]
        )
        e_sequentialized = seq(
            [
                sim([sim([s(1)]), sim([s(1)])]),
                sim([sim([s(2)])]),
            ]
        )
        self.assertEqual(e.sequentialize(), e_sequentialized)


if __name__ == "__main__":
    unittest.main()
