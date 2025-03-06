# Changelog
## v1.1.0 (2025-03-03)

- Add `ALL_STRUCTURES` object, allowing Data API queries for all structures in the PDB
- Add `progress_bar` and `batch_size` parameters to Data API package's `.exec`
- Add `group` function to Search API package
- Update README with new citation information
- Update search schemas: 1.48.0 -> 1.49.0
- Update data schemas: 
  - entry schema 9.0.3 -> 9.0.4
  - polymer_entity_instance schema 10.0.2 -> 10.0.3
  - nonpolymer_entity_instance schema 10.0.0 -> 10.0.1

## v1.0.1 (2025-01-17)

- Add import to `const.py` for compatibility with Python 3.8
- Update search schemas: 1.47.7 -> 1.48.0

## v1.0.0 (2024-11-6)

- Release version 1.0.0 of package
- Update search schemas: 1.47.6 -> 1.47.7
- Update data schemas: 
  - entry schema 9.0.2 -> 9.0.3
  - chem_comp schema 7.1.3 -> 7.1.4
- Update documentation

## v0.5.0 (2024-10-28)

- Separate out package-wide settings into immutable constants (`const.py`) and configurable parameters (`config.py`)
- Renamed `rcsb_attributes` -> `search_attributes`
- Automatically capitalize input_ids
- Added `dev_tools` directory and updated `update_schema.py`
- Search API `chemical_schema` and `structure_schema` at v1.47.6
- Update documentation

## v0.4.0 (2024-10-15)

- Merge [rcsbsearchapi package](https://github.com/rcsb/py-rcsbsearchapi/tree/2ba4d82ed1ff23c4ba5d07d4dec63f6f4030207d) into package as separate `rcsbapi.search` module
  - Renamed several classes and methods in this process:
    - `SequenceQuery` -> `SeqSimilarityQuery`
    - `StructureMotifResidue` -> `StructMotifResidue`
    - `Range` -> `FacetRange`
    - `rcsb_query_editor_url` -> `get_editor_link`
    - `rcsb_query_builder_url` -> `get_query_builder_link`
- Renamed several files and classes to prevent overlap with future developments:
  - `data/query.py` -> `data/data_query.py`
  - `data/schema.py` -> `data/schema_query.py`
  - `Query()` Data API class -> `DataQuery()`
  - `Schema()` Data API class -> `DataSchema()`
  - `search/search.py` -> `search/search_query.py`
  - `search/schema.py` -> `search/search_schema.py`
- Automatically change singular "input_type" to plural when possible
- Add warning message if fully qualified field path not provided
- Update documentation

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