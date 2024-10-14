# Additional Examples
Most examples come from [RCSB PDB Data API documentation](https://data.rcsb.org/#examples)

### Entries
Fetch information about structure title and experimental method for PDB entries:
```python
from rcsbapi.data import DataQuery as Query
query = Query(
    input_type="entries",
    input_ids=["1STP", "2JEF", "1CDG"],
    return_data_list=["entries.rcsb_id", "struct.title", "exptl.method"]
)
result_dict = query.exec()
print(result_dict)
```
Performs the following GraphQL query:
```
{
  entries(entry_ids: ["1STP", "2JEF", "1CDG"]) {
    rcsb_id
    struct {
      title
    }
    exptl {
      method
    }
  }
}
```
To find more about the return_data_list dot notation, see [ValueError: Not a unique field](query_construction.md#valueerror-not-a-unique-field)

### Primary Citation
Fetch primary citation information (structure authors, PubMed ID, DOI) and release date for PDB entries:

```python
from rcsbapi.data import DataQuery as Query
query = Query(
    input_type="entries",
    input_ids=["1STP", "2JEF", "1CDG"],
    return_data_list=[
        "entries.rcsb_id",
        "rcsb_accession_info.initial_release_date",
        "audit_author.name",
        "rcsb_primary_citation.pdbx_database_id_PubMed",
        "rcsb_primary_citation.pdbx_database_id_DOI"
    ]
)
result_dict = query.exec()
print(result_dict)
```
Performs the following GraphQL query:
```
{
  entries(entry_ids: ["1STP", "2JEF", "1CDG"]) {
    rcsb_id
    rcsb_accession_info {
      initial_release_date
    }
    audit_author {
      name
    }
    rcsb_primary_citation {
      pdbx_database_id_PubMed
      pdbx_database_id_DOI
    }
  }
}
```

### Polymer Entities
Fetch taxonomy information and information about membership in the sequence clusters for polymer entities:

```python
from rcsbapi.data import DataQuery as Query
query = Query(
    input_type="polymer_entities",
    input_ids=["2CPK_1", "3WHM_1", "2D5Z_1"],
    return_data_list=[
        "polymer_entities.rcsb_id",
        "rcsb_entity_source_organism.ncbi_taxonomy_id",
        "rcsb_entity_source_organism.ncbi_scientific_name",
        "cluster_id",
        "identity"
    ]
)
result_dict = query.exec()
print(result_dict)
```
Performs the following GraphQL query:
```
{
  polymer_entities(entity_ids: ["2CPK_1", "3WHM_1", "2D5Z_1"]) {
    rcsb_id
    rcsb_entity_source_organism {
      ncbi_taxonomy_id
      ncbi_scientific_name
    }
    rcsb_cluster_membership {
      cluster_id
      identity
    }
  }
}
```

### Polymer Instances
Fetch information about the domain assignments for polymer entity instances:

```python
from rcsbapi.data import DataQuery as Query
query = Query(
    input_type="polymer_entity_instances",
    input_ids=["4HHB.A", "12CA.A", "3PQR.A"],
    return_data_list=[
        "polymer_entity_instances.rcsb_id",
        "rcsb_polymer_instance_annotation.annotation_id",
        "rcsb_polymer_instance_annotation.name",
        "rcsb_polymer_instance_annotation.type"
    ]
)
result_dict = query.exec()
print(result_dict)
```
Performs the following GraphQL query:
```
{
  polymer_entity_instances(instance_ids: ["4HHB.A", "12CA.A", "3PQR.A"]) {
    rcsb_id
    rcsb_polymer_instance_annotation {
      annotation_id
      name
      type
    }
  }
}
```

### Carbohydrates
Query branched entities (sugars or oligosaccharides) for commonly used linear descriptors:

```python
from rcsbapi.data import DataQuery as Query
query = Query(
    input_type="branched_entities",
    input_ids=["5FMB_2", "6L63_3"],
    return_data_list=[
        "pdbx_entity_branch.type",
        "pdbx_entity_branch_descriptor.type",
        "pdbx_entity_branch_descriptor.descriptor"
    ]
)
result_dict = query.exec()
print(result_dict)
```
Performs the following GraphQL query:
```
{
  branched_entities(entity_ids: ["5FMB_2", "6L63_3"]) {
    pdbx_entity_branch {
      type
    }
    pdbx_entity_branch_descriptor {
      type
      descriptor
    }
  }
}
```

### Sequence Positional Features

Sequence positional features describe regions or sites of interest in the PDB sequences, such as binding sites, active sites, linear motifs, local secondary structure, structural and functional domains, etc. Positional annotations include depositor-provided information available in the PDB archive as well as annotations integrated from external resources (e.g. UniProtKB).

This example queries 'polymer_entity_instances' positional features. The query returns features of different type: for example, CATH and SCOP classifications assignments integrated from UniProtKB data, or the secondary structure annotations from the PDB archive data calculated by the data-processing program called MAXIT (Macromolecular Exchange and Input Tool) that is based on an earlier ProMotif implementation.

```python
from rcsbapi.data import DataQuery as Query
query = Query(
    input_type="polymer_entity_instances",
    input_ids=["1NDO.A"],
    return_data_list=[
        "polymer_entity_instances.rcsb_id",
        "rcsb_polymer_instance_feature.type",
        "rcsb_polymer_instance_feature.feature_positions.beg_seq_id",
        "rcsb_polymer_instance_feature.feature_positions.end_seq_id"
    ]
)
result_dict = query.exec()
print(result_dict)
```
Performs the following GraphQL query:
```
{
  polymer_entity_instances(instance_ids: ["1NDO.A"]) {
    rcsb_id
    rcsb_polymer_instance_feature {
      type
      feature_positions {
        beg_seq_id
        end_seq_id
      }
    }
  }
}
```

### Reference Sequence Identifiers
This example shows how to access identifiers related to entries (cross-references) and found in data collections other than PDB. Each cross-reference is described by the database name and the database accession. A single entry can have cross-references to several databases, e.g. UniProt and GenBank in 7NHM, or no cross-references, e.g. 5L2G:
```python
from rcsbapi.data import DataQuery as Query
query = Query(
    input_type="entries",
    input_ids=["7NHM", "5L2G"],
    return_data_list=[
        "polymer_entities.rcsb_id",
        "polymer_entities.rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession",
        "polymer_entities.rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_name"
    ]
)
result_dict = query.exec()
print(result_dict)
```
Performs the following GraphQL query:
```
{
  entries(entry_ids: ["7NHM", "5L2G"]){
    polymer_entities {
      rcsb_id
      rcsb_polymer_entity_container_identifiers {
        reference_sequence_identifiers {
          database_accession
          database_name
        }
      }
    }
  }
}
```

### Chemical Components
Query for specific items in the chemical component dictionary based on a given list of CCD ids:

```python
from rcsbapi.data import DataQuery as Query
query = Query(
    input_type="chem_comps",
    input_ids=["NAG", "EBW"],
    return_data_list=[
        "chem_comps.rcsb_id",
        "chem_comp.type",
        "chem_comp.formula_weight",
        "chem_comp.name",
        "chem_comp.formula",
        "rcsb_chem_comp_info.initial_release_date"
    ]
)
result_dict = query.exec()
print(result_dict)
```
Performs the following GraphQL query:
```
{
  chem_comps(comp_ids: ["NAG", "EBW"]) {
    rcsb_id
    chem_comp {
      type
      formula_weight
      name
      formula
    }
    rcsb_chem_comp_info {
      initial_release_date
    }
  }
}
```

### Computed Structure Models
This example shows how to get a list of global Model Quality Assessment metrics for AlphaFold structure of Hemoglobin subunit beta:

```python
from rcsbapi.data import DataQuery as Query
query = Query(
    input_type="entries",
    input_ids=["AF_AFP68871F1"],
    return_data_list=["ma_qa_metric_global.type", "ma_qa_metric_global.value"]
)
result_dict = query.exec()
print(result_dict)
```
Performs the following GraphQL query:
```
{
  entries(entry_ids: ["AF_AFP68871F1"]) {
    rcsb_ma_qa_metric_global {
      ma_qa_metric_global {
        type
        value
      }
    }
  }
}
```

### PubMed
This example gets the abstract text of the paper with the specified PubMed ID.

```python
query = Query(
  input_type="pubmed",
  return_data_list=["rcsb_pubmed_abstract_text"],
  input_ids=["6726807"]
)

result_dict = query.exec()
print(result_dict)
```

Performs the following GraphQL query:
```
{
  pubmed(pubmed_id: 6726807) {
    rcsb_pubmed_abstract_text
  }
}
```

### UniProt
This example gets a description of the function of a protein based on the UniProt ID.

```python
query = Query(
  input_type="uniprot",
  return_data_list=["function.details"],
  input_ids=["P68871"]
)

result_dict = query.exec()
print(result_dict)
```

Performs the following GraphQL query:
```
{
  uniprot(uniprot_id: "P68871") {
    rcsb_uniprot_protein {
      function {
        details
      }
    }
  }
}
```
