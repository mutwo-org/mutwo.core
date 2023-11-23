import unittest

import ranges

from mutwo import core_events
from mutwo import core_parameters


class DirectTempoPointTest(unittest.TestCase):
    def test_tempo(self):
        d = core_parameters.DirectTempoPoint
        self.assertEqual(d(60).tempo, 60)
        self.assertEqual(d(40).tempo, 40)
        self.assertEqual(d(40.32).tempo, 40.32)
        self.assertEqual(d('33.23').tempo, 33.23)


class WesternTempoPointTest(unittest.TestCase):
    def setUp(self):
        w = core_parameters.WesternTempoPoint
        self.tempo_point0 = w(60, 1)
        self.tempo_point1 = w(60, 1)
        self.tempo_point2 = w(60, 0.5)
        self.tempo_point3 = w(62, 1)
        self.tempo_point4 = w(ranges.Range(50, 60), 1)
        self.tempo_point5 = w(ranges.Range(50, 60), 1)
        self.tempo_point6 = w(30, 1, "adagio")

    def test_equal_with_tempo_point(self):
        self.assertEqual(self.tempo_point0, self.tempo_point1)

    def test_equal_with_tempo_range(self):
        self.assertEqual(self.tempo_point4, self.tempo_point5)

    def test_unequal_reference(self):
        self.assertNotEqual(self.tempo_point0, self.tempo_point2)

    def test_unequal_tempo_point(self):
        self.assertNotEqual(self.tempo_point0, self.tempo_point3)

    def test_tempo(self):
        self.assertEqual(self.tempo_point0.tempo, 60)
        self.assertEqual(self.tempo_point2.tempo, 30)
        self.assertEqual(self.tempo_point3.tempo, 62)
        self.assertEqual(self.tempo_point5.tempo, 50)

    def test_tempo_range(self):
        self.assertEqual(self.tempo_point0.tempo_range, ranges.Range(60, 60))
        self.assertEqual(self.tempo_point1.tempo_range, ranges.Range(60, 60))
        self.assertEqual(self.tempo_point4.tempo_range, ranges.Range(50, 60))

    def test_set_tempo_range(self):
        self.tempo_point0.tempo_range = ranges.Range(100, 110)
        self.assertEqual(self.tempo_point0.tempo, 100)
        self.assertEqual(self.tempo_point0.tempo_range, ranges.Range(100, 110))

    def test_default_tempo(self):
        """Ensure when reference isn't changed 1/4 note equals 1 second on BPM=60.

        This is the expected standard in western music (notation).
        """
        e = core_events.Chronon('1/4')
        e.tempo_envelope = core_events.TempoEnvelope([[0, core_parameters.WesternTempoPoint(60)]])
        self.assertEqual(e.metrize().duration, 1)

    def test_textual_indication(self):
        self.assertEqual(self.tempo_point6.textual_indication, "adagio")
