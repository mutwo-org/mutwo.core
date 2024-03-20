import unittest

try:
    import quicktions as fractions
except ImportError:
    import fractions

from mutwo import core_parameters


f = fractions.Fraction


class RatioDurationTest(unittest.TestCase):
    def setUp(self):
        self.d = core_parameters.RatioDuration
        self.d0, self.d1 = self.d("1/1"), self.d("3/2")

    def test_beat_count_get(self):
        self.assertEqual(self.d0.beat_count, 1.0)
        self.assertEqual(self.d1.beat_count, 1.5)

    def test_beat_count_set(self):
        self.d0.beat_count = 40
        self.assertEqual(self.d0.beat_count, 40.0)
        self.d0.beat_count = "3/2"
        self.assertEqual(self.d0.beat_count, 1.5)

    def test_ratio_get(self):
        self.assertEqual(self.d0.ratio, f(1, 1))
        self.assertEqual(self.d1.ratio, f(3, 2))

    def test_ratio_set(self):
        self.d0.ratio = "5/4"
        self.assertEqual(self.d0.ratio, f(5, 4))
        self.d0.ratio = 101
        self.assertEqual(self.d0.ratio, f(101, 1))
        self.assertEqual(self.d0.beat_count, 101)
        self.d0.ratio = f(29, 27)
        self.assertEqual(self.d0.ratio, f(29, 27))
        self.d0.ratio = 1.5
        self.assertEqual(self.d0.beat_count, 1.5)
        self.assertEqual(self.d0.ratio, f(3, 2))

    def test_equal(self):
        for d in (10, 14.12512561920591245, -10):
            self.assertEqual(core_parameters.DirectDuration(d), self.d(d))
            self.assertEqual(self.d(d), self.d(d))

    def test_add(self):
        self.assertEqual(self.d0 + 1, self.d(2))
        self.assertEqual(self.d0 + self.d1, self.d("5/2"))
