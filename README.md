[![PyPi Release](https://img.shields.io/pypi/v/rcsb-api.svg)](https://pypi.org/project/rcsb-api/)
[![Build Status](https://dev.azure.com/rcsb/RCSB%20PDB%20Python%20Projects/_apis/build/status/rcsb.py-rcsb-api?branchName=master)](https://dev.azure.com/rcsb/RCSB%20PDB%20Python%20Projects/_build/latest?definitionId=40&branchName=master)
[![Documentation Status](https://readthedocs.org/projects/rcsbapi/badge/?version=latest)](https://rcsbapi.readthedocs.io/en/latest/?badge=latest)

# rcsb-api
Python interface for RCSB PDB API services at RCSB.org.

This package requires Python 3.7 or later.

## Installation
Get it from PyPI:

    pip install rcsb-api

Or, download from [GitHub](https://github.com/rcsb/py-rcsb-api/)


## Getting Started
Full documentation available at [readthedocs](https://rcsbapi.readthedocs.io/en/latest/).

The [RCSB PDB Data API](https://data.rcsb.org) supports requests using [GraphQL](https://graphql.org/), a language for API queries. This package simplifies generating queries in GraphQL syntax. 

In GraphQL, you must begin your query at specific fields. These "input_types" are fields like entry, polymer_entity, and polymer_entity_instance (see full list [here](https://rcsbapi.readthedocs.io/en/latest/query_construction.html#input-type)). You request data through the "return_data_list" argument. Available data can be explored with the [GraphiQL editor's documentation explorer](https://data.rcsb.org/graphql/index.html).

### Examples
This is a [simple query](https://data.rcsb.org/graphql/index.html?query=%7B%0A%20%20entry(entry_id%3A%20%224HHB%22)%20%7B%0A%20%20%20%20exptl%20%7B%0A%20%20%20%20%20%20method%0A%20%20%20%20%7D%0A%20%20%7D%0A%7D) requesting the experimental method of a structure with PDB ID 4HHB (Hemoglobin).

The query must be executed using the `.exec()` method, which will return the JSON response as well as store the response as an attribute of the Query object. From the object, you can access the Data API response, get an interactive editor link, or access the arguments used to create the query.
The package is able to automatically build queries based on the input_type and path segment passed into return_data_list. If using this package in code intended for long-term use, it's recommended to use fully-specified paths. When autocompletion is being used, an INFO message will be printed out as a reminder.

```python
from rcsbapi.data import Query
query = Query(
    input_type="entries",
    input_ids=["4HHB"],
    return_data_list=["exptl.method"]
)
# Note: when the package autocompletes a paths, it prints an INFO message.
# Using fully-specified paths ("entries.exptl.method") will prevent the message

print(query.exec())
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

Here is a [more complex query](https://data.rcsb.org/graphql/index.html?query=%7B%0A%20%20polymer_entities(entity_ids%3A%5B%222CPK_1%22%2C%223WHM_1%22%2C%222D5Z_1%22%5D)%20%7B%0A%20%20%20%20rcsb_id%0A%20%20%20%20rcsb_entity_source_organism%20%7B%0A%20%20%20%20%20%20ncbi_taxonomy_id%0A%20%20%20%20%20%20ncbi_scientific_name%0A%20%20%20%20%7D%0A%20%20%20%20rcsb_cluster_membership%20%7B%0A%20%20%20%20%20%20cluster_id%0A%20%20%20%20%20%20identity%0A%20%20%20%20%7D%0A%20%20%7D%0A%7D). Note that periods can be used to further specify requested data in return_data_list. Also note multiple return data items and ids can be requested in one query.
```python
from rcsbapi.data import Query
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
print(query.exec())
```

### Jupyter Notebooks
A notebook briefly summarizing the [readthedocs](https://rcsbapi.readthedocs.io/en/latest/index.html) is available in [notebooks/quickstart.ipynb](notebooks/quickstart.ipynb) or online through Google Colab <a href="https://colab.research.google.com/github/rcsb/py-rcsb-api/blob/master/notebooks/quickstart.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

Another notebook using both Search and Data API packages for a COVID-19 related example is available in [notebooks/search_data_workflow.ipynb](notebooks/search_data_workflow.ipynb) or online through Google Colab <a href="https://colab.research.google.com/github/rcsb/py-rcsb-api/blob/master/notebooks/search_data_workflow.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>.

___

Learn about more features and troubleshooting at the [readthedocs page](https://rcsbapi.readthedocs.io/en/latest/index.html) and walk through some examples using the Juptyer notebooks!