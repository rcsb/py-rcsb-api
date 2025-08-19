"""
Configurable settings for rcsb-api

These settings can be overridden at runtime.

For example, you can turn off autocompletion warning messages by
modifying the `SUPPRESS_AUTOCOMPLETE_WARNING` setting as follows:

Example:
    from rcsbapi.config import config

    # Override the default warning suppression flag
    config.SUPPRESS_AUTOCOMPLETE_WARNING = True
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


class Config:
    API_TIMEOUT: int = 100                       # Timeout in seconds for all API calls
    MAX_RETRIES: int = 5                         # Maximum number of retries to perform per request upon failure
    RETRY_BACKOFF: int = 1                       # Delay in seconds to wait between retries; increases exponentially between retries (e.g., 1s, 2s, 4s, 8s, ...)
    SEARCH_API_REQUESTS_PER_SECOND: int = 10     # Requests per second limit for the Search API
    DATA_API_REQUESTS_PER_SECOND: int = 20       # Requests per second limit for the Data API
    DATA_API_BATCH_ID_SIZE: int = 300            # Size of batches to use for batching input ID list to Data API (reduce this if encountering timeouts or errors)
    DATA_API_MAX_CONCURRENT_REQUESTS: int = 4    # Max number of Data API requests to run concurrently (e.g., when input ID list is split into many small batches)
    DATA_API_INPUT_ID_LIMIT: int = 50_000        # Threshold for warning user that input ID list for Data API query is very large and may hinder performance
    MODEL_API_REQUESTS_PER_SECOND: int = 10      # Requests per second limit for the Model API
    SUPPRESS_AUTOCOMPLETE_WARNING: bool = False  # Turn off autocompletion warnings from being raised for Data API queries

    def __setattr__(self, name: str, value: Any) -> None:
        """Verify attribute exists when a user tries to set a configuration parameter, and ensure proper typing.
        Raises an error if user accidentally tries to create a new, unused attribute (e.g., due to a typo or misspelling),
        or sets it to an unexpected type.
        """
        # Verify attribute exists
        if not hasattr(self, name):
            raise AttributeError(f"'{name}' is not a valid attribute of Config class")

        # Enforce consistent typing
        expected_type = self.__annotations__.get(name, None)
        if expected_type and not isinstance(value, expected_type):
            raise TypeError(f"Expected type '{expected_type.__name__}' for attribute '{name}', but got '{type(value).__name__}'")
        super().__setattr__(name, value)


config = Config()
