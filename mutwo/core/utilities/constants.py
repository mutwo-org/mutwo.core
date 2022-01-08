"""Definition of global variables which are used all over mutwo.

The main reason for this package is a mypy issue with Pythons buildin
[numbers module](https://docs.python.org/3/library/numbers.html) which
is documented [here](https://github.com/python/mypy/issues/3186). Mypy
doesn't accept numbers abstract base classes. Until numbers will be
supported users have to define their own typing data for general number
classes. PEP 3141 recommends users to simply annotate arguments with
'float', but this wouldn't include `fractions.Fraction` which is often
necessary in musical contexts (as github user arseniiv also remarked).
"""

import fractions
import typing

Real = typing.Union[float, fractions.Fraction]
