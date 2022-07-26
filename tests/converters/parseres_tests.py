import unittest

from mutwo import core_converters
from mutwo import core_events


class UnknownObjectToObjectTest(unittest.TestCase):
    def setUp(self):
        self.unknown_object_to_string = core_converters.UnknownObjectToObject[str](
            (
                ((float, int, list), str),
                ((tuple,), lambda t: str(len(t))),
                ([], lambda _: "..."),
            )
        )

        self.unknown_object_to_integer = core_converters.UnknownObjectToObject[int](
            (((float, int), int),)
        )

    def test_convert_defined(self):
        self.assertEqual(self.unknown_object_to_string(100), "100")
        self.assertEqual(self.unknown_object_to_string([1, 2, 3]), "[1, 2, 3]")
        self.assertEqual(self.unknown_object_to_string((1, 2)), "2")
        self.assertEqual(self.unknown_object_to_string(b""), "...")

    def test_convert_implicit_defined(self):
        self.assertEqual(self.unknown_object_to_string("abc"), "abc")
        self.assertEqual(self.unknown_object_to_integer(7), 7)

    def test_convert_undefined(self):
        self.assertRaises(
            NotImplementedError, self.unknown_object_to_integer, ([1, 2, 3],)
        )


class SimpleEventToAttributeTest(unittest.TestCase):
    def setUp(self):
        self.simple_event_to_attribute = core_converters.SimpleEventToAttribute(
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


class MutwoParameterDictToKeywordArgumentTest(unittest.TestCase):
    def setUp(self):
        self.mutwo_parameter_dict_to_duration = (
            core_converters.MutwoParameterDictToKeywordArgument("duration")
        )
        self.mutwo_parameter_dict_to_noodles = (
            core_converters.MutwoParameterDictToKeywordArgument("pasta", "noodles")
        )

    def test_convert_with_content(self):
        self.assertEqual(
            self.mutwo_parameter_dict_to_duration.convert({"duration": 10}),
            ("duration", 10),
        )
        self.assertEqual(
            self.mutwo_parameter_dict_to_noodles.convert({"pasta": "mie"}),
            ("noodles", "mie"),
        )

    def test_convert_without_content(self):
        self.assertEqual(
            self.mutwo_parameter_dict_to_noodles.convert({"bread": "ciabatta"}), None
        )


class MutwoParameterDictToDurationTest(unittest.TestCase):
    def setUp(self):
        self._default_default_duration_keyword_name = str(
            core_converters.configurations.DEFAULT_DURATION_KEYWORD_NAME
        )
        # Set to esperanto mode
        core_converters.configurations.DEFAULT_DURATION_KEYWORD_NAME = "daŭro"
        self.mutwo_parameter_dict_to_duration = (
            core_converters.MutwoParameterDictToDuration()
        )

    def tearDown(self):
        # Reset to original value
        core_converters.configurations.DEFAULT_DURATION_KEYWORD_NAME = (
            self._default_default_duration_keyword_name
        )

    def test_convert_with_content(self):
        self.assertEqual(
            self.mutwo_parameter_dict_to_duration.convert({"duration": 10}),
            ("daŭro", 10),
        )

    def test_convert_without_content(self):
        self.assertEqual(
            self.mutwo_parameter_dict_to_duration.convert({"daŭro": 10}), None
        )


class MutwoParameterDictToSimpleEventTest(unittest.TestCase):
    def setUp(self):
        self.mutwo_parameter_dict_to_simple_event = (
            core_converters.MutwoParameterDictToSimpleEvent()
        )

    def test_convert(self):
        self.assertEqual(
            self.mutwo_parameter_dict_to_simple_event.convert({"duration": 10}),
            core_events.SimpleEvent(10),
        )


if __name__ == "__main__":
    unittest.main()
