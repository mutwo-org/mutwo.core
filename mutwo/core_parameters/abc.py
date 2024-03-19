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

"""Abstract base classes for different parameters.

This module defines the public API of parameters.
Most other mutwo classes rely on this API. This means
when someone creates a new class inheriting from any of the
abstract parameter classes which are defined in this module,
she or he can make use of all other mutwo modules with this
newly created parameter class.
"""

from __future__ import annotations

import abc
import ast
import functools
import operator
import typing

try:
    import quicktions as fractions
except ImportError:
    import fractions

    _fractions = None
else:
    import fractions as _fractions

from mutwo import core_constants
from mutwo import core_parameters
from mutwo import core_utilities

__all__ = (
    "Parameter",
    "SingleValueParameter",
    "SingleNumberParameter",
    "Duration",
    "Tempo",
)

T = typing.TypeVar("T", bound="Parameter")


class Parameter(core_utilities.MutwoObject, abc.ABC):
    """A Parameter is the base class for all mutwo parameters

    It can be useful as a type hint for any code where a parameter
    object is expected. This isn't necessarily at many places,
    as mostly any object can be assigned as a parameter to an event.
    """

    @classmethod
    def from_any(cls: typing.Type[T], object) -> T:
        """Parse any object to Parameter.

        :param object: Object that is parsed to the parameter.
        :raises: core_utilities.CannotParseError in case the object
          can't be parsed to the parameter type.

        This method is useful for allowing syntactic sugar.
        """
        if not isinstance(object, cls):
            raise core_utilities.CannotParseError(object, cls)
        return object


class SingleValueParameter(Parameter):
    """Abstract base class for all parameters which are defined by one value.

    Classes which inherit from this base class have
    to provide an additional keyword argument `value_name`.
    Furthermore they can provide the optional keyword argument
    `value_return_type`.

    **Example:**

    >>> from mutwo import core_parameters
    >>> class Color(
    ...     core_parameters.abc.SingleValueParameter,
    ...     value_name="color",
    ...     value_return_type=str
    ... ):
    ...     def __init__(self, color: str):
    ...         self._color = color
    ...     @property
    ...     def color(self) -> str:
    ...         return self._color
    >>> red = Color('red')
    >>> red.color
    'red'
    >>> orange = Color('orange')
    >>> red2 = Color('red')
    >>> red == orange
    False
    >>> red == red2
    True
    """

    def __init_subclass__(
        cls, value_name: str = "", value_return_type: typing.Type = typing.Any
    ):
        # We will only add an abstract method with "value_name" in two
        # cases for the following reasons
        #
        #   1. If our value_name is empty we shouldn't add any new method.
        #      With this we can prevent that a new abstract property is created
        #      when no value_name is provided and the default value_name isn't
        #      empty. This would be a problem if for instance we would have the
        #      following inheritance structure:
        #
        #      SingleValueParameter ->
        #
        #           Pitch(SingleValueParameter, value_name="frequency") ->
        #
        #               MidiPitch(Pitch)
        #
        #       The last class shouldn't get any new abstract property (with
        #       a not-empty default name).
        #
        #   2. If the class already defines a method with the specific
        #      value_name it shouldn't be overridden (because the user already
        #      ensured there is a property). Overriding this manually defined property
        #      would lead to unexpected and undesired results.
        if value_name:
            if not hasattr(cls, value_name):

                @abc.abstractmethod
                def abstract_method(_) -> value_return_type:
                    raise NotImplementedError

                setattr(cls, value_name, property(abstract_method))

            if hasattr(cls, "value_name"):
                raise core_utilities.AlreadyDefinedValueNameError(cls)

            setattr(cls, "value_name", classmethod(property(lambda _: value_name)))

    def __repr_content__(self) -> str:
        return f"{getattr(self, self.value_name)}"  # type: ignore

    def __str_content__(self) -> str:
        return f"{getattr(self, self.value_name)}"  # type: ignore

    def __eq__(self, other: typing.Any) -> bool:
        try:
            return getattr(self, self.value_name) == getattr(other, self.value_name)  # type: ignore
        except AttributeError:
            return False


@functools.total_ordering
class SingleNumberParameter(SingleValueParameter):
    """Abstract base class for all parameters which are defined by one number.

    Classes which inherit from this base class have to override
    the same methods and properties as one have to override
    when inheriting from :class:`SingleValueParameter`.

    Furthermore the property `digit_to_round_to_count`
    can be overridden. This should return an integer or `None`.
    If it returns an integer it will first round two numbers
    before comparing them with the `==` or `<` or `<=` or `>`
    or `>=` operators.
    The default implementation always returns `None.

    **Example:**

    >>> from mutwo import core_parameters
    >>> class Speed(
    ...     core_parameters.abc.SingleNumberParameter,
    ...     value_name="meter_per_seconds",
    ...     value_return_type=float
    ... ):
    ...     def __init__(self, meter_per_seconds: float):
    ...         self._meter_per_seconds = meter_per_seconds
    ...     @property
    ...     def meter_per_seconds(self) -> float:
    ...         return self._meter_per_seconds
    >>> light_speed = Speed(299792458)
    >>> sound_speed = Speed(343)
    >>> light_speed > sound_speed
    True
    """

    direct_comparison_type_tuple = tuple([])

    @property
    def digit_to_round_to_count(self) -> typing.Optional[int]:
        return None

    def _prepare_value_pair_for_comparison(
        self, value_pair: tuple[core_constants.Real, core_constants.Real]
    ) -> tuple[core_constants.Real, core_constants.Real]:
        return tuple(
            core_utilities.round_floats(value, self.digit_to_round_to_count)
            if self.digit_to_round_to_count
            else value
            for value in value_pair
        )

    def _compare(
        self,
        other: typing.Any,
        compare: typing.Callable[[core_constants.Real, core_constants.Real], bool],
        raise_exception: bool,
    ):
        """Compare itself with other object"""

        try:
            value_pair = (
                getattr(self, self.value_name),  # type: ignore
                other
                if isinstance(other, self.direct_comparison_type_tuple)
                else getattr(other, self.value_name),  # type: ignore
            )
        except AttributeError:
            if raise_exception:
                raise TypeError(
                    f"Can't compare object '{self}' of type '{type(self)}' with"
                    f" object '{other}' of type '{type(other)}'!"
                )
            return False

        return compare(*self._prepare_value_pair_for_comparison(value_pair))

    def __float__(self) -> float:
        return float(getattr(self, self.value_name))  # type: ignore

    def __int__(self) -> int:
        return int(float(self))

    def __eq__(self, other: typing.Any) -> bool:
        return self._compare(other, lambda value0, value1: value0 == value1, False)

    def __lt__(self, other: typing.Any) -> bool:
        return self._compare(other, lambda value0, value1: value0 < value1, True)


class Duration(
    SingleNumberParameter, value_name="beat_count", value_return_type="float"
):
    """Abstract base class for any duration.

    If the user wants to define a Duration class, the abstract
    property :attr:`beat_count` has to be overridden.

    The ``duration`` of :mod:`mutwo` events are not
    related to a clear physical unit as for instance seconds.
    The reason for this decision is to simplify musical usage.
    """

    direct_comparison_type_tuple = (float, int, fractions.Fraction)
    if _fractions:
        direct_comparison_type_tuple += (_fractions.Fraction,)

    Type: typing.TypeAlias = typing.Union[core_constants.Real, str, "Duration"]
    """Duration.Type hosts all types that are supported by the duration parser
    :func:`Duration.from_any`."""

    def _math_operation(
        self,
        other: Duration | core_constants.Real,
        operation: typing.Callable[[float, float], float],
    ) -> Duration:
        self.beat_count = float(
            operation(self.beat_count, getattr(other, "beat_count", other))
        )
        return self

    def add(self, other: Duration | core_constants.Real) -> Duration:
        return self._math_operation(other, operator.add)

    def subtract(self, other: Duration | core_constants.Real) -> Duration:
        return self._math_operation(other, operator.sub)

    def multiply(self, other: Duration | core_constants.Real) -> Duration:
        return self._math_operation(other, operator.mul)

    def divide(self, other: Duration | core_constants.Real) -> Duration:
        return self._math_operation(other, operator.truediv)

    def __add__(self, other: Duration | core_constants.Real) -> Duration:
        return self.copy().add(other)

    def __sub__(self, other: Duration | core_constants.Real) -> Duration:
        return self.copy().subtract(other)

    def __mul__(self, other: Duration | core_constants.Real) -> Duration:
        return self.copy().multiply(other)

    def __truediv__(self, other: Duration | core_constants.Real) -> Duration:
        return self.copy().divide(other)

    def __float__(self) -> float:
        return self.beat_count

    @property
    @abc.abstractmethod
    def beat_count(self) -> float:
        ...

    @beat_count.setter
    @abc.abstractmethod
    def beat_count(self, beat_count: core_constants.Real):
        ...

    @classmethod
    def from_any(cls: typing.Type[T], object: Duration.Type) -> T:
        builtin_fraction = _fractions.Fraction if _fractions else fractions.Fraction
        match object:
            case Duration():
                return object
            case float() | int():
                return core_parameters.DirectDuration(object)
            case fractions.Fraction() | builtin_fraction():
                return core_parameters.RatioDuration(object)
            case str():
                f = core_utilities.str_to_number_parser(object)
                try:
                    v = f(object)
                except ValueError:
                    pass
                else:
                    return Duration.from_any(v)
            case _:
                pass

        raise core_utilities.CannotParseError(object, cls)


class Tempo(SingleNumberParameter, value_name="bpm", value_return_type="float"):
    """Represent the active tempo at a specific moment in time.

    If the user wants to define a `Tempo` class, the abstract
    property :attr:`bpm` needs to be overridden. ``BPM`` is an abbreviation
    for 'beats per minute' and the unit of the parameter tempo, see more
    information at this `wikipedia article <https://en.wikipedia.org/wiki/Tempo#Measurement>`_.
    """

    Type: typing.TypeAlias = typing.Union["Tempo", core_constants.Real]
    """Tempo.Type hosts all types that are supported by the tempo
    parser :func:`Tempo.from_any`."""

    @property
    def seconds(self) -> float:
        """How many seconds one beat lasts with current BPM."""
        return float(60 / self.bpm)

    @classmethod
    def from_any(cls: typing.Type[T], object: Tempo.Type) -> T:
        builtin_fraction = _fractions.Fraction if _fractions else fractions.Fraction
        match object:
            case Tempo():
                return object
            case float() | int() | fractions.Fraction() | builtin_fraction():
                return core_parameters.DirectTempo(object)
            case list() | tuple():
                return core_parameters.FlexTempo(object)
            case str():
                f, v = core_utilities.str_to_number_parser(object), None
                try:
                    v = f(object)
                except ValueError:
                    try:
                        v = ast.literal_eval(object)
                    except Exception:
                        raise core_utilities.CannotParseError(object, cls)
                return Tempo.from_any(v)
            case _:
                raise core_utilities.CannotParseError(object, cls)
