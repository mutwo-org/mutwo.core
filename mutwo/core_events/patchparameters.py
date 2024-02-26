# This file is part of mutwo, ecosystem for time-based arts.
#
# Copyright (C) 2024-
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

"""This file defines the flex parameter abc and an implementation for a
flex tempo trajectory. These bits should actually be inside of

  core_parameters/abc.py
  core_parameters/tempos.py

but we can't put them there, because the classes inherit from an event and
it would create a circular import error if we would move these definitions
there. Therefore we fix the circular import error by monkey-patching
'core_parameters' module inside the 'core_events' module. In order to ensure
this patch is applied whenever loading 'core_parameters', we also import
'core_events' inside 'core_parameters/__init__.py'.

While this solution is far from ideal, it's still the best way how this can
be archived:

(1) We can't force an import order (inside 'mutwo/__init__.py' because we use
    a namespace package (breaking this would break the whole mutwo
    infrastructure).

(2) We can't defer event import to call time, because it's needed at class
    creation (and we need proper classes and not some functions to construct
    classes to support inheritance,  to preserve pickle-ability and to have
    better documentation).

(3) We also can't defer the import of these bits inside 'core_parameters',
    because mutwos module structure prohibits deeper nesting apart from
    'abc', 'constants' and 'configurations': this *needs* to be present
    inside 'core_parameters'.

(4) We can't export this part to another package, as this clearly belongs
    to 'mutwo.core' and nothing else.
"""

import abc
import typing

from mutwo import core_parameters

from .envelopes import Envelope


# Extend 'mutwo/core_parameters/abc.py'
class FlexParameterMixin(Envelope):
    """Flex mixin for any :class:`SingleValueParameter`"""

    def __init__(self, event_iterable_or_point_sequence=[], *args, **kwargs):
        super().__init__(event_iterable_or_point_sequence, *args, **kwargs)

    @property
    @abc.abstractmethod
    def parameter_name(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def default_parameter(self) -> str:
        ...

    @classmethod
    def from_parameter(cls, parameter):
        if isinstance(parameter, cls):
            return parameter
        return cls([[0, parameter]])

    def value_to_parameter(self, value: typing.Any):
        return self.from_any(value)

    def parameter_to_value(self, parameter: typing.Any):
        return getattr(parameter, self.value_name)

    def apply_parameter_on_event(self, event, parameter: typing.Any):
        setattr(event, self.parameter_name, self.from_any(parameter))

    def event_to_parameter(self, event):
        return getattr(event, self.parameter_name, self.default_parameter)


core_parameters.abc.FlexParameterMixin = FlexParameterMixin
core_parameters.abc.__all__ += ("FlexParameterMixin",)


# Extend 'mutwo/core_parameters/tempos.py'
class FlexTempo(
    core_parameters.abc.Tempo, core_parameters.abc.FlexParameterMixin
):
    """A flex tempo."""

    @classmethod
    @property
    def parameter_name(cls) -> str:
        return "tempo"

    @classmethod
    @property
    def default_parameter(cls) -> core_parameters.abc.Tempo:
        return core_parameters.DirectTempo(60)

    @property
    def bpm(self):
        return self.value_at(0)


core_parameters.FlexTempo = FlexTempo
core_parameters.__all__ += ("FlexTempo",)
