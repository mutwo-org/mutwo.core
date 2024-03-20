# This file is part of mutwo, ecosystem for time-based arts.
#
# Copyright (C) 2020-2023
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Standardization for transformations between parameters and chronons

Adds classes to allow transformations in two directions:

1. Extract data (e.g. mutwo parameters) from chronons
2. Convert data (e.g. mutwo parameters) to chronons
"""

import typing

from mutwo import core_converters
from mutwo import core_events
from mutwo import core_utilities


__all__ = (
    "ChrononToAttribute",
    "MutwoParameterDict",
    "MutwoParameterDictToKeywordArgument",
    "MutwoParameterDictToDuration",
    "MutwoParameterDictToChronon",
)


class ChrononToAttribute(core_converters.abc.Converter):
    """Extract from a chronon an attribute.

    :param attribute_name: The name of the attribute which is fetched
        from a :class:`mutwo.core_events.Chronon`.
    :param exception_value: This value is returned in case an `AttributeError`
        raises .
    """

    def __init__(self, attribute_name: str, exception_value: typing.Any):
        self._attribute_name = attribute_name
        self._exception_value = exception_value

    def convert(self, chronon_to_convert: core_events.Chronon) -> typing.Any:
        """Extract from a :class:`mutwo.core_events.Chronon` an attribute.

        :param chronon_to_convert: The :class:`mutwo.core_events.Chronon`
            from which an attribute shall be extracted.
        :type chronon_to_convert: mutwo.core_events.Chronon

        **Example:**

        >>> from mutwo import core_converters
        >>> from mutwo import core_events
        >>> chronon = core_events.Chronon(duration=10.0)
        >>> chronon_to_duration = core_converters.ChrononToAttribute(
        ...     'duration', 0
        ... )
        >>> chronon_to_duration.convert(chronon)
        DirectDuration(10.0)
        >>> chronon_to_pasta = core_converters.ChrononToAttribute(
        ...     'pasta', 'spaghetti'
        ... )
        >>> chronon_to_pasta.convert(chronon)
        'spaghetti'
        >>> chronon.pasta = 'tagliatelle'
        >>> chronon_to_pasta.convert(chronon)
        'tagliatelle'
        """

        return core_utilities.call_function_except_attribute_error(
            lambda chronon: getattr(chronon, self._attribute_name),
            chronon_to_convert,
            self._exception_value,
        )


MutwoParameterDict: typing.TypeAlias = dict[str, typing.Any]


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
    ...     {'duration': core_parameters.DirectDuration(1.0)}
    ... )
    ('duration', DirectDuration(1.0))
    """

    def __init__(
        self, mutwo_parameter_to_search_name: str, keyword: typing.Optional[str] = None
    ):
        self._mutwo_parameter_to_search_name = mutwo_parameter_to_search_name
        self._keyword = keyword or str(mutwo_parameter_to_search_name)

    def convert(
        self, mutwo_parameter_dict_to_convert: MutwoParameterDict
    ) -> typing.Optional[tuple[str, typing.Any]]:
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
        super().__init__(
            duration_to_search_name
            or core_converters.configurations.DEFAULT_DURATION_TO_SEARCH_NAME,
            duration_keyword_name
            or core_converters.configurations.DEFAULT_DURATION_KEYWORD_NAME,
        )


class MutwoParameterDictToChronon(core_converters.abc.Converter):
    """Convert a dict of mutwo parameters to a :class:`mutwo.core_events.Chronon`

    :param mutwo_parameter_dict_to_keyword_argument_sequence: A sequence of
        :class:`MutwoParameterDictToKeywordArgument`. If set to `None`
        a sequence with :class:`MutwoParameterDictToDuration` will be created.
        Default to `None`.
    :type mutwo_parameter_dict_to_keyword_argument_sequence: typing.Optional[typing.Sequence[MutwoParameterDictToKeywordArgument]]
    :param chronon_class: Default to :class:`mutwo.core_events.Chronon`.
    :type chronon_class: typing.Type[core_events.Chronon]
    """

    def __init__(
        self,
        mutwo_parameter_dict_to_keyword_argument_sequence: typing.Optional[
            typing.Sequence[MutwoParameterDictToKeywordArgument]
        ] = None,
        chronon_class: typing.Type[core_events.Chronon] = core_events.Chronon,
    ):
        self._mutwo_parameter_dict_to_keyword_argument_sequence = (
            mutwo_parameter_dict_to_keyword_argument_sequence
            or (MutwoParameterDictToDuration(),)
        )
        self._chronon_class = chronon_class

    def convert(
        self, mutwo_parameter_dict_to_convert: MutwoParameterDict
    ) -> core_events.Chronon:
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
        return self._chronon_class(**keyword_argument_dict)


T = typing.TypeVar("T")
