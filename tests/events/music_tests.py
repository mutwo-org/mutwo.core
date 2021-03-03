import unittest

from mutwo.events import basic
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

    def test_parameters_to_compare(self):
        note_like = music.NoteLike([30], 1, 1)
        expected_parameters_to_compare = ("duration", "pitch_or_pitches", "volume")
        self.assertEqual(
            note_like._parameters_to_compare, expected_parameters_to_compare
        )

    def test_equality_check(self):
        note_like0 = music.NoteLike([30], 1, 1)
        note_like1 = music.NoteLike([30], 1, 1)
        note_like2 = music.NoteLike([100], 1, 1)
        note_like3 = music.NoteLike([], 1, 2)
        note_like4 = music.NoteLike([400, 500], 1, 2)
        simple_event = basic.SimpleEvent(1)

        self.assertEqual(note_like0, note_like0)
        self.assertEqual(note_like1, note_like0)
        self.assertEqual(note_like0, note_like1)  # different order

        self.assertNotEqual(note_like0, note_like2)
        self.assertNotEqual(note_like2, note_like0)  # different order
        self.assertNotEqual(note_like2, note_like3)
        self.assertNotEqual(note_like2, note_like4)
        self.assertNotEqual(note_like3, note_like4)
        self.assertNotEqual(note_like0, simple_event)
        self.assertNotEqual(simple_event, note_like0)  # different order
