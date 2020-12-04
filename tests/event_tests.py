import unittest

from mutwo.events import abc


class EventTest(unittest.TestCase):
    def test_abstract_error(self):
        self.assertRaises(TypeError, abc.Event)

    def test_duration_error(self):
        self.assertRaises(TypeError, abc.Event.duration)


class SimpleEventTest(unittest.TestCase):
    pass


class ComplexEventTest(unittest.TestCase):
    def test_abstract_error(self):
        self.assertRaises(TypeError, abc.ComplexEvent)


class SequentialEventTest(unittest.TestCase):
    pass


class SimultaneousEventTest(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
