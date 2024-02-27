import unittest

import ranges

from mutwo import core_events
from mutwo import core_parameters


class DirectTempoTest(unittest.TestCase):
    def test_bpm(self):
        d = core_parameters.DirectTempo
        self.assertEqual(d(60).bpm, 60)
        self.assertEqual(d(40).bpm, 40)
        self.assertEqual(d(40.32).bpm, 40.32)
        self.assertEqual(d("33.23").bpm, 33.23)

    def test_seconds(self):
        d = core_parameters.DirectTempo
        self.assertEqual(d(60).seconds, 1)
        self.assertEqual(d(30).seconds, 2)
        self.assertEqual(d(120).seconds, 0.5)


class WesternTempoTest(unittest.TestCase):
    def setUp(self):
        w = core_parameters.WesternTempo
        self.tempo0 = w(60, 1)
        self.tempo1 = w(60, 1)
        self.tempo2 = w(60, 0.5)
        self.tempo3 = w(62, 1)
        self.tempo4 = w(ranges.Range(50, 60), 1)
        self.tempo5 = w(ranges.Range(50, 60), 1)
        self.tempo6 = w(30, 1, "adagio")

    def test_seconds(self):
        d = core_parameters.WesternTempo
        self.assertEqual(d(60, 2).seconds, 0.5)
        self.assertEqual(d(30, 1).seconds, 2)

    def test_equal_with_tempo(self):
        self.assertEqual(self.tempo0, self.tempo1)

    def test_equal_with_tempo_range(self):
        self.assertEqual(self.tempo4, self.tempo5)

    def test_unequal_reference(self):
        self.assertNotEqual(self.tempo0, self.tempo2)

    def test_unequal_tempo(self):
        self.assertNotEqual(self.tempo0, self.tempo3)

    def test_bpm(self):
        self.assertEqual(self.tempo0.bpm, 60)
        self.assertEqual(self.tempo2.bpm, 30)
        self.assertEqual(self.tempo3.bpm, 62)
        self.assertEqual(self.tempo5.bpm, 50)

    def test_bpm_range(self):
        self.assertEqual(self.tempo0.bpm_range, ranges.Range(60, 60))
        self.assertEqual(self.tempo1.bpm_range, ranges.Range(60, 60))
        self.assertEqual(self.tempo4.bpm_range, ranges.Range(50, 60))

    def test_set_bpm_range(self):
        self.tempo0.bpm_range = ranges.Range(100, 110)
        self.assertEqual(self.tempo0.bpm, 100)
        self.assertEqual(self.tempo0.bpm_range, ranges.Range(100, 110))

    def test_default_tempo(self):
        """Ensure when reference isn't changed 1/4 note equals 1 second on BPM=60.

        This is the expected standard in western music (notation).
        """
        e = core_events.Chronon("1/4")
        e.tempo = core_parameters.FlexTempo(
            [[0, core_parameters.WesternTempo(60)]]
        )
        self.assertEqual(e.metrize().duration, 1)

    def test_textual_indication(self):
        self.assertEqual(self.tempo6.textual_indication, "adagio")
