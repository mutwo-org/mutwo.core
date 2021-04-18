import unittest

import abjad  # type: ignore
import expenvelope  # type: ignore

from mutwo.converters import frontends
from mutwo.events import basic
from mutwo.events import music
from mutwo import parameters

# TODO(Add more unit tests to make abjad conversion more reliable!)


class MutwoPitchToAbjadPitchConverterTest(unittest.TestCase):
    def test_convert(self):
        converter = frontends.abjad.MutwoPitchToAbjadPitchConverter()
        self.assertEqual(
            converter.convert(parameters.pitches.WesternPitch("ds", 4)),
            abjad.NamedPitch("ds'"),
        )
        self.assertEqual(
            converter.convert(parameters.pitches.WesternPitch("gf", 5)),
            abjad.NamedPitch("gf''"),
        )
        self.assertEqual(
            converter.convert(
                parameters.pitches.JustIntonationPitch("3/2", concert_pitch=262)
            ),
            abjad.NumberedPitch(7),
        )
        self.assertEqual(
            converter.convert(
                parameters.pitches.JustIntonationPitch("3/4", concert_pitch=262)
            ),
            abjad.NumberedPitch(-5),
        )
        self.assertEqual(
            converter.convert(
                parameters.pitches.JustIntonationPitch("5/4", concert_pitch=262)
            ),
            abjad.NumberedPitch(4),
        )


class MutwoVolumeToAbjadAttachmentDynamicConverterTest(unittest.TestCase):
    def test_convert(self):
        converter = frontends.abjad.MutwoVolumeToAbjadAttachmentDynamicConverter()
        self.assertEqual(
            converter.convert(parameters.volumes.WesternVolume("mf")),
            frontends.abjad_attachments.Dynamic("mf"),
        )
        self.assertEqual(
            converter.convert(parameters.volumes.WesternVolume("fff")),
            frontends.abjad_attachments.Dynamic("fff"),
        )
        self.assertEqual(
            converter.convert(parameters.volumes.DecibelVolume(-6)),
            frontends.abjad_attachments.Dynamic(
                parameters.volumes.WesternVolume.from_decibel(-6).name
            ),
        )


class ComplexTempoEnvelopeToAbjadAttachmentTempoConverterTest(unittest.TestCase):
    def test_convert_tempo_points(self):
        self.assertEqual(
            frontends.abjad.ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._convert_tempo_points(
                (60, 120, parameters.tempos.TempoPoint(120, reference=4))
            ),
            (
                parameters.tempos.TempoPoint(60),
                parameters.tempos.TempoPoint(120),
                parameters.tempos.TempoPoint(120, reference=4),
            ),
        )

    def test_find_dynamic_change_indication(self):
        self.assertEqual(
            frontends.abjad.ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._find_dynamic_change_indication(
                parameters.tempos.TempoPoint(120), parameters.tempos.TempoPoint(130)
            ),
            "acc.",
        )
        self.assertEqual(
            frontends.abjad.ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._find_dynamic_change_indication(
                parameters.tempos.TempoPoint(120), parameters.tempos.TempoPoint(110)
            ),
            "rit.",
        )
        self.assertEqual(
            frontends.abjad.ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._find_dynamic_change_indication(
                parameters.tempos.TempoPoint(120), parameters.tempos.TempoPoint(120)
            ),
            None,
        )
        self.assertEqual(
            frontends.abjad.ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._find_dynamic_change_indication(
                parameters.tempos.TempoPoint(120),
                parameters.tempos.TempoPoint(60, reference=2),
            ),
            None,
        )

    def test_shall_write_metronome_mark(self):
        tempo_envelope_to_convert = expenvelope.Envelope.from_levels_and_durations(
            levels=[
                parameters.tempos.TempoPoint(bpm)
                for bpm in (120, 120, 110, 120, 110, 120, 110, 100)
            ],
            durations=[2, 2, 2, 2, 0, 2, 0],
        )
        self.assertEqual(
            frontends.abjad.ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._shall_write_metronome_mark(
                tempo_envelope_to_convert,
                1,
                tempo_envelope_to_convert.levels[1],
                tempo_envelope_to_convert.levels,
            ),
            False,
        )
        self.assertEqual(
            frontends.abjad.ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._shall_write_metronome_mark(
                tempo_envelope_to_convert,
                2,
                tempo_envelope_to_convert.levels[2],
                tempo_envelope_to_convert.levels,
            ),
            True,
        )
        self.assertEqual(
            frontends.abjad.ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._shall_write_metronome_mark(
                tempo_envelope_to_convert,
                5,
                tempo_envelope_to_convert.levels[5],
                tempo_envelope_to_convert.levels,
            ),
            False,
        )
        self.assertEqual(
            frontends.abjad.ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._shall_write_metronome_mark(
                tempo_envelope_to_convert,
                7,
                tempo_envelope_to_convert.levels[7],
                tempo_envelope_to_convert.levels,
            ),
            True,
        )

    def test_shall_stop_dynamic_change_indication(self):
        previous_tempo_attachments = (
            (0, frontends.abjad_attachments.Tempo(dynamic_change_indication="rit.")),
            (2, frontends.abjad_attachments.Tempo(dynamic_change_indication=None)),
        )
        self.assertEqual(
            frontends.abjad.ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._shall_stop_dynamic_change_indication(
                previous_tempo_attachments
            ),
            False,
        )
        self.assertEqual(
            frontends.abjad.ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._shall_stop_dynamic_change_indication(
                previous_tempo_attachments[:1]
            ),
            True,
        )

    def test_find_metronome_mark_values(self):
        self.assertEqual(
            frontends.abjad.ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._find_metronome_mark_values(
                True,
                parameters.tempos.TempoPoint(
                    60, reference=2, textual_indication="ordinary"
                ),
                False,
            ),
            ((1, 2), 60, "ordinary"),
        )
        self.assertEqual(
            frontends.abjad.ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._find_metronome_mark_values(
                True,
                parameters.tempos.TempoPoint(
                    120, reference=1, textual_indication="faster"
                ),
                False,
            ),
            ((1, 4), 120, "faster"),
        )
        self.assertEqual(
            frontends.abjad.ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._find_metronome_mark_values(
                False,
                parameters.tempos.TempoPoint(
                    120, reference=1, textual_indication="faster"
                ),
                False,
            ),
            (None, None, None),
        )
        self.assertEqual(
            frontends.abjad.ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._find_metronome_mark_values(
                False,
                parameters.tempos.TempoPoint(
                    120, reference=1, textual_indication="faster"
                ),
                True,
            ),
            (None, None, "a tempo"),
        )

    def test_process_tempo_event(self):
        tempo_envelope_to_convert = expenvelope.Envelope.from_levels_and_durations(
            levels=[
                parameters.tempos.TempoPoint(bpm)
                for bpm in (120, 120, 110, 120, 110, 120, 110, 100)
            ],
            durations=[2, 2, 2, 2, 0, 2, 0],
        )
        tempo_points = tempo_envelope_to_convert.levels
        tempo_attachments = (
            (
                0,
                frontends.abjad_attachments.Tempo(
                    reference_duration=(1, 4),
                    units_per_minute=120,
                    textual_indication=None,
                    dynamic_change_indication=None,
                    stop_dynamic_change_indicaton=False,
                    print_metronome_mark=True,
                ),
            ),
            (
                2,
                frontends.abjad_attachments.Tempo(
                    reference_duration=None,
                    units_per_minute=None,
                    textual_indication=None,
                    dynamic_change_indication="rit.",
                    stop_dynamic_change_indicaton=False,
                    print_metronome_mark=False,
                ),
            ),
            (
                4,
                frontends.abjad_attachments.Tempo(
                    reference_duration=(1, 4),
                    units_per_minute=110,
                    textual_indication=None,
                    dynamic_change_indication="acc.",
                    stop_dynamic_change_indicaton=True,
                    print_metronome_mark=True,
                ),
            ),
            (
                6,
                frontends.abjad_attachments.Tempo(
                    reference_duration=(1, 4),
                    units_per_minute=120,
                    textual_indication=None,
                    dynamic_change_indication="rit.",
                    stop_dynamic_change_indicaton=True,
                    print_metronome_mark=True,
                ),
            ),
            (
                8,
                frontends.abjad_attachments.Tempo(
                    reference_duration=None,
                    units_per_minute=None,
                    textual_indication="a tempo",
                    dynamic_change_indication="rit.",
                    stop_dynamic_change_indicaton=True,
                    print_metronome_mark=True,
                ),
            ),
        )

        for nth_tempo_point, nth_tempo_attachment in (
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (5, 4),
        ):
            tempo_point = tempo_points[nth_tempo_point]
            current_tempo_attachments = tempo_attachments[:nth_tempo_attachment]
            current_tempo_attachment = tempo_attachments[nth_tempo_attachment][1]
            self.assertEqual(
                frontends.abjad.ComplexTempoEnvelopeToAbjadAttachmentTempoConverter._process_tempo_event(
                    tempo_envelope_to_convert,
                    nth_tempo_point,
                    tempo_point,
                    tempo_points,
                    current_tempo_attachments,
                ),
                current_tempo_attachment,
            )


class SequentialEventToAbjadVoiceConverterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.converter = frontends.abjad.SequentialEventToAbjadVoiceConverter()
        cls.sequential_event = basic.SequentialEvent(
            [
                music.NoteLike(pitch_name, duration=duration, volume="mf")
                for pitch_name, duration in (
                    ("c", 0.75),
                    ("a", 0.25),
                    ("g", 1 / 6),
                    ("es", 1 / 12),
                )
            ]
        )

    def test_convert(self):
        expected_abjad_voice = abjad.Voice(
            [
                abjad.score.Container("c'2. a'4"),
                abjad.score.Container(
                    [abjad.Tuplet(components="g'4 es'8"), abjad.Rest((3, 4))]
                ),
            ]
        )
        abjad.attach(abjad.TimeSignature((4, 4)), expected_abjad_voice[0][0])
        abjad.attach(abjad.Dynamic("mf"), expected_abjad_voice[0][0])
        abjad.attach(
            abjad.MetronomeMark(reference_duration=(1, 4), units_per_minute=120),
            expected_abjad_voice[0][0],
        )

        converted_sequential_event = self.converter.convert(self.sequential_event)

        # complex comparison because == raises Error (although leaves are equal)
        for component0, component1 in zip(
            abjad.select(expected_abjad_voice).components(),
            abjad.select(converted_sequential_event).components(),
        ):
            self.assertEqual(type(component0), type(component1))
            if hasattr(component0, "written_duration"):
                self.assertEqual(
                    component0.written_duration, component1.written_duration
                )
            if isinstance(component0, abjad.Note):
                self.assertEqual(component0.written_pitch, component1.written_pitch)

            indicators0, indicators1 = (
                # filter out q_events annotations
                [
                    indicator
                    for indicator in abjad.get.indicators(component)
                    if type(indicator) != dict
                ]
                for component in (component0, component1)
            )

            self.assertEqual(indicators0, indicators1)


if __name__ == "__main__":
    unittest.main()
