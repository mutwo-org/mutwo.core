import typing
import unittest

from mutwo import core_events
from mutwo import core_parameters

from .basic_tests import EventTest


class TempoTest(unittest.TestCase, EventTest):
    def setUp(self):
        EventTest.setUp(self)

    def get_event_class(self) -> typing.Type:
        return core_events.Tempo

    def get_event_instance(self) -> core_events.Tempo:
        return self.get_event_class()(tempo_point=60, duration=5)

    def test_initialization(self):
        # Ensure tempo point conversion works
        self.assertEqual(
            core_events.Tempo(60, 1),
            core_events.Tempo(core_parameters.DirectTempoPoint(60), 1),
        )
