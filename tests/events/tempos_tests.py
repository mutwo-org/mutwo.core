import typing
import unittest

from mutwo import core_events
from mutwo import core_parameters

from .basic_tests import EventTest


class TempoEventTest(unittest.TestCase, EventTest):
    def setUp(self):
        EventTest.setUp(self)

    def get_event_class(self) -> typing.Type:
        return core_events.TempoEvent

    def get_event_instance(self) -> core_events.TempoEvent:
        return self.get_event_class()(tempo_point=60, duration=5)

    def test_initialization(self):
        # Ensure tempo point conversion works
        self.assertEqual(
            core_events.TempoEvent(60, 1),
            core_events.TempoEvent(core_parameters.DirectTempoPoint(60), 1),
        )
