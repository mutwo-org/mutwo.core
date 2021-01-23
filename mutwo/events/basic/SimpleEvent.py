import copy
import types
import typing

from mutwo.events import abc
from mutwo import parameters
from mutwo.utilities import decorators


class SimpleEvent(abc.Event):
    """Event-Object, which doesn't contain other Event-Objects."""

    def __init__(self, new_duration: parameters.durations.abc.DurationType):
        self.duration = new_duration

    def __eq__(self, other: typing.Any) -> bool:
        """Test for checking if two objects are equal."""
        try:
            return self._is_equal(other) and other._is_equal(self)
        except AttributeError:
            return False

    def __repr__(self) -> str:
        attributes = (
            "{} = {}".format(attribute, getattr(self, attribute))
            for attribute in self._parameters_to_compare
        )
        return "{}({})".format(type(self).__name__, ", ".join(attributes))

    def _is_equal(self, other: typing.Any) -> bool:
        """Helper function to inspect if two SimpleEvent objects are equal."""

        for parameter_to_compare in self._parameters_to_compare:
            try:
                # if the assigned values of the specific parameter aren't
                # equal, both objects can't be equal
                if getattr(self, parameter_to_compare) != getattr(
                    other, parameter_to_compare
                ):
                    return False

            # if the other object doesn't know the essential parameter
            # mutwo assumes that both objects can't be equal
            except AttributeError:
                return False

        # if all compared parameters are equal, return True
        return True

    @property
    def _parameters_to_compare(self) -> typing.Tuple[str]:
        """Return tuple of attribute names which values define the SimpleEvent.

        The returned attribute names are used for equality check between two
        SimpleEvent objects.
        """
        return tuple(
            attribute
            for attribute in dir(self)
            # no private attributes
            if attribute[0] != "_"
            # no methods
            and not isinstance(getattr(self, attribute), types.MethodType)
        )

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, new_duration: parameters.durations.abc.DurationType):
        self._duration = new_duration

    def destructive_copy(self) -> "SimpleEvent":
        return copy.deepcopy(self)

    def get_parameter(self, parameter_name: str) -> typing.Any:
        """Return attribute if it has been assigned to the object.

        Otherwise returns None.
        """
        try:
            return getattr(self, parameter_name)
        except AttributeError:
            return None

    @decorators.add_return_option
    def set_parameter(
        self,
        parameter_name: str,
        object_or_function: typing.Union[
            typing.Callable[[parameters.abc.Parameter], parameters.abc.Parameter],
            typing.Any,
        ],
    ) -> None:
        old_parameter = self.get_parameter(parameter_name)
        try:
            new_parameter = object_or_function(old_parameter)
        except TypeError:
            new_parameter = object_or_function
        setattr(self, parameter_name, new_parameter)

    @decorators.add_return_option
    def mutate_parameter(
        self,
        parameter_name: str,
        function: typing.Union[
            typing.Callable[[parameters.abc.Parameter], None], typing.Any
        ],
    ) -> None:
        parameter = self.get_parameter(parameter_name)
        if parameter is not None:
            function(parameter)

    @decorators.add_return_option
    def cut_up(
        self,
        start: parameters.durations.abc.DurationType,
        end: parameters.durations.abc.DurationType,
    ) -> typing.Union[None, "SimpleEvent"]:
        self._assert_correct_start_and_end_values(start, end)

        duration = self.duration

        difference_to_duration = 0

        if start > 0:
            difference_to_duration += start
        if end < duration:
            difference_to_duration += duration - end

        try:
            assert difference_to_duration < duration
        except AssertionError:
            message = (
                "Can't cut up SimpleEvent '{}' with duration '{}' from (start = {} to"
                " end = {}).".format(self, duration, start, end)
            )
            raise ValueError(message)

        self.duration -= difference_to_duration
