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

"""Abstract base classes for events (definition of public API)."""

from __future__ import annotations

import abc
import functools
import typing

from mutwo import core_constants
from mutwo import core_events
from mutwo import core_parameters
from mutwo import core_utilities


__all__ = ("Event", "Compound")


class Event(core_utilities.MutwoObject, abc.ABC):
    """Abstract Event-Object

    :param tempo: An envelope which describes the dynamic tempo of an event.
    :param tag: The name of the event. This can be used to find the event
        inside a :class:`Compound`.
    """

    # It looks tempting to drop the 'tempo' attribute of events.
    # It may look simpler (and therefore more elegant) if events are only
    # defined by one attribute: their duration. Let's remember why the
    # 'tempo' attribute was initially introduced [1]:
    #
    # - With [1] it was decided that durations are represented in the unit
    #   'beat_count'.
    #
    # - An event should have an unambiguous duration, so that converters
    #   (and all other 'mutwo' parts) can treat an event consistently.
    #
    # - The unit of 'beat_count' doesn't say anything about the real duration:
    #   only in cooperation with a specified tempo it can be clearly stated how
    #   long an event is.
    #
    # - Therefore the combination of (a) having duration specified in the unit
    #   'beat_count' and (b) wanting to have events with unambiguous duration
    #   leads to the necessity to attach tempos to events.
    #
    # In the early days of mutwo (b) wasn't considered to be an objective:
    # it was the opposite, an implicit ambiguity was considered to be a good
    # idea [2]. But in the practical usage of the library it turned out that
    # this approach rather increased complexity, as other code bits are unable
    # to treat an event consistently and a user constantly has to keep in mind
    # the specific way how each converter interprets a duration. To fix this
    # complexity, the 'beat' unit was specified and a 'tempo'
    # attribute has been added. Now converters could reliably produce
    # results which match the duration of an event.
    #
    # Now we could change durations to be no longer in the unit 'beat_count',
    # but in the unit 'seconds'. Then the duration of an event would still be
    # unambiguous without the need of a tempo attribute.  We could
    # furthermore implement duration representations with beat & tempo as a
    # subclass of a more general 'duration=seconds' approach. This has two
    # problems:
    #
    # (1) It may be more computation intensive to ask for the
    #     'absolute_time_tuple' of a event with beat-based durations as their
    #     'seconds' attribute would need to be calculated from their beat+tempo
    #     values in run time.
    #
    # (2) It would be very impractical to use all event methods with absolute
    #     times as arguments (e. g. 'slide_in', 'split_at', ...) in a beat
    #     approached subclass, as we wouldn't squash in our event at the given
    #     'beat', but a given duration in seconds, which would depend on the
    #     tempo - and wouldn't resonate with how we usually think about music.
    #
    # (3) If we think of tempo, it's rather a global trajectory independent
    #     from single notes. So we usually think of a tempo trajectory as
    #     something that belongs to a nested event (e.g. a 'Consecution' or
    #     a 'Concurrence'). But with the duration=seconds approach such a
    #     tempo trajectory couldn't be persistently mapped to a nested event,
    #     because the duration of a Compound isn't a statically mapped and
    #     available entity, but ephemerally and dynamically calculated when
    #     needed. When the duration of a Compound is set, it becomes
    #     propagated to the duration of its children until it finds a leaf that
    #     statically declares its duration and then it's lost. So in order to
    #     have a persistently available tempo trajectory on a Compound
    #     that can be read and modified-in-place, we need an extra tempo
    #     attribute. Otherwise we would break the rule that the duration of
    #     a Compound is only a sum or max of its children duration.
    #
    # Due to these reasons, that describe new complexities by switching to a
    # 'duration=seconds' model, we should stick to the beats/tempo
    # approach until we can find a better solution.
    #
    # Now we could also ask the other way around, because if durations are in
    # 'beats', are musical applications too dominant in 'mutwo' and is the
    # 'mutwo' model not general enough? Interestingly duration as beats+tempo
    # isn't only a subset of a 'duration=seconds' model, but this is also
    # true vice versa: if the default tempo of an event (which is 60 BPM)
    # isn't changed, the beats of a duration does in fact equal seconds.
    # So for users who don't care about splitting duration into beats+tempo,
    # they can simply avoid any 'tempo' attribute and directly write
    # their duration in seconds.
    #
    # ---
    #
    # [1] https://github.com/mutwo-org/mutwo.core/commit/c2c7f3ba
    # [2] In fact this ambiguity was always only true for durations: pitches
    #     or volumes for instance were always unambiguous. Nowadays we can
    #     clearly describe the 'mutwo' approach as: events unambiguously
    #     represent a clear idea of *something*. Converters, on the other
    #     hand, interpret this event as it is in the converters idiosyncratic
    #     understanding of it, but by trying to be as true as possible to
    #     the original idea.

    def __init__(
        self,
        tempo: typing.Optional[core_parameters.abc.Tempo] = None,
        tag: typing.Optional[str] = None,
    ):
        self.tempo = tempo
        self.tag = tag

    # ###################################################################### #
    #                        abstract properties                             #
    # ###################################################################### #

    @property
    @abc.abstractmethod
    def duration(self) -> core_parameters.abc.Duration:
        """The duration of an event.

        This has to be an instance of :class:`mutwo.core_parameters.abc.Duration`.
        """

    # ###################################################################### #
    #                           private methods                              #
    # ###################################################################### #

    @staticmethod
    def _assert_correct_start_and_end_values(
        start: core_parameters.abc.Duration | core_constants.Real,
        end: core_parameters.abc.Duration | core_constants.Real,
        condition: typing.Callable[
            [core_parameters.abc.Duration, core_parameters.abc.Duration], bool
        ] = lambda start, end: end
        >= start,
    ):
        """Helper method to make sure that start < end.

        Can be used within the different cut_out methods.
        """
        if not condition(start, end):
            raise core_utilities.InvalidStartAndEndValueError(start, end)

    @staticmethod
    def _assert_valid_absolute_time(
        t: core_parameters.abc.Duration | core_constants.Real,
    ):
        if t < 0:
            raise core_utilities.InvalidAbsoluteTime(t)

    @functools.cached_property
    def _event_to_metrized_event(self):
        # Import in method to avoid circular import error
        return __import__(
            "mutwo.core_converters"
        ).core_converters.EventToMetrizedEvent()

    @abc.abstractmethod
    def _set_parameter(
        self,
        parameter_name: str,
        object_or_function: typing.Callable[[typing.Any], typing.Any] | typing.Any,
        set_unassigned_parameter: bool,
        id_set: set[int],
    ) -> Event:
        ...

    @abc.abstractmethod
    def _mutate_parameter(
        self,
        parameter_name: str,
        function: typing.Callable[[typing.Any], None] | typing.Any,
        id_set: set[int],
    ) -> Event:
        ...

    # ###################################################################### #
    #                           public properties                            #
    # ###################################################################### #

    @property
    def tempo(self) -> core_parameters.abc.Tempo:
        """The tempo of an event."""
        if self._tempo is None:
            self.reset_tempo()
        return self._tempo

    @tempo.setter
    def tempo(self, tempo: typing.Optional[core_parameters.abc.Tempo]):
        self._tempo = core_parameters.abc.Tempo.from_any(tempo) if tempo else None

    # ###################################################################### #
    #                           public methods                               #
    # ###################################################################### #

    @abc.abstractmethod
    def destructive_copy(self) -> Event:
        """Adapted deep copy method that returns a new object for every leaf.

        It's called 'destructive', because it forgets potential repetitions of
        the same object in compound objects. Instead of reproducing the original
        structure of the compound object that shall be copied, every repetition
        of the same reference returns a new unique independent object.

        The following example shall illustrate the difference between copy.deepcopy
        and destructive_copy:

        >>> import copy
        >>> from mutwo import core_events
        >>> chn0 = core_events.Chronon(2)
        >>> chn1 = core_events.Chronon(3)
        >>> cns = core_events.Consecution([chn0, chn1, chn0])
        >>> cns_copy = copy.deepcopy(cns)
        >>> cns_destr_copy = cns.destructive_copy()
        >>> cns_copy[0].duration = 10  # setting the duration of the first event
        >>> cns_destr_copy[0].duration = 10
        >>> # return True because the first and the third objects share the same
        >>> # reference (both are the same copy of 'my_chronon_0')
        >>> cns_copy[0].duration == cns_copy[2].duration
        True
        >>> # return False because destructive_copy forgets the shared reference
        >>> cns_destr_copy[0].duration == cns_destr_copy[2].duration
        False
        """

    def set(self, attribute_name: str, value: typing.Any) -> Event:
        """Set an attribute of the object to a specific value

        :param attribute_name: The name of the attribute which value shall be set.
        :param value: The value which shall be assigned to the given
            :attr:`attribute_name`
        :return: The event.

        This function is merely a convenience wrapper for...

        ``event.attribute_name = value``

        Because the function return the event itself it can be used
        in function composition.

        **Example:**

        >>> from mutwo import core_events
        >>> cns = core_events.Consecution([core_events.Chronon(2)])
        >>> cns.set('duration', 10).set('my_new_attribute', 'hello-world!')
        Consecution([Chronon(duration=DirectDuration(10.0))])
        """
        setattr(self, attribute_name, value)
        return self

    @abc.abstractmethod
    def get_parameter(
        self, parameter_name: str, flat: bool = False, filter_undefined: bool = False
    ) -> tuple[typing.Any, ...] | typing.Any:
        """Return event attribute with the entered name.

        :param parameter_name: The name of the attribute that shall be returned.
        :type parameter_name: str
        :param flat: ``True`` for flat sequence of parameter values, ``False`` if the
            resulting ``tuple`` shall repeat the nested structure of the event.
        :type flat: bool
        :param filter_undefined: If set to ``True`` all ``None`` values will be filtered
            from the returned tuple. Default to ``False``. This flag has no effect on
            :func:`get_parameter` of :class:`mutwo.core_events.Chronon`.
        :type flat: bool
        :return: Return tuple containing the assigned values for each contained
            event. If an event doesn't posses the asked parameter, mutwo will simply
            add None to the tuple for the respective event.

        **Example:**

        >>> from mutwo import core_events
        >>> cns = core_events.Consecution(
        ...     [core_events.Chronon(2), core_events.Chronon(3)]
        ... )
        >>> cns.get_parameter('duration')
        (DirectDuration(2.0), DirectDuration(3.0))
        >>> chn = core_events.Chronon(10)
        >>> chn.get_parameter('duration')
        DirectDuration(10.0)
        >>> chn.get_parameter('undefined_parameter')
        """

    def set_parameter(
        self,
        parameter_name: str,
        object_or_function: typing.Callable[[typing.Any], typing.Any] | typing.Any,
        set_unassigned_parameter: bool = True,
    ) -> typing.Optional[Event]:
        """Sets parameter to new value for all children events.

        :param parameter_name: The name of the parameter which values shall be changed.
        :type parameter_name: str
        :param object_or_function: For setting the parameter either a new value can be
            passed directly or a function can be passed. The function gets as an
            argument the previous value that has had been assigned to the respective
            object and has to return a new value that will be assigned to the object.
        :param set_unassigned_parameter: If set to False a new parameter will only be
            assigned to an Event if the Event already has a attribute with the
            respective `parameter_name`. If the Event doesn't know the attribute yet
            and `set_unassigned_parameter` is False, the method call will simply be
            ignored.
        :return: The event.

        **Example:**

        >>> from mutwo import core_events
        >>> cns = core_events.Consecution(
        ...     [core_events.Chronon(2), core_events.Chronon(3)]
        ... )
        >>> cns.set_parameter('duration', lambda duration: duration * 2)
        Consecution([Chronon(duration=DirectDuration(4.0)), Chronon(duration=DirectDuration(6.0))])
        >>> cns.get_parameter('duration')
        (DirectDuration(4.0), DirectDuration(6.0))

        **Warning:**

        If there are multiple references of the same Event inside a
        :class:`~mutwo.core_events.Consecution` or a
        :class:`~mutwo.core_events.Concurrence`, ``set_parameter``
        is only called once for each Event. So multiple references
        of the same event will be ignored. This behaviour ensures,
        that on a big scale level each item inside the
        :class:`mutwo.core_events.abc.Compound` is treated equally
        (so for instance the duration of each item is doubled, and
        nor for some doubled and for those with references which
        appear twice quadrupled).
        """
        return self._set_parameter(
            parameter_name,
            object_or_function,
            set_unassigned_parameter=set_unassigned_parameter,
            id_set=set([]),
        )

    def mutate_parameter(
        self,
        parameter_name: str,
        function: typing.Callable[[typing.Any], None] | typing.Any,
    ) -> typing.Optional[Event]:
        """Mutate parameter with a function.

        :param parameter_name: The name of the parameter which shall be mutated.
        :param function: The function which mutates the parameter. The function gets
            as an input the assigned value for the passed parameter_name of the
            respective object. The function shouldn't return anything, but simply
            calls a method of the parameter value.

        This method is useful when a particular parameter has been assigned to objects
        that know methods which mutate themselves. Then 'mutate_parameter' is a
        convenient wrapper to call the methods of those parameters for all children
        events.

        **Example:**

        >>> from mutwo import core_events
        >>> cons= core_events.Consecution([core_events.Chronon(1)])
        >>> cons.mutate_parameter(
        ...     'duration', lambda duration: duration.add(1)
        ... )
        Consecution([Chronon(duration=DirectDuration(2.0))])
        >>> # now duration should be + 1
        >>> cons.get_parameter('duration')
        (DirectDuration(2.0),)

        **Warning:**

        If there are multiple references of the same Event inside a
        :class:`~mutwo.core_events.Consecution` or a
        ~mutwo.core_events.Concurrence`, ``mutate_parameter`` will
        only be called once for each Event. So multiple references
        of the same event will be ignored. This behaviour ensures,
        that on a big scale level each item inside the
        :class:`mutwo.core_events.abc.Compound` is treated equally
        (so for instance the duration of each item is doubled, and
        nor for some doubled and for those with references which
        appear twice quadrupled).
        """
        return self._mutate_parameter(
            parameter_name,
            function,
            id_set=set([]),
        )

    def reset_tempo(self) -> Event:
        """Set events tempo so that one beat equals one second (tempo 60).

        **Example:**

        >>> from mutwo import core_events
        >>> chn = core_events.Chronon(duration = 1)
        >>> chn.tempo.bpm = 100
        >>> print(chn.tempo)
        D(100.0)
        >>> chn.reset_tempo()
        Chronon(duration=DirectDuration(1.0))
        >>> print(chn.tempo)
        D(60.0)
        """
        self.tempo = core_parameters.DirectTempo(60)
        return self

    @abc.abstractmethod
    def metrize(self) -> typing.Optional[Event]:
        """Apply tempo of event on itself

        Metrize is only syntactic sugar for a call of
        :class:`EventToMetrizedEvent`:

        >>> from mutwo import core_converters
        >>> from mutwo import core_events
        >>> chn = core_events.Chronon(1)
        >>> chn.tempo = core_parameters.FlexTempo([[0, 100], [1, 40]])
        >>> core_converters.EventToMetrizedEvent().convert(chn) == chn.metrize()
        True
        """

    @abc.abstractmethod
    def cut_out(
        self,
        start: core_parameters.abc.Duration.Type,
        end: core_parameters.abc.Duration.Type,
    ) -> typing.Optional[Event]:
        """Time-based slicing of the respective event.

        :param start: Duration when the cut out shall start.
        :param end: Duration when the cut up shall end.

        **Example:**

        >>> from mutwo import core_events
        >>> chn0, chn1 = (core_events.Chronon(3), core_events.Chronon(2))
        >>> cns = core_events.Consecution([chn0, chn1])
        >>> cns.cut_out(1, 4)
        Consecution([Chronon(duration=DirectDuration(2.0)), Chronon(duration=DirectDuration(1.0))])
        """

    @abc.abstractmethod
    def cut_off(
        self,
        start: core_parameters.abc.Duration.Type,
        end: core_parameters.abc.Duration.Type,
    ) -> typing.Optional[Event]:
        """Time-based deletion / shortening of the respective event.

        :param start: Duration when the cut off shall start.
        :param end: Duration when the cut off shall end.

        **Example:**

        >>> from mutwo import core_events
        >>> chn0, chn1 = (core_events.Chronon(3), core_events.Chronon(2))
        >>> cns = core_events.Consecution([chn0, chn1])
        >>> cns.cut_off(1, 3)
        Consecution([Chronon(duration=DirectDuration(1.0)), Chronon(duration=DirectDuration(2.0))])
        """

    def split_at(
        self,
        *absolute_time: core_parameters.abc.Duration.Type,
        ignore_invalid_split_point: bool = False,
    ) -> tuple[Event, ...]:
        """Split event into *n* events at :attr:`absolute_time`.

        :param *absolute_time: where event shall be split
        :param ignore_invalid_split_point: If set to `True` `split_at` won't raise
            :class:`mutwo.core_utilities.SplitError` in case a split time isn't
            inside the duration range of the event. Otherwise the exception is raised.
            Default to ``False``.
        :raises: :class:`mutwo.core_utilities.NoSplitTimeError` if no `absolute_time`
            is given. Raises :class:`mutwo.core_utilities.InvalidAbsoluteTime` if any
            absolute_time is smaller than 0. Raises :class:`mutwo.core_utilities.SplitError`
            if any absolute_time is bigger than the events duration and
            `ignore_invalid_split_point` is not set.
        :return:  Tuple of events that result from splitting the present event.

        **Hint:**

        Calling ``split_at`` once with multiple split time arguments is much more efficient
        than calling ``split_at`` multiple times with only one split time for
        :class:`mutwo.core_events.Consecution`.

        **Example:**

        >>> from mutwo import core_events
        >>> cns = core_events.Consecution([core_events.Chronon(3)])
        >>> cns.split_at(1)
        (Consecution([Chronon(duration=DirectDuration(1.0))]), Consecution([Chronon(duration=DirectDuration(2.0))]))
        >>> cns[0].split_at(1)
        (Chronon(duration=DirectDuration(1.0)), Chronon(duration=DirectDuration(2.0)))
        """
        if not absolute_time:
            raise core_utilities.NoSplitTimeError()

        abst_list = list(
            sorted([core_parameters.abc.Duration.from_any(t) for t in absolute_time])
        )
        # Already sorted => check if smallest t < 0
        self._assert_valid_absolute_time(abst_list[0])
        if 0 not in abst_list:
            abst_list.insert(0, core_parameters.DirectDuration(0))

        if (dur := self.duration) > abst_list[-1]:
            abst_list.append(dur)
        elif dur < abst_list[-1] and not ignore_invalid_split_point:
            raise core_utilities.SplitError(abst_list[-1])

        split_event_list = []
        for t0, t1 in zip(abst_list, abst_list[1:]):
            try:
                split_event_list.append(self.copy().cut_out(t0, t1))
            except (
                core_utilities.InvalidStartAndEndValueError,
                core_utilities.InvalidCutOutStartAndEndValuesError,
            ):
                if not ignore_invalid_split_point:
                    raise core_utilities.SplitError(t0)

        return tuple(split_event_list)


T = typing.TypeVar("T", bound=Event)


# FIXME(This Event can be initialised (no abstract error).
# Please see the following issue for comparison:
#   https://bugs.python.org/issue35815
class Compound(Event, abc.ABC, list[T], typing.Generic[T]):
    """Abstract Event-Object, which contains other Event-Objects."""

    _short_name_length = 4

    def __init__(
        self,
        iterable: typing.Iterable[T] = [],
        *,
        tempo: typing.Optional[core_parameters.abc.Tempo] = None,
        tag: typing.Optional[str] = None,
    ):
        Event.__init__(self, tempo, tag)
        list.__init__(self, iterable)

    def __init_subclass__(
        cls, class_specific_side_attribute_tuple: tuple[str, ...] = tuple([])
    ):
        # It's better to prove `class_specific_side_attribute_tuple`
        # as a class initialisation attribute instead of a simple class attribute,
        # because with a simple class attribute we have no guarantee that the
        # content of the parent class is available and we always have to explicitly
        # make it available with something like:
        #
        #   class MyCompound(Compound):
        #        _class_specific_side_attribute_tuple = (("new_attribute",) +
        #          Compound._class_specific_side_attribute_tuple)
        #
        # With __init_subclass__ we can simply write:
        #
        #   class MyCompound(
        #     Compound,
        #    class_specific_side_attribute_tuple = ("new_attribute",)
        #   ): pass
        #
        super_class_attr_tuple = getattr(
            cls, "_class_specific_side_attribute_tuple", ("tempo", "tag")
        )
        class_attr_tuple = super_class_attr_tuple + class_specific_side_attribute_tuple
        cls._class_specific_side_attribute_tuple = class_attr_tuple

    # ###################################################################### #
    #                           magic methods                                #
    # ###################################################################### #

    def __add__(self, event: list[T]) -> Compound[T]:
        e = self.empty_copy()
        e.extend(super().__add__(event))
        return e

    def __mul__(self, factor: int) -> Compound[T]:
        e = self.empty_copy()
        e.extend(super().__mul__(factor))
        return e

    @typing.overload
    def __getitem__(self, index_or_slice_or_tag: int) -> T:
        ...

    @typing.overload
    def __getitem__(self, index_or_slice_or_tag: slice) -> Compound[T]:
        ...

    @typing.overload
    def __getitem__(self, index_or_slice_or_tag: str) -> T:
        ...

    def __getitem__(
        self, index_or_slice_or_tag: int | slice | str
    ) -> T | Compound[T]:
        try:
            event = super().__getitem__(index_or_slice_or_tag)
        except TypeError as error:
            if isinstance(index_or_slice_or_tag, str):
                return self.__getitem__(self._tag_to_index(index_or_slice_or_tag))
            # It can't be a tag, therefore simply raise
            # original exception.
            raise error
        if isinstance(index_or_slice_or_tag, slice):
            empty_event = self.empty_copy()
            empty_event.extend(event)
            return empty_event
        else:
            return event

    @typing.overload
    def __setitem__(self, index_or_slice_or_tag: int, event: core_events.abc.Event):
        ...

    @typing.overload
    def __setitem__(self, index_or_slice_or_tag: slice, event: core_events.abc.Event):
        ...

    @typing.overload
    def __setitem__(self, index_or_slice_or_tag: str, event: core_events.abc.Event):
        ...

    def __setitem__(
        self, index_or_slice_or_tag: int | slice | str, event: core_events.abc.Event
    ):
        try:
            super().__setitem__(index_or_slice_or_tag, event)
        except TypeError as error:
            if isinstance(index_or_slice_or_tag, str):
                return self.__setitem__(
                    self._tag_to_index(index_or_slice_or_tag), event
                )
            # It can't be a tag, therefore simply raise
            # original exception.
            raise error

    # We write custom __delitem__ to support deletion via tag.
    @typing.overload
    def __delitem__(self, index_or_slice_or_tag: int):
        ...

    @typing.overload
    def __delitem__(self, index_or_slice_or_tag: slice):
        ...

    @typing.overload
    def __delitem__(self, index_or_slice_or_tag: str):
        ...

    def __delitem__(self, index_or_slice_or_tag: int | slice | str):
        try:
            super().__delitem__(index_or_slice_or_tag)
        except TypeError as error:
            if isinstance(index_or_slice_or_tag, str):
                return self.__delitem__(self._tag_to_index(index_or_slice_or_tag))
            # It can't be a tag, therefore simply raise
            # original exception.
            raise error

    def __eq__(self, other: typing.Any) -> bool:
        """Test for checking if two objects are equal."""
        try:
            parameter_to_compare_set = set([])
            for obj in (self, other):
                for param in obj._class_specific_side_attribute_tuple:
                    parameter_to_compare_set.add(param)
        except AttributeError:
            return False
        return core_utilities.test_if_objects_are_equal_by_parameter_tuple(
            self, other, tuple(parameter_to_compare_set)
        ) and super().__eq__(other)

    def __ne__(self, other: typing.Any):
        return not self.__eq__(other)

    def __repr_content__(self):
        return list.__repr__(self)

    def __str_content__(self):
        return ", ".join([str(e) for e in self])

    # ###################################################################### #
    #                           properties                                   #
    # ###################################################################### #

    @Event.duration.setter  # type: ignore
    def duration(self, duration: core_parameters.abc.Duration.Type):
        if not self:  # If empty and duration == 0, we'd run into ZeroDivision
            raise core_utilities.CannotSetDurationOfEmptyCompound()

        durf = core_parameters.abc.Duration.from_any(duration).beat_count
        if (old_durf := self.duration.beat_count) != 0:

            def f(event_duration: core_parameters.abc.Duration):
                return core_utilities.scale(
                    event_duration.beat_count, 0, old_durf, 0, durf
                )

        else:
            f = duration / len(self)

        self.set_parameter("duration", f)

    # ###################################################################### #
    #                           private methods                              #
    # ###################################################################### #

    # Keep private because:
    #   (1) Then we can later change the internal implementation of
    #       Compound (for instance: no longer inheriting from list).
    #   (2) It's not sure if tag_to_index is valuable for end users of
    #       Compound
    def _tag_to_index(self, tag: str) -> int:
        # Find index of an event by its tag.
        # param tag: The `tag` of the event which shall be found.
        # type tag: str
        for i, e in enumerate(self):
            if tag == e.tag:
                return i
        raise KeyError(f"No event found with tag = '{tag}'.")

    def _assert_start_in_range(
        self, start: core_parameters.abc.Duration | core_constants.Real
    ):
        """Helper method to make sure that start < event.duration.

        Can be used within the different squash_in methods.
        """
        if self.duration < start:
            raise core_utilities.InvalidStartValueError(start, self.duration)

    def _apply_once_per_event(
        self, method_name: str, *args, id_set: set[int], **kwargs
    ) -> Compound[T]:
        for e in self:
            if (e_id := id(e)) not in id_set:
                id_set.add(e_id)
                getattr(e, method_name)(*args, id_set=id_set, **kwargs)
        return self

    def _set_parameter(  # type: ignore
        self,
        parameter_name: str,
        object_or_function: typing.Callable[[typing.Any], typing.Any] | typing.Any,
        set_unassigned_parameter: bool,
        id_set: set[int],
    ) -> Compound[T]:
        return self._apply_once_per_event(
            "_set_parameter",
            parameter_name,
            object_or_function,
            id_set=id_set,
            set_unassigned_parameter=set_unassigned_parameter,
        )

    def _mutate_parameter(  # type: ignore
        self,
        parameter_name: str,
        function: typing.Callable[[typing.Any], None] | typing.Any,
        id_set: set[int],
    ) -> Compound[T]:
        return self._apply_once_per_event(
            "_mutate_parameter",
            parameter_name,
            function,
            id_set=id_set,
        )

    def _concatenate_tempo(self, other: Compound):
        """Concatenate the tempo of event with tempo of other event.

        If we concatenate events on the time axis, we also want to
        ensure that the tempo information is not lost.
        This includes the `+` magic method of ``Consecution``,
        but also the `concatenate_by...` methods of ``Concurrence``.

        It's important to first call this method before appending the
        child events of the other container, because we still need
        to know the original duration of the target event. Due to this
        difficulty this method is private.
        """
        # Trivial case: if tempo doesn't change and isn't flex, we
        # don't need to do anything to preserve the tempo of the other event.
        is_not_flex = map(
            lambda t: not isinstance(t, core_parameters.FlexTempo),
            (self.tempo, other.tempo),
        )
        if all(is_not_flex) and self.tempo == other.tempo:
            return

        # Convert to flex tempo, to easily handle tempos.
        for o in (self, other):
            o.tempo = core_parameters.FlexTempo.from_parameter(o.tempo)

        # We need to ensure the tempo of the event is as long as
        # it's duration, otherwise the others tempo may be
        # postponed (if our envelope is longer than the event)
        # or may be too early (if our tempo is shorted than the event).
        # We don't care here if the others event tempo is too
        # short or too long, because the relationships are still
        # the same.
        if (d := self.duration) < (d_env := self.tempo.duration):
            self._logger.warning(
                f"Tempo envelope of '{str(self)[:35]}...' needed "
                "to be truncated because the envelope was "
                "longer than the actual event."
            )
            self.tempo.cut_out(0, d)
        elif d > d_env:
            self.tempo.extend_until(d)
        self.tempo.extend(other.tempo.copy())

    # ###################################################################### #
    #                           public methods                               #
    # ###################################################################### #

    def destructive_copy(self) -> Compound[T]:
        empty_copy = self.empty_copy()
        empty_copy.extend([event.destructive_copy() for event in self])
        return empty_copy

    def empty_copy(self) -> Compound[T]:
        """Make a copy of the `Compound` without any child events.

        This method is useful if one wants to copy an instance of :class:`Compound`
        and make sure that all side attributes (e.g. any assigned properties specific
        to the respective subclass) get saved.

        **Example:**

        >>> from mutwo import core_events
        >>> piano_voice_0 = core_events.Consecution([core_events.Chronon(2)], tag="piano")
        >>> piano_voice_1 = piano_voice_0.empty_copy()
        >>> piano_voice_1.tag
        'piano'
        >>> piano_voice_1
        Consecution([])
        """
        return type(self)(
            [],
            **{a: getattr(self, a) for a in self._class_specific_side_attribute_tuple},
        )

    def get_event_from_index_sequence(
        self, index_sequence: typing.Sequence[int]
    ) -> Event:
        """Get nested :class:`Event` from a sequence of indices.

        :param index_sequence: The indices of the nested :class:`Event`.
        :type index_sequence: typing.Sequence[int]

        **Example:**

        >>> from mutwo import core_events
        >>> nested_consecution = core_events.Consecution(
        ...     [core_events.Consecution([core_events.Chronon(2)])]
        ... )
        >>> nested_consecution.get_event_from_index_sequence((0, 0))
        Chronon(duration=DirectDuration(2.0))
        >>> # this is equal to:
        >>> nested_consecution[0][0]
        Chronon(duration=DirectDuration(2.0))
        """

        return core_utilities.get_nested_item_from_index_sequence(index_sequence, self)

    def get_parameter(
        self, parameter_name: str, flat: bool = False, filter_undefined: bool = False
    ) -> tuple[typing.Any, ...]:
        plist: list[typing.Any] = []
        for e in self:
            param_or_param_tuple = e.get_parameter(parameter_name, flat=flat)
            if is_chronon := isinstance(e, core_events.Chronon):
                param_tuple = (param_or_param_tuple,)
            else:
                param_tuple = param_or_param_tuple
            if filter_undefined:
                param_tuple = tuple(filter(lambda v: v is not None, param_tuple))
            if flat:
                plist.extend(param_tuple)
            else:
                # Simple events should be added without tuple, they only
                # provide one parameter.
                if is_chronon:
                    if param_tuple:
                        plist.append(param_tuple[0])
                else:
                    plist.append(param_tuple)
        return tuple(plist)

    def remove_by(  # type: ignore
        self, condition: typing.Callable[[Event], bool]
    ) -> Compound[T]:
        """Condition-based deletion of child events.

        :param condition: Function which takes a :class:`Event` and returns ``True``
            or ``False``. If the return value of the function is ``False`` the
            respective `Event` will be deleted.
        :type condition: typing.Callable[[Event], bool]

        **Example:**

        >>> from mutwo import core_events
        >>> concurrence = core_events.Concurrence(
        ...     [core_events.Chronon(1), core_events.Chronon(3), core_events.Chronon(2)]
        ... )
        >>> concurrence.remove_by(lambda event: event.duration > 2)
        Concurrence([Chronon(duration=DirectDuration(3.0))])
        """
        for i, e in zip(reversed(range(len(self))), reversed(self)):
            if not condition(e):
                del self[i]
        return self

    def tie_by(  # type: ignore
        self,
        condition: typing.Callable[[Event, Event], bool],
        process_surviving_event: typing.Callable[
            [Event, Event], None
        ] = lambda event_to_survive, event_to_delete: event_to_survive.__setattr__(
            "duration", event_to_delete.duration + event_to_survive.duration
        ),
        event_type_to_examine: typing.Type[Event] = Event,
        event_to_remove: bool = True,
    ) -> Compound[T]:
        """Condition-based deletion of neighboring child events.

        :param condition: Function which compares two neighboring
            events and decides whether one of those events shall be
            removed. The function should return `True` for deletion and
            `False` for keeping both events.
        :param process_surviving_event: Function which gets two arguments: first
            the surviving event and second the event which shall be removed.
            The function should process the surviving event depending on
            the removed event. By default, mutwo will simply add the
            :attr:`duration` of the removed event to the duration of the surviving
            event.
        :param event_type_to_examine: Defines which events shall be compared.
            If one only wants to process the leaves, this should perhaps be
            :class:`mutwo.core_events.Chronon`.
        :param event_to_remove: `True` if the second (left) event shall be removed
            and `False` if the first (right) event shall be removed.
        """

        # Nothing to tie if no child events exist
        if not self:
            return self

        def tie_by_if_available(e: Event):
            if hasattr(e, "tie_by"):
                e.tie_by(
                    condition,
                    process_surviving_event,
                    event_type_to_examine,
                    event_to_remove,
                )

        pointer = 0
        while pointer + 1 < len(self):
            event_tuple = self[pointer], self[pointer + 1]
            if all(isinstance(e, event_type_to_examine) for e in event_tuple):
                if condition(*event_tuple):  # shall_delete
                    if event_to_remove:
                        process_surviving_event(*event_tuple)
                        del self[pointer + 1]
                    else:
                        process_surviving_event(*reversed(event_tuple))
                        del self[pointer]
                else:
                    pointer += 1
            # If event doesn't contain the event type which shall be tied,
            # it may still contain nested events which contains events with
            # the searched type
            else:
                tie_by_if_available(event_tuple[0])
                pointer += 1

        # Previously only the first event of the examined pairs has been tied,
        # therefore the very last event could have been forgotten.
        if not isinstance(self[-1], event_type_to_examine):
            tie_by_if_available(self[-1])

        return self

    def metrize(self) -> Compound:
        metrized_event = self._event_to_metrized_event(self)
        self.tempo = metrized_event.tempo
        self[:] = metrized_event[:]
        return self

    # ###################################################################### #
    #                           abstract methods                             #
    # ###################################################################### #

    @abc.abstractmethod
    def squash_in(
        self, start: core_parameters.abc.Duration.Type, event_to_squash_in: Event
    ) -> typing.Optional[Compound[T]]:
        """Time-based insert of a new event with overriding given event.

        :param start: Absolute time where the event shall be inserted.
        :param event_to_squash_in: the event that shall be squashed into
            the present event.

        Unlike `Compound.slide_in` the events duration won't change.
        If there is already an event at `start` this event will be shortened
        or removed.

        **Example:**

        >>> from mutwo import core_events
        >>> consecution = core_events.Consecution([core_events.Chronon(3)])
        >>> consecution.squash_in(1, core_events.Chronon(1.5))
        Consecution([Chronon(duration=DirectDuration(1.0)), Chronon(duration=DirectDuration(1.5)), Chronon(duration=DirectDuration(0.5))])
        """

    @abc.abstractmethod
    def slide_in(
        self, start: core_parameters.abc.Duration.Type, event_to_slide_in: Event
    ) -> Compound[T]:
        """Time-based insert of a new event into the present event.

        :param start: Absolute time where the event shall be inserted.
        :param event_to_slide_in: the event that shall be slide into
            the present event.

        Unlike `Compound.squash_in` the events duration will be prolonged
        by the event which is added. If there is an event at `start` the
        event will be split into two parts, but it won't be shortened or
        processed in any other way.

        **Example:**

        >>> from mutwo import core_events
        >>> consecution = core_events.Consecution([core_events.Chronon(3)])
        >>> consecution.slide_in(1, core_events.Chronon(1.5))
        Consecution([Chronon(duration=DirectDuration(1.0)), Chronon(duration=DirectDuration(1.5)), Chronon(duration=DirectDuration(2.0))])
        """

    @abc.abstractmethod
    def split_child_at(
        self, absolute_time: core_parameters.abc.Duration.Type
    ) -> typing.Optional[Compound[T]]:
        """Split child event in two events at :attr:`absolute_time`.

        :param absolute_time: where child event shall be split

        **Example:**

        >>> from mutwo import core_events
        >>> consecution = core_events.Consecution([core_events.Chronon(3)])
        >>> consecution.split_child_at(1)
        Consecution([Chronon(duration=DirectDuration(1.0)), Chronon(duration=DirectDuration(2.0))])
        """

    @abc.abstractmethod
    def extend_until(
        self,
        duration: core_parameters.abc.Duration.Type,
        duration_to_white_space: typing.Optional[
            typing.Callable[[core_parameters.abc.Duration], Event]
        ] = None,
        prolong_chronon: bool = True,
    ) -> Compound:
        """Prolong event until at least `duration` by appending an empty event.

        :param duration: Until which duration the event shall be extended.
            If event is already longer than or equal to given `duration`,
            nothing will be changed. For :class:`~mutwo.core_events.Concurrence`
            the default value is `None` which is equal to the duration of
            the `Concurrence`.
        :type duration: core_parameters.abc.Duration.Type
        :param duration_to_white_space: A function which creates the 'rest' or
            'white space' event from :class:`~mutwo.core_parameters.abc.Duration`.
            If this is ``None`` `mutwo` will fall back to use the default function
            which is `mutwo.core_events.configurations.DEFAULT_DURATION_TO_WHITE_SPACE`.
            Default to `None`.
        :type duration_to_white_space: typing.Optional[typing.Callable[[core_parameters.abc.Duration], Event]]
        :param prolong_chronon: If set to ``True`` `mutwo` will prolong a single
            :class:`~mutwo.core_events.Chronon` inside a :class:`~mutwo.core_events.Concurrence`.
            If set to ``False`` `mutwo` will raise an :class:`~mutwo.core_utilities.ImpossibleToExtendUntilError`
            in case it finds a single `Chronon` inside a `Concurrence`.
            This doesn't effect `Chronon` inside a `Consecution`, here we can
            simply append a new white space event.
        :type prolong_chronon: bool

        **Example:**

        >>> from mutwo import core_events
        >>> cns = core_events.Consecution([core_events.Chronon(1)])
        >>> cns.extend_until(10)
        Consecution([Chronon(duration=DirectDuration(1.0)), Chronon(duration=DirectDuration(9.0))])
        """
