# py-rcsb-api
Python interface for RCSB PDB API services at RCSB.org.

## Installation

Get it from PyPI:

    pip install rcsbdataapi

Or, download from [GitHub]() <!--TODO: add link-->

## Examples
<!-- Jupyter Notebook 1--> 
<!-- Jupyter Notebook 2--> 

## Background
The RCSB PDB Data API supports requests using [GraphQL](https://graphql.org/), a language for API queries. This package simplifies generating queries in GraphQL syntax. 

GraphQL is built on "types" and their associated "fields". All types and their fields are defined in a "schema". An example of a type in our schema is "CoreEntry" and a field under CoreEntry is "exptl" (experimental). Upon initialization, the data API package fetches the schema from the RCSB PDB website (See [Implementation Details](#implementation-details)). 

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
This creates a valid query even though "exptl" doesn't return a scalar, although the resulting query will be more verbose (see [return_data_list](#return_data_list))

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

input_types are designated points where you can begin querying. This includes entry, polymer_entity, polymer_entity_instance, etc. For the full list see below:  

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

In GraphQL, the final requested data must be a "scalar" type (string, integer, boolean). However, if you request non-scalar data, the package will auto-populate the query to include all fields under the specified data until scalars are reached. Once you receive the query response and understand what specific data you would like to request, you can refine your query by requesting more specific fields.

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

## Implementation Details
### Parsing Schema

### Constructing queries


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

## Error Handling
In GraphQL, all requests return HTTP status code 200 and instead errors appear in the JSON that is returned. The package will parse these errors, throwing a ValueError and displaying the corresponding error message or messages. To access the full query and return JSON in an interactive editor, you can use the `get_editor_link` method on the Query object. 