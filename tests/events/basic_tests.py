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

    def setUp(self):
        self.event = self.get_event_instance()

    @abc.abstractmethod
    def get_event_class(self) -> typing.Type:
        ...

    @abc.abstractmethod
    def get_event_instance(self) -> core_events.abc.Event:
        ...

    def test_tempo_auto_initialization(self):
        self.assertTrue(bool(self.event.tempo))
        self.assertTrue(
            isinstance(self.event.tempo, core_parameters.abc.Tempo)
        )

    def test_tempo_auto_initialization_and_settable(self):
        self.event.tempo.bpm = 20
        self.assertEqual(self.event.tempo.bpm, 20)

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

    def test_split_at_out_of_range_time_ignored(self):
        # Error shouldn't be raised if 'ignore_invalid_split_point' is set.
        self.assertTrue(
            self.event.split_at(
                self.event.duration + 1, ignore_invalid_split_point=True
            )
        )

    def test_split_at_split_time_order_does_not_matter(self):
        d = self.event.duration
        chr0, chr1 = d / 3, d / 2
        self.assertEqual(self.event.split_at(chr0, chr1), self.event.split_at(chr1, chr0))

    def test_split_at_empty(self):
        self.assertRaises(core_utilities.NoSplitTimeError, self.event.split_at)

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
            core_events.Chronon(1),
        )

    def test_squash_in_invalid_absolute_time(self):
        self.assertRaises(
            core_utilities.InvalidAbsoluteTime,
            self.event.squash_in,
            -1,
            core_events.Chronon(1),
        )

    def test_split_child_at(self):
        self.assertRaises(
            core_utilities.InvalidAbsoluteTime, self.event.split_child_at, -1
        )


class ChrononTest(unittest.TestCase, EventTest):
    def setUp(self) -> None:
        EventTest.setUp(self)

    def get_event_class(self) -> typing.Type:
        return core_events.Chronon

    def get_event_instance(self) -> core_events.Chronon:
        return self.get_event_class()(10)

    def test_copy(self):
        chronon0 = core_events.Chronon(20)
        chronon1 = chronon0.copy()
        chronon1.duration = 300

        self.assertEqual(chronon0.duration.beat_count, 20)
        self.assertEqual(chronon1.duration.beat_count, 300)

    def test_set(self):
        chronon = core_events.Chronon(1)
        self.assertEqual(chronon.duration, 1)

        chronon.set("duration", 10)
        self.assertEqual(chronon.duration, 10)

        chronon.set("new_attribute", "hello world!")
        self.assertEqual(chronon.new_attribute, "hello world!")

    def test_metrize(self):
        """Minimal test to ensure API keeps stable

        Please consult EventToMetrizedEventTest for tests of actual
        functionality.
        """

        chronon = core_events.Chronon(
            1, tempo=core_parameters.FlexTempo([[0, 30], [1, 120]])
        )
        self.assertEqual(
            chronon.copy().metrize(),
            core_converters.EventToMetrizedEvent().convert(chronon),
        )

    def test_reset_tempo(self):
        chronon = self.get_event_instance()
        chronon.tempo.bpm = 20
        self.assertEqual(chronon.tempo.bpm, 20)
        chronon.reset_tempo()
        self.assertEqual(chronon.tempo.bpm, 60)

    def test_get_assigned_parameter(self):
        duration = core_parameters.DirectDuration(10)
        self.assertEqual(
            core_events.Chronon(duration).get_parameter("duration"), duration
        )

    def test_get_not_assigned_parameter(self):
        self.assertEqual(core_events.Chronon(1).get_parameter("anyParameter"), None)

    def test_get_flat_assigned_parameter(self):
        duration = core_parameters.DirectDuration(10)
        self.assertEqual(
            core_events.Chronon(duration).get_parameter("duration", flat=True),
            duration,
        )

    def test_set_assigned_parameter_by_object(self):
        chronon = core_events.Chronon(1)
        duration = core_parameters.DirectDuration(10)
        chronon.set_parameter("duration", duration)
        self.assertEqual(chronon.duration, duration)

    def test_set_assigned_parameter_by_function(self):
        old_duration = 1
        chronon = core_events.Chronon(old_duration)
        chronon.set_parameter("duration", lambda old_duration: old_duration * 2)
        self.assertEqual(
            chronon.duration, core_parameters.DirectDuration(old_duration * 2)
        )

    def test_set_not_assigned_parameter(self):
        chronon = core_events.Chronon(1)
        new_unknown_parameter = 10
        new_unknown_parameter_name = "new"
        chronon.set_parameter(
            "new", new_unknown_parameter, set_unassigned_parameter=True
        )
        self.assertEqual(
            chronon.get_parameter(new_unknown_parameter_name),
            new_unknown_parameter,
        )

    def test_parameter_to_compare_tuple(self):
        chronon = core_events.Chronon(1)
        expected_parameter_to_compare_tuple = ("duration", "tag", "tempo")
        self.assertEqual(
            chronon._parameter_to_compare_tuple,
            expected_parameter_to_compare_tuple,
        )

    def test_equality_check(self):
        chronon0 = core_events.Chronon(2)
        chronon1 = core_events.Chronon(3)
        chronon2 = core_events.Chronon(2)
        chronon3 = core_events.Chronon(2.3)

        self.assertEqual(chronon0, chronon2)
        self.assertEqual(chronon2, chronon0)  # different order
        self.assertEqual(chronon0, chronon0)
        self.assertEqual(chronon2, chronon2)

        self.assertNotEqual(chronon0, chronon1)
        self.assertNotEqual(chronon1, chronon0)  # different order
        self.assertNotEqual(chronon0, chronon3)
        self.assertNotEqual(chronon2, chronon3)
        self.assertNotEqual(chronon2, chronon2.duration)
        self.assertNotEqual(chronon0, [1, 2, 3])

    def test_cut_out(self):
        event0 = core_events.Chronon(4)
        cut_out_event0 = core_events.Chronon(2)

        event1 = core_events.Chronon(10)
        cut_out_event1 = core_events.Chronon(5)

        event2 = core_events.Chronon(5)
        cut_out_event2 = core_events.Chronon(1)

        event2.cut_out(2, 3)

        self.assertEqual(event0.copy().cut_out(2, 4).duration, cut_out_event0.duration)
        self.assertEqual(event1.copy().cut_out(0, 5).duration, cut_out_event1.duration)
        self.assertEqual(event2.duration, cut_out_event2.duration)

        # this will raise an error because the chronon isn't within the
        # asked range.
        self.assertRaises(
            core_utilities.InvalidCutOutStartAndEndValuesError,
            lambda: event0.cut_out(4, 5),
        )
        self.assertRaises(
            # -2 is smaller than 0, so this isn't a valid absolute time =>
            # error is raised.
            core_utilities.InvalidAbsoluteTime,
            lambda: event0.cut_out(-2, -1),
        )

    def test_cut_off(self):
        event0 = core_events.Chronon(4)
        cut_off_event0 = core_events.Chronon(2)

        event1 = core_events.Chronon(10)
        cut_off_event1 = core_events.Chronon(5)

        self.assertEqual(event0.copy().cut_off(0, 2), cut_off_event0)
        self.assertEqual(event0.copy().cut_off(2, 5), cut_off_event0)

        event1.cut_off(0, 5)
        self.assertEqual(event1, cut_off_event1)

    def test_split_at(self):
        event = core_events.Chronon(4)

        split0 = (core_events.Chronon(1), core_events.Chronon(3))
        split1 = (core_events.Chronon(2), core_events.Chronon(2))
        split2 = (core_events.Chronon(3), core_events.Chronon(1))

        self.assertEqual(event.split_at(1), split0)
        self.assertEqual(event.split_at(2), split1)
        self.assertEqual(event.split_at(3), split2)


class ConsecutionTest(unittest.TestCase, ComplexEventTest):
    def setUp(self):
        EventTest.setUp(self)
        self.chronon0 = core_events.Chronon(1)
        self.chronon1 = core_events.Chronon(2)
        self.chronon2 = core_events.Chronon(3)
        self.sequence: core_events.Consecution[
            core_events.Chronon
        ] = core_events.Consecution(
            [
                self.chronon0,
                self.chronon1,
                self.chronon2,
            ]
        )

    def tag_sequence(self) -> tuple[str, ...]:
        tag_sequence = "abc"
        for tag, item in zip(tag_sequence, self.sequence):
            item.tag = tag

        return tuple(tag_sequence)

    def get_event_class(self) -> typing.Type:
        return core_events.Consecution

    def get_event_instance(self) -> core_events.Chronon:
        return self.get_event_class()([core_events.Chronon(3)])

    def test_getitem_index(self):
        self.assertEqual(self.chronon0, self.sequence[0])
        self.assertEqual(self.chronon1, self.sequence[1])
        self.assertEqual(self.chronon2, self.sequence[2])

    def test_getitem_slice(self):
        self.assertEqual(
            core_events.Consecution([self.chronon0, self.chronon1]),
            self.sequence[:2],
        )

    def test_getitem_tag(self):
        tag0, tag1, tag2 = self.tag_sequence()

        self.assertEqual(self.sequence[tag0], self.chronon0)
        self.assertEqual(self.sequence[tag1], self.chronon1)
        self.assertEqual(self.sequence[tag2], self.chronon2)

    def test_setitem_index(self):
        chronon = core_events.Chronon(100).set("unique-id", 100)
        self.sequence[0] = chronon
        self.assertEqual(self.sequence[0], chronon)

    def test_setitem_tag(self):
        chronon = core_events.Chronon(100).set("unique-id", 100)
        tag0, tag1, tag2 = self.tag_sequence()
        self.sequence[tag1] = chronon.set("tag", tag1)
        self.assertEqual(self.sequence[tag1], chronon)

    def test_duration(self):
        self.assertEqual(self.sequence.duration, core_parameters.DirectDuration(6))

    def test_zero_duration(self):
        self.assertEqual(
            core_events.Consecution().duration, core_parameters.DirectDuration(0)
        )

    def test_set(self):
        consecution = core_events.Consecution(
            [core_events.Chronon(1), core_events.Chronon(1)]
        )
        self.assertEqual(consecution.duration, 2)

        consecution.set("duration", 10)
        self.assertEqual(consecution.duration, 10)
        self.assertEqual(consecution[0].duration, 5)
        self.assertEqual(consecution[1].duration, 5)

        consecution.set("new_attribute", "hello world!")
        self.assertEqual(consecution.new_attribute, "hello world!")

    def test_equal_with_different_side_attributes(self):
        """Ensure __eq__ takes _class_specific_side_attribute_tuple into account"""

        consecution0 = core_events.Consecution([])
        consecution1 = core_events.Consecution([])

        self.assertEqual(consecution0, consecution1)

        consecution0.tempo = core_parameters.FlexTempo(
            [[0, 100], [10, 100]]
        )

        self.assertNotEqual(
            consecution0.tempo, consecution1.tempo
        )
        self.assertNotEqual(consecution0, consecution1)
        self.assertTrue(list.__eq__(consecution0, consecution1))

    def test_metrize(self):
        """Minimal test to ensure API keeps stable

        Please consult EventToMetrizedEventTest for tests of actual
        functionality.
        """

        consecution = core_events.Consecution(
            [
                core_events.Chronon(
                    1, tempo=core_parameters.FlexTempo([[0, 120], [1, 120]])
                )
            ],
            tempo=core_parameters.FlexTempo([[0, 30], [1, 120]]),
        )
        self.assertEqual(
            consecution.copy().metrize(),
            core_converters.EventToMetrizedEvent().convert(consecution),
        )

    def test_concatenate_tempo(self):
        cons0 = self.get_event_class()(
            [core_events.Chronon(1)],
            tempo=core_parameters.FlexTempo([[0, 20], [1, 20], [3, 100]]),
        )
        cons1 = self.get_event_class()(
            [core_events.Chronon(2)],
            tempo=core_parameters.FlexTempo([[0, 50], [1, 10]]),
        )
        cons0._concatenate_tempo(cons1)
        self.assertEqual(cons0.tempo.value_tuple, (20, 20, 50, 10))
        self.assertEqual(
            cons0.tempo.absolute_time_in_floats_tuple, (0, 1, 1, 2)
        )

    def test_magic_method_add(self):
        self.assertEqual(
            type(core_events.Consecution([]) + core_events.Consecution([])),
            core_events.Consecution,
        )

    def test_magic_method_add_children(self):
        """Ensure children and tempos are concatenated"""
        cons, chr = core_events.Consecution, core_events.Chronon
        cons0 = cons([chr(1)], tempo=core_parameters.FlexTempo([[0, 50], [1, 50]]))
        cons1 = cons([chr(1), chr(2)])
        cons_ok = cons(
            [chr(1), chr(1), chr(2)],
            tempo=core_parameters.FlexTempo(
                [[0, 50], [1, 50], [1, 60], [2, 60]]
            ),
        )
        self.assertEqual(cons0 + cons1, cons_ok)

    def test_magic_method_mul(self):
        self.assertEqual(
            type(core_events.Consecution([]) * 5), core_events.Consecution
        )

    def test_magic_method_del_by_tag(self):
        cons = core_events.Consecution([core_events.Chronon(1, tag="a")])
        del cons["a"]
        self.assertEqual(cons, core_events.Consecution([]))

    def test_get_duration(self):
        self.assertEqual(self.sequence.duration, core_parameters.DirectDuration(6))

    def test_set_duration(self):
        self.sequence.duration = 3
        self.assertEqual(self.sequence[0].duration, core_parameters.DirectDuration(0.5))
        self.assertEqual(self.sequence[1].duration, core_parameters.DirectDuration(1))
        self.assertEqual(self.sequence[2].duration, core_parameters.DirectDuration(1.5))

    def test_set_duration_with_equal_event(self):
        chronon = core_events.Chronon(1)
        consecution = core_events.Consecution([chronon, chronon])
        consecution.duration = 5
        self.assertEqual(consecution.duration, 5)
        self.assertEqual(consecution[0].duration, 2.5)
        self.assertEqual(consecution[1].duration, 2.5)

    def test_set_duration_of_empty_event(self):
        consecution = core_events.Consecution([])
        self.assertRaises(
            core_utilities.CannotSetDurationOfEmptyComplexEvent,
            consecution.set,
            "duration",
            1,
        )

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
        result0 = core_events.Consecution(
            [
                core_events.Chronon(0.5),
                core_events.Chronon(2),
                core_events.Chronon(2),
            ]
        )
        result1 = core_events.Consecution([core_events.Chronon(1)])
        self.assertEqual(
            [event.duration for event in result0],
            [event.duration for event in self.sequence.copy().cut_out(0.5, 5)],
        )
        self.assertEqual(
            [event.duration for event in result1],
            [event.duration for event in self.sequence.copy().cut_out(1, 2)],
        )

    def test_cut_off(self):
        result0 = core_events.Consecution(
            [
                core_events.Chronon(0.5),
                core_events.Chronon(2),
                core_events.Chronon(3),
            ]
        )
        result1 = core_events.Consecution([core_events.Chronon(1)])
        result2 = core_events.Consecution(
            [core_events.Chronon(1), core_events.Chronon(0.75)]
        )
        self.assertEqual(
            [event.duration for event in result0],
            [event.duration for event in self.sequence.copy().cut_off(0.5, 1)],
        )
        self.assertEqual(
            [event.duration for event in result1],
            [event.duration for event in self.sequence.copy().cut_off(1, 6)],
        )
        self.assertEqual(
            [event.duration for event in result1],
            [event.duration for event in self.sequence.copy().cut_off(1, 7)],
        )
        self.assertEqual(
            [event.duration for event in result2],
            [event.duration for event in self.sequence.copy().cut_off(1.75, 7)],
        )

    def test_squash_in(self):
        self.assertEqual(
            self.sequence.copy().squash_in(0.5, core_events.Chronon(1)),
            core_events.Consecution(
                [core_events.Chronon(duration) for duration in (0.5, 1, 1.5, 3)]
            ),
        )
        self.assertEqual(
            self.sequence.copy().squash_in(5, core_events.Chronon(2)),
            core_events.Consecution(
                [core_events.Chronon(duration) for duration in (1, 2, 2, 2)]
            ),
        )
        self.assertEqual(
            self.sequence.copy().squash_in(0, core_events.Chronon(1.5)),
            core_events.Consecution(
                [core_events.Chronon(duration) for duration in (1.5, 1.5, 3)]
            ),
        )
        self.assertEqual(
            self.sequence.copy().squash_in(6, core_events.Chronon(1)),
            core_events.Consecution(
                [core_events.Chronon(duration) for duration in (1, 2, 3, 1)]
            ),
        )
        self.assertEqual(
            self.sequence.copy().squash_in(0.5, core_events.Chronon(0.25)),
            core_events.Consecution(
                [
                    core_events.Chronon(duration)
                    for duration in (0.5, 0.25, 0.25, 2, 3)
                ]
            ),
        )
        self.assertRaises(
            core_utilities.InvalidStartValueError,
            lambda: self.sequence.copy().squash_in(7, core_events.Chronon(1.5)),
        )

    def test_squash_in_with_minor_differences(self):
        minor_difference = fractions.Fraction(6e-10)
        self.assertEqual(
            self.sequence.copy().squash_in(
                minor_difference, core_events.Chronon(1)
            ),
            core_events.Consecution(
                [
                    core_events.Chronon(duration)
                    for duration in (minor_difference, 1, 2 - minor_difference, 3)
                ]
            ),
        )

    def test_squash_in_event_with_0_duration(self):
        squashed_in_sequence = self.sequence.copy().squash_in(
            1, core_events.Chronon(0)
        )
        self.assertEqual(
            squashed_in_sequence,
            core_events.Consecution(
                [core_events.Chronon(duration) for duration in (1, 0, 2, 3)]
            ),
        )

        # Now ensure that when we squash_in, we will always be
        # before the old event (just like index
        # based squash_in: insert).

        # This still raises an error because of the problematic
        # behaviour of "get_event_index_at" -> that it doesn't
        # return events with duration = 0.

        squashed_in_sequence.squash_in(1, core_events.Chronon(0).set("test", 100))
        self.assertEqual(squashed_in_sequence[1].get_parameter("test"), 100)

    def test_slide_in(self):
        s, se = core_events.Chronon, core_events.Consecution
        f = fractions.Fraction

        for start, event_to_slide_in, expected_consecution in (
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
                    self.sequence.copy().slide_in(start, event_to_slide_in),
                    expected_consecution,
                )

    def test_slide_in_with_invalid_start(self):
        chr = core_events.Chronon(1)
        self.assertRaises(
            core_utilities.InvalidAbsoluteTime, self.sequence.slide_in, -1, chr
        )
        self.assertRaises(
            core_utilities.InvalidStartValueError, self.sequence.slide_in, 100, chr
        )

    def test_tie_by(self):
        # Ensure empty event can be tied without error
        self.assertEqual(
            core_events.Consecution([]).tie_by(
                lambda event_left, event_right: True
            ),
            core_events.Consecution([]),
        )
        # Ensure tie_by function as expected
        self.assertEqual(
            self.sequence.copy().tie_by(
                lambda event_left, event_right: event_left.duration + 1
                == event_right.duration,
                event_type_to_examine=core_events.Chronon,
            ),
            core_events.Consecution(
                [core_events.Chronon(3), core_events.Chronon(3)]
            ),
        )
        self.assertEqual(
            self.sequence.copy().tie_by(
                lambda event_left, event_right: event_left.duration + 1
                == event_right.duration,
                lambda event_to_survive, event_to_remove: None,
                event_type_to_examine=core_events.Chronon,
                event_to_remove=False,
            ),
            core_events.Consecution([core_events.Chronon(3)]),
        )
        self.assertEqual(
            self.sequence.copy().tie_by(
                lambda event_left, event_right: event_left.duration + 1
                == event_right.duration,
                lambda event_to_survive, event_to_remove: None,
                event_type_to_examine=core_events.Chronon,
                event_to_remove=True,
            ),
            core_events.Consecution(
                [core_events.Chronon(1), core_events.Chronon(3)]
            ),
        )

    def test_tie_by_for_nested_events(self):
        nested_consecution0 = core_events.Consecution(
            [
                core_events.Consecution(
                    [core_events.Chronon(3), core_events.Chronon(2)]
                ),
                core_events.Consecution(
                    [core_events.Chronon(4), core_events.Chronon(2)]
                ),
            ]
        )
        nested_consecution0.tie_by(
            lambda event_left, event_right: event_left.duration - 1
            == event_right.duration,
            event_type_to_examine=core_events.Chronon,
            event_to_remove=True,
        )

        self.assertEqual(
            nested_consecution0,
            core_events.Consecution(
                [
                    core_events.Consecution([core_events.Chronon(5)]),
                    core_events.Consecution(
                        [core_events.Chronon(4), core_events.Chronon(2)]
                    ),
                ]
            ),
        )

        nested_consecution1 = core_events.Consecution(
            [
                core_events.Consecution(
                    [core_events.Chronon(3), core_events.Chronon(2)]
                ),
                core_events.Consecution([core_events.Chronon(5)]),
            ]
        )
        nested_consecution1.tie_by(
            lambda event_left, event_right: event_left.duration == event_right.duration,
            event_to_remove=True,
        )
        self.assertEqual(
            nested_consecution1,
            core_events.Consecution(
                [
                    core_events.Consecution(
                        [core_events.Chronon(6), core_events.Chronon(4)]
                    )
                ]
            ),
        )

    def test_split_child_at(self):
        consecution0 = core_events.Consecution([core_events.Chronon(3)])
        consecution0.split_child_at(1)
        consecution_to_compare0 = core_events.Consecution(
            [core_events.Chronon(1), core_events.Chronon(2)]
        )
        self.assertEqual(consecution0, consecution_to_compare0)

        consecution1 = core_events.Consecution(
            [core_events.Chronon(4), core_events.Chronon(1)]
        )
        consecution1.split_child_at(3)
        consecution_to_compare1 = core_events.Consecution(
            [
                core_events.Chronon(3),
                core_events.Chronon(1),
                core_events.Chronon(1),
            ]
        )
        self.assertEqual(consecution1, consecution_to_compare1)

        consecution2 = core_events.Consecution(
            [core_events.Chronon(3), core_events.Chronon(2)]
        )
        consecution2_copy = consecution2.copy()
        consecution2.split_at(3)
        self.assertEqual(consecution2, consecution2_copy)

    def test_split_child_at_unavailable_time(self):
        self.assertRaises(
            core_utilities.SplitUnavailableChildError,
            lambda: self.sequence.split_child_at(1000),
        )

    def test_split_at_multi(self):
        cons, chr = core_events.Consecution, core_events.Chronon
        # Only at already pre-defined split times.
        self.assertEqual(
            self.sequence.split_at(1, 3),
            (cons([chr(1)]), cons([chr(2)]), cons([chr(3)])),
        )
        # Here mutwo really needs to split.
        self.assertEqual(
            self.sequence.split_at(2, 3),
            (cons([chr(1), chr(1)]), cons([chr(1)]), cons([chr(3)])),
        )
        self.assertEqual(
            self.sequence.split_at(2, 3, 5, 5.5),
            (cons([chr(1), chr(1)]), cons([chr(1)]), cons([chr(2)]), cons([chr(0.5)]), cons([chr(0.5)])),
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
        s, se = core_events.Chronon, core_events.Consecution

        self.assertEqual(
            self.sequence.copy().extend_until(100), se([s(1), s(2), s(3), s(94)])
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


class ConcurrenceTest(unittest.TestCase, ComplexEventTest):
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
        return core_events.Concurrence

    def get_event_instance(self) -> core_events.Chronon:
        return self.get_event_class()(
            [
                core_events.Chronon(3),
                core_events.Consecution([core_events.Chronon(2)]),
            ]
        )

    def setUp(self) -> None:
        EventTest.setUp(self)
        self.sequence: core_events.Concurrence[
            core_events.Chronon
        ] = core_events.Concurrence(
            [
                core_events.Chronon(1),
                core_events.Chronon(2),
                core_events.Chronon(3),
            ]
        )
        self.nested_sequence: core_events.Concurrence[
            core_events.Consecution[core_events.Chronon]
        ] = core_events.Concurrence(
            [
                core_events.Consecution(
                    [
                        core_events.Chronon(1),
                        core_events.Chronon(2),
                        core_events.Chronon(3),
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
            core_events.Concurrence().duration, core_parameters.DirectDuration(0)
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

        for consecution in nested_sequence:
            self.assertEqual(consecution[0].duration, 0.5)
            self.assertEqual(consecution[1].duration, 1)
            self.assertEqual(consecution[2].duration, 1.5)

        nested_sequence.duration = 6
        self.assertEqual(nested_sequence, self.nested_sequence)

    def test_destructive_copy(self):
        chronon = core_events.Chronon(2)
        concurrence = core_events.Concurrence([chronon, chronon])
        copied_concurrence = concurrence.destructive_copy()
        copied_concurrence[0].duration = 10
        self.assertNotEqual(
            copied_concurrence[0].duration, copied_concurrence[1].duration
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
        consecution = core_events.Consecution(
            [core_events.Chronon(1), core_events.Chronon(2)]
        )
        consecution[0].set("name", "event0")
        self.assertEqual(consecution.get_parameter("name"), ("event0", None))
        self.assertEqual(
            consecution.get_parameter("name", filter_undefined=True), ("event0",)
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
        chronon_tuple = (
            core_events.Chronon(1),
            core_events.Chronon(1),
            core_events.Chronon(2),
        )
        for chronon, dummy_parameter in zip(
            chronon_tuple, dummy_parameter_tuple
        ):
            if dummy_parameter is not None:
                chronon.dummy_parameter = dummy_parameter  # type: ignore
        concurrence = core_events.Concurrence(
            chronon_tuple
        ).destructive_copy()
        concurrence.mutate_parameter(
            "dummy_parameter",
            lambda dummy_parameter: dummy_parameter.double_value(),
        )
        for event, dummy_parameter in zip(concurrence, dummy_parameter_tuple):
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
        result = core_events.Concurrence(
            [core_events.Chronon(0.5) for _ in range(3)]
        )

        self.assertEqual(
            [event.duration for event in result],
            [event.duration for event in self.sequence.copy().cut_out(0.5, 1)],
        )
        self.assertEqual(
            [event.duration for event in result],
            [event.duration for event in self.sequence.copy().cut_out(0, 0.5)],
        )
        self.assertEqual(
            [event.duration for event in result],
            [event.duration for event in self.sequence.copy().cut_out(0.25, 0.75)],
        )

        # this will raise an error because the concurrence contains chronons
        # where some chronon aren't long enough for the following cut up arguments.
        self.assertRaises(
            core_utilities.InvalidCutOutStartAndEndValuesError,
            lambda: self.sequence.cut_out(2, 3),
        )

    def test_cut_off(self):
        result0 = core_events.Concurrence(
            [core_events.Chronon(duration) for duration in (0.5, 1.5, 2.5)]
        )
        result1 = core_events.Concurrence(
            [core_events.Chronon(duration) for duration in (1, 2, 2.5)]
        )

        self.assertEqual(
            [event.duration for event in result0],
            [event.duration for event in self.sequence.copy().cut_off(0, 0.5)],
        )
        self.assertEqual(
            [event.duration for event in result1],
            [event.duration for event in self.sequence.copy().cut_off(2.5, 3)],
        )

    def test_squash_in(self):
        self.assertRaises(
            core_utilities.ImpossibleToSquashInError,
            lambda: self.sequence.copy().squash_in(0, core_events.Chronon(1.5)),
        )

        concurrence_to_test = core_events.Concurrence(
            [
                core_events.Consecution(
                    [core_events.Chronon(duration) for duration in (2, 3)]
                ),
                core_events.Consecution(
                    [core_events.Chronon(duration) for duration in (1, 1, 1, 2)]
                ),
            ]
        )
        expected_concurrence = core_events.Concurrence(
            [
                core_events.Consecution(
                    [core_events.Chronon(duration) for duration in (1, 1.5, 2.5)]
                ),
                core_events.Consecution(
                    [core_events.Chronon(duration) for duration in (1, 1.5, 0.5, 2)]
                ),
            ]
        )

        self.assertEqual(
            concurrence_to_test.copy().squash_in(
                1, core_events.Chronon(1.5)
            ),
            expected_concurrence,
        )

    def test_slide_in(self):
        s, si, se = (
            core_events.Chronon,
            core_events.Concurrence,
            core_events.Consecution,
        )

        for start, event_to_slide_in, expected_concurrence in (
            (0, s(100), si([se([s(100), s(1), s(2), s(3)])] * 2)),
            (1, s(100), si([se([s(1), s(100), s(2), s(3)])] * 2)),
            (2, s(100), si([se([s(1), s(1), s(100), s(1), s(3)])] * 2)),
        ):
            with self.subTest(start=start):
                self.assertEqual(
                    self.nested_sequence.copy().slide_in(start, event_to_slide_in),
                    expected_concurrence,
                )

    def test_slide_in_exception(self):
        self.assertRaises(
            core_utilities.ImpossibleToSlideInError,
            self.sequence.slide_in,
            0,
            core_events.Chronon(1),
        )

    def test_split_child_at(self):
        concurrence0 = core_events.Concurrence(
            [core_events.Consecution([core_events.Chronon(3)])]
        )
        concurrence0.split_child_at(1)
        concurrence_to_compare0 = core_events.Concurrence(
            [
                core_events.Consecution(
                    [core_events.Chronon(1), core_events.Chronon(2)]
                )
            ]
        )
        self.assertEqual(concurrence0, concurrence_to_compare0)

    def test_remove_by(self):
        concurrence_to_filter = core_events.Concurrence(
            [
                core_events.Chronon(1),
                core_events.Chronon(3),
                core_events.Chronon(2),
            ]
        )
        concurrence_to_filter.remove_by(
            lambda event: event.duration > core_parameters.DirectDuration(2)
        )
        self.assertEqual(
            concurrence_to_filter,
            core_events.Concurrence([core_events.Chronon(3)]),
        )

    def test_extend_until(self):
        s, se, si = (
            core_events.Chronon,
            core_events.Consecution,
            core_events.Concurrence,
        )

        # Extend chronons inside concurrence..
        self.assertEqual(
            self.sequence.copy().extend_until(10), si([s(10), s(10), s(10)])
        )

        # ..should raise if flag is set to False
        self.assertRaises(
            core_utilities.ImpossibleToExtendUntilError,
            self.sequence.extend_until,
            10,
            prolong_chronon=False,
        )

        # We can't call 'extend_until' on an empty Concurrence: this would
        # raise an error.
        self.assertRaises(
            core_utilities.IneffectiveExtendUntilError, si().extend_until, 10
        )

        # Extend consecutions inside concurrence..
        ese = se([s(1), s(2), s(3), s(4)])  # extended consecution
        self.assertEqual(self.nested_sequence.copy().extend_until(10), si([ese, ese]))

        # Nothing happens if already long enough
        self.assertEqual(
            self.nested_sequence.copy().extend_until(4), self.nested_sequence
        )

        # Check default value for Concurrence
        self.assertEqual(si([s(1), s(3)]).extend_until(), si([s(3), s(3)]))

    def test_concatenate_by_index(self):
        # In this test we call 'metrize()' on each concatenated
        # event, so for each layer 'reset_tempo' is called
        # and we don't have to provide the concatenated tempo
        # (which is != the default tempo when constructing events).
        #
        # We already carefully test the tempo concatenation
        # feature of 'conatenate_by_tag' in
        # 'test_concatenate_by_index_persists_tempo'.
        s, se, si = (
            core_events.Chronon,
            core_events.Consecution,
            core_events.Concurrence,
        )

        # Equal size concatenation
        self.assertEqual(
            self.nested_sequence.copy()
            .concatenate_by_index(self.nested_sequence)
            .metrize(),
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
        empty_conc = core_events.Concurrence([])
        filled_conc = core_events.Concurrence(
            [core_events.Consecution([core_events.Chronon(1)])]
        )
        empty_conc.concatenate_by_index(filled_conc)
        self.assertEqual(empty_conc, filled_conc)

    def test_concatenate_by_index_persists_tempo(self):
        """Verify that concatenation also concatenates the tempos"""
        conc0 = core_events.Concurrence(
            [
                core_events.Consecution(
                    [core_events.Chronon(1)],
                    tempo=core_parameters.FlexTempo(
                        [[0, 1], [1, 20], [10, 100]]
                    ),
                )
            ]
        )
        conc1 = core_events.Concurrence(
            [
                core_events.Consecution(
                    [core_events.Chronon(1)],
                    tempo=core_parameters.FlexTempo([[0, 1000], [1, 10]]),
                )
            ]
        )
        conc0.concatenate_by_index(conc1)
        self.assertEqual(conc0[0].tempo.value_tuple, (1, 20, 1000, 10))
        self.assertEqual(
            conc0[0].tempo.absolute_time_in_floats_tuple, (0, 1, 1, 2)
        )

    def test_concatenate_by_tag(self):
        s, tse, si, t = (
            core_events.Chronon,
            core_events.Consecution,
            core_events.Concurrence,
            core_parameters.FlexTempo,
        )

        chr1 = si([tse([s(1), s(1)], tag="a", tempo=t([[0, 50], [1, 50]]))])
        chr2 = si([tse([s(2), s(1)], tag="a"), tse([s(0.5)], tag="b")])

        # Concatenation flex tempos
        t0 = t([[0, 50], [1, 50], [2, 50], [2, 50], [3, 50]])
        t1 = t([[0, 50], [1, 50], [2, 50], [2, 60], [3, 60]])
        t2 = t([[0, 60], [1, 60], [3, 60], [3, 50], [4, 50]])

        # Equal size concatenation
        self.assertEqual(
            chr1.copy().concatenate_by_tag(chr1),
            si([tse([s(1), s(1), s(1), s(1)], tag="a", tempo=t0)]),
        )

        # Smaller self
        chr2.reverse()  # verify order doesn't matter
        self.assertEqual(
            chr1.copy().concatenate_by_tag(chr2),
            si(
                [
                    tse([s(1), s(1), s(2), s(1)], tag="a", tempo=t1),
                    # Tempo envelope is default, because no ancestor existed
                    # (so '_concatenate_tempo' wasn't called)
                    tse([s(2), s(0.5)], tag="b"),
                ]
            ),
        )

        # Smaller other
        chr2.reverse()  # reverse to original order
        self.assertEqual(
            chr2.copy().concatenate_by_tag(chr1),
            si(
                [
                    tse([s(2), s(1), s(1), s(1)], tag="a", tempo=t2),
                    # Tempo envelope is default, because no successor existed
                    # (so '_concatenate_tempo' wasn't called)
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

        chr1 = core_events.Concurrence([core_events.Chronon(1, tag="a")])
        self.assertRaises(
            core_utilities.ConcatenationError,
            chr1.concatenate_by_tag,
            chr1,
        )

    def test_concatenate_by_tag_to_empty_event(self):
        empty_se = core_events.Concurrence([])
        filled_se = core_events.Concurrence(
            [core_events.Consecution([core_events.Chronon(1)], tag="t")]
        )
        empty_se.concatenate_by_tag(filled_se)
        self.assertEqual(empty_se, filled_se)

    def test_sequentialize_empty_event(self):
        self.assertEqual(
            core_events.Concurrence([]).sequentialize(),
            core_events.Consecution([]),
        )

    def test_sequentialize_chronon(self):
        e = core_events.Concurrence(
            [core_events.Chronon(3), core_events.Chronon(1)]
        )
        e_sequentialized = core_events.Consecution(
            [
                core_events.Concurrence(
                    [core_events.Chronon(1), core_events.Chronon(1)]
                ),
                core_events.Concurrence([core_events.Chronon(2)]),
            ]
        )
        self.assertEqual(e.sequentialize(), e_sequentialized)

    def test_sequentialize_consecution(self):
        cons, conc, chr = (
            core_events.Consecution,
            core_events.Concurrence,
            core_events.Chronon,
        )
        e = conc(
            [
                cons([chr(2), chr(1)]),
                cons([chr(3)]),
            ]
        )
        e_sequentialized = cons(
            [
                conc([cons([chr(2)]), cons([chr(2)])]),
                conc([cons([chr(1)]), cons([chr(1)])]),
            ]
        )
        self.assertEqual(e.sequentialize(), e_sequentialized)

    def test_sequentialize_concurrence(self):
        cons, conc, chr = (
            core_events.Consecution,
            core_events.Concurrence,
            core_events.Chronon,
        )
        e = conc(
            [
                conc([chr(3)]),
                conc([chr(1)]),
            ]
        )
        e_sequentialized = cons(
            [
                conc([conc([chr(1)]), conc([chr(1)])]),
                conc([conc([chr(2)])]),
            ]
        )
        self.assertEqual(e.sequentialize(), e_sequentialized)

    def test_split_at_multi(self):
        conc, chr = (core_events.Concurrence, core_events.Chronon)
        chr0, chr1, chr2 = self.sequence.split_at(1, 2)
        self.assertEqual(chr0, conc([chr(1), chr(1), chr(1)]))
        self.assertEqual(chr1, conc([chr(1), chr(1)]))
        self.assertEqual(chr2, conc([chr(1)]))

    def test_split_at_multi_nested(self):
        cons, conc, chr = (
            core_events.Consecution,
            core_events.Concurrence,
            core_events.Chronon,
        )
        chr0, chr1, chr2 = self.nested_sequence.split_at(1, 4)
        self.assertEqual(chr0, conc([cons([chr(1)]), cons([chr(1)])]))
        self.assertEqual(chr1, conc([cons([chr(2), chr(1)]), cons([chr(2), chr(1)])]))
        self.assertEqual(chr2, conc([cons([chr(2)]), cons([chr(2)])]))


if __name__ == "__main__":
    unittest.main()
