import unittest

from mutwo.generators import edwards


class EdwardsTest(unittest.TestCase):
    def test_activity_level(self):
        activity_level0 = edwards.ActivityLevel()
        activity_level1 = edwards.ActivityLevel(start_at=1)

        for activity_level, start_at in (
            (activity_level0, 0),
            (activity_level1, 1),
        ):
            for level in range(9):
                level += 1
                states = edwards.constants.ACTIVITY_LEVELS[level][start_at]
                for nth_iteration in range(10):
                    self.assertEqual(bool(states[nth_iteration]), activity_level(level))

        # test invalid values for start_at
        self.assertRaises(ValueError, lambda: edwards.ActivityLevel(start_at=3))
        self.assertRaises(ValueError, lambda: edwards.ActivityLevel(start_at=-1))


if __name__ == "__main__":
    unittest.main()
