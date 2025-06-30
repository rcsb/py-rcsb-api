# Quickstart

## Installation
Get it from PyPI:

    pip install rcsb-api

Or, download from [GitHub](https://github.com/rcsb/py-rcsb-api)

## Import
To import this package, use:
```python
import rcsbapi.sequence
# NOTE: in the below examples we'll import individual classes from the `sequence` module
# Whether to import the whole module or individual classes is a matter of preference
```

## Getting Started
<!-- TODO: can edit the below text -->
The [RCSB PDB Sequence Coordinates API](https://sequence-coordinates.rcsb.org/#sequence-coordinates-api) allows querying for alignments between structural and sequence databases, integrating protein positional features from multiple resources. The API supports requests using [GraphQL](https://graphql.org/), a language for API queries. This package simplifies generating queries in GraphQL syntax. 

<!-- TODO: Add chart of enumerated query structure/sequence databases -->

There are two main types of queries: `Alignments` and `Annotations`

## Alignments
`Alignments` queries request data about alignments between an object in a supported database to all objects of another supported database.

```python
from rcsbapi.sequence import Alignments

# Fetch alignments between a UniProt Accession and PDB Entities
query = Alignments(
    from_="UNIPROT",
    to="PDB_ENTITY",
    queryId="P01112",
    return_data_list=["query_sequence", "target_alignments", "aligned_regions"]
)
query.exec()
```

| Argument  | Description|
| ----------|------------|
|`from_`    |From which structure/sequence database|
|`to`       |To which structure/sequence database|
|`queryId`  |Sequence identifier for database specified in `from_`|
|`range`    |Optional integer list (2-tuple) to filter annotations that fall in a particular region|
|`return_data_list`|Fields to request data for|
|`suppress_autocomplete_warning`|Suppress warning message about field path autocompletion. Defaults to False.|

### Pagination
Some GraphQL fields support pagination using standard parameters: first and offset.
These parameters are commonly used to limit or paginate results from a list-type field. For example:

```python
from rcsbapi.sequence.seq_query import Alignments

query_obj = Alignments(
    from_="NCBI_PROTEIN",
    to="PDB_ENTITY",
    queryId="XP_642496",
    range=[1, 100],
    return_data_list=["target_alignments"],
    data_list_args={
        "target_alignments": {
            "first": 10,
            "offset": 5
        },
    }
)
query_obj.exec()
```

## Annotations
`Annotations`

```python
from rcsbapi.sequence import Annotations

# Fetch all positional features for a particular PDB Instance
query = Annotations(  # type: ignore
    reference="PDB_INSTANCE",
    sources=["UNIPROT"],
    queryId="2UZI.C",
    return_data_list=["target_id", "features"]
)
query.exec()
```

| Argument  | Description|
| ----------|------------|
|`reference`|Structure/sequence database to request|
|`sources`  |Enumerated list defining the annotation collections to be requested|
|`queryId`  |Sequence identifier for database specified in `reference`|
|`return_data_list`|Fields to request data for|
|`filters`|Optional list of `AnnotationFilterInput` that can be used to select what annotations will be retrieved. See [Additional Examples](/docs/seq_api/additional_examples.md).|
|`suppress_autocomplete_warning`|Suppress warning message about field path autocompletion. Defaults to False.|

Valid Inputs for `reference`
- `"UNIPROT"`
- `"PDB_ENTITY"`
- `"PDB_INSTANCE"`

## Additional Examples
For examples using other query types like `GroupAlignments`, `GroupAnnotations`, and `GroupAnnotationsSummary` or for examples using filters, check [Additional Examples](/docs/seq_api/additional_examples.md).

## Jupyter Notebooks
<!-- TODO: add Jupyter notebooks here -->