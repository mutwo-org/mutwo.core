import unittest

from mutwo.converters.frontends import reaper


class TempoConverterTest(unittest.TestCase):
    def setUp(self):
        self.converter = reaper.ReaperFileConverter()


if __name__ == "__main__":
    unittest.main()
