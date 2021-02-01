import typing


def reflected_binary_code(length: int, modulus: int) -> typing.Tuple[typing.Tuple[int]]:
    """Returns the length-tuple reflected binary code mod modulus.

    :param length: how long one code is
    :param modulus: how many different numbers are included

    Basic code has been copied from:
        https://yetalengthothermodulusathblog.com/tag/gray-codes/
    """

    def _recursive_gray_code_maker(
        length: int, modulus: int
    ) -> typing.List[typing.List[int]]:
        F = range(modulus)
        if length == 1:
            return [[i] for i in F]
        L = _recursive_gray_code_maker(length - 1, modulus)
        M = []
        for j in F:
            M = M + [ll + [j] for ll in L]
        k = len(M)
        Mr = [0] * modulus
        for i in range(modulus - 1):
            i1 = i * int(k / modulus)
            i2 = (i + 1) * int(k / modulus)
            Mr[i] = M[i1:i2]
        Mr[modulus - 1] = M[(modulus - 1) * int(k / modulus) :]
        for i in range(modulus):
            if i % 2 != 0:
                Mr[i].reverse()
        M0 = []
        for i in range(modulus):
            M0 = M0 + Mr[i]
        return M0

    return tuple(
        tuple(reversed(list_)) for list_ in _recursive_gray_code_maker(length, modulus)
    )
