"""Abstract base classes for different parameters.

This module defines the public API of parameters.
Most other mutwo classes rely on this API. This means
when someone creates a new class inheriting from any of the
abstract parameter classes which are defined in this module,
she or he can make use of all other mutwo modules with this
newly created parameter class.
"""


import abc
import typing

from mutwo.core import events
from mutwo.core.utilities import constants

__all__ = ("ParameterWithEnvelope",)


class ParameterWithEnvelope(abc.ABC):
    """Abstract base class for all parameters with an envelope."""

    def __init__(self, envelope: events.envelopes.RelativeEnvelope):
        self.envelope = envelope

    @property
    def envelope(self) -> events.envelopes.RelativeEnvelope:
        return self._envelope

    @envelope.setter
    def envelope(self, new_envelope: typing.Any):
        try:
            assert isinstance(new_envelope, events.envelopes.RelativeEnvelope)
        except AssertionError:
            raise TypeError(
                f"Found illegal object '{new_envelope}' of not "
                f"supported type '{type(new_envelope)}'. "
                f"Only instances of '{events.envelopes.RelativeEnvelope}'"
                " are allowed!"
            )
        self._envelope = new_envelope

    def resolve_envelope(
        self,
        duration: constants.DurationType,
        resolve_envelope_class: type[
            events.envelopes.Envelope
        ] = events.envelopes.Envelope,
    ) -> events.envelopes.Envelope:
        return self.envelope.resolve(duration, self, resolve_envelope_class)
