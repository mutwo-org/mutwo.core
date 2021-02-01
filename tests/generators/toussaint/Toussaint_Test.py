import unittest

from mutwo.generators import toussaint


class ToussaintTest(unittest.TestCase):
    def test_euclidean(self):
        rhythms = ((2, 2), (3, 2), (3, 2, 3), (4, 3, 3))
        for rhythm in rhythms:
            self.assertEqual(toussaint.euclidean(sum(rhythm), len(rhythm)), rhythm)


if __name__ == "__main__":
    unittest.main()
