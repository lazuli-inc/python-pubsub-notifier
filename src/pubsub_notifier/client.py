import json
import os
from typing import Any, Dict, Optional, Union

from google.api_core.exceptions import GoogleAPIError
from google.api_core.retry import Retry
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
        timeout: Optional[float] = 30.0,
        retry: Optional[Retry] = None,
    ):
        """
        Initialize the NotificationClient.

        Args:
            project_id: Google Cloud project ID where the Pub/Sub topic exists
            topic_name: Pub/Sub topic name
            credentials_path: Path to the service account key file (optional)
            timeout: Timeout for Pub/Sub operations in seconds (default: 30.0)
            retry: Retry configuration for Pub/Sub operations (optional)
        """
        self.project_id = project_id
        self.topic_name = topic_name
        self.topic_path = f"projects/{project_id}/topics/{topic_name}"
        self.timeout = timeout
        self.retry = retry

        # Initialize the client
        try:
            client_options = {"api_endpoint": os.environ.get(
                "PUBSUB_EMULATOR_HOST", None)}

            if credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                self.publisher = pubsub_v1.PublisherClient(
                    credentials=credentials,
                    client_options=client_options if client_options["api_endpoint"] else None,
                )
            else:
                self.publisher = pubsub_v1.PublisherClient(
                    client_options=client_options if client_options["api_endpoint"] else None,
                )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to initialize Pub/Sub client: {e}")

    def publish_message(
        self,
        message: Dict[str, Any],
        attributes: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> str:
        """
        Send a message to the Pub/Sub topic.

        Args:
            message: Message data that can be converted to JSON
            attributes: Additional attributes to attach to the message (optional)
            timeout: Custom timeout for this specific operation (overrides client timeout)

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

        # Use the specified timeout or fall back to client timeout
        operation_timeout = timeout if timeout is not None else self.timeout

        # Prepare publish arguments
        publish_kwargs = {"retry": self.retry}

        # Add attributes if provided
        if attributes is not None:
            publish_kwargs.update(attributes)

        # Publish the message to Pub/Sub
        try:
            future = self.publisher.publish(
                self.topic_path,
                data,
                **publish_kwargs
            )
            message_id = future.result(timeout=operation_timeout)
            return message_id
        except GoogleAPIError as e:
            raise PublishError(f"Failed to publish message to Pub/Sub: {e}")
        except TimeoutError:
            raise PublishError(
                f"Operation timed out after {operation_timeout} seconds")
        except Exception as e:
            raise PublishError(f"Unexpected error occurred: {e}")

    def send_slack_notification(
        self,
        channel: str,
        title: str,
        body: str,
        attributes: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> str:
        """
        Send a Slack notification message.

        Args:
            channel: Slack channel name (e.g. "#general")
            title: Notification title
            body: Notification body (Slack markdown compatible)
            attributes: Additional attributes to attach to the message (optional)
            timeout: Custom timeout for this operation (overrides client timeout)

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
        return self.publish_message(message, attributes, timeout)
