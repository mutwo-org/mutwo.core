import unittest

from mutwo import core_constants
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities


class EnvelopeTest(unittest.TestCase):
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

        with self.assertWarns(core_utilities.InvalidAverageValueStartAndEndWarning):
            self.envelope.get_average_value(0, 0)

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


if __name__ == "__main__":
    unittest.main()
