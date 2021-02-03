import unittest

from mutwo.generators import brown


class BrownTest(unittest.TestCase):
    def test_random_walk_noise(self):
        expected_result = (
            0.40608634,
            0.25314724,
            0.1211043,
            -0.14713786,
            0.06921405,
            -0.50617062,
            -0.06996768,
            -0.26026941,
            -0.18050963,
            -0.24285223,
        )
        for state0, state1 in zip(
            expected_result, brown.random_walk_noise(0, 10, 10 / 10, 0.25, None, 1)
        ):
            self.assertAlmostEqual(state0, state1)


if __name__ == "__main__":
    unittest.main()
