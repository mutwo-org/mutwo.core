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


if __name__ == "__main__":
    unittest.main()
