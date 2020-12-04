import unittest

from mutwo.events import abc


class ComplexEventTest(unittest.TestCase):
    def test_abstract_error(self):
        self.assertRaises(TypeError, abc.ComplexEvent)


if __name__ == "__main__":
    unittest.main()
