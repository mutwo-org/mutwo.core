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

"""Module for mutwo specific exceptions."""

__all__ = (
    "CannotSetDurationOfEmptyCompound",
    "AlreadyDefinedValueNameError",
    "InvalidAverageValueStartAndEndWarning",
    "InvalidStartValueError",
    "InvalidPointError",
    "ImpossibleToPutInError",
    "ImpossibleToSquashInError",
    "ImpossibleToSlideInError",
    "ImpossibleToExtendUntilError",
    "IneffectiveExtendUntilError",
    "InvalidStartAndEndValueError",
    "InvalidCutOutStartAndEndValuesError",
    "SplitUnavailableChildError",
    "EmptyEnvelopeError",
    "ConcatenationError",
    "NoTagError",
    "SplitError",
    "InvalidAbsoluteTime",
    "NoSplitTimeError",
    "CannotParseError",
)


class CannotSetDurationOfEmptyCompound(Exception):
    def __init__(self):
        super().__init__(
            "You tried to set the duration of a Compound "
            "(e.g. 'Consecution' or 'Concurrence') "
            "which doesn't have any child events. This"
            " is impossible, because the duration of a 'Compound'"
            " is simply the sum of its consuentially ordered child events."
        )


class AlreadyDefinedValueNameError(Exception):
    def __init__(self, cls):
        super().__init__(
            f"Confusing setup in class '{cls}' which inherits from "
            "'SingleValueParameter'. Found already a defined value for"
            " 'value_name'. SingleValueParameter instances can only "
            "have one value!"
        )


class InvalidStartValueError(Exception):
    def __init__(
        self,
        start,
        duration,
    ):
        super().__init__(
            f"Invalid value for start = '{start}' in 'squash_in' call "
            f"for event with duration = '{duration}'!"
            " Start has to be equal or smaller than the events duration."
        )


class InvalidAverageValueStartAndEndWarning(RuntimeWarning):
    def __init__(self):
        super().__init__(
            "Average value for range where start == end is equal to"
            " envelope.value_at(start)!"
        )


class InvalidPointError(Exception):
    def __init__(self, point, point_count):
        super().__init__(
            f"Found invalid point: '{point}' with {point_count} "
            "items! Points should have two or three items."
        )


class ImpossibleToPutInError(TypeError):
    def __init__(self, event_to_be_put_into, event_to_put_in, method_name):
        m = method_name
        super().__init__(
            f"Can't {m} '{event_to_put_in}' in '{event_to_be_put_into}'. "
            "Does the Concurrence contain Chronons or events that inherit"
            f" from Chronon? For being able to {m} in, the"
            " Concurrence needs to only contain Consecutions or"
            " Concurrences."
        )


class ImpossibleToSquashInError(ImpossibleToPutInError):
    def __init__(self, event_to_be_squashed_into, event_to_squash_in):
        super().__init__(event_to_be_squashed_into, event_to_squash_in, "squash")


class ImpossibleToSlideInError(TypeError):
    def __init__(self, event_to_be_slided_into, event_to_slide_in):
        super().__init__(event_to_be_slided_into, event_to_slide_in, "slide")


class ImpossibleToExtendUntilError(TypeError):
    def __init__(self, event_to_extend_until):
        super().__init__(
            f"Can't extend '{event_to_extend_until}' of type"
            f"'{type(event_to_extend_until)}' which resides inside a "
            "Concurrence. Set 'prolong_chronon' to 'True' in"
            "case you want chronons to be prolonged."
        )


class IneffectiveExtendUntilError(ValueError):
    def __init__(self, event_to_extend_until):
        super().__init__(
            f"Can't extend empty event '{event_to_extend_until}' of type"
            f"'{type(event_to_extend_until)}'. If you want to extend "
            "a Concurrence you should first append an empty "
            "Consecution to your Concurrence."
        )


class InvalidStartAndEndValueError(Exception):
    def __init__(self, start, end):
        super().__init__(
            f"Invalid values for start and end property (start = '{start}' "
            f"and end = '{end}')!"
            " Value for 'end' has to be bigger than value for 'start'."
        )


class InvalidCutOutStartAndEndValuesError(Exception):
    def __init__(self, start, end, chronon, duration):
        super().__init__(
            f"Can't cut out Chronon '{chronon}' with "
            f"duration '{duration}' from"
            f" (start = {start} to end = {end})."
        )


class SplitError(Exception):
    def __init__(self, absolute_time: "core_parameters.abc.Duration"):
        super().__init__(f"Can't split event at absolute time '{absolute_time}'.")


class SplitUnavailableChildError(Exception):
    def __init__(self, absolute_time: "core_parameters.abc.Duration"):
        super().__init__(
            f"Can't split child at absolute time '{absolute_time}'. There is no child"
            " event available at the requested time."
        )


class EmptyEnvelopeError(Exception):
    def __init__(self, envelope, method):
        super().__init__(f"Can't call '{method}' on empty envelope '{envelope}'!")


class ConcatenationError(TypeError):
    def __init__(self, ancestor, event):
        super().__init__(
            f"Can't concatenate event '{event}' to event '{ancestor}' "
            f"of type '{type(ancestor)}'. It is only possible to"
            " concatenate a new event to events which are instances of "
            "Consecution or Concurrence. To fix this bug you can"
            f" put your event '{ancestor}' inside a Consecution or"
            " a Concurrence."
        )


class NoTagError(Exception):
    def __init__(self, event_without_tag):
        super().__init__(
            "It's not possible to concatenate an event "
            "with the 'concatenate_by_tag' method if not "
            "all child events have tags != None. Here 'mutwo' detected the "
            f"child event '{str(event_without_tag)[:50]}...' "
            "which has a tag attribute that is set to 'None'."
        )


class InvalidAbsoluteTime(Exception):
    def __init__(self, t):
        super().__init__(
            f"Duration '{t}' is smaller than 0 and can therefore not "
            "represent an absolute time. The absolute time line starts "
            "from 0 until +inf and therefore the smallest absolute time is 0."
        )


class NoSplitTimeError(Exception):
    def __init__(self):
        super().__init__("Nothing to split (no split time given)!")


class CannotParseError(NotImplementedError):
    def __init__(self, o, parse_type):
        super().__init__(f"Can't parse '{o}' of type '{type(o)}' to '{parse_type}'!")
