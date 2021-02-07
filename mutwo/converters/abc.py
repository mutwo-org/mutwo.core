import abc
import typing

__all__ = ("Converter",)


class Converter(abc.ABC):
    @abc.abstractmethod
    def convert(self, event_or_parameter_or_file_to_convert: typing.Any) -> typing.Any:
        raise NotImplementedError
