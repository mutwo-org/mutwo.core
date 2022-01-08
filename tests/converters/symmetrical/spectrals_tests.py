import unittest

from mutwo.core import converters
from mutwo.core import parameters


class TwoPitchesToCommonHarmonicsConverterTest(unittest.TestCase):
    def test_convert(self):
        converter = converters.symmetrical.spectrals.TwoPitchesToCommonHarmonicsConverter(
            True, 1, 16
        )

        self.assertEqual(
            converter.convert(
                (
                    parameters.pitches.JustIntonationPitch("7/4"),
                    parameters.pitches.JustIntonationPitch(),
                )
            ),
            (
                parameters.pitches.CommonHarmonic(
                    (
                        parameters.pitches.Partial(1, True),
                        parameters.pitches.Partial(7, True),
                    ),
                    "7/1",
                ),
                parameters.pitches.CommonHarmonic(
                    (
                        parameters.pitches.Partial(2, True),
                        parameters.pitches.Partial(14, True),
                    ),
                    "14/1",
                ),
            ),
        )


if __name__ == "__main__":
    unittest.main()
