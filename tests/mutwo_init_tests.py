import unittest

import mutwo


class MutwoInitTest(unittest.TestCase):
    def test_find_extension(self):
        # If the namespace of mutwo has at least one entry
        # we know that it found the dummy extension.
        self.assertTrue(len(dir(mutwo)) > 0)

    def test_find_dummy_extension_module_list(self):
        # Make sure all entry points are added to muwo.
        dummy_extension_module_name_list = (
            "dummy_module_1",
            "dummy_module_2",
            "dummy_module_3",
        )
        for dummy_extension_module_name in dummy_extension_module_name_list:
            self.assertTrue(getattr(mutwo, dummy_extension_module_name))

    def test_dummy_module_1(self):
        self.assertEqual(mutwo.dummy_module_1.Dummy().speak(), "Dummy")

    def test_dummy_module_2(self):
        self.assertEqual(mutwo.dummy_module_2.ExtendedDummy().speak(), "Dummy2")

    def test_dummy_module_3(self):
        self.assertEqual(mutwo.dummy_module_3.NestedDummy().speak(), "NestedDummy")


if __name__ == "__main__":
    unittest.main()
