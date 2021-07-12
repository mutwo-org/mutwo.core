"""Abstract bracket classes."""

import abc
import bisect
import statistics
import typing

from mutwo.events import basic
from mutwo.utilities import constants

__all__ = (
    "Bracket",
    "BracketContainer",
)

AbstractTime = typing.Any
AbstractTimeOrAbstractTimeRange = typing.Union[
    AbstractTime, typing.Tuple[AbstractTime, AbstractTime]
]


class Bracket(basic.SimultaneousEvent):
    def __init__(
        self,
        tagged_events: typing.Sequence[
            typing.Union[
                basic.TaggedSimpleEvent,
                basic.TaggedSequentialEvent,
                basic.TaggedSimultaneousEvent,
            ]
        ],
        start_or_start_range: AbstractTimeOrAbstractTimeRange,
        end_or_end_range: AbstractTimeOrAbstractTimeRange,
    ):
        super().__init__(tagged_events)
        self.start_or_start_range = start_or_start_range
        self.end_or_end_range = end_or_end_range

    @staticmethod
    def _get_mean_of_value_or_value_range(
        value_or_value_range: typing.Union[
            constants.Real, typing.Tuple[constants.Real, constants.Real]
        ],
    ) -> constants.Real:
        if isinstance(value_or_value_range, typing.Sequence):
            return statistics.mean(value_or_value_range)
        else:
            return value_or_value_range

    @property
    def start_or_start_range(self) -> AbstractTimeOrAbstractTimeRange:
        return self._start_or_start_range

    @start_or_start_range.setter
    def start_or_start_range(
        self, start_or_start_range: AbstractTimeOrAbstractTimeRange
    ):
        self._start_or_start_range = start_or_start_range

    @property
    def end_or_end_range(self) -> AbstractTimeOrAbstractTimeRange:
        return self._end_or_end_range

    @end_or_end_range.setter
    def end_or_end_range(self, end_or_end_range: AbstractTimeOrAbstractTimeRange):
        self._end_or_end_range = end_or_end_range

    @property
    @abc.abstractmethod
    def mean_start(self) -> constants.Real:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def mean_end(self) -> constants.Real:
        raise NotImplementedError


T = typing.TypeVar("T", bound=Bracket)


class BracketContainer(typing.Generic[T]):
    def __init__(self, brackets: typing.Sequence[T]):
        self._brackets = basic.SequentialEvent(
            sorted(brackets, key=lambda bracket: bracket.mean_start)
        )

    def __repr__(self) -> str:
        return "BracketContainer({})".format(tuple(self._brackets))

    def __iter__(self):
        return iter(self._brackets)

    def register(self, bracket: T):
        """Add new bracket to BracketContainer.

        :arg bracket: The bracket which shall be added.
        """

        start_of_brackets = tuple(bracket.mean_start for bracket in self._brackets)
        index = bisect.bisect_left(start_of_brackets, bracket.mean_start)
        self._brackets.insert(index, bracket)

    def filter(self, tag: str) -> typing.Tuple[T, ...]:
        """Filter and return all brackets which contain events with the requested tag

        :arg tag: The tag which shall be investigated.
        """

        filtered_brackets = []
        for bracket in self._brackets:
            for tagged_event in bracket:
                if tagged_event.tag == tag:
                    filtered_brackets.append(bracket)
                    break

        return tuple(filtered_brackets)
