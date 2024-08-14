# Quickstart

## Installation
Get it from PyPI:

    pip install rcsb-api

Or, download from [GitHub](https://github.com/rcsb/py-rcsb-api)

To import this package, use:
```python
from rcsbapi.data import Schema, Query
```

## Jupyter Notebooks
A notebook briefly summarizing the README is available in [notebooks/quickstart.ipynb](notebooks/quickstart.ipynb).

Another notebook using both Search and Data API packages in a COVID-19 related example is available in [notebooks/search_data_workflow.ipynb](notebooks/search_data_workflow.ipynb).

## Background
The [RCSB PDB Data API](https://data.rcsb.org) supports requests using [GraphQL](https://graphql.org/), a language for API queries. This package simplifies generating queries in GraphQL syntax. 

GraphQL is built on "types" and their associated "fields". All types and their fields are defined in a "schema". An example of a type in our schema is "CoreEntry" and a field under CoreEntry is "exptl" (experimental). Upon initialization, the Data API package fetches the schema from the RCSB PDB website (See [Implementation Details](#implementation-details) for more). 

In GraphQL, you must begin your query at specific fields. These are fields like entry, polymer_entity, and polymer_entity_instance (see full list [here](#input_types)). Each field can return a scalar (e.g. string, integer) or a type. Every query must ultimately request scalar value(s), which can be seen in the example query below. As shown in the example, only fields are explicitly included in queries while types are implicit. Types are named in CamelCase (CoreEntry) while fields are in snake case (exptl or audit_author).

## Example 
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

To generate the same query in this package, you would create a Query object. The Query object must be executed using the `.exec()` method, which will return the JSON response as well as store the response as an attribute of the Query object. From the object, you can access the Data API response, get an interactive editor link, or access the arguments used to create the query.
```python
from rcsbapi.data import Query
query = Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["exptl.method"])
query.exec()
```

## Auto-completion of Queries
One way this package simplifies making requests is by adding fields that return scalars into the generated query if you request a field that returns a type.
```python
from rcsbapi.data import Query
query = Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["exptl"])
query.exec()
```
This creates a valid query even though "exptl" doesn't return a scalar. However, the resulting query will be more verbose, requesting all scalar fields under "exptl" (see [return_data_list](#return_data_list)).

