import unittest

import expenvelope  # type: ignore

from mutwo.generators import koenig


class TendencyTest(unittest.TestCase):
    def setUp(self):
        minima_curve = expenvelope.Envelope.from_points((0, 0), (1, 1), (2, 0))
        maxima_curve = expenvelope.Envelope.from_points((0, 1), (1, 2), (2, 3))
        self.tendecy = koenig.Tendency(minima_curve, maxima_curve)

    def test_range_at(self):
        self.assertEqual(self.tendecy.range_at(-100), (0, 1))
        self.assertEqual(self.tendecy.range_at(0), (0, 1))
        self.assertEqual(self.tendecy.range_at(1), (1, 2))
        self.assertEqual(self.tendecy.range_at(2), (0, 3))
        self.assertEqual(self.tendecy.range_at(100), (0, 3))

    def test_gamble_at(self):
        for position in (-100, 0, 1, 2, 100):
            value = self.tendecy.value_at(position)
            current_range = self.tendecy.range_at(value)
            self.assertTrue(value >= current_range[0])
            self.assertTrue(value <= current_range[1])


if __name__ == "__main__":
    unittest.main()
