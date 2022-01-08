import unittest

from mutwo.core import converters
from mutwo.core import events

from mutwo.ext import events as ext_events


class GraceNotesConverterTest(unittest.TestCase):
    def setUp(self):
        self.grace_notes_converter = (
            converters.symmetrical.grace_notes.GraceNotesConverter()
        )

    def test_convert_note_like(self):
        note_like = ext_events.music.NoteLike(
            duration=1,
            grace_note_sequential_event=events.basic.SequentialEvent(
                [ext_events.music.NoteLike(duration=0.5), ext_events.music.NoteLike(duration=1)]
            ),
        )
        converted_note_like = self.grace_notes_converter.convert(note_like)

        self.assertEqual(note_like.duration, converted_note_like.duration)
        self.assertEqual(
            len(converted_note_like), 1 + len(note_like.grace_note_sequential_event)
        )
        self.assertTrue(isinstance(converted_note_like, events.basic.SequentialEvent))
        self.assertAlmostEqual(
            converted_note_like[0].duration / converted_note_like[1].duration,
            note_like.grace_note_sequential_event[0].duration
            / note_like.grace_note_sequential_event[1].duration,
        )

    def test_convert_sequential_event(self):
        sequential_event = events.basic.SequentialEvent(
            [
                ext_events.music.NoteLike("a"),
                ext_events.music.NoteLike(
                    "e",
                    after_grace_note_sequential_event=events.basic.SequentialEvent(
                        [ext_events.music.NoteLike("f")]
                    ),
                ),
            ]
        )
        converted_sequental_event = self.grace_notes_converter.convert(sequential_event)
        self.assertEqual(sequential_event.duration, converted_sequental_event.duration)
        self.assertEqual(
            len(converted_sequental_event), 3  # two main events + one after grace note
        )


if __name__ == "__main__":
    unittest.main()
