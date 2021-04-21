import unittest


try:
    import quicktions as fractions  # type: ignore
except ImportError:
    import fractions  # type: ignore

from mutwo.parameters import pitches
from mutwo.parameters import pitches_constants


class DirectPitch_Test(unittest.TestCase):
    def test_property_frequency(self):
        frequency0 = 200
        frequency1 = 502.42
        frequency2 = 10
        self.assertEqual(frequency0, pitches.DirectPitch(frequency0).frequency)
        self.assertEqual(frequency1, pitches.DirectPitch(frequency1).frequency)
        self.assertEqual(frequency2, pitches.DirectPitch(frequency2).frequency)


class EqualDividedOctavePitch_Test(unittest.TestCase):
    def test_false_pitch_class(self):
        self.assertRaises(
            ValueError, lambda: pitches.EqualDividedOctavePitch(12, -2, 0, 0, 0)
        )
        self.assertRaises(
            ValueError, lambda: pitches.EqualDividedOctavePitch(12, 13, 0, 0, 0)
        )

    def test_property_frequency(self):
        pitch0 = pitches.EqualDividedOctavePitch(12, 0, 1, 0, 0)
        pitch1 = pitches.EqualDividedOctavePitch(6, 0, -1, 0, 0)
        pitch2 = pitches.EqualDividedOctavePitch(12, 6, 0, 0, 0)
        self.assertAlmostEqual(pitch0.frequency, pitch0.concert_pitch.frequency * 2)
        self.assertAlmostEqual(pitch1.frequency, pitch1.concert_pitch.frequency * 0.5)
        self.assertAlmostEqual(pitch2.frequency, 622.253967444162)

    def test_property_step_factor(self):
        pitch0 = pitches.EqualDividedOctavePitch(12, 0, 1, 0, 0)
        pitch1 = pitches.EqualDividedOctavePitch(6, 0, -1, 0, 0)
        self.assertAlmostEqual(
            (pitch0.step_factor ** pitch0.n_pitch_classes_per_octave)
            * pitch0.concert_pitch.frequency,
            pitch0.frequency,
        )
        self.assertAlmostEqual(
            pitch1.concert_pitch.frequency
            / (pitch1.step_factor ** pitch1.n_pitch_classes_per_octave),
            pitch1.frequency,
        )

    def test_magic_method_sub(self):
        pitch0 = pitches.EqualDividedOctavePitch(12, 7, 0, 0, 0)
        pitch1 = pitches.EqualDividedOctavePitch(12, 1, 0, 0, 0)
        pitch2 = pitches.EqualDividedOctavePitch(12, 0, 1, 0, 0)
        pitch3 = pitches.EqualDividedOctavePitch(24, 1, 0, 0, 0)
        self.assertEqual(pitch0 - pitch1, 6)
        self.assertEqual(pitch2 - pitch0, 5)
        self.assertEqual(pitch2 - pitch1, 11)
        self.assertRaises(ValueError, lambda: pitch3 - pitch1)

    def test_add(self):
        pitch0 = pitches.EqualDividedOctavePitch(12, 7, 0, 0, 0)
        pitch1 = pitches.EqualDividedOctavePitch(12, 1, 0, 0, 0)
        pitch2 = pitches.EqualDividedOctavePitch(12, 0, 1, 0, 0)
        pitch3 = pitches.EqualDividedOctavePitch(12, 11, -1, 0, 0)
        pitch4 = pitches.EqualDividedOctavePitch(12, 0, 0, 0, 0)
        pitch4.add(-1)
        self.assertEqual(pitch0.add(-6, mutate=False), pitch1)
        self.assertEqual(pitch0.add(5, mutate=False), pitch2)
        self.assertEqual(pitch0.add(-8, mutate=False), pitch3)
        self.assertEqual(pitch4, pitch3)

    def test_subtract(self):
        pitch0 = pitches.EqualDividedOctavePitch(12, 7, 0, 0, 0)
        pitch1 = pitches.EqualDividedOctavePitch(12, 1, 0, 0, 0)
        pitch2 = pitches.EqualDividedOctavePitch(12, 0, 1, 0, 0)
        pitch3 = pitches.EqualDividedOctavePitch(12, 11, -1, 0, 0)
        pitch4 = pitches.EqualDividedOctavePitch(12, 0, 0, 0, 0)
        pitch4.subtract(1)
        self.assertEqual(pitch0.subtract(6, mutate=False), pitch1)
        self.assertEqual(pitch0.subtract(-5, mutate=False), pitch2)
        self.assertEqual(pitch0.subtract(8, mutate=False), pitch3)
        self.assertEqual(pitch4, pitch3)


class WesternPitchTest(unittest.TestCase):
    def test_constructor_from_string(self):
        pitch0 = pitches.WesternPitch("cf", 4)
        pitch1 = pitches.WesternPitch("dqs", 3)
        pitch2 = pitches.WesternPitch("gss")
        pitch3 = pitches.WesternPitch("ges", 0)
        pitch4 = pitches.WesternPitch("bss", 10)
        self.assertEqual(pitch0.name, "cf4")
        self.assertEqual(pitch1.name, "dqs3")
        self.assertEqual(pitch2.name, "gss4")
        self.assertEqual(pitch3.name, "ges0")
        self.assertEqual(pitch4.name, "bss10")
        self.assertEqual(pitch0.pitch_class, -1)
        self.assertEqual(pitch1.pitch_class, 2.5)
        self.assertEqual(pitch2.pitch_class, 9)
        self.assertEqual(pitch3.pitch_class, 7.25)
        self.assertEqual(pitch4.pitch_class, 13)

    def test_constructor_from_float(self):
        pitch0 = pitches.WesternPitch(0)
        pitch1 = pitches.WesternPitch(1)
        pitch2 = pitches.WesternPitch(2.25)
        pitch3 = pitches.WesternPitch(-0.5)
        pitch4 = pitches.WesternPitch(7.166, 5)
        self.assertEqual(pitch0.name, "c4")
        self.assertEqual(pitch1.name, "df4")
        self.assertEqual(pitch2.name, "des4")
        self.assertEqual(pitch3.name, "cqf4")
        self.assertEqual(pitch4.name, "gts5")

    def test_representation(self):
        pitch0 = pitches.WesternPitch("cs", 2)
        self.assertEqual(repr(pitch0), "WesternPitch(cs2)")

    def test_property_frequency(self):
        pitch0 = pitches.WesternPitch("a", 4)
        pitch1 = pitches.WesternPitch("a", 3)
        pitch2 = pitches.WesternPitch("a", 5)
        pitch3 = pitches.WesternPitch("as", 4)
        pitch4 = pitches.WesternPitch("bqs", 4)
        self.assertAlmostEqual(
            pitch0.frequency, pitches_constants.DEFAULT_CONCERT_PITCH
        )
        self.assertAlmostEqual(
            pitch1.frequency, pitches_constants.DEFAULT_CONCERT_PITCH * 0.5
        )
        self.assertAlmostEqual(
            pitch2.frequency, pitches_constants.DEFAULT_CONCERT_PITCH * 2
        )
        self.assertAlmostEqual(
            pitch3.frequency,
            pitches_constants.DEFAULT_CONCERT_PITCH * pitch3.step_factor,
        )
        self.assertAlmostEqual(
            pitch4.frequency,
            pitches_constants.DEFAULT_CONCERT_PITCH * (pitch4.step_factor ** 2.5),
        )


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

    def test_property_ratio(self):
        ratio0 = fractions.Fraction(3, 2)
        ratio1 = fractions.Fraction(25, 1)
        ratio2 = fractions.Fraction(11, 9)
        self.assertEqual(
            pitches.JustIntonationPitch(ratio0).ratio, ratio0,
        )
        self.assertEqual(
            pitches.JustIntonationPitch(ratio1).ratio, ratio1,
        )
        self.assertEqual(
            pitches.JustIntonationPitch(ratio2).ratio, ratio2,
        )

    def test_property_closest_pythagorean_pitch(self):
        self.assertEqual(
            pitches.JustIntonationPitch("5/4").closest_pythagorean_interval,
            pitches.JustIntonationPitch("81/64"),
        )
        self.assertEqual(
            pitches.JustIntonationPitch("11/8").closest_pythagorean_interval,
            pitches.JustIntonationPitch("4/3"),
        )
        self.assertEqual(
            pitches.JustIntonationPitch("8/7").closest_pythagorean_interval,
            pitches.JustIntonationPitch("9/8"),
        )

    def test_count_accidentals(self):
        self.assertEqual(pitches.JustIntonationPitch._count_accidentals("f"), -1)
        self.assertEqual(pitches.JustIntonationPitch._count_accidentals("s"), 1)
        self.assertEqual(pitches.JustIntonationPitch._count_accidentals("sss"), 3)
        self.assertEqual(pitches.JustIntonationPitch._count_accidentals(""), 0)
        self.assertEqual(pitches.JustIntonationPitch._count_accidentals("ssf"), 1)

    def test_get_accidentals(self):
        self.assertEqual(pitches.JustIntonationPitch._get_accidentals(2), "ss")
        self.assertEqual(pitches.JustIntonationPitch._get_accidentals(-2), "ff")
        self.assertEqual(pitches.JustIntonationPitch._get_accidentals(0), "")
        self.assertEqual(pitches.JustIntonationPitch._get_accidentals(-1), "f")

    def test_conversion_to_float(self):
        ratio0 = fractions.Fraction(3, 2)
        ratio1 = fractions.Fraction(25, 1)
        ratio2 = fractions.Fraction(11, 9)
        self.assertEqual(
            float(pitches.JustIntonationPitch(ratio0)), float(ratio0),
        )
        self.assertEqual(
            float(pitches.JustIntonationPitch(ratio1)), float(ratio1),
        )
        self.assertEqual(
            float(pitches.JustIntonationPitch(ratio2)), float(ratio2),
        )

    def test_octave(self):
        jip0 = pitches.JustIntonationPitch("3/1")
        jip1 = pitches.JustIntonationPitch("1/1")
        jip2 = pitches.JustIntonationPitch("5/8")
        jip3 = pitches.JustIntonationPitch("5/16")
        jip4 = pitches.JustIntonationPitch("15/8")
        jip5 = pitches.JustIntonationPitch("2/1")
        jip6 = pitches.JustIntonationPitch("1/2")
        self.assertEqual(jip0.octave, 1)
        self.assertEqual(jip1.octave, 0)
        self.assertEqual(jip2.octave, -1)
        self.assertEqual(jip3.octave, -2)
        self.assertEqual(jip4.octave, 0)
        self.assertEqual(jip5.octave, 1)
        self.assertEqual(jip6.octave, -1)

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

    def test_indigestibility(self):
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

    def test_operator_overload_add(self):
        jip0 = pitches.JustIntonationPitch("3/2")
        jip1 = pitches.JustIntonationPitch("5/4")
        jip2 = pitches.JustIntonationPitch("3/1")
        jip0plus1 = pitches.JustIntonationPitch("15/8")
        jip0plus2 = pitches.JustIntonationPitch("9/2")
        jip1plus2 = pitches.JustIntonationPitch("15/4")
        self.assertEqual(jip0 + jip1, jip0plus1)
        self.assertEqual(jip0 + jip2, jip0plus2)
        self.assertEqual(jip1 + jip2, jip1plus2)

    def test_operator_overload_sub(self):
        jip0 = pitches.JustIntonationPitch("3/2")
        jip1 = pitches.JustIntonationPitch("5/4")
        jip2 = pitches.JustIntonationPitch("3/1")
        jip0minus1 = pitches.JustIntonationPitch("6/5")
        jip0minus2 = pitches.JustIntonationPitch("1/2")
        jip1minus2 = pitches.JustIntonationPitch("5/12")
        self.assertEqual(jip0 - jip1, jip0minus1)
        self.assertEqual(jip0 - jip2, jip0minus2)
        self.assertEqual(jip1 - jip2, jip1minus2)

    def test_operator_overload_abs(self):
        jip0 = pitches.JustIntonationPitch("1/3")
        jip0_abs = pitches.JustIntonationPitch("3/1")
        jip1 = pitches.JustIntonationPitch("5/7")
        jip1_abs = pitches.JustIntonationPitch("7/5")
        self.assertEqual(abs(jip0), jip0_abs)
        self.assertEqual(abs(jip1), jip1_abs)

    def test_add(self):
        jip0 = pitches.JustIntonationPitch("3/2")
        jip1 = pitches.JustIntonationPitch("5/4")
        jip2 = pitches.JustIntonationPitch("3/1")
        jip0.add(jip1)
        jip1.add(jip2)
        jip0plus1 = pitches.JustIntonationPitch("15/8")
        jip1plus2 = pitches.JustIntonationPitch("15/4")
        self.assertEqual(jip0, jip0plus1)
        self.assertEqual(jip1, jip1plus2)

    def test_subtract(self):
        jip0 = pitches.JustIntonationPitch("3/2")
        jip1 = pitches.JustIntonationPitch("5/4")
        jip2 = pitches.JustIntonationPitch("3/1")
        jip0.subtract(jip1)
        jip1.subtract(jip2)
        jip0minus1 = pitches.JustIntonationPitch("6/5")
        jip1minus2 = pitches.JustIntonationPitch("5/12")
        self.assertEqual(jip0, jip0minus1)
        self.assertEqual(jip1, jip1minus2)

    def test_inverse(self):
        jip0 = pitches.JustIntonationPitch("3/2")
        jip0inverse = pitches.JustIntonationPitch("2/3")
        jip1 = pitches.JustIntonationPitch("7/1")
        jip1inverse = pitches.JustIntonationPitch("1/7")
        jip2 = pitches.JustIntonationPitch("9/11")
        jip2inverse = pitches.JustIntonationPitch("11/9")

        jip0.inverse()
        jip1.inverse()

        self.assertEqual(jip0, jip0inverse)
        self.assertEqual(jip1, jip1inverse)
        self.assertEqual(jip2.inverse(mutate=False), jip2inverse)

    def test_normalize(self):
        jip0 = pitches.JustIntonationPitch("3/1")
        jip0normalized = pitches.JustIntonationPitch("3/2")
        jip1 = pitches.JustIntonationPitch("5/6")
        jip1normalized = pitches.JustIntonationPitch("5/3")
        jip2 = pitches.JustIntonationPitch("27/7")
        jip2normalized = pitches.JustIntonationPitch("27/14")

        jip0.normalize()
        jip1.normalize()

        self.assertEqual(jip0, jip0normalized)
        self.assertEqual(jip1, jip1normalized)
        self.assertEqual(jip2.normalize(mutate=False), jip2normalized)

    def test_register(self):
        jip0 = pitches.JustIntonationPitch("3/1")
        jip0registered = pitches.JustIntonationPitch("3/2")
        jip1 = pitches.JustIntonationPitch("5/3")
        jip1registered = pitches.JustIntonationPitch("5/12")
        jip2 = pitches.JustIntonationPitch("1/1")
        jip2registered = pitches.JustIntonationPitch("4/1")

        jip0.register(0)
        jip1.register(-2)

        self.assertEqual(jip0, jip0registered)
        self.assertEqual(jip1, jip1registered)
        self.assertEqual(jip2.register(2, mutate=False), jip2registered)

    def test_move_to_closest_register(self):
        jip0 = pitches.JustIntonationPitch("3/1")
        jip0_reference = pitches.JustIntonationPitch("5/4")
        jip0_closest = pitches.JustIntonationPitch("3/2")

        jip1 = pitches.JustIntonationPitch("7/1")
        jip1_reference = pitches.JustIntonationPitch("1/1")
        jip1_closest = pitches.JustIntonationPitch("7/8")

        jip2 = pitches.JustIntonationPitch("1/1")
        jip2_reference = pitches.JustIntonationPitch("7/4")
        jip2_closest = pitches.JustIntonationPitch("2/1")

        jip2.move_to_closest_register(jip2_reference)

        self.assertEqual(
            jip0.move_to_closest_register(jip0_reference, mutate=False), jip0_closest
        )
        self.assertEqual(
            jip1.move_to_closest_register(jip1_reference, mutate=False), jip1_closest
        )
        self.assertEqual(jip2, jip2_closest)

    def test_get_closest_pythagorean_pitch_name(self):
        self.assertEqual(
            pitches.JustIntonationPitch("7/4").get_closest_pythagorean_pitch_name("c"),
            "bf",
        )
        self.assertEqual(
            pitches.JustIntonationPitch("5/4").get_closest_pythagorean_pitch_name("c"),
            "e",
        )
        self.assertEqual(
            pitches.JustIntonationPitch("5/4").get_closest_pythagorean_pitch_name("a"),
            "cs",
        )
        self.assertEqual(
            pitches.JustIntonationPitch("4/5").get_closest_pythagorean_pitch_name("c"),
            "af",
        )
        self.assertEqual(
            pitches.JustIntonationPitch("1/5").get_closest_pythagorean_pitch_name("c"),
            "af",
        )
        self.assertEqual(
            pitches.JustIntonationPitch("128/25").get_closest_pythagorean_pitch_name("c"),
            "ff",
        )
        self.assertEqual(
            pitches.JustIntonationPitch("11/8").get_closest_pythagorean_pitch_name("e"),
            "a",
        )


if __name__ == "__main__":
    unittest.main()
