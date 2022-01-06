import unittest

from mutwo.parameters import pitches
from mutwo.parameters import pitches_constants


class ConstantsTest(unittest.TestCase):
    def test_default_prime_to_comma(self):
        # Make sure all default commas are notated in a way so that the relevant
        # prime number (which is neither 2 nor 3) has a positive exponent.
        for comma in pitches_constants.DEFAULT_PRIME_TO_COMMA_DICT.values():
            self.assertEqual(
                sum(pitches.JustIntonationPitch(comma.ratio).exponent_tuple[2:]), 1
            )


if __name__ == "__main__":
    unittest.main()
