import fractions

ACCIDENTAL_NAME_TO_PITCH_CLASS_MODIFICATION = {
    # multiply with 2 because the difference of "1" in pitch
    # class is defined as one chromatic step (see class
    # definition of WesternPitch)
    accidental_name: accidental_value * 2
    for accidental_name, accidental_value in {
        # double sharp / double flat
        "ff": -fractions.Fraction(1, 1),
        "ss": fractions.Fraction(1, 1),
        # eleven twelfth-tone
        "etf": -fractions.Fraction(11, 12),
        "ets": fractions.Fraction(11, 12),
        # seven eigth-tone
        "sef": -fractions.Fraction(7, 8),
        "ses": fractions.Fraction(7, 8),
        # two third-tone
        "trf": -fractions.Fraction(2, 3),
        "trs": fractions.Fraction(2, 3),
        # three quarter-tone
        "tqf": -fractions.Fraction(3, 4),
        "tqs": fractions.Fraction(3, 4),
        # seven sixth-tone
        "sxf": -fractions.Fraction(7, 6),
        "sxs": fractions.Fraction(7, 6),
        # nine eight-tone
        "nef": -fractions.Fraction(9, 8),
        "nes": fractions.Fraction(9, 8),
        # seven twelfth-tone
        "stf": -fractions.Fraction(7, 12),
        "sts": fractions.Fraction(7, 12),
        # ordinary sharp / flat
        "f": -fractions.Fraction(1, 2),
        "s": fractions.Fraction(1, 2),
        # five twelfth-tone
        "ftf": -fractions.Fraction(5, 12),
        "fts": fractions.Fraction(5, 12),
        # three eigth-tone
        "tef": -fractions.Fraction(3, 8),
        "tes": fractions.Fraction(3, 8),
        # one third-tone (use "r" to avoid conufsion with twelfth-tone)
        "rf": -fractions.Fraction(1, 3),
        "rs": fractions.Fraction(1, 3),
        # one quarter-tone
        "qf": -fractions.Fraction(1, 4),
        "qs": fractions.Fraction(1, 4),
        # one sixth-tone (use x to avoid confusion with double-sharp ss)
        "xf": -fractions.Fraction(1, 6),
        "xs": fractions.Fraction(1, 6),
        # one eigth-tone
        "ef": -fractions.Fraction(1, 8),
        "es": fractions.Fraction(1, 8),
        # one twelfth-tone
        "tf": -fractions.Fraction(1, 12),
        "ts": fractions.Fraction(1, 12),
        # no accidental / empty string
        "": fractions.Fraction(0, 1),
    }.items()
}
