import unittest

from mutwo.events import music


class NoteLikeTest(unittest.TestCase):
    def test_pitch_or_pitches_setter_from_None(self):
        self.assertEqual([], music.NoteLike(None, 1, 1).pitch_or_pitches)

    def test_pitch_or_pitches_setter_from_element(self):
        pitch = 100
        self.assertEqual([pitch], music.NoteLike(pitch, 1, 1).pitch_or_pitches)

    def test_pitch_or_pitches_setter_from_list(self):
        pitches = [100, 200, 300]
        self.assertEqual(pitches, music.NoteLike(pitches, 1, 1).pitch_or_pitches)
