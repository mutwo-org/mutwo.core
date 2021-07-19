import os
import unittest

from mutwo.utilities import decorators


class DecoratorsTest(unittest.TestCase):
    def test_add_return_option(self):
        class TestClass(object):
            a = 10

            @decorators.add_return_option
            def duplicate(self) -> None:
                self.a *= 2

        test_object = TestClass()

        # with mutate=False
        self.assertEqual(test_object.duplicate(mutate=False).a, TestClass.a * 2)

        # with mutate=True
        test_object.duplicate()
        self.assertEqual(test_object.a, TestClass.a * 2)

    def test_compute_lazy(self):
        global nth_calculation
        nth_calculation = 0
        pickle_path = "tests/utilities/compute_lazy_test.pickle"

        @decorators.compute_lazy(path=pickle_path)
        def make_complex_calculation(_=0):
            globals()["nth_calculation"] += 1
            return globals()["nth_calculation"]

        # file shouldn't exist before making calculation
        self.assertFalse(os.path.isfile(pickle_path))

        make_complex_calculation()

        # file should exist after making the first calculation
        self.assertTrue(os.path.isfile(pickle_path))

        make_complex_calculation()

        # the second time when the function got called
        # it shouldn't run the actual function anymore
        self.assertEqual(nth_calculation, 1)

        # but if the input changes, mutwo will calculate again!
        make_complex_calculation(100)
        self.assertEqual(nth_calculation, 2)

        # remove no longer needed global variable
        # and file which became saved in between
        del nth_calculation
        os.remove(pickle_path)


if __name__ == "__main__":
    unittest.main()
