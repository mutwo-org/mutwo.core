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

import ranges

TempoInBeatsPerMinute = float
"""Type alias for `TempoInBeatsPerMinute`. Used in
`core_parameters.abc.TempoPoint`"""

TempoRangeInBeatsPerMinute = ranges.Range
"""Type alias for `TempoRangeInBeatsPerMinute`. Used in
`core_parameters.abc.TempoPoint`"""

TempoOrTempoRangeInBeatsPerMinute = TempoInBeatsPerMinute | TempoRangeInBeatsPerMinute
"""Type alias for `TempoOrTempoRangeInBeatsPerMinute`. Used in
`core_parameters.abc.TempoPoint`"""

# Cleanup
del ranges
