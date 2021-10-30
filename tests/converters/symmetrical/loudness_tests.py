import unittest

from mutwo import converters


class LoudnessToAmplitudeConverterTest(unittest.TestCase):
    def test_sone_to_phon(self):
        self.assertEqual(
            converters.symmetrical.loudness.LoudnessToAmplitudeConverter._sone_to_phon(
                1
            ),
            40,
        )
        self.assertEqual(
            converters.symmetrical.loudness.LoudnessToAmplitudeConverter._sone_to_phon(
                2
            ),
            50,
        )
        self.assertEqual(
            converters.symmetrical.loudness.LoudnessToAmplitudeConverter._sone_to_phon(
                0.5
            ),
            31.39434452534506,
        )

    def test_convert(self):
        converter = converters.symmetrical.loudness.LoudnessToAmplitudeConverter()

        # test different frequencies
        self.assertAlmostEqual(converter.convert(1, 50), 0.1549792455)
        self.assertAlmostEqual(converter.convert(1, 100), 0.03308167306999658)
        self.assertAlmostEqual(converter.convert(1, 200), 0.0093641)
        self.assertAlmostEqual(converter.convert(1, 500), 0.0028416066734875583)
        self.assertAlmostEqual(converter.convert(1, 2000), 0.0018302564694597117)
        self.assertAlmostEqual(converter.convert(1, 10000), 0.010357060382149575)

        # test different loudness
        converter = converters.symmetrical.loudness.LoudnessToAmplitudeConverter()
        self.assertAlmostEqual(converter.convert(0.5, 50), 0.08150315492680121)
        self.assertAlmostEqual(converter.convert(0.5, 100), 0.015624188922340446)
        self.assertAlmostEqual(converter.convert(0.5, 200), 0.003994808241065453)
        self.assertAlmostEqual(converter.convert(0.5, 500), 0.0010904941511850816)


if __name__ == "__main__":
    unittest.main()
