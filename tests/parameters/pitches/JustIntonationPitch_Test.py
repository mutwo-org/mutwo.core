import unittest

try:
    import quicktions as fractions
except ImportError:
    import fractions

from mutwo.parameters import pitches


class JustIntonationPitchTest(unittest.TestCase):
    def test_constructor_from_string(self):
        self.assertEqual(
            pitches.JustIntonationPitch("3/2").ratio, fractions.Fraction(3, 2)
        )
        self.assertEqual(
            pitches.JustIntonationPitch("5/1").ratio, fractions.Fraction(5, 1)
        )
        self.assertEqual(
            pitches.JustIntonationPitch("1/17").ratio, fractions.Fraction(1, 17)
        )

    def test_constructor_from_ratio(self):
        ratio0 = fractions.Fraction(3, 2)
        ratio1 = fractions.Fraction(5, 1)
        ratio2 = fractions.Fraction(1, 17)
        self.assertEqual(pitches.JustIntonationPitch(ratio0).ratio, ratio0)
        self.assertEqual(pitches.JustIntonationPitch(ratio1).ratio, ratio1)
        self.assertEqual(pitches.JustIntonationPitch(ratio2).ratio, ratio2)

    def test_constructor_from_vector(self):
        ratio0 = fractions.Fraction(3, 2)
        ratio1 = fractions.Fraction(5, 1)
        ratio2 = fractions.Fraction(1, 17)
        self.assertEqual(pitches.JustIntonationPitch((-1, 1)).ratio, ratio0)
        self.assertEqual(pitches.JustIntonationPitch((0, 0, 1)).ratio, ratio1)
        self.assertEqual(
            pitches.JustIntonationPitch([0, 0, 0, 0, 0, 0, -1]).ratio, ratio2
        )

    def test_constructor_with_different_concert_pitch(self):
        concert_pitch0 = pitches.DirectPitch(300)
        concert_pitch1 = pitches.DirectPitch(200)
        self.assertEqual(
            pitches.JustIntonationPitch(concert_pitch=concert_pitch0).concert_pitch,
            concert_pitch0,
        )
        self.assertEqual(
            pitches.JustIntonationPitch(
                concert_pitch=concert_pitch1.frequency
            ).concert_pitch,
            concert_pitch1,
        )

    def test_property_exponents(self):
        ratio0 = fractions.Fraction(3, 2)
        ratio1 = fractions.Fraction(25, 1)
        ratio2 = fractions.Fraction(11, 9)
        self.assertEqual(pitches.JustIntonationPitch(ratio0).exponents, (-1, 1))
        self.assertEqual(pitches.JustIntonationPitch(ratio1).exponents, (0, 0, 2))
        self.assertEqual(
            pitches.JustIntonationPitch(ratio2).exponents, (0, -2, 0, 0, 1)
        )

    def test_property_primes(self):
        ratio0 = fractions.Fraction(3, 2)
        ratio1 = fractions.Fraction(25, 1)
        ratio2 = fractions.Fraction(11, 9)
        self.assertEqual(pitches.JustIntonationPitch(ratio0).primes, (2, 3))
        self.assertEqual(pitches.JustIntonationPitch(ratio1).primes, (2, 3, 5))
        self.assertEqual(pitches.JustIntonationPitch(ratio2).primes, (2, 3, 5, 7, 11))

    def test_property_occupied_primes(self):
        ratio0 = fractions.Fraction(3, 2)
        ratio1 = fractions.Fraction(25, 1)
        ratio2 = fractions.Fraction(11, 9)
        self.assertEqual(pitches.JustIntonationPitch(ratio0).occupied_primes, (2, 3))
        self.assertEqual(pitches.JustIntonationPitch(ratio1).occupied_primes, (5,))
        self.assertEqual(pitches.JustIntonationPitch(ratio2).occupied_primes, (3, 11))

    def test_property_frequency(self):
        ratio0 = fractions.Fraction(3, 2)
        concert_pitch0 = 200
        ratio1 = fractions.Fraction(25, 1)
        concert_pitch1 = 300
        ratio2 = fractions.Fraction(11, 9)
        concert_pitch2 = 10
        self.assertAlmostEqual(
            pitches.JustIntonationPitch(ratio0, concert_pitch0).frequency,
            ratio0 * concert_pitch0,
        )
        self.assertAlmostEqual(
            pitches.JustIntonationPitch(ratio1, concert_pitch1).frequency,
            ratio1 * concert_pitch1,
        )
        self.assertAlmostEqual(
            pitches.JustIntonationPitch(ratio2, concert_pitch2).frequency,
            ratio2 * concert_pitch2,
        )

    def test_harmonic(self):
        jip0 = pitches.JustIntonationPitch([-1, 1])
        jip1 = pitches.JustIntonationPitch([-2, 0, 1])
        jip2 = pitches.JustIntonationPitch([0, 0, 0, -1, 1])
        jip3 = pitches.JustIntonationPitch([2, -1])
        jip4 = pitches.JustIntonationPitch([4, 0, 0, -1])
        jip5 = pitches.JustIntonationPitch([])
        self.assertEqual(jip0.harmonic, 3)
        self.assertEqual(jip1.harmonic, 5)
        self.assertEqual(jip2.harmonic, 0)
        self.assertEqual(jip3.harmonic, -3)
        self.assertEqual(jip4.harmonic, -7)
        self.assertEqual(jip5.harmonic, 1)

    def test_tonality(self):
        jip0 = pitches.JustIntonationPitch([0, 1])
        jip1 = pitches.JustIntonationPitch([0, -1])
        jip2 = pitches.JustIntonationPitch([0, 1, -1])
        jip3 = pitches.JustIntonationPitch([0, -2, 0, 0, 1])
        jip4 = pitches.JustIntonationPitch([0, 0])
        self.assertEqual(jip0.tonality, True)
        self.assertEqual(jip1.tonality, False)
        self.assertEqual(jip2.tonality, False)
        self.assertEqual(jip3.tonality, True)
        self.assertEqual(jip4.tonality, True)

    def test_normalize(self):
        p0 = pitches.JustIntonationPitch((0, 1))
        p1 = pitches.JustIntonationPitch((-1, 1))
        self.assertEqual(p0.normalize(2), p1)

    def test__indigestibility(self):
        self.assertEqual(pitches.JustIntonationPitch._indigestibility(1), 0)
        self.assertEqual(pitches.JustIntonationPitch._indigestibility(2), 1)
        self.assertEqual(pitches.JustIntonationPitch._indigestibility(4), 2)
        self.assertEqual(pitches.JustIntonationPitch._indigestibility(5), 6.4)
        self.assertEqual(
            pitches.JustIntonationPitch._indigestibility(6), 3.6666666666666665
        )
        self.assertEqual(pitches.JustIntonationPitch._indigestibility(8), 3)

    def test_harmonicity_barlow(self):
        jip0 = pitches.JustIntonationPitch((-1, 1,))
        jip1 = pitches.JustIntonationPitch([])
        jip2 = pitches.JustIntonationPitch((-2, 0, 1))
        jip3 = pitches.JustIntonationPitch((3, 0, -1))
        self.assertEqual(jip0.harmonicity_barlow, 0.27272727272727276)
        self.assertEqual(jip1.harmonicity_barlow, float("inf"))
        self.assertEqual(jip2.harmonicity_barlow, 0.11904761904761904)
        self.assertEqual(jip3.harmonicity_barlow, -0.10638297872340426)

    def test_harmonicity_euler(self):
        jip0 = pitches.JustIntonationPitch((-1, 1,))
        jip1 = pitches.JustIntonationPitch([])
        jip2 = pitches.JustIntonationPitch((-2, 0, 1))
        jip3 = pitches.JustIntonationPitch((3, 0, -1))
        self.assertEqual(jip0.harmonicity_euler, 4)
        self.assertEqual(jip1.harmonicity_euler, 1)
        self.assertEqual(jip2.harmonicity_euler, 7)
        self.assertEqual(jip3.harmonicity_euler, 8)

    def test_harmonicity_tenney(self):
        jip0 = pitches.JustIntonationPitch((-1, 1,))
        jip1 = pitches.JustIntonationPitch([])
        jip2 = pitches.JustIntonationPitch((-2, 0, 1))
        jip3 = pitches.JustIntonationPitch((3, 0, -1))
        self.assertEqual(jip0.harmonicity_tenney, 2.584962500721156)
        self.assertEqual(jip1.harmonicity_tenney, 0)
        self.assertEqual(jip2.harmonicity_tenney, 4.321928094887363)
        self.assertEqual(jip3.harmonicity_tenney, 5.321928094887363)

    def test_harmonicity_vogel(self):
        jip0 = pitches.JustIntonationPitch((-1, 1,))
        jip1 = pitches.JustIntonationPitch([])
        jip2 = pitches.JustIntonationPitch((-2, 0, 1))
        jip3 = pitches.JustIntonationPitch((3, 0, -1))
        self.assertEqual(jip0.harmonicity_vogel, 4)
        self.assertEqual(jip1.harmonicity_vogel, 1)
        self.assertEqual(jip2.harmonicity_vogel, 7)
        self.assertEqual(jip3.harmonicity_vogel, 8)

    def test_harmonicity_wilson(self):
        jip0 = pitches.JustIntonationPitch((-1, 1,))
        jip1 = pitches.JustIntonationPitch([])
        jip2 = pitches.JustIntonationPitch((-2, 0, 1))
        jip3 = pitches.JustIntonationPitch((3, 0, -1))
        self.assertEqual(jip0.harmonicity_wilson, 3)
        self.assertEqual(jip1.harmonicity_wilson, 1)
        self.assertEqual(jip2.harmonicity_wilson, 5)
        self.assertEqual(jip3.harmonicity_wilson, 5)


if __name__ == "__main__":
    unittest.main()
