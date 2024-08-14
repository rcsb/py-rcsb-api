# py-rcsb-api
Python interface for RCSB PDB API services at RCSB.org.

## Installation
Get it from PyPI:

    pip install rcsbapi

Or, download from [GitHub](https://github.com/rcsb/py-rcsbsearchapi)

To import this package, use:
```python
from rcsbapi.data import Schema, Query
```

## Jupyter Notebooks
A notebook briefly summarizing the [readthedocs](https://py-rcsb-api.readthedocs.io/en/latest/index.html) is available in [notebooks/quickstart.ipynb](notebooks/quickstart.ipynb).

Another notebook using both Search and Data API packages for a COVID-19 related example is available in [notebooks/search_data_workflow.ipynb](notebooks/search_data_workflow.ipynb).

## Quickstart
Full documentation available at [readthedocs](https://py-rcsb-api.readthedocs.io/en/latest/).

The [RCSB PDB Data API](https://data.rcsb.org) supports requests using [GraphQL](https://graphql.org/), a language for API queries. This package simplifies generating queries in GraphQL syntax. 

In GraphQL, you must begin your query at specific fields. These "input_types" are fields like entry, polymer_entity, and polymer_entity_instance <!--TODO: add link (see full list [here]())-->. You request data through the "return_data_list" argument. Available data can be explored with the [GraphiQL editor's documentation explorer](https://data.rcsb.org/graphql/index.html).

## Examples
This is a simple query in GraphQL syntax requesting the experimental method of a structure with PDB ID 4HHB (Hemoglobin).
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

To generate the same query in this package, you would create a Query object. The Query object must be executed using the `.exec()` method, which will return the JSON response as well as store the response as an attribute of the Query object. From the object, you can access the Data API response, get an interactive editor link, or access the arguments used to create the query.
```python
from rcsbapi.data import Query
query = Query(input_ids={"entry_id":"4HHB"},input_type="entry", return_data_list=["exptl.method"])
query.exec()
```

Here is a slightly more complex query and how to construct its equivalent. Note that periods can be used to further specify requested data in return_data_list. Also note many return data items and multiple ids can be requested in one query.
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

Learn about more features and troubleshooting at the [readthedocs page](https://py-rcsb-api.readthedocs.io/en/latest/index.html) and walk through some examples using the [Juptyer notebooks](#jupyter-notebooks)!