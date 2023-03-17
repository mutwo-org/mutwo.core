import cython
from cython.cimports.libc import math

@cython.nonecheck(False)
@cython.cdivision(True)
def scalex(
    value: cython.longdouble,
    old_min: cython.longdouble,
    old_max: cython.longdouble,
    new_min: cython.longdouble,
    new_max: cython.longdouble,
    translation_shape: cython.longdouble,
) -> cython.longdouble:
    old_span: cython.longdouble = old_max - old_min

    percentage: cython.longdouble = (value - old_min) / old_span
    new_range: cython.longdouble = new_max - new_min
    if translation_shape:
        value: cython.longdouble = (new_range / ((math.exp(translation_shape)) - 1)) * (
            math.exp(translation_shape * percentage) - 1
        )
    else:
        value: cython.longdouble = new_range * percentage
    r: cython.longdouble = value + new_min
    return r


