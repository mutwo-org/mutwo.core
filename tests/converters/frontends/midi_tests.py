import itertools
import os
import unittest

import mido  # type: ignore

# events
from mutwo.events import basic
from mutwo.events import music

# converter
from mutwo.converters.frontends import midi
from mutwo.converters.frontends import midi_constants

# parameters
from mutwo.parameters import pitches
from mutwo.parameters import volumes


class MidiFileConverterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.midi_file_path = "tests/converters/frontends/test.mid"
        cls.converter = midi.MidiFileConverter(cls.midi_file_path)
        cls.sequential_event = basic.SequentialEvent(
            [
                music.NoteLike(pitches.WesternPitch(pitch), 1, 1)
                for pitch in "c d e f g a b a g f e d c".split(" ")
            ]
        )
        cls.simultaneous_event = basic.SimultaneousEvent(
            [cls.sequential_event, cls.sequential_event]
        )

    # ########################################################### #
    # tests to make sure that the methods return the expected     #
    # results.                                                    #
    # ########################################################### #

    def test_assert_midi_file_type_has_correct_type(self):
        for wrong_midi_file_type in ("hi", 2, 100, -10, 1.3, pitches.WesternPitch()):
            self.assertRaises(
                ValueError,
                lambda: self.converter._assert_midi_file_type_has_correct_value(
                    wrong_midi_file_type
                ),
            )

    def test_assert_available_midi_channels_have_correct_value(self):
        for problematic_available_midi_channels in ((0, 14, 19), (100,), ("hi", 12)):
            self.assertRaises(
                ValueError,
                lambda: self.converter._assert_available_midi_channels_have_correct_value(
                    problematic_available_midi_channels
                ),
            )

    def test_beats_per_minute_to_beat_length_in_microseconds(self):
        for bpm, beat_length_in_microseconds in (
            # bpm 60 should take one second per beat
            (60, 1000000),
            (30, 2000000),
            (120, 500000),
        ):
            self.assertEqual(
                self.converter._beats_per_minute_to_beat_length_in_microseconds(bpm),
                beat_length_in_microseconds,
            )

    def test_adjust_beat_length_in_microseconds(self):
        # should return the same number
        tempo_event0 = basic.EnvelopeEvent(4, mido.bpm2tempo(40))
        self.assertEqual(
            midi.MidiFileConverter._adjust_beat_length_in_microseconds(
                tempo_event0, tempo_event0.object_start
            ),
            tempo_event0.object_start,
        )

        # should return MAXIMUM_MICROSECONDS_PER_BEAT, because bpm 3
        # is already too slow
        tempo_event1 = basic.EnvelopeEvent(4, mido.bpm2tempo(3))
        self.assertEqual(
            midi.MidiFileConverter._adjust_beat_length_in_microseconds(
                tempo_event1, tempo_event1.object_start
            ),
            midi_constants.MAXIMUM_MICROSECONDS_PER_BEAT,
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

            self.assertEqual(
                self.converter._tune_pitch(*data_to_tune), expected_midi_data
            )

    def test_tempo_events_to_midi_messages(self):
        tempo_events = basic.SequentialEvent(
            [
                basic.EnvelopeEvent(2, 60),
                basic.EnvelopeEvent(3, 40),
                basic.EnvelopeEvent(2, 100),
            ]
        )
        midi_messages = tuple(
            mido.MetaMessage(
                "set_tempo",
                tempo=self.converter._beats_per_minute_to_beat_length_in_microseconds(
                    tempo_event.object_start
                ),
                time=absolute_time * midi_constants.DEFAULT_TICKS_PER_BEAT,
            )
            for absolute_time, tempo_event in zip(
                tempo_events.absolute_times, tempo_events
            )
        )

        self.assertEqual(
            self.converter._tempo_events_to_midi_messages(tempo_events), midi_messages
        )

    def test_note_information_to_midi_messages(self):
        # loop only channel 0
        midi_channel = 0
        available_midi_channels_cycle = itertools.cycle((midi_channel,))
        for note_information in (
            (0, 100, 127, pitches.WesternPitch("c", 4)),
            (200, 300, 0, pitches.WesternPitch("ds", 3)),
            (121, 122, 42, pitches.JustIntonationPitch("7/4")),
            (101221, 120122, 100, pitches.DirectPitch(443)),
            (12, 14, 122, pitches.DirectPitch(2)),
        ):
            start, end, velocity, pitch = note_information

            midi_pitch, pitch_bending_message = self.converter._tune_pitch(
                start, pitch, midi_channel
            )
            note_on_message = mido.Message(
                "note_on",
                note=midi_pitch,
                velocity=velocity,
                time=start,
                channel=midi_channel,
            )
            note_off_message = mido.Message(
                "note_off",
                note=midi_pitch,
                velocity=velocity,
                time=end,
                channel=midi_channel,
            )
            expected_midi_messages = (
                pitch_bending_message,
                note_on_message,
                note_off_message,
            )

            self.assertEqual(
                self.converter._note_information_to_midi_messages(
                    start, end, velocity, pitch, available_midi_channels_cycle
                ),
                expected_midi_messages,
            )

    def test_extracted_data_to_midi_messages(self):
        # TODO(is this really a test (just using the same code or code structure
        # that is used in the tested method)?)

        # loop only channel 0
        midi_channel = 0
        available_midi_channels_cycle = itertools.cycle((midi_channel,))
        for extracted_data in (
            (
                0,
                10,
                (pitches.WesternPitch("c", 4),),
                volumes.DecibelVolume(0),
                tuple([]),
            ),
            (
                101,
                232,
                (pitches.WesternPitch("ds", 2), pitches.JustIntonationPitch("3/7")),
                volumes.DirectVolume(0.1212),
                (mido.Message("control_change", channel=0, value=100, time=22),),
            ),
        ):
            (
                absolute_time,
                duration,
                pitch_or_pitches,
                volume,
                control_messages,
            ) = extracted_data
            start = self.converter._beats_to_ticks(absolute_time)
            end = self.converter._beats_to_ticks(duration) + start
            velocity = volume.midi_velocity
            expected_midi_messages = list(control_messages)
            for control_message in expected_midi_messages:
                control_message.time = start

            for pitch in pitch_or_pitches:
                expected_midi_messages.extend(
                    self.converter._note_information_to_midi_messages(
                        start, end, velocity, pitch, available_midi_channels_cycle
                    )
                )

            self.assertEqual(
                self.converter._extracted_data_to_midi_messages(
                    absolute_time,
                    duration,
                    available_midi_channels_cycle,
                    pitch_or_pitches,
                    volume,
                    control_messages,
                ),
                tuple(expected_midi_messages),
            )

    def test_simple_event_to_midi_messages(self):
        # loop only channel 2
        midi_channel = 2
        available_midi_channels_cycle = itertools.cycle((midi_channel,))

        # ########################### #
        #         test a rest         #
        # ########################### #

        # a rest shouldn't produce any messages
        rest = basic.SimpleEvent(2)
        self.assertEqual(
            self.converter._simple_event_to_midi_messages(
                rest, 0, available_midi_channels_cycle
            ),
            tuple([]),
        )

        # ########################### #
        #         test a tone         #
        # ########################### #

        tone = music.NoteLike(pitches.WesternPitch("c", 4), 2, 1)
        absolute_time1 = 32
        absolute_time1_in_ticks = self.converter._beats_to_ticks(absolute_time1)
        self.assertEqual(
            self.converter._simple_event_to_midi_messages(
                tone, absolute_time1, available_midi_channels_cycle
            ),
            (
                mido.Message(
                    "pitchwheel",
                    channel=midi_channel,
                    pitch=0,
                    time=absolute_time1_in_ticks - 1,
                ),
                mido.Message(
                    "note_on",
                    note=60,
                    velocity=127,
                    time=absolute_time1_in_ticks,
                    channel=midi_channel,
                ),
                mido.Message(
                    "note_off",
                    note=60,
                    velocity=127,
                    time=absolute_time1_in_ticks
                    + self.converter._beats_to_ticks(tone.duration),
                    channel=midi_channel,
                ),
            ),
        )

        # ########################### #
        #         test a chord        #
        # ########################### #

        # use two different channels
        midi_channels = 2, 3
        available_midi_channels_cycle = itertools.cycle(midi_channels)

        chord = music.NoteLike(
            [pitches.WesternPitch("c", 4), pitches.WesternPitch("aqs", 4)], 2, 0.5
        )
        absolute_time2 = 2
        absolute_time2_in_ticks = self.converter._beats_to_ticks(absolute_time2)
        self.assertEqual(
            self.converter._simple_event_to_midi_messages(
                chord, absolute_time2, available_midi_channels_cycle
            ),
            (
                mido.Message(
                    "pitchwheel",
                    channel=midi_channels[0],
                    pitch=0,
                    time=absolute_time2_in_ticks - 1,
                ),
                mido.Message(
                    "note_on",
                    note=60,
                    velocity=64,
                    time=absolute_time2_in_ticks,
                    channel=midi_channels[0],
                ),
                mido.Message(
                    "note_off",
                    note=60,
                    velocity=64,
                    time=absolute_time2_in_ticks
                    + self.converter._beats_to_ticks(tone.duration),
                    channel=midi_channels[0],
                ),
                mido.Message(
                    "pitchwheel",
                    channel=midi_channels[1],
                    pitch=2048,
                    time=absolute_time2_in_ticks - 1,
                ),
                mido.Message(
                    "note_on",
                    note=69,
                    velocity=64,
                    time=absolute_time2_in_ticks,
                    channel=midi_channels[1],
                ),
                mido.Message(
                    "note_off",
                    note=69,
                    velocity=64,
                    time=absolute_time2_in_ticks
                    + self.converter._beats_to_ticks(tone.duration),
                    channel=midi_channels[1],
                ),
            ),
        )

    def test_sequential_event_to_midi_messages(self):
        pass

    def test_midi_messages_to_midi_track(self):
        pass

    def test_add_simple_event_to_midi_file(self):
        pass

    def test_add_sequential_event_to_midi_file(self):
        pass

    def test_add_simultaneous_event_to_midi_file(self):
        pass

    def test_event_to_midi_file(self):
        pass

    # ########################################################### #
    # tests to make sure that the different init arguments do     #
    # work correctly                                              #
    # ########################################################### #

    def test_correct_midi_file_type(self):
        # make sure generated midi file has the correct midi file type

        converter0 = midi.MidiFileConverter(self.midi_file_path, midi_file_type=0)
        converter1 = midi.MidiFileConverter(self.midi_file_path, midi_file_type=1)

        for converter in (converter0, converter1):
            for event in (self.sequential_event, self.simultaneous_event):
                converter.convert(self.simultaneous_event)
                midi_file = mido.MidiFile(converter.path)
                self.assertEqual(midi_file.type, converter._midi_file_type)
                os.remove(converter.path)

    def test_overriding_simple_event_to_arguments(self):
        # make sure generated midi file has the correct midi file type

        constant_pitch = pitches.WesternPitch("c")
        constant_volume = volumes.DirectVolume(1)
        constant_control_message = mido.Message("control_change", value=100)
        converter = midi.MidiFileConverter(
            self.midi_file_path,
            simple_event_to_pitches=lambda event: (constant_pitch,),
            simple_event_to_volume=lambda event: constant_volume,
            simple_event_to_control_messages=lambda event: (constant_control_message,),
        )

        converter.convert(self.sequential_event)
        midi_file = mido.MidiFile(converter.path)
        n_control_message = 0
        n_note_on_messages = 0
        for message in midi_file:
            if message.type == "note_on":
                self.assertAlmostEqual(message.note, constant_pitch.midi_pitch_number)
                self.assertEqual(
                    message.velocity, constant_volume.midi_velocity,
                )
                n_note_on_messages += 1
            elif message.type == "control_change":
                self.assertEqual(message.value, constant_control_message.value)
                n_control_message += 1

        self.assertEqual(n_note_on_messages, len(self.sequential_event))
        self.assertEqual(n_control_message, len(self.sequential_event))

        os.remove(converter.path)

    def test_available_midi_channels_argument(self):
        # make sure mutwo only writes notes to midi channel that are
        # available and furthermore cycles through all available midi
        # channels!

        for available_midi_channels in ((0,), (0, 1, 2, 3), (0, 3, 4), (2, 11,)):
            converter = midi.MidiFileConverter(
                self.midi_file_path, available_midi_channels=available_midi_channels
            )
            converter.convert(self.sequential_event)
            midi_file = mido.MidiFile(converter.path)
            available_midi_channels_cycle = itertools.cycle(available_midi_channels)
            for message in midi_file:
                if message.type == "note_on":
                    self.assertEqual(
                        message.channel, next(available_midi_channels_cycle)
                    )
            os.remove(converter.path)

    def test_distribute_midi_channels_argument(self):
        # makes sure mutwo distributes midi channels on different
        # sequential events according to the behaviour that is written
        # in the MidiFileConverter docstring

        pass


if __name__ == "__main__":
    unittest.main()
