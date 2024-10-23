# Changelog

## v0.4.1 (2024-10-17)

- Separate out package-wide settings into immutable constants (`const.py`) and configurable parameters (`config.py`)
- Update documentation

## v0.4.0 (2024-10-15)

- Merge [rcsbsearchapi package](https://github.com/rcsb/py-rcsbsearchapi/tree/2ba4d82ed1ff23c4ba5d07d4dec63f6f4030207d) into package as separate `rcsbapi.search` module
  - Renamed several classes and methods in this process:
    - `SequenceQuery` -> `SeqSimilarityQuery`
    - `StructureMotifResidue` -> `StructMotifResidue`
    - `Range` -> `FacetRange`
    - `rcsb_query_editor_url` -> `get_editor_link`
    - `rcsb_query_builder_url` -> `get_query_builder_link`
  - renamed `rcsb_attributes` -> `search_attributes`
- Renamed several files and classes to prevent overlap with future developments:
  - `data/query.py` -> `data/data_query.py`
  - `data/schema.py` -> `data/schema_query.py`
  - `Query()` Data API class -> `DataQuery()`
  - `Schema()` Data API class -> `DataSchema()`
  - `search/search.py` -> `search/search_query.py`
  - `search/schema.py` -> `search/search_schema.py`
- Automatically change singular "input_type" to plural when possible
- Automatically capitalize input_ids
- Add warning message if fully qualified field path not provided
- Update documentation
- Added dev_tools and updated `update_schema.py`

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