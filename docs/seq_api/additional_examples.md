# Additional Examples
Several of the examples below come from [RCSB PDB Sequence Coordinates API documentation](https://sequence-coordinates.rcsb.org/#examples).

## Alignments Query with Range
Filter alignments to a particular range:
```python
from rcsbapi.sequence import Alignments

# Only return alignments data that fall in given range
query = Alignments(
    db_from="NCBI_PROTEIN",
    db_to="PDB_ENTITY",
    query_id="XP_642496",
    range=[1, 100],
    return_data_list=["target_alignments"]
)
query.exec()
```

## Annotations Query with Filter
You can use the `filters` argument in combination with `AnnotationFilterInput` to select which annotations to retrieve.

For example, to select just the binding site annotations:
```python
from rcsbapi.sequence import Annotations, AnnotationFilterInput

# Fetch protein-ligand binding sites for PDB Instances of UniProt Q6P1M3
query = Annotations(
    reference="UNIPROT",
    query_id="Q6P1M3",
    sources=["PDB_INSTANCE"],
    filters=[
        AnnotationFilterInput(
            field="TYPE",
            operation="EQUALS",
            values=["BINDING_SITE"],
            source="PDB_INSTANCE"
        )
    ],
    return_data_list=["target_id", "features"]
)
query.exec()
```

## GroupAlignments
Use `GroupAlignments` to get alignments for groups of sequences (e.g., for [UniProt P01112](https://www.rcsb.org/groups/sequence/polymer_entity/P01112)).

```python
from rcsbapi.sequence import GroupAlignments

query = GroupAlignments(
    group="MATCHING_UNIPROT_ACCESSION",
    group_id="P01112",
    return_data_list=["target_alignments.aligned_regions", "target_id"],
)
query.exec()
```

### GroupAlignments with Filter
To filter the results down to specific set of PDB entity IDs, use the `filter` option:

```python
from rcsbapi.sequence import GroupAlignments

query = GroupAlignments(
    group="MATCHING_UNIPROT_ACCESSION",
    group_id="P01112",
    return_data_list=["target_alignments.aligned_regions", "target_id"],
    filter=["8CNJ_1", "8FG4_1"]
)
query.exec()
```

## GroupAnnotations
Use `GroupAnnotations` to get annotations for groups of sequences.

```python
from rcsbapi.sequence import GroupAnnotations

query = GroupAnnotations(
    group="MATCHING_UNIPROT_ACCESSION",
    group_id="P01112",
    sources=["PDB_ENTITY"],
    return_data_list=["features.name","features.feature_positions", "target_id"]
)
query.exec()
```

### GroupAnnotations with Filter
Use the `filters` argument in combination with `AnnotationFilterInput` to select which annotations to retrieve.

```python
from rcsbapi.sequence import GroupAnnotations, AnnotationFilterInput

# Fetch only "BINDING_SITE" annotations from PDB instances
query = GroupAnnotations(
    group="MATCHING_UNIPROT_ACCESSION",
    group_id="P01112",
    sources=["PDB_INSTANCE"],
    filters=[
        AnnotationFilterInput(
            field="TYPE",
            operation="EQUALS",
            values=["BINDING_SITE"],
            source="PDB_INSTANCE"
        )
    ],
    return_data_list=["features.name", "features.type", "features.feature_positions", "target_id"],
)
query.exec()
```

## GroupAnnotationsSummary
Use `GroupAnnotationsSummary` to get annotations summaries for groups of sequences.

```python
from rcsbapi.sequence import GroupAnnotationsSummary

query = GroupAnnotationsSummary(
    group="MATCHING_UNIPROT_ACCESSION",
    group_id="P01112",
    sources=["PDB_INSTANCE"],
    return_data_list=["target_id", "features.type", "features.value"]
)
query.exec()
```

### GroupAnnotationsSummary with Filter
Use the `filters` argument in combination with `AnnotationFilterInput` to select which annotation summaries to retrieve.

```python
from rcsbapi.sequence import GroupAnnotationsSummary, AnnotationFilterInput

# Fetch only the "LIGAND_INTERACTION" annotation summary information
query = GroupAnnotationsSummary(
    group="MATCHING_UNIPROT_ACCESSION",
    group_id="P01112",
    sources=["PDB_INSTANCE"],
    filters=[
        AnnotationFilterInput(
            field="TYPE",
            operation="EQUALS",
            values=["LIGAND_INTERACTION"],
            source="PDB_INSTANCE"
        )
    ],
    return_data_list=["target_id", "features.type", "features.value"]
)
query.exec()
```

## Pagination
Some GraphQL fields support pagination using standard parameters: `first` and `offset`.
These parameters are commonly used to limit or paginate results from a list-type field. Currently, pagination is only available for `Alignments` queries.

For example, to get the first 10 results, use:

```python
from rcsbapi.sequence.seq_query import Alignments

align_query = Alignments(
    db_from="UNIPROT",
    db_to="PDB_ENTITY",
    query_id="P18158",
    return_data_list=["target_alignments"],
    data_list_args={
        "target_alignments": {
            "first": 10,
            "offset": 0
        },
    }
)
align_query.exec()
```

And to get the next 10 results, use:

```python
from rcsbapi.sequence.seq_query import Alignments

align_query = Alignments(
    db_from="UNIPROT",
    db_to="PDB_ENTITY",
    query_id="P18158",
    return_data_list=["target_alignments"],
    data_list_args={
        "target_alignments": {
            "first": 10,
            "offset": 10
        },
    }
)
align_query.exec()
```
