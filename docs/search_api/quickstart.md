# Quickstart

## Installation

Get it from PyPI:

    pip install rcsb-api

Or, download from [GitHub](https://github.com/rcsb/py-rcsb-api)

## Getting Started
### Basic Query Construction

#### Full-text search
To perform a "full-text" search for structures associated with the term "Hemoglobin", you can create a `TextQuery`:

```python
from rcsbapi.search import TextQuery

# Search for structures associated with the phrase "Hemoglobin"
query = TextQuery(value="Hemoglobin")

# Execute the query by running it as a function
results = query()

# Results are returned as an iterator of result identifiers.
for rid in results:
    print(rid)
```

#### Attribute search
To perform a search for specific structure or chemical attributes, you can create an `AttributeQuery`.

```python
from rcsbapi.search import AttributeQuery

# Construct a query searching for structures from humans
query = AttributeQuery(
    attribute="rcsb_entity_source_organism.scientific_name",
    operator="exact_match",  # Other operators include "contains_phrase", "exists", and more
    value="Homo sapiens"
)

# Execute query and construct a list from results
results = list(query())
print(results)
```

Refer to the [Search Attributes](https://search.rcsb.org/structure-search-attributes.html) and [Chemical Attributes](https://search.rcsb.org/chemical-search-attributes.html) documentation for a full list of attributes and applicable operators.

Alternatively, you can also construct attribute queries with comparative operators using the `rcsb_attributes` object (which also allows for names to be tab-completed):

```python
from rcsbapi.search import rcsb_attributes as attrs

# Search for structures from humans
query = attrs.rcsb_entity_source_organism.scientific_name == "Homo sapiens"

# Run query and construct a list from results
results = list(query())
print(results)
```

#### Grouping sub-queries

You can combine multiple queries using Python bitwise operators. 

```python
from rcsbapi.search import rcsb_attributes as attrs

# Query for human epidermal growth factor receptor (EGFR) structures (UniProt ID P00533)
#  with investigational or experimental drugs bound
q1 = attrs.rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession == "P00533"
q2 = attrs.rcsb_entity_source_organism.scientific_name == "Homo sapiens"
q3 = attrs.drugbank_info.drug_groups == "investigational"
q4 = attrs.drugbank_info.drug_groups == "experimental"

# Structures matching UniProt ID P00533 AND from humans
#  AND (investigational OR experimental drug group)
query = q1 & q2 & (q3 | q4)

# Execute query and print first 10 ids
results = list(query())
print(results[:10])
```

These examples are in `operator` syntax. You can also make queries in `fluent` syntax. Learn more about both syntaxes and implementation details in [Constructing and Executing Queries](query_construction.html#constructing-and-executing-queries).

### Supported Search Services
The list of supported search service types are listed in the table below. For more details on their usage, see [Search Service Types](query_construction.html#search-service-types).

|Search service                    |QueryType                 |
|----------------------------------|--------------------------|
|Full-text                         |`TextQuery()`             |
|Attribute (structure or chemical) |`AttributeQuery()`        |
|Sequence similarity               |`SeqSimilarityQuery()`         |
|Sequence motif                    |`SequenceMotifQuery()`    |
|Structure similarity              |`StructSimilarityQuery()` |
|Structure motif                   |`StructMotifQuery()`      |
|Chemical similarity               |`ChemSimilarityQuery()`   |

Learn more about available search services on the [RCSB PDB Search API docs](https://search.rcsb.org/#search-services).

## Jupyter Notebooks
A runnable jupyter notebook is available in [notebooks/search_quickstart.ipynb](https://github.com/rcsb/py-rcsb-api/blob/master/notebooks/search_quickstart.ipynb), or can be run online using Google Colab:
<a href="https://colab.research.google.com/github/rcsb/py-rcsb-api/blob/master/notebooks/search_quickstart.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

An additional Covid-19 related example is in [notebooks/covid.ipynb](https://github.com/rcsb/py-rcsb-api/blob/master/notebooks/covid.ipynb):
<a href="https://colab.research.google.com/github//rcsb/py-rcsb-api/blob/master/notebooks/covid.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
