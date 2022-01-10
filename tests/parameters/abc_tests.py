import unittest

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

from mutwo.core import parameters


class PitchTest(unittest.TestCase):
    def test_abstract_error(self):
        self.assertRaises(TypeError, parameters.abc.Pitch)

    def test_hertz_to_cents(self):
        self.assertEqual(1200, parameters.abc.Pitch.hertz_to_cents(440, 880))
        self.assertEqual(-1200, parameters.abc.Pitch.hertz_to_cents(880, 440))
        self.assertEqual(0, parameters.abc.Pitch.hertz_to_cents(10, 10))
        self.assertEqual(
            702, round(parameters.abc.Pitch.hertz_to_cents(440, 440 * 3 / 2))
        )

    def test_ratio_to_cents(self):
        self.assertEqual(
            1200, parameters.abc.Pitch.ratio_to_cents(fractions.Fraction(2, 1))
        )
        self.assertEqual(
            -1200, parameters.abc.Pitch.ratio_to_cents(fractions.Fraction(1, 2))
        )
        self.assertEqual(
            0, parameters.abc.Pitch.ratio_to_cents(fractions.Fraction(1, 1))
        )
        self.assertEqual(
            702, round(parameters.abc.Pitch.ratio_to_cents(fractions.Fraction(3, 2)))
        )

    def test_cents_to_ratio(self):
        self.assertEqual(
            fractions.Fraction(2, 1), parameters.abc.Pitch.cents_to_ratio(1200)
        )
        self.assertEqual(
            fractions.Fraction(1, 2), parameters.abc.Pitch.cents_to_ratio(-1200)
        )
        self.assertEqual(
            fractions.Fraction(1, 1), parameters.abc.Pitch.cents_to_ratio(0)
        )

    def test_hertz_to_midi_pitch_number(self):
        self.assertEqual(69, parameters.abc.Pitch.hertz_to_midi_pitch_number(440))
        self.assertEqual(
            60, round(parameters.abc.Pitch.hertz_to_midi_pitch_number(261))
        )


class PitchIntervalEnvelopeTest(unittest.TestCase):
    def setUp(cls):
        pitch_interval0 = (
            parameters.abc.Pitch.PitchIntervalEnvelope.make_generic_pitch_interval(1200)
        )
        pitch_interval1 = (
            parameters.abc.Pitch.PitchIntervalEnvelope.make_generic_pitch_interval(0)
        )
        pitch_interval2 = (
            parameters.abc.Pitch.PitchIntervalEnvelope.make_generic_pitch_interval(-100)
        )
        cls.pitch = parameters.abc.Pitch.PitchEnvelope.make_generic_pitch_class(440)(
            envelope=parameters.abc.Pitch.PitchIntervalEnvelope(
                [[0, pitch_interval0], [10, pitch_interval1], [20, pitch_interval2]]
            )
        )
        cls.pitch_envelope = cls.pitch.resolve_envelope(1)

    def test_value_at(self):
        self.assertEqual(self.pitch.envelope.value_at(0), 1200)
        self.assertEqual(self.pitch.envelope.value_at(5), 600)
        self.assertEqual(self.pitch.envelope.value_at(10), 0)
        self.assertEqual(self.pitch.envelope.value_at(15), -50)
        self.assertEqual(self.pitch.envelope.value_at(20), -100)

    def test_parameter_at(self):
        for absolute_time, cents in (
            (0, 1200),
            (5, 600),
            (10, 0),
            (15, -50),
            (20, -100),
        ):
            self.assertEqual(
                self.pitch.envelope.parameter_at(absolute_time),
                parameters.abc.Pitch.PitchIntervalEnvelope.make_generic_pitch_interval(
                    cents
                ),
            )

    def test_value_tuple(self):
        self.assertEqual(self.pitch.envelope.value_tuple, (1200, 0, -100))

    def test_resolve_envelope(self):
        point_list = []
        for position, frequency in (
            (0, 880),
            (0.5, 440),
            (1, fractions.Fraction(116897880079141095, 281474976710656)),
        ):
            point_list.append(
                (
                    position,
                    parameters.abc.Pitch.PitchEnvelope.make_generic_pitch(frequency),
                )
            )
        pitch_envelope = self.pitch.PitchEnvelope(point_list)
        self.assertEqual(self.pitch_envelope, pitch_envelope)

    def test_value_at_resolved_envelope(self):
        for position, frequency in (
            (0, 880),
            (0.25, 622.2539674441618),
            (0.5, 440),
            (1, 415.3046975799451),
        ):
            self.assertAlmostEqual(
                self.pitch_envelope.value_at(position),  # type: ignore
                parameters.abc.Pitch.hertz_to_cents(
                    parameters.pitches_constants.PITCH_ENVELOPE_REFERENCE_FREQUENCY,
                    frequency,
                ),  # type: ignore
            )

    def test_parameter_at_resolved_envelope(self):
        for position, frequency in (
            (0, 880),
            (0.25, 622.2539674441618),
            (0.5, 440),
            (1, 415.3046975799451),
        ):
            self.assertAlmostEqual(
                self.pitch_envelope.parameter_at(position).frequency, frequency
            )


class VolumeTest(unittest.TestCase):
    def test_decibel_to_amplitude_ratio(self):
        self.assertEqual(
            parameters.abc.Volume.decibel_to_amplitude_ratio(0),
            1,
        )
        self.assertEqual(
            round(
                parameters.abc.Volume.decibel_to_amplitude_ratio(-6),
                2,
            ),
            0.5,
        )
        self.assertEqual(
            round(
                parameters.abc.Volume.decibel_to_amplitude_ratio(-12),
                2,
            ),
            0.25,
        )
        # different reference amplitude
        self.assertEqual(
            parameters.abc.Volume.decibel_to_amplitude_ratio(0, 0.5),
            0.5,
        )
        self.assertEqual(
            parameters.abc.Volume.decibel_to_amplitude_ratio(0, 2),
            2,
        )

    def test_decibel_to_power_ratio(self):
        self.assertEqual(
            parameters.abc.Volume.decibel_to_power_ratio(0),
            1,
        )
        self.assertEqual(
            parameters.abc.Volume.decibel_to_power_ratio(-6),
            0.251188643150958,
        )
        self.assertEqual(
            parameters.abc.Volume.decibel_to_power_ratio(6),
            3.9810717055349722,
        )

    def test_amplitude_ratio_to_decibel(self):
        self.assertEqual(
            parameters.abc.Volume.amplitude_ratio_to_decibel(1),
            0,
        )
        self.assertEqual(
            parameters.abc.Volume.amplitude_ratio_to_decibel(
                0.5, reference_amplitude=0.5
            ),
            0,
        )
        self.assertAlmostEqual(
            parameters.abc.Volume.amplitude_ratio_to_decibel(0.50118), -6, places=3
        )
        self.assertAlmostEqual(
            parameters.abc.Volume.amplitude_ratio_to_decibel(0.25), -12.041, places=3
        )
        self.assertEqual(
            parameters.abc.Volume.amplitude_ratio_to_decibel(0),
            float("-inf"),
        )

    def test_power_ratio_to_decibel(self):
        self.assertEqual(
            parameters.abc.Volume.power_ratio_to_decibel(1),
            0,
        )
        self.assertEqual(
            parameters.abc.Volume.power_ratio_to_decibel(0.5, reference_amplitude=0.5),
            0,
        )
        self.assertAlmostEqual(
            parameters.abc.Volume.power_ratio_to_decibel(0.25), -6, places=1
        )
        self.assertAlmostEqual(
            parameters.abc.Volume.power_ratio_to_decibel(0.06309), -12, places=3
        )
        self.assertEqual(
            parameters.abc.Volume.power_ratio_to_decibel(0),
            float("-inf"),
        )

    def test_amplitude_ratio_to_velocity(self):
        amplitude0 = 1
        amplitude1 = 0
        self.assertEqual(
            parameters.abc.Volume.amplitude_ratio_to_midi_velocity(amplitude0), 127
        )
        self.assertEqual(
            parameters.abc.Volume.amplitude_ratio_to_midi_velocity(amplitude1), 0
        )


if __name__ == "__main__":
    unittest.main()
