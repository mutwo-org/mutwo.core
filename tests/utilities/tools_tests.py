import unittest

from mutwo.utilities import tools


class ToolsTest(unittest.TestCase):
    def test_value_out_of_range(self):
        self.assertRaises(AssertionError, tools.scale, 2, 0, 1, 1, 2)

    def test_value(self):
        self.assertEqual(tools.scale(0.5, 0, 1, 1, 2), 1.5)


if __name__ == "__main__":
    unittest.main()
