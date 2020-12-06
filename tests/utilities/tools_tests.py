import unittest

from mutwo.utilities import tools


class ToolsTest(unittest.TestCase):
    def test_scale_out_of_range(self):
        self.assertRaises(AssertionError, tools.scale, 2, 0, 1, 1, 2)

    def test_scale_easy(self):
        result = tools.scale(0.5, 0, 1, 1, 2)
        self.assertEqual(result, 1.5)

    def test_scale_negative(self):
        result = tools.scale(0, -1, 1, 1, 2)
        self.assertEqual(result, 1.5)

    def test_accumulate_from_value(self):
        result = tuple(tools.accumulate_from_n((1, 2, 3), 6))
        self.assertEqual(result, (6, 7, 9, 12))

    def test_accumulate_from_zero(self):
        result = tuple(tools.accumulate_from_zero((1, 2, 3)))
        self.assertEqual(result, (0, 1, 3, 6))


if __name__ == "__main__":
    unittest.main()
