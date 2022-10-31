import unittest

from mutwo import core_converters
from mutwo import core_events
from mutwo import core_parameters


class TempoPointConverterTest(unittest.TestCase):
    def test_convert_beats_per_minute_to_seconds_per_beat(self):
        self.assertEqual(
            core_converters.TempoPointConverter._beats_per_minute_to_seconds_per_beat(
                60
            ),
            1,
        )
        self.assertEqual(
            core_converters.TempoPointConverter._beats_per_minute_to_seconds_per_beat(
                30
            ),
            2,
        )
        self.assertEqual(
            core_converters.TempoPointConverter._beats_per_minute_to_seconds_per_beat(
                120
            ),
            0.5,
        )

    def test_extract_beats_per_minute_and_reference_from_complete_tempo_point_object(
        self,
    ):
        tempo_point = core_parameters.TempoPoint(40, 2)
        self.assertEqual(
            core_converters.TempoPointConverter._extract_beats_per_minute_and_reference_from_tempo_point(
                tempo_point
            ),
            (tempo_point.tempo_in_beats_per_minute, tempo_point.reference),
        )

    def test_extract_beats_per_minute_and_reference_from_incomplete_tempo_point_object(
        self,
    ):
        tempo_point = core_parameters.TempoPoint(40)
        self.assertEqual(
            core_converters.TempoPointConverter._extract_beats_per_minute_and_reference_from_tempo_point(
                tempo_point
            ),
            (tempo_point.tempo_in_beats_per_minute, 1),
        )

    def test_extract_beats_per_minute_and_reference_from_number(self):
        tempo_point = 60
        self.assertEqual(
            core_converters.TempoPointConverter._extract_beats_per_minute_and_reference_from_tempo_point(
                tempo_point
            ),
            (60, 1),
        )

    def test_convert(self):
        tempo_point0 = core_parameters.TempoPoint(60, 1)
        tempo_point1 = core_parameters.TempoPoint(60, 2)
        tempo_point2 = core_parameters.TempoPoint(30, 1)
        tempo_point3 = 60
        tempo_point4 = 120

        converter = core_converters.TempoPointConverter()

        self.assertEqual(converter.convert(tempo_point0), 1)
        self.assertEqual(converter.convert(tempo_point1), 0.5)
        self.assertEqual(converter.convert(tempo_point2), 2)
        self.assertEqual(converter.convert(tempo_point3), 1)
        self.assertEqual(converter.convert(tempo_point4), 0.5)


class TempoConverterTest(unittest.TestCase):
    def test_convert_simple_event(self):
        tempo_envelope = core_events.Envelope([[0, 30], [4, 60]])
        simple_event = core_events.SimpleEvent(4)
        converter = core_converters.TempoConverter(tempo_envelope)
        converted_simple_event = converter.convert(simple_event)
        expected_duration = 6
        self.assertEqual(converted_simple_event.duration, expected_duration)

    def test_convert_sequential_event(self):
        sequential_event = core_events.SequentialEvent(
            [core_events.SimpleEvent(2) for _ in range(5)]
        )
        tempo_point_list = [
            # Event 0
            (0, 30, 0),
            (2, core_parameters.TempoPoint(30), 0),
            # Event 1
            (2, 60, 0),
            (3, core_parameters.TempoPoint(60), 0),
            (3, 30, 0),
            (4, 30, 0),  # Event 2
            (6, 60, 0),
            # Event 3
            (6, 30, 10),
            (8, 60, 0),
            # Event 4
            (8, core_parameters.TempoPoint(30, reference=1), -10),
            (10, core_parameters.TempoPoint(30, reference=2), 0),
        ]
        tempo_envelope = core_events.Envelope(tempo_point_list)
        converter = core_converters.TempoConverter(tempo_envelope)
        converted_sequential_event = converter.convert(sequential_event)
        expected_duration_tuple = (4, 3, 3, 3.800090804, 2.199909196)
        self.assertEqual(
            tuple(
                float(duration)
                for duration in converted_sequential_event.get_parameter("duration")
            ),
            expected_duration_tuple,
        )

    def test_convert_simultaneous_event(self):
        tempo_envelope = core_events.Envelope([[0, 30], [4, 60]])
        simple_event0 = core_events.SimpleEvent(4)
        simple_event1 = core_events.SimpleEvent(8)
        simultaneous_event = core_events.SimultaneousEvent(
            [simple_event0, simple_event0, simple_event1]
        )
        converter = core_converters.TempoConverter(tempo_envelope)
        converted_simultaneous_event = converter.convert(simultaneous_event)
        expected_duration0 = simultaneous_event[0].duration * 1.5
        expected_duration1 = 10
        self.assertEqual(converted_simultaneous_event[0].duration, expected_duration0)
        self.assertEqual(converted_simultaneous_event[1].duration, expected_duration0)
        self.assertEqual(converted_simultaneous_event[2].duration, expected_duration1)

    def test_convert_tempo_envelope(self):
        tempo_envelope = core_events.Envelope([[0, 30], [4, 60]])
        simple_event = core_events.SimpleEvent(4)
        simple_event.tempo_envelope = tempo_envelope.copy()
        converter = core_converters.TempoConverter(tempo_envelope)
        converted_simple_event = converter.convert(simple_event)
        self.assertEqual(converted_simple_event.tempo_envelope.duration, 6)

    def test_convert_tempo_envelope_with_too_short_global_tempo_envelope(self):
        # Tempo envelope only goes until duration "1", but
        # sequential event has duration == 2. This will throw
        # an error, because in line 196 the tempo envelope is cut out
        # to fit to the specific event and to adjust the events tempo
        # envelope. But then, if the envelope is too short, the cut-out
        # envelope won't contain any items and therefore it won't be
        # possible to call "value_at" on this envelope.
        # This has to be fixed, by adjusting an envelopes "cut_out"
        # method. The envelope first has to find the current value at
        # the given cut points, than add events which represent those
        # values at the cut points and then finally add all points in
        # between those cut points.
        tempo_envelope = core_events.Envelope([[0, 30], [0.5, 30]])
        sequential_event = core_events.SequentialEvent(
            [core_events.SimpleEvent(1), core_events.SimpleEvent(1)]
        )
        converter = core_converters.TempoConverter(tempo_envelope)
        converted_sequential_event = converter.convert(sequential_event)
        self.assertEqual(converted_sequential_event[1].tempo_envelope.duration, 1)


class EventToMetrizedEventTest(unittest.TestCase):
    def test_convert_simple_event(self):
        simple_event = core_events.SimpleEvent(
            2, tempo_envelope=core_events.TempoEnvelope([[0, 30], [2, 30]])
        )
        expected_simple_event = core_events.SimpleEvent(4)
        event_to_metrized_event = core_converters.EventToMetrizedEvent()
        self.assertEqual(
            event_to_metrized_event.convert(simple_event), expected_simple_event
        )

    def test_convert_nested_event_with_simple_hierarchy(self):
        """
        Test that tempo envelopes are propagated to all children events.
        """
        sequential_event = core_events.SequentialEvent(
            [
                core_events.SequentialEvent(
                    [
                        core_events.SimpleEvent(
                            1,
                            tempo_envelope=core_events.TempoEnvelope(
                                [[0, 30], [1, 30]]
                            ),
                        ),
                        core_events.SimpleEvent(1),
                    ],
                    tempo_envelope=core_events.TempoEnvelope([[0, 30], [1, 30]]),
                )
            ],
            tempo_envelope=core_events.TempoEnvelope([[0, 30], [1, 30]]),
        )
        expected_sequential_event = core_events.SequentialEvent(
            [
                core_events.SequentialEvent(
                    [core_events.SimpleEvent(8), core_events.SimpleEvent(4)]
                )
            ]
        )
        event_to_metrized_event = core_converters.EventToMetrizedEvent()
        self.assertEqual(
            event_to_metrized_event.convert(sequential_event), expected_sequential_event
        )

    def test_convert_nested_event_with_complex_hierarchy(self):
        """
        Ensure tempo envelopes only influence deeper nested events
        and no events on the same level.
        """

        sequential_event = core_events.SequentialEvent(
            [
                core_events.SequentialEvent(
                    [
                        core_events.SimpleEvent(
                            1,
                            tempo_envelope=core_events.TempoEnvelope(
                                [[0, 30], [1, 30]]
                            ),
                        )
                    ],
                    tempo_envelope=core_events.TempoEnvelope([[0, 30], [1, 30]]),
                ),
                core_events.SimpleEvent(1),
            ],
        )
        expected_sequential_event = core_events.SequentialEvent(
            [
                core_events.SequentialEvent([core_events.SimpleEvent(4)]),
                core_events.SimpleEvent(1),
            ]
        )
        event_to_metrized_event = core_converters.EventToMetrizedEvent()
        self.assertEqual(
            event_to_metrized_event.convert(sequential_event), expected_sequential_event
        )

    def test_convert_with_skip_level_count(self):
        """
        Ensure skip_level_count takes effect
        """
        sequential_event = core_events.SequentialEvent(
            [
                core_events.SequentialEvent(
                    [
                        core_events.SimpleEvent(
                            1,
                            tempo_envelope=core_events.TempoEnvelope(
                                [[0, 30], [1, 30]]
                            ),
                        ),
                        core_events.SimpleEvent(1),
                    ],
                    tempo_envelope=core_events.TempoEnvelope([[0, 30], [1, 30]]),
                )
            ],
            tempo_envelope=core_events.TempoEnvelope([[0, 11], [1, 11]]),
        )
        expected_sequential_event = core_events.SequentialEvent(
            [
                core_events.SequentialEvent(
                    [core_events.SimpleEvent(4), core_events.SimpleEvent(2)]
                )
            ],
            tempo_envelope=core_events.TempoEnvelope([[0, 11], [1, 11]]),
        )
        event_to_metrized_event = core_converters.EventToMetrizedEvent(
            skip_level_count=0
        )
        self.assertEqual(
            event_to_metrized_event.convert(sequential_event), expected_sequential_event
        )

    def test_convert_with_maxima_depth_count(self):
        """
        Ensure maxima_depth_count takes effect
        """
        sequential_event = core_events.SequentialEvent(
            [
                core_events.SequentialEvent(
                    [
                        core_events.SimpleEvent(
                            1,
                            tempo_envelope=core_events.TempoEnvelope([[0, 4], [1, 4]]),
                        ),
                        core_events.SimpleEvent(1),
                    ],
                    tempo_envelope=core_events.TempoEnvelope([[0, 30], [1, 30]]),
                )
            ],
            tempo_envelope=core_events.TempoEnvelope([[0, 30], [1, 30]]),
        )
        expected_sequential_event = core_events.SequentialEvent(
            [
                core_events.SequentialEvent(
                    [
                        core_events.SimpleEvent(
                            4,
                            tempo_envelope=core_events.TempoEnvelope([[0, 4], [4, 4]]),
                        ),
                        core_events.SimpleEvent(
                            4,
                            tempo_envelope=core_events.TempoEnvelope(
                                [[0, 60], [4, 60]]
                            ),
                        ),
                    ]
                )
            ]
        )
        event_to_metrized_event = core_converters.EventToMetrizedEvent(
            maxima_depth_count=2
        )
        self.assertEqual(
            event_to_metrized_event.convert(sequential_event), expected_sequential_event
        )


if __name__ == "__main__":
    unittest.main()
