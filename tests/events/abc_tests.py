import unittest

from mutwo import core_events


class EventTest(unittest.TestCase):
    def test_abstract_error(self):
        self.assertRaises(TypeError, core_events.abc.Event)

    def test_duration_error(self):
        self.assertRaises(TypeError, core_events.abc.Event.duration)


class ComplexEventTest(unittest.TestCase):
    @unittest.skip(
        "ComplexEvent is broke (can be initialised); this need "
        "to be fixed, but it's not clear how."
    )
    def test_abstract_error(self):
        self.assertRaises(TypeError, core_events.abc.ComplexEvent)


if __name__ == "__main__":
    unittest.main()
