import unittest

from mutwo.events import basic


class SequentialEventTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sequence = basic.SequentialEvent(
            [basic.SimpleEvent(1), basic.SimpleEvent(2), basic.SimpleEvent(3)]
        )

    def test_get_duration(self):
        self.assertEqual(self.sequence.duration, 6)

    def test_set_duration(self):
        self.sequence.duration = 3
        self.assertEqual(self.sequence[0].duration, 0.5)
        self.assertEqual(self.sequence[1].duration, 1)
        self.assertEqual(self.sequence[2].duration, 1.5)

    def test_get_absolute_times(self):
        result = tuple(self.sequence.absolute_times)
        self.assertEqual(result, (0, 1, 3))

    def test_get_event_at(self):
        result = self.sequence.get_event_at(1.5)
        self.assertEqual(result, self.sequence[1])

    def test_cut_up(self):
        result0 = basic.SequentialEvent(
            [basic.SimpleEvent(0.5), basic.SimpleEvent(2), basic.SimpleEvent(2)]
        )
        result1 = basic.SequentialEvent([basic.SimpleEvent(1)])
        self.assertEqual(
            [event.duration for event in result0],
            [event.duration for event in self.sequence.cut_up(0.5, 5, mutate=False)],
        )
        self.assertEqual(
            [event.duration for event in result1],
            [event.duration for event in self.sequence.cut_up(1, 2, mutate=False)],
        )


if __name__ == "__main__":
    unittest.main()
