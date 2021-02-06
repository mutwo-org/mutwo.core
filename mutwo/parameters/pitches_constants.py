import fractions
import math

# constant used for cent calculation in mutwo.parameters.pitches.abc.Pitch
CENT_CALCULATION_CONSTANT = 1200 / (math.log10(2))

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


PITCH_CLASS_MODIFICATION_TO_ACCIDENTAL_NAME = {
    accidental_value: accidental_name
    for accidental_name, accidental_value in ACCIDENTAL_NAME_TO_PITCH_CLASS_MODIFICATION.items()
}


DEFAULT_CONCERT_PITCH = 440

# sets octave of default concert pitch for western pitch to one line (')
# (so that the resulting concert pitch is a' or in midi nomenclature a4)
DEFAULT_CONCERT_PITCH_OCTAVE_FOR_WESTERN_PITCH = 4

# sets pitch class 'a' as default pitch class for the concert pitch of
# the WesternPitch class
DEFAULT_CONCERT_PITCH_PITCH_CLASS_FOR_WESTERN_PITCH = 9

DIATONIC_PITCH_NAME_TO_PITCH_CLASS = {
    diatonic_pitch_name: pitch_class
    for diatonic_pitch_name, pitch_class in zip(
        "c d e f g a b".split(" "), (0, 2, 4, 5, 7, 9, 11)
    )
}

MIDI_PITCH_FREQUENCIES = (
    8.175798915643705,
    8.66195721802725,
    9.177023997418985,
    9.722718241315027,
    10.300861153527185,
    10.91338223228137,
    11.562325709738575,
    12.249857374429666,
    12.978271799373287,
    13.750000000000,
    14.567617547440312,
    15.433853164253883,
    16.35159783128741,
    17.3239144360545,
    18.35404799483797,
    19.445436482630054,
    20.60172230705437,
    21.82676446456274,
    23.12465141947715,
    24.499714748859333,
    25.956543598746574,
    27.500000000000004,
    29.135235094880624,
    30.867706328507765,
    32.70319566257482,
    34.647828872109,
    36.70809598967594,
    38.89087296526011,
    41.20344461410874,
    43.65352892912548,
    46.2493028389543,
    48.999429497718666,
    51.91308719749315,
    55.00000000000001,
    58.27047018976125,
    61.73541265701553,
    65.40639132514964,
    69.295657744218,
    73.41619197935188,
    77.78174593052022,
    82.40688922821748,
    87.30705785825096,
    92.4986056779086,
    97.99885899543733,
    103.8261743949863,
    110.00000000000001,
    116.5409403795225,
    123.47082531403106,
    130.81278265029928,
    138.591315488436,
    146.83238395870376,
    155.56349186104043,
    164.81377845643496,
    174.6141157165019,
    184.9972113558172,
    195.99771799087466,
    207.6523487899726,
    220.00000000000003,
    233.081880759045,
    246.94165062806212,
    261.62556530059857,
    277.182630976872,
    293.6647679174075,
    311.12698372208087,
    329.6275569128699,
    349.2282314330038,
    369.9944227116344,
    391.9954359817493,
    415.3046975799452,
    440.00000000000006,
    466.16376151809,
    493.88330125612424,
    523.2511306011971,
    554.365261953744,
    587.329535834815,
    622.2539674441617,
    659.2551138257398,
    698.4564628660077,
    739.9888454232688,
    783.9908719634986,
    830.6093951598904,
    880.0000000000001,
    932.32752303618,
    987.7666025122485,
    1046.5022612023943,
    1108.730523907488,
    1174.65907166963,
    1244.5079348883235,
    1318.5102276514797,
    1396.9129257320153,
    1479.9776908465376,
    1567.9817439269973,
    1661.2187903197807,
    1760.0000000000002,
    1864.65504607236,
    1975.533205024497,
    2093.0045224047885,
    2217.461047814976,
    2349.31814333926,
    2489.015869776647,
    2637.0204553029594,
    2793.8258514640306,
    2959.955381693075,
    3135.9634878539946,
    3322.4375806395615,
    3520.0000000000005,
    3729.31009214472,
    3951.066410048994,
    4186.009044809577,
    4434.922095629952,
    4698.63628667852,
    4978.031739553294,
    5274.040910605919,
    5587.651702928061,
    5919.91076338615,
    6271.926975707989,
    6644.875161279123,
    7040.000000000001,
    7458.62018428944,
    7902.132820097988,
    8372.018089619154,
    8869.844191259905,
    9397.27257335704,
    9956.063479106588,
    10548.081821211837,
    11175.303405856122,
    11839.8215267723,
)


MIDI_PITCH_NUMBERS = tuple(range(127))
