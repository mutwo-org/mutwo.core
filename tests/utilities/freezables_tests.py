import unittest

from mutwo import core_utilities


class FreeezableTest(unittest.TestCase):
    def setUp(self):
        self.f = core_utilities.Freezable()

    def test_freeze_needs_liquiditiy(self):
        self.f.freeze()
        self.assertRaises(core_utilities.FrozenError, self.f.freeze)

    def test_defrost_needs_solidity(self):
        self.assertRaises(core_utilities.NotFrozenError, self.f.defrost)

    def test_freeze_setattribute(self):
        self.f.a = 10
        self.assertEqual(self.f.a, 10)

        self.f.freeze()

        def set_a():
            self.f.a = 20

        # Prohibited to override
        self.assertRaises(core_utilities.FrozenError, set_a)
        # Should keep the same, nothing should have changed.
        self.assertEqual(self.f.a, 10)

    def test_freezeable_attribute(self):
        self.f.t = T(1)
        self.f.t.a = 10
        self.f.freeze()

        def set_a():
            self.f.t.a = 1

        self.assertRaises(core_utilities.FrozenError, set_a)

        f2 = self.f.defrost()
        f2.t.a = 1


class FreezableChildTest(unittest.TestCase):
    def setUp(self):
        self.default_a = 1
        self.t = T(self.default_a)

    def test_freezable_property_unfrozen(self):
        self.assertEqual(self.t.b, 10000)
        # After resetting 'a', the returned value should change.
        self.t.a = 2
        self.assertEqual(self.t.b, 20000)

    def test_freezable_property_frozen(self):
        self.t.freeze()
        self.assertEqual(self.t.b, 10000)

        # Even hacking 'T' by resetting 'a' shouldn't make a difference:
        # 'b' has already been cached and shouldn't be recalculated.
        object.__setattr__(self.t, "a", 2)
        self.assertEqual(self.t.b, 10000)

    def test_needs_solidity(self):
        self.assertRaises(core_utilities.NotFrozenError, self.t.needs_solidity)
        self.t.freeze()
        self.assertEqual(self.t.needs_solidity(), 1)
        t2 = self.t.defrost()
        self.assertRaises(core_utilities.NotFrozenError, t2.needs_solidity)

    def test_needs_liquiditiy(self):
        self.assertEqual(self.t.needs_liquiditiy(), 1)
        self.t.freeze()
        self.assertRaises(core_utilities.FrozenError, self.t.needs_liquiditiy)
        t2 = self.t.defrost()
        self.assertEqual(t2.needs_liquiditiy(), 1)

    def test_freezable_property_unsettable(self):
        """A method decorated with 'freezable_property' should be unsettable, like @property."""

        def set_b():
            self.t.b = 20

        self.assertRaises(AttributeError, set_b)


class FreezableListTest(unittest.TestCase):
    def setUp(self):
        self.ls = core_utilities.FreezableList([T(1), 1, 2, 3])

    def test_needs_liquiditiy(self):
        dtuple = (
            ("__setitem__", 0, 1),
            ("__delitem__", 0),
            ("clear",),
            ("insert", 1, 0),
            ("extend", [1, 2, 3]),
            ("append", 1),
            ("remove", 1),
            ("pop",),
            ("sort",),
            ("reverse",),
        )

        def run_success(ls):
            for d in dtuple:
                f, *args = d
                getattr(ls, f)(*args)

        def run_failure(ls):
            for d in dtuple:
                f, *args = d
                self.assertRaises(core_utilities.FrozenError, getattr(ls, f), *args)

        run_success(self.ls)
        self.ls.freeze()
        run_failure(self.ls)
        ls2 = self.ls.defrost()
        run_success(ls2)

    def test_frozen_child(self):
        self.ls[0].a = 20
        self.ls.freeze()

        def set_a():
            self.ls[0].a = 1

        self.assertRaises(core_utilities.FrozenError, set_a)

        ls2 = self.ls.defrost()
        ls2[0].a = 1


class freezable_list_Test(unittest.TestCase):
    def test_ignored_method(self):
        @core_utilities.freezable_list("append", "extend")
        class T(core_utilities.Freezable, list):
            def __init__(self, *args, **kwargs):
                list.__init__(self, *args, **kwargs)
                core_utilities.Freezable.__init__(self)

            def append(self, v):
                return v

            @core_utilities.needs_liquiditiy
            def extend(self, v):
                return v

            def insert(self, i, v):
                return v

        t = T([1, 2, 3])

        # Ignored methods shouldn't be overridden
        self.assertEqual(t.append(1), 1)
        self.assertEqual(t.extend(1), 1)

        t.freeze()
        # Other methods but the ignored methods shouldn't be affected
        self.assertRaises(core_utilities.FrozenError, t.insert, 0, 1)

        # Ignored methods shouldn't be affected by freezability...
        self.assertEqual(t.append(1), 1)
        # ...unless they explicitly declare it
        self.assertRaises(core_utilities.FrozenError, t.extend, 0)


class T(core_utilities.Freezable):
    def __init__(self, a: float):
        super().__init__()
        self.a = a

    @core_utilities.freezable_property
    def b(self):
        return self.a * 10000

    @core_utilities.needs_solidity
    def needs_solidity(self):
        return 1

    @core_utilities.needs_liquiditiy
    def needs_liquiditiy(self):
        return 1
