# Customizing Configuration Settings

There are a handful of global settings that are configurable via the `rcsbapi.config` object. 

### Default settings

The default configuration settings are as follows:

| Configuration Setting              | Default Value | Description                                                                                                     |
| ---------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------- |
| `API_TIMEOUT`                      | 100           | Timeout in seconds for all API calls                                                                            |
| `MAX_RETRIES`                      | 5             | Maximum number of retries to perform per request upon failure                                                   |
| `RETRY_BACKOFF`                    | 1             | Delay in seconds to wait between retries; increases exponentially between retries (e.g., 1s, 2s, 4s, 8s, ...)   |
| `SEARCH_API_REQUESTS_PER_SECOND`   | 10            | Requests per second limit for the Search API                                                                    |
| `DATA_API_REQUESTS_PER_SECOND`     | 20            | Requests per second limit for the Data API                                                                      |
| `DATA_API_BATCH_ID_SIZE`           | 300           | Size of batches to use for batching input ID list to Data API (reduce this if encountering timeouts or errors)  |
| `DATA_API_MAX_CONCURRENT_REQUESTS` | 4             | Max number of Data API requests to run concurrently (e.g., when input ID list is split into batches)            |
| `DATA_API_INPUT_ID_LIMIT`          | 50_000        | Threshold for warning user that input ID list for Data API query is very large and may take a while to complete |
| `MODEL_API_REQUESTS_PER_SECOND`    | 10            | Requests per second limit for the Model API                                                                     |
| `SUPPRESS_AUTOCOMPLETE_WARNING`    | `False`       | Turn off autocompletion warnings from being raised for Data API queries                                         |


### Overriding settings
You are free to customize these settings as you wish; however, we caution against changing them significantly as doing so may lead to detrimental effects on performance (e.g., increasing the number of requests per second too much may exceed our API server rate limits, resulting in 429s being issued). 

These settings can be overridden as follows:

```python
from rcsbapi.config import config

# Override the default batch size for Data API queries
config.DATA_API_BATCH_ID_SIZE = 100
```
