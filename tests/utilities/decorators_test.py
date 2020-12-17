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


if __name__ == "__main__":
    unittest.main()
