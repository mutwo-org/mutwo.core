import unittest

from mutwo.generators import wilson
from mutwo.parameters import pitches


class CommonProductSetScaleTest(unittest.TestCase):
    def test_make_common_product_set_scale_with_one_number(self):
        self.assertEqual(
            wilson.make_common_product_set_scale((3, 5, 7, 11), 1, True),
            tuple(
                pitches.JustIntonationPitch(ratio)
                for ratio in "3/1 5/1 7/1 11/1".split(" ")
            ),
        )

    def test_make_common_product_set_scale_with_two_numbers(self):
        self.assertEqual(
            wilson.make_common_product_set_scale((3, 5, 7), 2, True),
            tuple(
                pitches.JustIntonationPitch(ratio)
                for ratio in "15/1 21/1 35/1".split(" ")
            ),
        )

    def test_make_common_product_set_scale_with_utonality(self):
        self.assertEqual(
            wilson.make_common_product_set_scale((3, 5, 7), 2, False),
            tuple(
                pitches.JustIntonationPitch(ratio)
                for ratio in "1/15 1/21 1/35".split(" ")
            ),
        )

    def test_make_wilsons_brun_euclidean_algorithm_generator(self):
        pitch_tuple = (
            pitches.JustIntonationPitch("2/1"),
            pitches.JustIntonationPitch("3/2"),
            pitches.JustIntonationPitch("5/4"),
        )
        expected_interval_tuple_per_call_per_subtraction_index = (
            (
                (pitches.JustIntonationPitch("2/1"),),
                (
                    pitches.JustIntonationPitch("3/2"),
                    pitches.JustIntonationPitch("4/3"),
                ),
                (
                    pitches.JustIntonationPitch("4/3"),
                    pitches.JustIntonationPitch("9/8"),
                    pitches.JustIntonationPitch("4/3"),
                ),
                (
                    pitches.JustIntonationPitch("5/4"),
                    pitches.JustIntonationPitch("16/15"),
                    pitches.JustIntonationPitch("9/8"),
                    pitches.JustIntonationPitch("5/4"),
                    pitches.JustIntonationPitch("16/15"),
                ),
            ),
            (
                (pitches.JustIntonationPitch("2/1"),),
                (
                    pitches.JustIntonationPitch("5/4"),
                    pitches.JustIntonationPitch("8/5"),
                ),
                (
                    pitches.JustIntonationPitch("5/4"),
                    pitches.JustIntonationPitch("5/4"),
                    pitches.JustIntonationPitch("32/25"),
                ),
                (
                    pitches.JustIntonationPitch("5/4"),
                    pitches.JustIntonationPitch("5/4"),
                    pitches.JustIntonationPitch("6/5"),
                    pitches.JustIntonationPitch("16/15"),
                ),
            ),
        )
        for subtraction_index, expected_interval_tuple_per_call in zip(
            (1, 2), expected_interval_tuple_per_call_per_subtraction_index
        ):
            wilsons_brun_euclidean_algorithm_generator = (
                wilson.make_wilsons_brun_euclidean_algorithm_generator(
                    pitch_tuple, subtraction_index
                )
            )
            for expected_interval_tuple in expected_interval_tuple_per_call:
                interval_tuple_tuple = next(wilsons_brun_euclidean_algorithm_generator)
                self.assertEqual((expected_interval_tuple,), interval_tuple_tuple)


if __name__ == "__main__":
    unittest.main()
