"""Defining the public api for any converter class."""

import abc
import typing

__all__ = ("Converter",)


class Converter(abc.ABC):
    """Abstract base class for all Converter classes.

    Converter classes are defined as classes that convert data between
    two different encodings. Their only public method (besides initialisation)
    should be a `convert` method that has exactly one argument (the data that
    should be converted).
    """

    @abc.abstractmethod
    def convert(self, event_or_parameter_or_file_to_convert: typing.Any) -> typing.Any:
        raise NotImplementedError
