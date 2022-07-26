import typing
import unittest

from mutwo import core_parameters


class SingleValueParameterTest(unittest.TestCase):
    class AbstractSingleValueParameter(
        core_parameters.abc.SingleValueParameter, value_name="undefined"
    ):
        pass

    class Color(
        core_parameters.abc.SingleValueParameter,
        value_name="color",
        value_return_type=str,
    ):
        def __init__(self, color: str):
            self._color = color

        @property
        def color(self) -> str:
            return self._color

    class Blue(Color):
        def __init__(self):
            super().__init__("blue")

    class Red(Color):
        def __init__(self):
            super().__init__("red")

    def test_abstract_property_error(self):
        # We shouldn't be able to instantiate class with abstract property
        self.assertRaises(TypeError, self.AbstractSingleValueParameter)

    def test_simple_subclass(self):
        orange = self.Color("orange")

        # Our property 'color' will not be overridden
        self.assertEqual(orange.color, "orange")

        orange1 = self.Color("orange")
        white = self.Color("white")

        # Two unequal colors shouldn't be equal
        self.assertNotEqual(orange, white)
        # A color and any other object shouldn't be equal
        self.assertNotEqual(orange, 100)
        self.assertNotEqual(orange, "orange")
        # Two colors should be equal
        self.assertEqual(orange, orange1)

    def test_deeper_subclass(self):
        # When inherting again there shouldn't be any
        # new abstract methods
        blue = self.Blue()
        red = self.Red()
        blue1 = self.Color("blue")
        self.assertEqual(blue, blue1)
        self.assertNotEqual(blue, red)

    def test_two_values(self):
        # Two different values should be prohibited

        def make_two_values():
            class _(self.Color, value_name="grayscale"):  # type: ignore
                pass

        self.assertRaises(Exception, make_two_values)


class SingleNumberParameterTest(unittest.TestCase):
    class Speed(
        core_parameters.abc.SingleNumberParameter,
        value_name="meter_per_seconds",
        value_return_type=float,
    ):
        def __init__(self, meter_per_seconds: float):
            self._meter_per_seconds = meter_per_seconds

        @property
        def meter_per_seconds(self) -> float:
            return self._meter_per_seconds

        @property
        def digit_to_round_to_count(self) -> typing.Optional[int]:
            return 5

    def test_float(self):
        light_speed = self.Speed(299792458.5)
        self.assertEqual(float(light_speed), 299792458.5)

    def test_int(self):
        light_speed = self.Speed(299792458.5)
        self.assertEqual(int(light_speed), 299792458)

    def test_comparison(self):
        light_speed = self.Speed(299792458)
        light_speed1 = self.Speed(299792458)
        sound_speed = self.Speed(343)

        self.assertEqual(light_speed, light_speed1)
        self.assertNotEqual(light_speed, "not_a_speed_object")
        self.assertNotEqual(light_speed, 299792458)
        self.assertTrue(light_speed > sound_speed)
        self.assertTrue(light_speed >= sound_speed)
        self.assertTrue(sound_speed < light_speed)
        self.assertTrue(sound_speed <= light_speed)
        self.assertTrue(light_speed1 <= light_speed)
        self.assertTrue(light_speed1 >= light_speed)

    def test_rounding(self):
        light_speed = self.Speed(299792458)
        light_speed1 = self.Speed(299792458.000001)
        self.assertEqual(light_speed, light_speed1)

    def test_raise_exception_for_invalid_comparison(self):
        self.assertRaises(TypeError, lambda: self.Speed(100) > "abc")


if __name__ == "__main__":
    unittest.main()
