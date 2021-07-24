"""Generic decorators that are used within :mod:`mutwo`."""

import copy
import functools
import os
import typing

try:
    import dill as pickle
except ImportError:
    import pickle

__all__ = ("add_return_option", "compute_lazy")


F = typing.TypeVar("F", bound=typing.Callable[..., typing.Any])


def add_return_option(function: F) -> F:
    """This decorator adds a return option for object mutating methods.

    The 'add_return_option' decorator adds the 'mutate' keyword argument
    to the decorated method. If 'mutate' is set to False, the decorator deep
    copies the respective object, then applies the called method on the new
    copied object and finally returns the copied object. This can be useful
    for methods that by default mutate its object. When adding this method,
    it is up to the user whether the original object shall be changed
    (for mutate=True) or if a copied version of the object with the
    respective mutation shall be returned (for mutate=False).
    """

    @functools.wraps(function)
    def wrapper(self, *args, mutate: bool = True, **kwargs) -> typing.Any:
        if mutate is True:
            function(self, *args, **kwargs)
        else:
            deep_copied_object = copy.deepcopy(self)
            function(deep_copied_object, *args, **kwargs)
            return deep_copied_object

    wrapped_function = typing.cast(F, wrapper)
    wrapped_function.__annotations__.update({"mutate": bool})
    return wrapped_function


G = typing.TypeVar("G")


def add_tag_to_class(class_to_decorate: G) -> G:
    """This decorator adds a 'tag' argument to the init method of a class.

    :arg class_to_decorate: The class which shall be decorated.
    """

    init = class_to_decorate.__init__

    def init_with_tag(self, *args, tag: typing.Optional[str] = None, **kwargs):
        init(self, *args, **kwargs)
        self.tag = tag

    class_to_decorate.__init__ = init_with_tag
    return class_to_decorate


def compute_lazy(path: str, force_to_compute: bool = False):
    """Only run function if its input changes and otherwise load return value from disk.

    :param path: Where to save the computed result.
    :type path: str
    :param force_to_compute: Set to ``True`` if function has to be re-computed.
    :type force_to_compute: bool

    This function is helpful if there is a complex, long-taking calculation,
    which should only run once or from time to time if the input changes.

    **Example:**

    >>> from mutwo.utilities import decorators
    >>> @decorators.compute_lazy("magic_output", False)
        def my_super_complex_calculation(n_numbers):
            return sum(number for number in range(n_numbers))
    >>> N_NUMBERS = 100000000
    >>> my_super_complex_calculation(N_NUMBERS)
    4999999950000000
    >>> # takes very little time when calling the function the second time
    >>> my_super_complex_calculation(N_NUMBERS)
    4999999950000000
    >>> # takes long again, because the input changed
    >>> my_super_complex_calculation(N_NUMBERS + 10)
    4999999950000000
    """

    def decorator(function_to_decorate: F) -> F:
        @functools.wraps(function_to_decorate)
        def wrapper(*args, **kwargs) -> typing.Any:
            has_to_compute = False

            current_args_and_kwargs = (args, kwargs)
            is_file = os.path.isfile(path)

            if not is_file:
                has_to_compute = True
            else:
                with open(path, "rb") as f:
                    function_result, previous_args_and_kwargs = pickle.load(f)

                if previous_args_and_kwargs != current_args_and_kwargs:
                    has_to_compute = True

            if has_to_compute or force_to_compute:
                function_result = function_to_decorate(*args, **kwargs)
                with open(path, "wb") as f:
                    pickle.dump((function_result, current_args_and_kwargs), f)

            return function_result

        wrapped_function = typing.cast(F, wrapper)
        return wrapped_function

    return decorator
