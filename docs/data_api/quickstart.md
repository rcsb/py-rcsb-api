# Quickstart

## Installation
Get it from PyPI:

    pip install rcsb-api

Or, download from [GitHub](https://github.com/rcsb/py-rcsb-api)

## Import
To import this package, use:
```python
from rcsbapi.data import DataSchema, DataQuery
```

## Getting Started
The [RCSB PDB Data API](https://data.rcsb.org) supports requests using [GraphQL](https://graphql.org/), a language for API queries. This package simplifies generating queries in GraphQL syntax. 

To generate a query in this package, you would create a DataQuery object. The DataQuery object must be executed using the `.exec()` method, which will return the JSON response as well as store the response as an attribute of the DataQuery object. From the object, you can access the Data API response, get an interactive editor link, or access the arguments used to create the query.

The package is able to automatically build queries based on the input_type and path segment passed into return_data_list. If the package is included in code that is going to be used long-term, it's recommended to use fully-specified paths. When autocompletion is being used, an INFO message will be printed out as a reminder.

```python
from rcsbapi.data import DataQuery as Query
query = Query(
    input_type="entries",
    input_ids=["4HHB"],
    return_data_list=["exptl.method"]
)
# Note: when package autocompletes a paths, it prints an INFO message.
# Using fully-specified paths ("entries.exptl.method") will prevent the message

result_dict = query.exec()
print(result_dict)
# print(query.get_response()) would be equivalent
```
Data is returned in JSON format
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

### GraphQL
This is the equivalent query in GraphQL syntax.
```
{
  entries(entry_ids: ["4HHB"]) {  # returns type "CoreEntry"
    exptl {  # returns type "Exptl"
      method  # returns a scalar (string)
    }
  }
}
```
GraphQL is built on "types" and their associated "fields". All types and their fields are defined in a "schema". An example of a type in our schema is "CoreEntry" and a field under CoreEntry is "exptl" (experimental). Upon initialization, the Data API package fetches the schema from the RCSB PDB website (See [Implementation Details](implementation_details.md) for more). 

In GraphQL, you must begin your query at specific fields. These are fields like entry, polymer_entity, and polymer_entity_instance (see full list [here](query_construction.md#input-type)). Each field can return a scalar (e.g. string, integer) or a type. Every query must ultimately request scalar value(s), which can be seen in the example query below. As shown in the example, only fields are explicitly included in queries while types are implicit. Types are named in CamelCase (CoreEntry) while fields are in snake case (exptl or audit_author).

### Autocompletion of Queries
One way this package simplifies making requests is by adding fields that return scalars into the generated query if you request a field that returns a type.
```python
from rcsbapi.data import DataQuery as Query
query = Query(
    input_type="entries",
    input_ids=["4HHB"],
    return_data_list=["exptl"]
)
result_dict = query.exec()
print(result_dict)
```
This creates a valid query even though "exptl" doesn't return a scalar. However, the resulting query will be more verbose, requesting all scalar fields under "exptl" (see [return_data_list](query_construction.md#return-data-list)).

## Jupyter Notebooks
A notebook briefly summarizing the [readthedocs](https://rcsbapi.readthedocs.io/en/latest/index.html) is available in [notebooks/quickstart.ipynb](notebooks/quickstart.ipynb) or online through Google Colab <a href="https://colab.research.google.com/github/rcsb/py-rcsb-api/blob/master/notebooks/quickstart.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

Another notebook using both Search and Data API packages for a COVID-19 related example is available in [notebooks/search_data_workflow.ipynb](notebooks/search_data_workflow.ipynb) or online through Google Colab <a href="https://colab.research.google.com/github/rcsb/py-rcsb-api/blob/master/notebooks/search_data_workflow.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>.