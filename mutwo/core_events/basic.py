# This file is part of mutwo, ecosystem for time-based arts.
#
# Copyright (C) 2020-2024
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

"""Generic event classes which can be used in multiple contexts.

The different events differ in their timing structure and whether they
are nested or not:
"""

from __future__ import annotations

import bisect
import functools
import operator
import types
import typing

import ranges

from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities


__all__ = ("Chronon", "Consecution", "Concurrence")


class Chronon(core_events.abc.Event):
    """A :class:`Chronon` is an event that cannot be further subdivided (a leaf of a tree).

    :param duration: The duration of the ``Chronon``. Mutwo converts
        the incoming object to a :class:`mutwo.core_parameters.abc.Duration` object
        with the global `core_parameters.abc.Duration.from_any`
        callable.
    :param *args: Arguments parsed to :class:`mutwo.core_events.abc.Event`.
    :param **kwargs: Keyword arguments parsed to :class:`mutwo.core_events.abc.Event`.

    **Example:**

    >>> from mutwo import core_events
    >>> chronon = core_events.Chronon(2)
    >>> chronon
    Chronon(duration=DirectDuration(2.0))
    >>> print(chronon)  # pretty print for debugging
    C(dur=D(2.0))
    """

    parameter_to_exclude_from_representation_tuple = ("tempo", "tag")

    def __init__(self, duration: core_parameters.abc.Duration.Type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.duration = duration

    # ###################################################################### #
    #                           magic methods                                #
    # ###################################################################### #

    def __eq__(self, other: typing.Any) -> bool:
        """Test for checking if two objects are equal."""
        try:
            parameter_to_compare_set = set([])
            for object_ in (self, other):
                for parameter_to_compare in object_._parameter_to_compare_tuple:
                    parameter_to_compare_set.add(parameter_to_compare)
        except AttributeError:
            return False
        return core_utilities.test_if_objects_are_equal_by_parameter_tuple(
            self, other, tuple(parameter_to_compare_set)
        )

    def __repr_content__(self) -> str:
        return ", ".join([f"{attr}={repr(v)}" for attr, v in self._print_data.items()])

    def __str_content__(self) -> str:
        return ", ".join(
            [f"{attr[:3]}={str(v)}" for attr, v in self._print_data.items()]
        )

    # ###################################################################### #
    #                           private methods                              #
    # ###################################################################### #

    def _set_parameter(
        self,
        parameter_name: str,
        object_or_function: typing.Callable[[typing.Any], typing.Any] | typing.Any,
        set_unassigned_parameter: bool,
        id_set: set[int],
    ) -> Chronon:
        old_parameter = self.get_parameter(parameter_name)
        if set_unassigned_parameter or old_parameter is not None:
            if hasattr(object_or_function, "__call__"):
                new_parameter = object_or_function(old_parameter)
            else:
                new_parameter = object_or_function
            setattr(self, parameter_name, new_parameter)
        return self

    def _mutate_parameter(
        self,
        parameter_name: str,
        function: typing.Callable[[typing.Any], None] | typing.Any,
        id_set: set[int],
    ) -> Chronon:
        if (p := self.get_parameter(parameter_name)) is not None:
            function(p)
        return self

    # ###################################################################### #
    #                           properties                                   #
    # ###################################################################### #

    @property
    def _parameter_to_print_tuple(self) -> tuple[str, ...]:
        """Return tuple of attribute names which shall be printed for repr."""
        # Avoid printing too verbose parameters.
        return tuple(
            filter(
                lambda attribute: attribute
                not in self.parameter_to_exclude_from_representation_tuple,
                self._parameter_to_compare_tuple,
            )
        )

    @property
    def _print_data(self) -> dict[str, typing.Any]:
        return {attr: getattr(self, attr) for attr in self._parameter_to_print_tuple}

    @property
    def _parameter_to_compare_tuple(self) -> tuple[str, ...]:
        """Return tuple of attribute names which values define the :class:`Chronon`.

        The returned attribute names are used for equality check between two
        :class:`Chronon` objects.
        """
        return tuple(
            attribute
            for attribute in dir(self)
            # We have to use 'and' (lazy evaluation) instead of
            #      'all', to avoid redundant checks!
            #
            # no private attributes
            if attribute[0] != "_"
            # no redundant comparisons
            and attribute not in ("parameter_to_exclude_from_representation_tuple",)
            # no methods
            and not isinstance(getattr(self, attribute), types.MethodType)
        )

    @property
    def duration(self) -> core_parameters.abc.Duration:
        return self._duration

    @duration.setter
    def duration(self, duration: core_parameters.abc.Duration.Type):
        self._duration = core_parameters.abc.Duration.from_any(duration)

    # ###################################################################### #
    #                           public methods                               #
    # ###################################################################### #

    def destructive_copy(self) -> Chronon:
        return self.copy()

    def get_parameter(
        self, parameter_name: str, flat: bool = False, filter_undefined: bool = False
    ) -> typing.Any:
        return getattr(self, parameter_name, None)

    # Update docstring
    def set_parameter(  # type: ignore
        self,
        *args,
        **kwargs,
    ) -> Chronon:
        """Sets event parameter to new value.

        :param parameter_name: The name of the parameter which values shall be changed.
        :param object_or_function: For setting the parameter either a new value can be
            passed directly or a function can be passed. The function gets as an
            argument the previous value that has had been assigned to the respective
            object and has to return a new value that is assigned to the object.
        :param set_unassigned_parameter: If set to ``False`` a new parameter is only
            assigned to an Event if the Event already has a attribute with the
            respective `parameter_name`. If the Event doesn't know the attribute yet
            and `set_unassigned_parameter` is False, the method call is simply
            ignored.

        **Example:**

        >>> from mutwo import core_events
        >>> chronon = core_events.Chronon(2)
        >>> chronon.set_parameter(
        ...     'duration', lambda old_duration: old_duration * 2
        ... )
        Chronon(duration=DirectDuration(4.0))
        >>> chronon.duration
        DirectDuration(4.0)
        >>> chronon.set_parameter('duration', 3)
        Chronon(duration=DirectDuration(3.0))
        >>> chronon.duration
        DirectDuration(3.0)
        >>> chronon.set_parameter(
        ...     'unknown_parameter', 10, set_unassigned_parameter=False
        ... )  # this will be ignored
        Chronon(duration=DirectDuration(3.0))
        >>> chronon.unknown_parameter
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        AttributeError: 'Chronon' object has no attribute 'unknown_parameter'
        >>> chronon.set_parameter(
        ...     'unknown_parameter', 10, set_unassigned_parameter=True
        ... )  # this will be written
        Chronon(duration=DirectDuration(3.0), unknown_parameter=10)
        >>> chronon.unknown_parameter
        10
        """
        return super().set_parameter(*args, **kwargs)

    def metrize(self) -> Chronon:
        metrized_event = self._event_to_metrized_event(self)
        self.duration = metrized_event.duration
        self.tempo = metrized_event.tempo
        return self

    def cut_out(  # type: ignore
        self,
        start: core_parameters.abc.Duration.Type,
        end: core_parameters.abc.Duration.Type,
    ) -> Chronon:
        start, end = (core_parameters.abc.Duration.from_any(o) for o in (start, end))
        self._assert_valid_absolute_time(start)
        self._assert_correct_start_and_end_values(
            start, end, condition=lambda start, end: start < end
        )

        dur = self.duration
        diff: core_parameters.DirectDuration = core_parameters.DirectDuration(0)

        if start > 0:
            diff += start
        if end < dur:
            diff += dur - end
        if diff >= dur:
            raise core_utilities.InvalidCutOutStartAndEndValuesError(
                start, end, self, dur
            )

        self.duration -= diff
        return self

    def cut_off(  # type: ignore
        self,
        start: core_parameters.abc.Duration.Type,
        end: core_parameters.abc.Duration.Type,
    ) -> Chronon:
        start, end = (core_parameters.abc.Duration.from_any(o) for o in (start, end))

        self._assert_valid_absolute_time(start)
        self._assert_correct_start_and_end_values(start, end)

        duration = self.duration
        if start < duration:
            if end > duration:
                end = duration
            self.duration -= end - start
        return self


T = typing.TypeVar("T", bound=core_events.abc.Event)


class Consecution(core_events.abc.Compound, typing.Generic[T]):
    """A :class:`Consecution`hosts events that take place one after the other."""

    # ###################################################################### #
    #                           magic methods                                #
    # ###################################################################### #

    def __add__(self, event: list[T]) -> Consecution[T]:
        e = self.copy()
        e._concatenate_tempo(event)
        e.extend(event)
        return e

    # ###################################################################### #
    #                    private static methods                              #
    # ###################################################################### #

    @staticmethod
    def _get_index_at_from_absolute_time_tuple(
        abst: float,
        abst_tuple: float,
        duration: float,
    ) -> typing.Optional[int]:
        if abst < duration and abst >= 0:
            return bisect.bisect_right(abst_tuple, abst) - 1
        else:
            return None

    # ###################################################################### #
    #                        private  methods                                #
    # ###################################################################### #

    # We need to have a private "_cut_off" method to simplify
    # overriding the public "cut_off" method in children classes
    # of Consecution. This is necessary, because the implementation
    # of "squash_in" makes use of "_cut_off". In this way it is possible
    # to adjust the meaning of the public "cut_off" method, without
    # having to change the meaning of "squash_in" (this happens for instance
    # in the mutwo.core_events.Envelope class).
    def _cut_off(
        self,
        start: core_parameters.abc.Duration,
        end: core_parameters.abc.Duration,
        cut_off_duration: typing.Optional[core_parameters.abc.Duration] = None,
    ) -> Consecution[T]:
        if cut_off_duration is None:
            cut_off_duration = end - start
        # Collect events which are only active within the cut_off - range
        event_to_delete_list = []
        abst_tuple = self.absolute_time_tuple
        for i, t0, t1, e in zip(
            range(len(self)), abst_tuple, abst_tuple[1:] + (None,), self
        ):
            if t1 is None:
                t1 = t0 + e.duration
            if t0 >= start and t1 <= end:
                event_to_delete_list.append(i)
            # Shorten event which are partly active within the
            # cut_off - range
            elif t0 <= start and t1 >= start:
                diff = start - t0
                e.cut_off(diff, diff + cut_off_duration)
            elif t0 < end and t1 > end:
                diff = t0 - start
                e.cut_off(0, cut_off_duration - diff)
        for i in reversed(event_to_delete_list):
            del self[i]
        return self

    def _split_child_at(
        self,
        absolute_time: core_parameters.abc.Duration.Type,
        abstf_tuple: tuple[float, ...],
        durf: float,
    ) -> int:
        absolute_time = core_parameters.abc.Duration.from_any(absolute_time)
        self._assert_valid_absolute_time(absolute_time)
        abstf = absolute_time.beat_count

        event_index = Consecution._get_index_at_from_absolute_time_tuple(
            abstf, abstf_tuple, durf
        )

        # If there is no event at the requested time, raise error
        if event_index is None:
            raise core_utilities.SplitUnavailableChildError(absolute_time)

        # Only try to split child event at the requested time if there isn't
        # a segregation already anyway
        elif abstf != abstf_tuple[event_index]:
            try:
                end = abstf_tuple[event_index + 1]
            except IndexError:
                end = durf

            difference = end - abstf
            split_event = self[event_index].split_at(difference)
            split_event_count = len(split_event)
            match split_event_count:
                case 1:
                    pass
                case 2:
                    self[event_index] = split_event[0]
                    self.insert(event_index, split_event[1])
                case _:
                    raise RuntimeError("Unexpected event count!")

            return event_index + 1
        return event_index

    # ###################################################################### #
    #                        private   properties                            #
    # ###################################################################### #

    @property
    def _abst_tuple_and_dur(
        self,
    ) -> [tuple[core_parameters.abc.Duration, ...], core_parameters.abc.Duration]:
        """Return start time for each event and the end time of the last event.

        This property helps to improve performance of various functions
        which uses duration and absolute_time_tuple attribute.
        """
        d_iter = (e.duration for e in self)
        abst_tuple = tuple(
            core_utilities.accumulate_from_n(d_iter, core_parameters.DirectDuration(0))
        )
        return abst_tuple[:-1], abst_tuple[-1]

    @property
    def _abstf_tuple_and_dur(
        self,
    ) -> tuple[tuple[float, ...], float]:
        """Return start time for each event and the end time of the last event.

        This property helps to improve performance of various functions
        which uses duration and absolute_time_tuple attribute.
        """
        d_iter = (e.duration.beat_count for e in self)
        abstf_tuple = tuple(
            # We need to round each duration again after accumulation,
            # because floats were summed which could lead to
            # potential floating point errors again, which will
            # lead to bad errors later (for instance in
            # core_utilities.scale).
            map(
                lambda d: core_utilities.round_floats(
                    d,
                    core_parameters.configurations.ROUND_DURATION_TO_N_DIGITS,
                ),
                core_utilities.accumulate_from_n(d_iter, 0),
            )
        )
        return abstf_tuple[:-1], abstf_tuple[-1]

    # ###################################################################### #
    #                           properties                                   #
    # ###################################################################### #

    @core_events.abc.Compound.duration.getter
    def duration(self) -> core_parameters.abc.Duration:
        try:
            return functools.reduce(operator.add, (e.duration for e in self))
        # If Consecution is empty
        except TypeError:
            return core_parameters.DirectDuration(0)

    @property
    def absolute_time_tuple(self) -> tuple[core_parameters.abc.Duration, ...]:
        """Return start time as :class:`core_parameters.abc.Duration` for each event."""
        return self._abst_tuple_and_dur[0]

    @property
    def absolute_time_in_floats_tuple(self) -> tuple[float, ...]:
        """Return start time as `float` for each event."""
        return self._abstf_tuple_and_dur[0]

    @property
    def start_and_end_time_per_event(
        self,
    ) -> tuple[ranges.Range, ...]:
        """Return start and end time for each event."""
        d_iter = (e.duration for e in self)
        abst_tuple = tuple(
            core_utilities.accumulate_from_n(d_iter, core_parameters.DirectDuration(0))
        )
        return tuple(ranges.Range(*t) for t in zip(abst_tuple, abst_tuple[1:]))

    # ###################################################################### #
    #                           public methods                               #
    # ###################################################################### #

    def get_event_index_at(
        self, absolute_time: core_parameters.abc.Duration.Type
    ) -> typing.Optional[int]:
        """Get index of event which is active at the passed absolute_time.

        :param absolute_time: The absolute time where the method shall search
            for the active event.
        :type absolute_time: core_parameters.abc.Duration.Type
        :return: Index of event if there is any event at the requested absolute time
            and ``None`` if there isn't any event.

        **Example:**

        >>> from mutwo import core_events
        >>> consecution = core_events.Consecution([core_events.Chronon(2), core_events.Chronon(3)])
        >>> consecution.get_event_index_at(1)
        0
        >>> consecution.get_event_index_at(3)
        1
        >>> consecution.get_event_index_at(100)

        **Warning:**

        This method ignores events with duration == 0.
        """
        abstf = core_parameters.abc.Duration.from_any(absolute_time).beat_count
        abstf_tuple, durf = self._abstf_tuple_and_dur
        return Consecution._get_index_at_from_absolute_time_tuple(
            abstf, abstf_tuple, durf
        )

    def get_event_at(
        self, absolute_time: core_parameters.abc.Duration.Type
    ) -> typing.Optional[T]:
        """Get event which is active at the passed absolute_time.

        :param absolute_time: The absolute time where the method shall search
            for the active event.
        :type absolute_time: core_parameters.abc.Duration.Type
        :return: Event if there is any event at the requested absolute time
            and ``None`` if there isn't any event.

        **Example:**

        >>> from mutwo import core_events
        >>> consecution = core_events.Consecution([core_events.Chronon(2), core_events.Chronon(3)])
        >>> consecution.get_event_at(1)
        Chronon(duration=DirectDuration(2.0))
        >>> consecution.get_event_at(3)
        Chronon(duration=DirectDuration(3.0))
        >>> consecution.get_event_at(100)

        **Warning:**

        This method ignores events with duration == 0.
        """
        event_index = self.get_event_index_at(absolute_time)
        if event_index is None:
            return None
        return self[event_index]  # type: ignore

    def cut_out(  # type: ignore
        self,
        start: core_parameters.abc.Duration.Type,
        end: core_parameters.abc.Duration.Type,
    ) -> Consecution[T]:
        start, end = (core_parameters.abc.Duration.from_any(o) for o in (start, end))
        self._assert_valid_absolute_time(start)
        self._assert_correct_start_and_end_values(start, end)

        event_to_remove_index_list = []
        for i, t0, e in zip(range(len(self)), self.absolute_time_tuple, self):
            event_duration = e.duration
            t1 = t0 + event_duration
            cut_out_start: core_parameters.DirectDuration = (
                core_parameters.DirectDuration(0)
            )
            cut_out_end = event_duration
            if t0 < start:
                cut_out_start += start - t0
            if t1 > end:
                cut_out_end -= t1 - end
            if cut_out_start < cut_out_end:
                e.cut_out(cut_out_start, cut_out_end)
            elif not (
                # Support special case of events with duration = 0.
                e.duration == 0
                and t0 >= start
                and t0 <= end
            ):
                event_to_remove_index_list.append(i)

        for event_to_remove_index in reversed(event_to_remove_index_list):
            del self[event_to_remove_index]
        return self

    def cut_off(  # type: ignore
        self,
        start: core_parameters.abc.Duration.Type,
        end: core_parameters.abc.Duration.Type,
    ) -> Consecution[T]:
        start, end = (core_parameters.abc.Duration.from_any(o) for o in (start, end))
        self._assert_valid_absolute_time(start)
        cut_off_duration = end - start
        # Avoid unnecessary iterations
        if cut_off_duration > 0:
            return self._cut_off(start, end, cut_off_duration)
        return self

    def squash_in(  # type: ignore
        self,
        start: core_parameters.abc.Duration.Type,
        event_to_squash_in: core_events.abc.Event,
    ) -> Consecution[T]:
        start = core_parameters.abc.Duration.from_any(start)
        self._assert_valid_absolute_time(start)
        start_in_floats = start.beat_count
        self._assert_start_in_range(start_in_floats)

        # Only run cut_off if necessary -> Improve performance
        if (event_to_squash_in_duration := event_to_squash_in.duration) > 0:
            cut_off_end = start + event_to_squash_in_duration
            self._cut_off(start, cut_off_end, event_to_squash_in_duration)

        # We already know that the given start is within the
        # range of the event. This means that if the start
        # is bigger than the duration, it is only due to a
        # floating point rounding error. To avoid odd bugs
        # we therefore have to define the bigger-equal
        # relationship.
        abstf_tuple, durf = self._abstf_tuple_and_dur
        if start_in_floats >= durf:
            self.append(event_to_squash_in)
        else:
            try:
                insert_index = abstf_tuple.index(start)
            # There is an event on the given point which need to be
            # split.
            except ValueError:
                active_event_index = Consecution._get_index_at_from_absolute_time_tuple(
                    start_in_floats,
                    abstf_tuple,
                    durf,
                )
                split_position = start_in_floats - abstf_tuple[active_event_index]
                if (
                    split_position > 0
                    and split_position < self[active_event_index].duration
                ):
                    split_active_event = self[active_event_index].split_at(
                        split_position
                    )
                    self[active_event_index] = split_active_event[1]
                    self.insert(active_event_index, split_active_event[0])
                    active_event_index += 1

                insert_index = active_event_index

            self.insert(insert_index, event_to_squash_in)
        return self

    def slide_in(
        self,
        start: core_parameters.abc.Duration.Type,
        event_to_slide_in: core_events.abc.Event,
    ) -> Consecution[T]:
        start = core_parameters.abc.Duration.from_any(start)
        self._assert_valid_absolute_time(start)
        start_in_floats = start.beat_count
        if start_in_floats == 0:
            self.insert(0, event_to_slide_in)
            return self
        self._assert_start_in_range(start_in_floats)
        try:
            self[:], b = self.split_at(start)
        except ValueError:  # Only one event => start == duration.
            self.append(event_to_slide_in)
        else:
            self.extend([event_to_slide_in] + b)
        return self

    def split_child_at(
        self, absolute_time: core_parameters.abc.Duration.Type
    ) -> Consecution[T]:
        abstf_tuple, durf = self._abstf_tuple_and_dur
        self._split_child_at(absolute_time, abstf_tuple, durf)
        return self

    def split_at(
        self,
        *absolute_time: core_parameters.abc.Duration.Type,
        ignore_invalid_split_point: bool = False,
    ) -> tuple[Consecution, ...]:
        if not absolute_time:
            raise core_utilities.NoSplitTimeError()

        split_abstf_list = [
            core_parameters.abc.Duration.from_any(t).beat_count for t in absolute_time
        ]

        abstf_tuple, durf = self._abstf_tuple_and_dur
        abstf_list = list(abstf_tuple)
        c = self.copy()

        index_list = []
        is_first = True
        for t in sorted(split_abstf_list):
            if is_first:  # First is smallest, check if t < 0
                self._assert_valid_absolute_time(t)
                is_first = False
            # Improve performance: don't try to split if we know it is
            # already split here. We also need to be sure to not
            # add any duplicates to 'absolute_time_list', so we need
            # to check anyway.
            if t in abstf_list:
                index_list.append(abstf_list.index(t))
                continue
            # It's okay to ignore, this is still within the given event
            # (if we don't continue 'split_child_at' raises an error).
            if t == durf:
                continue
            try:
                i = c._split_child_at(t, tuple(abstf_list), durf)
            except core_utilities.SplitUnavailableChildError:
                if not ignore_invalid_split_point:
                    raise core_utilities.SplitError(t)
                # We can stop, because if there isn't any child at this time
                # there won't be any child at a later time (remember: our
                # absolute times are sorted).
                break
            index_list.append(i)
            abstf_list.append(t)
            abstf_list.sort()

        # Add frame indices (if not already present)
        if 0 not in index_list:
            index_list.insert(0, 0)

        if (event_count := len(c)) not in index_list:
            index_list.append(event_count)

        return tuple(c[i0:i1] for i0, i1 in zip(index_list, index_list[1:]))

    def extend_until(
        self,
        duration: core_parameters.abc.Duration.Type,
        duration_to_white_space: typing.Optional[
            typing.Callable[[core_parameters.abc.Duration], core_events.abc.Event]
        ] = None,
        prolong_chronon: bool = True,
    ) -> Consecution[T]:
        duration = core_parameters.abc.Duration.from_any(duration)
        duration_to_white_space = (
            duration_to_white_space
            or core_events.configurations.DEFAULT_DURATION_TO_WHITE_SPACE
        )
        if (difference := duration - self.duration) > 0:
            self.append(duration_to_white_space(difference))
        return self


class Concurrence(core_events.abc.Compound, typing.Generic[T]):
    """A :class:`Concurrence` hosts events that take place at the same time."""

    # ###################################################################### #
    #                       private static methods                           #
    # ###################################################################### #

    @staticmethod
    def _extend_ancestor(ancestor: core_events.abc.Event, event: core_events.abc.Event):
        try:
            ancestor._concatenate_tempo(event)
        # We can't concatenate to a chronon.
        # We also can't concatenate to anything else.
        except AttributeError:
            raise core_utilities.ConcatenationError(ancestor, event)
        match ancestor:
            case core_events.Consecution():
                ancestor.extend(event)
            case core_events.Concurrence():
                try:
                    ancestor.concatenate_by_tag(event)
                except core_utilities.NoTagError:
                    ancestor.concatenate_by_index(event)
            # This should already fail above, but if this strange object
            # somehow owned '_concatenate_tempo', it should
            # fail here.
            case _:
                raise core_utilities.ConcatenationError(ancestor, event)

    # ###################################################################### #
    #                           private methods                              #
    # ###################################################################### #

    def _make_event_slice_tuple(
        self,
        absolute_time_list: list[core_parameters.abc.Duration],
        slice_tuple_to_event: typing.Callable[
            [tuple[core_events.abc.Event, ...]], core_events.abc.Event
        ],
    ) -> tuple[core_events.abc.Event, ...]:
        """Split at given times and cast split events into new events."""
        abst_list = absolute_time_list

        # Slice all child events
        slices = []
        for e in self:
            slices.append(list(e.split_at(*abst_list, ignore_invalid_split_point=True)))

        # Ensure all slices have the same amount of entries,
        # because we use 'zip' later and if one of them is
        # shorter we loose some parts of our event.
        if slices:
            slices_count_tuple = tuple(len(s) for s in slices)
            max_slice_count = max(slices_count_tuple)
            for s, c in zip(slices, slices_count_tuple):
                if delta := max_slice_count - c:
                    s.extend([None] * delta)

        # Finally, build new sequence from event slices
        event_list = []
        for slice_tuple in zip(*slices):
            if slice_tuple := tuple(filter(bool, slice_tuple)):
                e = slice_tuple_to_event(slice_tuple)
                event_list.append(e)

        return tuple(event_list)

    # ###################################################################### #
    #                           properties                                   #
    # ###################################################################### #

    @core_events.abc.Compound.duration.getter
    def duration(self) -> core_parameters.abc.Duration:
        try:
            return max(e.duration for e in self)
        # If Concurrence is empty
        except ValueError:
            return core_parameters.DirectDuration(0)

    # ###################################################################### #
    #                           public methods                               #
    # ###################################################################### #

    def cut_out(  # type: ignore
        self,
        start: core_parameters.abc.Duration.Type,
        end: core_parameters.abc.Duration.Type,
    ) -> Concurrence[T]:
        start, end = (core_parameters.abc.Duration.from_any(o) for o in (start, end))
        self._assert_valid_absolute_time(start)
        self._assert_correct_start_and_end_values(start, end)
        [e.cut_out(start, end) for e in self]
        return self

    def cut_off(  # type: ignore
        self,
        start: core_parameters.abc.Duration.Type,
        end: core_parameters.abc.Duration.Type,
    ) -> Concurrence[T]:
        start, end = (core_parameters.abc.Duration.from_any(o) for o in (start, end))
        self._assert_valid_absolute_time(start)
        self._assert_correct_start_and_end_values(start, end)
        [e.cut_off(start, end) for e in self]
        return self

    def squash_in(  # type: ignore
        self,
        start: core_parameters.abc.Duration.Type,
        event_to_squash_in: core_events.abc.Event,
    ) -> Concurrence[T]:
        start = core_parameters.abc.Duration.from_any(start)
        self._assert_valid_absolute_time(start)
        self._assert_start_in_range(start)

        for e in self:
            try:
                e.squash_in(start, event_to_squash_in)  # type: ignore
            # Simple events don't have a 'squash_in' method.
            except AttributeError:
                raise core_utilities.ImpossibleToSquashInError(self, event_to_squash_in)
        return self

    def slide_in(
        self,
        start: core_parameters.abc.Duration.Type,
        event_to_slide_in: core_events.abc.Event,
    ) -> Concurrence[T]:
        start = core_parameters.abc.Duration.from_any(start)
        self._assert_valid_absolute_time(start)
        self._assert_start_in_range(start)
        for e in self:
            try:
                e.slide_in(start, event_to_slide_in)  # type: ignore
            # Simple events don't have a 'slide_in' method.
            except AttributeError:
                raise core_utilities.ImpossibleToSlideInError(self, event_to_slide_in)
        return self

    def split_child_at(
        self, absolute_time: core_parameters.abc.Duration.Type
    ) -> Concurrence[T]:
        abst = core_parameters.abc.Duration.from_any(absolute_time)
        for i, e in enumerate(self):
            try:
                e.split_child_at(abst)
            # chronons don't have a 'split_child_at' method
            except AttributeError:
                split_event = e.split_at(abst)
                self[i] = Consecution(split_event)
        return self

    def extend_until(
        self,
        duration: typing.Optional[core_parameters.abc.Duration.Type] = None,
        duration_to_white_space: typing.Optional[
            typing.Callable[[core_parameters.abc.Duration], core_events.abc.Event]
        ] = None,
        prolong_chronon: bool = True,
    ) -> Concurrence[T]:
        duration = (
            self.duration
            if duration is None
            else core_parameters.abc.Duration.from_any(duration)
        )
        duration_to_white_space = (
            duration_to_white_space
            or core_events.configurations.DEFAULT_DURATION_TO_WHITE_SPACE
        )
        # We only append chronons to consecutions, because there
        # are many problems with the Concurrence[Chronon] construct
        # ('extend_until' and 'squash_in' will fail on such a container).
        # Therefore calling 'extend_until' on an empty Concurrence is
        # in fact ineffective: The user would get a Concurrence which
        # still has duration = 0, which is absolutely unexpected. Therefore
        # we raise an error, to avoid confusion by the user.
        if not self:
            raise core_utilities.IneffectiveExtendUntilError(self)
        for e in self:
            try:
                e.extend_until(duration, duration_to_white_space, prolong_chronon)
            # Chronon
            except AttributeError:
                if prolong_chronon:
                    if (difference := duration - e.duration) > 0:
                        e.duration += difference
                else:
                    raise core_utilities.ImpossibleToExtendUntilError(e)
        return self

    def concatenate_by_index(self, other: Concurrence) -> Concurrence:
        """Concatenate with other :class:`~mutwo.core_events.Concurrence` along their indices.

        :param other: The other `Concurrence` with which to concatenate.
            The other `Concurrence` can contain more or less events.
        :type other: Concurrence
        :raises core_utilities.ConcatenationError: If there are any :class:`Chronon`
            inside a :class:`Concurrence`.

        **Hint:**

        Similarly to Pythons ``list.extend`` the concatenation simply appends
        the children of the other event to the sequence without copying them.
        This means when changing the children in the new event, it also changes
        the child event in the original sequence. If you want to avoid this,
        call ``event.copy()`` before concatenating it to the host event.

        **Example:**

        >>> from mutwo import core_events
        >>> cnc = core_events.Concurrence(
        ...     [core_events.Consecution([core_events.Chronon(1)])]
        ... )
        >>> cnc.concatenate_by_index(cnc)
        Concurrence([Consecution([Chronon(duration=DirectDuration(1.0)), Chronon(duration=DirectDuration(1.0))])])
        """
        if (dur := self.duration) > 0:
            self.extend_until(dur)
        for i, e in enumerate(other):
            try:
                ancestor = self[i]
            except IndexError:
                if dur > 0:
                    # Shallow copy before 'slide_in': We use the same
                    # events, but we don't want to change the other sequence.
                    e_new = e.empty_copy()
                    e_new.extend(e[:])
                    e = e_new.slide_in(0, core_events.Chronon(dur))
                self.append(e)
            else:
                self._extend_ancestor(ancestor, e)
        return self

    def concatenate_by_tag(self, other: Concurrence) -> Concurrence:
        """Concatenate with other :class:`~mutwo.core_events.Concurrence` along their tags.

        :param other: The other `Concurrence` with which to concatenate.
            The other `Concurrence` can contain more or less events.
        :type other: Concurrence
        :return: Concatenated event.
        :raises core_utilities.NoTagError: If any child event doesn't have a 'tag'
            attribute.
        :raises core_utilities.ConcatenationError: If there are any :class:`Chronon`
            inside a :class:`Concurrence`.

        **Hint:**

        Similarly to Pythons ``list.extend`` the concatenation simply appends
        the children of the other event to the sequence without copying them.
        This means when changing the children in the new event, it also changes
        the child event in the original sequence. If you want to avoid this,
        call ``event.copy()`` before concatenating it to the host event.

        **Example:**

        >>> from mutwo import core_events
        >>> cnc = core_events.Concurrence(
        ...      [core_events.Consecution([core_events.Chronon(1)], tag="test")]
        ...  )
        >>> cnc.concatenate_by_tag(cnc)
        Concurrence([Consecution([Chronon(duration=DirectDuration(1.0)), Chronon(duration=DirectDuration(1.0))])])
        """
        if (dur := self.duration) > 0:
            self.extend_until(dur)
        for e in other:
            if not (tag := e.tag):
                raise core_utilities.NoTagError(e)
            try:
                ancestor = self[tag]
            except KeyError:
                if dur > 0:
                    # Shallow copy before 'slide_in': We use the same
                    # events, but we don't want to change the other sequence.
                    e_new = e.empty_copy()
                    e_new.extend(e[:])
                    e = e_new.slide_in(0, core_events.Chronon(dur))
                self.append(e)
            else:
                self._extend_ancestor(ancestor, e)
        return self

    # NOTE: 'sequentialize' is very generic, it works for all type of child
    # event structure. This is good, but in it's current form it's mostly
    # only useful with rather long and complex user defined 'slice_tuple_to_event'
    # definitions. For instance when sequentializing
    # Concurrence[Consecution[Chronon]] the returned event will be
    # Consecution[Concurrence[Consecution[Chronon]]]. Here the
    # inner consecutions are always pointless, since they will always only
    # contain one chronon.
    def sequentialize(
        self,
        slice_tuple_to_event: typing.Optional[
            typing.Callable[[tuple[core_events.abc.Event, ...]], core_events.abc.Event]
        ] = None,
    ) -> core_events.Consecution:
        """Convert parallel structure to a consuential structure.

        :param slice_tuple_to_event: In order to sequentialize the event
            `mutwo` splits each child event into small 'event slices'. These
            'event slices' are simply events created by the `split_at` method.
            Each of those parallel slice groups need to be bound together to
            one new event. These new events are consuentially ordered to result
            in a new consuential structure. The simplest and default way to
            archive this is by simply putting all event parts into a new
            :class:`Concurrence`, so the resulting :class:`Consecution`
            is a sequence of `Concurrence`. This parameter is
            available so that users can convert her/his parallel structure in
            meaningful ways (for instance to imitate the ``.chordify``
            `method from music21 <https://web.mit.edu/music21/doc/usersGuide/usersGuide_09_chordify.html>`
            which transforms polyphonic music to a chord structure).
            If ``None`` `slice_tuple_to_event` is set to
            :class:`Concurrence`. Default to ``None``.
        :type slice_tuple_to_event: typing.Optional[typing.Callable[[tuple[core_events.abc.Event, ...]], core_events.abc.Event]]

        **Warning:**

        Because the returned event is a :class:`Consecution` class specific
        side attributes of the :class:`Concurrence` aren't persistent in
        the returned event.

        **Example:**

        >>> from mutwo import core_events
        >>> e = core_events.Concurrence(
        ...     [
        ...         core_events.Consecution(
        ...             [core_events.Chronon(2), core_events.Chronon(1)]
        ...         ),
        ...         core_events.Consecution(
        ...             [core_events.Chronon(3)]
        ...         ),
        ...     ]
        ... )
        >>> cns = e.sequentialize()
        >>> print(cns)
        Cons(Conc(Cons(C(dur=D(2.0))), Cons(C(dur=D(2.0)))), Conc(Cons(C(dur=D(1.0))), Cons(C(dur=D(1.0)))))
        """
        if slice_tuple_to_event is None:
            slice_tuple_to_event = Concurrence

        # Find all start/end times
        abst_set = set([])
        for e in self:
            try:  # Consecution
                abst_tuple, dur = e._abstf_tuple_and_dur
            except AttributeError:  # Chronon or Concurrence
                abst_tuple, dur = (0,), e.duration.beat_count
            for t in abst_tuple + (dur,):
                abst_set.add(t)

        # Sort, but also remove the last entry: we don't need
        # to split at complete duration, because after duration
        # there isn't any event left in any child.
        abst_list = sorted(abst_set)[:-1]

        return core_events.Consecution(
            self._make_event_slice_tuple(abst_list, slice_tuple_to_event),
            tag=self.tag,
        )

    def split_at(
        self,
        *absolute_time: core_parameters.abc.Duration.Type,
        ignore_invalid_split_point: bool = False,
    ) -> tuple[Concurrence, ...]:
        if not absolute_time:
            raise core_utilities.NoSplitTimeError()

        abst_list = sorted(
            [core_parameters.abc.Duration.from_any(t) for t in absolute_time]
        )
        self._assert_valid_absolute_time(abst_list[0])
        if abst_list[-1] > self.duration and not ignore_invalid_split_point:
            raise core_utilities.SplitError(abst_list[-1])

        def slice_tuple_to_event(slice_tuple):
            e = self.empty_copy()
            e[:] = slice_tuple
            return e

        return self._make_event_slice_tuple(abst_list, slice_tuple_to_event)
