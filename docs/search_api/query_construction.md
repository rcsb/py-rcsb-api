# Query Construction

## Query Syntax and Execution
Two syntaxes are available for constructing queries: an "operator" syntax using Python's
comparators, and a "fluent" syntax where terms are chained together. Which to use is a
matter of preference, and both construct the same query object.

### Operator Syntax
Searches are built up from a series of `Terminal` nodes, which compare structural
attributes to some search value. In the operator syntax, Python's comparator
operators are used to construct the comparison. The operators are overloaded to
return `Terminal` objects for the comparisons.

Here is an example from the [RCSB PDB Search API](http://search.rcsb.org/#search-example-1) page created using the operator syntax. 
This query finds symmetric dimers having a twofold rotation with the DNA-binding domain of a heat-shock transcription factor.
```python
from rcsbapi.search import TextQuery
from rcsbapi.search import search_attributes as attrs

# Create terminals for each query
q1 = TextQuery("heat-shock transcription factor")
q2 = attrs.rcsb_struct_symmetry.symbol == "C2"
q3 = attrs.rcsb_struct_symmetry.kind == "Global Symmetry"
q4 = attrs.rcsb_entry_info.polymer_entity_count_DNA >= 1
```
Attributes are available from the `search_attributes` object and can be tab-completed. 
They can additionally be constructed from strings using the `Attr` (attribute) constructor. 

List of supported comparative operators:

|Operator|Description             |
|--------|------------------------|
|==      |is                      |
|!=      |is not                  |
|>       |greater than            |
|>=      |greater than or equal to|
|<       |less than               |
|<=      |less than or equal to   |

To use the `"exists"`, `"contains_phrase"`, or `"contains_words"` operator, create an [AttributeQuery](quickstart.md#attribute-search)

For methods to search and find details on attributes within this package, go to the [attributes page](attributes.md)
For a full list of attributes, please refer to the [RCSB PDB schema](http://search.rcsb.org/rcsbsearch/v2/metadata/schema).

Individual `Terminal`s are combined into `Group`s using python's bitwise operators. This is
analogous to how bitwise operators act on python `set` objects. The operators are
lazy and won't perform the search until the query is executed.

```python
query = q1 & (q2 & q3 & q4)  # AND of all queries
```
AND (`&`), OR (`|`), and terminal negation (`~`) are implemented directly by the API,
but the python package also implements set difference (`-`), symmetric difference (`^`),
and general negation by transforming the query.

List of supported bitwise operators:

|Operator|Description             |
|--------|------------------------|
|&       |AND                     |
|\|      |OR                      |
|~       |NOT                     |
|^       |XOR/symmetric difference|
|-       |set difference          |


Queries are executed by calling them as functions. They return an iterator of result
identifiers.

```python
# Call the query to execute it
results = query()

for rid in results:
    print(rid)
```

By default, the query will return "entry" results (PDB IDs corresponding to entries). It is also possible to
query other types of results (see [return-types](http://search.rcsb.org/#return-type)
for options):

```python
# Set return_type to "assembly" when executing
results = query(return_type="assembly")

for assembly_id in results:
    print(assembly_id)
```

### Fluent Syntax
The operator syntax is great for simple queries, but requires parentheses or
temporary variables for complex nested queries. In these cases the fluent syntax may
be clearer. Queries are built up by appending operations sequentially.

Here is the same example using the fluent syntax

```python
from rcsbapi.search import TextQuery, AttributeQuery, Attr

# Start with a Attr or TextQuery, then add terms
results = TextQuery("heat-shock transcription factor").and_(
    # Add attribute node as fully-formed AttributeQuery
    AttributeQuery(
        attribute="rcsb_struct_symmetry.symbol",
        operator="exact_match",
        value="C2"
    )

    # Add attribute node as Attr object with chained operations
    # Setting type to "text" specifies that it's a Structure Attribute
    .and_(Attr(
        attribute="rcsb_struct_symmetry.kind",
        type="text"
    )).exact_match("Global Symmetry")

    # Add attribute node by name (converted to Attr object) with chained operations
    .and_("rcsb_entry_info.polymer_entity_count_DNA").greater_or_equal(1)

    # Execute the query and return assembly ids
    ).exec(return_type="assembly")

# Exec produces an iterator of IDs
for assembly_id in results:
    print(assembly_id)
```

### Grouping Sub-Queries
Grouping of Structural Attribute and Chemical Attribute queries is permitted. More details on attributes that are available for attribute searches can be found on the [RCSB PDB Search API](https://search.rcsb.org/#search-attributes) page.

```python
from rcsbapi.search import AttributeQuery

# Query for structures determined by electron microscopy
q1 = AttributeQuery(
    attribute="exptl.method",
    operator="exact_match",
    value="electron microscopy"
)

# Drugbank annotations contain phrase "tylenol"
q2 = AttributeQuery(
    attribute="drugbank_info.brand_names",
    operator="contains_phrase",
    value="tylenol"
)

# Combine queries with AND
query = q1 & q2

list(query())
```

Some sets of attributes can be separately grouped for a more specific search. For example, the attribute `rcsb_chem_comp_related.resource_name` could be set to "DrugBank" or another database and grouped with the attribute `rcsb_chem_comp_related.resource_accession_code`, which can be used to search for an accession code. When grouped, these attributes will be searched for together (i.e. the accession code must be associated with the specified database). To identify attributes that can be grouped, check the [schema](http://search.rcsb.org/rcsbsearch/v2/metadata/schema) for attributes with `rcsb_nested_indexing` set to `true`. To specify that two attributes should be searched together, use the `group` function.

```python
from rcsbapi.search import AttributeQuery
from rcsbapi.search import group

q1 = AttributeQuery(
    attribute="rcsb_chem_comp_related.resource_name",
    operator="exact_match",
    value="DrugBank"
)

q2 = AttributeQuery(
    attribute="rcsb_chem_comp_related.resource_accession_code",
    operator="exact_match",
    value="DB00114"
)

q3 = AttributeQuery(
    attribute="rcsb_entity_source_organism.scientific_name",
    operator="exact_match",
    value="Escherichia coli"
)

# Using `group` ensures that `resource_name` and `accession_code` attributes are searched together
query = group(q1 & q2) & q3
list(query())
```

### Sessions
The result of executing a query (either by calling it as a function or using `exec()`) is a
`Session` object. It implements `__iter__`, so it is usually treated as an
iterator of IDs.

Paging is handled transparently by the session, with additional API requests made
lazily as needed. The page size can be controlled with the `rows` parameter.
```python
first = next(iter(query(rows=1)))
```
#### Query Editor Link
`get_editor_link()` is a `Session` method that will return a link to the [Search API query editor](https://search.rcsb.org/query-editor.html) populated with the query.

```python
from rcsbapi.search import AttributeQuery

query = AttributeQuery("exptl.method", operator="exact_match", value="electron microscopy")
session = query()
session.get_editor_link()
```

#### Advanced Search Query Builder Link
`get_query_builder_link()` is a `Session` method that will return a link to the [Advanced Search Query Builder](https://www.rcsb.org/search/advanced) populated with the query.

```python
from rcsbapi.search import AttributeQuery

query = AttributeQuery("exptl.method", operator="exact_match", value="electron microscopy")
session = query()
session.get_query_builder_link()
```

#### Progress Bar
The `iquery()` `Session` method provides a progress bar indicating the number of API
requests being made.
```python
results = query().iquery()
```

## Search Service Types
The list of supported search service types are listed in the table below.

|Search service                    |QueryType                 |
|----------------------------------|--------------------------|
|Full-text                         |`TextQuery()`             |
|Attribute (structure or chemical) |`AttributeQuery()`        |
|Sequence similarity               |`SeqSimilarityQuery()`    |
|Sequence motif                    |`SeqMotifQuery()`         |
|Structure similarity              |`StructSimilarityQuery()` |
|Structure motif                   |`StructMotifQuery()`      |
|Chemical similarity               |`ChemSimilarityQuery()`   |

Learn more about available search services on the [RCSB PDB Search API docs](https://search.rcsb.org/#search-services).

### Full-Text Search
To perform a general search for structures associated with the phrase "Hemoglobin", you can create a TextQuery. This does a "full-text" search, which is a general search on text associated with PDB structures or molecular definitions.

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

### Structure and Chemical Attribute Search
You can also search for specific structure or chemical attributes using an `AttributeQuery`.

```python
from rcsbapi.search import AttributeQuery

# Construct the query
query = AttributeQuery(
    attribute="rcsb_entity_source_organism.scientific_name",
    operator="exact_match",  # other operators include "contains_phrase" and "exists"
    value="Homo sapiens"
)
results = list(query())  # construct a list from query results
print(results)
```

As Structure Attributes and Chemical Attributes are almost all unique, the package is usually able to automatically determine the search `service` required. However, for attributes that are both Structure and Chemical Attributes (e.g., `"rcsb_id"`), specifying a search service is required (Structure Attribute service: `"text"`, Chemical Attribute service: `"text_chem"`).
```python
# "rcsb_id" is both a Structure Attribute and Chemical Attribute
#  so search `service` must be specified

# Specify Structure Attribute search by setting service to "text"
q1 = AttributeQuery(
    attribute="rcsb_id",
    operator="exact_match",
    value="4HHB",
    service="text"
)
list(q1())

# Specify Chemical Attribute search by setting service to "text_chem"
q2 = AttributeQuery(
    attribute="rcsb_id",
    operator="exact_match",
    value="HEM",
    service="text_chem"
)
list(q2())
```

|Arguments    |Required| Description                                 |Default               |
|-------------|--------|---------------------------------------------|----------------------|
|`attribute`  |yes     |Full attribute name                          |                      |
|`operator`   |yes     |Operation for query                          |                      |
|`value`      |no      |Search term(s)                               |                      |
|`service`    |no      |Specify structure or chemical search service |                      |
|`negation`   |no      |Indicates if the operator is negated         |False                 |


The `operator` can be one of a number of options, depending on the attribute type being queried. For example, `"contains_phrase"` or `"exact_match"` can be used to compare the attribute to a value, or the `"exists"` operator may be used to check if the attribute exists for a given structure. Refer to the [Search Attributes](https://search.rcsb.org/structure-search-attributes.html) and [Chemical Attributes](https://search.rcsb.org/chemical-search-attributes.html) documentation for a full list of attributes and applicable operators.

Alternatively, you can also construct attribute queries with comparative operators (e.g., `==`, `>`, or `<`) using the `search_attributes` object (which also allows for names to be tab-completed):

```python
from rcsbapi.search import search_attributes as attrs

# Search for structures from humans
query = attrs.rcsb_entity_source_organism.scientific_name == "Homo sapiens"
results = list(query())  # construct a list from query results
print(results)
```

The full list of supported comparative operators:

|Operator|Description             |
|--------|------------------------|
|==      |is                      |
|!=      |is not                  |
|>       |greater than            |
|>=      |greater than or equal to|
|<       |less than               |
|<=      |less than or equal to   |

### Sequence Similarity Search
Below is an example from the [RCSB PDB Search API](https://search.rcsb.org/#search-example-3) page, using the sequence search function. This query finds macromolecular PDB entities that share 90% sequence identity with GTPase HRas protein from *Gallus gallus* (*Chicken*).


```python
from rcsbapi.search import SeqSimilarityQuery

# Use SeqSimilarityQuery class and add parameters
query = SeqSimilarityQuery(
    "MTEYKLVVVGAGGVGKSALTIQLIQNHFVDEYDPTIEDSYRKQVVIDGET" +
    "CLLDILDTAGQEEYSAMRDQYMRTGEGFLCVFAINNTKSFEDIHQYREQI" +
    "KRVKDSDDVPMVLVGNKCDLPARTVETRQAQDLARSYGIPYIETSAKTRQ" +
    "GVEDAFYTLVREIRQHKLRKLNPPDESGPGCMNCKCVIS",
    evalue_cutoff=1,
    identity_cutoff=0.9,
    sequence_type="protein"
)
    
# query("polymer_entity") produces an iterator of IDs with return type polymer_entity
for polyid in query("polymer_entity"):
    print(polyid)
```

|Arguments        |Required| Description                                         |Default               |
|-----------------|--------|-----------------------------------------------------|----------------------|
|`value`          |yes     |Protein or nucleotide sequence                       |                      |
|`evalue_cutoff`  |no      |Upper cutoff for E-value (lower is more significant) |0.1                   |
|`identity_cutoff`|no      |Lower cutoff for sequence identity (0-1)             |0                     |
|`sequence_type`  |no      |Type of biological sequence ("protein", "dna", "rna")|"protein"             |

### Sequence Motif Search
Below is an example from the [RCSB PDB Search API](https://search.rcsb.org/#search-example-6) page, using the sequence motif search function. This query retrieves occurrences of the His<sub>2</sub>/Cys<sub>2</sub> Zinc Finger DNA-binding domain as represented by its PROSITE signature.

```python
from rcsbapi.search import SeqMotifQuery

# Use SeqMotifQuery class and add parameters
query = SeqMotifQuery(
    "C-x(2,4)-C-x(3)-[LIVMFYWC]-x(8)-H-x(3,5)-H.",
    pattern_type="prosite",
    sequence_type="protein"
)

# query("polymer_entity") produces an iterator of IDs with return type polymer_entity
for polyid in query("polymer_entity"):
    print(polyid)
```

|Arguments        |Required| Description                                         |Default               |
|-----------------|--------|-----------------------------------------------------|----------------------|
|`value`          |yes     |Motif to search                                      |                      |
|`pattern_type`   |no      |Motif syntax ("simple", "prosite", "regex")          |"simple"              |
|`sequence_type`  |no      |Type of biological sequence ("protein", "dna", "rna")|"protein"             |

See [Sequence Motif Search Examples](additional_examples.md#Sequence-Motif-Search-Examples) for more use cases.

### Structure Similarity Search
The PDB archive can be queried using the 3D shape of a protein structure. To perform this query, 3D protein structure data must be provided as an input, a `chain_id` or `assembly_id` must be specified, whether the input structure data should be compared to `assembly` or `polymer_entity_instance` (Chains) is required, and defining the search type as either `strict` or `relaxed` is required. More information on how Structure Similarity Queries work can be found on the [RCSB PDB Structure Similarity Search](https://www.rcsb.org/docs/search-and-browse/advanced-search/structure-similarity-search) page.

```python
from rcsbapi.search import StructSimilarityQuery

# Basic query:
# Querying using entry ID and default values:
# assembly ID "1", operator "strict", target search space "assembly"
q1 = StructSimilarityQuery(entry_id="4HHB")

# Same query but with parameters explicitly specified
q1 = StructSimilarityQuery(
    structure_search_type="entry_id",
    entry_id="4HHB",
    structure_input_type="assembly_id",
    assembly_id="1",
    operator="strict_shape_match",
    target_search_space="assembly"
)
for rid in q1("assembly"):
    print(rid)
```

|Arguments                | Description                                                                |Default      |
|-------------------------|----------------------------------------------------------------------------|-------------|
|`structure_search_type`  |How to find given structure ("entry_id", "file_url", "file_path")           |"entry_id"   |
|`entry_id`               |If "entry_id" specified, PDB ID or CSM ID                                   |             |
|`file_url`               |If "file_url" specified, url to file                                        |             |
|`file_path`              |If "file_path" specified, path to file                                      |             |
|`file_format`            |If "file_url" or "file_path" specified, type of file (ex: "cif")            |             |
|`structure_input_type`   |Type of the given structure                                                 |"assembly_id"|
|`assembly_id`            |If input_type is "assembly_id", the assembly id number                      |"1"          |
|`chain_id`               |If input_type is "chain_id", the chain id letter                            |             |
|`operator`               |Search mode ("strict_shape_match" or "relaxed_shape_match")                 |"strict_shape_match"|
|`target_search_space`    |Target objects against which the query will be compared for shape similarity|"assembly"   |


If you provide an `entry_id`, you must provide either an `assembly_id` or `chain_id`

If you provide a `file_url` or `file_path`, you must also provide a `file_format`.

See [Structure Similarity Search Examples](additional_examples.md#Structure-Similarity-Search-Examples) for more use cases.

### Structure Motif Search
The PDB Archive can also be queried by using a "motif" found in 3D structures. To perform this type of query, an entry id or a file URL/path must be provided, along with residues (which are parts of 3D structures). This is the bare minimum needed to make a search, but there are lots of other parameters that can be added to a Structure Motif Query (see [Search API reference](https://search.rcsb.org/redoc/index.html)).

To make a Structure Motif Query, you must first define anywhere from 2-10 "residues" that will be used in the query. Each individual residue has a chain ID, operator, residue number, and exchanges (optional) that can be declared in that order using positional arguments, or using the `chain_id`, `struct_oper_id`, and `label_seq_id` to define what parameter you are passing through. All 3 of the required parameters must be included, or the package will throw an `AssertionError`. 

Each residue can only have a maximum of 4 Exchanges, and each query can only have 16 exchanges total. Violating any of these rules will cause the package to throw an `AssertionError`. 

Examples of how to instantiate Residues can be found below. These can then be put into a list and passed through to a Structure Motif Query.
```python
from rcsbapi.search import StructMotifResidue

# Construct a Residue with:
# Chain ID of A, an operator of 1, residue number 192, and Exchanges of "LYS" and "HIS".
# As for what is a valid "Exchange", the package provides these as a literal,
# and they should be type checked. 
Res1 = StructMotifResidue(
    struct_oper_id="1",
    chain_id="A",
    exchanges=["LYS", "HIS"],  # exchanges are optional
    label_seq_id=192
)

Res2 = StructMotifResidue(
    struct_oper_id="1",
    chain_id="A",
    label_seq_id=162
)

# After declaring a minimum of 2 and as many as 10 residues,
# they can be passed into a list for use in the query itself:
ResList = [Res1, Res2]
```

From there, these residues can be used in a query. As stated before, you can only include 2-10 residues in a query. If you fail to provide residues for a query, or provide the wrong amount, the package will throw a `ValueError`. 

For a Structure Motif Query using an `entry_id`, the only other required argument is `residue_ids`. The default type of query is an `entry_id` query. 

As this type of query has a lot of optional parameters, do *not* use positional arguments as more than likely an error will occur. 

Below is an example of a basic `entry_id` Structure Motif Query, with the residues declared earlier:
```python
from rcsbapi.search import StructMotifQuery

q1 = StructMotifQuery(entry_id="2MNR", residue_ids=ResList)
list(q1())
```

|Arguments                     | Description                                                      |Default      |
|------------------------------|------------------------------------------------------------------|-------------|
|`structure_search_type`       |How to find given structure ("entry_id", "url", "file_path")      |"entry_id"   |
|`backbone_distance_tolerance` |Tolerance for distance between Cα atoms (in Å)                    |1            |
|`side_chain_distance_tolerance`|Tolerance for distance between Cβ atoms (in Å)                   |1            |
|`angle_tolerance`             |Angle between CαCβ vectors (in multiples of 20 degrees)           |1            |
|`entry_id`                    |If "entry_id" specified, PDB ID or CSM ID                         |             |
|`url`                         |If "file_url" specified, url to file                              |             |
|`file_path`                   |If "file_path" specified, path to file                            |             |
|`file_extension`              |If "file_url" specified, type of file linked to (ex: "cif")       |             |
|`residue_ids`                 |List of StructMotifResidue objects                                |             |
|`rmsd_cutoff`                 |Upper cutoff for root-mean-square deviation (RMSD) score          |2            |
|`atom_pairing_scheme`         |Which atoms to consider to compute RMSD scores and transformations.|"SIDE_CHAIN" |
|`motif_pruning_strategy`      |Specifies how query motifs are pruned (i.e. simplified)           |"KRUSKAL"    |
|`allowed_structures`          |If the list of structure identifiers is specified, the search will only consider those structures (ex: ["HIS", "LYS"])||
|`excluded_structures`         |If the list of structure identifiers is specified, the search will exclude those structures from the search space||
|`limit`                       |Stop after accepting this many hits                               |             |

If you provide an `entry_id`, the other optional parameters can be ignored.

If you provide a `file_url`, you must also provide a `file_extension`.

If you provide a `file_path`, you must also provide a `file_extension`.

See [Structure Motif Search Examples](additional_examples.md#Structure-Motif-Search-Examples) for more use cases.

### Chemical Similarity Search
When you have unique chemical information (e.g., a chemical formula or descriptor) you can use this information to find chemical components (e.g., drugs, inhibitors, modified residues, or building blocks such as amino acids, nucleotides, or sugars) that are similar to the formula/descriptor used in the query or contain the formula/descriptor as a substructure.

The search can also be used to identify PDB structures that include the chemical component(s) which match or are similar to the query. These structures can then be examined to learn about the interactions of the component within the structure. More information on Chemical Similarity Queries can be found on the [RCSB PDB Chemical Similarity Search](https://www.rcsb.org/docs/search-and-browse/advanced-search/chemical-similarity-search) page.

To do a Chemical Similarity query, you must first specify one of two possible query options: `formula` or `descriptor`. `formula` allows queries to be made by providing a chemical formula. `descriptor` allows you to search by chemical notations. Each query option has its own distinct set of parameters, but both options require a `value`.

The `formula` query option comes with a `match_subset` parameter which allows users to search chemical components whose formula exactly match the query or matches any portion of the query. The `descriptor` query option comes with a `descriptor_type` parameter and `match_type` parameter. The `descriptor_type` parameter specifies what type of descriptor the input value is. There are two options: `SMILES` (Simplified Molecular Input Line Entry Specification) and `InChI` (International Chemical Identifier). The `match_type` parameter has six options which are shown in the table below.

When doing Chemical Similarity queries in this package, it is important to note that by default the query option is set to `formula` and `match_subset` is set to `False`. An example of how that looks like is below.
```python
from rcsbapi.search import ChemSimilarityQuery

# Basic query with default values: query type = formula and match subset = False
q1 = ChemSimilarityQuery(
    value="C12 H17 N4 O S",
    query_type="formula",
    match_subset=False
)
list(q1())
```

|Arguments                |Required|Description                                                                             |Default      |
|-------------------------|--------|----------------------------------------------------------------------------------------|-------------|
|`value`                  |yes     |Chemical formula or descriptor (SMILES or InChI)                                        |             |
|`query_type`             |no      |"formula" or "descriptor"                                                               |"formula"    |
|`descriptor_type`        |no      |If "descriptor", whether it's "SMILES" or "InCHI"                                       |             |
|`match_subset`           |no      |If "formula", return chemical components/structures that contain the formula as a subset|False        |
|`match_type`             |no      |If "descriptor", type of matches to find and return (see below)                         |             |


| match_type                        |                                           |
|-----------------------------------|-------------------------------------------|
| "graph-relaxed"                   | Similar Ligands (including Stereoisomers) |
| "graph-relaxed-stereo"            | Similar Ligands (Stereospecific)          |
| "fingerprint-similarity"          | Similar Ligands (Quick screen)            |
| "sub-struct-graph-relaxed-stereo" | Substructure (Stereospecific)             |
| "sub-struct-graph-relaxed"        | Substructure (including Stereoisomers)    |
| "graph-exact"                     | Exact match                               |

See [Chemical Similarity Search Examples](additional_examples.md#Chemical-Similarity-Search-Examples) for more use cases.

## Request Options

### Return Types
A search query can return different results when a `return_type` is specified. Below are Structure Attribute query examples specifying return types `"polymer_entity"`, `"non_polymer_entity"`, `"polymer_instance"`, and `"mol_definition"`. More information on return types can be found in the [RCSB PDB Search API](https://search.rcsb.org/#return-type) page.

```python
from rcsbapi.search import AttributeQuery

# query for 4HHB deoxyhemoglobin
q1 = AttributeQuery(
    attribute="rcsb_entry_container_identifiers.entry_id",
    operator="in",
    value=["4HHB"]
)

# Polymer entities
for poly in q1(return_type="polymer_entity"):
    print(poly)
    
# Non-polymer entities
for nonPoly in q1(return_type="non_polymer_entity"):
    print(nonPoly)
    
# Polymer instances
for polyInst in q1(return_type="polymer_instance"):
    print(polyInst)
    
# Molecular definitions
for mol in q1(return_type="mol_definition"):
    print(mol)
```

### Computed Structure Models
The [RCSB PDB Search API](https://search.rcsb.org/#results_content_type) page provides information on how to include Computed Structure Models (CSMs) into a search query. Here is a code example below.

This query returns IDs for `experimental` and `computational` models associated with "hemoglobin". Queries for *only* computed models or *only* experimental models can also be made (default).
```python
from rcsbapi.search import TextQuery

q1 = TextQuery(value="hemoglobin")

# add parameter as a list with either "computational" or "experimental" or both
q2 = q1(return_content_type=["computational", "experimental"])

list(q2)
```

### Results Verbosity
Results can be returned alongside additional metadata, including result scores. To return this metadata, set the `results_verbosity` parameter to `"verbose"` (all metadata), `"minimal"` (scores only), or `"compact"` (default, no metadata). If set to `"verbose"` or `"minimal"`, results will be returned as a list of dictionaries. 

For example, here we get all experimental models associated with "hemoglobin", along with their scores, by setting verbosity to `"minimal"`.

```python
from rcsbapi.search import TextQuery

q1 = TextQuery(value="hemoglobin")
# Set results_verbosity to "minimal"
for idscore in list(q1(results_verbosity="minimal")):
    print(idscore)
```

### Count Queries
If only the number of results is desired, the `return_counts` request option can be used. This query returns the number of experimental models associated with "hemoglobin".
```python
from rcsbapi.search import TextQuery

q1 = TextQuery(value="hemoglobin")

# Set return_counts request option to True
result_count = q1(return_counts=True)
print(result_count)
```
### Faceted Queries
You can use a faceted query (or facets) to group and perform calculations and statistics on PDB data. Facets arrange search results into categories (buckets) based on the requested field values. More information on Faceted Queries can be found [here](https://search.rcsb.org/#using-facets). All facets should be provided with `name`, `aggregation_type`, and `attribute` values. Depending on the aggregation type, other parameters must also be specified. To run a faceted query, create a `Facet` object and pass it in as a single object or list into the `facets` argument during query execution.

```python
from rcsbapi.search import AttributeQuery, Facet

q = AttributeQuery(
    attribute="rcsb_accession_info.initial_release_date",
    operator="greater",
    value="2019-08-20",
)

q_result = q(facets=Facet(
    name="Methods",
    aggregation_type="terms",
    attribute="exptl.method"
))
print(q_result.facets)
```

List of available types of Faceted queries:
- Terms Facet
- Histogram Facet
- Range Facet
- Date Range Facet
- Cardinality Facet
- Multidimensional Facet
- Filter Facet

See example usage of each of these types of Faceted queries at [Faceted Query Examples](additional_examples.md#faceted-query-examples).

### Additional Request Options
Other request options can also be added to queries through arguments at execution. `facet`, `group_by`, and `sort` are more complex request options and require creating a `RequestOption` object (`Facet`, `GroupBy`, `Sort`).

List of available request options:
- `results_content_type`
- `results_verbosity`
- `return_counts`
- `facets`
- `group_by`
- `group_by_return_type`
- `sort`
- `return_explain_metadata`
- `scoring_strategy`


Some request options are currently not implemented:
- paginate: Automatically handled by package. Results are paginated by package and all results are returned.
- return_all_hits: Not implemented since all results are returned

For more information on what each request option does, refer to the [Search API documentation](https://search.rcsb.org/#scoring-strategy).

For information on how to create `RequestOption` objects, see the [API reference](api.rst).
