"""Generic decorators that are used within :mod:`mutwo`."""

import copy
import functools
import os
import types
import typing

__all__ = ("add_copy_option", "add_tag_to_class", "compute_lazy")

from mutwo import core_utilities


F = typing.TypeVar("F", bound=typing.Callable[..., typing.Any])


def add_copy_option(function: F) -> F:
    """This decorator adds a copy option for object mutating methods.

    :arg function: The method which shall be adjusted.

    The 'add_copy_option' decorator adds the 'mutate' keyword argument
    to the decorated method. If 'mutate' is set to ``False``, the decorator deep
    copies the respective object, then applies the called method on the new
    copied object and finally returns the copied object. This can be useful
    for methods that by default mutate its object. When adding this method,
    it is up to the user whether the original object shall be changed
    and returned (for mutate=True) or if a copied version of the object with
    the respective mutation shall be returned (for mutate=False).
    """

    @functools.wraps(function)
    def wrapper(self, *args, mutate: bool = True, **kwargs) -> typing.Any:
        if mutate is True:
            function(self, *args, **kwargs)
            return self
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


def compute_lazy(
    path: str,
    force_to_compute: bool = False,
    pickle_module: typing.Optional[types.ModuleType] = None,
):
    """Cache function output to disk via pickle.

    :param path: Where to save the computed result.
    :type path: str
    :param force_to_compute: Set to ``True`` if function has to be re-computed.
    :type force_to_compute: bool
    :param pickle_module: Depending on the object which should be pickled the
        default python pickle module won't be sufficient. Therefore alternative
        third party pickle modules (with the same API) can be used. If no
        argument is provided, the function will first try to use any of the
        pickle modules given in the
        :const:`mutwo.core_utilities.configurations.PICKLE_MODULE_TO_SEARCH_TUPLE`.
        If none of the modules could be imported it will fall back to the
        buildin pickle module.
    :type pickle_module: typing.Optional[types.ModuleType]

    The decorator will only run the function if its input changes
    and otherwise load the return value from the disk.

    This function is helpful if there is a complex, long-taking calculation,
    which should only run once or from time to time if the input changes.

    **Example:**

    >>> from mutwo import core_utilities
    >>> @core_utilities.compute_lazy("magic_output", False)
    ... def my_super_complex_calculation(n_numbers):
    ...     return sum(number for number in range(n_numbers))
    >>> N_NUMBERS = 10000000
    >>> my_super_complex_calculation(N_NUMBERS)
    49999995000000
    >>> # takes very little time when calling the function the second time
    >>> my_super_complex_calculation(N_NUMBERS)
    49999995000000
    >>> # takes long again, because the input changed
    >>> my_super_complex_calculation(N_NUMBERS + 10)
    50000095000045
    """

    if pickle_module is None:
        for (
            pickle_module_name
        ) in core_utilities.configurations.PICKLE_MODULE_TO_SEARCH_TUPLE:
            try:
                pickle_module = __import__(pickle_module_name)
            except ImportError:
                pass
            else:
                break

    if pickle_module is None:
        pickle_module = __import__("pickle")

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
                    function_result, previous_args_and_kwargs = pickle_module.load(f)

                if previous_args_and_kwargs != current_args_and_kwargs:
                    has_to_compute = True

            if has_to_compute or force_to_compute:
                function_result = function_to_decorate(*args, **kwargs)
                with open(path, "wb") as f:
                    pickle_module.dump((function_result, current_args_and_kwargs), f)

            return function_result

        wrapped_function = typing.cast(F, wrapper)
        return wrapped_function

    return decorator
