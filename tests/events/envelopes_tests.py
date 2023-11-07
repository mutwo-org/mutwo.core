import typing
import unittest

import ranges

from mutwo import core_constants
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities

from .basic_tests import ComplexEventTest


class EnvelopeTest(unittest.TestCase, ComplexEventTest):
    class EnvelopeEvent(core_events.SimpleEvent):
        def __init__(
            self,
            duration: core_constants.DurationType,
            value: core_constants.Real,
            curve_shape: core_constants.Real = 0,
        ):
            super().__init__(duration)
            self.value = value
            self.curve_shape = curve_shape

    def setUp(self):
        ComplexEventTest.setUp(self)
        self.envelope = core_events.Envelope(
            [
                self.EnvelopeEvent(1, 0),
                self.EnvelopeEvent(1, 1, 1),
                self.EnvelopeEvent(1, 0, -1),
                self.EnvelopeEvent(2, 1),
                self.EnvelopeEvent(1, 0.5),
            ]
        )
        self.double_value_envelope = core_events.Envelope(
            [
                self.EnvelopeEvent(1, 0),
                self.EnvelopeEvent(1, 1, 1),
                self.EnvelopeEvent(1, 0, -1),
                self.EnvelopeEvent(2, 1),
                self.EnvelopeEvent(1, 0.5),
            ],
            value_to_parameter=lambda value: value / 2,
            parameter_to_value=lambda parameter: parameter * 2,
        )

    def get_event_class(self) -> typing.Type:
        return core_events.Envelope

    def get_event_instance(self) -> core_events.SimpleEvent:
        return self.get_event_class()([[0, 1], [4, 10]])

    def test_split_at_end(self):
        # XXX: Tempo envelopes slightly differ, but not in their
        # actual content. So let's just metrize before comparing.
        self.assertEqual(
            (self.event.split_at(self.event.duration)[0].metrize(),),
            (self.event.metrize(),),
        )

    def test_parameter_tuple(self):
        self.assertEqual(self.envelope.parameter_tuple, (0, 1, 0, 1, 0.5))
        self.assertEqual(self.double_value_envelope.parameter_tuple, (0, 1, 0, 1, 0.5))

    def test_value_tuple(self):
        self.assertEqual(self.envelope.value_tuple, (0, 1, 0, 1, 0.5))
        self.assertEqual(self.double_value_envelope.value_tuple, (0, 2, 0, 2, 1))

    def _test_setitem(self, envelope_to_test: core_events.Envelope):
        self.assertEqual(type(envelope_to_test), core_events.Envelope)
        self.assertEqual(len(envelope_to_test), 2)
        self.assertEqual(envelope_to_test.duration, core_parameters.DirectDuration(3))
        self.assertEqual(envelope_to_test.value_tuple, (0, 1))

    def test_setitem(self):
        envelope = core_events.Envelope([])
        envelope[:] = [self.EnvelopeEvent(3, 0), self.EnvelopeEvent(0, 1)]
        self._test_setitem(envelope)

    def test_setitem_from_points(self):
        # Use syntactic sugar
        envelope = core_events.Envelope([])
        envelope[:] = [(0, 0), (3, 1)]
        self._test_setitem(envelope)

    def test_value_at_before(self):
        self.assertEqual(self.envelope.value_at(-1), self.envelope[0].value)
        self.assertEqual(self.envelope.value_at(-100), self.envelope[0].value)
        self.assertEqual(self.envelope.value_at(0), self.envelope[0].value)

    def test_value_at_after(self):
        self.assertEqual(self.envelope.value_at(100), self.envelope[-1].value)
        self.assertEqual(self.envelope.value_at(6), self.envelope[-1].value)
        self.assertEqual(self.envelope.value_at(5), self.envelope[-1].value)

    def test_value_at_curve_shape_0(self):
        self.assertEqual(self.envelope.value_at(0.25), 0.25)
        self.assertEqual(self.envelope.value_at(0.5), 0.5)
        self.assertEqual(self.envelope.value_at(0.75), 0.75)
        self.assertEqual(self.envelope.value_at(1), 1)

    def test_value_at_curve_shape_1(self):
        self.assertEqual(self.envelope.value_at(1.25), 0.83470382332888)
        self.assertEqual(self.envelope.value_at(1.5), 0.6224593312018545)
        self.assertEqual(self.envelope.value_at(1.75), 0.3499320087587726)
        self.assertEqual(self.envelope.value_at(2), 0)

    def test_value_at_curve_shape_minus_1(self):
        self.assertEqual(self.envelope.value_at(2.25), 0.3499320087587727)
        self.assertAlmostEqual(self.envelope.value_at(2.5), 0.6224593312018545)
        self.assertEqual(self.envelope.value_at(2.75), 0.83470382332888)
        self.assertEqual(self.envelope.value_at(3), 1)

    def test_value_at_with_duration_2(self):
        self.assertEqual(self.envelope.value_at(4), 0.75)

    def test_value_at_empty_envelope(self):
        self.assertRaises(
            core_utilities.EmptyEnvelopeError, core_events.Envelope([]).value_at, 0
        )

    def test_curve_shape_at_before(self):
        self.assertEqual(self.envelope.curve_shape_at(-1), 0)
        self.assertEqual(self.envelope.curve_shape_at(-100), 0)

    def test_curve_shape_at_after(self):
        self.assertEqual(self.envelope.curve_shape_at(100), 0)
        self.assertEqual(self.envelope.curve_shape_at(6), 0)

    def test_curve_shape_at_point(self):
        e = self.envelope
        self.assertEqual(e.curve_shape_at(1), 1)
        self.assertEqual(e.curve_shape_at(2), -1)

    def test_curve_shape_at_between_points(self):
        e = self.envelope
        self.assertEqual(e.curve_shape_at(1.5), 0.5)

    def test_curve_shape_at_empty_envelope(self):
        self.assertRaises(
            core_utilities.EmptyEnvelopeError,
            core_events.Envelope([]).curve_shape_at,
            0,
        )

    def test_point_at_before(self):
        d = core_parameters.DirectDuration
        self.assertEqual(self.envelope.point_at(-1), (d(-1), 0, 0))
        self.assertEqual(self.envelope.point_at(-100), (d(-100), 0, 0))

    def test_point_at_after(self):
        d = core_parameters.DirectDuration
        self.assertEqual(self.envelope.point_at(6), (d(6), 0.5, 0))
        self.assertEqual(self.envelope.point_at(100), (d(100), 0.5, 0))

    def test_point_at_points(self):
        d = core_parameters.DirectDuration
        self.assertEqual(self.envelope.point_at(0), (d(0), 0, 0))
        self.assertEqual(self.envelope.point_at(1), (d(1), 1, 1))
        self.assertEqual(self.envelope.point_at(2), (d(2), 0, -1))

    def test_time_range_to_point_tuple(self):
        d = core_parameters.DirectDuration
        # All pre-defined points
        self.assertEqual(
            self.envelope.time_range_to_point_tuple(ranges.Range(0, 5)),
            (
                (d(0), 0, 0),
                (d(1), 1, 1),
                (d(2), 0, -1),
                (d(3), 1, 0),
                (d(5), 0.5, 0),
            ),
        )
        # Interpolation points
        #   first point
        self.assertEqual(
            self.envelope.time_range_to_point_tuple(ranges.Range(0.5, 1)),
            ((d(0.5), 0.5, 0), (d(1), 1, 1)),
        )
        #   last point
        self.assertEqual(
            self.envelope.time_range_to_point_tuple(ranges.Range(0, 0.5)),
            ((d(0), 0, 0), (d(0.5), 0.5, 0)),
        )
        #   both points
        self.assertEqual(
            self.envelope.time_range_to_point_tuple(ranges.Range(0.25, 0.75)),
            ((d(0.25), 0.25, 0), (d(0.75), 0.75, 0)),
        )

    def test_from_points_simple(self):
        envelope_from_init = core_events.Envelope(
            [self.EnvelopeEvent(1, 0, 10), self.EnvelopeEvent(0, 1)]
        )
        envelope_from_points = core_events.Envelope.from_points((0, 0, 10), (1, 1))
        self.assertEqual(envelope_from_points, envelope_from_init)

    def test_is_static(self):
        self.assertEqual(self.envelope.is_static, False)
        self.assertEqual(core_events.Envelope([]).is_static, True)
        self.assertEqual(core_events.Envelope([[0, 10]]).is_static, True)
        self.assertEqual(core_events.Envelope([[0, 10], [10, 10]]).is_static, True)
        self.assertEqual(
            core_events.Envelope([[0, 10], [10, 10], [20, 10.001]]).is_static,
            False,
        )

    def test_integrate_interval(self):
        self.assertAlmostEqual(
            self.envelope.integrate_interval(0, 5), 3.163953413738653
        )
        self.assertAlmostEqual(self.envelope.integrate_interval(1, 1), 0)
        self.assertAlmostEqual(
            self.envelope.integrate_interval(0, 30), 15.663953413738653
        )
        self.assertAlmostEqual(self.envelope.integrate_interval(-3, 0.25), 0.03125)

    def test_get_average_value(self):
        self.assertEqual(self.envelope.get_average_value(-1, 0), 0)
        self.assertAlmostEqual(
            self.envelope.get_average_value(0, 5), 0.6327906827477305
        )
        # With implicit start and end
        self.assertAlmostEqual(self.envelope.get_average_value(), 0.6106589022895331)
        self.assertEqual(
            self.envelope.get_average_value(),
            self.envelope.get_average_value(0, self.envelope.duration),
        )

    def test_get_average_value_with_zero_duration(self):
        self.assertEqual(self.envelope.get_average_value(0, 0), 0)

    def test_get_average_parameter(self):
        self.assertAlmostEqual(
            self.envelope.get_average_parameter(0, 5), 0.6327906827477305
        )

    def _test_sample_at(
        self, sample_position: float, envelope_to_sample: core_events.Envelope
    ):
        sampled_envelope = envelope_to_sample.sample_at(sample_position, mutate=False)

        before_sample_position = sample_position * 0.9
        after_sample_position = sample_position * 1.1

        # Before new sampled point it should be the same
        self.assertEqual(
            envelope_to_sample.value_at(before_sample_position),
            sampled_envelope.value_at(before_sample_position),
        )

        # On new sampled point it should be the same
        self.assertEqual(
            envelope_to_sample.value_at(sample_position),
            sampled_envelope.value_at(sample_position),
        )

        # After new sampled point it should be the same
        self.assertEqual(
            envelope_to_sample.value_at(after_sample_position),
            sampled_envelope.value_at(after_sample_position),
        )

        return sampled_envelope

    def test_sample_at_with_curve_shape_0(self):
        sample_position = 0.5
        envelope_to_sample = self.envelope
        sampled_envelope = self._test_sample_at(sample_position, envelope_to_sample)

        self.assertNotEqual(sampled_envelope[1], envelope_to_sample[1])
        self.assertEqual(sampled_envelope[1].value, 0.5)
        self.assertEqual(sampled_envelope[1].duration, 0.5)

    def test_sample_at_with_curve_shape_1(self):
        sample_position = 1.5
        envelope_to_sample = self.envelope
        self._test_sample_at(sample_position, envelope_to_sample)

    def test_sample_at_after_any_already_defined_event(self):
        envelope_to_sample = self.envelope
        event_count_before = len(envelope_to_sample)
        envelope_to_sample_duration = envelope_to_sample.duration
        envelope_to_sample.sample_at(envelope_to_sample_duration + 1)
        event_count_after = len(envelope_to_sample)
        self.assertEqual(event_count_before, event_count_after - 1)
        self.assertEqual(
            envelope_to_sample.value_at(envelope_to_sample_duration),
            envelope_to_sample.value_at(envelope_to_sample_duration + 1),
        )

    def test_sample_at_empty_envelope(self):
        self.assertRaises(
            core_utilities.EmptyEnvelopeError, core_events.Envelope([]).sample_at, 0
        )

    def test_sample_at_invalid_absolute_time(self):
        self.assertRaises(
            core_utilities.InvalidAbsoluteTime,
            core_events.Envelope([[0, 10], [1, 10]]).sample_at,
            -1,
        )

    def test_cut_out(self):
        # Envelope needs extra test for customized cut out method.
        cut_out_envelope = self.envelope.cut_out(0.5, 1.5, mutate=False)
        self.assertEqual(cut_out_envelope.value_at(0.25), self.envelope.value_at(0.75))
        self.assertEqual(cut_out_envelope.value_at(0.5), self.envelope.value_at(1))
        self.assertEqual(cut_out_envelope.value_at(0.75), self.envelope.value_at(1.25))
        self.assertEqual(cut_out_envelope.value_at(1), self.envelope.value_at(1.5))

    def test_split_at(self):
        split_envelope_left, split_envelope_right = self.envelope.split_at(1.5)
        self.assertEqual(
            split_envelope_left.value_at(1.5), split_envelope_right.value_at(0)
        )

    def test_split_at_multi(self):
        for splitt in ((1.5, 3), (0, 1.5, 3)):
            split_envelope0, split_envelope1, split_envelope2 = self.envelope.split_at(
                *splitt
            )
            # Check if all split points have expected values
            self.assertEqual(split_envelope0.value_at(0), 0)
            self.assertEqual(split_envelope0.value_at(1.5), 0.6224593312018545)
            self.assertEqual(split_envelope1.value_at(0), 0.6224593312018545)
            self.assertEqual(split_envelope1.value_at(1.5), 1)
            self.assertEqual(split_envelope2.value_at(0), 1)
            self.assertEqual(split_envelope2.value_at(3), 0.5)
            # Check if their duration is correct
            self.assertEqual(split_envelope0.duration, 1.5)
            self.assertEqual(split_envelope1.duration, 1.5)
            self.assertEqual(split_envelope2.duration, 3)

    def test_cut_off(self):
        cut_off_envelope = self.envelope.cut_off(0.5, 1.5, mutate=False)
        self.assertEqual(self.envelope.value_at(0.4), cut_off_envelope.value_at(0.4))
        # There is a very small floating point error
        self.assertAlmostEqual(
            self.envelope.value_at(1.6), cut_off_envelope.value_at(0.6)
        )

    def test_extend_until(self):
        self.assertEqual(len(self.envelope), 5)
        self.envelope.extend_until(10)
        self.assertEqual(len(self.envelope), 6)
        self.assertEqual(self.envelope.duration, 10)
        self.assertEqual(self.envelope[-1].duration, 0)
        self.assertEqual(
            self.envelope.parameter_tuple[-1], self.envelope.parameter_tuple[-2]
        )
        self.assertRaises(
            core_utilities.EmptyEnvelopeError, core_events.Envelope([]).extend_until, 1
        )


class RelativeEnvelopeTest(unittest.TestCase):
    def setUp(cls):
        cls.envelope = core_events.RelativeEnvelope(
            [
                [0, 0],
                [5, 5],
                [10, 10],
            ],
            base_parameter_and_relative_parameter_to_absolute_parameter=lambda base_parameter, relative_parameter: base_parameter
            + relative_parameter,
        )

    def test_resolve(self):
        resolved_envelope = self.envelope.resolve(duration=1, base_parameter=100)
        self.assertEqual(resolved_envelope.duration, core_parameters.DirectDuration(1))
        self.assertEqual(resolved_envelope.value_tuple, (100, 105, 110))


class TempoEnvelopeTest(unittest.TestCase):
    def setUp(self):
        self.tempo_envelope_with_float = core_events.TempoEnvelope(
            [[0, 60], [1, 30], [2, 60]]
        )

        self.tempo_envelope_with_tempo_points = core_events.TempoEnvelope(
            [
                [0, core_parameters.DirectTempoPoint(60)],
                [1, core_parameters.DirectTempoPoint(30)],
                [2, core_parameters.DirectTempoPoint(30, reference=2)],
            ]
        )

        self.mixed_tempo_envelope = core_events.TempoEnvelope(
            [[0, 60], [1, core_parameters.DirectTempoPoint(30)], [2, 60]]
        )

    def _test_value_at(self, tempo_envelope: core_events.TempoEnvelope):
        self.assertEqual(tempo_envelope.value_at(0), 60)
        self.assertEqual(tempo_envelope.value_at(0.5), 45)
        self.assertEqual(tempo_envelope.value_at(1), 30)
        self.assertEqual(tempo_envelope.value_at(1.5), 45)
        self.assertEqual(tempo_envelope.value_at(2), 60)

    def test_value_at_with_float(self):
        self._test_value_at(self.tempo_envelope_with_float)

    def test_value_at_with_tempo_points(self):
        self._test_value_at(self.tempo_envelope_with_tempo_points)

    def test_value_at_with_mixed(self):
        self._test_value_at(self.mixed_tempo_envelope)


if __name__ == "__main__":
    unittest.main()
