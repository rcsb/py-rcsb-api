[![PyPi Release](https://img.shields.io/pypi/v/rcsb-api.svg)](https://pypi.org/project/rcsb-api/)
[![Build Status](https://dev.azure.com/rcsb/RCSB%20PDB%20Python%20Projects/_apis/build/status/rcsb.py-rcsb-api?branchName=master)](https://dev.azure.com/rcsb/RCSB%20PDB%20Python%20Projects/_build/latest?definitionId=40&branchName=master)
[![Documentation Status](https://readthedocs.org/projects/rcsbapi/badge/?version=latest)](https://rcsbapi.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14052470.svg)](https://doi.org/10.5281/zenodo.14052470)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/10424/badge)](https://www.bestpractices.dev/projects/10424)
[![FAIR checklist badge](https://fairsoftwarechecklist.net/badge.svg)](https://fairsoftwarechecklist.net/v0.2?f=31&a=30112&i=32111&r=133)
[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F-green)](https://fair-software.eu)

# rcsb-api
Python interface for RCSB PDB API services at RCSB.org.

This package requires Python 3.8 or later.


## Installation
Get it from PyPI:

    pip install rcsb-api

Or, download from [GitHub](https://github.com/rcsb/py-rcsb-api/)


## Getting Started
Full documentation available at [readthedocs](https://rcsbapi.readthedocs.io/en/latest/).

The [RCSB PDB Search API](https://search.rcsb.org) supports RESTful requests according to a defined [schema](https://search.rcsb.org/redoc/index.html). This package provides an `rcsbapi.search` module that simplifies generating complex search queries.

The [RCSB PDB Data API](https://data.rcsb.org) supports requests using [GraphQL](https://graphql.org/), a language for API queries. This package provides an `rcsbapi.data` module that simplifies generating queries in GraphQL syntax.

### Search API
The `rcsbapi.search` module supports all available [Advanced Search](https://www.rcsb.org/search/advanced) services, as listed below. For more details on their usage, see [Search Service Types](https://rcsbapi.readthedocs.io/en/latest/search_api/query_construction.html#search-service-types).

|Search service                    |QueryType                 |
|----------------------------------|--------------------------|
|Full-text                         |`TextQuery()`             |
|Attribute (structure or chemical) |`AttributeQuery()`        |
|Sequence similarity               |`SeqSimilarityQuery()`    |
|Sequence motif                    |`SeqMotifQuery()`         |
|Structure similarity              |`StructSimilarityQuery()` |
|Structure motif                   |`StructMotifQuery()`      |
|Chemical similarity               |`ChemSimilarityQuery()`   |

#### Search API Examples
To perform a search for all structures from humans associated with the term "Hemoglobin", you can combine a "full-text" query (`TextQuery`) with an "attribute" query (`AttributeQuery`):

```python
from rcsbapi.search import AttributeQuery, TextQuery
from rcsbapi.search import search_attributes as attrs

# Construct a "full-text" sub-query for structures associated with the term "Hemoglobin"
q1 = TextQuery(value="Hemoglobin")

# Construct an "attribute" sub-query to search for structures from humans
q2 = AttributeQuery(
    attribute="rcsb_entity_source_organism.scientific_name",
    operator="exact_match",  # Other operators include "contains_phrase", "exists", and more
    value="Homo sapiens"
)
# OR, do so by using Python bitwise operators:
q2 = attrs.rcsb_entity_source_organism.scientific_name == "Homo sapiens"

# Combine the sub-queries (can sub-group using parentheses and standard operators, "&", "|", etc.)
query = q1 & q2

# Fetch the results by iterating over the query execution
for rId in query():
    print(rId)

# OR, capture them into a variable
results = list(query())
```

These examples are in `operator` syntax. You can also make queries in `fluent` syntax. Learn more about both syntaxes and implementation details in [Query Syntax and Execution](https://rcsbapi.readthedocs.io/en/latest/search_api/query_construction.html#query-syntax-and-execution).


### Data API
The `rcsbapi.data` module allows you to easily construct GraphQL queries to the RCSB.org Data API.

This is done by specifying the following input:
- "input_type": the data hierarchy level you are starting from (e.g., "entry", "polymer_entity", etc.) (See full list [here](https://rcsbapi.readthedocs.io/en/latest/data_api/query_construction.html#input-type)).
- "input_ids": the list of IDs for which to fetch data (corresponding to the specified "input_type")
- "return_data_list": the list of data items ("fields") to retrieve. (Available fields can be explored [here](https://data.rcsb.org/data-attributes.html) or via  the [GraphiQL editor's Documentation Explorer panel](https://data.rcsb.org/graphql/index.html).)

#### Data API Examples
This is a [simple query](https://data.rcsb.org/graphql/index.html?query=%7B%0A%20%20entry(entry_id%3A%20%224HHB%22)%20%7B%0A%20%20%20%20exptl%20%7B%0A%20%20%20%20%20%20method%0A%20%20%20%20%7D%0A%20%20%7D%0A%7D) requesting the experimental method of a structure with PDB ID 4HHB (Hemoglobin).

The query must be executed using the `.exec()` method, which will return the JSON response as well as store the response as an attribute of the `DataQuery` object. From the object, you can access the Data API response, get an interactive editor link, or access the arguments used to create the query.
The package is able to automatically build queries based on the "input_type" and path segment passed into "return_data_list". If using this package in code intended for long-term use, it's recommended to use fully qualified paths. When autocompletion is being used, an WARNING message will be printed out as a reminder.

```python
from rcsbapi.data import DataQuery as Query
query = Query(
    input_type="entries",
    input_ids=["4HHB"],
    return_data_list=["exptl.method"]
)
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
from rcsbapi.data import DataQuery as Query
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

## Jupyter Notebooks
Several Jupyter notebooks with example use cases and workflows for all package modules are provided under [notebooks](notebooks/).

For example, one notebook using both Search and Data API packages for a COVID-19 related example is available in [notebooks/search_data_workflow.ipynb](notebooks/search_data_workflow.ipynb) or online through Google Colab <a href="https://colab.research.google.com/github/rcsb/py-rcsb-api/blob/master/notebooks/search_data_workflow.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>.


## Citing
Please cite the ``rcsb-api`` package with the following reference:

> Dennis W. Piehl, Brinda Vallat, Ivana Truong, Habiba Morsy, Rusham Bhatt, 
> Santiago Blaumann, Pratyoy Biswas, Yana Rose, Sebastian Bittrich, Jose M. Duarte,
> Joan Segura, Chunxiao Bi, Douglas Myers-Turnbull, Brian P. Hudson, Christine Zardecki,
> Stephen K. Burley. rcsb-api: Python Toolkit for Streamlining Access to RCSB Protein 
> Data Bank APIs, Journal of Molecular Biology, 2025.
> DOI: [10.1016/j.jmb.2025.168970](https://doi.org/10.1016/j.jmb.2025.168970)

You should also cite the RCSB.org API services this package utilizes:

> Yana Rose, Jose M. Duarte, Robert Lowe, Joan Segura, Chunxiao Bi, Charmi
> Bhikadiya, Li Chen, Alexander S. Rose, Sebastian Bittrich, Stephen K. Burley,
> John D. Westbrook. RCSB Protein Data Bank: Architectural Advances Towards
> Integrated Searching and Efficient Access to Macromolecular Structure Data
> from the PDB Archive, Journal of Molecular Biology, 2020.
> DOI: [10.1016/j.jmb.2020.11.003](https://doi.org/10.1016/j.jmb.2020.11.003)


## Documentation and Support
Please refer to the [readthedocs page](https://rcsbapi.readthedocs.io/en/latest/index.html) to learn more about package usage and other available features as well as to see more examples.

If you experience any issues installing or using the package, please submit an issue on [GitHub](https://github.com/rcsb/py-rcsb-api/issues) and we will try to respond in a timely manner.
