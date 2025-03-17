# PubSub Notifier

A client for sending notification messages to Google Cloud Pub/Sub topics

## Installation

### Poetry

- Add the following to your `pyproject.toml` file:

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

## License

MIT
