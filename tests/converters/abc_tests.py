import unittest

from mutwo import core_converters


class ConverterTest(unittest.TestCase):
    class DummyConverter(core_converters.abc.Converter):
        """Simple converter to test basic functionality"""

        def convert(self, number_to_convert: float) -> float:
            return number_to_convert / 2

    class UndefinedConverter(core_converters.abc.Converter):
        """Converter without specification for convert method.

        This converter should throw an error if it gets initialised.
        """

        pass

    def setUp(cls):
        cls.dummy_converter = cls.DummyConverter()

    def test_abstract_convert(self):
        self.assertRaises(TypeError, lambda: self.UndefinedConverter())

    def test_convert(self):
        self.assertEqual(self.dummy_converter.convert(10), 5)

    def test_call(self):
        self.assertEqual(self.dummy_converter(10), 5)


if __name__ == "__main__":
    unittest.main()
