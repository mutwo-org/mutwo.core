import fractions

ACCIDENTAL_NAME_TO_PITCH_CLASS_MODIFICATION = {
    accidental_name: pitch_class_modification
    for accidental_name, pitch_class_modification in zip(
        "f s qf qs rf rs ef es xf xs tf ts".split(" "),
        (
            -fractions.Fraction(1, 1),
            fractions.Fraction(1, 1),
            -fractions.Fraction(1, 2),
            fractions.Fraction(1, 2),
            -fractions.Fraction(1, 3),
            fractions.Fraction(1, 3),
            -fractions.Fraction(1, 4),
            fractions.Fraction(1, 4),
            -fractions.Fraction(1, 6),
            fractions.Fraction(1, 6),
            -fractions.Fraction(1, 12),
            fractions.Fraction(1, 12),
        ),
    )
}
