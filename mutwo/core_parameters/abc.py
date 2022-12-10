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
import functools
import operator
import typing

import quicktions as fractions
import fractions as _fractions

import ranges

from mutwo import core_constants
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities

__all__ = (
    "SingleValueParameter",
    "SingleNumberParameter",
    "ParameterWithEnvelope",
    "Duration",
    "TempoPoint",
)


class ParameterWithEnvelope(abc.ABC):
    """Abstract base class for all parameters with an envelope."""

    def __init__(self, envelope: core_events.RelativeEnvelope):
        self.envelope = envelope

    @property
    def envelope(self) -> core_events.RelativeEnvelope:
        return self._envelope

    @envelope.setter
    def envelope(self, new_envelope: typing.Any):
        if not isinstance(new_envelope, core_events.RelativeEnvelope):
            raise TypeError(
                f"Found illegal object '{new_envelope}' of not "
                f"supported type '{type(new_envelope)}'. "
                f"Only instances of '{core_events.RelativeEnvelope}'"
                " are allowed!"
            )
        self._envelope = new_envelope

    def resolve_envelope(
        self,
        duration: core_constants.DurationType,
        # XXX: We can't directly set the default attribute value,
        # but we have to do it with `None` and resolve it later,
        # because otherwise we will get a circular import
        # (core_parameters need to be imported before core_events,
        #  because we need core_parameters.Duration in core_events).
        resolve_envelope_class: typing.Optional[type[core_events.Envelope]] = None,
    ) -> core_events.Envelope:
        resolve_envelope_class = resolve_envelope_class or core_events.Envelope
        return self.envelope.resolve(duration, self, resolve_envelope_class)


class SingleValueParameter(abc.ABC):
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

            setattr(cls, "value_name", property(lambda _: value_name))

    def __str__(self) -> str:
        return (
            f"{type(self).__name__}"
            f"({self.value_name} = {getattr(self, self.value_name)})"  # type: ignore
        )

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

        value0, value1 = self._prepare_value_pair_for_comparison(value_pair)
        return compare(value0, value1)

    def __float__(self) -> float:
        return float(getattr(self, self.value_name))  # type: ignore

    def __int__(self) -> int:
        return int(float(self))

    def __eq__(self, other: typing.Any) -> bool:
        return self._compare(other, lambda value0, value1: value0 == value1, False)

    def __lt__(self, other: typing.Any) -> bool:
        return self._compare(other, lambda value0, value1: value0 < value1, True)


class Duration(
    SingleNumberParameter, value_name="duration", value_return_type="fractions.Fraction"
):
    """Abstract base class for any duration.

    If the user wants to define a Duration class, the abstract
    property :attr:`duration` has to be overridden.

    The attribute :attr:`duration` is stored in unit `beats`.
    """

    direct_comparison_type_tuple = (float, int, fractions.Fraction, _fractions.Fraction)

    def _math_operation(
        self, other: DurationOrReal, operation: typing.Callable[[float, float], float]
    ) -> Duration:
        self.duration = fractions.Fraction(
            operation(self.duration, getattr(other, "duration", other))
        )
        return self

    @core_utilities.add_copy_option
    def add(self, other: DurationOrReal) -> Duration:
        return self._math_operation(other, operator.add)

    @core_utilities.add_copy_option
    def subtract(self, other: DurationOrReal) -> Duration:
        return self._math_operation(other, operator.sub)

    @core_utilities.add_copy_option
    def multiply(self, other: DurationOrReal) -> Duration:
        return self._math_operation(other, operator.mul)

    @core_utilities.add_copy_option
    def divide(self, other: DurationOrReal) -> Duration:
        return self._math_operation(other, operator.truediv)

    def __add__(self, other: DurationOrReal) -> Duration:
        return self.add(other, mutate=False)

    def __sub__(self, other: DurationOrReal) -> Duration:
        return self.subtract(other, mutate=False)

    def __mul__(self, other: DurationOrReal) -> Duration:
        return self.multiply(other, mutate=False)

    def __truediv__(self, other: DurationOrReal) -> Duration:
        return self.divide(other, mutate=False)

    def __float__(self) -> float:
        return core_utilities.round_floats(
            float(self.duration),
            core_parameters.configurations.ROUND_DURATION_TO_N_DIGITS,
        )

    @property
    def duration_in_floats(self) -> float:
        return float(self)

    @property
    def duration(self) -> fractions.Fraction:
        ...

    @duration.setter
    @abc.abstractmethod
    def duration(self, duration: fractions.Fraction):
        ...


DurationOrReal = Duration | core_constants.Real


class TempoPoint(abc.ABC):
    """Represent the active tempo at a specific moment in time.

    If the user wants to define a `TempoPoint` class, the abstract
    properties :attr:`tempo_or_tempo_range_in_beats_per_minute`
    and `reference` have to be overridden.
    """

    def __repr__(self) -> str:
        return "{}(BPM = {}, reference = {})".format(
            type(self).__name__, self.tempo_in_beats_per_minute, self.reference
        )

    def __eq__(self, other: object) -> bool:
        attribute_to_compare_tuple = (
            "tempo_in_beats_per_minute",
            "reference",
        )
        return core_utilities.test_if_objects_are_equal_by_parameter_tuple(
            self, other, attribute_to_compare_tuple
        )

    @property
    @abc.abstractmethod
    def tempo_or_tempo_range_in_beats_per_minute(
        self,
    ) -> core_parameters.constants.TempoOrTempoRangeInBeatsPerMinute:
        ...

    @property
    @abc.abstractmethod
    def reference(self) -> core_constants.Real:
        ...

    @property
    def tempo_in_beats_per_minute(
        self,
    ) -> core_parameters.constants.TempoInBeatsPerMinute:
        """Get tempo in `beats per minute <https://en.wikipedia.org/wiki/Tempo#Measurement>`_

        If :attr:`tempo_or_tempo_range_in_beats_per_minute` is a range
        mutwo will return the minimal tempo.
        """

        if isinstance(self.tempo_or_tempo_range_in_beats_per_minute, ranges.Range):
            return self.tempo_or_tempo_range_in_beats_per_minute.start
        else:
            return self.tempo_or_tempo_range_in_beats_per_minute

    @property
    def absolute_tempo_in_beats_per_minute(self) -> float:
        """Get absolute tempo in `beats per minute <https://en.wikipedia.org/wiki/Tempo#Measurement>`_

        The absolute tempo takes the :attr:`reference` of the :class:`TempoPoint`
        into account.
        """

        return self.tempo_in_beats_per_minute * self.reference
