import unittest
from unittest.mock import patch

import keep_alive


class RunKeepAliveTests(unittest.TestCase):
    @patch("keep_alive.time.sleep")
    @patch("keep_alive.ping", side_effect=[True, True])
    def test_succeeds_without_retry(self, mock_ping, mock_sleep):
        self.assertEqual(keep_alive.run_keep_alive(attempts=3, retry_delay=1), 0)
        self.assertEqual(mock_ping.call_count, 2)
        mock_sleep.assert_not_called()

    @patch("keep_alive.time.sleep")
    @patch("keep_alive.ping", side_effect=[False, False, True, True])
    def test_retries_until_both_checks_succeed(self, mock_ping, mock_sleep):
        self.assertEqual(keep_alive.run_keep_alive(attempts=3, retry_delay=1), 0)
        self.assertEqual(mock_ping.call_count, 4)
        mock_sleep.assert_called_once_with(1)

    @patch("keep_alive.time.sleep")
    @patch("keep_alive.ping", side_effect=[False, False, False, False, False, False])
    def test_fails_after_exhausting_retries(self, mock_ping, mock_sleep):
        self.assertEqual(keep_alive.run_keep_alive(attempts=3, retry_delay=1), 1)
        self.assertEqual(mock_ping.call_count, 6)
        self.assertEqual(mock_sleep.call_count, 2)


if __name__ == "__main__":
    unittest.main()
