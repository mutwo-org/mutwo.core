import unittest


from mutwo.converters import symmetrical
from mutwo.events import basic
from mutwo.events import music


class ArpeggioConverterTest(unittest.TestCase):
    def test_convert(self):
        converter = symmetrical.playing_indicators.ArpeggioConverter(
            duration_for_each_attack=0.1
        )
        note_like = music.NoteLike("c g e b", duration=5)
        note_like.playing_indicators.arpeggio.direction = "up"
        arpeggio = basic.SequentialEvent(
            [
                music.NoteLike(pitch, duration)
                for pitch, duration in zip("c e g b".split(" "), (0.1, 0.1, 0.1, 4.7))
            ]
        )
        for note in arpeggio:
            note.playing_indicators.arpeggio.direction = "up"

        self.assertEqual(converter.convert(note_like), arpeggio)


class PlayingIndicatorsConverterTest(unittest.TestCase):
    def test_convert(self):
        converter = symmetrical.playing_indicators.PlayingIndicatorsConverter(
            [
                symmetrical.playing_indicators.ArpeggioConverter(
                    duration_for_each_attack=0.1
                )
            ]
        )
        note_like = music.NoteLike("c g e b", duration=5)
        note_like.playing_indicators.arpeggio.direction = "up"
        arpeggio = basic.SequentialEvent(
            [
                music.NoteLike(pitch, duration)
                for pitch, duration in zip("c e g b".split(" "), (0.1, 0.1, 0.1, 4.7))
            ]
        )
        for note in arpeggio:
            note.playing_indicators.arpeggio.direction = "up"

        self.assertEqual(converter.convert(note_like), arpeggio)


if __name__ == "__main__":
    unittest.main()
