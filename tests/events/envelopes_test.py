import unittest

from mutwo.core import events
from mutwo.core.utilities import constants


class EnvelopeTest(unittest.TestCase):
    class EnvelopeEvent(events.basic.SimpleEvent):
        def __init__(
            self,
            duration: constants.DurationType,
            value: constants.Real,
            curve_shape: constants.Real = 0,
        ):
            super().__init__(duration)
            self.value = value
            self.curve_shape = curve_shape

    def setUp(cls):
        cls.envelope = events.envelopes.Envelope(
            [
                cls.EnvelopeEvent(1, 0),
                cls.EnvelopeEvent(1, 1, 1),
                cls.EnvelopeEvent(1, 0, -1),
                cls.EnvelopeEvent(2, 1),
                cls.EnvelopeEvent(1, 0.5),
            ]
        )

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

    def test_from_points_simple(self):
        envelope_from_init = events.envelopes.Envelope(
            [self.EnvelopeEvent(1, 0, 10), self.EnvelopeEvent(0, 1)]
        )
        envelope_from_points = events.envelopes.Envelope.from_points((0, 0, 10), (1, 1))
        self.assertEqual(envelope_from_points, envelope_from_init)


class RelativeEnvelopeTest(unittest.TestCase):
    def setUp(cls):
        cls.envelope = events.envelopes.RelativeEnvelope(
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
        self.assertEqual(resolved_envelope.duration, 1)
        self.assertEqual(resolved_envelope.value_tuple, (100, 105, 110))


if __name__ == "__main__":
    unittest.main()
