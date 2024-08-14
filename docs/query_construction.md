# Query Construction

## Query Objects
Constructing a query object requires three inputs. The JSON response to a query is stored in the `response` attribute of a Query object and can be accessed using the `get_response()` method.
```python
from rcsbapi.data import Query

# constructing the Query object
query = Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["exptl.method"])

# executing the query
query.exec()

# accessing the response
print(query.get_response())
```

### input_ids
Specifies which entry, entity, etc you would like to request data for.

This can be a dictionary or a list. Dictionaries must be passed with specific keys corresponding to the input_type. You can find the key names by using the `get_input_id_dict(input_type)` method (see [Helpful Methods](query_construction.html#get-input-id-dict)) or by looking in the [GraphiQL editor](https://data.rcsb.org/graphql/index.html) Docs menu. Lists must be passed in PDB identifier format. 

|Type|PDB ID Format|Example|
|---|---|---|
|polymer, branched, or non-polymer entities|[entry_id]_[entity_id]|4HHB_1|
|polymer, branched, or non-polymer entity instances|[entry_id].[asym_id]|4HHB.A|
|biological assemblies|[entry_id]-[assembly_id]|4HHB-1|
|interface|[entry_id]-[assembly_id].[interface_id]|4HHB-1.1|

Dictionaries and Lists will be treated equivalently for the input_ids argument. For example, these input_ids arguments are equivalent.

```python
# input_type is polymer_entity_instance
input_ids=["4HHB.A"]
input_ids={"entry_id":"4HHB", "asym_id":"A"}
```
```python
# input_type is polymer_entity_instances (plural)
input_ids=["4HHB.A","4HHB.B"]
input_ids={"instance_ids":["4HHB.A","4HHB.B"]}
```

### input_type
Specifies which field you are starting your query from. 

input_types, also called "root fields", are designated points where you can begin querying. This includes entry, polymer_entity, polymer_entity_instance, etc. For the full list see below:  

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

### return_data_list
These are the data that you are requesting (or "fields").

In GraphQL syntax, the final requested data must be a "scalar" type (string, integer, boolean). However, if you request non-scalar data, the package will auto-populate the query to include all fields under the specified data until scalars are reached. Once you receive the query response and understand what specific data you would like to request, you can refine your query by requesting more specific fields.

```python
from rcsbapi.data import Query
query = Query(input_ids={"entry_id":"4HHB"}, input_type="entry", return_data_list=["exptl"])
query.exec()
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
This query can be made more concise by specifying a field, like "method". In this case, the field name "method" is redundant because it appears under other types and must be further specified using dot notation. For more details see [ValueError: Not a unique field](query_construction.html#valueerror-not-a-unique-field)
```python
from rcsbapi.data import Query
query = Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["exptl.method"])
query.exec()
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

## Helpful Methods
There are several methods included to make working with query objects easier. These methods can help you refine your queries to request exactly and only what you want and further understand the GraphQL syntax.

### get_editor_link()
This method returns the link to a [GraphiQL](https://data.rcsb.org/graphql/index.html) window with the query. From the window, you can use the user interface to explore other fields and refine your query. Method of Query class.

```python
from rcsbapi.data import Query
query = Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["exptl"])
print(query.get_editor_link())
```

### get_unique_fields() <!--Should this be moved outside the schema method?-->
Given a redundant field, this method returns a list of matching fields in dot notation. You can look through the list to identify your intended field. Method of Schema class.

```python
from rcsbapi.data import Schema
schema = Schema()
schema.get_unique_fields("id")
```

### find_field_names()
Given a string, this method will return all fields containing that string, along with a description of each field.

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

## Trouble-shooting
### ValueError: Not a unique field
Some fields are redundant within our GraphQL Data API schema. For example, "id" appears over 50 times. To allow for specific querying, redundant fields are identified by the syntax `<type>.<field name>`. If you request a redundant field without this syntax, a `ValueError` will be returned stating that the field exists, but is redundant. You can then use `get_unique_fields("<field name>")` to find notation that would specify a unique field for the given name.

```python
from rcsbapi.data import Query

# querying a redundant field
query = Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["id"])
query.exec()
```
```
> ValueError: "id" exists, but is not a unique field, must specify further. To find valid fields with this name, run: get_unique_fields("id")
```

```python
from rcsbapi.data import Schema

# Run get_unique_field("<field name>")
schema = Schema()
print(schema.get_unique_fields("id"))
```

```
['PdbxStructSpecialSymmetry.id',
'RcsbBirdCitation.id',
'ChemComp.id',
'Entry.id',
...
'RcsbUniprotKeyword.id',
'RcsbPolymerInstanceAnnotationAnnotationLineage.id',
'RcsbPolymerStructConn.id']
```
```python
from rcsbapi.data import Query

# valid Query
query = Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["entry.id"])
query.exec()
```