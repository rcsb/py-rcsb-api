# py-rcsb-api
Python interface for RCSB PDB API services at RCSB.org.

## Examples
<!-- Jupyter Notebook 1--> 
<!-- Jupyter Notebook 2--> 

This is a query in GraphQL syntax requesting the experimental method of a structure.
```
{
  entry(entry_id: "4HHB") {
    exptl {
      method
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

## Query Objects
To generate and POST the same query in this package, you would create a Query object. From the object, you can access the response, get an interactive editor link, or access the arguments used to create the query.
```python
Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["Exptl.method"])
```

### input_ids

Specifies which entry, entity, etc you would like to request data for.

This can be a dictionary or in some cases, a list. Dictionaries must be passed with specific keys corresponding to the arguments required in the GraphQL schema and viewable in the [GraphiQL editor](https://data.rcsb.org/graphql/index.html). <!--#TODO: You can also check what keys are required for a given type by running `get_input_keys(type name)`.--> Dictionaries will be accepted for all types and lists will also be accepted for "plural" types (entries, assemblies, etc). Lists must be passed in PDB identifier format. 

For example, these two input_ids arguments for input type polymer_entity_instances (Note plural) are equivalent.

```python
input_ids={"entry_ids":["4HHB.A","4HHB.B"]}
input_ids=["4HHB.A","4HHB.B"]
```

For polymer_entity_instance (singular), only a dictionary will be accepted. `input_ids=["4HHB.A"]` will not be accepted.

```python
input_ids={"entry_id":"4HHB", "asym_id":"A"}
```

### input_types
Specifies which type of the data where you are starting your query. input_type are designated points where you can begin querying. This includes entry, polymer_entity, polymer_entity_instance, etc. For the full list see below:  

<details>
  <summary>Full list of input_types</summary>

- entry
- entries
- assemblies
- polymer_entity
- branched_entity
- nonpolymer_entity
- polymer_entity_instance
- nonpolymer_entity_instance
- branched_entity_instance
- polymer_entities
- nonpolymer_entities
- branched_entities
- polymer_entity_instances
- nonpolymer_entity_instances
- branched_entity_instances
- assembly
- interface
- interfaces
- chem_comps
- uniprot
- pubmed
- chem_comp
- entry_groups
- entry_group
- polymer_entity_group
- polymer_entity_groups
- group_provenance

</details>

### return_data_list
These are the data that you are requesting (or "fields"). In GraphQL, the final requested data must be a "scalar" type (string, integer, boolean). However, if you request non-scalar data, the package will auto-populate the query to include all fields under the data until scalars are reached. Once you receive the query response and understand what specific data you would like to request, you can further refine your query by requesting more specific fields.

#### ValueError: Not a unique field
Some fields are redundant within our GraphQL data API. For example, "id" appears over 50 times. To allow for specific querying, redundant fields are identified by the syntax `<parent type>.<field name>`. If you request a redundant field without this syntax, a `ValueError` will be returned stating that the field exists, but is redundant. You can then use `get_unique_fields("<field name>")` to find notation that would specify a unique field for the given name.

<details>
  <summary>Example</summary>

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
> ...
> 'RcsbUniprotKeyword.id',
> 'RcsbPolymerInstanceAnnotationAnnotationLineage.id',
> 'RcsbPolymerStructConn.id']
```
</details>


## Error Handling
In GraphQL, all requests return HTTP status code 200 and instead errors appear in the JSON that is returned. The package will parse these errors, throwing a ValueError and displaying the corresponding error message or messages. To access the full query and return JSON in an interactive editor, you can use the `get_editor_link` method. 