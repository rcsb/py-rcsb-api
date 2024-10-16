"""
Configurable settings for rcsb-api

These settings can be overridden at runtime.

For example, you can turn off autocompletion warning messages by modifying
the `SUPPRESS_AUTOCOMPLETE_WARNING` setting as follows:

Example:
    from rcsbapi.config import config

    # Override the default timeout value
    config.SUPPRESS_AUTOCOMPLETE_WARNING = True
"""
import logging

logger = logging.getLogger(__name__)


class Config:
    DATA_API_TIMEOUT: int = 60
    SEARCH_API_REQUESTS_PER_SECOND: int = 10
    SUPPRESS_AUTOCOMPLETE_WARNING: bool = False

    def __setattr__(self, name, value):
        """Override `__setattr__` to verify attribute exists when a user tries to set a configuration parameter.
        Raises an error if users accidentally try to create a new, unused attribute (e.g., due to a typo or misspelling).
        """
        if not hasattr(self, name):
            raise AttributeError(f"'{name}' is not a valid attribute of Config class")
        super().__setattr__(name, value)


config = Config()
