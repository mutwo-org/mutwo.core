import unittest

import ranges

from mutwo import core_parameters


class DirectTempoPointTest(unittest.TestCase):
    def setUp(self):
        self.tempo_point0 = core_parameters.DirectTempoPoint(60, 1)
        self.tempo_point1 = core_parameters.DirectTempoPoint(60, 1)
        self.tempo_point2 = core_parameters.DirectTempoPoint(60, 0.5)
        self.tempo_point3 = core_parameters.DirectTempoPoint(62, 1)
        self.tempo_point4 = core_parameters.DirectTempoPoint(ranges.Range(50, 60), 1)
        self.tempo_point5 = core_parameters.DirectTempoPoint(ranges.Range(50, 60), 1)
        self.tempo_point6 = core_parameters.DirectTempoPoint(30, 1, "adagio")

    def test_equal_with_tempo_point(self):
        self.assertEqual(self.tempo_point0, self.tempo_point1)

    def test_equal_with_tempo_range(self):
        self.assertEqual(self.tempo_point4, self.tempo_point5)

    def test_unequal_reference(self):
        self.assertNotEqual(self.tempo_point0, self.tempo_point2)

    def test_unequal_tempo_point(self):
        self.assertNotEqual(self.tempo_point0, self.tempo_point3)

    def test_tempo_in_beats_per_minute(self):
        self.assertEqual(self.tempo_point0.tempo_in_beats_per_minute, 60)
        self.assertEqual(self.tempo_point2.tempo_in_beats_per_minute, 60)
        self.assertEqual(self.tempo_point3.tempo_in_beats_per_minute, 62)
        self.assertEqual(self.tempo_point5.tempo_in_beats_per_minute, 50)

    def test_absolute_tempo_in_beats_per_minute(self):
        self.assertEqual(self.tempo_point0.absolute_tempo_in_beats_per_minute, 60)
        self.assertEqual(self.tempo_point2.absolute_tempo_in_beats_per_minute, 30)
        self.assertEqual(self.tempo_point2.tempo_in_beats_per_minute, 60)

    def test_textual_indication(self):
        self.assertEqual(self.tempo_point6.textual_indication, "adagio")
