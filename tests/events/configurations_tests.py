import typing
import unittest

try:
    import quicktions as fractions
except ImportError:
    import fractions

from mutwo import core_events
from mutwo import core_parameters


class DefaultUnknownObjectToDurationTest(unittest.TestCase):
    def setUp(self):
        self.c = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION
        self.d = core_parameters.DirectDuration

    def _test(self, value: typing.Any, result: core_parameters.abc.Duration):
        self.assertEqual(self.c(value), result)

    def _test_bad_input(self, value: typing.Any):
        self.assertRaises(NotImplementedError, self.c, value)

    def test_float(self):
        self._test(10.1, self.d(10.1))

    def test_int(self):
        self._test(2, self.d(2))

    def test_fraction(self):
        f = fractions.Fraction(1, 4)
        self._test(f, self.d(f))

    def test_str_float(self):
        self._test("3.21", self.d(3.21))

    def test_str_fraction(self):
        self._test("3/2", self.d(fractions.Fraction(3, 2)))

    def test_str_int(self):
        self._test("3", self.d(3))

    def test_str_bad(self):
        self._test_bad_input("13a")

    def test_bad_object(self):
        self._test_bad_input([1, 2, 3])
        self._test_bad_input(lambda: None)
