import unittest

from mutwo import core_converters
from mutwo import core_events


class SimpleEventToAttributeTest(unittest.TestCase):
    def setUp(cls):
        cls.simple_event_to_attribute = core_converters.SimpleEventToAttribute(
            "dummy_attribute", float("inf")
        )

    def test_convert_with_attribute(self):
        simple_event = core_events.SimpleEvent(10)
        simple_event.dummy_attribute = 100  # type: ignore
        self.assertEqual(self.simple_event_to_attribute.convert(simple_event), 100)

    def test_convert_without_attribute(self):
        self.assertEqual(
            self.simple_event_to_attribute.convert(core_events.SimpleEvent(10)),
            float("inf"),
        )


if __name__ == "__main__":
    unittest.main()
