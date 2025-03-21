import json
import os
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
        self.assertEqual(
            call_args[0][0], "projects/test-project/topics/test-topic")

        # Get data from the first positional argument (should be bytes)
        data_bytes = call_args[0][1]
        data = json.loads(data_bytes.decode("utf-8"))
        self.assertEqual(data["type"], "test")
        self.assertEqual(data["data"]["key"], "value")

    def test_publish_message_with_custom_attributes(self):
        """Test publishing with custom attributes"""
        # Mock setup
        future = MagicMock()
        future.result.return_value = "test-message-id"
        self.client.publisher.publish.return_value = future

        # Test execution with custom attributes
        custom_attrs = {
            "publisher_project_id": "publisher-project",
            "custom_key": "custom_value",
            "another_key": "another_value"
        }
        result = self.client.publish_message(
            {"type": "test"}, attributes=custom_attrs
        )

        # Assertion
        self.assertEqual(result, "test-message-id")

        # Verify attributes were passed correctly
        call_kwargs = self.client.publisher.publish.call_args[1]
        self.assertEqual(
            call_kwargs["publisher_project_id"], "publisher-project")
        self.assertEqual(call_kwargs["custom_key"], "custom_value")
        self.assertEqual(call_kwargs["another_key"], "another_value")

    def test_publish_message_with_timeout(self):
        """Test publishing with custom timeout"""
        # Mock setup
        future = MagicMock()
        future.result.return_value = "test-message-id"
        self.client.publisher.publish.return_value = future

        # Test execution with custom timeout
        result = self.client.publish_message(
            {"type": "test"}, timeout=15.0
        )

        # Assertion
        self.assertEqual(result, "test-message-id")
        future.result.assert_called_once_with(timeout=15.0)

    def test_send_slack_notification(self):
        """Slack notification sending test"""
        # Mock setup
        future = MagicMock()
        future.result.return_value = "test-message-id"
        self.client.publisher.publish.return_value = future

        # Test execution
        attributes = {"publisher_project_id": "sender-project"}
        result = self.client.send_slack_notification(
            "#test-channel", "Test Title", "Test Body", attributes=attributes)

        # Assertion
        self.assertEqual(result, "test-message-id")

        # Get positional args (topic_path, data)
        call_args = self.client.publisher.publish.call_args
        topic_path = call_args[0][0]
        data_bytes = call_args[0][1]

        # Parse data
        data = json.loads(data_bytes.decode("utf-8"))
        self.assertEqual(data["type"], "slack")
        self.assertEqual(data["msg"]["channel"], "#test-channel")
        self.assertEqual(data["msg"]["title"], "Test Title")
        self.assertEqual(data["msg"]["body"], "Test Body")

        # Verify custom attributes were passed correctly
        kwargs = call_args[1]
        self.assertEqual(kwargs["publisher_project_id"], "sender-project")

    def test_send_slack_adds_hash_to_channel(self):
        """Test that a # is added to the channel name"""
        # Mock setup
        future = MagicMock()
        future.result.return_value = "test-message-id"
        self.client.publisher.publish.return_value = future

        # Specify the channel name without a #
        result = self.client.send_slack_notification(
            "test-channel", "Test Title", "Test Body")

        # Assertion - get data from positional args
        call_args = self.client.publisher.publish.call_args
        data_bytes = call_args[0][1]
        data = json.loads(data_bytes.decode("utf-8"))
        self.assertEqual(data["msg"]["channel"], "#test-channel")

    def test_publish_with_none_attributes(self):
        """Test publishing with None attributes"""
        # Mock setup
        future = MagicMock()
        future.result.return_value = "test-message-id"
        self.client.publisher.publish.return_value = future

        # Test execution without attributes
        result = self.client.publish_message(
            {"type": "test"}, attributes=None
        )

        # Check that no kwargs are passed except retry
        call_args = self.client.publisher.publish.call_args
        self.assertEqual(len(call_args[1]), 1)  # Only retry should be present
        self.assertIn("retry", call_args[1])

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

    @patch("google.cloud.pubsub_v1.PublisherClient")
    def test_publish_timeout_error(self, mock_publisher):
        """Test that a timeout error is handled properly"""
        client = NotificationClient("test-project", "test-topic")
        publisher = mock_publisher.return_value
        future = MagicMock()
        future.result.side_effect = TimeoutError("Operation timed out")
        publisher.publish.return_value = future

        # Check that a PublishError is raised with timeout message
        with self.assertRaises(PublishError) as context:
            client.publish_message({"type": "test"})
        self.assertIn("timed out", str(context.exception))


if __name__ == "__main__":
    unittest.main()
