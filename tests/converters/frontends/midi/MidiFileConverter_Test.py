import unittest

# events
from mutwo.events import basic
from mutwo.events import music

# converter
from mutwo.converters.frontends import midi


# TODO(write tests for the more complex methods!)


class MidiFileConverterTest(unittest.TestCase):
    def test_volume_to_velocity(self):
        volume0 = 1
        volume1 = 0
        volume2 = 2
        volume3 = -100
        volume4 = 0.5
        volume5 = 0.2
        self.assertEqual(midi.MidiFileConverter._volume_to_velocity(volume0), 127)
        self.assertEqual(midi.MidiFileConverter._volume_to_velocity(volume1), 0)
        self.assertEqual(midi.MidiFileConverter._volume_to_velocity(volume2), 127)
        self.assertEqual(midi.MidiFileConverter._volume_to_velocity(volume3), 0)
        self.assertEqual(
            midi.MidiFileConverter._volume_to_velocity(volume4),
            int(round(127 * volume4)),
        )
        self.assertEqual(
            midi.MidiFileConverter._volume_to_velocity(volume5),
            int(round(127 * volume5)),
        )

    def test_find_available_midi_channels(self):
        converter0 = midi.MidiFileConverter("test.mid")
        converter1 = midi.MidiFileConverter(
            "test.mid", distribute_midi_channels=True, n_midi_channels_per_track=1
        )

        n_sequential_events = 17
        simultaneous_event = basic.SimultaneousEvent(
            [
                basic.SequentialEvent([music.NoteLike([], 2, 1)])
                for _ in range(n_sequential_events)
            ]
        )

        self.assertEqual(
            converter0._find_available_midi_channels_per_sequential_event(
                simultaneous_event
            ),
            tuple(
                midi.constants.DEFAULT_AVAILABLE_MIDI_CHANNELS
                for _ in range(n_sequential_events)
            ),
        )

        self.assertEqual(
            converter1._find_available_midi_channels_per_sequential_event(
                simultaneous_event
            ),
            tuple(
                (nth_channel % len(midi.constants.ALLOWED_MIDI_CHANNELS),)
                for nth_channel in range(n_sequential_events)
            ),
        )

    def test_beats_to_ticks(self):
        converter0 = midi.MidiFileConverter("test.mid")
        converter1 = midi.MidiFileConverter("test.mid", ticks_per_beat=100)
        converter2 = midi.MidiFileConverter("test.mid", ticks_per_beat=1000)

        n_beats_collection = (10, 30, 31.12, 11231.5523)

        for converter in (converter0, converter1, converter2):
            for n_beats in n_beats_collection:
                self.assertEqual(
                    converter._beats_to_ticks(n_beats),
                    int(converter._ticks_per_beat * n_beats),
                )

    def test_cent_deviation_to_pitch_bending_number(self):
        converter0 = midi.MidiFileConverter(
            "test.mid", maximum_pitch_bend_deviation=200
        )
        converter1 = midi.MidiFileConverter(
            "test.mid", maximum_pitch_bend_deviation=500
        )

        # first test all 'border values'
        self.assertEqual(converter0._cent_deviation_to_pitch_bending_number(0), 0)
        self.assertEqual(
            converter0._cent_deviation_to_pitch_bending_number(200),
            midi.constants.NEUTRAL_PITCH_BEND,
        )
        self.assertEqual(
            converter0._cent_deviation_to_pitch_bending_number(-200),
            -midi.constants.NEUTRAL_PITCH_BEND,
        )
        self.assertEqual(
            converter1._cent_deviation_to_pitch_bending_number(-500),
            -midi.constants.NEUTRAL_PITCH_BEND,
        )
        self.assertEqual(
            converter1._cent_deviation_to_pitch_bending_number(5000),
            midi.constants.NEUTRAL_PITCH_BEND,
        )

        # now test values inbetween
        self.assertEqual(
            converter0._cent_deviation_to_pitch_bending_number(100),
            int(midi.constants.NEUTRAL_PITCH_BEND * 0.5),
        )
        self.assertEqual(
            converter0._cent_deviation_to_pitch_bending_number(200 * 0.3),
            int(midi.constants.NEUTRAL_PITCH_BEND * 0.3),
        )

    def test_tune_pitch(self):
        pass

    def test_tempo_events_to_midi_messages(self):
        pass

    def test_note_information_to_midi_messages(self):
        pass

    def test_extracted_data_to_midi_messages(self):
        pass


if __name__ == "__main__":
    unittest.main()
