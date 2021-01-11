import unittest

from mutwo.parameters import pitches


class EqualDividedOctavePitch_Test(unittest.TestCase):
    def test_false_pitch_class(self):
        self.assertRaises(
            ValueError, lambda: pitches.EqualDividedOctavePitch(12, -2, 0, 0, 0)
        )
        self.assertRaises(
            ValueError, lambda: pitches.EqualDividedOctavePitch(12, 13, 0, 0, 0)
        )

    def test_property_frequency(self):
        pitch0 = pitches.EqualDividedOctavePitch(12, 0, 1, 0, 0)
        pitch1 = pitches.EqualDividedOctavePitch(6, 0, -1, 0, 0)
        pitch2 = pitches.EqualDividedOctavePitch(12, 6, 0, 0, 0)
        self.assertAlmostEqual(pitch0.frequency, pitch0.concert_pitch.frequency * 2)
        self.assertAlmostEqual(pitch1.frequency, pitch1.concert_pitch.frequency * 0.5)
        self.assertAlmostEqual(pitch2.frequency, 622.253967444162)

    def test_property_step_factor(self):
        pitch0 = pitches.EqualDividedOctavePitch(12, 0, 1, 0, 0)
        pitch1 = pitches.EqualDividedOctavePitch(6, 0, -1, 0, 0)
        self.assertAlmostEqual(
            (pitch0.step_factor ** pitch0.n_pitch_classes_per_octave)
            * pitch0.concert_pitch.frequency,
            pitch0.frequency,
        )
        self.assertAlmostEqual(
            pitch1.concert_pitch.frequency
            / (pitch1.step_factor ** pitch1.n_pitch_classes_per_octave),
            pitch1.frequency,
        )

    def test_magic_method_sub(self):
        pitch0 = pitches.EqualDividedOctavePitch(12, 7, 0, 0, 0)
        pitch1 = pitches.EqualDividedOctavePitch(12, 1, 0, 0, 0)
        pitch2 = pitches.EqualDividedOctavePitch(12, 0, 1, 0, 0)
        pitch3 = pitches.EqualDividedOctavePitch(24, 1, 0, 0, 0)
        self.assertEqual(pitch0 - pitch1, 6)
        self.assertEqual(pitch2 - pitch0, 5)
        self.assertEqual(pitch2 - pitch1, 11)
        self.assertRaises(ValueError, lambda: pitch3 - pitch1)

    def test_add(self):
        pitch0 = pitches.EqualDividedOctavePitch(12, 7, 0, 0, 0)
        pitch1 = pitches.EqualDividedOctavePitch(12, 1, 0, 0, 0)
        pitch2 = pitches.EqualDividedOctavePitch(12, 0, 1, 0, 0)
        pitch3 = pitches.EqualDividedOctavePitch(12, 11, -1, 0, 0)
        pitch4 = pitches.EqualDividedOctavePitch(12, 0, 0, 0, 0)
        pitch4.add(-1)
        self.assertEqual(pitch0.add(-6, mutate=False), pitch1)
        self.assertEqual(pitch0.add(5, mutate=False), pitch2)
        self.assertEqual(pitch0.add(-8, mutate=False), pitch3)
        self.assertEqual(pitch4, pitch3)

    def test_subtract(self):
        pitch0 = pitches.EqualDividedOctavePitch(12, 7, 0, 0, 0)
        pitch1 = pitches.EqualDividedOctavePitch(12, 1, 0, 0, 0)
        pitch2 = pitches.EqualDividedOctavePitch(12, 0, 1, 0, 0)
        pitch3 = pitches.EqualDividedOctavePitch(12, 11, -1, 0, 0)
        pitch4 = pitches.EqualDividedOctavePitch(12, 0, 0, 0, 0)
        pitch4.subtract(1)
        self.assertEqual(pitch0.subtract(6, mutate=False), pitch1)
        self.assertEqual(pitch0.subtract(-5, mutate=False), pitch2)
        self.assertEqual(pitch0.subtract(8, mutate=False), pitch3)
        self.assertEqual(pitch4, pitch3)


if __name__ == "__main__":
    unittest.main()
