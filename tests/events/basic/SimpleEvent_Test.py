import unittest

from mutwo.events import basic


class SimpleEventTest(unittest.TestCase):
    def test_get_assigned_parameter(self):
        duration = 10
        self.assertEqual(
            basic.SimpleEvent(duration).get_parameter("duration"), duration
        )

    def test_get_not_assigned_parameter(self):
        self.assertEqual(basic.SimpleEvent(1).get_parameter("anyParameter"), None)

    def test_set_assigned_parameter_by_object(self):
        simple_event = basic.SimpleEvent(1)
        new_duration = 10
        simple_event.set_parameter("duration", new_duration)
        self.assertEqual(simple_event.duration, new_duration)

    def test_set_assigned_parameter_by_function(self):
        old_duration = 1
        simple_event = basic.SimpleEvent(old_duration)
        simple_event.set_parameter("duration", lambda old_duration: old_duration * 2)
        self.assertEqual(simple_event.duration, old_duration * 2)

    def test_set_not_assigned_parameter(self):
        simple_event = basic.SimpleEvent(1)
        new_unknown_parameter = 10
        new_unknown_parameter_name = "new"
        simple_event.set_parameter("new", new_unknown_parameter)
        self.assertEqual(
            simple_event.get_parameter(new_unknown_parameter_name),
            new_unknown_parameter,
        )

    def test_equality_check(self):
        simple_event0 = basic.SimpleEvent(2)
        simple_event1 = basic.SimpleEvent(3)
        simple_event2 = basic.SimpleEvent(2)
        simple_event3 = basic.SimpleEvent(2.3)

        self.assertEqual(simple_event0, simple_event2)
        self.assertEqual(simple_event2, simple_event0)  # different order
        self.assertEqual(simple_event0, simple_event0)
        self.assertEqual(simple_event2, simple_event2)

        self.assertNotEqual(simple_event0, simple_event1)
        self.assertNotEqual(simple_event1, simple_event0)  # different order
        self.assertNotEqual(simple_event0, simple_event3)
        self.assertNotEqual(simple_event2, simple_event3)
        self.assertNotEqual(simple_event2, simple_event2.duration)

    def test_cut_up(self):
        event0 = basic.SimpleEvent(4)
        cut_up_event0 = basic.SimpleEvent(2)

        event1 = basic.SimpleEvent(10)
        cut_up_event1 = basic.SimpleEvent(5)

        event2 = basic.SimpleEvent(5)
        cut_up_event2 = basic.SimpleEvent(1)

        event2.cut_up(2, 3)

        self.assertEqual(
            event0.cut_up(2, 4, mutate=False).duration, cut_up_event0.duration
        )
        self.assertEqual(
            event1.cut_up(0, 5, mutate=False).duration, cut_up_event1.duration
        )
        self.assertEqual(event2.duration, cut_up_event2.duration)

        # this will raise an error because the simple event isn't within the
        # asked range.
        self.assertRaises(ValueError, lambda: event0.cut_up(4, 5))
        self.assertRaises(ValueError, lambda: event0.cut_up(-2, -1))


if __name__ == "__main__":
    unittest.main()
