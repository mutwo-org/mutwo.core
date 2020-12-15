import copy
import functools
import typing


def add_return_option(function: typing.Callable) -> typing.Callable:
    @functools.wraps(function)
    def wrapper(self, *args, mutate: bool = True, **kwargs) -> typing.Any:
        if mutate is True:
            function(self, *args, **kwargs)
        else:
            deep_copied_object = copy.deepcopy(self)
            function(deep_copied_object, *args, **kwargs)
            return deep_copied_object

    return wrapper
