# Changelog

## v1.4.0 (2025-08-19)

- Switch from using `requests` to [`httpx`](https://www.python-httpx.org/) (Issue [#33](https://github.com/rcsb/py-rcsb-api/issues/33))
- Add asynchronous request support for Data API (`rcsbapi.data`) to speed up requests
- Add retry support for Search API (`rcsbapi.search`), Data API (`rcsbapi.data`), Model Server API (`rcsbapi.model`), and Sequence Coordinate API (`rcsbapi.sequence`) requests
- Adjust and add default settings to `rcsbapi.config` configuration
- Stop overriding logging configuration within package—this should be done by client applications (Issue [#52](https://github.com/rcsb/py-rcsb-api/issues/52))
- Fixed bug associated with `typing` observed for Python 3.8

## v1.3.0 (2025-07-23)

- Add support for [Model Server API](https://models.rcsb.org/) via new module `rcsbapi.model`. Use this to fetch structure/coordinate data from PDB entries and ligands as well as mmCIF metadata. (PR [#73](https://github.com/rcsb/py-rcsb-api/pull/73))
  - [Documentation](https://rcsbapi.readthedocs.io/en/latest/model_api/quickstart.html) and [Jupyter notebook](https://github.com/rcsb/py-rcsb-api/blob/master/notebooks/model_quickstart.ipynb) are provided
- Fixed bug with `rcsbapi.data` Data API module, in which requesting multiple data items with redundant target field names was causing them to be overwritten in the final constructed query (PR [#74](https://github.com/rcsb/py-rcsb-api/pull/74))
- Added Azure testing support for Windows (PR [#75](https://github.com/rcsb/py-rcsb-api/pull/75))
- Add model server API schema: 0.9.12
- Update search schemas: 1.50.1 -> 1.52.1
- Update data schemas: 
  - polymer_entity_instance schema 10.0.3 -> 10.0.4

## v1.2.0 (2025-07-11)

- Add support for [Sequence Coordinates API](https://sequence-coordinates.rcsb.org/) via new module `rcsbapi.sequence`. Use this to fetch alignments between sequences from different databases as well as sequence-level annotations integrated from external resources and RCSB PDB. (PRs [#46](https://github.com/rcsb/py-rcsb-api/pull/46), [#68](https://github.com/rcsb/py-rcsb-api/pull/68))
  - [Documentation](https://rcsbapi.readthedocs.io/en/latest/seq_api/quickstart.html) and [Jupyter notebook](https://github.com/rcsb/py-rcsb-api/blob/master/notebooks/sequence_coord_quickstart.ipynb) provided
  - Generalized pre-existing Data API module GraphQL schema and query generation code to be re-used by both `rcsbapi.data` and `rcsbapi.sequence` modules (no impact to user)
- Add `NestedAttributeQuery` to Search API `rcsbapi.search` module to support restricted/pair-wise grouping of nested attributes and prevent them from being automatically flattened down to the same group level as adjacent terminal nodes. Warning messages have been added to notify users of the need to make use of this for any nested attributes being included in search queries. (PR [#66](https://github.com/rcsb/py-rcsb-api/pull/66); Issue [#49](https://github.com/rcsb/py-rcsb-api/issues/49))
- Change `rcsbapi.search` Search API requests to use `POST` instead of `GET`, to handle very large query bodies that would otherwise generate massive URL lengths
- Add custom User-Agent to API request headers (`"User-Agent": "py-rcsb-api/__version__ (+https://github.com/rcsb/py-rcsb-api)"`)
- Add sequence-coordinates API schema (GraphQL; no version)
- Update search schemas: 1.49.0 -> 1.50.1
- Update data schemas: 
  - entry schema 9.0.4 -> 9.0.4
  - polymer_entity schema 10.0.5 -> 10.0.5

## v1.1.4 (2025-07-09)

- Fix: Patch schema parsing for search attributes - delete duplicate chemical attributes from structure attribute schema (following update to RCSB.org schemas in July 2025, in which chemical attributes are now merged into structure attribute schema). (Issue [#70](https://github.com/rcsb/py-rcsb-api/issues/70))

## v1.1.3 (2025-05-05)

- Fix: Update regex pattern for instances in `const.py` to support suffixes longer than one character (e.g., "1S5L.AA")

## v1.1.2 (2025-03-20)

- Update how `dataclass` attributes are created in `const.py`

## v1.1.1 (2025-03-13)

- Add missing dependency for building documentation
- Add docstrings

## v1.1.0 (2025-03-12)

- Add `ALL_STRUCTURES` object, allowing Data API queries for all PDB structures and chemical components
- Add `progress_bar` and `batch_size` parameters to Data API package's `.exec`
- Add `group` function to Search API package to enforce nested grouping
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