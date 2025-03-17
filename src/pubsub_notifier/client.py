"""
Notification client for sending messages to GCP Pub/Sub topics
"""

import json
from typing import Any, Dict, Optional, Union

from google.api_core.exceptions import GoogleAPIError
from google.cloud import pubsub_v1
from google.oauth2 import service_account

from pubsub_notifier.exceptions import ConfigurationError, PublishError


class NotificationClient:
    """
    Client for sending messages to GCP Pub/Sub topics
    """

    def __init__(
        self,
        project_id: str,
        topic_name: str,
        credentials_path: Optional[str] = None,
    ):
        """
        Initialize the NotificationClient.

        Args:
            project_id: Google Cloud project ID
            topic_name: Pub/Sub トピック名
            credentials_path: Path to the service account key file (optional)
        """
        self.project_id = project_id
        self.topic_name = topic_name
        self.topic_path = f"projects/{project_id}/topics/{topic_name}"

        # Initialize the client
        try:
            if credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                self.publisher = pubsub_v1.PublisherClient(
                    credentials=credentials)
            else:
                self.publisher = pubsub_v1.PublisherClient()
        except Exception as e:
            raise ConfigurationError(
                f"Failed to initialize Pub/Sub client: {e}")

    def publish_message(self, message: Dict[str, Any]) -> str:
        """
        Send a message to the Pub/Sub topic.

        Args:
            message: Message data that can be converted to JSON

        Returns:
            str: The ID of the published message

        Raises:
            PublishError: If the message publishing fails
        """
        # Convert the message to JSON format
        try:
            data = json.dumps(message).encode("utf-8")
        except (TypeError, ValueError) as e:
            raise PublishError(f"Failed to convert message to JSON: {e}")

        # Publish the message to Pub/Sub
        try:
            future = self.publisher.publish(self.topic_path, data)
            message_id = future.result()
            return message_id
        except GoogleAPIError as e:
            raise PublishError(f"Failed to publish message to Pub/Sub: {e}")
        except Exception as e:
            raise PublishError(f"Unexpected error occurred: {e}")

    def send_slack_notification(
        self,
        channel: str,
        title: str,
        body: str,
    ) -> str:
        """
        Send a Slack notification message.

        Args:
            channel: Slack channel name (e.g. "#general")
            title: Notification title
            body: Notification body (Slack markdown compatible)

        Returns:
            str: The ID of the published message
        """
        # Add # to the channel name if it doesn't already start with it
        if not channel.startswith("#"):
            channel = f"#{channel}"

        # Create the notification message
        message = {
            "type": "slack",
            "msg": {
                "channel": channel,
                "title": title,
                "body": body,
            },
        }

        # Publish the message to Pub/Sub
        return self.publish_message(message)
