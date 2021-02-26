import unittest

try:
    import quicktions as fractions
except ImportError:
    import fractions

from mutwo import parameters


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


class VolumeTest(unittest.TestCase):
    def test_decibel_to_amplitude_ratio(self):
        self.assertEqual(
            parameters.abc.Volume.decibel_to_amplitude_ratio(0), 1,
        )
        self.assertEqual(
            round(parameters.abc.Volume.decibel_to_amplitude_ratio(-6), 2,), 0.5,
        )
        self.assertEqual(
            round(parameters.abc.Volume.decibel_to_amplitude_ratio(-12), 2,), 0.25,
        )
        # different reference amplitude
        self.assertEqual(
            parameters.abc.Volume.decibel_to_amplitude_ratio(0, 0.5), 0.5,
        )
        self.assertEqual(
            parameters.abc.Volume.decibel_to_amplitude_ratio(0, 2), 2,
        )

    def test_decibel_to_power_ratio(self):
        self.assertEqual(
            parameters.abc.Volume.decibel_to_power_ratio(0), 1,
        )
        self.assertEqual(
            parameters.abc.Volume.decibel_to_power_ratio(-6), 0.251188643150958,
        )
        self.assertEqual(
            parameters.abc.Volume.decibel_to_power_ratio(6), 3.9810717055349722,
        )

    def test_amplitude_ratio_to_decibel(self):
        self.assertEqual(
            parameters.abc.Volume.amplitude_ratio_to_decibel(1), 0,
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
            parameters.abc.Volume.amplitude_ratio_to_decibel(0), float("inf"),
        )

    def test_power_ratio_to_decibel(self):
        self.assertEqual(
            parameters.abc.Volume.power_ratio_to_decibel(1), 0,
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
            parameters.abc.Volume.power_ratio_to_decibel(0), float("inf"),
        )

    def test_amplitude_to_velocity(self):
        amplitude0 = 1
        amplitude1 = 0
        amplitude2 = 2
        amplitude3 = -100
        amplitude4 = 0.5
        amplitude5 = 0.2
        self.assertEqual(
            parameters.abc.Volume.amplitude_to_midi_velocity(amplitude0), 127
        )
        self.assertEqual(
            parameters.abc.Volume.amplitude_to_midi_velocity(amplitude1), 0
        )
        self.assertEqual(
            parameters.abc.Volume.amplitude_to_midi_velocity(amplitude2), 127
        )
        self.assertEqual(
            parameters.abc.Volume.amplitude_to_midi_velocity(amplitude3), 0
        )
        self.assertEqual(
            parameters.abc.Volume.amplitude_to_midi_velocity(amplitude4),
            int(round(127 * amplitude4)),
        )
        self.assertEqual(
            parameters.abc.Volume.amplitude_to_midi_velocity(amplitude5),
            int(round(127 * amplitude5)),
        )


if __name__ == "__main__":
    unittest.main()
