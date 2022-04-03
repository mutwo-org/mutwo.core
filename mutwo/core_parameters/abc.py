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
import typing

from mutwo import core_constants
from mutwo import core_events
from mutwo import core_utilities

__all__ = (
    "SingleValueParameter",
    "SingleNumberParameter",
    "ParameterWithEnvelope",
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
        try:
            assert isinstance(new_envelope, core_events.RelativeEnvelope)
        except AssertionError:
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
        resolve_envelope_class: type[core_events.Envelope] = core_events.Envelope,
    ) -> core_events.Envelope:
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
            core_parameters.abc.SingleValueParameter,
            value_name="color",
            value_return_type=str
        ):
            def __init__(self, color: str):
                self._color = color
            @property
            def color(self) -> str:
                return self._color
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
        #      ensured there is a property). Overriding this manually defined property would lead to unexpected and undesired results.
        if value_name and not hasattr(cls, value_name):

            @abc.abstractmethod
            def abstract_method(_) -> value_return_type:
                raise NotImplementedError

            setattr(cls, value_name, property(abstract_method))

        if value_name:
            if hasattr(cls, "value_name"):
                raise Exception(
                    (
                        f"Confusing setup in class '{cls}' which inherits from "
                        "'SingleValueParameter'. Found already a defined value for"
                        " 'value_name'. SingleValueParameter instances can only "
                        "have one value!"
                    )
                )

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
            core_parameters.abc.SingleNumberParameter,
            value_name="meter_per_seconds",
            value_return_type=float
        ):
            def __init__(self, meter_per_seconds: float):
                self._meter_per_seconds = meter_per_seconds
            @property
            def meter_per_seconds(self) -> float:
                return self._meter_per_seconds
    >>> light_speed = Speed(299792458)
    >>> sound_speed = Speed(343)
    >>> light_speed > sound_speed
    True
    """

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
    ):
        """Compare itself with other object"""

        try:
            value_pair = (
                getattr(self, self.value_name),  # type: ignore
                getattr(other, self.value_name),  # type: ignore
            )
        except AttributeError:
            return False

        value0, value1 = self._prepare_value_pair_for_comparison(value_pair)
        return compare(value0, value1)

    def __float__(self) -> float:
        return float(getattr(self, self.value_name))  # type: ignore

    def __int__(self) -> int:
        return int(float(self))

    def __eq__(self, other: typing.Any) -> bool:
        return self._compare(other, lambda value0, value1: value0 == value1)

    def __lt__(self, other: typing.Any) -> bool:
        return self._compare(other, lambda value0, value1: value0 < value1)
