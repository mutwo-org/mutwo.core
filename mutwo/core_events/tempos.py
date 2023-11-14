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

from mutwo import core_events

__all__ = ("TempoEvent",)


# XXX: Currently type hints are deactivated here, because otherwise we get
# problems with circular imports (because 'TempoEvent' is needed by envelopes
# and because envelopes are needed by parameters). Because this code is very
# short, it may not matter so much.
class TempoEvent(core_events.SimpleEvent):
    def __init__(self, tempo_point, *args, **kwargs):
        self.tempo_point = tempo_point
        super().__init__(*args, **kwargs)

    @property
    def tempo_point(self):
        return self._tempo_point

    @tempo_point.setter
    def tempo_point(self, tempo_point):
        self._tempo_point = core_events.configurations.UNKNOWN_OBJECT_TO_TEMPO_POINT(
            tempo_point
        )
