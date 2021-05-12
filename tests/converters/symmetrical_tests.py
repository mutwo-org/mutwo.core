import unittest

import expenvelope  # type: ignore

import mutwo.converters.symmetrical.loudness
import mutwo.converters.symmetrical.metricities
import mutwo.converters.symmetrical.tempos
from mutwo import converters
from mutwo.events import basic
from mutwo.parameters import tempos


class LoudnessToAmplitudeConverterTest(unittest.TestCase):
    def test_sone_to_phon(self):
        self.assertEqual(
            mutwo.converters.symmetrical.loudness.LoudnessToAmplitudeConverter._sone_to_phon(1), 40
        )
        self.assertEqual(
            mutwo.converters.symmetrical.loudness.LoudnessToAmplitudeConverter._sone_to_phon(2), 50
        )
        self.assertEqual(
            mutwo.converters.symmetrical.loudness.LoudnessToAmplitudeConverter._sone_to_phon(0.5),
            31.39434452534506,
        )

    def test_convert(self):
        converter = mutwo.converters.symmetrical.loudness.LoudnessToAmplitudeConverter(1)

        # test different frequencies
        self.assertAlmostEqual(converter.convert(50), 0.1549792455)
        self.assertAlmostEqual(converter.convert(100), 0.03308167306999658)
        self.assertAlmostEqual(converter.convert(200), 0.0093641)
        self.assertAlmostEqual(converter.convert(500), 0.0028416066734875583)
        self.assertAlmostEqual(converter.convert(2000), 0.0018302564694597117)
        self.assertAlmostEqual(converter.convert(10000), 0.010357060382149575)

        # test different loudness
        converter = mutwo.converters.symmetrical.loudness.LoudnessToAmplitudeConverter(0.5)
        self.assertAlmostEqual(converter.convert(50), 0.08150315492680121)
        self.assertAlmostEqual(converter.convert(100), 0.015624188922340446)
        self.assertAlmostEqual(converter.convert(200), 0.003994808241065453)
        self.assertAlmostEqual(converter.convert(500), 0.0010904941511850816)


class RhythmicalStrataToIndispensabilityConverterTest(unittest.TestCase):
    def test_convert(self):
        converter = mutwo.converters.symmetrical.metricities.RhythmicalStrataToIndispensabilityConverter()

        # 3/4
        self.assertEqual(converter.convert((2, 3)), (5, 0, 3, 1, 4, 2))
        # 6/8
        self.assertEqual(converter.convert((3, 2)), (5, 0, 2, 4, 1, 3))


class TempoPointConverterTest(unittest.TestCase):
    def test_convert_beats_per_minute_to_seconds_per_beat(self):
        self.assertEqual(
            mutwo.converters.symmetrical.tempos.TempoPointConverter._beats_per_minute_to_seconds_per_beat(
                60
            ),
            1,
        )
        self.assertEqual(
            mutwo.converters.symmetrical.tempos.TempoPointConverter._beats_per_minute_to_seconds_per_beat(
                30
            ),
            2,
        )
        self.assertEqual(
            mutwo.converters.symmetrical.tempos.TempoPointConverter._beats_per_minute_to_seconds_per_beat(
                120
            ),
            0.5,
        )

    def test_extract_beats_per_minute_and_reference_from_complete_tempo_point_object(
        self,
    ):
        tempo_point = tempos.TempoPoint(40, 2)
        self.assertEqual(
            mutwo.converters.symmetrical.tempos.TempoPointConverter._extract_beats_per_minute_and_reference_from_tempo_point(
                tempo_point
            ),
            (tempo_point.tempo_in_beats_per_minute, tempo_point.reference),
        )

    def test_extract_beats_per_minute_and_reference_from_incomplete_tempo_point_object(
        self,
    ):
        tempo_point = tempos.TempoPoint(40)
        self.assertEqual(
            mutwo.converters.symmetrical.tempos.TempoPointConverter._extract_beats_per_minute_and_reference_from_tempo_point(
                tempo_point
            ),
            (tempo_point.tempo_in_beats_per_minute, 1),
        )

    def test_extract_beats_per_minute_and_reference_from_number(self):
        tempo_point = 60
        self.assertEqual(
            mutwo.converters.symmetrical.tempos.TempoPointConverter._extract_beats_per_minute_and_reference_from_tempo_point(
                tempo_point
            ),
            (60, 1),
        )

    def test_convert(self):
        tempo_point0 = tempos.TempoPoint(60, 1)
        tempo_point1 = tempos.TempoPoint(60, 2)
        tempo_point2 = tempos.TempoPoint(30, 1)
        tempo_point3 = 60
        tempo_point4 = 120

        converter = mutwo.converters.symmetrical.tempos.TempoPointConverter()

        self.assertEqual(converter.convert(tempo_point0), 1)
        self.assertEqual(converter.convert(tempo_point1), 0.5)
        self.assertEqual(converter.convert(tempo_point2), 2)
        self.assertEqual(converter.convert(tempo_point3), 1)
        self.assertEqual(converter.convert(tempo_point4), 0.5)


class TempoConverterTest(unittest.TestCase):
    def test_convert_simple_event(self):
        tempo_envelope = expenvelope.Envelope.from_levels_and_durations(
            levels=[30, 60], durations=[4]
        )
        simple_event = basic.SimpleEvent(4)
        converter = mutwo.converters.symmetrical.tempos.TempoConverter(tempo_envelope)
        converted_simple_event = converter.convert(simple_event)
        expected_duration = 6
        self.assertEqual(converted_simple_event.duration, expected_duration)

    def test_convert_sequential_event(self):
        sequential_event = basic.SequentialEvent(
            [basic.SimpleEvent(2) for _ in range(5)]
        )
        tempo_envelope = expenvelope.Envelope.from_levels_and_durations(
            levels=[
                30,
                tempos.TempoPoint(30),
                60,
                tempos.TempoPoint(60),
                30,
                30,
                60,
                30,
                60,
                tempos.TempoPoint(30, reference=1),
                tempos.TempoPoint(30, reference=2),  # -> 60 BPM for ref=1
            ],
            durations=[2, 0, 1, 0, 1, 2, 0, 2, 0, 2],
            curve_shapes=[0, 0, 0, 0, 0, 0, 0, 10, 0, -10],
        )
        converter = mutwo.converters.symmetrical.tempos.TempoConverter(tempo_envelope)
        converted_sequential_event = converter.convert(sequential_event)
        expected_durations = (4, 3, 3, 3.8000908039820196, 2.1999091960179804)
        self.assertEqual(
            converted_sequential_event.get_parameter("duration"), expected_durations
        )

    def test_convert_simultaneous_event(self):
        tempo_envelope = expenvelope.Envelope.from_levels_and_durations(
            levels=[30, 60], durations=[4]
        )
        simple_event0 = basic.SimpleEvent(4)
        simple_event1 = basic.SimpleEvent(8)
        simultaneous_event = basic.SimultaneousEvent(
            [simple_event0, simple_event0, simple_event1]
        )
        converter = mutwo.converters.symmetrical.tempos.TempoConverter(tempo_envelope)
        converted_simultaneous_event = converter.convert(simultaneous_event)
        expected_duration0 = simultaneous_event[0].duration * 1.5
        expected_duration1 = 10
        self.assertEqual(converted_simultaneous_event[0].duration, expected_duration0)
        self.assertEqual(converted_simultaneous_event[1].duration, expected_duration0)
        self.assertEqual(converted_simultaneous_event[2].duration, expected_duration1)


if __name__ == "__main__":
    unittest.main()
