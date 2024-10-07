# Query Construction

## Query Objects
Constructing a query object requires three inputs. The JSON response to a query is stored in the `response` attribute of a Query object and can be accessed using the `get_response()` method.
```python
from rcsbapi.data import Query

# constructing the Query object
query = Query(
    input_type="entries",
    input_ids=["4HHB"],
    return_data_list=["exptl.method"]
)

# executing the query
query.exec()

# accessing the response
# can also print using print(query.exec())
print(query.get_response())
```

### input_type
Specifies which field you are starting your query from.

input_types, also called "root fields", are designated points where you can begin querying. This includes entries, polymer_entities, polymer_entity_instances, etc. Singular input_types are converted to their plural form to allow for more flexibility in input_ids. If no plural form is available, then the input_type will not be converted. For the full list see below:

<details open>
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
- uniprot
- pubmed
- chem_comp
- chem_comps
- entry_group
- entry_groups
- polymer_entity_group
- polymer_entity_groups
- group_provenance

</details>

### input_ids
Specifies which entries, entities, etc you would like to request data for.

This can be a dictionary or a list. Dictionaries must be passed with specific keys corresponding to the input_type. You can find the key names by using the `get_input_id_dict(input_type)` method (see [Helpful Methods](query_construction.md#get-input-id-dict)) or by looking in the [GraphiQL editor](https://data.rcsb.org/graphql/index.html) Docs menu. Lists must be passed in PDB identifier format.

<div style="width:750px">

|Type|PDB ID Format|Example|
|---|---|---|
|entries|entry id|4HHB|
|polymer, branched, or non-polymer entities|[entry_id]_[entity_id]|4HHB_1|
|polymer, branched, or non-polymer entity instances|[entry_id].[asym_id]|4HHB.A|
|biological assemblies|[entry_id]-[assembly_id]|4HHB-1|
|interface|[entry_id]-[assembly_id].[interface_id]|4HHB-1.1|

</div>

Dictionaries and Lists will be treated equivalently for the input_ids argument. For example, these input_ids arguments are equivalent.

```python
# input_type is polymer_entity_instance
input_ids=["4HHB.A"]
input_ids={"entry_id": "4HHB", "asym_id": "A"}
```
```python
# input_type is polymer_entity_instances (plural)
input_ids=["4HHB.A", "4HHB.B"]
input_ids={"instance_ids": ["4HHB.A", "4HHB.B"]}
```

### return_data_list
These are the data that you are requesting (or "fields").

In GraphQL syntax, the final requested data must be a "scalar" type (string, integer, boolean). However, if you request non-scalar data, the package will auto-populate the query to include all fields under the specified data until scalars are reached. Once you receive the query response and understand what specific data you would like to request, you can refine your query by requesting more specific fields.

```python
from rcsbapi.data import Query
query = Query(
    input_type="entries",
    input_ids=["4HHB"],
    return_data_list=["exptl"]
)
result_dict = query.exec()
print(result_dict)
```
```json
{
  "data": {
    "entries": [
      {
        "rcsb_id": "4HHB",
        "exptl": [
          {
            "method_details": null,
            "method": "X-RAY DIFFRACTION",
            "crystals_number": null,
            "details": null
          }
        ]
      }
    ]
  }
}
```
This query can be made more concise by specifying a field, like "method". In this case, the field name "method" is redundant because it appears under other types and must be further specified using dot notation. For more details see [ValueError: Not a unique field](query_construction.md#valueerror-not-a-unique-field)
```python
from rcsbapi.data import Query
query = Query(
    input_type="entries",
    input_ids=["4HHB"],
    return_data_list=["exptl.method"]
)
result_dict = query.exec()
print(result_dict)
```
```json
{
  "data": {
    "entries": [
      {
        "rcsb_id": "4HHB",
        "exptl": [
          {
            "method": "X-RAY DIFFRACTION"
          }
        ]
      }
    ]
  }
}
```

## Helpful Methods
There are several methods included to make working with query objects easier. These methods can help you refine your queries to request exactly and only what you want and further understand the GraphQL syntax.

### get_editor_link()
This method returns the link to a [GraphiQL](https://data.rcsb.org/graphql/index.html) window with the query. From the window, you can use the user interface to explore other fields and refine your query. Method of Query class.

```python
from rcsbapi.data import Query
query = Query(
    input_type="entries",
    input_ids=["4HHB"],
    return_data_list=["exptl"]
)
editor_link = query.get_editor_link()
print(editor_link)
```

### find_paths()
Given a redundant field, this method finds all paths from an input_type to nodes named as return_data_name. Method of Schema class.

```python
from rcsbapi.data import Schema
schema = Schema()
schema.find_paths(input_type="entries", return_data_name="id")
```

To return a dictionary with descriptions for each path, set `descriptions` to true.
```python
schema.find_paths(input_type="entries", return_data_name="id". descriptions=True)
```

### find_field_names()
Given a string, this method will return all fields containing that string.

```python
from rcsbapi.data import Schema
schema = Schema()
schema.find_field_names("exptl")
```

### get_input_id_dict()
Given an input_type, returns a dictionary with the corresponding keys and descriptions of each key. Method of Schema class.

```python
from rcsbapi.data import Schema
schema = Schema()
schema.get_input_id_dict("polymer_entity_instance")
```

## Troubleshooting
### ValueError: Not a unique field
Some fields are redundant within our GraphQL Data API schema. For example, "id" appears over 50 times. To allow for specific querying, redundant fields are identified by the syntax `<field name>.<field name>...`. If you request a redundant field without this syntax, a `ValueError` will be returned stating that the field exists, but is not unique. You can then use `find_paths(input_type, return_data_name)` to find a path that would specify the field.

```python
from rcsbapi.data import Query

# querying a redundant field
query = Query(
    input_type="entries",
    input_ids=["4HHB"],
    return_data_list=["id"]
)
result_dict = query.exec()
print(result_dict)
```
```
ValueError: "id" exists, but is not a unique field, must specify further.
10 of 118 possible paths:
  entries.assemblies.branched_entity_instances.branched_entity.chem_comp_monomers.chem_comp.id
  entries.assemblies.branched_entity_instances.branched_entity.chem_comp_monomers.rcsb_bird_citation.id
  ...

For all paths run:
  from rcsbapi.data import Schema
  schema = Schema()
  schema.find_paths("entries", "id")
```
```python
from rcsbapi.data import Schema

# run find_paths(input_type, return_data_name)
schema = Schema()
print(schema.find_paths(input_type="entries", return_data_name="id"))
```

```python
# select desired field from the returned list
['citation.id',
'diffrn.id'
'entry.id'
...
'polymer_entities.prd.chem_comp.id',
'polymer_entities.prd.rcsb_bird_citation.id',
'polymer_entities.prd.rcsb_chem_comp_annotation.annotation_lineage.id']
```
```python
from rcsbapi.data import Query

# valid query
query = Query(
    input_type="entries",
    input_ids=["4HHB"],
    return_data_list=["entry.id"]
)
result_dict = query.exec()
print(result_dict)
```