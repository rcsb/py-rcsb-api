# py-rcsb-api
Python interface for RCSB PDB API services at RCSB.org.

## Installation

Get it from PyPI:

    pip install rcsbdataapi

Or, download from [GitHub](https://github.com/rcsb/py-rcsbsearchapi)

## Jupyter Notebooks
A quick-start Jupyter notebook briefly summarizing the README is available in [notebooks/quickstart.ipynb](), or can be run online using binder:
[![Binder](https://mybinder.org/badge_logo.svg)]()
<!-- Jupyter Notebook 2--> 

## Background
The [RCSB PDB Data API](https://data.rcsb.org/#data-organization) supports requests using [GraphQL](https://graphql.org/), a language for API queries. This package simplifies generating queries in GraphQL syntax. 

GraphQL is built on "types" and their associated "fields". All types and their fields are defined in a "schema". An example of a type in our schema is "CoreEntry" and a field under CoreEntry is "exptl" (experimental). Upon initialization, the data API package fetches the schema from the RCSB PDB website (See [Implementation Details](#implementation-details) for more). 

In GraphQL, you must begin your query at specific fields. These are fields like entry, polymer_entity, and polymer_entity_instance (see full list [here](#input_types)). Each field can return a scalar (e.g. string, integer) or a type. Every query must ultimately request scalar value(s), which can be seen in the example query below. As shown in the example, only fields are explicitly included in queries while types are implicit. Types are named in CamelCase (CoreEntry) while fields are in snake case (exptl or audit_author).

This is a query in GraphQL syntax requesting the experimental method of a structure with PDB ID 4HHB (Hemoglobin).
```
{
  entry(entry_id: "4HHB") {  # returns type "CoreEntry"
    exptl {  # returns type "Exptl"
      method  # returns a scalar (string)
    }
  }
}

```
Data is returned in JSON format
```json
{
  "data": {
    "entry": {
      "exptl": [
        {
          "method": "X-RAY DIFFRACTION"
        }
      ]
    }
  }
}
```

To generate and POST the same query in this package, you would create a Query object. From the object, you can access the response, get an interactive editor link, or access the arguments used to create the query.
```python
Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["Exptl.method"])
```

One way this package simplifies making requests is by auto-populating corresponding fields that return scalars even if you request a field that returns a type.
```python
Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["exptl"])
```
This creates a valid query even though "exptl" doesn't return a scalar. However, the resulting query will be more verbose (see [return_data_list](#return_data_list))

## Query Objects
Constructing a query object requires three inputs.
```python
Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["Exptl.method"])
```

### input_ids

Specifies which entry, entity, etc you would like to request data for.

This can be a dictionary or a list. Dictionaries must be passed with specific keys corresponding to the arguments required in the GraphQL schema and viewable in the [GraphiQL editor](https://data.rcsb.org/graphql/index.html) Docs menu. <!--#TODO: You can also check what keys are required for a given type by running `get_input_keys(type name)`.--> Lists must be passed in PDB identifier format. 

|Type|Format|Example|
|---|---|---|
|polymer, branched, or non-polymer entities|[entry_id]_[entity_id]|4HHB_1|
|polymer, branched, or non-polymer entity instances|[entry_id].[asym_id]|4HHB.A|
|biological assemblies|[entry_id]-[assembly_id]|4HHB-1|


Dictionaries and Lists will be treated equivalently for the input_ids argument. For example, these input_ids arguments are equivalent.

```python
input_ids=["4HHB.A"]
input_ids={"entry_id":"4HHB", "asym_id": "A"}
```
```python
input_ids=["4HHB.A","4HHB.B"]
input_ids={"entry_ids":["4HHB.A","4HHB.B"]}
```

### input_types
Specifies which field you are starting your query from. 

input_types, also called "root fields", are designated points where you can begin querying. This includes entry, polymer_entity, polymer_entity_instance, etc. For the full list see below:  

<details>
  <summary>Full list of input_types</summary>

- entry
- entries
- polymer_entity
- polymer_entities
- branched_entity
- branched_entities
- nonpolymer_entity
- nonpolymer_entities
- polymer_entity_instance
- polymer_entity_instances
- nonpolymer_entity_instance
- nonpolymer_entity_instances
- branched_entity_instance
- branched_entity_instances
- assembly
- assemblies
- interface
- interfaces
- chem_comps
- uniprot
- pubmed
- chem_comp
- entry_group
- entry_groups
- polymer_entity_group
- polymer_entity_groups
- group_provenance

</details>

### return_data_list
These are the data that you are requesting (or "fields").

In GraphQL syntax, the final requested data must be a "scalar" type (string, integer, boolean). However, if you request non-scalar data, the package will auto-populate the query to include all fields under the specified data until scalars are reached. Once you receive the query response and understand what specific data you would like to request, you can refine your query by requesting more specific fields.

```python
Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["exptl"])
```
```json
{
  "data": {
    "entry": {
      "exptl": [
        {
          "details": null,
          "crystals_number": null,
          "method_details": null,
          "method": "X-RAY DIFFRACTION"
        }
      ]
    }
  }
}
```
This query can be made more concise by specifying a field. In this case, the field name "method" is redundant because it appears under other types and must be further specified using dot notation. For more details see [ValueError: Not a unique field](#valueerror-not-a-unique-field)
```python
Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["Exptl.method"])
```
```json
{
  "data": {
    "entry": {
      "exptl": [
        {
          "method": "X-RAY DIFFRACTION"
        }
      ]
    }
  }
}
```

## Helpful methods
There are several methods included to make working with query objects easier. These methods can also help you further understand the GraphQL syntax and refine your queries to request exactly and only what you want.

### get_editor_link()
This method returns the link to a [GraphiQL](https://data.rcsb.org/graphql/index.html) window with the query. From the window, you can use the user interface to explore other fields and refine your query.

```python
query = Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["exptl"])
print(query.get_editor_link())
```

### get_unique_fields() <!--Should this be moved outside the schema method?-->
Given a redundant field, this method returns a list of matching fields in dot notation. You can look through the list to identify your intended field.

```python
print(SCHEMA.get_unique_fields("id"))
```

<!--TODO: add partial string match-->
<!--TODO: add finding input_type keys-->

## Trouble-shooting
### ValueError: Not a unique field
Some fields are redundant within our GraphQL data API schema. For example, "id" appears over 50 times. To allow for specific querying, redundant fields are identified by the syntax `<type>.<field name>`. If you request a redundant field without this syntax, a `ValueError` will be returned stating that the field exists, but is redundant. You can then use `get_unique_fields("<field name>")` to find notation that would specify a unique field for the given name.

```python
# querying a redundant field
Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["id"])
```
```
> ValueError: Not a unique field, must specify further. To find valid fields with this name, run: get_unique_fields(id)
```

```python
# Run get_unique_field("<field name>")
print(get_unique_fields("id"))
```

```
> ['PdbxStructSpecialSymmetry.id',
> 'ChemComp.id',
> 'RcsbBirdCitation.id',
> 'Entry.id',
> ...
> 'RcsbUniprotKeyword.id',
> 'RcsbPolymerInstanceAnnotationAnnotationLineage.id',
> 'RcsbPolymerStructConn.id']
```
```python
# valid Query
Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["Entry.id"])
```

## Implementation Details
### Parsing Schema
<<<<<<< HEAD
Upon initialization of the package, the GraphQL schema is fetched from the RCSB PDB website. After fetching the file, the python package parses the schema and creates a graph object to represent it. This graph representation of how fields and types connect is key to how queries are automatically constructed using a shortest path algoritm. By default the graph is constructed as a directed graph in [rustworkx](https://www.rustworkx.org/)
=======
>>>>>>> 94bc30f (Documentation and jupyter notebooks added. Minor changes to schema and query)

### Constructing queries

### Error Handling
In GraphQL, all requests return HTTP status code 200 and instead errors appear in the JSON that is returned. The package will parse these errors, throwing a ValueError and displaying the corresponding error message or messages. To access the full query and return JSON in an interactive editor, you can use the `get_editor_link()` method on the Query object. 

```python
query_obj = Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["exptl"])
query_obj.get_editor_link()
```
## Additional examples
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
query = Query(input_ids={"entry_ids": ["1STP","2JEF","1CDG"]},input_type="entries", return_data_list=["CoreEntry.rcsb_id", "Struct.title", "Exptl.method"])
```
To find more about the return_data_list dot notation, see [ValueError: Not a unique field](#valueerror-not-a-unique-field)

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
query = Query(input_ids={"entry_ids": ["1STP","2JEF","1CDG"]},input_type="entries", return_data_list=["CoreEntry.rcsb_id", "RcsbAccessionInfo.initial_release_date", "AuditAuthor.name", "RcsbPrimaryCitation.pdbx_database_id_PubMed", "RcsbPrimaryCitation.pdbx_database_id_DOI"])
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
query = Query(input_ids={"entity_ids":["2CPK_1","3WHM_1","2D5Z_1"]},input_type="polymer_entities", return_data_list=["CorePolymerEntity.rcsb_id", "RcsbEntitySourceOrganism.ncbi_taxonomy_id", "RcsbEntitySourceOrganism.ncbi_scientific_name", "cluster_id", "identity"])
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
query = Query(input_ids={"instance_ids":["4HHB.A", "12CA.A", "3PQR.A"]},input_type="polymer_entity_instances", return_data_list=["CorePolymerEntityInstance.rcsb_id", "RcsbPolymerInstanceAnnotation.annotation_id", "RcsbPolymerInstanceAnnotation.name", "RcsbPolymerInstanceAnnotation.type"])
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
query = Query(input_ids={"entity_ids":["5FMB_2", "6L63_3"]},input_type="branched_entities", return_data_list=["PdbxEntityBranch.type","PdbxEntityBranchDescriptor.type","PdbxEntityBranchDescriptor.descriptor"])
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
query = Query(input_ids={"instance_ids":["1NDO.A"]},input_type="polymer_entity_instances", return_data_list=["CorePolymerEntityInstance.rcsb_id", "RcsbPolymerInstanceFeature.type", "RcsbPolymerInstanceFeatureFeaturePositions.beg_seq_id", "RcsbPolymerInstanceFeatureFeaturePositions.end_seq_id"])
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
query = Query(input_ids={"entry_ids": ["7NHM", "5L2G"]}, input_type="entries", return_data_list=["CoreEntry.rcsb_id", "RcsbPolymerEntityContainerIdentifiersReferenceSequenceIdentifiers.database_accession", "RcsbPolymerEntityContainerIdentifiersReferenceSequenceIdentifiers.database_name"])
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
query = Query(input_ids={"comp_ids":["NAG", "EBW"]}, input_type="chem_comps", return_data_list=["CoreChemComp.rcsb_id","ChemComp.type","ChemComp.formula_weight","ChemComp.name","ChemComp.formula","RcsbChemCompInfo.initial_release_date"])
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
query = Query(input_ids={"entry_ids": ["AF_AFP68871F1"]}, input_type="entries", return_data_list=["RcsbMaQaMetricGlobalMaQaMetricGlobal.type", "RcsbMaQaMetricGlobalMaQaMetricGlobal.value"])
```


