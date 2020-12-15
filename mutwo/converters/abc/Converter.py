import abc
import typing


class Converter(abc.ABC):
    @abc.abstractmethod
    def convert(self, event_or_parameter_to_convert: typing.Any) -> typing.Any:
        raise NotImplementedError
