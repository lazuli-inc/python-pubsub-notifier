"""
NotificationClient test
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from pubsub_notifier import NotificationClient
from pubsub_notifier.exceptions import PublishError


class TestNotificationClient(unittest.TestCase):
    """Unit tests for NotificationClient"""

    @patch("google.cloud.pubsub_v1.PublisherClient")
    def setUp(self, mock_publisher):
        """Test setup"""
        self.mock_publisher = mock_publisher
        self.client = NotificationClient("test-project", "test-topic")
        self.client.publisher = mock_publisher.return_value

    def test_publish_message(self):
        """Basic message sending test"""
        # Mock setup
        future = MagicMock()
        future.result.return_value = "test-message-id"
        self.client.publisher.publish.return_value = future

        # Test execution
        test_message = {"type": "test", "data": {"key": "value"}}
        result = self.client.publish_message(test_message)

        # Assertion
        self.assertEqual(result, "test-message-id")
        self.client.publisher.publish.assert_called_once()

        # Verification of the published message
        call_args = self.client.publisher.publish.call_args
        topic_path, data_bytes = call_args[0]
        self.assertEqual(topic_path, "projects/test-project/topics/test-topic")

        # Decode the byte string to JSON
        data = json.loads(data_bytes.decode("utf-8"))
        self.assertEqual(data["type"], "test")
        self.assertEqual(data["data"]["key"], "value")

    def test_send_slack_notification(self):
        """Slack notification sending test"""
        # Mock setup
        future = MagicMock()
        future.result.return_value = "test-message-id"
        self.client.publisher.publish.return_value = future

        # Test execution
        result = self.client.send_slack_notification(
            "#test-channel", "Test Title", "Test Body")

        # Assertion
        self.assertEqual(result, "test-message-id")
        call_args = self.client.publisher.publish.call_args
        _, data_bytes = call_args[0]
        data = json.loads(data_bytes.decode("utf-8"))
        self.assertEqual(data["type"], "slack")
        self.assertEqual(data["msg"]["channel"], "#test-channel")
        self.assertEqual(data["msg"]["title"], "Test Title")
        self.assertEqual(data["msg"]["body"], "Test Body")

    def test_send_slack_adds_hash_to_channel(self):
        """Test that a # is added to the channel name"""
        # Mock setup
        future = MagicMock()
        future.result.return_value = "test-message-id"
        self.client.publisher.publish.return_value = future

        # Specify the channel name without a #
        result = self.client.send_slack_notification(
            "test-channel", "Test Title", "Test Body")

        # Assertion
        call_args = self.client.publisher.publish.call_args
        _, data_bytes = call_args[0]
        data = json.loads(data_bytes.decode("utf-8"))
        self.assertEqual(data["msg"]["channel"], "#test-channel")

    @patch("google.cloud.pubsub_v1.PublisherClient")
    def test_publish_error(self, mock_publisher):
        """Test that an error is raised when publishing"""
        client = NotificationClient("test-project", "test-topic")
        publisher = mock_publisher.return_value
        future = MagicMock()
        future.result.side_effect = Exception("Test error")
        publisher.publish.return_value = future

        # Check that an error is raised
        with self.assertRaises(PublishError):
            client.publish_message({"type": "test"})


if __name__ == "__main__":
    unittest.main()
