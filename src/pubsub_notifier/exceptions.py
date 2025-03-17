"""
Exception definition module
"""


class NotifierException(Exception):
    """Base exception for notification processing"""

    pass


class ConfigurationError(NotifierException):
    """Error in configuration"""

    pass


class PublishError(NotifierException):
    """Error publishing to Pub/Sub"""

    pass
