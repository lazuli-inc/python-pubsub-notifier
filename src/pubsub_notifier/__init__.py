"""
PubSub Notifier - A client for sending notification messages to GCP Pub/Sub topics
"""

from pubsub_notifier.client import NotificationClient
from pubsub_notifier.exceptions import NotifierException

__version__ = "0.0.1"
__all__ = ["NotificationClient", "NotifierException"]
