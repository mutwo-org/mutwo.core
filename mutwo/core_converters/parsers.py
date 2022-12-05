"""Standardization for transformations between parameters and simple events

Adds classes to allow transformations in two directions:

1. Extract data (e.g. mutwo parameters) from simple events
2. Convert data (e.g. mutwo parameters) to simple events
"""

import typing

from mutwo import core_constants
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_utilities


__all__ = (
    "SimpleEventToAttribute",
    "MutwoParameterDict",
    "MutwoParameterDictToKeywordArgument",
    "MutwoParameterDictToDuration",
    "MutwoParameterDictToSimpleEvent",
    "UnknownObjectToObject",
)


class SimpleEventToAttribute(core_converters.abc.Converter):
    """Extract from a simple event an attribute.

    :param attribute_name: The name of the attribute which is fetched
        from a :class:`mutwo.core_events.SimpleEvent`.
    :param exception_value: This value is returned in case an `AttributeError`
        raises .
    """

    def __init__(self, attribute_name: str, exception_value: typing.Any):
        self._attribute_name = attribute_name
        self._exception_value = exception_value

    def convert(self, simple_event_to_convert: core_events.SimpleEvent) -> typing.Any:
        """Extract from a :class:`mutwo.core_events.SimpleEvent` an attribute.

        :param simple_event_to_convert: The :class:`mutwo.core_events.SimpleEvent`
            from which an attribute shall be extracted.
        :type simple_event_to_convert: mutwo.core_events.SimpleEvent

        **Example:**

        >>> from mutwo import core_converters
        >>> from mutwo import core_events
        >>> simple_event = core_events.SimpleEvent(duration=10)
        >>> simple_event_to_duration = core_converters.SimpleEventToAttribute(
        ...     'duration', 0
        ... )
        >>> simple_event_to_duration.convert(simple_event)
        DirectDuration(10)
        >>> simple_event_to_pasta = core_converters.SimpleEventToAttribute(
        ...     'pasta', 'spaghetti'
        ... )
        >>> simple_event_to_pasta.convert(simple_event)
        'spaghetti'
        >>> simple_event.pasta = 'tagliatelle'
        >>> simple_event_to_pasta.convert(simple_event)
        'tagliatelle'
        """

        return core_utilities.call_function_except_attribute_error(
            lambda simple_event: getattr(simple_event, self._attribute_name),
            simple_event_to_convert,
            self._exception_value,
        )


MutwoParameterDict = dict[str, core_constants.ParameterType]


class MutwoParameterDictToKeywordArgument(core_converters.abc.Converter):
    """Extract from a dict of mutwo parameters specific objects.

    :param mutwo_parameter_to_search_name: The parameter name which
        should be fetched from the MutwoParameterDict (if it exists).
    :type mutwo_parameter_to_search_name: str
    :param keyword: The keyword string to return. If no argument is given
        it will use the same value as :param:`mutwo_parameter_to_search_name`.
    :type keyword: typing.Optional[str]

    **Example:**

    >>> from mutwo import core_converters
    >>> from mutwo import core_parameters
    >>> mutwo_parameter_dict_to_keyword_argument = core_converters.MutwoParameterDictToKeywordArgument('duration')
    >>> mutwo_parameter_dict_to_keyword_argument.convert(
    ...     {'duration': core_parameters.DirectDuration(1)}
    ... )
    ('duration', DirectDuration(1))
    """

    def __init__(
        self, mutwo_parameter_to_search_name: str, keyword: typing.Optional[str] = None
    ):
        if keyword is None:
            keyword = str(mutwo_parameter_to_search_name)
        self._mutwo_parameter_to_search_name = mutwo_parameter_to_search_name
        self._keyword = keyword

    def convert(
        self, mutwo_parameter_dict_to_convert: MutwoParameterDict
    ) -> typing.Optional[tuple[str, core_constants.ParameterType]]:
        try:
            return (
                self._keyword,
                mutwo_parameter_dict_to_convert[self._mutwo_parameter_to_search_name],
            )
        except KeyError:
            return None


class MutwoParameterDictToDuration(MutwoParameterDictToKeywordArgument):
    """Extract from a dict of mutwo parameters the duration.

    :param duration_to_search_name: The name of the duration which shall
        be searched for in the :const:`MutwoParameterDict`. If `None` the
        value of the global constants
        :const:`mutwo.core_converters.configurations.DEFAULT_DURATION_TO_SEARCH_NAME`
        will be used. Default to `None`.
    :type duration_to_search_name: typing.Optional[str]
    :param duration_keyword_name: The name of the duration keyword for the
        event. If `None` the value of the global constants
        :const:`mutwo.core_converters.configurations.DEFAULT_DURATION_KEYWORD_NAME`
        will be used. Default to `None`.
    :type duration_keyword_name: typing.Optional[str]
        :const:`mutwo.core_converters.configurations.DEFAULT_DURATION_KEYWORD_NAME`.
    """

    def __init__(
        self,
        duration_to_search_name: typing.Optional[str] = None,
        duration_keyword_name: typing.Optional[str] = None,
    ):
        if duration_to_search_name is None:
            duration_to_search_name = (
                core_converters.configurations.DEFAULT_DURATION_TO_SEARCH_NAME
            )
        if duration_keyword_name is None:
            duration_keyword_name = (
                core_converters.configurations.DEFAULT_DURATION_KEYWORD_NAME
            )
        assert isinstance(duration_to_search_name, str)
        assert isinstance(duration_keyword_name, str)
        super().__init__(duration_to_search_name, duration_keyword_name)


class MutwoParameterDictToSimpleEvent(core_converters.abc.Converter):
    """Convert a dict of mutwo parameters to a :class:`mutwo.core_events.SimpleEvent`

    :param mutwo_parameter_dict_to_keyword_argument_sequence: A sequence of
        :class:`MutwoParameterDictToKeywordArgument`. If set to `None`
        a sequence with :class:`MutwoParameterDictToDuration` will be created.
        Default to `None`.
    :type mutwo_parameter_dict_to_keyword_argument_sequence: typing.Optional[typing.Sequence[MutwoParameterDictToKeywordArgument]]
    :param simple_event_class: Default to :class:`mutwo.core_events.SimpleEvent`.
    :type simple_event_class: typing.Type[core_events.SimpleEvent]
    """

    def __init__(
        self,
        mutwo_parameter_dict_to_keyword_argument_sequence: typing.Optional[
            typing.Sequence[MutwoParameterDictToKeywordArgument]
        ] = None,
        simple_event_class: typing.Type[
            core_events.SimpleEvent
        ] = core_events.SimpleEvent,
    ):
        if mutwo_parameter_dict_to_keyword_argument_sequence is None:
            mutwo_parameter_dict_to_keyword_argument_sequence = (
                MutwoParameterDictToDuration(),
            )
        self._mutwo_parameter_dict_to_keyword_argument_sequence = (
            mutwo_parameter_dict_to_keyword_argument_sequence
        )
        self._simple_event_class = simple_event_class

    def convert(
        self, mutwo_parameter_dict_to_convert: MutwoParameterDict
    ) -> core_events.SimpleEvent:
        keyword_argument_dict = {}
        for (
            mutwo_parameter_dict_to_keyword_argument
        ) in self._mutwo_parameter_dict_to_keyword_argument_sequence:
            keyword_argument_or_none = mutwo_parameter_dict_to_keyword_argument.convert(
                mutwo_parameter_dict_to_convert
            )
            if keyword_argument_or_none:
                keyword, argument = keyword_argument_or_none
                keyword_argument_dict.update({keyword: argument})
        return self._simple_event_class(**keyword_argument_dict)


T = typing.TypeVar("T")


class UnknownObjectToObject(core_converters.abc.Converter, typing.Generic[T]):
    """Helper to simplify standardisation of syntactic sugar.

    :param type_tuple_to_callable_dict: Define which types are converted by
        which methods.

    **Example:**

    >>> from mutwo import core_converters
    >>> anything_to_string = core_converters.UnknownObjectToObject[str](
    ...     (
    ...         ((float, int, list), str),
    ...         ((tuple,), lambda t: str(len(t))),
    ...         ([], lambda _: "..."),
    ...     )
    ... )
    >>> anything_to_string.convert(100)
    '100'
    >>> anything_to_string.convert(7.32)
    '7.32'
    >>> anything_to_string.convert((1, 2, 3))
    '3'
    >>> anything_to_string.convert(b'')
    '...'
    """

    def __init__(
        self,
        type_tuple_and_callable_tuple: tuple[tuple[typing.Type, ...], typing.Callable],
    ):
        self._type_tuple_and_callable_tuple = type_tuple_and_callable_tuple

    def convert(self, unknown_object_to_convert: typing.Any) -> T:
        # XXX: This may break in the future, because it is an implementation
        # detail.
        if isinstance(unknown_object_to_convert, typing.get_args(self.__orig_class__)):
            return unknown_object_to_convert
        for type_tuple, callable_object in self._type_tuple_and_callable_tuple:
            if type_tuple:
                if isinstance(unknown_object_to_convert, type_tuple):
                    return callable_object(unknown_object_to_convert)
            else:
                return callable_object(unknown_object_to_convert)

        raise NotImplementedError(
            f"No conversion routine defined for object '{unknown_object_to_convert}'"
            f" of type '{type(unknown_object_to_convert)}'."
        )
