import unittest

from mutwo.core.events import abc


class EventTest(unittest.TestCase):
    def test_abstract_error(self):
        self.assertRaises(TypeError, abc.Event)

    def test_duration_error(self):
        self.assertRaises(TypeError, abc.Event.duration)


class ComplexEventTest(unittest.TestCase):
    def test_abstract_error(self):
        self.assertRaises(TypeError, abc.ComplexEvent)


if __name__ == "__main__":
    unittest.main()
