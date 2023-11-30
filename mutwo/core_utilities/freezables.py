from __future__ import annotations

import copy
import typing

from mutwo import core_utilities

__all__ = (
    "needs_liquiditiy",
    "needs_solidity",
    "freezable_property",
    "freezable_list",
    "Freezable",
    "FreezableList",
)


# mutwo defines general 'freezability' by various cooperating code bits.
# The main entry point for the user is the 'Freezable' class and the method
# decorators 'needs_solidity', 'needs_liquidity' and 'freezable_property'.
#
# The decorators are based on the private '_AttributeSwitch' class: this class
# functions by replacing the original function with a simple dummy function
# that always returns a proxy. This proxy is either mapped to the original
# function or to a drop-in function, depending on the current objects state
# (frozen or not).
#
# The mapping of this proxy happens within 'Freezable.freeze' and
# 'Freezable.defrost', so not in the actual decorators code, but in the
# 'Freezable' class code.
#
# The following table documents the proxy mappings in the frozen/unfrozen
# state for the different decorators:
#
#     frozen:
#
#       needs_solidity          =>      original function
#       needs_liquidity         =>      error
#       freezable_property      =>      cached value
#
#     unfrozen:
#
#       needs_solidity          =>      error
#       needs_liquidity         =>      original function
#       freezable_property      =>      original function
class _AttributeSwitch(object):
    def __init__(self, function):
        self.freezable_list_name = f"__{type(self).__name__}__"

        self.function = function
        self.proxy = None
        self.original_function = None
        self.__doc__ = function.__doc__
        self.instance = None

        self.name = None

    def __set_name__(self, owner, name):
        self.name = name
        self.original_function = f"_func_{name}"

        # Proxy is onto which we map either the original function, or
        # a special function in un/frozen state.
        self.proxy = f"_proxy_{name}"

        # Do the actual mapping of name to function.
        setattr(owner, self.original_function, self.function)

        # Override the special class attribute, which saves the names
        # of all special un/frozen state attributes/methods, so that
        # 'Freezable.freeze' & 'Freezable.defrost' can handle their
        # proxy assignments.
        #
        # Note that we use 'tuple' and we change the original attribute,
        # we don't use list: list can be problematic as lists between classes
        # are copies and we don't want to append methods of children to its
        # parent list, which don't exist in the parent.
        setattr(
            owner,
            self.freezable_list_name,
            getattr(owner, self.freezable_list_name)
            + ((self.proxy, self.original_function),),
        )

    def __get__(self, instance, owner=None):
        self.instance = instance
        return self

    def __set__(self, *args, **kwargs):
        raise AttributeError(f"AttributeError: can't set attribute '{self.name}'")

    def _get_proxy(self):
        return getattr(self.instance, self.proxy)


class _NeedsSpecificAggregate(_AttributeSwitch):
    def __call__(self, *args, **kwargs):
        return self._get_proxy()(*args, **kwargs)


class needs_liquiditiy(_NeedsSpecificAggregate):
    """Raise a :class:`~mutwo.core_utilities.FrozenError` if called when object is frozen.

    :param function: The method which should be decorated.
    :type function: types.MethodType

    Useful for methods which shouldn't be called if an object is frozen,
    because they'd change the internal state of the object & therefore
    contradict an objects present frozenness.
    """


class needs_solidity(_NeedsSpecificAggregate):
    """Raise a :class:`~mutwo.core_utilities.NotFrozenError` if called when object is not frozen.

    :param function: The method which should be decorated.
    :type function: types.MethodType

    Useful for methods which shouldn't be called if an object is not yet
    frozen, because they are only available if the object is frozen.
    """


class freezable_property(_AttributeSwitch):
    """Declare a property that is memorized if object is frozen.

    :param function: The method which should be decorated.
    :type function: types.MethodType

    **Example:**

    >>> from mutwo import core_utilities
    >>> class A(core_utilities.Freezable):
    ...     def __init__(self, a, b):
    ...         super().__init__()
    ...         self.a, self.b = a, b
    ...     @core_utilities.freezable_property
    ...     def c(self):
    ...         return self.a * self.b
    """

    def __get__(self, instance, owner=None):
        super().__get__(instance)
        return self._get_proxy()()


class Freezable(object):
    """Base class for objects that can switch between im/mutable states.

    Mutability of objects can help to improve the performance of some
    operations: if we only want to change one element of a very long
    array, it's more efficient to only change this one element in-place
    (mutable) instead of copying the whole array and changing only one
    element in this copy-process (immutable).

    On the other hand, some situations are inefficient if objects are
    mutable: if an object has various dynamic (= mutable) properties
    that are used to calculate a specific value, this value always
    needs to be re-calculated even if its dependencies - the dynamic
    properties - never change. In such a case - when we know we never
    need to change our dynamic properties - it's much more efficient
    to only call the computation that results in the searched value
    once and cache this value then for further usages.

    We see that in different situations mutability or immutability
    can be more efficient. In order to support both situations a
    class can inherit from :class:`mutwo.core_utilities.Freezable`.
    By default classes are mutable then, but they become immutable
    once the :meth:`mutwo.core_utilities.Freezable.freeze` method
    has been called.

    If you want to cache properties once an object is frozen,
    please use the :class:`freezable_property` decorator.

    If you want to prohibit methods to be called if an object
    is frozen, please use the :class:`needs_liquiditiy` decorator
    (its counterpart is the :class:`needs_solidity` decorator).

    **Warning:**

    Freezing isn't a safe operation: due to Pythons 'we are all
    adults here' policy, technically it's still possible to change
    the state of a 'frozen' object.

    This is the same as the behaviour of Pythons builtin ``dataclasses``
    module. Even if you decorate a class with...

        >>> import dataclasses
        >>> @dataclasses.dataclass(frozen=True)
        ... class a:
        ...     b: int

    ...it's still possible to change ``b`` of ``a`` via...

        >>> x = a(10)
        >>> object.__setattr__(x, 'b', 100)

    The same can be said of a frozen :class:`Freezable` instance.

    Furthermore classes that inherit from :class:`Freezable` need to
    collaborate to ensure a state of a frozen object can't be changed:
    for instance if your freezable object has mutable attributes, the
    attributes can still be changed after :meth:`mutwo.core_utilities.Freezable.freeze`
    has been called, unless the given class explicitly also freezes this
    attribute.

    Generally speaking :class:`mutwo.core_utilities.Freezable` tries its best
    to raise :class:`mutwo.core_utilities.FrozenError` whenever the user
    attempts to change a frozen object. This works well when sticking
    to the usual syntax and when carefully designing your custom
    classes, but magic methods or tricky class designs can still break the
    frozenness and alter the state of a frozen object.
    """

    __freezable_property__ = tuple([])
    __needs_liquiditiy__ = tuple([])
    __needs_solidity__ = tuple([])

    # Initialize frozen data when attribute can't be found
    # (e.g. when '__getattribute__' fails). In this way
    # we don't need to force all children classes to call
    # 'super().__init__()'.
    def __getattr__(self, name: str):
        try:
            super().__getattribute__('__frozen__')
        except AttributeError:
            self._defrost(init=True)
        return super().__getattribute__(name)

    def copy(self) -> Freezable:
        """Return deep-copy of object."""
        return copy.deepcopy(self)

    @needs_liquiditiy
    def freeze(self):
        """Make object immutable e.g. its internal state can't be changed anymore.

        This is useful if

            - you want to improve performance of properties that has been
              decorated with :class:`~mutwo.core_utilities.freezable_property`:
              these properties are cached and only calculated once if an object
              is frozen

            - you want to ensure no further procedure is changing this
              object anymore (you consider it as final in its given state)

        In order to unfreeze an object you can call :meth:`~mutwo.core_utilities.Freezable.defrost`.
        Unlike ``freeze`` this returns a new object and doesn't change
        the frozen object: A frozen object can never be unfrozen nor changed
        in any other way, as it becomes truly immutable.
        """
        self.__frozen__ = True

        # Proceed freezable properties:
        # calculate the current value of the function and map the
        # proxy property attribute to a function which forever
        # only return the value of the current state.
        for proxy, original_function_name in self.__freezable_property__:
            value = getattr(self, original_function_name)()

            def _():
                return value

            # 'setattr(...) isn't possible, because __setattr__
            # could already be overridden to
            # 'raise core_utilitites.FrozenError()'
            object.__setattr__(self, proxy, _)

        # Proceed liquid-only methods:
        # if we are in frozen state methods should only return error,
        # map error rising function to proxy.
        def _(*args, **kwargs):
            raise core_utilities.FrozenError()

        for proxy, original_function_name in self.__needs_liquiditiy__:
            object.__setattr__(self, proxy, _)

        # Proceed solid-only methods:
        # in frozen state they should work normally, so just map the
        # original function to the proxy.
        for proxy, original_function_name in self.__needs_solidity__:
            object.__setattr__(self, proxy, getattr(self, original_function_name))

        for _, attr in self._freezable_attribute_tuple:
            try:
                attr.freeze()
            except AttributeError:
                pass

    @needs_solidity
    def defrost(self) -> Freezable:
        """Make an unfrozen copy of the object e.g. provide a mutable copy.

        Unlike its complementary method :meth:`~mutwo.core_utilities.Freezable.freeze`,
        ``defrost`` doesn't change the object in-place, but instead returns
        a mutable copy of the object. This inconsistency to ``freeze`` exists,
        because a frozen object should never be changed e.g. be truly
        immutable [1]. On the other hand, we prefer to not-copy an object if
        possible as copying can be an expensive operation: due to this
        :meth:`~mutwo.core_utilities.Freezable.freeze` doesn't copy our
        object.

        [1] This is particularly important for freezable sequences as for
        instance lists: if a lists elements are freezable and they are frozen
        once the freezable list is frozen, the lists frozenness property
        could be broken by a single list element which would be defrosted
        in-place.
        """
        obj = self.copy()
        obj._defrost()
        return obj

    # Private helper of defrost, needed during initialization. Does all
    # the work except of copying. Should be avoided to be called anywhere
    # outside of Freezable internal methods.
    def _defrost(self, init: bool = False):
        # Proceed freezable properties & liquid-only methods:
        # simply map the proxy attribute to the original function,
        # which is dynamically calculated.
        for proxy, original_function_name in (
            self.__freezable_property__ + self.__needs_liquiditiy__
        ):
            object.__setattr__(self, proxy, getattr(self, original_function_name))

        # Proceed solid-only methods:
        # if we are in unfrozen state methods should only return error,
        # map error rising function to proxy.
        def _(*args, **kwargs):
            raise core_utilities.NotFrozenError()

        for proxy, original_function_name in self.__needs_solidity__:
            object.__setattr__(self, proxy, _)

        # Order matters! First reset attributes to be settable again,
        # before we can use the normal 'setattr' syntax again.
        self.__frozen__ = False

        # Initially attributes should already be mutable, we shouldn't
        # need to defrost them: save CPU by avoiding deep-copy.
        if init:
            return

        for attr_name, attr in self._freezable_attribute_tuple:
            try:
                v = attr.defrost()
            except AttributeError:
                pass
            else:
                setattr(self, attr_name, v)

    @property
    def is_frozen(self) -> bool:
        """``True`` if frozen and otherwise ``False``."""
        return self.__frozen__

    @needs_liquiditiy
    def __setattr__(self, *args, **kwargs):
        return object.__setattr__(self, *args, **kwargs)

    @property
    def _freezable_attribute_tuple(self) -> tuple[str, ...]:
        # Collect all attributes of the class which may be freezable.
        return tuple((n, getattr(self, n)) for n in dir(self) if not n.startswith("_"))


# To freeze lists, we use a decorator and not inheritance. In this way it's
# possible to have complex inheritance structures without breaking them, e.g.
#
#   Freezable   =>  Event   =>
#                               SimpleEvent
#                   list    =>  ComplexEvent
#
# So ComplexEvent inherits from both, Freezable and list. But it would be
# prohibited if it would inherit from "FreezableList" and "Event". A workaround
# for this problem is to offer the freezable list property via a decorator.
def freezable_list(*ignored_method):
    """Make a list inherited class freezable.

    :param *ignored_method: This decorator overrides methods of the list type.
        In case the user defines her/his/* own method in order to override an
        inherited list method, this user defined method may be overridden by
        this decorator. In order to avoid this the user can specify all method
        names which shouldn't be overridden. This function overrides:
        __setitem__, __delitem__, sort, clear, insert, extend, append, remove,
        pop, sort, reverse, freeze, defrost.

    Your class needs to inherit from :class:`mutwo.core_utilities.Freezable`
    and :class:`list`.

    **Example**:

    >>> from mutwo import core_utilities
    >>> @core_utilities.freezable_list()
    ... class MyFreezableList(core_utilities.Freezable, list):
    ...     def __init__(self, *args, **kwargs):
    ...         list.__init__(self, *args, **kwargs)
    ...         core_utilities.Freezable.__init__(self)
    >>> fl = MyFreezableList([1, 2, 3])
    >>> fl.append(10)
    >>> fl.freeze()
    >>> fl.append(20)
    Traceback (most recent call last):
      ...
    mutwo.core_utilities.exceptions.FrozenError: Can't mutate frozen object.
    >>> defrost_fl = fl.defrost()
    >>> defrost_fl.append(20)
    >>> defrost_fl != fl
    True
    """
    return lambda cls: _freezable_list(cls, *ignored_method)


def _freezable_list(cls, *ignored_method):
    for m in (
        "__setitem__",
        "__delitem__",
        "sort",
        "clear",
        "insert",
        "extend",
        "append",
        "remove",
        "pop",
        "sort",
        "reverse",
    ):
        if m not in ignored_method:
            # Note: Needs to be called in extra method, otherwise
            # 'm' is for all functions 'reverse', because it's the
            # last value the local variable 'm' has.
            _setm(cls, m)

    def freeze(self):
        super(cls, self).freeze()
        for e in self:
            try:
                e.freeze()
            except AttributeError:
                pass

    def defrost(self):
        # XXX: This is very unefficient & unsafe for multi-threaded
        # applications.
        self._defrost()
        for e in self:
            try:
                e._defrost()
            except AttributeError:
                pass

        obj = self.copy()
        self.freeze()
        return obj

    if freeze.__name__ not in ignored_method:
        cls.freeze = freeze
    if defrost.__name__ not in ignored_method:
        cls.defrost = defrost
    return cls


def _setm(cls, m: str):
    @needs_liquiditiy
    def _(self, *args, **kwargs):
        # Note: we load parent method, instead of using the class
        # original method, because deepcopy becomes much more expensive
        # and slow if we use the original class method.
        return getattr(super(cls, self), m)(*args, **kwargs)

    _.__set_name__(cls, m)
    setattr(cls, m, _)


T = typing.TypeVar("T", bound=Freezable)


@freezable_list()
class FreezableList(Freezable, list[T], typing.Generic[T]):
    """A list that's freezable."""

    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        Freezable.__init__(self)
