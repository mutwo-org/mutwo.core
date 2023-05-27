"""Definition of global constants which are used all over mutwo.
"""

import fractions
import typing

import quicktions

Real = float | fractions.Fraction | quicktions.Fraction | int
"""The main reason for this constant is a mypy issue with Pythons buildin
[numbers module](https://docs.python.org/3/library/numbers.html) which
is documented [here](https://github.com/python/mypy/issues/3186). Mypy
doesn't accept numbers abstract base classes. Until numbers will be
supported users have to define their own typing data for general number
classes. PEP 3141 recommends users to simply annotate arguments with
'float', but this wouldn't include `fractions.Fraction` which is often
necessary in musical contexts (as github user arseniiv also remarked)."""

DurationType = Real
"""Type variable to arguments and return values for `duration`.
This can be any real number (float, integer, fraction)."""

ParameterType = typing.Any
"""Type variable to assign to arguments and return values
which expect objects from the :mod:`mutwo.core.parameters` module,
but could actually be anything."""
