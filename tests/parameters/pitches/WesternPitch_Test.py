import unittest

from mutwo.parameters import pitches


class WesternPitchTest(unittest.TestCase):
    def test_constructor_from_string(self):
        pitch0 = pitches.WesternPitch("cf", 4)
        pitch1 = pitches.WesternPitch("dqs", 3)
        pitch2 = pitches.WesternPitch("gss")
        pitch3 = pitches.WesternPitch("ges", 0)
        pitch4 = pitches.WesternPitch("bss", 10)
        self.assertEqual(pitch0.name, "cf4")
        self.assertEqual(pitch1.name, "dqs3")
        self.assertEqual(pitch2.name, "gss4")
        self.assertEqual(pitch3.name, "ges0")
        self.assertEqual(pitch4.name, "bss10")
        self.assertEqual(pitch0.pitch_class, -1)
        self.assertEqual(pitch1.pitch_class, 2.5)
        self.assertEqual(pitch2.pitch_class, 9)
        self.assertEqual(pitch3.pitch_class, 7.25)
        self.assertEqual(pitch4.pitch_class, 13)

    def test_constructor_from_float(self):
        pitch0 = pitches.WesternPitch(0)
        pitch1 = pitches.WesternPitch(1)
        # SMALLER THAN ONE HALF STEP DOESN'T WORK YET
        # pitch2 = pitches.WesternPitch(2.25)
        # pitch3 = pitches.WesternPitch(-0.5)
        self.assertEqual(pitch0.name, "c4")
        self.assertEqual(pitch1.name, "df4")
        # self.assertEqual(pitch2.name, "des")
        # self.assertEqual(pitch3.name, "cqf")

    def test_property_frequency(self):
        pitch0 = pitches.WesternPitch("a", 4)
        pitch1 = pitches.WesternPitch("a", 3)
        pitch2 = pitches.WesternPitch("a", 5)
        pitch3 = pitches.WesternPitch("as", 4)
        pitch4 = pitches.WesternPitch("bqs", 4)
        self.assertAlmostEqual(
            pitch0.frequency, pitches.constants.DEFAULT_CONCERT_PITCH
        )
        self.assertAlmostEqual(
            pitch1.frequency, pitches.constants.DEFAULT_CONCERT_PITCH * 0.5
        )
        self.assertAlmostEqual(
            pitch2.frequency, pitches.constants.DEFAULT_CONCERT_PITCH * 2
        )
        self.assertAlmostEqual(
            pitch3.frequency,
            pitches.constants.DEFAULT_CONCERT_PITCH * pitch3.step_factor,
        )
        self.assertAlmostEqual(
            pitch4.frequency,
            pitches.constants.DEFAULT_CONCERT_PITCH * (pitch4.step_factor ** 2.5),
        )


if __name__ == "__main__":
    unittest.main()
