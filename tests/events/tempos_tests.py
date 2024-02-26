import typing
import unittest

from mutwo import core_events
from mutwo import core_parameters

from .basic_tests import EventTest


class TempoChrononTest(unittest.TestCase, EventTest):
    def setUp(self):
        EventTest.setUp(self)

    def get_event_class(self) -> typing.Type:
        return core_events.TempoChronon

    def get_event_instance(self) -> core_events.TempoChronon:
        return self.get_event_class()(tempo=60, duration=5)

    def test_initialization(self):
        # Ensure tempo conversion works
        self.assertEqual(
            core_events.TempoChronon(60, 1),
            core_events.TempoChronon(core_parameters.DirectTempo(60), 1),
        )
