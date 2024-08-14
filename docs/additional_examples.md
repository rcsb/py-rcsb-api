# Additional examples
Examples come from [RCSB PDB Data API documentation](https://data.rcsb.org/#examples)

### Entries
Fetch information about structure title and experimental method for PDB entries:
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
```python
from rcsbapi.data import Query
query = Query(input_ids={"entry_ids": ["1STP","2JEF","1CDG"]},input_type="entries", return_data_list=["entries.rcsb_id", "struct.title", "exptl.method"])
query.exec()
```
To find more about the return_data_list dot notation, see [ValueError: Not a unique field](query_construction.md#valueerror-not-a-unique-field)

### Primary Citation
Fetch primary citation information (structure authors, PubMed ID, DOI) and release date for PDB entries:

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
```python
from rcsbapi.data import Query
query = Query(input_ids={"entry_ids": ["1STP","2JEF","1CDG"]},input_type="entries", return_data_list=["entries.rcsb_id", "rcsb_accession_info.initial_release_date", "audit_author.name", "rcsb_primary_citation.pdbx_database_id_PubMed", "rcsb_primary_citation.pdbx_database_id_DOI"])
query.exec()
```

### Polymer Entities
Fetch taxonomy information and information about membership in the sequence clusters for polymer entities:

```
{
  polymer_entities(entity_ids:["2CPK_1","3WHM_1","2D5Z_1"]) {
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
```python
from rcsbapi.data import Query
query = Query(input_ids={"entity_ids":["2CPK_1","3WHM_1","2D5Z_1"]},input_type="polymer_entities", return_data_list=["polymer_entities.rcsb_id", "rcsb_entity_source_organism.ncbi_taxonomy_id", "rcsb_entity_source_organism.ncbi_scientific_name", "cluster_id", "identity"])
query.exec()
```

### Polymer Instances
Fetch information about the domain assignments for polymer entity instances:

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
```python
from rcsbapi.data import Query
query = Query(input_ids={"instance_ids":["4HHB.A", "12CA.A", "3PQR.A"]},input_type="polymer_entity_instances", return_data_list=["polymer_entity_instances.rcsb_id", "rcsb_polymer_instance_annotation.annotation_id", "rcsb_polymer_instance_annotation.name", "rcsb_polymer_instance_annotation.type"])
query.exec()
```

### Carbohydrates
Query branched entities (sugars or oligosaccharides) for commonly used linear descriptors:

```
{
  branched_entities(entity_ids:["5FMB_2", "6L63_3"]) {
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
```python
from rcsbapi.data import Query
query = Query(input_ids={"entity_ids":["5FMB_2", "6L63_3"]},input_type="branched_entities", return_data_list=["pdbx_entity_branch.type","pdbx_entity_branch_descriptor.type","pdbx_entity_branch_descriptor.descriptor"])
query.exec()
```

### Sequence Positional Features

Sequence positional features describe regions or sites of interest in the PDB sequences, such as binding sites, active sites, linear motifs, local secondary structure, structural and functional domains, etc. Positional annotations include depositor-provided information available in the PDB archive as well as annotations integrated from external resources (e.g. UniProtKB).

This example queries 'polymer_entity_instances' positional features. The query returns features of different type: for example, CATH and SCOP classifications assignments integrated from UniProtKB data, or the secondary structure annotations from the PDB archive data calculated by the data-processing program called MAXIT (Macromolecular Exchange and Input Tool) that is based on an earlier ProMotif implementation.

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
```python
from rcsbapi.data import Query
query = Query(input_ids={"instance_ids":["1NDO.A"]},input_type="polymer_entity_instances", return_data_list=["polymer_entity_instances.rcsb_id", "rcsb_polymer_instance_feature.type", "feature_positions.beg_seq_id", "feature_positions.end_seq_id"])
query.exec()
```

### Reference Sequence Identifiers
This example shows how to access identifiers related to entries (cross-references) and found in data collections other than PDB. Each cross-reference is described by the database name and the database accession. A single entry can have cross-references to several databases, e.g. UniProt and GenBank in 7NHM, or no cross-references, e.g. 5L2G:
```
{
  entries(entry_ids:["7NHM", "5L2G"]){
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
```python
from rcsbapi.data import Query
query = Query(input_ids={"entry_ids": ["7NHM", "5L2G"]}, input_type="entries", return_data_list=["entries.rcsb_id", "reference_sequence_identifiers.database_accession", "reference_sequence_identifiers.database_name"])
query.exec()
```

### Chemical Components
Query for specific items in the chemical component dictionary based on a given list of CCD ids:

```
{
  chem_comps(comp_ids:["NAG", "EBW"]) {
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
```python
from rcsbapi.data import Query
query = Query(input_ids={"comp_ids":["NAG", "EBW"]}, input_type="chem_comps", return_data_list=["chem_comps.rcsb_id","chem_comp.type","chem_comp.formula_weight","chem_comp.name","chem_comp.formula","rcsb_chem_comp_info.initial_release_date"])
query.exec()
```

### Computed Structure Models
This example shows how to get a list of global Model Quality Assessment metrics for AlphaFold structure of Hemoglobin subunit beta:

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
```python
from rcsbapi.data import Query
query = Query(input_ids={"entry_ids": ["AF_AFP68871F1"]}, input_type="entries", return_data_list=["ma_qa_metric_global.type", "ma_qa_metric_global.value"])
query.exec()
```