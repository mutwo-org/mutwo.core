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


if __name__ == "__main__":
    unittest.main()
