import unittest

from mutwo.events import abc


class EventTest(unittest.TestCase):
    def test_abstract_error(self):
        self.assertRaises(TypeError, abc.Event)

    def test_duration_error(self):
        self.assertRaises(TypeError, abc.Event.duration)
