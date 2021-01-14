import unittest

from mutwo import converters
from mutwo.parameters import tempos


class TempoPointConverterTest(unittest.TestCase):
    def test_convert_beats_per_minute_to_seconds_per_beat(self):
        self.assertEqual(
            converters.symmetrical.TempoPointConverter.beats_per_minute_to_seconds_per_beat(
                60
            ),
            1,
        )
        self.assertEqual(
            converters.symmetrical.TempoPointConverter.beats_per_minute_to_seconds_per_beat(
                30
            ),
            2,
        )
        self.assertEqual(
            converters.symmetrical.TempoPointConverter.beats_per_minute_to_seconds_per_beat(
                120
            ),
            0.5,
        )

    def test_extract_beats_per_minute_and_reference_from_complete_tempo_point_object(
        self,
    ):
        tempo_point = tempos.TempoPoint(40, 2)
        self.assertEqual(
            converters.symmetrical.TempoPointConverter.extract_beats_per_minute_and_reference_from_tempo_point(
                tempo_point
            ),
            (tempo_point.tempo_in_beats_per_minute, tempo_point.reference),
        )

    def test_extract_beats_per_minute_and_reference_from_incomplete_tempo_point_object(
        self,
    ):
        tempo_point = tempos.TempoPoint(40)
        self.assertEqual(
            converters.symmetrical.TempoPointConverter.extract_beats_per_minute_and_reference_from_tempo_point(
                tempo_point
            ),
            (tempo_point.tempo_in_beats_per_minute, 1),
        )

    def test_extract_beats_per_minute_and_reference_from_number(self):
        tempo_point = 60
        self.assertEqual(
            converters.symmetrical.TempoPointConverter.extract_beats_per_minute_and_reference_from_tempo_point(
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

        converter = converters.symmetrical.TempoPointConverter()

        self.assertEqual(converter.convert(tempo_point0), 1)
        self.assertEqual(converter.convert(tempo_point1), 0.5)
        self.assertEqual(converter.convert(tempo_point2), 2)
        self.assertEqual(converter.convert(tempo_point3), 1)
        self.assertEqual(converter.convert(tempo_point4), 0.5)


if __name__ == "__main__":
    unittest.main()
