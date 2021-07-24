import os
import unittest

from PIL import Image  # type: ignore
from PIL import ImageChops  # type: ignore

import abjad  # type: ignore
import expenvelope  # type: ignore

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

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


class MutwoPitchToHEJIAbjadPitchConverterTest(unittest.TestCase):
    def test_convert(self):
        converter = frontends.abjad.MutwoPitchToHEJIAbjadPitchConverter(
            reference_pitch="c"
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(parameters.pitches.JustIntonationPitch("1/1"))
            ),
            abjad.lilypond(abjad.NamedPitch("c'")),
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(parameters.pitches.JustIntonationPitch("3/2"))
            ),
            abjad.lilypond(abjad.NamedPitch("g'")),
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(parameters.pitches.JustIntonationPitch("5/4"))
            ),
            "eoaa'",
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(parameters.pitches.JustIntonationPitch("7/4"))
            ),
            "bfoba'",
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(parameters.pitches.JustIntonationPitch("7/6"))
            ),
            "efoba'",
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(parameters.pitches.JustIntonationPitch("12/7"))
            ),
            "auba'",
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(parameters.pitches.JustIntonationPitch("9/8"))
            ),
            "d'",
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(parameters.pitches.JustIntonationPitch("9/16"))
            ),
            "d",
        )
        self.assertEqual(
            abjad.lilypond(
                converter.convert(parameters.pitches.JustIntonationPitch("9/4"))
            ),
            "d''",
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
    @staticmethod
    def _are_png_equal(path_to_png0: str, path_to_png1: str) -> bool:
        image0, image1 = (Image.open(path) for path in (path_to_png0, path_to_png1))
        difference = ImageChops.difference(image1, image0)
        return difference.getbbox() is None

    @staticmethod
    def _make_complex_sequential_event() -> basic.SequentialEvent[music.NoteLike]:
        complex_sequential_event = basic.SequentialEvent(
            [
                music.NoteLike(pitch_name, duration=duration, volume="mf")
                for pitch_name, duration in (
                    ("c f a d", 0.75),
                    ("a", 0.25),
                    ("g", fractions.Fraction(1, 12)),
                    ("es", fractions.Fraction(1, 12)),
                    ("fqs bf bqf", fractions.Fraction(1, 12)),
                    ("c", fractions.Fraction(3, 4)),
                    ([], 1),  # full measure rest
                    ("ds", 0.75),
                    ([], fractions.Fraction(3, 8)),
                    ("1/3", 0.75),
                    ([], 0.25),
                    ("1/7", 1.5),
                    ("5/4", 0.25),
                    ("7/4", fractions.Fraction(1, 8)),
                    ([], fractions.Fraction(3, 4)),
                    ("c", fractions.Fraction(1, 4)),
                    ("c", fractions.Fraction(1, 4)),
                    ("c", fractions.Fraction(1, 4)),
                    ("c", fractions.Fraction(1, 4)),
                    ("c", fractions.Fraction(1, 4)),
                    ("c", fractions.Fraction(1, 4)),
                )
            ]
        )

        complex_sequential_event[0].notation_indicators.margin_markup.content = (
            "Magic Instr"
        )
        complex_sequential_event[2].playing_indicators.bartok_pizzicato.is_active = True
        complex_sequential_event[3].volume = "fff"
        complex_sequential_event[4].volume = "fff"
        complex_sequential_event[7].playing_indicators.fermata.fermata_type = "fermata"
        complex_sequential_event[9].notation_indicators.ottava.n_octaves = -1
        complex_sequential_event[
            9
        ].playing_indicators.string_contact_point.contact_point = (
            "sul tasto"
        )
        complex_sequential_event[
            11
        ].playing_indicators.string_contact_point.contact_point = (
            "sul tasto"
        )
        complex_sequential_event[11].notation_indicators.ottava.n_octaves = -2
        complex_sequential_event[
            12
        ].playing_indicators.string_contact_point.contact_point = (
            "pizzicato"
        )
        return complex_sequential_event

    @classmethod
    def setUpClass(cls):
        # initialise converter and sequential event for simple tests
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
        # initialise complex converter and sequential event for complex tests
        cls.complex_converter = frontends.abjad.SequentialEventToAbjadVoiceConverter(
            frontends.abjad.SequentialEventToQuantizedAbjadContainerConverter(
                time_signatures=[
                    abjad.TimeSignature(ts)
                    for ts in (
                        (4, 4),
                        (4, 4),
                        (4, 4),
                        (4, 4),
                        (4, 4),
                        (4, 4),
                        (4, 4),
                        (3, 4),
                        (6, 8),
                        (3, 4),
                    )
                ],
                tempo_envelope=expenvelope.Envelope.from_levels_and_durations(
                    levels=(120, 120, 130, 130, 100), durations=(3, 2, 2.75, 0)
                ),
            )
        )
        cls.complex_sequential_event = (
            SequentialEventToAbjadVoiceConverterTest._make_complex_sequential_event()
        )

    def test_convert(self):
        # TODO(improve readability of conversion method!)
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

    def test_general_convert_with_lilypond_output(self):
        # basically an integration test (testing if the rendered png
        # is equal to the previously rendered and manually checked png)
        converted_sequential_event = self.complex_converter.convert(
            self.complex_sequential_event
        )
        tests_path = "tests/converters/frontends"
        png_file_to_compare_path = "{}/abjad_expected_png_output.png".format(tests_path)
        new_png_file_path = "{}/abjad_png_output.png".format(tests_path)
        lilypond_file = abjad.LilyPondFile()
        header_block = abjad.Block(name="header")
        header_block.tagline = abjad.Markup("---integration-test---")
        score_block = abjad.Block(name="score")
        score_block.items.append([abjad.Staff([converted_sequential_event])])
        lilypond_file.items.extend((header_block, score_block))
        abjad.persist.as_png(
            lilypond_file, png_file_path=new_png_file_path, remove_ly=True
        )

        self.assertTrue(
            SequentialEventToAbjadVoiceConverterTest._are_png_equal(
                new_png_file_path, png_file_to_compare_path
            )
        )

        # remove test file
        os.remove(new_png_file_path)

    def test_tempo_range_conversion(self):
        # basically an integration test (testing if the rendered png
        # is equal to the previously rendered and manually checked png)
        # -> this tests, if the resulting notation prints tempo ranges

        tempo_envelope = expenvelope.Envelope.from_levels_and_durations(
            levels=[
                parameters.tempos.TempoPoint((30, 50), 2),
                parameters.tempos.TempoPoint((30, 50), 2),
            ],
            durations=[2],
        )
        converter = frontends.abjad.SequentialEventToAbjadVoiceConverter(
            frontends.abjad.SequentialEventToQuantizedAbjadContainerConverter(
                tempo_envelope=tempo_envelope
            )
        )
        sequential_event_to_convert = basic.SequentialEvent(
            [music.NoteLike("c", 1), music.NoteLike("c", 1), music.NoteLike("c", 1)]
        )
        converted_sequential_event = converter.convert(sequential_event_to_convert)

        tests_path = "tests/converters/frontends"
        png_file_to_compare_path = (
            "{}/abjad_expected_png_output_for_tempo_range_test.png".format(tests_path)
        )
        new_png_file_path = "{}/abjad_png_output_for_tempo_range_test.png".format(
            tests_path
        )

        lilypond_file = abjad.LilyPondFile()
        header_block = abjad.Block(name="header")
        header_block.tagline = abjad.Markup("---integration-test---")
        score_block = abjad.Block(name="score")
        score_block.items.append([abjad.Staff([converted_sequential_event])])
        lilypond_file.items.extend((header_block, score_block))
        abjad.persist.as_png(
            lilypond_file, png_file_path=new_png_file_path, remove_ly=True
        )

        self.assertTrue(
            SequentialEventToAbjadVoiceConverterTest._are_png_equal(
                new_png_file_path, png_file_to_compare_path
            )
        )

        # remove test file
        os.remove(new_png_file_path)

    def test_duration_line_notation(self):
        # basically an integration test (testing if the rendered png
        # is equal to the previously rendered and manually checked png)
        # -> this tests, if duration lines are printed in a correct manner

        converter = frontends.abjad.SequentialEventToAbjadVoiceConverter(
            frontends.abjad.SequentialEventToDurationLineBasedQuantizedAbjadContainerConverter()
        )
        sequential_event_to_convert = basic.SequentialEvent(
            [
                music.NoteLike([], 1),
                music.NoteLike("c", 0.125),
                music.NoteLike("d", 1),
                music.NoteLike([], 0.375),
                music.NoteLike("e", 0.25),
                music.NoteLike("d", 0.5),
                music.NoteLike("c", 0.75),
                music.NoteLike("a", 0.25),
            ]
        )
        converted_sequential_event = converter.convert(sequential_event_to_convert)

        tests_path = "tests/converters/frontends"
        png_file_to_compare_path = (
            "{}/abjad_expected_png_output_for_duration_line_test.png".format(tests_path)
        )
        new_png_file_path = "{}/abjad_png_output_for_duration_line_test.png".format(
            tests_path
        )

        lilypond_file = abjad.LilyPondFile()
        header_block = abjad.Block(name="header")
        header_block.tagline = abjad.Markup("---integration-test---")
        score_block = abjad.Block(name="score")
        score_block.items.append([abjad.Staff([converted_sequential_event])])
        lilypond_file.items.extend((header_block, score_block))
        abjad.persist.as_png(
            lilypond_file, png_file_path=new_png_file_path, remove_ly=True
        )

        self.assertTrue(
            SequentialEventToAbjadVoiceConverterTest._are_png_equal(
                new_png_file_path, png_file_to_compare_path
            )
        )

        # remove test file
        os.remove(new_png_file_path)


if __name__ == "__main__":
    unittest.main()
