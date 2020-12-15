import abc
import typing

import mutwo.converters.abc as converters_abc


class ParameterConverter(converters_abc.Converter):
    """Abstract base class for converters that translate mutwo parameters to different formats."""

    @abc.abstractmethod
    def convert(self, parameter_to_convert: typing.Any) -> typing.Any:
        raise NotImplementedError
