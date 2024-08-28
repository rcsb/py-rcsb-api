# Changelog

## v0.3.0 (2024-08-23)

- Falls back to local schema file when fetch fails
- Supports dot separated field names for requesting data
- `get_unique_fields` deleted and replaced with `find_paths`
- `find_field_names` changed to return only field names, no descriptions
- Executing queries called with `.exec()`
- Updates to documentation
- See [PR #31](https://github.com/rcsb/py-rcsb-api/pull/31) for full details
- Updated data_api_schema.json and added all schema files on https://data.rcsb.org/#data-schema

## v0.2.0 (2024-07-25)

- Updates to Query methods
- Added GraphQL query validation
- Updates to documentation

## v0.1.0 (2024-07-22)

- First release!
- Provides Pythonic interface for interacting with RCSB.org Data API
- Automated Data API schema parsing via Schema.py
- Enables query building and execution via Query.py
- Documentation and example notebooks
- See [PR #23](https://github.com/rcsb/py-rcsb-api/pull/23) for full details