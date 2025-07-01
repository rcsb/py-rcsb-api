# Additional Examples

## Annotations Query with Filter
Example comes from [RCSB PDB Sequence Coordinates API documentation](https://sequence-coordinates.rcsb.org/#examples)

```python
from rcsbapi.sequence import Annotations, AnnotationFilterInput

# Fetch protein-ligand binding sites for PDB Instances that fall within Human Chromosome 1
query = Annotations(
    reference="NCBI_GENOME",
    sources=["PDB_INSTANCE"],
    query_id="NC_000001",
    filters=[
        AnnotationFilterInput(
            field="TYPE",
            operation="EQUALS",
            values=["BINDING_SITE"],
            source="UNIPROT"
        )
    ],
    return_data_list=["features.description"]
)
query.exec()
```

## Alignments with Range
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

## GroupAlignments
<!-- TODO: See if you can add more detail to description text -->
Get alignments for structures in groups

```python
from rcsbapi.sequence import GroupAlignments

# TODO: add description
query = GroupAlignments(
    group="MATCHING_UNIPROT_ACCESSION",
    group_id="P01112",
    return_data_list=["target_alignments.aligned_regions", "target_id"],
)
query.exec()
```

## GroupAlignments with Filter
`filter` specify which IDs to return results for

```python
from rcsbapi.sequence import GroupAlignments

# TODO: add description
query = GroupAlignments(
    group="MATCHING_UNIPROT_ACCESSION",
    group_id="P01112",
    return_data_list=["target_alignments.aligned_regions", "target_id"],
    filter=["8CNJ_1", "8FG4_1"]
)
query.exec()
```

## GroupAnnotations
<!-- TODO: See if you can add more detail to description text -->
Get annotations for structures in groups

```python
from rcsbapi.sequence import GroupAnnotations

# TODO Add description
query = GroupAnnotations(
    group="MATCHING_UNIPROT_ACCESSION",
    group_id="P01112",
    sources=["PDB_ENTITY"],
    return_data_list=["features.name","features.feature_positions", "target_id"]
)
query.exec()
```

## GroupAnnotations with Filter
`filters` specify what annotations will be retrieved.

```python
from rcsbapi.sequence import GroupAnnotations, AnnotationFilterInput

# TODO: Add description
query = GroupAnnotations(
    group="MATCHING_UNIPROT_ACCESSION",
    group_id="P01112",
    sources=["PDB_ENTITY"],
    filters=[
        AnnotationFilterInput(
            field="TYPE",
            operation="EQUALS",
            values=["BINDING_SITE"],
            source="UNIPROT"
        )
    ],
    return_data_list=["features.name", "features.feature_positions", "target_id"],
)
query.exec()
```

## GroupAnnotationsSummary
<!-- TODO: This currently fails for reasons unrelated to python package, Joan is looking into it -->
<!-- TODO: Add description -->

```python
from rcsbapi.sequence import GroupAnnotationsSummary

# TODO: add description
query = GroupAnnotationsSummary(
    group="MATCHING_UNIPROT_ACCESSION",
    group_id="P01112",
    sources=["PDB_INSTANCE"],
    return_data_list=["target_id", "features.type"]
)
query.exec()
```

## GroupAnnotations with Filter
<!-- TODO: This currently fails for reasons unrelated to python package, Joan is looking into it -->
`filters` specify what annotations will be retrieved.

```python
from rcsbapi.sequence import GroupAnnotationsSummary, AnnotationFilterInput

# TODO: add description
query = GroupAnnotationsSummary(
    group="MATCHING_UNIPROT_ACCESSION",
    group_id="P01112",
    sources=["PDB_INSTANCE"],
    filters=[
        AnnotationFilterInput(
            field="TYPE",
            operation="EQUALS",
            values=["BINDING_SITE"],
            source="UNIPROT"
        )
    ],
    return_data_list=["target_id", "features.type"]
)
query.exec()
```