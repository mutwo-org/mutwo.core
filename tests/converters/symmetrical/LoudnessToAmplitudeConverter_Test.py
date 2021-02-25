import unittest

from mutwo import converters


class LoudnessToAmplitudeConverterTest(unittest.TestCase):
    def test_decibel_to_amplitude_ratio(self):
        self.assertEqual(
            converters.symmetrical.LoudnessToAmplitudeConverter._decibel_to_amplitude_ratio(
                0
            ),
            1,
        )
        self.assertEqual(
            round(
                converters.symmetrical.LoudnessToAmplitudeConverter._decibel_to_amplitude_ratio(
                    -6
                ),
                2,
            ),
            0.5,
        )
        self.assertEqual(
            round(
                converters.symmetrical.LoudnessToAmplitudeConverter._decibel_to_amplitude_ratio(
                    -12
                ),
                2,
            ),
            0.25,
        )
        # different reference amplitude
        self.assertEqual(
            converters.symmetrical.LoudnessToAmplitudeConverter._decibel_to_amplitude_ratio(
                0, 0.5
            ),
            0.5,
        )
        self.assertEqual(
            converters.symmetrical.LoudnessToAmplitudeConverter._decibel_to_amplitude_ratio(
                0, 2
            ),
            2,
        )

    def test_decibel_to_power_ratio(self):
        self.assertEqual(
            converters.symmetrical.LoudnessToAmplitudeConverter._decibel_to_power_ratio(
                0
            ),
            1,
        )
        self.assertEqual(
            converters.symmetrical.LoudnessToAmplitudeConverter._decibel_to_power_ratio(
                -6
            ),
            0.251188643150958,
        )
        self.assertEqual(
            converters.symmetrical.LoudnessToAmplitudeConverter._decibel_to_power_ratio(
                6
            ),
            3.9810717055349722,
        )

    def test_sone_to_phon(self):
        self.assertEqual(
            converters.symmetrical.LoudnessToAmplitudeConverter._sone_to_phon(1), 40
        )
        self.assertEqual(
            converters.symmetrical.LoudnessToAmplitudeConverter._sone_to_phon(2), 50
        )
        self.assertEqual(
            converters.symmetrical.LoudnessToAmplitudeConverter._sone_to_phon(0.5),
            31.39434452534506,
        )

    def test_convert(self):
        converter = converters.symmetrical.LoudnessToAmplitudeConverter(1)

        # test different frequencies
        self.assertAlmostEqual(converter.convert(50), 0.1549792455)
        self.assertAlmostEqual(converter.convert(100), 0.03308167306999658)
        self.assertAlmostEqual(converter.convert(200), 0.0093641)
        self.assertAlmostEqual(converter.convert(500), 0.0028416066734875583)
        self.assertAlmostEqual(converter.convert(2000), 0.0018302564694597117)
        self.assertAlmostEqual(converter.convert(10000), 0.010357060382149575)

        # test different loudness
        converter = converters.symmetrical.LoudnessToAmplitudeConverter(0.5)
        self.assertAlmostEqual(converter.convert(50), 0.08150315492680121)
        self.assertAlmostEqual(converter.convert(100), 0.015624188922340446)
        self.assertAlmostEqual(converter.convert(200), 0.003994808241065453)
        self.assertAlmostEqual(converter.convert(500), 0.0010904941511850816)


if __name__ == "__main__":
    unittest.main()
