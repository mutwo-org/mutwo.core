# This file is part of mutwo, ecosystem for time-based arts.
#
# Copyright (C) 2020-2023
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Definition of global constants which are used all over mutwo.
"""

import fractions
import typing

try:
    import quicktions
except ImportError:
    quicktions = None

Real: typing.TypeAlias = float | fractions.Fraction | int
"""The main reason for this constant is a mypy issue with Pythons buildin
`numbers module <https://docs.python.org/3/library/numbers.html>`_ which
is documented `here <https://github.com/python/mypy/issues/3186>_. Mypy
doesn't accept numbers abstract base classes. Until numbers will be
supported users have to define their own typing data for general number
classes. PEP 3141 recommends users to simply annotate arguments with
'float', but this wouldn't include `fractions.Fraction` which is often
necessary in musical contexts (as github user arseniiv also remarked)."""

if quicktions:
    Real |= quicktions.Fraction

# Cleanup
del fractions, quicktions, typing
