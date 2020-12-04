import unittest

from mutwo import events


class EventTest(unittest.TestCase):
    def test_abstract_error(self):
        self.assertRaises(TypeError, events.Event)

    def test_duration_error(self):
        self.assertRaises(TypeError, events.Event.duration)


class SimpleEventTest(unittest.TestCase):
    pass


class ComplexEventTest(unittest.TestCase):
    def test_abstract_error(self):
        self.assertRaises(TypeError, events.ComplexEvent)


class SequentialEventTest(unittest.TestCase):
    pass


class SimultaneousEventTest(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()