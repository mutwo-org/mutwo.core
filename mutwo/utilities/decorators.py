"""Generic decorators that are used within :mod:`mutwo`."""

import copy
import functools
import typing

__all__ = ("add_return_option",)


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
