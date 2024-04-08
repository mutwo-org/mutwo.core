# This file is part of mutwo, ecosystem for time-based arts.
#
# Copyright (C) 2020-2024
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

"""Defining the public API for any converter class."""

import abc
import typing

from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities

__all__ = ("Converter", "EventConverter", "SymmetricalEventConverter")


class Converter(core_utilities.MutwoObject, abc.ABC):
    """Abstract base class for all Converter classes.

    Converter classes are defined as classes that convert data between
    two different encodings. Their only public method (besides initialisation)
    should be a `convert` method. The first argument of the convert method
    should be the data to convert.
    """

    @abc.abstractmethod
    def convert(
        self, event_or_parameter_or_file_to_convert: typing.Any, *args, **kwargs
    ) -> typing.Any:
        ...

    def __call__(self, *args, **kwargs) -> typing.Any:
        return self.convert(*args, **kwargs)


class EventConverter(Converter):
    """Abstract base class for Converter which handle mutwo events.

    This class helps building new classes which convert mutwo events
    with few general private methods (and without adding any new public
    method). Converting mutwo event often involves the same pattern:
    due to the nested structure of an Event, the converter has
    to iterate through the different layers until it reaches leaves
    (any class that inherits from :class:`mutwo.core_events.Chronon`).
    This common iteration process and the different time treatment
    between :class:`mutwo.core_events.Consecution` and
    :class:`mutwo.core_events.Concurrence` are implemented in
    :class:`EventConverter`.  For writing a new EventConverter class,
    one only has to override the abstract method :func:`_convert_chronon`
    and the abstract method :func:`convert` (where one will perhaps call
    :func:`_convert_event`.).

    **Example:**

    The following example defines a dummy class for demonstrating how
    to use EventConverter.

    >>> from mutwo import core_converters
    >>> class DurationPrintConverter(core_converters.abc.EventConverter):
    ...     def _convert_chronon(self, event_to_convert, absolute_time):
    ...         return "{}: {}".format(absolute_time, event_to_convert.duration),
    ...     def convert(self, event_to_convert):
    ...         data_per_event = self._convert_event(event_to_convert, 0)
    ...         [print(data) for data in data_per_event]
    >>> # now test with random event
    >>> import random
    >>> from mutwo import core_events
    >>> random.seed(100)
    >>> random_event = core_events.Concurrence(
    ...     [
    ...        core_events.Consecution(
    ...             [
    ...                core_events.Chronon(random.uniform(0.5, 2))
    ...                 for _ in range(random.randint(2, 5))
    ...             ]
    ...         )
    ...         for _ in range(random.randint(1, 3))
    ...     ]
    ... )
    >>> DurationPrintConverter().convert(random_event)
    D(0.0): D(1.1823905068)
    D(1.1823905068): D(1.6561757085)
    D(2.8385662153): D(1.5582698404)
    D(4.3968360557): D(1.5979384595)
    D(5.9947745152): D(1.1502716523)
    """

    @abc.abstractmethod
    def _convert_chronon(
        self,
        event_to_convert: core_events.Chronon,
        absolute_time: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> typing.Sequence[typing.Any]:
        """Convert instance of :class:`mutwo.core_events.Chronon`."""

    def _convert_concurrence(
        self,
        concurrence: core_events.Concurrence,
        absolute_time: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> typing.Sequence[typing.Any]:
        """Convert instance of :class:`mutwo.core_events.Concurrence`."""
        d: list[tuple[typing.Any]] = []
        for e in concurrence:
            d.extend(self._convert_event(e, absolute_time, depth + 1))
        return tuple(d)

    def _convert_consecution(
        self,
        consecution: core_events.Consecution,
        absolute_time: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> typing.Sequence[typing.Any]:
        """Convert instance of :class:`mutwo.core_events.Consecution`."""
        d: list[tuple[typing.Any]] = []
        for t, e in zip(consecution.absolute_time_tuple, consecution):
            d.extend(self._convert_event(e, t + absolute_time, depth + 1))
        return tuple(d)

    def _convert_event(
        self,
        event_to_convert: core_events.abc.Event,
        absolute_time: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> typing.Any:
        """Convert :class:`mutwo.core_events.abc.Event` of unknown type.

        The method calls different subroutines depending on whether
        the passed event either are instances from:

            1. :class:`mutwo.core_events.Chronon` or
            2. :class:`mutwo.core_events.Consecution` or
            3. :class:`mutwo.core_events.Concurrence`.
        """
        e = event_to_convert
        t = core_parameters.abc.Duration.from_any(absolute_time)
        match e:
            case core_events.Consecution():
                f = self._convert_consecution
            case core_events.Concurrence():
                f = self._convert_concurrence
            case core_events.Chronon():
                f = self._convert_chronon
            case _:
                raise TypeError(
                    f"Can't convert object '{event_to_convert}' of type "
                    f"'{type(event_to_convert)}' with EventConverter."
                    " Supported types only include all inherited classes "
                    f"from '{core_events.abc.Event}'."
                )
        try:
            return f(event_to_convert, t, depth)
        except TypeError:
            return f(event_to_convert, t)


class SymmetricalEventConverter(EventConverter):
    """Abstract base class for Converter which handle mutwo core_events.

    This converter is a more specified version of the :class:`EventConverter`.
    It helps for building converters which aim to return mutwo core_events.
    """

    @abc.abstractmethod
    def _convert_chronon(
        self,
        event_to_convert: core_events.Chronon,
        absolute_time: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> core_events.Chronon:
        """Convert instance of :class:`mutwo.core_events.Chronon`."""

    def _convert_concurrence(
        self,
        concurrence: core_events.Concurrence,
        absolute_time: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> core_events.Concurrence:
        """Convert instance of :class:`mutwo.core_events.Concurrence`."""
        sim: core_events.Concurrence = concurrence.empty_copy()
        for e in concurrence:
            sim.append(self._convert_event(e, absolute_time, depth + 1))
        return sim

    def _convert_consecution(
        self,
        consecution: core_events.Consecution,
        absolute_time: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> core_events.Consecution:
        """Convert instance of :class:`mutwo.core_events.Consecution`."""
        cons: core_events.Consecution = consecution.empty_copy()
        for t, e in zip(consecution.absolute_time_tuple, consecution):
            cons.append(self._convert_event(e, t + absolute_time, depth + 1))
        return cons

    def _convert_event(
        self,
        event_to_convert: core_events.abc.Event,
        absolute_time: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> core_events.abc.Compound[core_events.abc.Event]:
        return super()._convert_event(event_to_convert, absolute_time, depth)
