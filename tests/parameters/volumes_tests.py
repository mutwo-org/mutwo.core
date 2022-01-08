import unittest


from mutwo.core.parameters import volumes


class DirectVolumeTest(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(volumes.DirectVolume(1), volumes.DirectVolume(1))
        self.assertEqual(volumes.DirectVolume(0.3), volumes.DirectVolume(0.3))
        self.assertNotEqual(volumes.DirectVolume(0.5), volumes.DirectVolume(0.3))

    def test_comparision(self):
        self.assertLess(volumes.DirectVolume(0.4), volumes.DirectVolume(1))
        self.assertLess(volumes.DirectVolume(0.1), volumes.DirectVolume(0.3))
        self.assertGreater(volumes.DirectVolume(0.5), volumes.DirectVolume(0.3))
        self.assertGreaterEqual(volumes.DirectVolume(0.3), volumes.DirectVolume(0.3))

    def test_midi_velocity(self):
        self.assertEqual(volumes.DirectVolume(1).midi_velocity, 127)
        self.assertEqual(volumes.DirectVolume(0).midi_velocity, 0)
        self.assertEqual(volumes.DirectVolume(0.5).midi_velocity, 107)

    def test_decibel(self):
        self.assertEqual(volumes.DirectVolume(1).decibel, 0)
        self.assertEqual(volumes.DirectVolume(0).decibel, float("-inf"))
        self.assertAlmostEqual(volumes.DirectVolume(0.5).decibel, -6, places=1)


if __name__ == "__main__":
    unittest.main()
