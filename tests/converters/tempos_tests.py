import unittest

from mutwo import core_converters
from mutwo import core_events
from mutwo import core_parameters


class TempoToBeatLengthInSecondsTest(unittest.TestCase):
    def setUp(self):
        self.converter = core_converters.TempoToBeatLengthInSeconds()

    def test_convert(self):
        tempo0 = core_parameters.DirectTempo(60)
        tempo1 = core_parameters.WesternTempo(60, 2)
        tempo2 = core_parameters.WesternTempo(30, 1)
        tempo3 = 60
        tempo4 = 120

        converter = core_converters.TempoToBeatLengthInSeconds()

        self.assertEqual(converter.convert(tempo0), 1)
        self.assertEqual(converter.convert(tempo1), 0.5)
        self.assertEqual(converter.convert(tempo2), 2)
        self.assertEqual(converter.convert(tempo3), 1)
        self.assertEqual(converter.convert(tempo4), 0.5)


class TempoConverterTest(unittest.TestCase):
    def test_convert_chronon(self):
        tempo_envelope = core_events.Envelope([[0, 30], [4, 60]])
        chronon = core_events.Chronon(4)
        converter = core_converters.TempoConverter(tempo_envelope)
        converted_chronon = converter.convert(chronon)
        expected_duration = 6
        self.assertEqual(converted_chronon.duration, expected_duration)

    def test_convert_consecution(self):
        consecution = core_events.Consecution(
            [core_events.Chronon(2) for _ in range(5)]
        )
        tempo_list = [
            # Event 0
            (0, 30, 0),
            (2, core_parameters.DirectTempo(30), 0),
            # Event 1
            (2, 60, 0),
            (3, core_parameters.DirectTempo(60), 0),
            (3, 30, 0),
            (4, 30, 0),  # Event 2
            (6, 60, 0),
            # Event 3
            (6, 30, 10),
            (8, 60, 0),
            # Event 4
            (8, core_parameters.WesternTempo(30, reference=1), -10),
            (10, core_parameters.WesternTempo(30, reference=2), 0),
        ]
        tempo_envelope = core_events.Envelope(tempo_list)
        converter = core_converters.TempoConverter(tempo_envelope)
        converted_consecution = converter.convert(consecution)
        expected_duration_tuple = (4.0, 3.0, 3.0, 3.800090804, 2.199909196)
        self.assertEqual(
            tuple(
                float(duration)
                for duration in converted_consecution.get_parameter("duration")
            ),
            expected_duration_tuple,
        )

    def test_convert_concurrence(self):
        tempo_envelope = core_events.Envelope([[0, 30], [4, 60]])
        chronon0 = core_events.Chronon(4)
        chronon1 = core_events.Chronon(8)
        concurrence = core_events.Concurrence([chronon0, chronon0, chronon1])
        converter = core_converters.TempoConverter(tempo_envelope)
        converted_concurrence = converter.convert(concurrence)
        expected_duration0 = concurrence[0].duration * 1.5
        expected_duration1 = 10
        self.assertEqual(converted_concurrence[0].duration, expected_duration0)
        self.assertEqual(converted_concurrence[1].duration, expected_duration0)
        self.assertEqual(converted_concurrence[2].duration, expected_duration1)

    def test_convert_tempo_envelope(self):
        tempo_envelope = core_events.Envelope([[0, 30], [4, 60]])
        chronon = core_events.Chronon(4)
        chronon.tempo_envelope = tempo_envelope.copy()
        converter = core_converters.TempoConverter(tempo_envelope)
        converted_chronon = converter.convert(chronon)
        self.assertEqual(converted_chronon.tempo_envelope.duration, 6)

    def test_convert_tempo_envelope_with_too_short_global_tempo_envelope(self):
        tempo_envelope = core_events.Envelope([[0, 30], [0.5, 30]])
        consecution = core_events.Consecution(
            [core_events.Chronon(1), core_events.Chronon(1)]
        )
        converter = core_converters.TempoConverter(tempo_envelope)
        converted_consecution = converter.convert(consecution)
        # This has to be 2 instead of 1 because of tempo 30 BPM
        # (which is half of normal tempo 60, so duration should be
        # doubled).
        self.assertEqual(converted_consecution[1].tempo_envelope.duration, 2)


class EventToMetrizedEventTest(unittest.TestCase):
    def test_convert_chronon(self):
        chronon = core_events.Chronon(
            2, tempo_envelope=core_events.TempoEnvelope([[0, 30], [2, 30]])
        )
        expected_chronon = core_events.Chronon(4)
        event_to_metrized_event = core_converters.EventToMetrizedEvent()
        self.assertEqual(event_to_metrized_event.convert(chronon), expected_chronon)

    def test_convert_nested_event_with_simple_hierarchy(self):
        """
        Test that tempo envelopes are propagated to all children events.
        """
        consecution = core_events.Consecution(
            [
                core_events.Consecution(
                    [
                        core_events.Chronon(
                            1,
                            tempo_envelope=core_events.TempoEnvelope(
                                [[0, 30], [1, 30]]
                            ),
                        ),
                        core_events.Chronon(1),
                    ],
                    tempo_envelope=core_events.TempoEnvelope([[0, 30], [1, 30]]),
                )
            ],
            tempo_envelope=core_events.TempoEnvelope([[0, 30], [1, 30]]),
        )
        expected_consecution = core_events.Consecution(
            [core_events.Consecution([core_events.Chronon(8), core_events.Chronon(4)])]
        )
        event_to_metrized_event = core_converters.EventToMetrizedEvent()
        self.assertEqual(
            event_to_metrized_event.convert(consecution), expected_consecution
        )

    def test_convert_nested_event_with_complex_hierarchy(self):
        """
        Ensure tempo envelopes only influence deeper nested events
        and no events on the same level.
        """

        consecution = core_events.Consecution(
            [
                core_events.Consecution(
                    [
                        core_events.Chronon(
                            1,
                            tempo_envelope=core_events.TempoEnvelope(
                                [[0, 30], [1, 30]]
                            ),
                        )
                    ],
                    tempo_envelope=core_events.TempoEnvelope([[0, 30], [1, 30]]),
                ),
                core_events.Chronon(1),
            ],
        )
        expected_consecution = core_events.Consecution(
            [
                core_events.Consecution([core_events.Chronon(4)]),
                core_events.Chronon(1),
            ]
        )
        event_to_metrized_event = core_converters.EventToMetrizedEvent()
        self.assertEqual(
            event_to_metrized_event.convert(consecution), expected_consecution
        )

    def test_convert_with_skip_level_count(self):
        """
        Ensure skip_level_count takes effect
        """
        consecution = core_events.Consecution(
            [
                core_events.Consecution(
                    [
                        core_events.Chronon(
                            1,
                            tempo_envelope=core_events.TempoEnvelope(
                                [[0, 30], [1, 30]]
                            ),
                        ),
                        core_events.Chronon(1),
                    ],
                    tempo_envelope=core_events.TempoEnvelope([[0, 30], [1, 30]]),
                )
            ],
            tempo_envelope=core_events.TempoEnvelope([[0, 11], [1, 11]]),
        )
        expected_consecution = core_events.Consecution(
            [core_events.Consecution([core_events.Chronon(4), core_events.Chronon(2)])],
            tempo_envelope=core_events.TempoEnvelope([[0, 11], [1, 11]]),
        )
        event_to_metrized_event = core_converters.EventToMetrizedEvent(
            skip_level_count=0
        )
        self.assertEqual(
            event_to_metrized_event.convert(consecution), expected_consecution
        )

    def test_convert_with_maxima_depth_count(self):
        """
        Ensure maxima_depth_count takes effect
        """
        consecution = core_events.Consecution(
            [
                core_events.Consecution(
                    [
                        core_events.Chronon(
                            1,
                            tempo_envelope=core_events.TempoEnvelope([[0, 4], [1, 4]]),
                        ),
                        core_events.Chronon(1),
                    ],
                    tempo_envelope=core_events.TempoEnvelope([[0, 30], [1, 30]]),
                )
            ],
            tempo_envelope=core_events.TempoEnvelope([[0, 30], [1, 30]]),
        )
        expected_consecution = core_events.Consecution(
            [
                core_events.Consecution(
                    [
                        core_events.Chronon(
                            4,
                            tempo_envelope=core_events.TempoEnvelope([[0, 4], [4, 4]]),
                        ),
                        core_events.Chronon(
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
            event_to_metrized_event.convert(consecution), expected_consecution
        )


if __name__ == "__main__":
    unittest.main()
