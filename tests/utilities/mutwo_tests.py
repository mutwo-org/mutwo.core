import unittest

from mutwo import core_utilities


class MutwoObjectTest(unittest.TestCase):
    class T(core_utilities.MutwoObject):
        """test object"""

    def test_logger(self):
        t = self.T()
        self.assertTrue(t._logger)

        with self.assertLogs(t._logger, level="INFO") as cm:
            t._logger.info("Test")
        self.assertEqual(cm.output, ["INFO:tests.utilities.mutwo_tests.T:Test"])

        with self.assertLogs(t._logger, level="DEBUG") as cm:
            t._logger.debug("Test")
        self.assertEqual(cm.output, ["DEBUG:tests.utilities.mutwo_tests.T:Test"])

        with self.assertLogs(t._logger, level="INFO") as cm:
            # Debug message should be ignored as our logging level is
            # only 'INFO'.
            t._logger.debug("Test")
            t._logger.info("Test")
        self.assertEqual(cm.output, ["INFO:tests.utilities.mutwo_tests.T:Test"])
