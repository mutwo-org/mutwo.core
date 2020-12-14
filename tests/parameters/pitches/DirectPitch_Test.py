import unittest

from mutwo.parameters import pitches


class DirectPitch_Test(unittest.TestCase):
    def test_property_frequency(self):
        frequency0 = 200
        frequency1 = 502.42
        frequency2 = 10
        self.assertEqual(frequency0, pitches.DirectPitch(frequency0).frequency)
        self.assertEqual(frequency1, pitches.DirectPitch(frequency1).frequency)
        self.assertEqual(frequency2, pitches.DirectPitch(frequency2).frequency)


if __name__ == "__main__":
    unittest.main()
