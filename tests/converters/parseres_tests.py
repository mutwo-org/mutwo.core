import unittest

from mutwo import core_converters
from mutwo import core_events


class ChrononToAttributeTest(unittest.TestCase):
    def setUp(self):
        self.chronon_to_attribute = core_converters.ChrononToAttribute(
            "dummy_attribute", float("inf")
        )

    def test_convert_with_attribute(self):
        chronon = core_events.Chronon(10)
        chronon.dummy_attribute = 100  # type: ignore
        self.assertEqual(self.chronon_to_attribute.convert(chronon), 100)

    def test_convert_without_attribute(self):
        self.assertEqual(
            self.chronon_to_attribute.convert(core_events.Chronon(10)),
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


class MutwoParameterDictToChrononTest(unittest.TestCase):
    def setUp(self):
        self.mutwo_parameter_dict_to_chronon = (
            core_converters.MutwoParameterDictToChronon()
        )

    def test_convert(self):
        self.assertEqual(
            self.mutwo_parameter_dict_to_chronon.convert({"duration": 10}),
            core_events.Chronon(10),
        )


if __name__ == "__main__":
    unittest.main()
