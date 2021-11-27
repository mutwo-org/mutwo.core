import unittest

try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

import numpy as np

from mutwo.generators import brun


class BrunTest(unittest.TestCase):
    def test_make_bruns_euclidean_algorithm_generator(self):
        expected_element_tuple_per_call = (
            # initial element tuple
            (
                fractions.Fraction(2, 1),
                fractions.Fraction(3, 2),
                fractions.Fraction(5, 4),
            ),
            # first processed element tuple
            (
                fractions.Fraction(3, 2),
                fractions.Fraction(5, 4),
                fractions.Fraction(1, 2),
            ),
        )
        expected_matrix_per_call = (
            np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
            np.array([[1, 1, 0], [0, 0, 1], [1, 0, 0]]),
        )
        expected_previous_subtraction_result_per_call = (
            fractions.Fraction(2, 1),
            fractions.Fraction(1, 2),
        )
        bruns_euclidean_algorithm_generator = (
            brun.make_bruns_euclidean_algorithm_generator(
                expected_element_tuple_per_call[0]
            )
        )
        for (
            expected_element_tuple,
            expected_matrix,
            expected_previous_subtraction_result,
        ) in zip(
            expected_element_tuple_per_call,
            expected_matrix_per_call,
            expected_previous_subtraction_result_per_call,
        ):
            element_tuple, matrix, previous_subtraction_result = next(
                bruns_euclidean_algorithm_generator
            )
            self.assertEqual(element_tuple, expected_element_tuple)
            self.assertEqual(
                previous_subtraction_result, expected_previous_subtraction_result
            )
            self.assertTrue((expected_matrix == matrix).all())


if __name__ == "__main__":
    unittest.main()
