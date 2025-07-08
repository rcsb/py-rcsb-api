# Quickstart
This is a quickstart guide to interacting with the RCSB PDB [Sequence Coordinates API](https://sequence-coordinates.rcsb.org/#sequence-coordinates-api) using the *rcsb-api* Python package.

## Installation
Get it from PyPI:

    pip install rcsb-api

Or, download from [GitHub](https://github.com/rcsb/py-rcsb-api)

## Import
To import this module, use:
```python
import rcsbapi.sequence
```
(***Note:*** in the examples below we'll import individual classes from the `sequence` module. Whether to import the whole module or individual classes is a matter of preference.)

## Getting Started
The [RCSB PDB Sequence Coordinates API](https://sequence-coordinates.rcsb.org/#sequence-coordinates-api) allows querying for alignments between structural and sequence databases as well as protein positional annotations/features integrated from multiple resources. Alignment data is available for NCBI [RefSeq](https://www.ncbi.nlm.nih.gov/refseq/) (including protein and genomic sequences), UniProt and PDB sequences. Protein positional features are integrated from [UniProt](https://www.uniprot.org/), [CATH](https://www.cathdb.info/), [SCOPe](https://scop.berkeley.edu/) and [RCSB PDB](https://www.rcsb.org/) and collected from the [RCSB PDB Data Warehouse](https://data.rcsb.org/#data-api).

Alignments and positional features provided by this API include Experimental Structures from the [PDB](https://www.rcsb.org/) and [select Computed Structure Models (CSMs)](https://www.rcsb.org/docs/general-help/computed-structure-models-and-rcsborg#what-csms-are-available). Alignments and positional features for CSMs can be requested using the same parameters as Experimental Structures providing CSM Ids.

The API supports requests using [GraphQL](https://graphql.org/), a language for API queries. This package simplifies generating queries in GraphQL syntax. 

There are two main types of queries: `Alignments` and `Annotations`.

## Alignments
`Alignments` queries request data about alignments between an object in a supported database to all objects of another supported database.

```python
from rcsbapi.sequence import Alignments

# Fetch alignments between a UniProt Accession and PDB Entities
query = Alignments(
    db_from="UNIPROT",
    db_to="PDB_ENTITY",
    query_id="P01112",
    return_data_list=["query_sequence", "target_alignments", "alignment_length"]
)
result_dict = query.exec()
print(result_dict)
```

| Argument  | Description|
| ----------|------------|
|`db_from`  |From which structure/sequence database (see [`SequenceReference` table below](#sequencereference-and-corresponding-database-identifiers) for possible values)|
|`db_to`    |To which structure/sequence database (see [`SequenceReference` table below](#sequencereference-and-corresponding-database-identifiers) for possible values)|
|`query_id` |Sequence identifier for database specified in `db_from` (see [`SequenceReference` table below](#sequencereference-and-corresponding-database-identifiers) for examples)|
|`range`    |Optional list of two integers that can be used to filter the alignment to a particular region (e.g., `[1, 100]`)|
|`return_data_list`|Data to fetch (e.g., `["query_sequence", "target_alignments", "alignment_length"]`)|
|`suppress_autocomplete_warning`|Suppress warning message about field path autocompletion. Defaults to False.|


### SequenceReference and Corresponding Database Identifiers

The table below describes the type of database identifiers used for each `SequenceReference` value.

| `SequenceReference` | Database Identifier Description              | Example                        |
|---------------------|-----------------------------------------------|--------------------------------|
| `NCBI_GENOME`       | NCBI RefSeq Chromosome Accession              | `NC_000001`                    |
| `NCBI_PROTEIN`      | NCBI RefSeq Protein Accession                 | `NP_789765`                    |
| `UNIPROT`           | UniProt Accession                             | `P01112`                       |
| `PDB_ENTITY`        | RCSB PDB Entity Id / CSM Entity Id            | `2UZI_3` / `AF_AFP68871F1_1`   |
| `PDB_INSTANCE`      | RCSB PDB Instance Id / CSM Instance Id        | `2UZI.C` / `AF_AFP68871F1.A`   |


## Annotations
`Annotations` queries request annotation data about a sequence (e.g., residue-level annotations/features). Protein positional features are integrated from [UniProt](https://www.uniprot.org/), [CATH](https://www.cathdb.info/), [SCOPe](https://scop.berkeley.edu/) and [RCSB PDB](https://www.rcsb.org/) and collected from the [RCSB PDB Data Warehouse](https://data.rcsb.org/#data-api). 

```python
from rcsbapi.sequence import Annotations

# Fetch all positional features for a particular PDB Instance
query = Annotations(  # type: ignore
    reference="PDB_INSTANCE",
    query_id="2UZI.C",
    sources=["UNIPROT"],
    return_data_list=["target_id", "features"]
)
result_dict = query.exec()
print(result_dict)
```

| Argument  | Description|
| ----------|------------|
|`reference`|Structure/sequence database to request (see [`SequenceReference` table above](#sequencereference-and-corresponding-database-identifiers) for possible values)|
|`query_id` |Sequence identifier for database specified in `reference` (see [`SequenceReference` table above](#sequencereference-and-corresponding-database-identifiers) for examples)|
|`sources`  |Enumerated list defining the annotation collections to be requested (possible values: `"UNIPROT"`, `"PDB_ENTITY"`, `"PDB_INSTANCE"`, `"PDB_INTERFACE"`)|
|`return_data_list`|Data to fetch (e.g., `["target_id", "features"]`)|
|`filters`|Optional list of `AnnotationFilterInput` that can be used to select what annotations will be retrieved. See [Additional Examples](additional_examples.md).|
|`suppress_autocomplete_warning`|Suppress warning message about field path autocompletion. Defaults to False.|


## Additional Usage and Examples
For examples using other query types like `GroupAlignments`, `GroupAnnotations`, and `GroupAnnotationsSummary` or for examples using filters, check [Additional Examples](additional_examples.md).

## Jupyter Notebooks
A runnable jupyter notebook is available in [notebooks/sequence_coord_quickstart.ipynb](https://github.com/rcsb/py-rcsb-api/blob/master/notebooks/sequence_coord_quickstart.ipynb), or can be run online using Google Colab:
<a href="https://colab.research.google.com/github/rcsb/py-rcsb-api/blob/master/notebooks/sequence_coord_quickstart.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
