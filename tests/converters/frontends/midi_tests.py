import unittest

import mido

# events
from mutwo.events import basic
from mutwo.events import music

# converter
from mutwo.converters.frontends import midi
from mutwo.converters.frontends import midi_constants

# parameters
from mutwo.parameters import pitches


# TODO(write tests for the more complex methods!)


class MidiFileConverterTest(unittest.TestCase):
    def test_adjust_beat_length_in_seconds(self):
        # should return the same number
        tempo_event0 = basic.EnvelopeEvent(4, mido.bpm2tempo(40))
        self.assertEqual(
            midi.MidiFileConverter._adjust_beat_length_in_seconds(
                tempo_event0, tempo_event0.object_start
            ),
            tempo_event0.object_start,
        )

        # should return MAXIMUM_MICROSECONDS_PER_BEAT, because bpm 3
        # is already too slow
        tempo_event1 = basic.EnvelopeEvent(4, mido.bpm2tempo(3))
        self.assertEqual(
            midi.MidiFileConverter._adjust_beat_length_in_seconds(
                tempo_event1, tempo_event1.object_start
            ),
            midi_constants.MAXIMUM_MICROSECONDS_PER_BEAT,
        )

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
                midi_constants.DEFAULT_AVAILABLE_MIDI_CHANNELS
                for _ in range(n_sequential_events)
            ),
        )

        self.assertEqual(
            converter1._find_available_midi_channels_per_sequential_event(
                simultaneous_event
            ),
            tuple(
                (nth_channel % len(midi_constants.ALLOWED_MIDI_CHANNELS),)
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
            midi_constants.NEUTRAL_PITCH_BEND,
        )
        self.assertEqual(
            converter0._cent_deviation_to_pitch_bending_number(-200),
            -midi_constants.NEUTRAL_PITCH_BEND,
        )
        self.assertEqual(
            converter1._cent_deviation_to_pitch_bending_number(-500),
            -midi_constants.NEUTRAL_PITCH_BEND,
        )
        self.assertEqual(
            converter1._cent_deviation_to_pitch_bending_number(5000),
            midi_constants.NEUTRAL_PITCH_BEND,
        )

        # test too high / too low values
        self.assertEqual(
            converter0._cent_deviation_to_pitch_bending_number(250),
            midi_constants.NEUTRAL_PITCH_BEND,
        )
        self.assertEqual(
            converter0._cent_deviation_to_pitch_bending_number(-250),
            -midi_constants.NEUTRAL_PITCH_BEND,
        )

        # now test values inbetween
        self.assertEqual(
            converter0._cent_deviation_to_pitch_bending_number(100),
            int(midi_constants.NEUTRAL_PITCH_BEND * 0.5),
        )
        self.assertEqual(
            converter0._cent_deviation_to_pitch_bending_number(200 * 0.3),
            int(midi_constants.NEUTRAL_PITCH_BEND * 0.3),
        )

    def test_tune_pitch(self):
        converter = midi.MidiFileConverter("test.mid")
        data_to_tune_per_test = (
            # absolute_tick_start, pitch_to_tune, channel
            (0, pitches.WesternPitch("c", 4), 0),
            (0, pitches.WesternPitch("c", 4), 1),
            (1, pitches.WesternPitch("c", 4), 0),
            (1, pitches.WesternPitch("a", 4), 1),
            (7, pitches.WesternPitch("c", 3), 10),
            (4, pitches.WesternPitch("cqs", 3), 10),
            (4, pitches.WesternPitch("cqf", 3), 10),
            (0, pitches.WesternPitch("ces", 4), 12),
        )
        expected_midi_data_per_test = (
            # expected midi note, expected pitch bending
            (60, 0),
            (60, 0),
            (60, 0),
            (69, 0),
            (48, 0),
            (48, round(midi_constants.NEUTRAL_PITCH_BEND * 0.25)),
            (47, round(midi_constants.NEUTRAL_PITCH_BEND * 0.25)),
            (60, round(midi_constants.NEUTRAL_PITCH_BEND * 0.125)),
        )
        for data_to_tune, expected_midi_data in zip(
            data_to_tune_per_test, expected_midi_data_per_test
        ):
            expected_midi_data = (
                expected_midi_data[0],
                mido.Message(
                    "pitchwheel",
                    time=data_to_tune[0] - 1 if data_to_tune[0] > 0 else 0,
                    channel=data_to_tune[2],
                    pitch=expected_midi_data[1],
                ),
            )

            self.assertEqual(converter._tune_pitch(*data_to_tune), expected_midi_data)

    def test_tempo_events_to_midi_messages(self):
        pass

    def test_note_information_to_midi_messages(self):
        pass

    def test_extracted_data_to_midi_messages(self):
        pass


if __name__ == "__main__":
    unittest.main()
