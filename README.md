# PubSub Notifier

A client for sending notification messages to Google Cloud Pub/Sub topics.

## Installation

### Poetry

Add the following to your `pyproject.toml` file:

```toml
[tool.poetry.dependencies]
pubsub-notifier = {git = "https://github.com/lazuli-inc/python-pubsub-notifier.git", rev = "main"}
```

## Usage

### Basic usage

```python
from pubsub_notifier import NotificationClient

# Initialize the client
client = NotificationClient(
    project_id="your-gcp-project-id",
    topic_name="your-pubsub-topic-name"  # Pub/Sub topic name
)

# Send a Slack notification
client.send_slack_notification(
    channel="#your-channel",
    title="System Notification",
    body="*Important Notice*\n\n• System Maintenance Scheduled\n• Tomorrow 13:00-15:00\n• Impact: None"
)

# Send a custom message
client.publish_message({
    "type": "custom",
    "custom_data": {
        "key1": "value1",
        "key2": "value2"
    }
})
```

### Advanced Configuration

The client supports additional configuration options:

```python
from pubsub_notifier import NotificationClient
from google.api_core.retry import Retry

# Advanced client configuration
client = NotificationClient(
    project_id="your-gcp-project-id",  # Project where topic exists
    topic_name="your-pubsub-topic-name",
    credentials_path="/path/to/service-account-key.json",
    timeout=60.0,  # Global timeout in seconds
    retry=Retry(
        initial=1.0,
        maximum=60.0,
        multiplier=2.0,
        predicate=Exception
    )
)

# Send message with custom attributes and timeout
client.send_slack_notification(
    channel="#alerts",
    title="Critical Alert",
    body="Urgent: Service unavailable",
    attributes={
        "publisher_project_id": "sending-project-id",  # Explicitly set publisher project
        "severity": "critical",
        "environment": "production",
        "team": "infrastructure"
    },
    timeout=10.0  # Override timeout for this specific operation
)
```

### Custom Message Attributes

You can add custom attributes to your messages:

```python
# Include publisher project ID in attributes (recommended for cross-project setups)
client.send_slack_notification(
    channel="#alerts",
    title="System Alert",
    body="Database backup failed",
    attributes={
        "publisher_project_id": "my-publisher-project",  # Source project ID
        "severity": "warning",
        "component": "database"
    }
)
```

### Authentication

Authentication is done using Google Cloud credentials. The following methods are available for setting up credentials:

1. Use application default credentials (ADC):

   ```bash
   gcloud auth application-default login
   ```

2. Use a service account key file:

   ```python
   client = NotificationClient(
       project_id="your-gcp-project-id",
       topic_name="notification",
       credentials_path="/path/to/service-account-key.json"
   )
   ```

3. For local development with a Pub/Sub emulator:

   ```bash
   export PUBSUB_EMULATOR_HOST=localhost:8085
   ```

## Message format

### Slack notification message

When sending a notification to Slack, the following message format is created:

```json
{
  "type": "slack",
  "msg": {
    "channel": "#channel-name",
    "title": "Message Title",
    "body": "Message body with *markdown* support"
  }
}
```

### Message Attributes

You can add custom attributes to your messages by using the `attributes` parameter:

```python
client.send_slack_notification(
    channel="#channel",
    title="Title",
    body="Body",
    attributes={
        "publisher_project_id": "my-project-id",  # Recommended for identifying the source
        "severity": "info",
        "environment": "production"
    }
)
```

## Development

### Setup

```bash
# Install the development environment
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Local Development with Emulator

You can use the Pub/Sub Emulator for local development:

```bash
# Start the emulator
gcloud beta emulators pubsub start --project=your-project-id

# Configure environment to use the emulator
$(gcloud beta emulators pubsub env-init)
```

## License

MIT
