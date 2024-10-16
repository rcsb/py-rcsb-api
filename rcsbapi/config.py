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
        if not hasattr(self, name):
            logger.error("Attribute name '%s' not a member of Config class", name)
            # raise AttributeError(f"Attribute name '{name}' not a member of Config class")
        super().__setattr__(name, value)


config = Config()
